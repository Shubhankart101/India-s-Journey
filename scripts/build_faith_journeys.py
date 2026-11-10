"""Builds data/faith-journeys.json (Vedas & Upanishads, Panchatantra, Buddha, Mahavira, Sikh Gurus journey maps).

Inputs: scripts/faith_journeys_source.py (verse specs), scripts/faith_journeys_data.py (journeys, translations),
data/faith-sources/verses.json (verse text pulled by scripts/pull_faith_verses.py). Every stop must end up with an
original-language quote, our English translation, a citation and a verified_from link; nothing is ever null.

    python scripts/pull_faith_verses.py
    python scripts/build_faith_journeys.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import build_epic_atlas as epic_atlas
import faith_journeys_data as content
from faith_journeys_source import VERSES

ROOT = Path(__file__).resolve().parent.parent
PULLED = ROOT / "data" / "faith-sources" / "verses.json"
OUT = ROOT / "data" / "faith-journeys.json"
COPIES = [ROOT / "docs" / "data", ROOT / "frontend" / "public" / "data", ROOT / "frontend" / "src" / "data"]
SOURCES = ROOT / "data" / "epic-sources"
GENERIC_LABEL = "From the text (general)"
METHODOLOGY = [
    "Every verse is copied verbatim from the public page named in its 'verified from' link (Wikisource, SuttaCentral, BaniDB or the Valmiki and Mahabharata pages already used for the epic atlas); English translations are our own.",
    "Where a stage or stop has no verse we could check for that exact place, we show a verified verse from the same text and label it 'From the text (general)'.",
    "Places for ancient and traditional events are approximate identifications, not surveyed sites; stops marked approximate are drawn with a dashed ring.",
    "Borders are a cartographic convention for orientation; the basemap is Natural Earth (public domain) with India drawn from the Survey of India outline.",
    "Prakrit Jain canonical texts could not be checked against an online edition, so Mahavira's stops use the Sanskrit Tattvartha Sutra.",
]


def quote_for(stop: dict, pulled: dict) -> dict:
    verse_id = stop["verse"]
    spec, got = VERSES[verse_id], pulled[verse_id]
    quote = {
        "text": got["text"], "lang": spec["lang"], "translation": content.TRANSLATIONS[verse_id],
        "citation": spec["citation"], "work": spec["work"], "verified_from": spec["verified_from"],
        "generic": bool(stop["generic"]), "label": GENERIC_LABEL if stop["generic"] else "",
    }
    if got.get("writer"):
        quote["writer"] = got["writer"]
    if stop.get("verse_note"):
        quote["note"] = stop["verse_note"]
    return quote


def km_between(a: dict, b: dict) -> int:
    """Great-circle distance in km between two stops."""
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp, dl = p2 - p1, math.radians(b["lon"] - a["lon"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(12742 * math.asin(math.sqrt(h)))


def epic_journeys() -> list[dict]:
    """The Pandavas' and Rama's routes as journeys, built from the same stops the epic atlas draws."""
    meta = {
        "mahabharata": ("pandavas", "india_journey_pandavas", "The Pandavas\u2019 journey and battles", "Mahabharata", "#1e88e5",
                        "From Hastinapura through the house of lac, hiding at Ekachakra, Indraprastha, exile and the eighteen-day war at Kurukshetra, to the last walk toward Mount Meru."),
        "ramayana": ("rama", "india_journey_rama", "Rama\u2019s route: Ayodhya to Lanka and back", "Ramayana", "#ff9933",
                     "From Ayodhya across the Ganga and through the Dandaka forest to Panchavati, Kishkindha, the bridge to Lanka and the return."),
    }
    out = []
    atlas = epic_atlas.build()["epics"]
    for epic, (jid, series_key, title, tradition, colour, subtitle) in meta.items():
        route = atlas[epic]["route"]
        stops = []
        for stop in route["stops"]:
            q = stop["shloka"]
            stops.append({"id": stop["id"], "name": stop["name"], "lat": stop["lat"], "lon": stop["lon"],
                          "when": "Battle" if stop["kind"] == "battle" else "On the way", "description": stop["note"],
                          "approximate": bool(stop.get("approximate")),
                          "quote": {"text": q["sa"], "lang": "sa", "translation": q["translation"], "citation": q["citation"],
                                    "work": "Mahabharata" if epic == "mahabharata" else "Valmiki Ramayana", "verified_from": q["verified_from"],
                                    "generic": bool(q.get("generic")), "label": GENERIC_LABEL if q.get("generic") else ""}})
        out.append({"id": jid, "series_key": series_key, "subgroup": "Epics", "title": title, "subtitle": subtitle, "tradition": tradition,
                    "color": colour, "intro": "Stops are approximate modern identifications of places named in the epic; each verse is copied from the public text linked beside it.",
                    "routes": [{"id": "route", "label": route["title"], "colour": colour, "summary": route["summary"], "stops": stops}]})
    return out


def build() -> dict:
    pulled = json.loads(PULLED.read_text(encoding="utf-8"))
    journeys, problems = [], []
    for journey in content.JOURNEYS:
        routes = []
        for route in journey["routes"]:
            stops, seen = [], set()
            for stop in route["stops"]:
                quote = quote_for(stop, pulled)
                missing = [key for key in ("text", "lang", "translation", "citation", "verified_from") if not quote.get(key)]
                if missing or stop["id"] in seen or not (-60 <= stop["lat"] <= 70 and -30 <= stop["lon"] <= 170):
                    problems.append(f"{journey['id']}/{route['id']}/{stop['id']}: missing={missing}")
                seen.add(stop["id"])
                stops.append({"id": stop["id"], "name": stop["name"], "lat": stop["lat"], "lon": stop["lon"], "when": stop["when"],
                              "description": stop["description"], "approximate": stop["approximate"], "quote": quote})
            routes.append({**{k: route[k] for k in ("id", "label", "colour", "summary")}, "stops": stops})
        journeys.append({**{k: journey[k] for k in ("id", "series_key", "subgroup", "title", "subtitle", "tradition", "color", "intro")}, "routes": routes})
    journeys += epic_journeys()
    for journey in journeys:
        for route in journey["routes"]:
            for index, stop in enumerate(route["stops"]):
                stop["leg_km"] = km_between(route["stops"][index - 1], stop) if index else 0
    if problems:
        raise ValueError("Invalid stops:\n" + "\n".join(problems))
    return {"meta": {"title": "Faith and epic journeys", "methodology": METHODOLOGY, "basemap": "assets/maps/world-asia.json", "basemap_k": 10},
            "journeys": journeys}


def main() -> None:
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for folder in COPIES:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / OUT.name).write_text(compact, encoding="utf-8")
    stops = sum(len(r["stops"]) for j in data["journeys"] for r in j["routes"])
    generic = sum(1 for j in data["journeys"] for r in j["routes"] for s in r["stops"] if s["quote"]["generic"])
    print(f"Wrote {OUT.name}: {len(data['journeys'])} journeys, {stops} stops ({generic} labelled general)")


if __name__ == "__main__":
    main()
