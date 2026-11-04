from __future__ import annotations

from urllib.parse import urlparse

import pytest

from scripts import indian_railways_layer as rail


ALLOWED_SUBGROUPS = {
    "Network & Electrification",
    "Passenger Services",
    "Freight Operations",
    "Rolling Stock & Operations",
    "Railway Safety",
    "Finance & Efficiency",
    "Global Rail Comparison",
}


def wb_row(iso: str, year: str, value: float | None) -> dict:
    return {"countryiso3code": iso, "date": year, "value": value}


def complete_wb_payload(url: str) -> list:
    peers = rail.PEERS
    rows = [wb_row(iso, str(year), (i + 1) * 100_000 + year * 10)
            for i, iso in enumerate(peers) for year in (2018, 2019, 2020, 2021)]
    return [{"page": 1, "pages": 1}, rows]


def build(get_json=complete_wb_payload, previous=None):
    return rail.build_indian_railways_layer(get_json, previous or {})


def test_all_seven_exact_subgroups_are_populated():
    series = build()
    groups = {item["meta"]["subgroup"] for item in series.values()}
    assert groups == ALLOWED_SUBGROUPS
    assert all(any(s["meta"]["subgroup"] == group for s in series.values()) for group in ALLOWED_SUBGROUPS)


def test_every_key_is_rail_prefixed_and_unique():
    keys = list(build())
    assert len(keys) == len(set(keys))
    assert all(key.startswith("rail_") for key in keys)


def test_each_chart_has_https_source_and_complete_explanation():
    for key, series in build().items():
        assert series["source"].startswith("https://"), key
        explanation = series["meta"]["explain"]
        assert all(explanation.get(field) for field in ("what", "read", "why")), key
        assert series["note"], key


def test_year_book_notes_include_a_page_citation():
    static = rail._static()
    series = {key: builder()[1] for key, builder in static.items()}
    year_book = [item for item in series.values() if item["source"] == rail.YEAR_BOOK]
    assert all("Year Book 2023-24" in item["note"] and "p." in item["note"] for item in year_book)
    pib = series["rail_freight_loading_pib"]
    assert "PIB release 2117417" in pib["note"] and "opening freight-loading paragraph" in pib["note"]


def test_labels_are_strings_and_values_align_for_single_and_multi_series():
    for key, series in build().items():
        assert series["labels"] and all(isinstance(label, str) for label in series["labels"]), key
        if "values" in series:
            assert len(series["labels"]) == len(series["values"]), key
        for dataset in series.get("datasets", []):
            assert len(series["labels"]) == len(dataset["values"]), key


def test_static_series_are_not_dropped_when_world_bank_is_unavailable():
    series = build(lambda _: (_ for _ in ()).throw(OSError("offline")))
    assert "rail_route_km" in series
    assert "rail_wb_freight_trend" not in series
    assert "rail_wb_passenger_trend" not in series
    assert len(series) >= len(rail._static())


def test_zone_routes_reconcile_to_the_national_total():
    assert sum(rail.ZONE_ROUTE_KM.values()) == 69_181
    series = build()
    assert sum(series["rail_zone_route_km"]["values"]) == 69_181


def test_state_routes_reconcile_to_the_national_total():
    assert sum(rail.STATE_ROUTE_KM.values()) == 69_181
    series = build()
    assert sum(series["rail_state_route_km"]["values"]) == 69_181


def test_passenger_suburban_and_non_suburban_splits_reconcile_each_year():
    assert all(suburban + non_suburban == total for suburban, non_suburban, total in
               zip(rail.PASSENGERS_SUBURBAN, rail.PASSENGERS_NON_SUBURBAN, rail.PASSENGERS_TOTAL))


def test_passenger_mix_categories_reconcile_to_2023_24_total():
    series = build()
    assert sum(series["rail_passenger_mix"]["values"]) == rail.PASSENGERS_TOTAL[-1] == 6_905


def test_commodity_loading_reconciles_to_2023_24_freight_total():
    assert round(sum(value[1] for value in rail.COMMODITIES.values()), 2) == rail.FREIGHT_TONNES[-1]
    series = build()
    assert round(sum(series["rail_freight_commodity_mix"]["values"]), 2) == 1_588.06


def test_commodity_share_chart_sums_to_100_percent():
    values = build()["rail_freight_commodity_share"]["values"]
    assert sum(values) == pytest.approx(100, abs=0.1)


def test_accident_type_table_reconciles_to_reported_totals():
    yearly = [sum(values[index] for values in rail.ACCIDENTS.values())
              for index in range(len(rail.ACCIDENT_YEARS))]
    assert yearly == [55, 22, 35, 48, 40]
    assert yearly[-1] == build()["rail_accidents_total"]["values"][-1]


def test_accident_mix_has_all_40_incidents():
    assert sum(build()["rail_accident_mix"]["values"]) == 40


def test_accident_type_share_is_bounded_and_aligned():
    values = build()["rail_derailment_share_pct"]["values"]
    assert len(values) == len(rail.ACCIDENT_YEARS)
    assert all(0 <= value <= 100 for value in values)


def test_electrified_route_share_is_calculated_from_source_values():
    series = build()["rail_electrified_route_share"]
    assert series["values"][-1] == pytest.approx(rail.ELECTRIFIED_KM[-1] / rail.ROUTE_KM[-1] * 100, abs=0.01)


def test_calculated_passenger_average_lead_uses_passenger_km_and_journeys():
    series = build()["rail_passenger_average_lead_calculated"]
    assert series["values"][-1] == pytest.approx(rail.PASSENGER_KM[-1] / rail.PASSENGERS_TOTAL[-1], abs=0.01)


def test_suburban_and_non_suburban_percentages_sum_to_100():
    series = build()
    suburban = series["rail_passenger_suburban_share"]["values"]
    non_suburban = series["rail_passenger_non_suburban_share"]["values"]
    assert all(a + b == pytest.approx(100, abs=0.1) for a, b in zip(suburban, non_suburban))


def test_freight_commodity_growth_uses_published_two_year_values():
    series = build()["rail_freight_commodity_growth_pct"]
    expected = (rail.COMMODITIES["Coal"][1] / rail.COMMODITIES["Coal"][0] - 1) * 100
    assert series["values"][series["labels"].index("Coal")] == pytest.approx(expected, abs=0.01)


def test_live_freight_and_passenger_world_bank_trends_build_from_real_api_shape():
    series = build()
    for key in ("rail_wb_freight_trend", "rail_wb_passenger_trend"):
        chart = series[key]
        assert len(chart["labels"]) >= 2
        assert {dataset["label"] for dataset in chart["datasets"]} >= {"India", "China"}
        assert all(len(dataset["values"]) == len(chart["labels"]) for dataset in chart["datasets"])


def test_world_bank_values_are_scaled_from_millions_to_billions():
    series = build()["rail_wb_freight_trend"]
    india = next(dataset for dataset in series["datasets"] if dataset["label"] == "India")
    assert india["values"][0] == pytest.approx((100_000 + 2018 * 10) / 1000, abs=0.001)


def test_partial_world_bank_payload_builds_sparse_trends():
    def partial(url):
        return [{"page": 1}, [wb_row("IND", "2020", 2_000_000), wb_row("IND", "2019", 1_500_000),
                              wb_row("CHN", "2019", 3_000_000)]]

    series = build(partial)
    chart = series["rail_wb_freight_trend"]
    assert chart["labels"] == ["2019", "2020"]
    china = next(dataset for dataset in chart["datasets"] if dataset["label"] == "China")
    assert china["values"] == [3000.0, None]


def test_empty_world_bank_payload_uses_previous_good_trend():
    previous = {"rail_wb_freight_trend": {"labels": ["2019", "2020"], "values": [10, 11]}}
    series = build(lambda _: [{"page": 1}, None], previous)
    assert series["rail_wb_freight_trend"] == previous["rail_wb_freight_trend"]
    assert "rail_route_km" in series


def test_empty_world_bank_payload_without_fallback_keeps_static_series():
    series = build(lambda _: [{"page": 1}, []])
    assert "rail_route_km" in series
    assert "rail_wb_freight_trend" not in series


def test_world_bank_exception_preserves_previous_good_series():
    previous_series = {"labels": ["a", "b"], "values": [1, 2]}
    series = build(lambda _: (_ for _ in ()).throw(RuntimeError("network")),
                   {"rail_wb_freight_trend": previous_series})
    assert series["rail_wb_freight_trend"] == previous_series


def test_latest_common_year_ranking_selects_latest_year_with_four_countries():
    def dated(url):
        rows = [wb_row("IND", "2021", 900), wb_row("CHN", "2021", 800),
                wb_row("USA", "2021", 700), wb_row("RUS", "2021", 600),
                wb_row("IND", "2022", 1000), wb_row("CHN", "2022", 900)]
        return [{"page": 1}, rows]

    chart = build(dated)["rail_wb_freight_latest_common_rank"]
    assert "2021" in chart["note"]
    assert "2021" in chart["meta"]["title"]
    assert len(chart["labels"]) == 4


def test_global_world_bank_sources_point_to_indicator_pages():
    for key, series in build().items():
        if series["meta"]["subgroup"] == rail.GLOBAL:
            assert urlparse(series["source"]).scheme == "https"
            assert "worldbank.org/indicator/" in series["source"], key
