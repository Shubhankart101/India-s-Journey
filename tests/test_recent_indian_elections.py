from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from scripts.collect_recent_indian_elections import (
    ECI_LS2024_RESULTS_URL,
    parse_lok_sabha_2024_rows,
    parse_recent_csv,
    parse_state_names,
)

ROOT = Path(__file__).resolve().parents[1]
TEST_SHA = "a" * 40
OFFICIAL_LS2024_SEATS = {
    "Bharatiya Janata Party": 240,
    "Indian National Congress": 99,
    "Samajwadi Party": 37,
    "All India Trinamool Congress": 29,
    "Dravida Munnetra Kazhagam": 22,
    "Telugu Desam": 16,
    "Janata Dal (United)": 12,
    "Independent": 7,
}


def _row(state, seat, candidate, party, votes):
    return [state, seat, candidate, "", "", "", party, "", 0, 0, votes, 0, votes]


class RecentIndianElectionTests(unittest.TestCase):
    def test_parses_eci_lok_sabha_rows_keeps_namesakes_and_adds_surat(self):
        rows = [
            _row("State A", "Seat One", "Candidate A", "BJP", 600),
            _row("State A", "Seat One", "Candidate A", "IND", 50),
            _row("State A", "Seat One", "Candidate B", "INC", 350),
            ["Footnote"],
        ]
        records = parse_lok_sabha_2024_rows(rows, {"BJP": "Bharatiya Janata Party", "IND": "Independent"})
        seat = [row for row in records if row["constituency"] == "Seat One"]
        self.assertEqual([row["votes"] for row in seat], [600, 50, 350])
        self.assertEqual(seat[0]["party"], "Bharatiya Janata Party")
        self.assertEqual(seat[0]["vote_share_percent"], 60.0)
        self.assertEqual(seat[0]["source"], ECI_LS2024_RESULTS_URL)
        surat = [row for row in records if row["constituency"] == "Surat"]
        self.assertEqual(len(surat), 1)
        self.assertEqual(surat[0]["result_status"], "uncontested")
        self.assertIsNone(surat[0]["votes"])

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
            recent["source_files"][row["source_file"]]["url"].startswith(
                "https://raw.githubusercontent.com/" if row["election_type"] == "State Assembly"
                else "https://www.eci.gov.in/"
            )
            for row in recent["observations"]
        ))

    def test_published_lok_sabha_2024_winners_match_official_party_tally(self):
        recent = json.loads((ROOT / "data" / "recent-indian-elections.json").read_text(encoding="utf-8"))
        seats = {}
        for row in recent["observations"]:
            if row["election_type"] == "Lok Sabha":
                seats.setdefault((row["state_or_ut"], row["constituency"]), []).append(row)
        winners = Counter(max(rows, key=lambda row: row["votes"] or 0)["party"] for rows in seats.values())
        self.assertEqual(len(seats), 543)
        self.assertEqual({party: winners[party] for party in OFFICIAL_LS2024_SEATS}, OFFICIAL_LS2024_SEATS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
