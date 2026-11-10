"""Builds data/epic-kingdoms.json (Mahabharata kingdoms and Ramayana places) and copies it to the sites.

Content lives in data/epic-sources/{mahabharata,ramayana}.json. This script validates it, projects each place onto the
same SVG space as frontend/public/maps/india-states.json (so markers sit on the India map) and writes the merged file to
data/, frontend/public/data/ and frontend/src/data/.

    python scripts/build_epic_atlas.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import faith_journeys_data as content  # noqa: E402
from faith_journeys_source import EPIC_GENERIC, EPIC_ROUTE_VERSES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "epic-sources"
PULLED = ROOT / "data" / "faith-sources" / "verses.json"
OUT = ROOT / "data" / "epic-kingdoms.json"
COPIES = [ROOT / "frontend" / "public" / "data", ROOT / "frontend" / "src" / "data"]
# Survey of India outline used by build_india_maps.py: (min_lon, min_lat, max_lon, max_lat) and output width.
BBOX = (68.09347709896305, 6.75436793493344, 97.41149826167937, 37.07761064660468)
WIDTH = 1000

EPICS = {
    "mahabharata": {
        "title": "Kingdoms of the Mahabharata",
        "source_text": "Mahabharata (Vyasa)",
        "toggle_label": "Mahabharata",
        "sides": {
            "pandava": {"label": "Pandava side", "colour": "#1e88e5"},
            "kaurava": {"label": "Kaurava side", "colour": "#c62828"},
            "neutral": {"label": "Neutral / unclear", "colour": "#8d8d8d"},
            "divided": {"label": "Divided / split allegiance", "colour": "#7b61a8"},
        },
        "location_field": "parva",
    },
    "ramayana": {
        "title": "Places of the Ramayana",
        "source_text": "Valmiki Ramayana",
        "toggle_label": "Ramayana",
        "sides": {
            "rama": {"label": "Rama's side", "colour": "#1e88e5"},
            "ravana": {"label": "Ravana's side", "colour": "#c62828"},
            "neutral": {"label": "Neutral / friendly non-combatants", "colour": "#8d8d8d"},
        },
        "location_field": "kanda",
    },
}
REQUIRED = ["id", "name", "name_sa", "side", "modern_location", "lat", "lon", "ruler", "role", "description"]
MAHABHARATA_SIDE = {
    "hastinapura": "kaurava", "kurukshetra": "neutral", "indraprastha": "pandava",
    "dvaraka-anarta": "divided", "mathura-shurasena": "divided", "kekaya": "divided",
    "vidarbha": "neutral", "madra": "kaurava", "yavana-shaka": "kaurava",
}
RAMAYANA_SIDE = {
    "ayodhya": "rama", "mithila": "rama", "kishkindha": "rama", "riksha-allies": "rama",
    "pampa": "rama", "rishyamukha": "rama", "rameshwaram-setu": "rama", "mahendra-hill": "rama", "vibhishana": "rama",
    "lanka": "ravana", "janasthana": "ravana", "dandakaranya": "ravana",
}
EXTRA_ENTRIES = {
    "mahabharata": [{
        "id": "yavana-shaka", "name": "Yavana and Shaka contingents", "name_sa": "\u092f\u0935\u0928-\u0936\u0915",
        "modern_location": "Northwestern frontier regions; locations approximate", "lat": 34.2, "lon": 71.4,
        "outside_india": True, "side": "kaurava", "ruler": "Northwestern chiefs; individual commanders vary",
        "role": "Yavana and Shaka contingents are named among the peoples associated with the Kaurava host; no separate akshauhini count is assigned to them.",
        "parva": "Bhishma Parva", "description": "The Sanskrit geographical and army catalogues name Yavanas and Shakas among frontier peoples. Their precise political boundaries and unit strengths are not specified here.",
        "template": "kamboja", "generic_label": "General verse naming frontier peoples in the epic",
    }],
    "ramayana": [{
        "id": "riksha-allies", "name": "Riksha allies (Jambavan)", "name_sa": "\u090b\u0915\u094d\u0937 (\u091c\u093e\u092e\u094d\u092c\u0935\u093e\u0928)",
        "modern_location": "Kishkindha region; traditional identification", "lat": 15.4, "lon": 76.8,
        "outside_india": False, "side": "rama", "ruler": "Jambavan, leader of the rikshas",
        "role": "Jambavan and the riksha allies join Rama's campaign alongside Sugriva's vanaras.",
        "kanda": "Kishkindha Kanda; Yuddha Kanda", "description": "The epic describes Jambavan as a leader among the allied forest forces. Their exact territorial organization is not mapped as a separate kingdom in the text.",
        "template": "kishkindha", "generic_label": "General verse from the Ramayana; not a place-specific quotation",
    }, {
        "id": "vibhishana", "name": "Vibhishana", "name_sa": "\u0935\u093f\u092d\u0940\u0937\u0923",
        "modern_location": "Lanka (Sri Lanka); traditional identification", "lat": 7.9, "lon": 80.7,
        "outside_india": True, "side": "rama", "ruler": "Vibhishana",
        "role": "Ravana's brother defects to Rama in Yuddha Kanda and is accepted as an ally.",
        "kanda": "Yuddha Kanda", "description": "After rejecting Ravana's course, Vibhishana seeks refuge with Rama and later rules Lanka.",
        "template": "lanka", "generic_label": "General verse from the Ramayana; not a place-specific quotation",
        "allegiance_citation": "Yuddha Kanda 17",
    }],
}
METHODOLOGY = [
    "Places are pinned at approximate modern locations; identifications of ancient janapadas are scholarly proposals, not certainties.",
    "Places outside today's India (Gandhara, Kekaya, Madra, Kamboja, Bahlika, Lanka) are drawn as hollow markers on the nearest edge of the map frame with a note.",
    "Alliances follow the epic's war narrative and are simplified; where participation is unclear a place is marked neutral / unclear.",
    "Sanskrit verses are shown only when copied verbatim from a source page listed in 'verified_from'. Where no verse about the exact place could be checked, a verified general verse of the epic is shown and labelled as such. Verse numbering follows that page's edition and may differ from the BORI critical edition.",
    "Routes join the places in the order the epic narrates them; straight segments are a schematic, not the paths the heroes walked.",
    "Descriptions and translations are original summaries, not quotations of any published translation.",
]


def fill_epic_sources(pulled: dict) -> None:
    """Gives the epic places that had no shloka a verified verse (labelled when it is a general verse of the epic)."""
    for key, spec in EPIC_GENERIC.items():
        path = SOURCES / f"{spec['epic']}.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        entry = next(e for e in raw["entries"] if e["id"] == spec["entry"])
        if entry.get("shloka"):
            continue
        got = pulled[f"epic:{key}"]
        entry["shloka"] = {"sa": got["text"], "translation": content.EPIC_TRANSLATIONS[f"epic:{key}"], "citation": spec["citation"],
                           "edition": "Numbering follows the page named in 'verified from' and may differ from the critical edition",
                           "verified_from": got["source_url"], "generic": bool(spec["generic"])}
        path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_route(epic: str, entries: list[dict], pulled: dict) -> dict:
    spec = content.EPIC_ROUTES[epic]
    by_id = {entry["id"]: entry for entry in entries}
    stops, used = [], {}
    for item in spec["stops"]:
        if "entry" in item:
            base = by_id[item["entry"]]
            shloka, approximate = base["shloka"], False
            stop = {"id": base["id"], "name": base["name"], "lat": base["lat"], "lon": base["lon"], "x": base["x"], "y": base["y"]}
        else:
            got = pulled[item["verse"]]
            shloka = {"sa": got["text"], "translation": content.EPIC_TRANSLATIONS[item["verse"]], "citation": EPIC_ROUTE_VERSES[item["verse"]]["citation"],
                      "verified_from": got["source_url"], "generic": bool(EPIC_ROUTE_VERSES[item["verse"]]["generic"])}
            approximate = bool(item.get("approximate"))
            x, y = project(item["lon"], item["lat"])
            stop = {"id": item["id"], "name": item["name"], "lat": item["lat"], "lon": item["lon"], "x": x, "y": y}
        used[stop["id"]] = used.get(stop["id"], 0) + 1
        if used[stop["id"]] > 1:
            stop["id"] = f"{stop['id']}-{used[stop['id']]}"
        legs = 0
        if stops:
            prev = stops[-1]
            p1, p2 = math.radians(prev["lat"]), math.radians(stop["lat"])
            h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(stop["lon"] - prev["lon"]) / 2) ** 2
            legs = round(12742 * math.asin(math.sqrt(h)))
        stops.append({**stop, "kind": item["kind"], "note": item["note"], "approximate": approximate, "leg_km": legs,
                      "entry": item.get("entry"), "shloka": shloka})
    return {"title": spec["title"], "summary": spec["summary"], "stops": stops}


def project(lon: float, lat: float) -> tuple[float, float]:
    min_lon, min_lat, max_lon, max_lat = BBOX
    cos_mid = math.cos(math.radians((min_lat + max_lat) / 2))
    scale = WIDTH / ((max_lon - min_lon) * cos_mid)
    return round((lon - min_lon) * cos_mid * scale, 1), round((max_lat - lat) * scale, 1)


def build() -> dict:
    pulled = json.loads(PULLED.read_text(encoding="utf-8")) if PULLED.exists() else {}
    if pulled:
        fill_epic_sources(pulled)
    epics = {}
    for epic, config in EPICS.items():
        raw = json.loads((SOURCES / f"{epic}.json").read_text(encoding="utf-8"))
        source_entries = list(raw["entries"])
        for extra in EXTRA_ENTRIES.get(epic, []):
            template = next(item for item in source_entries if item["id"] == extra["template"])
            addition = {key: value for key, value in extra.items() if key not in ("template", "generic_label")}
            addition["shloka"] = {**template["shloka"], "generic": True, "note": extra["generic_label"]}
            source_entries.append(addition)
        entries, seen = [], set()
        for entry in source_entries:
            if epic == "mahabharata" and entry["id"] in MAHABHARATA_SIDE:
                entry["side"] = MAHABHARATA_SIDE[entry["id"]]
            elif epic == "ramayana":
                entry["side"] = RAMAYANA_SIDE.get(entry["id"], "neutral")
            missing = [field for field in REQUIRED if entry.get(field) in (None, "")]
            if missing or entry["side"] not in config["sides"] or entry["id"] in seen:
                raise ValueError(f"Invalid {epic} entry {entry.get('id')}: missing={missing} side={entry.get('side')}")
            seen.add(entry["id"])
            shloka = entry.get("shloka")
            if not shloka or not all(shloka.get(key) for key in ("sa", "translation", "citation", "verified_from")):
                raise ValueError(f"Incomplete shloka for {entry['id']}")
            x, y = project(entry["lon"], entry["lat"])
            if entry["id"] == "vibhishana":
                x += 16
                y -= 16
            # Keep markers inside the frame for places west/north of the outline.
            entry = {**entry, "x": min(max(x, 14), WIDTH - 14), "y": max(y, 14), "outside_india": bool(entry.get("outside_india")),
                     "citation": shloka["citation"], "allegiance_citation": entry.get("allegiance_citation", shloka["citation"]),
                     "akshauhinis": "Not stated individually" if epic == "mahabharata" else "Not enumerated as an akshauhini",
                     "allegiance_role": entry["role"]}
            if epic == "mahabharata" and entry["id"] in ("dvaraka-anarta", "mathura-shurasena"):
                entry["allegiance_role"] = "Yadava forces were divided: Krishna and Satyaki supported the Pandavas; Balarama remained neutral, while Krishna's Narayani Sena fought for the Kauravas."
            if epic == "mahabharata" and entry["id"] == "kekaya":
                entry["allegiance_role"] = "The Kekaya brothers split between the Pandava and Kaurava alliances."
            if epic == "mahabharata" and entry["id"] == "madra":
                entry["allegiance_role"] = "Shalya led Madra; Duryodhana secured his support through a hospitality ruse before Shalya could reach the Pandavas."
            if epic == "ramayana" and entry["id"] == "dandakaranya":
                entry["allegiance_role"] = "The forest's rakshasa forces, including Khara and Dushana at Janasthana, oppose Rama."
            if epic == "ramayana" and entry["id"] == "lanka":
                entry["allegiance_role"] = "Ravana's kingdom supplies the opposing force; Vibhishana separately defects to Rama."
            if epic == "ramayana" and entry["id"] == "vibhishana":
                entry["allegiance_role"] = "Vibhishana defects from Ravana and joins Rama; the narrative is in Yuddha Kanda 17."
            entries.append(entry)
        epics[epic] = {
            "title": config["title"], "source_text": config["source_text"], "toggle_label": config["toggle_label"],
            "sides": config["sides"], "location_field": config["location_field"], "edition_note": raw.get("edition_note", ""),
            "forces": {"pandava": 7, "kaurava": 11} if epic == "mahabharata" else {},
            "entries": entries, "route": build_route(epic, entries, pulled),
        }
    return {"meta": {"title": "Epic kingdoms atlas", "methodology": METHODOLOGY}, "epics": epics}


def main() -> None:
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1)
    OUT.write_text(text, encoding="utf-8")
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for folder in COPIES:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / OUT.name).write_text(compact, encoding="utf-8")
    counts = {epic: (len(item["entries"]), sum(1 for e in item["entries"] if e.get("shloka"))) for epic, item in data["epics"].items()}
    print(f"Wrote {OUT.name}: {counts} (places, verified shlokas)")


if __name__ == "__main__":
    main()
