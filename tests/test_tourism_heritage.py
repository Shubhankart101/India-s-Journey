import unittest
import json
from unittest.mock import patch
from pathlib import Path

from scripts.generate_public_charts import build_unesco_india_series

ROOT = Path(__file__).resolve().parents[1]


class TourismHeritageTests(unittest.TestCase):
    @patch("scripts.generate_public_charts.time.sleep")
    @patch("scripts.generate_public_charts.get_text")
    def test_builds_cumulative_and_annual_series_from_official_site_pages(self, get_text, _sleep):
        pages = {
            "https://whc.unesco.org/en/list/": """
                <h4><a href="/en/statesparties/in">India</a></h4>
                <ul>
                  <li class="cultural"><a href="/en/list/252">Taj Mahal</a></li>
                  <li class="natural"><a href="/en/list/335">Kaziranga National Park</a></li>
                </ul>
                <h4><a href="/en/statesparties/other">Other country</a></h4>
                <ul><li class="cultural"><a href="/en/list/1">Other property</a></li></ul>
            """,
            "https://whc.unesco.org/en/list/252": "<strong>Date of Inscription:</strong> 1983",
            "https://whc.unesco.org/en/list/335": "<strong>Date of Inscription:</strong> 1985",
        }
        get_text.side_effect = lambda url: pages[url]

        series = build_unesco_india_series()

        cumulative = series["unesco_india_sites_cumulative"]
        annual = series["unesco_india_new_inscriptions"]
        self.assertEqual(cumulative["labels"][:3], ["1983", "1984", "1985"])
        self.assertEqual(cumulative["values"][:3], [1, 1, 2])
        self.assertEqual(annual["values"][:3], [1, 0, 1])
        self.assertIn("current official list", cumulative["note"])
        self.assertEqual(series["unesco_india_current_categories"]["values"], [1, 1, 0])
        self.assertEqual(series["unesco_india_current_categories"]["chartType"], "doughnut")

    def test_published_tourism_series_have_sources_and_dashboard_placements(self):
        payload = json.loads((ROOT / "data" / "chart-latest.json").read_text(encoding="utf-8"))
        definitions = (ROOT / "docs" / "additional-chart-definitions.js").read_text(encoding="utf-8")
        for key in (
            "tourism_arrivals",
            "tourism_departures",
            "tourism_receipts_usd",
            "unesco_india_sites_cumulative",
            "unesco_india_new_inscriptions",
            "unesco_india_current_categories",
        ):
            series = payload["series"][key]
            self.assertTrue(series.get("labels"), key)
            self.assertEqual(len(series["labels"]), len(series["values"]), key)
            self.assertTrue(series.get("source"), key)
            self.assertIn(key, definitions)
        self.assertGreater(payload["series"]["unesco_india_sites_cumulative"]["values"][-1], 0)
        self.assertEqual(payload["series"]["unesco_india_current_categories"]["chartType"], "doughnut")


if __name__ == "__main__":
    unittest.main(verbosity=2)
