"""Offline contract tests for the Water Transport dashboard layer."""
from urllib.parse import unquote
import pytest
from scripts import water_transport_layer as water


def wb_payload(url):
    code=url.split("/indicator/")[1].split("?")[0]
    base=1000 if code==water.WB_CODES["container"] else 25
    return [{"page":1},[{"countryiso3code":c,"date":y,"value":base+i*100+j*10}
        for j,y in enumerate(("2021","2022","2023")) for i,c in enumerate(water.WB_PEERS)]]


def build(get_json=wb_payload,previous=None):
    return water.build_water_transport_layer(get_json,previous or {})


def test_exact_category_and_six_subgroups_are_populated():
    items=build()
    assert {s["meta"]["category"] for s in items.values()}=={water.CATEGORY}
    assert {s["meta"]["subgroup"] for s in items.values()}==set(water.SUBGROUPS)
    for group in water.SUBGROUPS: assert any(s["meta"]["subgroup"]==group for s in items.values())


def test_at_least_35_series_exist(): assert len(build())>=35

def test_every_key_has_water_prefix(): assert all(k.startswith("water_") for k in build())

def test_sources_are_https_and_explanations_complete():
    for item in build().values():
        assert item["source"].startswith("https://")
        assert set(item["meta"]["explain"])=={"what","read","why"}
        assert all(item["meta"]["explain"][field].strip() for field in ("what","read","why"))
        assert item["note"].strip()


def test_all_labels_are_strings_and_series_aligned():
    for item in build().values():
        assert all(isinstance(label,str) for label in item["labels"])
        if "values" in item: assert len(item["labels"])==len(item["values"])
        else: assert item["datasets"] and all(len(d["values"])==len(item["labels"]) for d in item["datasets"])


def test_major_port_ranking_uses_reported_provisional_data():
    item=build()["water_major_port_cargo_rank"]
    assert item["labels"][:3]==["Paradip","Deendayal (Kandla)","Jawaharlal Nehru"]
    assert item["values"][:3]==[145.38,132.37,85.82]
    assert "provisional" in item["note"]


def test_port_traffic_totals_reconcile():
    assert sum(water.PORT_2223)==pytest.approx(784.305)
    assert sum(water.PORT_2324)==pytest.approx(819.227)
    chart=build()["water_major_port_cargo_two_years"]
    assert sum(chart["datasets"][0]["values"])==pytest.approx(784.305)
    assert sum(chart["datasets"][1]["values"])==pytest.approx(819.227)


def test_commodity_mix_reconciles_to_total():
    assert sum(v[-1] for v in water.COMMODITIES.values())==pytest.approx(819.23)
    assert sum(build()["water_commodity_mix"]["values"])==pytest.approx(819.23)


def test_major_nonmajor_residuals_reconcile():
    chart=build()["water_major_nonmajor_cargo"]
    for i,total in enumerate((1434.19,1540.0)):
        assert chart["datasets"][0]["values"][i]+chart["datasets"][1]["values"][i]==pytest.approx(total)


def test_container_throughput_uses_teu_not_tonnage():
    item=build()["water_container_teu_trend"]
    assert item["unit"]=="million TEUs" and item["values"][-1]==12.31
    assert "Commodity-wise Cargo Traffic" in item["note"]


def test_world_bank_rank_explanation_matches_sorted_data():
    item=build()["water_wb_container_rank"]
    india_rank=item["labels"].index("India")+1
    assert item["labels"][india_rank-1]=="India"
    assert f"India ranks {india_rank} of {len(item['labels'])}" in item["meta"]["explain"]["read"]
    assert "2023" in item["note"]


def test_world_bank_peer_set_is_exact():
    assert water.WB_PEERS==("IND","CHN","SGP","USA","ARE","KOR","NLD","DEU","JPN","MYS","VNM","BRA","AUS")


def test_doughnuts_disclaim_global_or_market_share():
    result=build()
    assert "not global share" in result["water_wb_container_share"]["meta"]["subtitle"]
    assert "not market share" in result["water_wb_connectivity_share"]["meta"]["subtitle"]


def test_fetch_exception_preserves_previous_values():
    old={"labels":["old"],"values":[7],"source":"https://example.test/old"}
    result=build(lambda _:(_ for _ in ()).throw(OSError("offline")),{"water_wb_container_rank":old})
    assert result["water_wb_container_rank"]==old
    assert "water_major_port_cargo_rank" in result


def test_empty_wb_response_falls_back_and_keeps_static_charts():
    old={"labels":["old"],"values":[1],"source":"https://example.test/old"}
    result=build(lambda _:[{"page":1},[]],{"water_wb_container_trend":old})
    assert result["water_wb_container_trend"]==old
    assert "water_major_port_cargo_rank" in result


def test_partial_wb_payload_uses_only_available_countries():
    def partial(_): return [{"page":1},[
        {"countryiso3code":"IND","date":"2022","value":10},
        {"countryiso3code":"CHN","date":"2022","value":30},
        {"countryiso3code":"IND","date":"2023","value":12}]]
    result=build(partial)
    assert [d["label"] for d in result["water_wb_container_trend"]["datasets"]]==["India","China"]
    rank=result["water_wb_container_rank"]
    assert rank["labels"]==["China","India"]
    assert "India ranks 2 of 2" in rank["meta"]["explain"]["read"]


def test_partial_payload_without_common_year_does_not_invent_rank():
    def partial(_): return [{"page":1},[
        {"countryiso3code":"IND","date":"2021","value":10},
        {"countryiso3code":"CHN","date":"2022","value":30}]]
    result=build(partial)
    assert "water_wb_container_trend" in result
    assert "water_wb_container_rank" not in result


def test_series_notes_match_their_official_source_documents():
    for item in build().values():
        if item["source"] == water.REPORT:
            assert "Annual Report 2023-24" in item["note"]
        elif item["source"] == water.IWT_STATS:
            assert "Statistics of Inland Water Transport 2022-23" in item["note"]
        elif item["source"] == water.SANSAD_PASSENGERS:
            assert "Lok Sabha" in item["note"]
        elif item["source"] == water.PIB_CRUISE:
            assert "PIB release" in item["note"]
        elif item["source"].startswith("https://api.worldbank.org/"):
            assert "World Bank" in item["note"]
        else:
            pytest.fail(f"Unrecognized source on series: {item['source']}")


def test_turnaround_and_berth_values_match_report():
    result=build()
    assert result["water_port_turnaround_history"]["values"]==[52.90,48.06]
    assert result["water_ship_berth_output_history"]["values"]==[17605,18925]
    assert result["water_container_ship_turnaround"]["values"]==[30.10,30.12]


def test_capacity_ratio_uses_reported_data():
    item=build()["water_major_port_capacity_utilization"]
    assert item["values"][-1]==pytest.approx(819.23/1629.86*100,abs=.01)
    assert "calculated" in item["note"]


def test_world_bank_sources_point_to_requested_indicator_api():
    result=build()
    for key,code in (("water_wb_container_trend",water.WB_CODES["container"]),
                     ("water_wb_connectivity_trend",water.WB_CODES["connectivity"])):
        assert f"/indicator/{code}?" in result[key]["source"]
        assert "IND;CHN;SGP;USA;ARE;KOR;NLD;DEU;JPN;MYS;VNM;BRA;AUS" in unquote(result[key]["source"])


NEW_PASSENGER_SERIES = (
    "water_national_waterway_passenger_history",
    "water_inland_passenger_state_trends",
    "water_assam_inland_passengers",
    "water_karnataka_inland_passengers",
    "water_kerala_inland_passengers",
    "water_maharashtra_inland_passengers",
    "water_west_bengal_inland_passengers",
    "water_inland_passenger_state_rank_2023",
    "water_ocean_cruise_passenger_history",
    "water_ocean_cruise_call_history",
)


def test_at_least_eight_new_verified_passenger_series_are_present():
    result = build()
    assert len(NEW_PASSENGER_SERIES) >= 8
    assert set(NEW_PASSENGER_SERIES) <= result.keys()
    assert all(result[key]["meta"]["subgroup"] == water.PASSENGER for key in NEW_PASSENGER_SERIES)


def test_parliamentary_national_waterway_passenger_totals_and_basis():
    item = build()["water_national_waterway_passenger_history"]
    assert item["labels"] == ["2023-24", "2024-25"]
    assert item["values"] == [1.61, 7.64]
    assert item["unit"] == "crore passengers"
    assert item["source"] == water.SANSAD_PASSENGERS
    assert "12 December 2025" in item["note"]
    assert "National Waterways" in item["note"]


def test_state_passenger_histories_match_mopsw_table_3_2():
    result = build()
    chart = result["water_inland_passenger_state_trends"]
    assert chart["labels"] == ["2019", "2020", "2021", "2022", "2023"]
    assert chart["source"] == water.IWT_STATS
    actual = {dataset["label"]: dataset["values"] for dataset in chart["datasets"]}
    assert actual == water.IWT_STATE_PASSENGERS
    for state, slug in (("Assam", "assam"), ("Karnataka", "karnataka"), ("Kerala", "kerala"),
                        ("Maharashtra", "maharashtra"), ("West Bengal", "west_bengal")):
        item = result[f"water_{slug}_inland_passengers"]
        assert item["labels"] == chart["labels"]
        assert item["values"] == water.IWT_STATE_PASSENGERS[state]
        assert item["unit"] == "thousand passengers"
        assert item["source"] == water.IWT_STATS
        assert "Table 3.2" in item["note"] and "printed p.62" in item["note"]


def test_state_rank_omits_rows_marked_unavailable_or_repeated():
    item = build()["water_inland_passenger_state_rank_2023"]
    assert item["source"] == water.IWT_STATS
    assert "Bihar" not in item["labels"] and "Odisha" not in item["labels"]
    assert item["labels"][0] == "West Bengal"
    assert item["values"][0] == pytest.approx(29762.61)
    assert item["labels"][-1] == "Uttar Pradesh"
    assert item["values"][-1] == pytest.approx(23.86)
    assert "previous-year-repeated" in item["note"]


def test_cruise_history_uses_exact_pib_years_and_separate_units():
    result = build()
    passengers = result["water_ocean_cruise_passenger_history"]
    calls = result["water_ocean_cruise_call_history"]
    assert passengers["labels"] == calls["labels"] == ["2013-14", "2022-23"]
    assert passengers["values"] == [0.84, 4.72]
    assert passengers["unit"] == "lakh passengers"
    assert calls["values"] == [102, 227]
    assert calls["unit"] == "calls"
    assert passengers["source"] == calls["source"] == water.PIB_CRUISE


def test_mopsw_cruise_snapshot_does_not_infer_an_unreported_year():
    result = build()
    for key, value in (("water_ocean_cruise_passengers", 471000), ("water_ocean_cruise_calls", 227)):
        item = result[key]
        assert item["datasets"][0]["values"] == [value]
        assert item["labels"] == ["Annual-report snapshot"]
        assert "does not state the observation period" in item["note"] or "observation period not stated" in item["note"]
