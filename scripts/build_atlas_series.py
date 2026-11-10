"""Write data/atlas-series.json: the catalog series for the Lok Sabha and epic atlases.

Run after build_lok_sabha_atlas.py and build_epic_atlas.py. The atlases themselves
render from data/lok-sabha-atlas.json and data/epic-kingdoms.json; these
series only give them a catalog entry (title, group, subgroup, source, note).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EPICS = [
    ("india_epic_kingdoms_mahabharata", "mahabharata", "Kingdoms of the Mahabharata",
     "Pandava side, Kaurava side and neutral kingdoms pinned on the map of India"),
    ("india_epic_kingdoms_ramayana", "ramayana", "Kingdoms and places of the Ramayana",
     "Kosala, Kishkindha, Lanka and the ashramas of Rama's journey, pinned on the map"),
]


GROUP = "Epics, Faiths & Journeys"
JOURNEY_SUBGROUP = {
    "pandavas": "Epics: Mahabharata & Ramayana", "rama": "Epics: Mahabharata & Ramayana",
    "vedas-upanishads": "Vedic & Upanishadic Journeys", "buddha": "Buddhist Journeys", "mahavira": "Jain Journeys",
    "sikh-gurus": "Sikh Journeys", "panchatantra": "Folk & Story Traditions",
}


def journey_series():
    """One interactive journey map per journey, plus small bar charts of the distance of each leg."""
    data = json.loads((DATA / "faith-journeys.json").read_text(encoding="utf-8"))
    series = {}
    for journey in data["journeys"]:
        sub = JOURNEY_SUBGROUP[journey["id"]]
        stops = [stop for route in journey["routes"] for stop in route["stops"]]
        generic = sum(1 for stop in stops if stop["quote"]["generic"])
        series[journey["series_key"]] = {
            "labels": [journey["id"]], "values": [len(stops)], "chartType": "journey-map", "scope": "module",
            "source": stops[0]["quote"]["verified_from"],
            "note": (f"{journey['subtitle']}. {len(stops)} stops across {len(journey['routes'])} route(s); press play or drag the slider to follow the "
                     f"journey, and click a stop for its description and a verse copied from a public text ({generic} stops show a general verse of the text, labelled as such)."),
            "meta": {"title": journey["title"], "subtitle": journey["subtitle"], "frequency": "Journey", "color": journey["color"],
                     "suffix": " stops", "category": GROUP, "subgroup": sub},
        }
        for route in journey["routes"]:
            if len(route["stops"]) < 3 or (journey["id"] == "sikh-gurus" and route["id"] != "nanak"):
                continue
            suffix = "" if len(journey["routes"]) == 1 else f"_{route['id'].replace('-', '_')}"
            label = journey["title"] if len(journey["routes"]) == 1 else f"{journey['title']} ({route['label']})"
            series[f"{journey['series_key']}{suffix}_leg_km"] = {
                "labels": [stop["name"] for stop in route["stops"][1:]], "values": [stop["leg_km"] for stop in route["stops"][1:]],
                "chartType": "bar", "scope": "module", "source": route["stops"][0]["quote"]["verified_from"],
                "note": "Straight-line (great-circle) distance between consecutive stops: a schematic of how far each leg is, not the walked route.",
                "meta": {"title": f"{label}: kilometres per leg", "subtitle": f"Distance from each stop to the next, {route['label']}",
                         "frequency": "Per leg", "color": route["colour"], "suffix": " km", "category": GROUP, "subgroup": sub},
            }
    gurus = next(j for j in data["journeys"] if j["id"] == "sikh-gurus")["routes"]
    names = [route["label"].split(" (")[0] for route in gurus]
    source = gurus[0]["stops"][0]["quote"]["verified_from"]
    series["india_journey_sikh_gurus_km_by_guru"] = {
        "labels": names, "values": [sum(s["leg_km"] for s in route["stops"]) for route in gurus],
        "chartType": "bar", "scope": "module", "source": source,
        "note": "Total straight-line distance between the key places associated with each Guru; Guru Nanak\u2019s four udasis dominate.",
        "meta": {"title": "The ten Sikh Gurus: distance covered between key places", "subtitle": "Sum of leg distances per Guru",
                 "frequency": "Per Guru", "color": "#e07b00", "suffix": " km", "category": GROUP, "subgroup": "Sikh Journeys"},
    }
    series["india_journey_sikh_gurus_stops_by_guru"] = {
        "labels": names, "values": [len(route["stops"]) for route in gurus],
        "chartType": "bar", "scope": "module", "source": source, "note": "Number of key places mapped for each Guru.",
        "meta": {"title": "The ten Sikh Gurus: key places mapped", "subtitle": "Stops per Guru", "frequency": "Per Guru",
                 "color": "#e07b00", "suffix": " places", "category": GROUP, "subgroup": "Sikh Journeys"},
    }
    return series


def main():
    series = {}
    lok = json.loads((DATA / "lok-sabha-atlas.json").read_text(encoding="utf-8"))
    years = lok["years"]
    series["india_lok_sabha_atlas_1952_2024"] = {
        "labels": [row["label"] for row in years],
        "values": [row["seats_counted"] for row in years],
        "chartType": "categorical-map",
        "scope": "module",
        "source": lok["meta"]["sources"][0]["url"],
        "note": (f"Each State/UT is shaded by the party that won the most Lok Sabha seats there, for {len(years)} general elections "
                 f"({years[0]['label']}-{years[-1]['label']}). Click a State/UT for seats by party and seat-by-seat winners. "
                 "Old states are mapped onto today's State/UT boundaries; see the methodology in the atlas."),
        "meta": {"title": "Lok Sabha elections by state, 1952\u20132024",
                 "subtitle": "Winning party by State/UT for every general election",
                 "frequency": "Per Lok Sabha election", "color": "#ff9933", "suffix": " seats",
                 "category": "Elections", "subgroup": "Maps"},
    }
    epic_data = json.loads((DATA / "epic-kingdoms.json").read_text(encoding="utf-8"))["epics"]
    for key, epic, title, subtitle in EPICS:
        entries = epic_data[epic]["entries"]
        verified = [e for e in entries if e.get("shloka")]
        series[key] = {
            "labels": [e["name"] for e in entries],
            "values": [1] * len(entries),
            "chartType": "point-map",
            "scope": "module",
            "source": verified[0]["shloka"]["verified_from"] if verified else "",
            "note": (f"{len(entries)} places pinned at approximate modern locations; each carries a Sanskrit verse copied verbatim from an online text of the original epic "
                     f"({len(verified) - sum(1 for e in entries if e['shloka'].get('generic'))} about the place itself, the rest general verses of the epic, labelled). "
                     "Click a pin for the ruler, role in the epic, description and shloka, or trace the hero's route with the play button."),
            "meta": {"title": title, "subtitle": subtitle, "frequency": "Epic geography",
                     "color": next(iter(epic_data[epic]["sides"].values()))["colour"], "suffix": " places",
                     "category": "Tourism & Heritage", "subgroup": "Epic geography"},
        }
    series.update(journey_series())
    out = DATA / "atlas-series.json"
    out.write_text(json.dumps({"series": series}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Wrote", out.relative_to(ROOT), list(series))


if __name__ == "__main__":
    main()
