from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.collect_recent_indian_elections import parse_recent_csv, parse_state_names

ROOT = Path(__file__).resolve().parents[1]
TEST_SHA = "a" * 40


class RecentIndianElectionTests(unittest.TestCase):
    def test_parses_2024_lok_sabha_votes_and_keeps_same_numbered_seats_separate(self):
        content = (
            'State;"Constituency";"Party";"Candidate";"Votes";"State ID";"Constituency ID"\n'
            'State A;"Seat One";"Party A";"Candidate A";"600";"S01";"1"\n'
            'State A;"Seat One";"Party B";"Candidate B";"400";"S01";"1"\n'
            'State A;"Seat Two";"Party A";"Candidate A";"100";"S01";"1"\n'
            'State A;"Seat Two";"Party B";"Candidate C";"900";"S01";"1"\n'
        ).encode()
        records = parse_recent_csv(
            content,
            "archive/2024 Parliamentary Elections India.csv",
            TEST_SHA,
            {},
        )
        self.assertEqual(len(records), 4)
        self.assertEqual(
            {row["constituency"]: row["vote_share_percent"] for row in records if row["candidate"] in ("Candidate A", "Candidate C")},
            {"Seat One": 60.0, "Seat Two": 90.0},
        )
        self.assertEqual(records[0]["election_type"], "Lok Sabha")
        self.assertEqual(records[0]["year"], 2024)
        self.assertEqual(records[0]["vote_share_method"], "calculated_from_listed_candidate_votes")
        self.assertIn(TEST_SHA, records[0]["source"])

    def test_parses_assembly_evm_and_postal_votes_with_state_lookup(self):
        state_names = parse_state_names(
            b"state_code,state_name\nTN,Tamil Nadu\n",
            TEST_SHA,
        )
        content = (
            "election_year,election_type,election_state,constituency,constituency_no,"
            "serial_no,candidate,party,evm_votes,postal_votes\n"
            "2026,Assembly,TN,TEST SEAT,1,1,Candidate A,Party A,600,10\n"
            "2026,Assembly,TN,TEST SEAT,1,2,Candidate B,Party B,390,0\n"
            "2026,Assembly,TN,TEST SEAT,1,3,NOTA,None of the Above,0,0\n"
        ).encode()
        records = parse_recent_csv(
            content,
            "data/csv/2026Assembly-TN.csv",
            TEST_SHA,
            state_names,
        )
        self.assertEqual([row["votes"] for row in records], [610, 390, 0])
        self.assertEqual([row["vote_share_percent"] for row in records], [61.0, 39.0, 0.0])
        self.assertEqual(records[0]["state_or_ut"], "Tamil Nadu")
        self.assertEqual(records[0]["election_type"], "State Assembly")

    def test_published_snapshot_covers_all_2024_lok_sabha_seats_and_recent_assemblies(self):
        recent = json.loads(
            (ROOT / "data" / "recent-indian-elections.json").read_text(encoding="utf-8")
        )
        deployed = json.loads(
            (ROOT / "docs" / "data" / "recent-indian-elections.json").read_text(encoding="utf-8")
        )
        self.assertEqual(recent, deployed)
        self.assertEqual(recent["collection_status"], "ok")
        self.assertEqual(recent["lok_sabha_2024_constituency_count"], 543)
        self.assertGreaterEqual(len(recent["source_files"]), 20)
        self.assertEqual(recent["observation_count"], len(recent["observations"]))
        self.assertEqual(recent["assembly_election_years"], [2022, 2023, 2024, 2025, 2026])
        self.assertIn("calculated from the listed candidate vote totals", recent["vote_share_method"].lower())
        self.assertTrue(all(
            recent["source_files"][row["source_file"]]["url"].startswith("https://raw.githubusercontent.com/")
            for row in recent["observations"]
        ))


if __name__ == "__main__":
    unittest.main(verbosity=2)
