"""Deploys the web app to a Hugging Face Docker Space.

Usage: ``python scripts/deploy_hf_space.py [--space owner/name]``. Authenticate first with ``hf auth login``
or by setting ``HF_TOKEN`` (a token with write access).
"""
from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
SPACE_README = ROOT / "huggingface" / "README.md"
BACKUP_SITE_URL = "https://shubhankart101.github.io/India-s-Journey/"
VARIABLES = {
    "DJANGO_SQLITE_PATH": "/tmp/db.sqlite3",
    "DJANGO_FRAME_ANCESTORS": "https://huggingface.co",
    "BACKUP_SITE_URL": BACKUP_SITE_URL,
    "BACKUP_STATUS_URL": f"{BACKUP_SITE_URL}status.html",
    "MICROSOFT_TENANT": "common",
}


def stage(target: Path) -> int:
    files = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout.decode().split("\0")
    count = 0
    for name in filter(None, files):
        source = ROOT / name
        if not source.is_file():
            continue
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        count += 1
    # The Space README needs Hugging Face front matter, so it replaces the GitHub README.
    shutil.copy2(SPACE_README, target / "README.md")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--space", help="Space id (owner/name); defaults to <your user>/indiasjourney")
    args = parser.parse_args()

    api = HfApi(token=os.environ.get("HF_TOKEN"))
    space = args.space or f"{api.whoami()['name']}/indiasjourney"
    is_new = not api.repo_exists(space, repo_type="space")
    api.create_repo(space, repo_type="space", space_sdk="docker", exist_ok=True)
    if is_new:
        api.add_space_secret(space, "DJANGO_SECRET_KEY", secrets.token_urlsafe(50))
    for key, value in VARIABLES.items():
        api.add_space_variable(space, key, value)

    with tempfile.TemporaryDirectory() as tmp:
        count = stage(Path(tmp))
        api.upload_folder(
            repo_id=space,
            repo_type="space",
            folder_path=tmp,
            commit_message="Deploy from GitHub",
            delete_patterns=["*", "**/*"],
        )
    print(f"Uploaded {count} files to https://huggingface.co/spaces/{space}")
    print(f"App URL: https://{space.replace('/', '-').replace('_', '-').lower()}.hf.space")


if __name__ == "__main__":
    main()
