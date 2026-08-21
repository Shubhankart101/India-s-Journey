from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FEED_URL = "https://indianmatrix.substack.com/feed"


def main() -> None:
    request = Request(FEED_URL, headers={"User-Agent": "India's Journey public RSS collector"})
    with urlopen(request, timeout=60) as response:
        root = ET.fromstring(response.read())
    channel = root.find("channel")
    articles = []
    for item in channel.findall("item"):
        published = item.findtext("pubDate") or ""
        try:
            date = parsedate_to_datetime(published).astimezone(timezone.utc).date()
        except (TypeError, ValueError):
            continue
        articles.append({
            "title": (item.findtext("title") or "Untitled article").strip(),
            "link": (item.findtext("link") or "").strip(),
            "published": published.strip(),
            "date": date.isoformat(),
        })
    articles = articles[:60]
    weekly = Counter()
    for article in articles:
        year, week, _ = datetime.fromisoformat(article["date"]).isocalendar()
        weekly[f"{year}-W{week:02d}"] += 1
    snapshot = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "feed_url": FEED_URL,
        "feed_title": (channel.findtext("title") or "Indian Matrix").strip(),
        "article_count": len(articles),
        "articles": articles,
        "cadence": {"labels": sorted(weekly), "values": [weekly[label] for label in sorted(weekly)]},
    }
    (ROOT / "data" / "indian-matrix-latest.json").write_text(json.dumps(snapshot, indent=2) + "\n")


if __name__ == "__main__":
    main()
