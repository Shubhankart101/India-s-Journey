import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_RESOURCES = (
    "chart-latest.json",
    "election-results.json",
    "historical-elections.json",
    "economic-survey-monthly.json",
    "ncrb-and-analyses.json",
    "pew-india-reports.json",
    "pew-snapshots.json",
    "indian-matrix-latest.json",
    "substack-latest.json",
)


class StaticApiTests(unittest.TestCase):
    def test_openapi_get_paths_map_to_deployed_json_files(self):
        spec = json.loads((ROOT / "docs" / "openapi.json").read_text(encoding="utf-8"))
        paths = spec["paths"]
        self.assertEqual(set(paths), {f"/data/{name}" for name in API_RESOURCES})
        for resource in API_RESOURCES:
            self.assertIn("get", paths[f"/data/{resource}"])
            payload = json.loads((ROOT / "data" / resource).read_text(encoding="utf-8"))
            deployed_payload = json.loads((ROOT / "docs" / "data" / resource).read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict)
            self.assertEqual(payload, deployed_payload)

    def test_historical_archive_is_truthfully_labelled_as_partial(self):
        payload = json.loads((ROOT / "data" / "historical-elections.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["collection_status"], "partial")
        self.assertEqual(payload["observation_count"], len(payload["observations"]))
        self.assertGreaterEqual(payload["reports_with_candidate_results"], 1)
        self.assertGreater(payload["catalog_entries_scanned"], payload["reports_with_candidate_results"])
        self.assertTrue(all(row["source"].startswith("https://old.eci.gov.in/") for row in payload["observations"]))

    def test_api_page_exposes_swagger_and_all_resource_checks(self):
        page = (ROOT / "docs" / "api.html").read_text(encoding="utf-8")
        self.assertIn("SwaggerUIBundle", page)
        self.assertIn("Run all endpoint checks", page)
        for resource in API_RESOURCES:
            self.assertIn(resource, page)

    def test_historical_archive_refresh_and_pages_deployment_are_scheduled(self):
        workflow = (ROOT / ".github" / "workflows" / "historical-election-archive-update.yml").read_text(encoding="utf-8")
        deploy = (ROOT / ".github" / "workflows" / "deploy-dashboard.yml").read_text(encoding="utf-8")
        self.assertIn("0 7 1 * *", workflow)
        self.assertIn("python scripts/collect_historical_elections.py", workflow)
        self.assertIn("Historical Election Archive Update", deploy)
        self.assertIn("data/historical-elections.json", deploy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
