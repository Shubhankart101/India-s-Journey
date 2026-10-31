from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from rss_utils import fetch_rss_or_none

ROOT = Path(__file__).resolve().parents[1]
FEED_URL = "https://indianmatrix.substack.com/feed"


def main() -> None:
    root = fetch_rss_or_none(FEED_URL, "India's Journey public RSS collector")
    if root is None:
        return
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
    snapshot_text = json.dumps(snapshot, indent=2) + "\n"
    (ROOT / "data" / "indian-matrix-latest.json").write_text(snapshot_text)
    (ROOT / "docs" / "data" / "indian-matrix-latest.json").write_text(snapshot_text)


if __name__ == "__main__":
    main()
