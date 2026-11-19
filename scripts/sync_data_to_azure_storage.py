"""Sync all core datasets and index snapshots to Azure Blob Storage under budget."""

from __future__ import annotations

import argparse
import glob
import logging
import os
import sys

# Ensure repository root is in sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.azure_storage import AzureStorageClient, archive_dataset_to_azure

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("azure_storage_sync")

CORE_DATASETS = [
    "data/catalog.json",
    "data/catalog_embeddings.json",
    "data/infrastructure_energy_snapshot.json",
    "data/dpi_payments_snapshot.json",
    "data/market_indices_snapshot.json",
    "data/economic-survey-monthly.json",
    "data/recent-indian-elections.json",
    "data/election-indices.json",
    "data/historical-elections.json",
    "data/sports.json",
    "data/voter-roll.json",
]


def main():
    parser = argparse.ArgumentParser(description="Sync datasets to Azure Blob Storage.")
    parser.add_argument("--container", default="datasets", help="Target container name")
    parser.add_argument("--dry-run", action="store_true", help="Print files without uploading")
    args = parser.parse_args()

    client = AzureStorageClient()
    if not client.is_configured and not args.dry_run:
        logger.info("Azure Storage credentials not set. Running in zero-cost baseline mode (no-op).")
        print("Azure Storage not configured. Set AZURE_STORAGE_CONNECTION_STRING to enable cloud sync.")
        return

    synced = 0
    for rel_path in CORE_DATASETS:
        full_path = os.path.join(ROOT, rel_path)
        if not os.path.exists(full_path):
            continue
        blob_name = os.path.basename(full_path)
        if args.dry_run:
            logger.info("[Dry Run] Would upload %s -> %s/%s", full_path, args.container, blob_name)
            synced += 1
        else:
            ok = archive_dataset_to_azure(full_path, container=args.container, blob_name=blob_name)
            if ok:
                synced += 1

    print(f"Azure Storage Sync completed. {synced} dataset(s) processed.")


if __name__ == "__main__":
    main()
