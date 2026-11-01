"""Shared helpers for the official sports-source fetchers.

Every fetcher module in this package exposes:

* ``SNAPSHOT``: the file name written to ``data/sports_sources/``;
* ``PRODUCERS``: a mapping of series key to a zero-argument function that downloads
  one series from its official publisher and returns it in the snapshot schema
  (or a list of such series when one download yields several);
* ``NOT_AVAILABLE`` (optional): items the publishers do not expose, with reasons.

Only the Python standard library is used so the scheduled GitHub workflow needs no installs.
"""
from __future__ import annotations

import gzip
import json
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = ROOT / "data" / "sports_sources"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 IndiasJourneyDashboard/1.0 (+https://github.com/Shubhankart101/India-s-Journey)"
)


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def fetch(url: str, *, headers: dict | None = None, data: bytes | None = None, timeout: int = 45, retries: int = 3) -> bytes:
    """GET (or POST when ``data`` is given) with retries and gzip support."""
    merged = {"User-Agent": USER_AGENT, "Accept": "*/*", "Accept-Encoding": "gzip", "Accept-Language": "en"}
    merged.update(headers or {})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(Request(url, data=data, headers=merged), timeout=timeout) as response:
                body = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return body
        except (HTTPError, URLError, TimeoutError, ConnectionError) as exc:
            last = exc
            if isinstance(exc, HTTPError) and exc.code in (400, 401, 403, 404):
                break
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{url}: {last}")


def fetch_text(url: str, **kwargs) -> str:
    return fetch(url, **kwargs).decode("utf-8", errors="replace")


def fetch_json(url: str, **kwargs):
    return json.loads(fetch(url, **kwargs).decode("utf-8", errors="replace"))


class TableParser(HTMLParser):
    """Collects every <table> as a list of rows of cell text (th and td)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._stack: list[list[list[str]]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            table: list[list[str]] = []
            self.tables.append(table)
            self._stack.append(table)
        elif tag == "tr" and self._stack:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row and self._stack:
                self._stack[-1].append(self._row)
            self._row = None
        elif tag == "table" and self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def html_tables(html: str) -> list[list[list[str]]]:
    parser = TableParser()
    parser.feed(html)
    return parser.tables


def number(value, default=None):
    """Parse '1,234', '45.6', '102*' or '-' into a number."""
    text = str(value).replace(",", "").replace("*", "").replace("+", "").strip()
    if text in ("", "-", "\u2013"):
        return default
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return default


def series(key: str, sport: str, title: str, description: str, labels, datasets, *, chart: str = "bar",
           source_url: str, publisher: str, as_of: str | None = None, notes: str = "", **extra) -> dict:
    """Build one snapshot series. ``datasets`` is a list of (label, values) pairs or dicts."""
    rows = [ds if isinstance(ds, dict) else {"label": ds[0], "values": list(ds[1])} for ds in datasets]
    labels = [str(label) for label in labels]
    if not labels:
        raise ValueError(f"{key}: no rows returned")
    for row in rows:
        if len(row["values"]) != len(labels):
            raise ValueError(f"{key}: dataset {row['label']} has {len(row['values'])} values for {len(labels)} labels")
    out = {"key": key, "sport": sport, "title": title, "description": description, "labels": labels, "datasets": rows,
           "chart": chart, "source_url": source_url, "publisher": publisher, "as_of": as_of or f"fetched {today()}", "notes": notes}
    out.update(extra)
    return out


def load_snapshot(name: str) -> dict:
    path = SNAPSHOT_DIR / name
    if not path.exists():
        return {"series": [], "not_available": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_snapshot(name: str, payload: dict) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / name
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return path
