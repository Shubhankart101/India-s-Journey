"""Fetch and match source texts for the journey atlases (verification helpers)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "journey-sources" / "_cache"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, quote(unquote(parts.path), safe="/:@!$&'()*+,;=~"),
                       quote(unquote(parts.query), safe="=&:/,+"), ""))


def fetch(url: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.md5(url.encode()).hexdigest() + ".txt")
    if path.exists():
        return path.read_text(encoding="utf-8")
    last = "empty response"
    for attempt in range(3):
        try:
            request = Request(safe_url(url), headers={"User-Agent": UA})
            with urlopen(request, timeout=90) as response:
                body = response.read()
            if not body:
                raise ValueError("empty response")
            text = body.decode("utf-8", "replace")
            path.write_text(text, encoding="utf-8", newline="\n")
            return text
        except (URLError, TimeoutError, OSError, ValueError) as error:
            last = str(error)
            if attempt < 2:
                continue
    raise RuntimeError(f"could not fetch {url}: {last}")


def squash(text: str) -> str:
    """Keep only letters and combining marks so scripts and punctuation conventions do not matter."""
    text = unicodedata.normalize("NFC", text).casefold()
    text = text.replace("\u200d", "").replace("\u200c", "").replace("ṁ", "ṃ")
    return "".join(ch for ch in text if unicodedata.category(ch)[0] in "LM")


def page_text(url: str) -> str:
    body = fetch(url)
    if body.lstrip().startswith(("{", "[")):
        try:
            return json.dumps(json.loads(body), ensure_ascii=False)
        except ValueError:
            pass
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", body)


def contains(url: str, quotation: str) -> bool:
    return squash(quotation) in squash(page_text(url))


def main() -> None:
    url, quotation = sys.argv[1], sys.argv[2]
    print("OK" if contains(url, quotation) else "MISSING")


if __name__ == "__main__":
    main()
