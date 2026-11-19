"""Management command to pre-compute vector embeddings for all indicators in data/catalog.json.

Can be run locally, in CI, or during Azure App Service container build.
Usage:
    python webapp/manage.py build_catalog_embeddings [--output data/catalog_embeddings.json] [--limit N]
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from indicators.ai.azure_client import DEFAULT_EMBEDDING_DIM, AzureAIClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Pre-compute vector embeddings for 3,082 indicators from data/catalog.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=str(Path(settings.BASE_DIR).parent / 'data' / 'catalog_embeddings.json'),
            help='Output path for the generated catalog embeddings JSON file',
        )
        parser.add_argument(
            '--catalog',
            type=str,
            default=str(Path(settings.BASE_DIR).parent / 'data' / 'catalog.json'),
            help='Input catalog JSON path',
        )
        parser.add_argument(
            '--dimensions',
            type=int,
            default=DEFAULT_EMBEDDING_DIM,
            help=f'Embedding vector dimensionality (default: {DEFAULT_EMBEDDING_DIM})',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of indicators to embed (useful for quick dry runs)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=64,
            help='Batch size for remote embedding API calls',
        )

    def handle(self, *args, **options):
        output_path = Path(options['output'])
        catalog_path = Path(options['catalog'])
        dim = options['dimensions']
        limit = options['limit']
        batch_size = options['batch_size']

        if not catalog_path.is_file():
            self.stderr.write(self.style.ERROR(f'Catalog file not found at: {catalog_path}'))
            sys.exit(1)

        self.stdout.write(self.style.NOTICE(f'Loading catalog from {catalog_path}...'))
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        indicators_raw = catalog.get('indicators', [])
        if isinstance(indicators_raw, dict):
            indicators_list = list(indicators_raw.values())
        else:
            indicators_list = list(indicators_raw)

        total_count = len(indicators_list)
        self.stdout.write(f'Found {total_count} indicators in catalog.')

        client = AzureAIClient(dimensions=dim)
        self.stdout.write(self.style.SUCCESS(f'Using AI embedding provider: {client.provider} (dimensions={dim})'))

        if limit is not None:
            indicators_list = indicators_list[:limit]
            self.stdout.write(f'Limiting embedding run to first {limit} indicators.')

        embedded_items = []
        start_time = time.time()

        for idx, meta in enumerate(indicators_list):
            if not isinstance(meta, dict):
                continue
            key = meta.get('key', '')
            title = meta.get('title', '')
            subtitle = meta.get('subtitle', '')
            subgroup = meta.get('subgroup', '')
            category = meta.get('category', '')
            details = meta.get('details', '')
            note = meta.get('note', '')

            text_to_embed = f"{title}. {subtitle}. Group: {category}. Subgroup: {subgroup}. Details: {details} {note}".strip()
            vec = client.get_embedding(text_to_embed)

            embedded_items.append({
                'key': key,
                'title': title,
                'subtitle': subtitle,
                'category': category,
                'subgroup': subgroup,
                'frequency': meta.get('frequency', ''),
                'unit': meta.get('unit', '') or meta.get('suffix', ''),
                'source': meta.get('source', ''),
                'vec': vec,
            })

            if (idx + 1) % 500 == 0 or (idx + 1) == len(indicators_list):
                self.stdout.write(f'Processed {idx + 1}/{len(indicators_list)} indicators...')

        output_payload = {
            'version': '1.0',
            'provider': client.provider,
            'dimensions': dim,
            'count': len(embedded_items),
            'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'indicators': embedded_items,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_payload, f, separators=(',', ':'))

        elapsed = round(time.time() - start_time, 2)
        size_kb = round(os.path.getsize(output_path) / 1024, 1)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully wrote {len(embedded_items)} embeddings to {output_path} '
            f'({size_kb} KB in {elapsed}s)'
        ))
