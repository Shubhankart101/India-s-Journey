from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rbi_state_layer import (  # noqa: E402
    ALL_INDIA,
    STATES,
    STATES_AND_UTS,
    UNION_TERRITORIES,
    canonical_state,
    coverage_note,
    parse_rbi_table,
)


class CanonicalStateTests(unittest.TestCase):
    def test_official_spellings_map_to_one_name(self):
        cases = {
            "Jammu And Kashmir": "Jammu & Kashmir",
            "Andaman and Nicobar Islands": "Andaman & Nicobar Islands",
            "The Dadra And Nagar Haveli And Daman And Diu": "Dadra & Nagar Haveli and Daman & Diu",
            "1 Andhra Pradesh": "Andhra Pradesh",
            "Total": ALL_INDIA,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(canonical_state(raw), expected)

    def test_non_states_are_ignored(self):
        self.assertIsNone(canonical_state("Mumbai"))
        self.assertIsNone(canonical_state(""))

    def test_registry_covers_28_states_and_8_uts(self):
        self.assertEqual((len(STATES), len(UNION_TERRITORIES), len(STATES_AND_UTS)), (28, 8, 36))
        for name in STATES_AND_UTS:
            self.assertEqual(canonical_state(name), name)

    def test_coverage_note_lists_missing_entities(self):
        note = coverage_note([name for name in STATES_AND_UTS if name != "Ladakh"])
        self.assertIn("35 of 36", note)
        self.assertIn("Ladakh", note)


class ParseRbiTableTests(unittest.TestCase):
    def test_year_columns_include_union_territories(self):
        rows = [
            ["State/Union Territory", "2021-22", "2022-23"],
            ["1", "2", "3"],
            ["Kerala", "10", "12"],
            ["Ladakh", "1.5", "2"],
            ["Delhi", "-", "7"],
            ["All India", "100", "120"],
        ]
        columns = parse_rbi_table(rows)
        self.assertEqual(columns["2022-23"]["Ladakh"], 2)
        self.assertEqual(columns["2022-23"]["Delhi"], 7)
        self.assertNotIn("Delhi", columns["2021-22"])
        self.assertEqual(columns["2022-23"][ALL_INDIA], 120)


class GeneratedStateCoverageTests(unittest.TestCase):
    def test_state_charts_include_union_territories(self):
        series = json.loads((ROOT / "docs" / "data" / "chart-latest.json").read_text(encoding="utf-8"))["series"]
        rbi_keys = [key for key in series if key.startswith("rbi_state_")]
        self.assertGreaterEqual(len(rbi_keys), 100)
        for key in ("state_gsdp_comparison", "state_per_capita_income", "state_infant_mortality_rate"):
            with self.subTest(key=key):
                labels = set(series[key]["labels"])
                self.assertTrue(set(STATES) <= labels)
                self.assertTrue(labels & set(UNION_TERRITORIES))
                self.assertIn("of 36 States/UTs reported", series[key]["note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
