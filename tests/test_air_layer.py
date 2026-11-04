import pytest

from scripts import air_travel_layer as air

ALLOWED = {air.GROWTH, air.GLOBAL, air.TRAFFIC, air.AIRPORTS, air.CARGO, air.FINANCE}
COUNTRIES = {"IND": 1.0, "CHN": 3.0, "USA": 6.0, "JPN": 1.5, "GBR": 1.2, "DEU": 1.1, "FRA": 0.9, "BRA": 0.8,
             "AUS": 0.5, "ARE": 0.4, "RUS": 0.7, "WLD": 40.0}


def wb_payload(url, only=None):
    countries = url.split("/country/")[1].split("/")[0].split(";")
    code = url.split("/indicator/")[1].split("?")[0]
    scale = {"IS.AIR.PSGR": 1e8, "IS.AIR.DPRT": 1e6, "IS.AIR.GOOD.MT.K1": 1e7, "SP.POP.TOTL": 1e8}[code]
    rows = []
    for iso in countries:
        if only and iso not in only:
            continue
        for year in range(2010, 2024):
            factor = 0.4 if year == 2020 else 1 + 0.03 * (year - 2010)
            rows.append({"countryiso3code": iso, "date": str(year), "value": COUNTRIES[iso] * scale * factor})
    return [{"page": 1}, rows]


@pytest.fixture(scope="module")
def built():
    return air.build_air_travel_layer(lambda url: wb_payload(url), {})


def raising(url):
    raise OSError("offline")


def test_series_count_and_subgroup_balance(built):
    assert len(built) >= 70
    counts = {g: sum(1 for s in built.values() if s["meta"]["subgroup"] == g) for g in ALLOWED}
    assert all(n >= 8 for n in counts.values()), counts


def test_keys_unique_prefixed_and_existing_keys_kept(built):
    assert all(k.startswith("air_") for k in built)
    for key in ("air_aai_passengers", "air_aai_profit", "air_wb_india_passengers", "air_udan_routes", "air_wb_freight_share"):
        assert key in built


def test_only_allowed_subgroups_and_category(built):
    for key, s in built.items():
        assert s["meta"]["subgroup"] in ALLOWED, key
        assert s["meta"]["category"] == air.CATEGORY


def test_sources_are_https_and_notes_cite_a_document(built):
    for key, s in built.items():
        assert s["source"].startswith("https://"), key
        assert len(s["note"]) > 25, key


def test_labels_are_strings_and_values_aligned(built):
    for key, s in built.items():
        assert s["labels"] and all(isinstance(x, str) for x in s["labels"]), key
        sets = s["datasets"] if "datasets" in s else [s]
        assert all(len(d["values"]) == len(s["labels"]) for d in sets), key


def test_every_series_explains_what_read_why(built):
    for key, s in built.items():
        explain = s["meta"]["explain"]
        assert all(explain.get(part) for part in ("what", "read", "why")), key


def test_traffic_history_splits_reconcile_with_totals():
    for i in range(len(air.HY)):
        assert air.H_PAX_I[i] + air.H_PAX_D[i] == pytest.approx(air.H_PAX_T[i], abs=0.02)
        assert air.H_FR_I[i] + air.H_FR_D[i] == pytest.approx(air.H_FR_T[i], abs=0.02)
    assert air.H_MOV_I[5] + air.H_MOV_D[5] == pytest.approx(2677.59, abs=0.01)
    assert air.H_MOV_I[7] + air.H_MOV_D[7] == pytest.approx(2906.241, abs=0.01)


def test_category_tables_reconcile_with_national_totals():
    assert sum(air.CAT_PAX[0]) == air.NATIONAL_2526["passengers"] == 420089356
    assert sum(air.CAT_PAX[1]) == 412086111
    assert sum(air.CAT_MOV[0]) == air.NATIONAL_2526["movements"] == 2906241
    assert sum(air.CAT_MOV[1]) == 2886809
    assert sum(air.CAT_FREIGHT) == pytest.approx(air.NATIONAL_2526["freight_t"], abs=0.2)


def test_region_tables_reconcile():
    assert sum(air.REG_PAX[0]) == air.NATIONAL_2526["passengers"]
    assert sum(air.REG_PAX[1]) == 412086111
    assert sum(air.REG_MOV[0]) == air.NATIONAL_2526["movements"]
    assert sum(air.REG_FREIGHT[0]) == pytest.approx(air.NATIONAL_2526["freight_t"], abs=0.2)
    for i, total in enumerate(air.REG_PAX[0]):
        assert air.REG_INTL_PAX[i] + air.REG_DOM_PAX[i] == total


def test_state_table_reconciles_with_national_totals():
    assert len(air.STATES) == 35
    assert sum(v[1] + v[2] for v in air.STATES.values()) == air.NATIONAL_2526["passengers"]
    assert sum(v[0] for v in air.STATES.values()) == air.NATIONAL_2526["movements"]
    assert sum(v[3] + v[4] for v in air.STATES.values()) ==     pytest.approx(air.NATIONAL_2526["freight_t"], abs=0.6)
    assert sum(v[1] for v in air.STATES.values()) == sum(air.REG_INTL_PAX)


def test_airport_top_tables_are_within_national_totals():
    assert sum(v[0] for v in air.AIRPORT_PASSENGERS.values()) < air.NATIONAL_2526["passengers"]
    assert sum(v[0] for v in air.AIRPORT_MOVEMENTS.values()) < air.NATIONAL_2526["movements"]
    assert sum(v[0] for v in air.AIRPORT_FREIGHT.values()) < air.NATIONAL_2526["freight_t"]
    for name, (intl, _) in air.AIRPORT_INTL_FREIGHT.items():
        assert intl <= air.AIRPORT_FREIGHT.get(name, (intl,))[0]


def test_airline_tables_reconcile_with_official_totals():
    assert sum(v[0] for v in air.AIRLINE_DOM.values()) == air.AIRLINE_DOM_TOTAL[0]
    assert sum(v[1] for v in air.AIRLINE_DOM.values()) == air.AIRLINE_DOM_TOTAL[1]
    assert sum(air.QTR_DOM[0]) == air.AIRLINE_DOM_TOTAL[0]
    assert sum(air.QTR_DOM[1]) == air.AIRLINE_DOM_TOTAL[1]
    assert sum(v[0] for v in air.AIRLINE_FY25.values()) == air.AIRLINE_FY25_TOTAL[0]
    assert sum(v[1] for v in air.AIRLINE_FY25.values()) == air.AIRLINE_FY25_TOTAL[1]


def test_monthly_domestic_plus_international_matches_total():
    for table in (air.M_PAX, air.M_FREIGHT):
        for period in (0, 1):
            for i in range(9):
                assert table["intl"][period][i] + table["dom"][period][i] == pytest.approx(table["total"][period][i], abs=0.02)


def test_udan_tables_reconcile_with_reply_totals():
    assert sum(air.UDAN_PHASE1) + sum(air.UDAN_PHASE2) == pytest.approx(air.UDAN_EXPENDITURE_TOTAL, abs=0.01)
    assert sum(air.UDAN_VGF) == pytest.approx(air.UDAN_VGF_TOTAL, abs=0.01)
    assert air.UDAN_ROUTES["Routes operationalised"] < air.UDAN_ROUTES["Routes awarded"]


def test_aai_finances_reconcile():
    for rev, exp, pbt in zip(air.D_REV, air.D_EXP, air.D_PBT):
        assert rev - exp == pytest.approx(pbt, abs=0.02)
    capex = air.D_CAPEX[4:]
    for i, actual in enumerate(capex):
        assert sum(v[i] for v in air.CAPEX_FUNDING.values()) == pytest.approx(actual, abs=0.05)
    for i, total in enumerate(air.D_REV[4:9]):
        assert sum(v[i] for v in air.REVENUE_MIX.values()) == pytest.approx(total, abs=0.05)
    assert air.D_REV[8] == 12172.35
    for j, total in enumerate((air.D_EXP[9], air.D_EXP[10])):
        assert sum(v[j] for v in air.COSTS.values()) == pytest.approx(total, abs=0.01)


def test_history_growth_math_matches_series(built):
    series = built["air_history_passengers_yoy"]
    for i, value in enumerate(series["values"], start=1):
        assert value == pytest.approx((air.H_PAX_T[i] / air.H_PAX_T[i - 1] - 1) * 100, abs=0.01)
    monthly = built["air_monthly_passengers_yoy"]["values"]
    assert monthly[0] == pytest.approx((38.63 / 37.13 - 1) * 100, abs=0.01)


def test_ranked_series_are_sorted_and_notes_match_data(built):
    top = built["air_top10_airport_passengers"]
    assert top["labels"][0] == "Delhi" and top["values"] == sorted(top["values"], reverse=True)
    assert top["values"][0] == pytest.approx(78.70, abs=0.01)
    assert top["indexAxis"] == "y"
    assert "78.7" in top["meta"]["explain"]["read"]
    for key in ("air_airline_domestic_2024", "air_state_passengers", "air_top10_airport_freight"):
        assert built[key]["values"] == sorted(built[key]["values"], reverse=True)


def test_doughnut_shares_add_up(built):
    share = built["air_airline_market_share_2024"]
    assert share["chartType"] == "doughnut"
    assert sum(share["values"]) == pytest.approx(air.AIRLINE_DOM_TOTAL[1] / 1e6, abs=0.05)
    assert sum(built["air_top5_airport_share"]["values"]) == pytest.approx(420.089356, abs=0.01)
    assert sum(built["air_category_passenger_share"]["values"]) == pytest.approx(420.089, abs=0.01)


def test_world_bank_rank_note_matches_computed_rank(built):
    series = built["air_wb_recovery_2019"]
    assert series["labels"][0] == max(series["labels"], key=lambda n: series["values"][series["labels"].index(n)])
    rank = series["labels"].index("India") + 1
    assert f"India ranks {rank} of {len(series['labels'])}" in series["note"]


def test_world_aggregate_does_not_leak_into_peer_charts(built):
    assert "World" not in built["air_wb_passengers_rank"]["labels"]
    share = built["air_wb_india_share_passengers"]
    assert share["values"][0] == pytest.approx(1.0 / 40.0 * 100, abs=0.01)


def test_all_static_series_survive_when_every_fetch_fails():
    result = air.build_air_travel_layer(raising, {})
    assert len(result) >= 60
    assert not any(k.startswith("air_wb_") for k in result)
    assert "air_aai_decade_income" in result


def test_previous_world_bank_series_are_kept_when_fetch_fails():
    old = {"air_wb_india_passengers": {"labels": ["2023"], "values": [1.0], "source": "https://x", "note": "n", "meta": {}}}
    result = air.build_air_travel_layer(raising, old)
    assert result["air_wb_india_passengers"] is old["air_wb_india_passengers"]


def test_empty_world_bank_payload_drops_only_live_charts():
    result = air.build_air_travel_layer(lambda url: [{"page": 1}, None], {})
    assert not any(k.startswith("air_wb_") for k in result)
    assert "air_top10_airport_passengers" in result


def test_partial_world_bank_payload_with_only_india_skips_ranked_charts():
    result = air.build_air_travel_layer(lambda url: wb_payload(url, only={"IND"}), {})
    assert "air_wb_india_passengers" in result and "air_wb_india_passengers_yoy" in result
    assert "air_wb_passengers_rank" not in result and "air_wb_recovery_2019" not in result
    assert "air_wb_india_share_passengers" not in result


def test_one_failing_builder_does_not_stop_the_others(monkeypatch):
    def flaky(url):
        if "IS.AIR.DPRT" in url:
            raise OSError("boom")
        return wb_payload(url)

    result = air.build_air_travel_layer(flaky, {})
    assert "air_wb_departures_rank" not in result and "air_wb_passengers_rank" in result
