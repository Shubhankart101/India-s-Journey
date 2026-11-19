"""In-memory vector search index for India's Journey catalog indicators.

Designed for sub-5ms lookup latency on Azure App Service Linux B1 containers
with low RAM footprint (~3MB).
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings

logger = logging.getLogger(__name__)


def _slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')


class CatalogVectorIndex:
    """Manages pre-computed vector embeddings for 3,082 indicators."""

    _instance: Optional[CatalogVectorIndex] = None

    def __init__(self, embeddings_path: Optional[Path] = None):
        self.embeddings_path = embeddings_path or getattr(
            settings,
            'CATALOG_EMBEDDINGS_PATH',
            Path(settings.BASE_DIR).parent / 'data' / 'catalog_embeddings.json'
        )
        self.items: List[Dict[str, Any]] = []
        self._loaded = False

    @classmethod
    def get_instance(cls) -> CatalogVectorIndex:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def ensure_loaded(self) -> None:
        """Load pre-computed embeddings into memory if not already loaded."""
        if self._loaded:
            return

        path = Path(self.embeddings_path)
        if not path.is_file():
            # Alternative candidate locations across local and containerized Azure environments
            alt_candidates = [
                Path(settings.BASE_DIR) / 'data' / 'catalog_embeddings.json',
                Path(settings.BASE_DIR).parent / 'data' / 'catalog_embeddings.json',
                Path('/app/data/catalog_embeddings.json'),
            ]
            for cand in alt_candidates:
                if cand.is_file():
                    path = cand
                    break

        if not path.is_file():
            logger.warning('Catalog embeddings file not found at %s. Attempting fallback indexing.', self.embeddings_path)
            self._load_fallback_from_catalog()
            self._loaded = True
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.items = data.get('indicators', [])
            self._loaded = True
            logger.info('Loaded %d indicator embeddings into memory from %s', len(self.items), path)
        except Exception as exc:
            logger.error('Failed to load embeddings from %s: %s; falling back to catalog.json', path, exc)
            self._load_fallback_from_catalog()
            self._loaded = True

    def _load_fallback_from_catalog(self) -> None:
        """Build in-memory embeddings directly from data/catalog.json using offline vectorizer."""
        from .azure_client import AzureAIClient

        catalog_path = Path(settings.BASE_DIR).parent / 'data' / 'catalog.json'
        if not catalog_path.is_file():
            logger.error('catalog.json not found at %s', catalog_path)
            self.items = []
            return

        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)

            client = AzureAIClient()
            indicators_raw = catalog.get('indicators', [])
            indicators_list = list(indicators_raw.values()) if isinstance(indicators_raw, dict) else list(indicators_raw)
            items = []

            for meta in indicators_list:
                if not isinstance(meta, dict):
                    continue
                key = meta.get('key', '')
                title = meta.get('title', '')
                subgroup = meta.get('subgroup', '')
                category = meta.get('category', '')
                details = meta.get('details', '')
                text_to_embed = f"{title} | {subgroup} | {category} | {details}"

                vec = client.get_embedding(text_to_embed)
                items.append({
                    'key': key,
                    'title': title,
                    'subtitle': meta.get('subtitle', ''),
                    'category': category,
                    'subgroup': subgroup,
                    'frequency': meta.get('frequency', ''),
                    'unit': meta.get('unit', '') or meta.get('suffix', ''),
                    'source': meta.get('source', ''),
                    'vec': vec,
                })

            self.items = items
            logger.info('Built %d in-memory fallback embeddings from catalog.json', len(self.items))
        except Exception as exc:
            logger.error('Failed to build fallback embeddings from catalog.json: %s', exc)
            self.items = []

    def search(
        self,
        query_vec: List[float],
        query_text: str = '',
        limit: int = 10,
        category: Optional[str] = None,
        min_similarity: float = 0.15,
    ) -> List[Dict[str, Any]]:
        """Search the index using cosine similarity and hybrid term boosting."""
        self.ensure_loaded()
        if not self.items:
            return []

        query_terms = set(re.findall(r'[a-zA-Z0-9_\u0900-\u097F]+', query_text.lower()))
        target_cat_slug = _slug(category) if category else None

        scored_results: List[Tuple[float, Dict[str, Any]]] = []

        for item in self.items:
            if target_cat_slug:
                item_cat = item.get('category', '')
                if _slug(item_cat) != target_cat_slug and target_cat_slug not in _slug(item_cat):
                    continue

            item_vec = item.get('vec', [])
            if not item_vec or len(item_vec) != len(query_vec):
                continue

            # Dot product of normalized vectors = cosine similarity
            sim = sum(q * v for q, v in zip(query_vec, item_vec))

            # Hybrid keyword boost: elevate exact title / key matches
            title_lower = item.get('title', '').lower()
            key_lower = item.get('key', '').lower()

            boost = 0.0
            for term in query_terms:
                if len(term) >= 3:
                    if term in title_lower:
                        boost += 0.08
                    if term in key_lower:
                        boost += 0.05

            final_score = round(min(1.0, sim + boost), 4)
            if final_score >= min_similarity:
                scored_results.append((final_score, item))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, item in scored_results[:limit]:
            record = {k: v for k, v in item.items() if k != 'vec'}
            record['similarity'] = score
            results.append(record)

        return results

    def recommend(
        self,
        key: str,
        limit: int = 5,
        same_category_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Find the top-K contextually related indicators using embedding cosine similarity."""
        self.ensure_loaded()
        if not self.items:
            return []

        target = next((item for item in self.items if item.get('key') == key), None)
        if not target:
            return []

        target_vec = target.get('vec', [])
        if not target_vec:
            return []

        target_cat = target.get('category', '')
        scored: List[Tuple[float, Dict[str, Any]]] = []

        for item in self.items:
            if item.get('key') == key:
                continue
            if same_category_only and item.get('category') != target_cat:
                continue

            item_vec = item.get('vec', [])
            if not item_vec or len(item_vec) != len(target_vec):
                continue

            sim = sum(q * v for q, v in zip(target_vec, item_vec))
            scored.append((sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, item in scored[:limit]:
            record = {k: v for k, v in item.items() if k != 'vec'}
            record['similarity'] = round(score, 4)
            results.append(record)

        return results

