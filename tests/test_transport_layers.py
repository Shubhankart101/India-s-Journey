import json
from pathlib import Path

import pytest

from scripts import air_travel_layer as air
from scripts import indian_railways_layer as rail

ROOT = Path(__file__).resolve().parents[1]
SERIES = json.loads((ROOT / "data" / "chart-latest.json").read_text(encoding="utf-8"))["series"]
GROUPS = {
    air.CATEGORY: {air.GROWTH, air.GLOBAL, air.TRAFFIC, air.AIRPORTS, air.CARGO, air.FINANCE},
    rail.CATEGORY: {"Network & Electrification", "Passenger Services", "Freight Operations", "Rolling Stock & Operations",
                    "Railway Safety", "Finance & Efficiency", "Global Rail Comparison"},
}


@pytest.mark.parametrize("category,subgroups", GROUPS.items())
def test_every_subgroup_has_charts_and_official_source(category, subgroups):
    mine = [s for s in SERIES.values() if s.get("meta", {}).get("category") == category]
    assert {s["meta"]["subgroup"] for s in mine} == subgroups
    for s in mine:
        assert s["source"].startswith("https://")
        assert s["labels"] and all(isinstance(x, str) for x in s["labels"])
        assert s["meta"].get("explain")


def test_railway_tables_reconcile_with_year_book():
    assert sum(rail.ZONE_ROUTE_KM.values()) == 69181
    assert sum(rail.STATE_ROUTE_KM.values()) == 69181


def test_aai_traffic_totals():
    assert round(270.34 + 56.94, 2) == 327.28 and round(306.79 + 69.64, 2) == 376.43
