import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.collect_election_results import (
    _series_from_results,
    _without_total_rows,
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
          <tr><td></td><td>Total</td><td></td><td></td><td></td><td>1,815</td><td></td></tr>
        </table>
        """
        result = parse_constituency_results(
            html,
            "https://results.eci.gov.in/ResultAc/ConstituencywiseS2235.htm",
            "State Assembly by-election",
        )
        self.assertEqual(result["constituency"], "MADURANTAKAM")
        self.assertEqual(result["state_or_ut"], "Tamil Nadu")
        self.assertEqual(len(result["candidates"]), 2)
        self.assertNotIn("Total", [candidate["candidate"] for candidate in result["candidates"]])
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
            "source": "https://results.eci.gov.in/test",
            "candidates": [
                {"candidate": "Total", "party": "", "votes": 1815, "vote_share_percent": None},
                {"candidate": "Candidate A", "party": "Party A", "votes": 1010, "vote_share_percent": 55.25},
                {"candidate": "Candidate B", "party": "Party B", "votes": 805, "vote_share_percent": 44.35},
            ],
        }]
        presidential = [{
            "year": 2024,
            "winner": "Candidate A",
            "main_opponent": "Candidate B",
            "winner_electoral_votes": 312,
            "opponent_electoral_votes": 226,
        }]
        series = _series_from_results(records, presidential)
        self.assertEqual(series["india_live_candidate_votes"]["values"], [1010, 805])
        self.assertEqual(series["india_live_winner_vote_share"]["values"], [55.25])
        self.assertEqual(series["india_live_party_seats"]["labels"], ["Party A"])
        self.assertEqual(series["india_live_party_seats"]["values"], [1])
        self.assertEqual(series["india_live_party_seats_composition"]["chartType"], "doughnut")
        self.assertNotIn("Total", series["india_live_candidate_votes"]["labels"][0])
        self.assertIn("india_live_candidate_vote_share", series)
        self.assertIn("india_live_constituency_margin", series)
        self.assertIn("india_live_party_seats", series)
        self.assertIn("Form 20", series["india_live_candidate_votes"]["note"])
        self.assertIn("not popular votes", series["us_presidential_electoral_votes"]["note"])
        constituency_pies = [
            value for key, value in series.items()
            if key.startswith("india_live_constituency_vote_composition_")
        ]
        self.assertEqual(len(constituency_pies), 1)
        self.assertEqual(sum(constituency_pies[0]["values"]), 1815)
        self.assertEqual(constituency_pies[0]["chartType"], "doughnut")

    def test_cached_eci_totals_are_removed_and_candidates_ranked(self):
        records = [{
            "state_or_ut": "State",
            "constituency": "Seat",
            "candidates": [
                {"candidate": "Total", "party": "", "votes": 1000, "vote_share_percent": None},
                {"candidate": "Runner-up", "party": "Party B", "votes": 400, "vote_share_percent": 40},
                {"candidate": "Winner", "party": "Party A", "votes": 600, "vote_share_percent": 60},
            ],
        }]
        cleaned = _without_total_rows(records)
        self.assertEqual([candidate["candidate"] for candidate in cleaned[0]["candidates"]], ["Winner", "Runner-up"])

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
        self.assertIn("india_live_constituency_vote_composition_${index + 1}", app)
        self.assertIn(
            "extraChartPlacement[key] = { category: 'Elections', subgroup: 'Indian Elections' }",
            app,
        )
        self.assertGreaterEqual(len(payload["india_constituencies"]), 1)
        self.assertEqual(len(payload["us_presidential_elections"]), 7)
        self.assertEqual(payload, deployed_payload)
        for record in payload["india_constituencies"]:
            self.assertNotIn("Total", [candidate["candidate"] for candidate in record["candidates"]])
        winner_shares = payload["series"]["india_live_winner_vote_share"]["values"]
        self.assertTrue(winner_shares)
        self.assertTrue(all(value is not None for value in winner_shares))
        party_leads = payload["series"]["india_live_party_seats"]
        self.assertNotIn("Unspecified", party_leads["labels"])
        self.assertEqual(sum(party_leads["values"]), len(payload["india_constituencies"]))
        electoral_votes = payload["series"]["us_presidential_electoral_votes"]
        self.assertEqual(len(electoral_votes["labels"]), 7)
        self.assertTrue(all(len(dataset["values"]) == 7 for dataset in electoral_votes["datasets"]))
        for year in range(2000, 2025, 4):
            composition = payload["series"][f"us_presidential_electoral_composition_{year}"]
            self.assertEqual(sum(composition["values"]), 538)
            self.assertEqual(composition["chartType"], "doughnut")
        for file_name in ("README.md", "ELECTIONS.md", "SOURCES-AND-LIMITATIONS.md", "PIPELINES.md"):
            self.assertTrue((root / "docs" / file_name).is_file() or (root / file_name).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
