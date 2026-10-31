from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mospi_layer  # noqa: E402
from mospi_layer import SPECS, build_mospi_layer, build_series, clean_label, is_provisional, relabel_hidden_national  # noqa: E402

EXPLAIN = ("What.", "Read.", "Why.")


def spec(**overrides):
    base = {"key": "test_series", "dataset": "env", "code": 1, "kind": "line", "title": "Test", "subtitle": "Sub",
            "category": "Environment & Climate", "subgroup": "Forests & Land", "explain": EXPLAIN, "suffix": " sq km"}
    base.update(overrides)
    return base


class LabelTests(unittest.TestCase):
    def test_clean_label_strips_markers_and_isfr(self):
        self.assertEqual(clean_label("2022-23 (P)"), "2022-23")
        self.assertEqual(clean_label("2021*"), "2021")
        self.assertEqual(clean_label("ISFR 2023"), "2023")
        self.assertTrue(is_provisional("2023-24 (P)"))
        self.assertFalse(is_provisional("2019"))


class HiddenNationalTests(unittest.TestCase):
    def test_largest_row_is_relabelled_as_all_india(self):
        rows = [{"state": name, "year": "2023", "value": value}
                for name, value in [("A", 10), ("B", 20), ("C", 30), ("D", 40), ("Puducherry", 100)]]
        fixed = relabel_hidden_national(rows, "year")
        self.assertEqual([row["state"] for row in fixed if row["value"] == 100], ["All India"])

    def test_balanced_rows_are_left_alone(self):
        rows = [{"state": name, "year": "2023", "value": 10} for name in "ABCDE"]
        self.assertEqual(relabel_hidden_national(rows, "year"), rows)


class BuildSeriesTests(unittest.TestCase):
    def test_line_prefers_reported_national_row_and_notes_provisional(self):
        rows = [
            {"state": "A", "year": "2020", "value": "1"}, {"state": "B", "year": "2020", "value": "2"},
            {"state": "A", "year": "2021 (P)", "value": "3"}, {"state": "All India", "year": "2021 (P)", "value": "9"},
        ]
        series = build_series(spec(), rows)
        self.assertEqual(series["labels"], ["2020", "2021"])
        self.assertEqual(series["values"], [3, 9])
        self.assertEqual(series["meta"]["explain"], {"what": "What.", "read": "Read.", "why": "Why."})
        self.assertIn("provisional", series["note"])

    def test_state_kind_ranks_latest_period(self):
        rows = [{"state": f"S{i}", "year": year, "value": i * (2 if year == "2022" else 1)}
                for i in range(1, 7) for year in ("2021", "2022")]
        series = build_series(spec(kind="state"), rows)
        self.assertEqual(series["labels"][0], "S6")
        self.assertEqual(series["values"][0], 12)
        self.assertEqual(series["scope"], "state")
        self.assertIn("(2022)", series["meta"]["title"])

    def test_sum_series_totals_complete_periods_only(self):
        rows = [{"state": "All India", "year": year, "month": month, "value": 10}
                for year in ("2019", "2020", "2021") for month in ("Jan", "Feb") if not (year == "2021" and month == "Feb")]
        series = build_series(spec(series="month", members=("Jan", "Feb"), transform="sum_series"), rows)
        self.assertEqual(series["labels"], ["2019", "2020"])
        self.assertEqual(series["values"], [20, 20])

    def test_no_matching_rows_raises(self):
        with self.assertRaises(ValueError):
            build_series(spec(where={"state": "Nowhere"}), [{"state": "A", "year": "2020", "value": 1}])


class LayerTests(unittest.TestCase):
    def test_specs_are_unique_and_fully_explained(self):
        keys = [item["key"] for item in SPECS]
        self.assertEqual(len(keys), len(set(keys)))
        for item in SPECS:
            self.assertEqual(len(item["explain"]), 3, item["key"])
            self.assertTrue(all(part.strip() for part in item["explain"]), item["key"])

    def test_failed_fetch_keeps_previous_series(self):
        previous = {SPECS[0]["key"]: {"labels": ["2020"], "values": [1]}}
        with mock.patch.object(mospi_layer, "fetch_rows", side_effect=OSError("offline")):
            built = build_mospi_layer(previous)
        self.assertEqual(built, previous)


if __name__ == "__main__":
    unittest.main()
