from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ElectionIndicesTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((ROOT / "data" / "election-indices.json").read_text(encoding="utf-8"))

    def test_published_mirror_matches(self):
        deployed = json.loads((ROOT / "docs" / "data" / "election-indices.json").read_text(encoding="utf-8"))
        self.assertEqual(self.payload, deployed)

    def test_every_index_is_a_self_described_sourced_pie(self):
        series = self.payload["series"]
        self.assertGreaterEqual(len(series), 100)
        for key, item in series.items():
            with self.subTest(index=key):
                if item["meta"]["subgroup"] == "Election Comparisons Across States" and item["chartType"] == "bar":
                    self.assertEqual(item["scope"], "state")
                else:
                    self.assertEqual(item["chartType"], "doughnut")
                self.assertEqual(len(item["labels"]), len(item["values"]))
                self.assertGreaterEqual(len(item["labels"]), 1)
                self.assertGreater(sum(item["values"]), 0)
                self.assertTrue(all(value >= 0 for value in item["values"]))
                self.assertEqual(item["meta"]["category"], "Elections")
                self.assertTrue(item["meta"]["title"] and item["meta"]["subgroup"])
                self.assertTrue(item["source"].startswith("https://"))

    def test_lok_sabha_2024_seat_pie_matches_official_result(self):
        seats = self.payload["series"]["india_ls2024_party_seats"]
        tally = dict(zip(seats["labels"], seats["values"]))
        self.assertEqual(sum(seats["values"]), 543)
        self.assertEqual(tally["Bharatiya Janata Party"], 240)
        self.assertEqual(tally["Indian National Congress"], 99)
        self.assertEqual(tally["Samajwadi Party"], 37)

    def test_cross_state_comparisons_cover_every_contesting_state(self):
        series = self.payload["series"]
        self.assertGreaterEqual(len(series), 200)
        close = series["india_ls2024_state_close_contests"]
        self.assertEqual(len(close["labels"]), 36)
        self.assertTrue(all(0 <= value <= 100 for value in close["values"]))
        self.assertEqual(sum(series["india_assembly_latest_largest_party_states"]["values"]),
                         len(series["india_assembly_state_nota_share"]["labels"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
