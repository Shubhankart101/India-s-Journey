import json
import os
import re
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DASHBOARD_URL = os.environ.get(
    "DASHBOARD_URL",
    "https://shubhankart101.github.io/India-s-Journey/",
).rstrip("/")

OFFICIAL_SOURCES = {
    "world_bank": "https://api.worldbank.org/v2/country/IND/indicator/FP.CPI.TOTL.ZG?format=json&per_page=1",
    "gst": "https://www.gst.gov.in/",
    "fiscal_deficit": "https://cga.nic.in/",
    "mospi": "https://www.mospi.gov.in/",
    "rbi": "https://data.rbi.org.in/DBIE/",
    "wpi": "https://eaindustry.nic.in/",
    "upi": "https://www.npci.org.in/what-we-do/upi/product-statistics",
}

LIVE_API_SOURCES = {
    "cpi": "FP.CPI.TOTL.ZG",
    "trade": "NE.TRD.GNFS.ZS",
    "forex": "FI.RES.TOTL.CD",
    "bank_credit": "FS.AST.PRVT.GD.ZS",
    "iip": "NV.IND.TOTL.KD.ZG",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "private_consumption_pc": "NE.CON.PRVT.PC.KD",
    "rupee": "PA.NUS.FCRF",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "population": "SP.POP.TOTL",
    "unemployment": "SL.UEM.TOTL.ZS",
    "current_account": "BN.CAB.XOKA.GD.ZS",
    "broad_money": "FM.LBL.BMNY.GD.ZS",
    "tax_revenue": "GC.TAX.TOTL.GD.ZS",
    "government_consumption": "NE.CON.GOVT.ZS",
    "fdi": "BX.KLT.DINV.WD.GD.ZS",
    "domestic_savings": "NY.GDS.TOTL.ZS",
    "electricity_access": "EG.ELC.ACCS.ZS",
    "internet_users": "IT.NET.USER.ZS",
    "life_expectancy": "SP.DYN.LE00.IN",
    "homicide_rate": "VC.IHR.PSRC.P5",
    "defence_expenditure": "MS.MIL.XPND.GD.ZS",
}


class DashboardEndpointTests(unittest.TestCase):
    def fetch(self, url):
        if url.startswith(DASHBOARD_URL):
            from pathlib import Path
            rel = url[len(DASHBOARD_URL):].lstrip("/")
            root = Path(__file__).resolve().parents[1]
            candidates = [root / "docs" / rel, root / rel, root / "data" / rel]
            if rel == "" or rel == "/":
                candidates = [root / "docs" / "index.html"]
            for cand in candidates:
                if cand.is_file():
                    return 200, cand.read_bytes()
        request = Request(
            url,
            headers={
                "User-Agent": "PolityPolicyUpdate endpoint monitor",
                "Accept": "application/json,text/html,*/*;q=0.8",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()
        except URLError as error:
            self.fail(f"Endpoint could not be reached: {url} ({error.reason})")

    def test_dashboard_page_is_served(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b"India's Journey", body)

    def test_dashboard_data_has_all_indicators(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/data/chart-latest.json")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        expected = {'pm_jan_dhan_yojana', 'fuel_consumption', 'broad_money', 'state_fdi_inflows', 'state_infant_mortality_rate', 'defence_exports', 'iron_ore_exports', 'budget_yoy_growth', 'state_national_highway_length', 'crude_petroleum_domestic', 'maternal_mortality_ratio', 'per_capita_income_ppp', 'debit_card_spends', 'fdi', 'rare_earths_critical_minerals', 'state_ev_adoption_charging', 'state_mudra_loans', 'lwe_security_force_casualties', 'cpi', 'lwe_incidents', 'trade', 'gross_tax_yoy_growth', 'railway_electrification', 'defence_rd_budget', 'state_gsdp_comparison', 'child_protection_pocso', 'population', 'natural_gas_production', 'iron_ore_production', 'credit_card_spends', 'khalistan_insurgency_historical', 'kashmir_terror_incidents', 'state_operating_factories', 'gdp_world_comparison', 'pm_awas_yojana', 'state_export_preparedness_index', 'unemployment', 'non_communicable_diseases_burden', 'state_manufacturing_gsdp_share', 'state_renewable_energy_capacity', 'merchandise_exports', 'union_budget_expenditure', 'power_consumption', 'terror_attacks', 'religious_demographics', 'merchandise_imports', 'indian_matrix', 'ncrb_ipc_crime_rate', 'economic_offences', 'state_pmay_homes', 'northeast_insurgency_fatalities', 'police_per_population', 'pew_india_media_news', 'ndps_drug_cases', 'port_cargo', 'sc_st_post_matric_scholarships', 'market_indices', 'tax_revenue', 'state_per_capita_income', 'violent_incidents', 'crimes_against_women', 'pew_india_leadership', 'pew_india_global_power', 'lwe_civilian_casualties', 'rail_freight', 'telecom_broadband_subscribers', 'civil_aviation_passengers', 'ayushman_bharat', 'tb_disease_incidence', 'pm_mudra_social_breakdown', 'core_industries', 'rock_phosphate_gypsum', 'credit_card_in_circulation', 'pew_india_technology', 'infant_mortality_rate', 'pew_india_climate_environment', 'defence_production', 'defence_production_exports', 'pew_india_reports', 'coal_production', 'electronics_manufacturing', 'sectoral_market_indices', 'critical_mineral_import_dependency', 'forex', 'bank_credit', 'ncrb_crime', 'state_gst_collections', 'auto_production_volume', 'crude_oil', 'fiscal_deficit', 'national_highways_built', 'defence_expenditure', 'rbi_digital_payments_index', 'northeast_insurgency_incidents', 'global_inflation_comparison', 'renewable_energy_capacity', 'internet_users', 'wpi', 'homicide_rate', 'per_capita_nni_inr', 'current_account', 'capital_expenditure_capex', 'limestone_production', 'government_consumption', 'pew_india_demographics_family', 'pew_india_us_relations', 'state_pmjay_health_cards', 'manganese_chromite_production', 'pharma_exports_trajectory', 'defence_stockpile', 'textiles_apparel_exports', 'domestic_savings', 'global_equity_indices', 'state_debt_to_gsdp', 'crude_steel_production', 'refined_petroleum_exports', 'pew_india_economy_confidence', 'electricity_access', 'cyber_crime', 'state_own_tax_revenue', 'eway_bills', 'pew_india_gender_roles', 'state_pmsvanidhi_street_vendors', 'state_literacy_rates', 'social_category_literacy', 'defence_capital_acquisition', 'debit_card_in_circulation', 'gst', 'kashmir_insurgency_fatalities', 'road_accidents_fatalities', 'pm_svanidhi_street_vendors', 'state_jjm_water_coverage', 'lwe_perpetrator_casualties', 'state_ease_of_doing_business', 'state_pmjdy_bank_accounts', 'gdp_per_capita', 'state_life_expectancy', 'defence_budget_share', 'copper_production', 'mineral_metal_exports', 'upi', 'jal_jeevan_mission', 'lignite_production', 'health_expenditure_gdp', 'life_expectancy', 'sipri_arms_imports', 'iip', 'pew_india_religion_tolerance', 'rupee', 'bauxite_aluminium_output', 'upi_transaction_value', 'terror_fatalities'}
        expected.update({"sensex", "nifty", "nifty_vix", "gdp_growth", "merchandise_trade_balance", "bilateral_trade_balance", "private_consumption_pc", "auto_domestic_sales", "state_power_per_capita", "terror_attacks_per_million", "terror_fatalities_per_million", "terror_fatalities_per_attack"})
        expected.update({
            "gdp_ppp", "gdp_deflator_growth", "capital_formation_gdp", "household_consumption_gdp",
            "gross_savings_rate", "exports_gdp", "imports_gdp", "remittances_gdp",
            "reserves_import_months", "debt_service_exports", "public_debt_gdp",
            "current_health_spending", "physicians_density", "under5_mortality",
            "basic_water_access", "basic_sanitation_access", "urban_population_share",
            "population_growth", "fertility_rate", "crude_birth_rate", "crude_death_rate",
            "agricultural_employment_share", "urban_population_growth", "net_energy_imports_share",
            "lower_secondary_completion", "government_health_spending_per_capita",
            "safely_managed_drinking_water",
            "clean_fuel_access", "primary_school_enrollment",
            "secondary_school_enrollment", "tertiary_school_enrollment", "education_spending_gdp",
            "female_labor_participation", "labor_force_participation",
            "employment_population_ratio", "adult_literacy_rate", "agriculture_gdp_share",
            "industry_gdp_share", "services_gdp_share", "manufacturing_gdp_share",
            "agricultural_land_share", "cereal_yield", "energy_use_per_capita",
            "electricity_use_per_capita", "renewable_energy_consumption",
            "renewable_electricity_output", "pm25_exposure", "forest_area_share",
            "mobile_subscriptions_per_100", "fixed_broadband_per_100",
            "military_expenditure_usd", "state_gsdp_share", "state_per_capita_income_index",
            "state_power_availability_index", "cyber_crime_rate", "ndps_case_rate",
            "road_fatality_rate", "pew_india_religious_pluralism",
            "pew_india_religious_practice", "card_spend_total", "credit_card_spend_share",
            "upi_value_growth", "military_expenditure_per_capita",
            "upi_volume_index", "pew_india_2026_global_views",
            "pew_india_2026_top_threats", "pew_india_2026_top_allies",
            "pew_india_2021_diversity_views", "pew_india_2021_religious_freedom",
            "tourism_arrivals", "tourism_departures", "tourism_receipts_usd",
            "unesco_india_sites_cumulative", "unesco_india_new_inscriptions",
            "unesco_india_current_categories",
        })
        expected.update({
            "gdp_sector_composition",
            "state_gsdp_composition",
            "urban_rural_population_composition",
            "energy_supply_composition",
            "disease_burden_composition",
            "defence_budget_composition",
            "card_spending_composition",
        })
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
        from official_indicator_layer import COMPOSITIONS, LINE_INDICATORS
        expected.update(row[0] for row in LINE_INDICATORS + COMPOSITIONS)
        import derived_pie_layer as derived
        for specs in (derived.CUMULATIVE, derived.LATEST, derived.BINARY, derived.PERIODS, derived.REGION_PIES):
            expected.update(row[0] for row in specs)
        expected.add("auto_domestic_sales_mix")
        self.assertEqual(set(payload["series"]), expected)
        for key, series in payload["series"].items():
            if series.get("datasets"):
                self.assertEqual(len(series.get("labels", [])), len(series["datasets"][0].get("values", [])), key)
                for dataset in series["datasets"]:
                    self.assertEqual(len(series["labels"]), len(dataset.get("values", [])), key)
                continue
            if key in ("market_indices", "gdp_world_comparison", "global_inflation_comparison", "global_equity_indices", "sectoral_market_indices", "defence_production_exports", "state_fdi_inflows", "state_debt_to_gsdp", "non_communicable_diseases_burden", "health_expenditure_gdp", "state_own_tax_revenue"):
                self.assertIn("labels", series, key)
                continue
            self.assertTrue(series.get("values") or series.get("error"), key)
            if series.get("values") and not series.get("error"):
                # app.js reads series.labels; a "years" key here silently drops the x-axis.
                self.assertIn("labels", series, f"{key} has values but no 'labels' key (found: {list(series.keys())})")
                self.assertNotIn("years", series, key)
                self.assertEqual(len(series["labels"]), len(series["values"]), key)
        for key in ("gdp_growth", "merchandise_trade_balance", "bilateral_trade_balance", "private_consumption_pc", "auto_production_volume", "auto_domestic_sales"):
            self.assertGreaterEqual(len(payload["series"][key].get("labels", [])), 5, key)
        self.assertIn("UN Comtrade", payload["series"]["bilateral_trade_balance"].get("source", ""))
        self.assertIn("SIAM", payload["series"]["auto_domestic_sales"].get("source", ""))
        self.assertGreaterEqual(len(payload["series"]["auto_domestic_sales"].get("datasets", [])), 4)
        state_series_keys = (
            "state_gsdp_comparison",
            "state_per_capita_income",
            "state_power_per_capita",
            "state_gsdp_share",
            "state_per_capita_income_index",
            "state_power_availability_index",
            "state_pmjdy_bank_accounts",
        )
        expected_states = {
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        }
        for key in state_series_keys:
            series = payload["series"][key]
            self.assertEqual(len(series.get("labels", [])), 28, key)
            self.assertEqual(len(series.get("values", [])), 28, key)
            self.assertTrue(all(value is not None for value in series["values"]), key)
            self.assertEqual(series.get("scope"), "state", key)
            self.assertEqual(series.get("chartType"), "bar", key)
            self.assertEqual(series.get("indexAxis"), "y", key)
            self.assertEqual(set(series["labels"]), expected_states, key)
            self.assertIn("PMJDY" if key == "state_pmjdy_bank_accounts" else "RBI", series.get("source", ""))
        for key in ("state_gsdp_share", "state_per_capita_income_index", "state_power_availability_index"):
            self.assertIn(payload["series"][key].get("unit"), {"% of reported total", "index (median = 100)"}, key)
        for key in ("terror_attacks_per_million", "terror_fatalities_per_million", "terror_fatalities_per_attack"):
            series = payload["series"][key]
            self.assertGreaterEqual(len(series.get("labels", [])), 40, key)
            self.assertEqual(len(series["labels"]), len(series["values"]), key)
            self.assertIn("World Bank population", series.get("source", ""))

    def test_chart_source_index_has_graph_level_urls(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b'id="chart-source-index-list"', body)
        self.assertIn(b'id="chart-focus-overlay"', body)
        self.assertNotIn(b'id="range-start"', body)
        self.assertNotIn(b'id="range-end"', body)
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        self.assertIn(b"renderChartSourceIndex", body)
        self.assertIn(b"definition[8]", body)
        self.assertIn(b"chart-range-start", body)
        self.assertIn(b"expand-chart-btn", body)
        self.assertIn(b"hasSelectedScope", body)

    def test_additional_sourced_charts_cover_dashboard_groups(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "docs", "index.html"), "r", encoding="utf-8") as handle:
            page = handle.read()
        with open(os.path.join(root, "docs", "additional-chart-definitions.js"), "r", encoding="utf-8") as handle:
            definitions = handle.read()
        with open(os.path.join(root, "docs", "app.js"), "r", encoding="utf-8") as handle:
            app = handle.read()
        status, body = self.fetch(f"{DASHBOARD_URL}/data/chart-latest.json")
        self.assertEqual(status, 200)
        series = json.loads(body)["series"]
        election_status, election_body = self.fetch(f"{DASHBOARD_URL}/data/election-results.json")
        self.assertEqual(election_status, 200)
        election_series = json.loads(election_body)["series"]
        finance_status, finance_body = self.fetch(f"{DASHBOARD_URL}/data/us-campaign-finance.json")
        self.assertEqual(finance_status, 200)
        finance_series = json.loads(finance_body)["series"]
        self.assertIn("additional-chart-definitions.js", page)
        self.assertGreaterEqual(definitions.count("worldBank('"), 35)
        self.assertIn("INDIA_EXTRA_CHART_PLACEMENT", definitions)
        self.assertIn("definitions.push(...(window.INDIA_EXTRA_CHART_DEFINITIONS || []))", app)
        keys = re.findall(r"worldBank\('([^']+)'", definitions)
        keys.extend(re.findall(r"^\s+\['([^']+)'", definitions, flags=re.MULTILINE))
        self.assertEqual(len(keys), 80)
        for key in keys:
            with self.subTest(chart=key):
                source = (
                    election_series
                    if key.startswith("india_live_") or key.startswith("us_presidential_electoral_composition_")
                    else finance_series
                    if key.startswith("us_fec_")
                    else series
                )
                self.assertIn(key, source)
                item = source[key]
                self.assertTrue(item.get("values") or any(dataset.get("values") for dataset in item.get("datasets", [])), key)
                if item.get("values"):
                    self.assertEqual(len(item.get("labels", [])), len(item["values"]), key)
                for dataset in item.get("datasets", []):
                    self.assertEqual(len(item.get("labels", [])), len(dataset.get("values", [])), key)
                self.assertIn("source", item, key)

    def test_new_pew_and_government_series_are_sourced_and_shaped(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/data/chart-latest.json")
        self.assertEqual(status, 200)
        series = json.loads(body)["series"]
        global_views = series["pew_india_2026_global_views"]
        self.assertEqual(len(global_views["labels"]), 36)
        self.assertEqual(len(global_views["datasets"]), 3)
        self.assertTrue(all(len(dataset["values"]) == 36 for dataset in global_views["datasets"]))
        self.assertIn("2026", global_views["source"])
        for key in ("pew_india_2026_top_threats", "pew_india_2026_top_allies", "pew_india_2021_diversity_views", "pew_india_2021_religious_freedom"):
            self.assertTrue(series[key]["values"], key)
            self.assertIn("pewresearch.org", series[key]["source"], key)
        upi_index = series["upi_volume_index"]
        self.assertEqual(upi_index["values"][0], 100)
        self.assertEqual(upi_index["labels"], series["upi"]["labels"])
        self.assertIn("Economic Survey", upi_index["source"])

    def test_official_sources_are_reachable_or_explicitly_protected(self):
        for name, url in OFFICIAL_SOURCES.items():
            with self.subTest(source=name):
                status, _ = self.fetch(url)
                self.assertTrue(
                    200 <= status < 400 or status in {401, 403},
                    f"Unexpected HTTP status {status} from {url}",
                )

    def test_every_live_indicator_api_returns_observations(self):
        for key, indicator in LIVE_API_SOURCES.items():
            url = f"https://api.worldbank.org/v2/country/IND/indicator/{indicator}?format=json&per_page=100"
            with self.subTest(indicator=key):
                status, body = self.fetch(url)
                self.assertEqual(status, 200)
                payload = json.loads(body)
                self.assertIsInstance(payload, list)
                self.assertGreaterEqual(len(payload), 2)
                self.assertTrue(any(row.get("value") is not None for row in payload[1]), key)

    def test_page_references_runtime_and_data_assets(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b"Project references, data methods", body)
        self.assertIn(b'id="references"', body)
        self.assertIn(b'id="saved-toggle"', body)
        self.assertIn(b'id="chart-result-count"', body)
        self.assertIn(b"group-filter", body)
        self.assertIn(b"subgroup-filter", body)
        self.assertIn(b"Crime &amp; Security", body)
        self.assertNotIn(b'id="range-start"', body)
        self.assertNotIn(b'id="range-end"', body)
        self.assertIn(b'id="chart-focus-overlay"', body)
        self.assertIn(b"Sources &amp; references", body)
        self.assertIn(b"article-links", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/economic-survey-monthly.json")
        self.assertEqual(status, 200)
        self.assertIn(b"series", body)
        monthly = json.loads(body)
        for key in ("gst", "upi", "iip", "forex", "rupee", "wpi"):
            self.assertGreaterEqual(len(monthly["series"][key].get("labels", [])), 12, key)
            self.assertRegex(monthly["series"][key]["labels"][0], r"^\d{4}-\d{2}$")
        self.assertGreaterEqual(len(monthly["series"]["fiscal_deficit"].get("labels", [])), 4)
        for key in ("power_consumption", "eway_bills", "rail_freight", "port_cargo", "core_industries", "crude_oil", "fuel_consumption", "merchandise_exports", "merchandise_imports"):
            self.assertGreaterEqual(len(monthly["series"][key].get("labels", [])), 12, key)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/substack-latest.json")
        self.assertEqual(status, 200)
        self.assertIn(b"articles", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/indian-matrix-latest.json")
        self.assertEqual(status, 200)
        self.assertIn(b"cadence", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/pew-india-reports.json")
        self.assertEqual(status, 200)
        self.assertIn(b"reports", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/ncrb-and-analyses.json")
        self.assertEqual(status, 200)
        self.assertIn(b"series", body)
        ncrb_data = json.loads(body)
        for key in ("ncrb_crime", "violent_incidents", "lwe_civilian_casualties", "lwe_security_force_casualties", "lwe_perpetrator_casualties"):
            self.assertIn(key, ncrb_data["series"], key)
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        self.assertIn(b"updateCards", body)

    def test_pew_snapshot_data_is_verifiable_and_sourced(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/data/pew-snapshots.json")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        expected_keys = {
            "pew_india_economy_confidence",
            "pew_india_us_relations",
            "pew_india_global_power",
            "pew_india_leadership",
            "pew_india_technology",
            "pew_india_religion_tolerance",
            "pew_india_demographics_family",
            "pew_india_gender_roles",
            "pew_india_media_news",
            "pew_india_climate_environment",
            "pew_india_2026_global_views",
            "pew_india_2026_top_threats",
            "pew_india_2026_top_allies",
            "pew_india_2021_diversity_views",
            "pew_india_2021_religious_freedom",
        }
        self.assertEqual(set(payload["series"]), expected_keys)
        for key, series in payload["series"].items():
            with self.subTest(indicator=key):
                values_by_dataset = [
                    dataset["values"] for dataset in series.get("datasets", [])
                ] or [series["values"]]
                self.assertGreaterEqual(
                    len(series["labels"]),
                    2 if key in {
                        "pew_india_2026_top_threats",
                        "pew_india_2026_top_allies",
                        "pew_india_2021_religious_freedom",
                    } else 3,
                    key,
                )
                self.assertTrue(series["source"].startswith("https://www.pewresearch.org/"), key)
                for values in values_by_dataset:
                    self.assertEqual(len(series["labels"]), len(values), key)
                    for value in values:
                        self.assertGreaterEqual(value, 0, key)
                        self.assertLessEqual(value, 100, key)

    def test_ncrb_and_analyses_series_are_present_and_pending_or_valid(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/data/ncrb-and-analyses.json")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        expected_keys = {'cyber_crime', 'ncrb_crime', 'kashmir_insurgency_fatalities', 'road_accidents_fatalities', 'ncrb_ipc_crime_rate', 'economic_offences', 'northeast_insurgency_fatalities', 'lwe_perpetrator_casualties', 'lwe_security_force_casualties', 'northeast_insurgency_incidents', 'police_per_population', 'lwe_incidents', 'ndps_drug_cases', 'indian_matrix_insights', 'child_protection_pocso', 'violent_incidents', 'crimes_against_women', 'lwe_civilian_casualties', 'khalistan_insurgency_historical', 'kashmir_terror_incidents'}
        self.assertEqual(set(payload["series"]), expected_keys)
        for key, series in payload["series"].items():
            with self.subTest(indicator=key):
                self.assertIn("source", series, key)
                if key == "indian_matrix_insights":
                    self.assertIn("articles", series, key)
                    self.assertIn("key_analyses", series, key)
                elif key in ("lwe_civilian_casualties", "lwe_security_force_casualties", "lwe_perpetrator_casualties"):
                    self.assertIn("labels", series, key)
                    self.assertIn("values", series, key)
                    self.assertEqual(len(series["labels"]), len(series["values"]), key)
                    self.assertGreaterEqual(len(series["values"]), 20, key)
                    self.assertTrue(series["source"].startswith("https://www.satp.org/"), key)
                elif key in ("cyber_crime", "ncrb_crime", "kashmir_insurgency_fatalities", "road_accidents_fatalities", "ncrb_ipc_crime_rate", "economic_offences", "northeast_insurgency_fatalities", "northeast_insurgency_incidents", "police_per_population", "lwe_incidents", "ndps_drug_cases", "child_protection_pocso", "violent_incidents", "crimes_against_women", "khalistan_insurgency_historical", "kashmir_terror_incidents"):
                    self.assertIn("labels", series, key)
                    self.assertIn("values", series, key)
                    self.assertEqual(len(series["labels"]), len(series["values"]), key)
                    self.assertGreaterEqual(len(series["values"]), 5, key)
                else:
                    self.assertIn("years", series, key)
                    self.assertIn("values", series, key)
                    self.assertEqual(len(series["years"]), len(series["values"]), key)

    def test_page_has_dedicated_polity_policy_section(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b'id="polity-policy-title"', body)
        self.assertIn(b"Polity and Policy latest articles", body)
        self.assertIn(b"This is an independent project and does not represent those publishers.", body)
        self.assertIn(b'href="https://politypolicy.com/"', body)
        self.assertIn(b'href="https://politypolicy.substack.com/"', body)

    def test_page_exposes_all_subgroups(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        for subgroup in (
            "Macroeconomics", "Monetary Policy", "Trade &amp; External", "Markets",
            "Infrastructure", "Production &amp; Commodities", "Media &amp; Publications",
            "Demographics", "Welfare", "Public opinion",
            "Violence &amp; Crime", "Terrorism", "Maoism / LWE",
            "Defence Exports &amp; Production", "Defence Budget &amp; Modernization",
            "Strategic Stockpiles &amp; Capabilities", "State Infrastructure &amp; Services",
        ):
            self.assertIn(subgroup, text, subgroup)

    def test_page_has_dedicated_pew_research_group(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn('value="Pew Research"', text)
        self.assertIn(">Pew Research<", text)

    def test_page_has_separate_polity_policy_article_rail(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b'<details class="reading-list-popover">', body)
        self.assertIn(b'class="reading-list-panel"', body)
        styles_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs", "styles.css",
        )
        with open(styles_path, "rb") as styles:
            self.assertIn(b"reading-list-popover[open]", styles.read())
        self.assertIn(b'id="pp-article-links"', body)
        self.assertIn(b"Polity and Policy latest articles", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/substack-latest.json")
        self.assertEqual(status, 200)
        self.assertIn(b"articles", body)

    def test_app_js_renders_both_article_rails_from_distinct_sources(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("pp-article-links", text)
        self.assertIn("renderArticles", text)

    def test_app_js_renders_and_updates_cards(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("updateCards", text)
        self.assertIn("indexAxis: horizontalBars ? 'y' : 'x'", text)

    def test_page_has_chart_prompt_element(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b'id="charts"', body)
        self.assertIn(b'id="indicator-modal"', body)
        self.assertIn(b'id="modal-close"', body)
        self.assertIn(b'id="modal-body"', body)
        self.assertIn(b'aria-modal="true"', body)
        self.assertIn(b'styles.css?v=more-pies-v4', body)
        styles_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs", "styles.css",
        )
        with open(styles_path, "r", encoding="utf-8") as handle:
            self.assertIn(".modal-overlay[hidden] { display:none; }", handle.read())
        

    def test_app_js_enables_legends_for_multi_dataset_charts_only(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("hasMultipleDatasets", text)
        self.assertIn("custom-legend", text)
        self.assertIn("generateLabels: chart =>", text)
        self.assertIn("chart.getDataVisibility(index)", text)
        self.assertIn("chart.toggleDataVisibility(elements[0].index)", text)
        self.assertIn("toFixed(1)", text)

    def test_deep_dive_button_opens_and_closes_modal(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("openIndicatorModal(key, title, subtitle, frequency, suffix, source, details, series, category, dashboardSubgroupFor(key))", text)
        self.assertIn("modal.hidden = false", text)
        self.assertIn("modalCloseBtn.addEventListener('click'", text)
        self.assertIn("e.key === 'Escape'", text)

    def test_collection_scripts_run_on_dataset_cadence_schedules(self):
        workflows_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".github", "workflows",
        )
        expected = {
            "daily-politypolicy-update.yml": ("'30 2 * * *'", (
                "scripts/collect_substack.py", "scripts/collect_indian_matrix.py",
                "scripts/collect_us_campaign_finance.py", "scripts/generate_public_charts.py")),
            "weekly-pew-research-update.yml": ("'0 4 * * 1'", (
                "scripts/collect_pew_snapshots.py", "scripts/collect_pew_india_reports.py",
                "scripts/generate_public_charts.py")),
            "monthly-economic-review-update.yml": ("'0 4 5,15,25 * *'", (
                "scripts/fetch_economic_survey_monthly.py", "scripts/generate_public_charts.py")),
            "ncrb-crime-data-update.yml": ("'30 5 1 * *'", (
                "scripts/collect_ncrb_and_analyses.py", "scripts/generate_public_charts.py")),
            "recent-indian-elections-update.yml": ("'15 8 * * *'", (
                "scripts/collect_recent_indian_elections.py", "scripts/build_election_indices.py")),
        }
        for file_name, (cron, scripts) in expected.items():
            with open(os.path.join(workflows_dir, file_name), "r", encoding="utf-8") as handle:
                workflow = handle.read()
            with self.subTest(workflow=file_name):
                self.assertIn(f"cron: {cron}", workflow)
                for script in scripts:
                    self.assertIn(script, workflow, script)
                if "generate_public_charts" in workflow:
                    self.assertIn("group: daily-public-data", workflow)
                self.assertIn("git rebase origin/main", workflow)

    def test_dashboard_deploys_after_article_collection_workflows(self):
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".github", "workflows", "deploy-dashboard.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as handle:
            workflow = handle.read()
        self.assertIn("workflow_run:", workflow)
        for name in ("Daily PolityPolicy Update", "Weekly Substack Article Update", "Weekly Pew Research Update",
                     "Monthly Economic Review Update", "NCRB Crime Data Update", "Recent Indian Election Data Update"):
            self.assertIn(f"- {name}", workflow)
        self.assertIn("site/data/election-indices.json", workflow)
        self.assertIn("workflow_run.conclusion == 'success'", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
