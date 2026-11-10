"""Copy the scripture corpus (plus group theme tags) to the static site and the React app.

Reads data/scripture-verses.json and data/catalog.json and writes the React data module.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "scripture-verses.json"
CATALOG = ROOT / "data" / "catalog.json"
OUTPUTS = [ROOT / "frontend" / "src" / "data" / "scripture-verses.json"]

GROUP_THEMES = {
    "Economic": ["economy", "markets", "fiscal", "prices", "trade"],
    "Industry Trends & Performance": ["industry", "manufacturing", "labour", "economy"],
    "Mining & Natural Resources": ["mining", "environment", "energy"],
    "Payments & Digital Banking": ["payments", "banking", "economy"],
    "State Performance & Regional Health": ["states", "governance", "health"],
    "India in Maps": ["maps", "states", "unity"],
    "Public Health & Epidemiology": ["health", "peace"],
    "Social": ["social", "education", "unity"],
    "Environment & Climate": ["environment", "water", "energy"],
    "Agriculture & Food": ["agriculture", "food", "water"],
    "Defence & Strategic": ["defence", "security", "peace"],
    "Crime & Security": ["crime", "security", "justice"],
    "Pew Research": ["opinion", "research", "data"],
    "Elections": ["elections", "governance", "unity"],
    "U.S. Elections": ["us-elections", "elections", "governance"],
    "Tourism & Heritage": ["tourism", "peace", "unity"],
    "Sports": ["sports", "effort"],
    "Cricket": ["sports", "effort"],
    "Hockey": ["sports", "effort"],
    "Football": ["sports", "effort"],
    "Innovation & Technology": ["innovation", "research", "education"],
    "Judiciary & Pending Cases": ["justice", "governance"],
    "Air Travel & Civil Aviation": ["aviation", "logistics", "trade"],
    "Indian Railways": ["railways", "logistics", "trade"],
    "Water Transport & Shipping": ["shipping", "water", "trade"],
    "Logistics & Freight": ["logistics", "trade"],
    "Union Budget": ["fiscal", "economy", "payments"],
    "Epics, Faiths & Journeys": ["peace", "unity", "justice", "tourism"],
}


def catalog_groups() -> list[str]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return [item["name"] for item in catalog["categories"]]


def build_payload() -> dict:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    # Unknown or new groups are left out on purpose: the picker falls back to every verse.
    return {"note": corpus["note"], "verses": corpus["verses"], "GROUP_THEMES": dict(GROUP_THEMES)}


def render(payload: dict) -> tuple[str, str]:
    json_text = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    js_text = "window.IJ_SCRIPTURE = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    return json_text, js_text


def main() -> None:
    json_text, _ = render(build_payload())
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json_text, encoding="utf-8", newline="\n")

    missing = [name for name in catalog_groups() if name not in GROUP_THEMES]
    print(f"Wrote React scripture data; groups using fallback: {missing or 'none'}")


if __name__ == "__main__":
    main()
