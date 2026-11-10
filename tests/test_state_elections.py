import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "frontend" / "public" / "data" / "state-elections"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def state_files():
    return sorted(p for p in DOCS.glob("*.json") if p.name != "index.json")


def test_index_matches_files_and_copy():
    index = load(DOCS / "index.json")
    assert index["meta"]["methodology"] and index["meta"]["citation"]
    assert len(index["states"]) >= 28
    assert {v["slug"] for v in index["states"].values()} == {p.stem for p in state_files()}
    assert {"Odisha", "Kerala", "Uttar Pradesh"} <= set(index["states"])


def test_each_state_file_is_ordered_and_consistent():
    for path in state_files():
        data = load(path)
        assert data["sources"] and data["source"] and data["source_url"].startswith("http"), path.name
        for src in data["sources"]:
            assert src["name"] and src["url"].startswith("http") and src["licence"]
        years = data["years"]
        assert years, path.name
        keys = [(y["year"], y["id"]) for y in years]
        assert keys == sorted(keys) and len(set(y["id"] for y in years)) == len(years), path.name
        assert set(data["elections"]) == {y["id"] for y in years}
        for y in years:
            assert sum(y["seats"].values()) == y["total"] == len(data["elections"][y["id"]]["list"]), (path.name, y["id"])
            assert y["lead"] in y["seats"] and set(y["seats"]) <= set(data["parties"])
            assert y["source"] in {"TCPD", "ECI", "IVD"}
            if y["turnout"] is not None:
                assert 0 < y["turnout"] <= 100


def test_odisha_covers_every_assembly_election_since_1961():
    data = load(DOCS / "odisha.json")
    assert data["years"][0]["year"] == 1961 and data["years"][-1]["year"] == 2024
    assert len(data["years"]) == 15


def test_index_includes_latest_party_headline_and_result_numbers():
    index = load(DOCS / "index.json")
    odisha = index["states"]["Odisha"]
    assert odisha["latest_headline"].startswith(odisha["lead_latest_name"])
    assert f"{odisha['latest_seats']} of {odisha['latest_total']}" in odisha["latest_headline"]
    assert odisha["latest_label"] == str(odisha["last"])
    assert odisha["lead_latest_colour"].startswith("#")
