#!/usr/bin/env python3
"""Record homepage reachability in data/latest.json and data/latest-status.json."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://politypolicy.com/"
OUTPUTS = (ROOT / "data" / "latest.json", ROOT / "data" / "latest-status.json")


def status_payload() -> dict:
    status: int | str = "error"
    error = ""
    request = Request(URL, headers={"User-Agent": "PolityPolicyUpdate public monitor"})
    try:
        with urlopen(request, timeout=30) as response:
            status = response.status
    except HTTPError as exc:
        status = exc.code
        error = f"HTTP {exc.code}: {exc.reason}"
    except URLError as exc:
        error = str(exc.reason)
    except TimeoutError as exc:
        error = str(exc) or "request timed out"
    if status == "error":
        raise RuntimeError(error or "homepage check failed")
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "site": URL,
        "homepage_status": status,
        "collection_status": "ok" if status == 200 else "partial_or_blocked",
        "collection_errors": [error] if error else [],
    }


def stable(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key != "generated_at_utc"}


def run(offline: bool = False) -> int:
    existing = None
    for path in OUTPUTS:
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                break
            except (OSError, json.JSONDecodeError):
                continue
    if offline:
        print("offline: retained cached site status" if existing else "offline: no site-status cache; skipped")
        return 0
    try:
        payload = status_payload()
    except Exception as error:
        print(f"warning: {error}; retained existing site status")
        return 0
    if existing is not None and stable(existing) == stable(payload):
        print("site status unchanged")
        return 0
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="retain the current status without contacting the site")
    args = parser.parse_args()
    return run(args.offline)


if __name__ == "__main__":
    raise SystemExit(main())
