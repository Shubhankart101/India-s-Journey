import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "docs" / "api"


class StaticApiTests(unittest.TestCase):
    def test_build_exports_the_api_snapshots_consumed_by_react(self):
        expected = {"categories", "indicators", "articles", "search-index", "stats", "legacy-aliases"}
        self.assertTrue(all((API / f"{name}.json").is_file() for name in expected))
        stats = json.loads((API / "stats.json").read_text(encoding="utf-8"))
        indicators = json.loads((API / "indicators.json").read_text(encoding="utf-8"))
        articles = json.loads((API / "articles.json").read_text(encoding="utf-8"))
        search = json.loads((API / "search-index.json").read_text(encoding="utf-8"))
        self.assertEqual(len(indicators), stats["indicators"])
        self.assertEqual(len(articles), stats["articles"])
        self.assertEqual(len(search), len(indicators))
        self.assertTrue(any(item["key"] == "gdp_growth" for item in indicators))
        categories = json.loads((API / "categories.json").read_text(encoding="utf-8"))
        self.assertIsInstance(categories[0]["badges"], list)
        self.assertEqual(stats["last_refresh"], stats["source_generated_at"].replace("+00:00", "Z"))
        self.assertTrue({"title", "url", "published", "published_at", "publisher", "kind", "is_featured"} <= articles[0].keys())

    def test_legacy_pages_are_small_redirect_stubs_and_keep_aliases(self):
        for page in ("explore", "indicator", "compare", "sources", "about"):
            html = (ROOT / "docs" / f"{page}.html").read_text(encoding="utf-8")
            self.assertIn("legacy-redirect.js", html)
            self.assertLess(len(html), 600)
        aliases = json.loads((API / "legacy-aliases.json").read_text(encoding="utf-8"))
        self.assertEqual(aliases["groups"]["Economic"]["group"], "Economy & Markets")
        self.assertIn("category", (ROOT / "docs" / "legacy-redirect.js").read_text(encoding="utf-8"))

    def test_historical_archive_is_truthfully_labelled_as_partial(self):
        payload = json.loads((ROOT / "data" / "historical-elections.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["collection_status"], "partial")
        self.assertEqual(payload["observation_count"], len(payload["observations"]))
        self.assertGreaterEqual(payload["reports_with_candidate_results"], 1)

    def test_historical_archive_refresh_and_pages_deployment_are_scheduled(self):
        workflow = (ROOT / ".github" / "workflows" / "historical-election-archive-update.yml").read_text(encoding="utf-8")
        deploy = (ROOT / ".github" / "workflows" / "deploy-dashboard.yml").read_text(encoding="utf-8")
        self.assertIn("0 7 1 * *", workflow)
        self.assertIn("python scripts/collect_historical_elections.py", workflow)
        self.assertIn("Historical Election Archive Update", deploy)
        self.assertIn("data/historical-elections.json", deploy)

    def test_recent_indian_election_refresh_is_scheduled_and_deployed(self):
        workflow = (ROOT / ".github" / "workflows" / "recent-indian-elections-update.yml").read_text(encoding="utf-8")
        deploy = (ROOT / ".github" / "workflows" / "deploy-dashboard.yml").read_text(encoding="utf-8")
        self.assertIn("schedule:", workflow)
        self.assertIn("python scripts/collect_recent_indian_elections.py", workflow)
        self.assertIn("Recent Indian Election Data Update", deploy)
        self.assertIn("data/recent-indian-elections.json", deploy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
