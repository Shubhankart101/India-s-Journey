from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "docs" / "app.js"
ASSETS = ROOT / "docs" / "assets"
APP_TEXT = APP.read_text(encoding="utf-8")

WATER_SUBGROUPS = {
    "Port Cargo Traffic": "water-ports.svg",
    "Inland Waterways": "water-inland.svg",
    "Coastal Shipping": "water-coastal.svg",
    "Water Passenger Traffic": "water-passenger.svg",
    "Container & Port Performance": "water-container.svg",
    "Global Maritime Comparison": "water-global.svg",
}
LOGISTICS_SUBGROUPS = {
    "Road Freight": "logistics-road.svg",
    "Rail Freight": "logistics-rail.svg",
    "Sea Freight": "logistics-sea.svg",
    "Air Freight": "logistics-air.svg",
    "Modal Split & Comparison": "logistics-modal.svg",
    "Logistics Revenue": "logistics-revenue.svg",
}
TRANSPORT_CATEGORIES = (
    "Air Travel & Civil Aviation",
    "Indian Railways",
    "Water Transport & Shipping",
    "Logistics & Freight",
)


def registry_body(name: str) -> str:
    start = APP_TEXT.index(f"const {name} = {{")
    end = APP_TEXT.index("\n  };", start)
    return APP_TEXT[start:end]


def entries_for(name: str) -> dict[str, str]:
    return dict(re.findall(r'^\s*"([^"]+)":\s*"(assets/[^"\n]+)"', registry_body(name), re.M))


def object_keys(name: str) -> set[str]:
    return set(re.findall(r'^\s*"([^"]+)":\s*\{', registry_body(name), re.M))


def category_order_values() -> dict[str, float]:
    match = re.search(r"const categoryOrder = \{([^}]+)\};", APP_TEXT)
    assert match, "categoryOrder registry is missing"
    return {key: float(value) for key, value in re.findall(r"'([^']+)':\s*([0-9.]+)", match.group(1))}


def test_water_shipping_has_group_art_registry_entry():
    assert entries_for("categoryBgMap")["Water Transport & Shipping"] == "assets/water-group.svg"


def test_logistics_has_group_art_registry_entry():
    assert entries_for("categoryBgMap")["Logistics & Freight"] == "assets/logistics-group.svg"


def test_transport_categories_have_distinct_order_values():
    values = category_order_values()
    selected = [values[name] for name in TRANSPORT_CATEGORIES]
    assert len(set(selected)) == len(TRANSPORT_CATEGORIES)


def test_water_shipping_has_order_12_4():
    assert category_order_values()["Water Transport & Shipping"] == 12.4


def test_logistics_order_does_not_collide_with_innovation():
    values = category_order_values()
    assert values["Logistics & Freight"] not in {values[name] for name in TRANSPORT_CATEGORIES[:-1]} | {values["Innovation & Technology"]}


def test_water_shipping_group_has_source_summary_and_badges():
    entry = registry_body("groupHeroData").split('"Water Transport & Shipping": {', 1)[1].split("\n    },", 1)[0]
    assert "Ministry of Ports, Shipping & Waterways" in entry
    assert "Indian Ports Association" in entry and "IWAI" in entry and "DG Shipping" in entry
    assert "UNCTAD" in entry and "World Bank" in entry
    assert "badge1:" in entry and "badge2:" in entry


def test_logistics_group_explains_repeated_modal_figures_and_bases():
    entry = registry_body("groupHeroData").split('"Logistics & Freight": {', 1)[1].split("\n    },", 1)[0]
    assert "MoRTH" in entry and "Railway Board" in entry and "AAI" in entry and "MoPSW" in entry
    assert "DPIIT" in entry and "NITI Aayog" in entry and "World Bank LPI" in entry
    assert "intentionally repeat" in entry and "reporting units" in entry


def test_all_water_subgroups_have_art_registry_entries():
    art = entries_for("subgroupArtMap")
    assert {name: art.get(name, "").split("/")[-1] for name in WATER_SUBGROUPS} == WATER_SUBGROUPS


def test_all_logistics_subgroups_have_art_registry_entries():
    art = entries_for("subgroupArtMap")
    assert {name: art.get(name, "").split("/")[-1] for name in LOGISTICS_SUBGROUPS} == LOGISTICS_SUBGROUPS


def test_every_water_subgroup_has_a_hero_summary():
    assert set(WATER_SUBGROUPS).issubset(object_keys("subgroupHeroData"))


def test_every_logistics_subgroup_has_a_hero_summary():
    assert set(LOGISTICS_SUBGROUPS).issubset(object_keys("subgroupHeroData"))


def test_new_art_paths_exist():
    category_art = entries_for("categoryBgMap")
    subgroup_art = entries_for("subgroupArtMap")
    paths = [category_art[name] for name in ("Water Transport & Shipping", "Logistics & Freight")]
    paths.extend(subgroup_art[name] for name in (*WATER_SUBGROUPS, *LOGISTICS_SUBGROUPS))
    missing = [path for path in paths if not (ASSETS / Path(path).name).is_file()]
    assert not missing, f"Missing generated dashboard artwork: {', '.join(missing)}"


def test_chart_toolbar_has_fullscreen_png_csv_and_log_controls():
    assert "className = 'chart-tools'" in APP_TEXT
    assert 'data-tool="expand"' in APP_TEXT
    assert 'data-tool="png"' in APP_TEXT
    assert 'data-tool="csv"' in APP_TEXT
    assert 'data-tool="log"' in APP_TEXT
    assert 'data-tool="show-all"' in APP_TEXT
    assert "tools.style.setProperty('display', 'flex', 'important')" in APP_TEXT


def test_fullscreen_modal_supports_escape_focus_and_dialog_semantics():
    assert "event.key === 'Escape'" in APP_TEXT
    assert "event.key === 'Tab' && expandedChart" in APP_TEXT
    assert "focusOverlay.setAttribute('aria-label'" in APP_TEXT
    assert 'role="dialog"' in (ROOT / "docs" / "explore.html").read_text(encoding="utf-8")


def test_tooltips_include_formatted_values_and_share_percentages():
    assert "formatMagnitude(value, suffix)" in APP_TEXT
    assert "% of total" in APP_TEXT
    assert "const showShare = (type === 'bar'" in APP_TEXT and "|| !isTimeSeries" in APP_TEXT


def test_chart_point_detail_includes_value_rank_change_and_share():
    assert "className = 'chart-point-detail'" in APP_TEXT
    assert "Rank ${rank} of ${seriesValues.length}" in APP_TEXT
    assert "Change vs previous:" in APP_TEXT
    assert "Share of visible series:" in APP_TEXT


def test_legend_supports_toggle_isolate_and_show_all():
    assert "chart.setDatasetVisibility(datasetIdx" in APP_TEXT
    assert "chip.addEventListener('dblclick'" in APP_TEXT
    assert "showAll.textContent = 'Show all'" in APP_TEXT


def test_chart_type_and_time_range_presets_are_available():
    assert "availableTypes = nativeRadial" in APP_TEXT
    assert 'data-range="5"' in APP_TEXT and 'data-range="10"' in APP_TEXT
    assert "chartPrefs.range === '5'" in APP_TEXT


def test_dashboard_and_chart_choices_are_saved_in_local_storage():
    assert "indiaDashboard.interactivity.v1" in APP_TEXT
    assert "localStorage.getItem(DASHBOARD_PREFS_KEY)" in APP_TEXT
    assert "localStorage.setItem(DASHBOARD_PREFS_KEY" in APP_TEXT
    assert "writeChartPrefs(key" in APP_TEXT


def test_quick_jump_navigation_and_title_search_are_accessible():
    assert "Quick jump to dashboard groups and subgroups" in APP_TEXT
    assert "Search chart titles in ${groupFilter.value}" in APP_TEXT
    assert "card.dataset.chartTitle.includes(query)" in APP_TEXT
    assert "aria-pressed" in APP_TEXT


def test_interactive_controls_have_labels_and_mobile_styles():
    assert 'aria-label="Download chart as PNG"' in APP_TEXT
    assert "aria-label=" in APP_TEXT
    css = (ROOT / "docs" / "styles.css").read_text(encoding="utf-8")
    assert "@media (max-width: 600px)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert ".quick-jump-chip:focus-visible" in css


def test_new_group_and_subgroup_titles_have_no_mangled_question_marks():
    group_titles = registry_body("groupHeroData")
    subgroup_titles = registry_body("subgroupHeroData")
    titles = re.findall(r'title:\s*"([^"]*)"', group_titles + subgroup_titles)
    scoped = [title for title in titles if any(name in title for name in ("Water Transport & Shipping", "Logistics & Freight", *WATER_SUBGROUPS, *LOGISTICS_SUBGROUPS))]
    assert scoped
    assert all("??" not in title and "\ufffd" not in title for title in scoped)


def test_app_js_parses_with_available_javascript_parser():
    try:
        import tree_sitter
        import tree_sitter_javascript
    except ImportError:
        try:
            import esprima
        except ImportError:
            pytest.skip("Neither tree-sitter JavaScript nor esprima is installed")
        try:
            esprima.parseScript(APP_TEXT)
        except Exception as exc:
            if "Unexpected token" in str(exc) and ("?" in str(exc) or "optional" in str(exc).lower()):
                pytest.skip("Installed esprima does not support optional chaining used by this dashboard")
            raise
        return
    language = tree_sitter.Language(tree_sitter_javascript.language())
    parser = tree_sitter.Parser(language)
    tree = parser.parse(APP_TEXT.encode("utf-8"))
    assert not tree.root_node.has_error, "JavaScript parser reported syntax errors"
