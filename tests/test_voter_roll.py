import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATHS = [ROOT / "data" / "voter-roll.json",
              ROOT / "frontend" / "src" / "data" / "voter-roll.json", ROOT / "frontend" / "public" / "data" / "voter-roll.json"]


def load_data():
    return json.loads(DATA_PATHS[0].read_text(encoding="utf-8"))


def test_voter_roll_data_is_reproducible_across_site_bundles():
    expected = load_data()
    assert all(json.loads(path.read_text(encoding="utf-8")) == expected for path in DATA_PATHS[1:])


def test_historical_election_figures_have_citations_and_cover_1951_to_2024():
    data = load_data()
    assert len(data["elections"]) == 18
    assert data["elections"][0]["label"] == "1951–52"
    assert data["elections"][-1]["label"] == "2024"
    assert all(row["electors"] > 0 and 0 <= row["turnout_percent"] <= 100 and row["population"] > 0 for row in data["elections"])
    assert all(set(row["sources"]) == {"electors", "turnout", "population"} for row in data["elections"])
    assert all(url.startswith("https://") for row in data["elections"] for url in row["sources"].values())
    assert "1989" in [row["label"] for row in data["elections"]]
    assert all(data["figures"][key]["source"] for key in data["figures"])


def test_sir_states_have_sourced_phase_or_comparable_roll_figures():
    data = load_data()
    assert len(data["sir"]["states"]) == 36
    bihar = next(item for item in data["sir"]["states"] if item["state"] == "Bihar")
    assert bihar["before"] > bihar["draft"] and bihar["final"] > bihar["draft"]
    assert bihar["source"].startswith("https://") and bihar["rounded"] is True
    assert sum(1 for item in data["sir"]["states"] if item["phase"] == 2) == 12
    assert sum(1 for item in data["sir"]["states"] if item["phase"] == 3) == 19
    assert all(item["source"].startswith("https://") for item in data["sir"]["states"])
    assert "does not mean they were not revised" in data["sir"]["note"]


def test_revision_calendar_deletion_reasons_and_form_routes_have_sources():
    data = load_data()
    assert {item["title"] for item in data["calendar"]} >= {"1 January", "1 April", "1 July", "1 October", "Draft roll", "Claims & objections", "Final roll"}
    assert all(item["source"].startswith("https://") for item in data["calendar"])
    deletion = data["deletions"]
    assert all(item["value"] > 0 and item["source"].startswith("https://") for item in deletion["reasons"])
    assert all(item["before"] > 0 and item["after"] > 0 and item["source"].startswith("https://") for item in deletion["ratios"])
    assert all(item["source"].startswith("https://") for item in deletion["safeguards"])
    assert deletion["safeguards"][2]["source"] == data["sources"]["deletion_thresholds"]["url"]
    assert "difference of 77,199" in deletion["note"]
    assert {item["form"] for item in data["scenarios"]} >= {"Form 6", "Form 7", "Form 8", "Form 6A"}
    assert all(item["source"].startswith("https://") and len(item["steps"]) >= 3 for item in data["scenarios"])


def test_catalog_registers_chart_and_interactive_module_in_india_in_maps():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    entries = {item["key"]: item for item in catalog["indicators"] if item["key"].startswith("india_") and item["category"] in ("India in Maps", "Elections & Democracy")}
    assert entries["india_lok_sabha_registered_electors"]["series"]["chart_type"] == "bar"
    assert entries["india_voter_roll_ssr_sir_atlas"]["series"]["chart_type"] == "voter-roll"
    atlas = [entries["india_lok_sabha_registered_electors"], entries["india_voter_roll_ssr_sir_atlas"]]
    assert all(item["subgroup"] == "Live Results, Rolls & Recent Elections" for item in atlas)