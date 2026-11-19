"""Azure Blob Storage helper for pipeline dataset snapshots and backups.

Works seamlessly with:
1. `azure-storage-blob` SDK (if installed).
2. Pure standard library (urllib.request + HMAC-SHA256 Shared Key) with zero external dependencies.
3. Graceful offline fallback when Azure Storage credentials are not supplied (₹0 tier).
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import hmac
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Union

logger = logging.getLogger(__name__)


def parse_connection_string(conn_str: str) -> dict[str, str]:
    """Parse Azure Storage connection string into dictionary."""
    parts = {}
    for item in conn_str.strip().split(";"):
        if "=" in item:
            key, val = item.split("=", 1)
            parts[key.strip()] = val.strip()
    return parts


class AzureStorageClient:
    """Lightweight Azure Blob Storage client supporting both SDK and REST fallback."""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
        self.account_name = os.environ.get("AZURE_STORAGE_ACCOUNT", "")
        self.account_key = os.environ.get("AZURE_STORAGE_KEY", "")

        if self.connection_string:
            parsed = parse_connection_string(self.connection_string)
            self.account_name = parsed.get("AccountName", self.account_name)
            self.account_key = parsed.get("AccountKey", self.account_key)

    @property
    def is_configured(self) -> bool:
        return bool(self.account_name and self.account_key)

    def upload_blob(
        self,
        container: str,
        blob_name: str,
        content: Union[str, bytes],
        content_type: str = "application/json",
    ) -> bool:
        """Upload blob to Azure Storage container. Returns True on success, False if skipped/failed."""
        if not self.is_configured:
            logger.info("Azure Storage not configured; skipping cloud archival for %s/%s", container, blob_name)
            return False

        data_bytes = content.encode("utf-8") if isinstance(content, str) else content

        # Try SDK first if installed
        try:
            from azure.storage.blob import BlobServiceClient  # type: ignore

            service = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = service.get_container_client(container)
            if not container_client.exists():
                container_client.create_container()
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data_bytes, overwrite=True)
            logger.info("Uploaded %s to Azure container %s via SDK", blob_name, container)
            return True
        except ImportError:
            pass
        except Exception as exc:
            logger.warning("SDK upload failed, attempting REST API: %s", exc)

        # Fallback to direct Azure REST API with SharedKey Auth
        try:
            date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            url = f"https://{self.account_name}.blob.core.windows.net/{container}/{blob_name}"

            # Canonicalized string for SharedKey authentication (2020-10-28 version)
            # VERB + "\n" + Content-Encoding + "\n" + Content-Language + "\n" + Content-Length + "\n" + Content-MD5 + "\n"
            # Content-Type + "\n" + Date + "\n" + If-Modified-Since + "\n" + If-Match + "\n" + If-None-Match + "\n"
            # If-Unmodified-Since + "\n" + Range + "\n" + CanonicalizedHeaders + "\n" + CanonicalizedResource
            string_to_sign = (
                f"PUT\n\n\n{len(data_bytes)}\n\n{content_type}\n\n\n\n\n\n\n"
                f"x-ms-blob-type:BlockBlob\nx-ms-date:{date_str}\nx-ms-version:2020-10-28\n"
                f"/{self.account_name}/{container}/{blob_name}"
            )

            decoded_key = base64.b64decode(self.account_key)
            signature = base64.b64encode(
                hmac.new(decoded_key, string_to_sign.encode("utf-8"), hashlib.sha256).digest()
            ).decode("utf-8")

            req = urllib.request.Request(
                url,
                data=data_bytes,
                method="PUT",
                headers={
                    "x-ms-blob-type": "BlockBlob",
                    "x-ms-date": date_str,
                    "x-ms-version": "2020-10-28",
                    "Content-Type": content_type,
                    "Content-Length": str(len(data_bytes)),
                    "Authorization": f"SharedKey {self.account_name}:{signature}",
                },
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201):
                    logger.info("Successfully uploaded %s to Azure container %s via REST API", blob_name, container)
                    return True
                logger.warning("Azure REST API returned HTTP %s for %s", resp.status, blob_name)
                return False
        except Exception as exc:
            logger.error("Failed to upload blob %s to Azure: %s", blob_name, exc)
            return False


def archive_dataset_to_azure(
    local_path: str,
    container: str = "datasets",
    blob_name: Optional[str] = None,
) -> bool:
    """Convenience helper to upload a local file to Azure Storage."""
    if not os.path.exists(local_path):
        return False
    target_name = blob_name or os.path.basename(local_path)
    client = AzureStorageClient()
    with open(local_path, "rb") as f:
        data = f.read()
    content_type = "application/json" if local_path.endswith(".json") else "application/octet-stream"
    return client.upload_blob(container, target_name, data, content_type)
