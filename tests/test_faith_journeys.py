import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUP = "Epics, Faiths & Journeys"
SUBGROUPS = {
    "Epics: Mahabharata & Ramayana",
    "Vedic & Upanishadic Journeys",
    "Buddhist Journeys",
    "Jain Journeys",
    "Sikh Journeys",
    "Folk & Story Traditions",
}
EXPECTED_JOURNEYS = {"vedas-upanishads", "panchatantra", "buddha", "mahavira", "sikh-gurus", "pandavas", "rama"}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def all_routes():
    for journey in load("data/faith-journeys.json")["journeys"]:
        for route in journey["routes"]:
            yield journey, route


def test_expected_journeys_present():
    ids = {journey["id"] for journey in load("data/faith-journeys.json")["journeys"]}
    assert EXPECTED_JOURNEYS <= ids


def test_every_stop_has_a_verified_verse_and_source():
    for journey, route in all_routes():
        assert len(route["stops"]) >= 2, route["id"]
        for stop in route["stops"]:
            where = f"{journey['id']}/{route['id']}/{stop['name']}"
            quote = stop.get("quote")
            assert quote, where
            for field in ("text", "translation", "citation", "work", "lang"):
                assert str(quote.get(field) or "").strip(), f"{where}: empty {field}"
            assert str(quote.get("verified_from", "")).startswith("http"), where
            assert -90 <= stop["lat"] <= 90 and -180 <= stop["lon"] <= 180, where
            assert stop["description"].strip() and stop["when"].strip(), where
            assert "?" * 3 not in json.dumps(stop, ensure_ascii=False), where


def test_routes_are_ordered_with_unique_stop_ids():
    for journey, route in all_routes():
        ids = [stop["id"] for stop in route["stops"]]
        assert len(ids) == len(set(ids)), f"duplicate stop ids in {journey['id']}/{route['id']}"
        assert route["stops"][0]["leg_km"] == 0
        assert all(stop["leg_km"] > 0 for stop in route["stops"][1:]), route["id"]


def test_epic_atlas_has_no_missing_shlokas_and_routes():
    epics = load("data/epic-kingdoms.json")["epics"]
    total = 0
    for key, epic in epics.items():
        for entry in epic["entries"]:
            total += 1
            shloka = entry.get("shloka")
            assert shloka and shloka["sa"] and shloka["translation"] and shloka["verified_from"].startswith("http"), entry["id"]
        stops = epic["route"]["stops"]
        assert len(stops) >= 8, key
        for stop in stops:
            assert stop["shloka"] and stop["shloka"]["verified_from"].startswith("http"), stop["id"]
    assert total == 58


def test_group_is_present_among_eleven():
    catalog = load("data/catalog.json")
    names = [category["name"] for category in catalog["categories"]]
    assert len(names) == 11 and GROUP in names
    category = next(item for item in catalog["categories"] if item["name"] == GROUP)
    assert {sub["name"] for sub in category["subgroups"]} == SUBGROUPS
    members = [item for item in catalog["indicators"] if item["category"] == GROUP]
    kinds = {item["series"]["chart_type"] for item in members}
    assert {"journey-map", "point-map"} <= kinds
    map_ids = {item["series"]["labels"][0] for item in members if item["series"]["chart_type"] == "journey-map"}
    assert map_ids == EXPECTED_JOURNEYS
    assert {item["subgroup"] for item in members} == SUBGROUPS


def test_old_epic_location_still_resolves():
    aliases = load("data/catalog.json")["legacy_aliases"]
    target = aliases["subgroups"].get("Tourism & Heritage|Epic geography")
    assert target and target["group"] == GROUP
