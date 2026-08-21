from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.pewresearch.org/search/india/"
USER_AGENT = "India's Journey Pew India report catalog"


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def main() -> None:
    reports = {}
    for page_number in range(1, 147):
        url = BASE_URL if page_number == 1 else f"{BASE_URL}page/{page_number}/"
        try:
            html = fetch(url)
        except Exception:
            continue
        matches = re.findall(
            r'<h2[^>]*class="[^"]*header[^"]*"[^>]*>\s*<a href="(https://www\.pewresearch\.org/[^"]+)"[^>]*>(.*?)</a>',
            html,
            flags=re.I | re.S,
        )
        for link, raw_title in matches:
            title = re.sub(r"<[^>]+>", " ", raw_title)
            title = re.sub(r"\s+", " ", title).strip()
            date_match = re.search(r"/((?:19|20)\d{2})/(\d{2})/(\d{2})/", link)
            if not date_match:
                continue
            date = "-".join(date_match.groups())
            reports[link] = {"title": title, "link": link, "date": date}
    ordered = sorted(reports.values(), key=lambda item: (item["date"], item["title"]), reverse=True)
    counts = Counter(item["date"][:4] for item in ordered)
    snapshot = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "Pew Research Center public India search results",
        "search_url": BASE_URL,
        "report_count": len(ordered),
        "reports": ordered,
        "cadence": {"labels": sorted(counts), "values": [counts[label] for label in sorted(counts)]},
    }
    (ROOT / "data" / "pew-india-reports.json").write_text(json.dumps(snapshot, indent=2) + "\n")


if __name__ == "__main__":
    main()
