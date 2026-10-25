import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.collect_election_results import (
    _series_from_results,
    collect_us_presidential_results,
    parse_constituency_results,
)


class ElectionResultsTests(unittest.TestCase):
    def test_parses_constituency_candidate_votes_and_source(self):
        html = """
        <h2>Assembly Constituency <span>35 - MADURANTAKAM
        <strong> (Tamil Nadu)</strong></span></h2>
        <table>
          <tr><th>S.N.</th><th>Candidate</th><th>Party</th><th>EVM Votes</th>
          <th>Postal Votes</th><th>Total Votes</th><th>% of Votes</th></tr>
          <tr><td>1</td><td>Candidate A</td><td>Party A</td><td>1,000</td>
          <td>10</td><td>1,010</td><td>55.25</td></tr>
          <tr><td>2</td><td>Candidate B</td><td>Party B</td><td>800</td>
          <td>5</td><td>805</td><td>44.75</td></tr>
        </table>
        """
        result = parse_constituency_results(
            html,
            "https://results.eci.gov.in/ResultAc/ConstituencywiseS2235.htm",
            "State Assembly by-election",
        )
        self.assertEqual(result["constituency"], "MADURANTAKAM")
        self.assertEqual(result["state_or_ut"], "Tamil Nadu")
        self.assertEqual(result["candidates"][0]["votes"], 1010)
        self.assertEqual(result["candidates"][0]["vote_share_percent"], 55.25)
        self.assertIn("ConstituencywiseS2235.htm", result["source"])

    def test_missing_eci_results_table_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "table was not found"):
            parse_constituency_results("<html>No result data</html>", "https://example.test", "Assembly")

    def test_parses_parliamentary_constituency_heading(self):
        html = """
        <h2>Parliamentary Constituency <span>9 - Nagaon<strong> (Assam)</strong></span></h2>
        <table><tr><th>Candidate</th><th>Party</th><th>Total Votes</th><th>% of Votes</th></tr>
        <tr><td>Candidate A</td><td>Party A</td><td>900</td><td>60</td></tr></table>
        """
        result = parse_constituency_results(
            html,
            "https://results.eci.gov.in/ResultPc/ConstituencywiseS039.htm",
            "Lok Sabha by-election",
        )
        self.assertEqual(result["constituency"], "Nagaon")
        self.assertEqual(result["state_or_ut"], "Assam")

    def test_us_archives_parser_extracts_all_presidential_cycles(self):
        def fake_fetch(url):
            year = int(re.search(r"/(\d{4})$", url).group(1))
            return f"""
            <table>
              <tr><th>President</th><td>Winner {year}</td></tr>
              <tr><th>Main Opponent</th><td>Opponent {year}</td></tr>
              <tr><th>Electoral Vote</th><td>Winner: 300</td>
              <td>Main Opponent: 238</td><td>Total/Majority: 538/270</td></tr>
            </table>
            """

        with patch("scripts.collect_election_results.fetch_text", side_effect=fake_fetch):
            results = collect_us_presidential_results()
        self.assertEqual([item["year"] for item in results], list(range(2000, 2025, 4)))
        self.assertEqual(results[-1]["winner_electoral_votes"], 300)

    def test_generated_series_preserves_scope_and_caveats(self):
        records = [{
            "state_or_ut": "Tamil Nadu",
            "constituency": "MADURANTAKAM",
            "candidates": [{"candidate": "Candidate A", "party": "Party A", "votes": 1010, "vote_share_percent": 55.25}],
        }]
        presidential = [{
            "year": 2024,
            "winner_electoral_votes": 312,
            "opponent_electoral_votes": 226,
        }]
        series = _series_from_results(records, presidential)
        self.assertEqual(series["india_live_candidate_votes"]["values"], [1010])
        self.assertIn("india_live_candidate_vote_share", series)
        self.assertIn("india_live_constituency_margin", series)
        self.assertIn("india_live_party_seats", series)
        self.assertIn("Form 20", series["india_live_candidate_votes"]["note"])
        self.assertIn("not popular votes", series["us_presidential_electoral_votes"]["note"])

    def test_workflow_deploy_and_documentation_cover_election_data(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "election-results-update.yml").read_text(encoding="utf-8")
        deploy = (root / ".github" / "workflows" / "deploy-dashboard.yml").read_text(encoding="utf-8")
        app = (root / "docs" / "app.js").read_text(encoding="utf-8")
        data_file = root / "data" / "election-results.json"
        payload = json.loads(data_file.read_text(encoding="utf-8"))
        deployed_payload = json.loads((root / "docs" / "data" / "election-results.json").read_text(encoding="utf-8"))
        self.assertIn("0 */3 * * *", workflow)
        self.assertIn("scripts/collect_election_results.py", workflow)
        self.assertIn("data/election-results.json", deploy)
        self.assertIn("safeFetchJson('election-results.json'", app)
        self.assertGreaterEqual(len(payload["india_constituencies"]), 1)
        self.assertEqual(len(payload["us_presidential_elections"]), 7)
        self.assertEqual(payload, deployed_payload)
        for file_name in ("README.md", "ELECTIONS.md", "SOURCES-AND-LIMITATIONS.md", "PIPELINES.md"):
            self.assertTrue((root / "docs" / file_name).is_file() or (root / file_name).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
