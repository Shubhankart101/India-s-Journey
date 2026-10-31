from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

from rss_utils import fetch_rss_or_none

ROOT = Path(__file__).resolve().parents[1]
FEED_URL = "https://politypolicy.substack.com/feed"


def main() -> None:
    root = fetch_rss_or_none(FEED_URL, "India's Journey Polity and Policy RSS collector")
    if root is None:
        return
    channel = root.find("channel")
    items = []
    for item in channel.findall("item")[:20]:
        title = (item.findtext("title") or "Untitled article").strip()
        link = (item.findtext("link") or "").strip()
        published = (item.findtext("pubDate") or "").strip()
        description = re.sub(r"\s+", " ", unescape(item.findtext("description") or "")).strip()
        items.append({"title": title, "link": link, "published": published, "description": description})

    now = datetime.now(timezone.utc).replace(microsecond=0)
    snapshot = {
        "generated_at_utc": now.isoformat(),
        "feed_url": FEED_URL,
        "feed_title": (channel.findtext("title") or "Polity and Policy by Tushar Gupta").strip(),
        "feed_last_build_date": (channel.findtext("lastBuildDate") or "").strip(),
        "article_count": len(items),
        "articles": items,
    }
    snapshot_text = json.dumps(snapshot, indent=2) + "\n"
    (ROOT / "data" / "substack-latest.json").write_text(snapshot_text)
    (ROOT / "docs" / "data" / "substack-latest.json").write_text(snapshot_text)
    print(f"Generated: data/substack-latest.json & docs/data/substack-latest.json ({len(items)} articles)")


if __name__ == "__main__":
    main()
