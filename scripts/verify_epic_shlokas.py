"""Checks every Sanskrit verse in data/epic-sources against the page named in its 'verified_from' URL.

A verse passes only if its Devanagari text (ignoring spaces, danda marks, verse numbers and joiners) appears
verbatim in that page. Pages are cached under data/epic-sources/_cache to keep reruns cheap.

    python scripts/verify_epic_shlokas.py [--drop]   # --drop rewrites the source files, nulling verses that fail
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "epic-sources"
CACHE = SOURCES / "_cache"


def squash(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    text = unicodedata.normalize("NFC", text).replace("\u200d", "").replace("\u200c", "")
    return re.sub(r"[\s|।॥\d०-९.,;:\-–—'\"()\[\]]+", "", text)


def safe_url(url: str) -> str:
    parts = urlsplit(unquote(url))
    return urlunsplit((parts.scheme, parts.netloc, quote(parts.path), quote(parts.query, safe="=&"), ""))


def fetch(url: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.md5(url.encode()).hexdigest() + ".html")
    if path.exists():
        return path.read_text(encoding="utf-8")
    last = None
    for _ in range(3):
        try:
            with urlopen(Request(safe_url(url), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}), timeout=120) as response:
                body = response.read().decode("utf-8", "replace")
            path.write_text(body, encoding="utf-8")
            return body
        except Exception as error:  # noqa: BLE001 - network flakiness; retried then reported
            last = error
            time.sleep(2)
    raise RuntimeError(f"{url}: {last}")


def shloka_records() -> list[tuple[Path, str, dict]]:
    found = []
    for path in sorted(SOURCES.rglob("*.json")):
        if "_cache" in path.parts:
            continue
        entries = json.loads(path.read_text(encoding="utf-8")).get("entries")
        if isinstance(entries, dict):
            found += [(path, key, value) for key, value in entries.items() if value]
        elif isinstance(entries, list):
            found += [(path, item["id"], item["shloka"]) for item in entries if item.get("shloka")]
    return found


def main(argv: list[str]) -> int:
    failures = []
    for path, key, shloka in shloka_records():
        try:
            ok = squash(shloka["sa"]) in squash(fetch(shloka["verified_from"]))
        except RuntimeError as error:
            ok = False
            print("  ", error)
        print("OK  " if ok else "FAIL", path.name, key, shloka["citation"])
        if not ok:
            failures.append((path, key))
    if "--drop" in argv:
        for path in {p for p, _ in failures}:
            data = json.loads(path.read_text(encoding="utf-8"))
            for _, key in [f for f in failures if f[0] == path]:
                if isinstance(data["entries"], dict):
                    data["entries"][key] = None
                else:
                    next(item for item in data["entries"] if item["id"] == key)["shloka"] = None
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(failures)} failing")
    return 1 if failures and "--drop" not in argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
