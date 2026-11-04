"""Offline contract tests for the cross-mode logistics chart layer."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts import air_travel_layer, indian_railways_layer, logistics_layer


def offline_get_json(url):
    raise OSError("network disabled in test")


def build_offline(previous=None):
    return logistics_layer.build_logistics_layer(offline_get_json, previous or {})


def test_offline_build_has_at_least_forty_series():
    assert len(build_offline()) >= 40


def test_exactly_six_requested_subgroups_are_populated():
    series = build_offline()
    counts = Counter(item["meta"]["subgroup"] for item in series.values())
    assert set(counts) == set(logistics_layer.SUBGROUPS)
    assert len(counts) == 6
    assert all(counts[name] > 0 for name in logistics_layer.SUBGROUPS)


def test_every_key_has_log_prefix_and_keys_are_unique():
    series = build_offline()
    assert len(series) == len(set(series))
    assert all(key.startswith("log_") for key in series)


def test_category_and_subgroups_are_exact():
    for item in build_offline().values():
        assert item["meta"]["category"] == "Logistics & Freight"
        assert item["meta"]["subgroup"] in logistics_layer.SUBGROUPS


def test_every_source_uses_https():
    assert all(item["source"].startswith("https://") for item in build_offline().values())


def test_every_series_has_all_explanation_fields():
    for item in build_offline().values():
        explain = item["meta"].get("explain", {})
        assert all(isinstance(explain.get(field), str) and explain[field].strip()
                   for field in ("what", "read", "why"))


def test_every_chart_has_a_note_and_url():
    for item in build_offline().values():
        assert item.get("note", "").strip()
        assert item.get("source", "").startswith("https://")


def test_all_labels_are_nonempty_strings():
    for item in build_offline().values():
        assert item["labels"]
        assert all(isinstance(label, str) and label for label in item["labels"])


def test_all_chart_data_are_aligned_with_labels():
    for key, item in build_offline().items():
        if "values" in item:
            assert len(item["values"]) == len(item["labels"]), key
        else:
            assert item.get("datasets"), key
            for dataset in item["datasets"]:
                assert len(dataset["values"]) == len(item["labels"]), key


def test_modal_split_adds_to_one_hundred():
    item = build_offline()["log_modal_niti_share"]
    assert sum(item["values"]) == pytest.approx(100)
    assert item["labels"] == ["Road", "Rail", "Other modes (residual)"]


def test_modal_residual_is_explicitly_documented():
    item = build_offline()["log_modal_niti_share"]
    assert "residual" in item["note"].lower()
    assert "not an independently reported estimate" in item["note"]
    assert "2021" in item["note"]


def test_inland_waterway_share_complement_sums_to_one_hundred():
    item = build_offline()["log_modal_inland_water"]
    assert sum(item["values"]) == pytest.approx(100)
    assert "calculated complement" in item["note"]


def test_air_cargo_copy_matches_air_layer_values():
    air = air_travel_layer.build_air_travel_layer(offline_get_json, {})["air_aai_freight"]
    logistics = build_offline()["log_air_aai_freight"]
    assert logistics["labels"] == air["labels"]
    assert [d["values"] for d in logistics["datasets"]] == [d["values"] for d in air["datasets"]]
    assert logistics["datasets"][1]["values"][-1] == pytest.approx(3365.68)


def test_rail_loading_copy_matches_rail_layer_values():
    rail = indian_railways_layer.build_indian_railways_layer(offline_get_json, {})["rail_freight_tonnes"]
    logistics = build_offline()["log_rail_loading"]
    assert logistics["labels"] == rail["labels"]
    assert logistics["values"] == rail["values"]
    assert logistics["values"][-1] == pytest.approx(1588.06)


def test_rail_ntkm_copy_matches_rail_layer_values():
    rail = indian_railways_layer.build_indian_railways_layer(offline_get_json, {})["rail_freight_ntkm"]
    logistics = build_offline()["log_rail_ntkm"]
    assert logistics["labels"] == rail["labels"]
    assert logistics["values"] == rail["values"]
    assert logistics["values"][-1] == 973968


def test_air_cross_mode_copy_uses_the_aai_report_source():
    item = build_offline()["log_air_aai_freight"]
    assert item["source"] == air_travel_layer.AAI_REPORT
    assert "2023-24" in item["note"]
    assert "airport" in item["note"].lower()


def test_rail_cross_mode_copy_uses_the_year_book_source():
    item = build_offline()["log_rail_loading"]
    assert item["source"] == indian_railways_layer.YEAR_BOOK
    assert "revenue-earning" in item["note"]
    assert "excluding Konkan Railway" in item["note"]


def test_offline_exception_preserves_previous_dynamic_series():
    old = {"labels": ["old", "series"], "values": [1, 2], "source": "https://example.test/old"}
    result = logistics_layer.build_logistics_layer(offline_get_json, {"log_road_wb_freight": old})
    assert result["log_road_wb_freight"] is old


def test_empty_world_bank_payload_uses_fallback():
    old = {"labels": ["2019", "2020"], "values": [3, 4], "source": "https://example.test/previous"}
    result = logistics_layer.build_logistics_layer(lambda url: [[], []], {"log_rail_wb_freight": old})
    assert result["log_rail_wb_freight"] is old


def test_partial_world_bank_payload_builds_only_valid_india_observations():
    calls = []

    def partial(url):
        calls.append(url)
        if "IS.ROD.GOOD.MT.K6" in url:
            return [{"page": 1}, [
                {"countryiso3code": "IND", "date": "2020", "value": 100.0},
                {"countryiso3code": "IND", "date": "2021", "value": 125.0},
                {"countryiso3code": "CHN", "date": "2021", "value": 900.0},
                {"countryiso3code": "IND", "date": "2022", "value": None},
            ]]
        return [{"page": 1}, []]

    result = logistics_layer.build_logistics_layer(partial, {})
    item = result["log_road_wb_freight"]
    assert item["labels"] == ["2020", "2021"]
    assert item["values"] == [100.0, 125.0]
    assert len(calls) == 4


def test_partial_world_bank_country_without_india_keeps_fallback():
    old = {"labels": ["a", "b"], "values": [10, 20], "source": "https://example.test/old"}
    payload = [{"page": 1}, [{"countryiso3code": "CHN", "date": "2020", "value": 2.0}]]
    result = logistics_layer.build_logistics_layer(lambda url: payload, {"log_road_wb_freight": old})
    assert result["log_road_wb_freight"] is old


def test_empty_world_bank_response_does_not_remove_static_charts():
    result = logistics_layer.build_logistics_layer(lambda url: [[], []], {})
    assert len(result) >= 40
    assert "log_air_aai_freight" in result
    assert "log_rail_loading" in result


def test_one_point_official_metrics_are_not_padded_with_fake_years():
    item = build_offline()["log_road_fastag_collection"]
    assert item["labels"] == ["FY 2023-24"]
    assert item["datasets"][0]["values"] == [55000]


def test_port_revisions_are_explicitly_not_silently_combined():
    item = build_offline()["log_sea_port_classes"]
    assert "provisional" in item["note"].lower()
    assert "differs from the annual report's later revised 819.23" in item["note"]


def test_logistics_cost_bases_are_separately_labelled():
    item = build_offline()["log_modal_cost_bases"]
    assert item["labels"] == ["Share of GDP", "Share of non-services output"]
    assert item["values"] == [7.97, 9.09]
    assert "denominators differ" in item["note"].lower()


def test_fallback_is_per_key_not_all_or_nothing():
    previous = {"log_road_wb_freight": {"labels":["x","y"],"values":[1,2]},
                "log_sea_container_wb": {"labels":["x","y"],"values":[3,4]}}
    result = logistics_layer.build_logistics_layer(offline_get_json, previous)
    assert result["log_road_wb_freight"] is previous["log_road_wb_freight"]
    assert result["log_sea_container_wb"] is previous["log_sea_container_wb"]
    assert "log_air_aai_freight" in result
