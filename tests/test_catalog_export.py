import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CatalogExportTests(unittest.TestCase):
    def test_export_prefers_refreshed_feeds_over_embedded_article_copies(self):
        feeds = (
            (ROOT / "data" / "indian-matrix-latest.json", "Indian Matrix"),
            (ROOT / "data" / "substack-latest.json", "Polity and Policy"),
        )
        expected_articles = []
        for path, publisher in feeds:
            snapshot = json.loads(path.read_text(encoding="utf-8"))
            newest = snapshot["articles"][0]
            expected_articles.append((publisher, newest["link"], newest["title"]))

        output = ROOT / "tests" / ".catalog-export-test.json"
        try:
            subprocess.run(
                ["node", str(ROOT / "scripts" / "export_catalog.mjs"), str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            catalog = json.loads(output.read_text(encoding="utf-8"))
        finally:
            output.unlink(missing_ok=True)

        exported_articles = {
            (item["publisher"], item["url"], item["title"])
            for item in catalog["articles"]
        }
        for expected_article in expected_articles:
            with self.subTest(publisher=expected_article[0]):
                self.assertIn(expected_article, exported_articles)


if __name__ == "__main__":
    unittest.main()