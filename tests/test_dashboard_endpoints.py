import json
import os
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
        expected.update({"sensex", "nifty", "nifty_vix"})
        self.assertEqual(set(payload["series"]), expected)
        for key, series in payload["series"].items():
            if key in ("market_indices", "gdp_world_comparison", "global_inflation_comparison", "global_equity_indices", "sectoral_market_indices", "defence_production_exports", "state_gsdp_comparison", "state_fdi_inflows", "state_debt_to_gsdp", "non_communicable_diseases_burden", "health_expenditure_gdp", "state_own_tax_revenue"):
                self.assertIn("labels", series, key)
                continue
            self.assertTrue(series.get("values") or series.get("error"), key)
            if series.get("values") and not series.get("error"):
                # app.js reads series.labels; a "years" key here silently drops the x-axis.
                self.assertIn("labels", series, f"{key} has values but no 'labels' key (found: {list(series.keys())})")
                self.assertNotIn("years", series, key)
                self.assertEqual(len(series["labels"]), len(series["values"]), key)

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
        self.assertIn(b"References: APIs", body)
        self.assertIn(b"chart-filter", body)
        self.assertIn(b"group-filter", body)
        self.assertIn(b"subgroup-filter", body)
        self.assertIn(b"Crime &amp; Security", body)
        self.assertIn(b"range-start", body)
        self.assertIn(b"range-end", body)
        self.assertIn(">🔗 References<".encode("utf-8"), body)
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
        }
        self.assertEqual(set(payload["series"]), expected_keys)
        for key, series in payload["series"].items():
            with self.subTest(indicator=key):
                self.assertEqual(len(series["labels"]), len(series["values"]), key)
                self.assertGreaterEqual(len(series["labels"]), 3, key)
                self.assertTrue(series["source"].startswith("https://www.pewresearch.org/"), key)
                for value in series["values"]:
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
        self.assertIn(b"PolityPolicy and Polity and Policy", body)
        self.assertIn(b"independent, separately-built project", body)

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
            "Strategic Stockpiles &amp; Capabilities",
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

    def test_page_has_chart_prompt_element(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b'id="charts"', body)
        

    def test_app_js_enables_legends_for_multi_dataset_charts_only(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("hasMultipleDatasets", text)
        self.assertIn("custom-legend", text)

    def test_daily_workflow_runs_all_collection_scripts(self):
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".github", "workflows", "daily-politypolicy-update.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as handle:
            workflow = handle.read()
        for script in (
            "scripts/generate_public_charts.py",
            "scripts/fetch_economic_survey_monthly.py",
            "scripts/collect_ncrb_and_analyses.py",
            "scripts/collect_pew_snapshots.py",
        ):
            self.assertIn(script, workflow, script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
