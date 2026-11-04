"""India in Maps: boundary build, State/UT name parity between Python and JS, and map derivation."""
import json
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest

from scripts.build_india_maps import GROUPS, ring_area, simplify, slug
from scripts.rbi_state_layer import STATES_AND_UTS, _ALIASES, canonical_state

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = ROOT / "docs" / "assets" / "maps" / "india-states.json"
NODE = shutil.which("node")


def test_simplify_keeps_endpoints_and_drops_collinear_points():
    line = [(0, 0), (1, 0.01), (2, 0), (3, 5), (4, 0)]
    assert simplify(line, 0.5) == [(0, 0), (2, 0), (3, 5), (4, 0)]
    assert ring_area([(0, 0), (4, 0), (4, 3)]) == 6


def test_geometry_covers_every_state_and_ut_with_canonical_names():
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    assert sorted(geometry["states"]) == sorted(STATES_AND_UTS)
    assert geometry["license"] == "CC BY 2.5 IN"
    assert all(path.startswith("M") and path.endswith("Z") for path in geometry["states"].values())
    assert GEOMETRY.read_bytes() == (ROOT / "frontend" / "public" / "maps" / "india-states.json").read_bytes()
    assert len(GEOMETRY.read_bytes()) < 150_000


def test_group_and_subgroup_artwork_exists_for_both_sites():
    for name in ["india-maps"] + [f"maps-{slug(group)}" for group in GROUPS]:
        for folder in (ROOT / "docs" / "assets", ROOT / "frontend" / "public" / "art"):
            svg = (folder / f"{name}.svg").read_text(encoding="utf-8")
            assert svg.startswith("<svg") and "prefers-reduced-motion" in svg
            ElementTree.fromstring(svg)  # browsers refuse to draw malformed SVG backgrounds


def run_node(script: str):
    result = subprocess.run([NODE, "-e", script], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True, timeout=120)
    return json.loads(result.stdout)


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_js_state_names_match_python():
    names = list(STATES_AND_UTS) + [key for key in _ALIASES if canonical_state(key) not in (None, "__ALL_INDIA__")]
    names += ["Andaman and Nicobar", "Dadra and Nagar Haveli and Daman and Diu", "1. Orissa", "The Jammu and Kashmir*", "All India", "Total"]
    js = run_node(
        "require('./docs/india-maps.js');"
        f"console.log(JSON.stringify({json.dumps(names)}.map(globalThis.IndiaMaps.canonicalState)))"
    )
    expected = [None if canonical_state(name) == "__ALL_INDIA__" else canonical_state(name) for name in names]
    assert js == expected


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_derives_one_map_per_state_statistic_dataset_and_state_trend():
    script = """
require('./docs/india-maps.js');
const states = ['Kerala', 'Goa', 'Bihar', 'Assam', 'Punjab', 'Delhi'];
const series = {
  plain: { labels: [...states, 'All India'], values: [1, 2, 3, 4, 5, 6, 99], source: 'S' },
  years: { labels: ['2020', '2021'], values: [1, 2] },
  multi: { labels: states, datasets: [{ label: 'Male', values: [1, 2, 3, 4, 5, 6] }, { label: 'Female', values: [6, 5, 4, 3, 2, 1] }] },
  trend: { labels: ['2021', '2022'], datasets: states.map((state, i) => ({ label: state, values: [i, i === 0 ? null : i * 10] })) },
  few: { labels: ['Kerala', 'Goa'], values: [1, 2] },
  hidden: { labels: states, values: [1, 2, 3, 4, 5, 6] },
};
const out = globalThis.IndiaMaps.deriveMapSeries(series, key => key === 'hidden' ? null : ({ group: 'Social', subgroup: 'Sub', title: key }));
console.log(JSON.stringify(out));
"""
    out = run_node(script)
    assert sorted(out) == ["map__multi__1", "map__multi__2", "map__plain", "map__trend__latest"]
    plain = out["map__plain"]
    assert plain["chartType"] == "map" and plain["labels"] == ["Kerala", "Goa", "Bihar", "Assam", "Punjab", "Delhi"]
    assert plain["meta"]["category"] == "India in Maps" and plain["meta"]["subgroup"] == "Social on the map"
    assert out["map__multi__2"]["meta"]["title"] == "multi: Female — map"
    assert out["map__trend__latest"]["values"] == [0, 10, 20, 30, 40, 50]


def test_catalog_exports_the_india_in_maps_group():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    maps = [item for item in catalog["indicators"] if item["category"] == "India in Maps"]
    assert len(maps) >= 200
    assert all(item["series"]["chart_type"] == "map" and len(item["series"]["labels"]) >= 5 for item in maps)
    group = next(item for item in catalog["categories"] if item["name"] == "India in Maps")
    assert group["art"] == "india-maps.svg" and len(group["subgroups"]) >= 5
    assert all(sub["art"].startswith("maps-") for sub in group["subgroups"])
    assert "Lower Courts on the map" in {sub["name"] for sub in group["subgroups"]}


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_per_state_breakdowns_become_one_map_per_category_plus_a_total():
    script = """
require('./docs/india-maps.js');
const states = ['Kerala', 'Goa', 'Bihar', 'Assam', 'Punjab', 'Delhi', 'Sikkim', 'Odisha', 'Tripura', 'Haryana'];
const series = Object.fromEntries(states.map((state, i) => [`jud_${i}`, {
  scope: `jurisdiction:${state}`, labels: ['Original', 'Appeal', '2024'], values: [i + 1, 10, 99],
  meta: { title: `${state}: Total cases case-category breakdown pending`, category: 'Judiciary & Pending Cases', subgroup: 'Lower Courts' },
}]));
series.hc = { scope: 'jurisdiction:Allahabad High Court', labels: ['Original'], values: [5], meta: { title: 'Allahabad High Court: x' } };
const out = globalThis.IndiaMaps.deriveMapSeries(series, () => ({ group: 'Judiciary & Pending Cases', subgroup: 'Lower Courts' }));
console.log(JSON.stringify(out));
"""
    out = run_node(script)
    assert sorted(out) == [
        "map__jur__judiciary-pending-cases__total-cases-case-category-breakdown-pending__appeal",
        "map__jur__judiciary-pending-cases__total-cases-case-category-breakdown-pending__original",
        "map__jur__judiciary-pending-cases__total-cases-case-category-breakdown-pending__total",
    ]
    total = out["map__jur__judiciary-pending-cases__total-cases-case-category-breakdown-pending__total"]
    assert total["values"] == [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    assert total["meta"]["subgroup"] == "Lower Courts on the map" and total["meta"]["mapTheme"] == "Lower Courts"
    assert total["meta"]["title"] == "Total cases case-category breakdown pending: total by State/UT — map"
