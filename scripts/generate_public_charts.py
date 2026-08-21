from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CHART_DIR = ROOT / "assets" / "charts"
USER_AGENT = "PolityPolicyUpdate public data dashboard"


def get_json(url: str) -> object:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def get_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def svg_chart(title: str, subtitle: str, labels: list[str], values: list[float], color: str, value_suffix: str) -> str:
    width, height, padding = 960, 360, 62
    chart_width, chart_height = width - padding * 2, height - padding * 2
    maximum = max(values) if values else 1
    minimum = min(0, min(values)) if values else 0
    span = max(maximum - minimum, 1)
    points = []
    for index, value in enumerate(values):
        x = padding + (chart_width * index / max(len(values) - 1, 1))
        y = padding + chart_height - ((value - minimum) / span * chart_height)
        points.append((x, y))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{padding},{padding + chart_height} {line} {padding + chart_width},{padding + chart_height}"
    grid = []
    for index in range(5):
        y = padding + chart_height * index / 4
        value = maximum - span * index / 4
        grid.append(f'<line x1="{padding}" y1="{y:.1f}" x2="{padding + chart_width}" y2="{y:.1f}" stroke="#263241" stroke-width="1"/>')
        grid.append(f'<text x="{padding - 12}" y="{y + 4:.1f}" text-anchor="end" fill="#9da7b3" font-size="11">{value:.1f}{value_suffix}</text>')
    x_labels = []
    for index, label in enumerate(labels):
        if index == 0 or index == len(labels) - 1 or index % max(len(labels) // 5, 1) == 0:
            x = padding + chart_width * index / max(len(labels) - 1, 1)
            x_labels.append(f'<text x="{x:.1f}" y="{height - 22}" text-anchor="middle" fill="#9da7b3" font-size="11">{label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
  <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
  <text x="{padding}" y="30" fill="#e6edf3" font-size="18" font-family="system-ui, sans-serif" font-weight="700">{title}</text>
  <text x="{padding}" y="50" fill="#9da7b3" font-size="12" font-family="system-ui, sans-serif">{subtitle}</text>
  {''.join(grid)}
  <polygon points="{area}" fill="{color}" opacity="0.16"/>
  <polyline points="{line}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  {''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>' for x, y in points)}
  {''.join(x_labels)}
</svg>'''


def build_cpi_chart() -> dict:
    payload = get_json("https://api.worldbank.org/v2/country/IND/indicator/FP.CPI.TOTL.ZG?format=json&per_page=100")
    rows = [row for row in payload[1] if row["value"] is not None]
    rows = sorted(rows, key=lambda row: int(row["date"]))[-15:]
    labels = [row["date"] for row in rows]
    values = [float(row["value"]) for row in rows]
    svg = svg_chart(
        "India CPI Inflation",
        "Annual consumer-price inflation; World Bank indicator FP.CPI.TOTL.ZG",
        labels,
        values,
        "#63b3ed",
        "%",
    )
    (CHART_DIR / "india-cpi-inflation.svg").write_text(svg)
    return {"source": "World Bank API FP.CPI.TOTL.ZG", "years": labels, "values": values}


def build_world_bank_chart(indicator: str, file_name: str, title: str, subtitle: str, color: str, suffix: str) -> dict:
    payload = get_json(f"https://api.worldbank.org/v2/country/IND/indicator/{indicator}?format=json&per_page=100")
    rows = [row for row in payload[1] if row["value"] is not None]
    rows = sorted(rows, key=lambda row: int(row["date"]))[-15:]
    labels = [row["date"] for row in rows]
    values = [float(row["value"]) for row in rows]
    (CHART_DIR / file_name).write_text(svg_chart(title, subtitle, labels, values, color, suffix))
    return {"source": f"World Bank API {indicator}", "years": labels, "values": values}


def build_substack_chart() -> dict:
    feed = ET.fromstring(get_bytes("https://politypolicy.substack.com/feed"))
    dates = []
    for item in feed.find("channel").findall("item"):
        value = item.findtext("pubDate")
        if value:
            dates.append(parsedate_to_datetime(value).astimezone(timezone.utc).date())
    today = datetime.now(timezone.utc).date()
    weeks = [today - timedelta(days=7 * index) for index in range(11, -1, -1)]
    counts = []
    labels = []
    for week in weeks:
        end = week + timedelta(days=6)
        counts.append(sum(week <= published <= end for published in dates))
        labels.append(week.strftime("%d %b"))
    svg = svg_chart(
        "Polity and Policy Publication Cadence",
        "Public articles from the weekly RSS feed; rolling 12-week view",
        labels,
        counts,
        "#2ea44f",
        "",
    )
    (CHART_DIR / "substack-publication-cadence.svg").write_text(svg)
    return {"feed": "https://politypolicy.substack.com/feed", "weeks": labels, "article_counts": counts}


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result = {"generated_at_utc": generated, "series": {}}
    indicators = [
        ("cpi", "FP.CPI.TOTL.ZG", "india-cpi-inflation.svg", "India CPI Inflation", "Annual consumer-price inflation; World Bank indicator FP.CPI.TOTL.ZG", "#63b3ed", "%"),
        ("trade", "NE.TRD.GNFS.ZS", "india-trade-share-gdp.svg", "India Trade Share of GDP", "Exports plus imports as share of GDP; World Bank indicator NE.TRD.GNFS.ZS", "#2ea44f", "%"),
        ("forex", "FI.RES.TOTL.CD", "india-foreign-reserves.svg", "India Foreign Exchange Reserves", "Total reserves including gold; World Bank indicator FI.RES.TOTL.CD", "#63b3ed", ""),
        ("bank_credit", "FS.AST.PRVT.GD.ZS", "india-domestic-credit.svg", "India Domestic Credit", "Domestic credit to private sector as share of GDP; World Bank indicator FS.AST.PRVT.GD.ZS", "#a371f7", "%"),
        ("iip", "NV.IND.TOTL.KD.ZG", "india-industrial-growth.svg", "India Industrial Value Added Growth", "Annual industrial value-added growth; World Bank indicator NV.IND.TOTL.KD.ZG", "#f56c6c", "%"),
    ]
    for key in ["gst", "fiscal_deficit", "rupee", "wpi", "upi"]:
        result["series"][key] = {"error": "Official export adapter pending"}
    for key, indicator, file_name, title, subtitle, color, suffix in indicators:
        try:
            series = build_world_bank_chart(indicator, file_name, title, subtitle, color, suffix)
            result["series"][key] = {"labels": series["years"], "values": series["values"], "source": series["source"]}
        except Exception as error:
            result["series"][key] = {"error": str(error)}
    (ROOT / "data" / "chart-latest.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
