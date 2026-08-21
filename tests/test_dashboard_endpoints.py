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
        self.assertIn(b"India, In Signals", body)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
