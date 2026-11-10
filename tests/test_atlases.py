import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data"
GENERAL_ELECTIONS = [1952, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999, 2004, 2009, 2014, 2019, 2024]
DEVANAGARI = re.compile(r"[\u0900-\u097f]")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_lok_sabha_atlas_shared_outputs_match():
    source = DOCS / "lok-sabha-atlas.json"
    assert source.exists()
    for copy in (ROOT / "frontend" / "public" / "data" / "lok-sabha-atlas.json", ROOT / "frontend" / "src" / "data" / "lok-sabha-atlas.json"):
        assert copy.read_bytes() == source.read_bytes()


def test_every_general_election_is_present_or_documented():
    data = load(DOCS / "lok-sabha-atlas.json")
    present = {row["year"] for row in data["years"]}
    documented_missing = {int(str(year)[:4]) for year in data["meta"].get("missing_years", [])}
    assert set(GENERAL_ELECTIONS) <= present | documented_missing
    assert present == set(GENERAL_ELECTIONS)
    assert data["meta"]["methodology"] and any("Bombay" in line for line in data["meta"]["methodology"])


def test_lok_sabha_records_are_consistent():
    data = load(DOCS / "lok-sabha-atlas.json")
    for state, years in data["states"].items():
        for year, record in years.items():
            assert sum(record["seats"].values()) == record["total"] == len(record["list"]), (state, year)
            assert record["lead"] in record["seats"]
            assert record["seats"][record["lead"]] == max(record["seats"].values())
            for code in record["seats"]:
                assert code in data["parties"], code
    assert data["states"]["Kerala"]["2024"]["total"] == 20
    assert sum(data["years"][-1]["national"].values()) == 543


def test_epic_kingdoms_have_locations_descriptions_and_valid_shlokas():
    data = load(DOCS / "epic-kingdoms.json")
    assert (ROOT / "data" / "epic-kingdoms.json").exists()
    assert len(data["epics"]["mahabharata"]["entries"]) >= 30
    assert len(data["epics"]["ramayana"]["entries"]) >= 20
    for key, epic in data["epics"].items():
        ids = [entry["id"] for entry in epic["entries"]]
        assert len(ids) == len(set(ids))
        for entry in epic["entries"]:
            assert entry["modern_location"] and entry["description"] and entry["ruler"] and entry["role"], entry["id"]
            assert entry["side"] in epic["sides"], entry["id"]
            assert DEVANAGARI.search(entry["name_sa"]) and "\u00c3" not in entry["name_sa"], entry["id"]
            assert 0 <= entry["x"] <= 1000 and 0 <= entry["y"] <= 1115, entry["id"]
            shloka = entry["shloka"]
            assert shloka is not None, entry["id"]
            assert entry["citation"] and entry["allegiance_citation"], entry["id"]
            assert entry["akshauhinis"] and entry["allegiance_role"], entry["id"]
            assert DEVANAGARI.search(shloka["sa"]), entry["id"]
            assert shloka["citation"] and shloka["translation"], entry["id"]
            assert shloka["verified_from"].startswith("https://"), entry["id"]



def test_epic_allegiances_are_complete_and_force_totals_preserved():
    data = load(DOCS / "epic-kingdoms.json")["epics"]
    mahabharata = data["mahabharata"]
    ramayana = data["ramayana"]
    assert mahabharata["forces"] == {"pandava": 7, "kaurava": 11}
    assert {"pandava", "kaurava", "neutral", "divided"} == set(mahabharata["sides"])
    assert {"rama", "ravana", "neutral"} == set(ramayana["sides"])
    mbh = {entry["id"]: entry for entry in mahabharata["entries"]}
    assert {"panchala", "matsya", "kashi", "chedi", "magadha", "pandya", "gandhara", "madra", "sindhu-sauvira", "pragjyotisha", "kamboja", "avanti", "trigarta", "anga", "kalinga", "kosala", "shalva", "yavana-shaka"} <= set(mbh)
    assert mbh["dvaraka-anarta"]["side"] == "divided"
    assert mbh["kekaya"]["side"] == "divided"
    assert mbh["vidarbha"]["side"] == "neutral"
    assert mbh["madra"]["side"] == "kaurava"
    assert mbh["kosala"]["side"] == "neutral" and mbh["shalva"]["side"] == "neutral"
    assert "Balarama" in mbh["dvaraka-anarta"]["allegiance_role"] and "Rukmi" in mbh["vidarbha"]["ruler"]
    assert all(entry["side"] and entry["allegiance_citation"] and entry["shloka"] and entry["shloka"]["sa"] and entry["shloka"]["translation"] and entry["shloka"]["verified_from"].startswith("https://") for entry in mahabharata["entries"] + ramayana["entries"])
    ram = {entry["id"]: entry for entry in ramayana["entries"]}
    assert ram["ayodhya"]["side"] == "rama" and ram["kishkindha"]["side"] == "rama"
    assert ram["riksha-allies"]["side"] == "rama" and ram["lanka"]["side"] == "ravana"
    assert ram["janasthana"]["side"] == "ravana" and ram["dandakaranya"]["side"] == "ravana"
    assert ram["kekaya"]["side"] == "neutral" and ram["shringaverapura"]["side"] == "neutral"
    assert ram["vibhishana"]["side"] == "rama"
    assert ram["vibhishana"]["allegiance_citation"] == "Yuddha Kanda 17"
    assert ram["vibhishana"]["shloka"]["generic"] is True
    assert "Vibhishana" in ram["lanka"]["allegiance_role"]

def test_required_kingdoms_and_outside_markers():
    data = load(DOCS / "epic-kingdoms.json")["epics"]
    mbh = {entry["id"] for entry in data["mahabharata"]["entries"]}
    assert {"hastinapura", "indraprastha", "panchala", "matsya", "magadha", "gandhara", "kamboja", "manipura"} <= mbh
    ram = {entry["id"]: entry for entry in data["ramayana"]["entries"]}
    assert {"ayodhya", "mithila", "kishkindha", "lanka", "panchavati", "chitrakuta", "rameshwaram-setu"} <= set(ram)
    assert ram["lanka"]["outside_india"] is True
    assert ram["ayodhya"]["shloka"]["sa"].startswith("अयोध्या नाम नगरी")


def test_atlas_series_are_catalogued_in_their_groups():
    series = load(DOCS / "atlas-series.json")["series"]
    placement = {key: (item["meta"]["category"], item["meta"]["subgroup"], item["chartType"]) for key, item in series.items()}
    assert placement["india_lok_sabha_atlas_1952_2024"] == ("Elections", "Maps", "categorical-map")
    assert placement["india_epic_kingdoms_mahabharata"] == ("Tourism & Heritage", "Epic geography", "point-map")
    assert placement["india_epic_kingdoms_ramayana"] == ("Tourism & Heritage", "Epic geography", "point-map")
