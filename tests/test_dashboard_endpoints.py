import json
import os
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DASHBOARD_URL = os.environ.get(
    "DASHBOARD_URL",
    "https://shubhankart101.github.io/PolityPolicyUpdate/",
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
        self.assertIn(b"range-start", body)
        self.assertIn(b"range-end", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/economic-survey-monthly.json")
        self.assertEqual(status, 200)
        self.assertIn(b"series", body)
        monthly = json.loads(body)
        for key in ("gst", "upi", "iip", "forex", "rupee"):
            self.assertGreaterEqual(len(monthly["series"][key].get("labels", [])), 12, key)
            self.assertRegex(monthly["series"][key]["labels"][0], r"^\d{4}-\d{2}$")
        self.assertIn(">🔗 References<".encode("utf-8"), body)
        self.assertIn(b"article-links", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/data/substack-latest.json")
        self.assertEqual(status, 200)
        self.assertIn(b"articles", body)
        status, body = self.fetch(f"{DASHBOARD_URL}/app.js?v=40677a3")
        self.assertEqual(status, 200)
        self.assertIn(b"updateCards", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
