"""AI embedding and inference client tailored for Azure App Service.

Supports:
1. Azure OpenAI Service (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`).
2. Standard OpenAI API (`OPENAI_API_KEY`).
3. Google Gemini Embeddings API (`GEMINI_API_KEY`).
4. High-performance offline deterministic vectorizer fallback when no API keys are configured.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Default embedding dimensionality (compact representation for Azure B1 App Service)
DEFAULT_EMBEDDING_DIM = 256


class AzureAIClient:
    """Client for generating text embeddings on Azure App Service with graceful fallbacks."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        dimensions: int = DEFAULT_EMBEDDING_DIM,
    ):
        self.endpoint = (endpoint or getattr(settings, 'AZURE_OPENAI_ENDPOINT', '')).strip().rstrip('/')
        if self.endpoint and not self.endpoint.startswith(('http://', 'https://')):
            self.endpoint = f'https://{self.endpoint}'
        self.api_key = (api_key or getattr(settings, 'AZURE_OPENAI_API_KEY', '')).strip()
        self.deployment = (deployment or getattr(settings, 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-small')).strip()
        self.api_version = (api_version or getattr(settings, 'AZURE_OPENAI_API_VERSION', '2024-02-01')).strip()
        self.openai_key = getattr(settings, 'OPENAI_API_KEY', '').strip()
        self.gemini_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
        self.dimensions = dimensions

    @property
    def provider(self) -> str:
        if self.endpoint and self.api_key:
            return 'azure-openai'
        if self.openai_key:
            return 'openai'
        if self.gemini_key:
            return 'gemini'
        return 'offline-fallback'

    def get_embedding(self, text: str) -> List[float]:
        """Generate a single embedding vector for a query or passage."""
        text = text.strip()
        if not text:
            return [0.0] * self.dimensions

        if self.provider == 'azure-openai':
            try:
                return self._embed_azure_openai([text])[0]
            except Exception as exc:
                logger.warning('Azure OpenAI embedding request failed: %s; falling back to offline generator', exc)
                return self._offline_vectorize(text, self.dimensions)

        if self.provider == 'openai':
            try:
                return self._embed_openai([text])[0]
            except Exception as exc:
                logger.warning('OpenAI embedding request failed: %s; falling back to offline generator', exc)
                return self._offline_vectorize(text, self.dimensions)

        if self.provider == 'gemini':
            try:
                return self._embed_gemini(text)
            except Exception as exc:
                logger.warning('Gemini embedding request failed: %s; falling back to offline generator', exc)
                return self._offline_vectorize(text, self.dimensions)

        return self._offline_vectorize(text, self.dimensions)

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts (used during catalog embedding generation)."""
        if not texts:
            return []

        if self.provider == 'azure-openai':
            try:
                return self._embed_azure_openai(texts)
            except Exception as exc:
                logger.warning('Azure OpenAI batch embedding failed: %s; falling back', exc)

        if self.provider == 'openai':
            try:
                return self._embed_openai(texts)
            except Exception as exc:
                logger.warning('OpenAI batch embedding failed: %s; falling back', exc)

        return [self._offline_vectorize(t, self.dimensions) for t in texts]

    def _embed_azure_openai(self, texts: List[str]) -> List[List[float]]:
        url = f'{self.endpoint}/openai/deployments/{self.deployment}/embeddings?api-version={self.api_version}'
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key,
        }
        body: dict[str, Any] = {
            'input': texts if len(texts) > 1 else texts[0],
            'dimensions': self.dimensions,
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode('utf-8'))
            data = payload.get('data', [])
            data.sort(key=lambda x: x.get('index', 0))
            return [item['embedding'] for item in data]

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        url = 'https://api.openai.com/v1/embeddings'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_key}',
        }
        body = {
            'model': 'text-embedding-3-small',
            'input': texts if len(texts) > 1 else texts[0],
            'dimensions': self.dimensions,
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode('utf-8'))
            data = payload.get('data', [])
            data.sort(key=lambda x: x.get('index', 0))
            return [item['embedding'] for item in data]

    def _embed_gemini(self, text: str) -> List[float]:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.gemini_key}'
        headers = {'Content-Type': 'application/json'}
        body = {
            'model': 'models/text-embedding-004',
            'content': {'parts': [{'text': text}]},
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode('utf-8'))
            embedding = payload.get('embedding', {}).get('values', [])
            if len(embedding) > self.dimensions:
                embedding = embedding[:self.dimensions]
            return _normalize(embedding)

    @staticmethod
    def _offline_vectorize(text: str, dim: int = DEFAULT_EMBEDDING_DIM) -> List[float]:
        """Deterministic, zero-dependency token hashing vectorizer.

        Normalizes text, extracts unigrams and character trigrams, hashes them across `dim` buckets,
        and applies L2 normalization. Guarantees deterministic semantic similarity for shared words/roots.
        """
        vec = [0.0] * dim
        tokens = re.findall(r'[a-zA-Z0-9_\u0900-\u097F]+', text.lower())
        if not tokens:
            return vec

        for token in tokens:
            # Word feature
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16) % dim
            vec[h] += 2.0

            # Sub-word character trigram features (captures stemming & plurals, e.g. "subsidies" ~ "subsidy")
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    trigram = token[i:i + 3]
                    th = int(hashlib.sha256(trigram.encode('utf-8')).hexdigest(), 16) % dim
                    vec[th] += 0.8

        return _normalize(vec)


def _normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm < 1e-9:
        return vec
    return [round(v / norm, 5) for v in vec]
