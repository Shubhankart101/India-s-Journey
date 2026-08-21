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
}


class DashboardEndpointTests(unittest.TestCase):
    def fetch(self, url):
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
        expected = {
            "cpi", "gst", "fiscal_deficit", "iip", "rupee", "trade",
            "forex", "bank_credit", "wpi", "upi", "gdp_per_capita",
            "population", "unemployment", "current_account", "broad_money",
            "tax_revenue", "government_consumption", "fdi", "domestic_savings",
            "electricity_access", "internet_users", "life_expectancy",
                    "homicide_rate", "lwe_incidents", "terror_attacks",
                                "terror_fatalities", "violent_incidents", "lwe_civilian_casualties",
                                "lwe_security_force_casualties", "lwe_perpetrator_casualties",
                    "indian_matrix",
                    "sensex", "nifty", "nifty_vix", "market_indices",
        }
        self.assertEqual(set(payload["series"]), expected)
        for key, series in payload["series"].items():
            self.assertTrue(series.get("values") or series.get("error"), key)

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
        self.assertIn(">🔗 References<".encode("utf-8"), body)
        self.assertIn(b"article-links", body)
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
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js?v=pew-group-strict-filters")
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
        expected_keys = {
            "ncrb_crime",
            "violent_incidents",
            "lwe_civilian_casualties",
            "lwe_security_force_casualties",
            "lwe_perpetrator_casualties",
            "indian_matrix_insights",
        }
        self.assertEqual(set(payload["series"]), expected_keys)
        for key, series in payload["series"].items():
            with self.subTest(indicator=key):
                self.assertIn("source", series, key)
                if key == "indian_matrix_insights":
                    self.assertIn("articles", series, key)
                    self.assertIn("key_analyses", series, key)
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

    def test_page_exposes_all_thirteen_subgroups(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        for subgroup in (
            "Macroeconomics", "Monetary Policy", "Trade &amp; External", "Markets",
            "Infrastructure", "Production &amp; Commodities", "Media &amp; Publications",
            "Demographics", "Welfare", "Public opinion",
            "Violence &amp; Crime", "Terrorism", "Maoism / LWE",
        ):
            self.assertIn(subgroup, text, subgroup)

    def test_page_has_dedicated_pew_research_group(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn('value="Pew Research"', text)
        self.assertIn(">Pew Research<", text)

    def test_app_js_requires_group_and_subgroup_before_showing_charts(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js?v=pew-group-strict-filters")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("groupFilter.value !== 'all' && subgroupFilter.value !== 'all'", text)
        self.assertIn("chart-prompt", text)

    def test_page_has_chart_prompt_element(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/")
        self.assertEqual(status, 200)
        self.assertIn(b'id="chart-prompt"', body)
        self.assertIn(b"Select both a Group and a Subgroup", body)

    def test_app_js_enables_legends_for_multi_dataset_charts_only(self):
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js?v=pew-group-strict-filters")
        self.assertEqual(status, 200)
        text = body.decode("utf-8")
        self.assertIn("hasMultipleDatasets", text)
        self.assertIn("display: hasMultipleDatasets", text)

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
