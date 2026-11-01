"""Validation for derived groups built from the committed official datasets."""
from __future__ import annotations

import json
import math
import unittest
from collections import Counter
from pathlib import Path

from scripts.derived_groups_layer import NEW_SUBGROUPS, build_derived_groups_layer

ROOT = Path(__file__).resolve().parents[1]
EXISTING_SUBGROUPS = {
    "Pew Research": {"Public opinion"},
    "Elections": {
        "Indian Elections",
        "Lok Sabha 2024 — National",
        "Lok Sabha 2024 — States",
        "State Assembly Results 2022–2026",
        "Election Comparisons Across States",
    },
    "U.S. Elections": {
        "U.S. Presidential Elections",
        "U.S. Presidential Campaign Finance",
        "U.S. Congressional Campaign Finance",
        "U.S. Campaign Funding Composition",
    },
}


class DerivedGroupsLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = build_derived_groups_layer(ROOT)

    def test_each_group_has_two_new_subgroups_with_six_series(self):
        counts = Counter(
            (item["meta"].get("category"), item["meta"].get("subgroup"))
            for item in self.series.values()
        )
        for category, subgroups in NEW_SUBGROUPS.items():
            self.assertGreaterEqual(len(subgroups), 2, category)
            self.assertEqual(len(set(subgroups)), len(subgroups), category)
            for subgroup in subgroups:
                with self.subTest(category=category, subgroup=subgroup):
                    self.assertNotIn(subgroup, EXISTING_SUBGROUPS[category])
                    self.assertGreaterEqual(counts[(category, subgroup)], 6)

    def test_series_shape_and_explanations(self):
        self.assertTrue(self.series)
        for key, item in self.series.items():
            with self.subTest(key=key):
                self.assertTrue(key.startswith("dg_"))
                self.assertIsInstance(item.get("labels"), list)
                self.assertIsInstance(item.get("values"), list)
                self.assertEqual(len(item["labels"]), len(item["values"]))
                self.assertTrue(item["labels"])
                self.assertTrue(all(isinstance(label, str) for label in item["labels"]))
                self.assertTrue(all(isinstance(value, (int, float)) and math.isfinite(value) for value in item["values"]))
                self.assertTrue(item.get("source"))
                self.assertTrue(item.get("unit"))
                self.assertTrue(item.get("note"))
                meta = item.get("meta", {})
                self.assertTrue(meta.get("title"))
                self.assertTrue(meta.get("subtitle"))
                self.assertTrue(meta.get("frequency"))
                self.assertTrue(meta.get("color"))
                self.assertIn("category", meta)
                self.assertIn("subgroup", meta)
                explain = meta.get("explain", {})
                self.assertTrue(all(explain.get(field) for field in ("what", "read", "why")))

    def test_no_collisions_with_committed_chart_keys(self):
        indices = json.loads((ROOT / "data" / "election-indices.json").read_text(encoding="utf-8"))
        latest = json.loads((ROOT / "data" / "chart-latest.json").read_text(encoding="utf-8"))
        index_keys = set(indices.get("series", {}))
        # chart-latest.json already contains this layer's own dg_* output once generated.
        latest_keys = {key for key in latest.get("series", {}) if not key.startswith("dg_")}
        self.assertFalse(set(self.series) & index_keys)
        self.assertFalse(set(self.series) & latest_keys)

    def test_missing_inputs_are_skipped(self):
        self.assertEqual(build_derived_groups_layer(ROOT / "nonexistent-derived-layer-fixture"), {})


if __name__ == "__main__":
    unittest.main()