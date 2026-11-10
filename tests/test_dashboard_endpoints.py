import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StaticReactDashboardTests(unittest.TestCase):
    def test_static_entrypoint_loads_relative_react_chunks(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn('src="./build/', html)
        self.assertIn('href="./build/', html)
        self.assertTrue((ROOT / "docs" / "build").is_dir())

    def test_api_snapshots_cover_core_app_requests(self):
        api = ROOT / "docs" / "api"
        stats = json.loads((api / "stats.json").read_text(encoding="utf-8"))
        indicators = json.loads((api / "indicators.json").read_text(encoding="utf-8"))
        categories = json.loads((api / "categories.json").read_text(encoding="utf-8"))
        articles = json.loads((api / "articles.json").read_text(encoding="utf-8"))
        self.assertEqual(len(indicators), stats["indicators"])
        self.assertEqual(len(categories), stats["categories"])
        self.assertEqual(len(articles), stats["articles"])
        self.assertTrue(all("series" in row for row in indicators))

    def test_old_html_routes_redirect_into_the_hash_router(self):
        redirect = (ROOT / "docs" / "legacy-redirect.js").read_text(encoding="utf-8")
        for page in ("explore", "indicator", "compare", "sources", "about"):
            self.assertIn("legacy-redirect.js", (ROOT / "docs" / f"{page}.html").read_text(encoding="utf-8"))
        self.assertIn("#/explore", redirect)
        self.assertIn("#/indicator/", redirect)
        self.assertIn("#/compare", redirect)


if __name__ == "__main__":
    unittest.main()
