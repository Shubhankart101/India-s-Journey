import math
import unittest
from pathlib import Path

from scripts.legal_layer import CATEGORY, SUBGROUPS, build_legal_layer


class LegalLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = build_legal_layer(Path(__file__).resolve().parents[1])

    def test_subgroups_have_at_least_150_series(self):
        counts = {name: 0 for name in SUBGROUPS.values()}
        for item in self.series.values():
            meta = item.get("meta", {})
            if meta.get("subgroup") in counts:
                counts[meta["subgroup"]] += 1
        for subgroup, count in counts.items():
            with self.subTest(subgroup=subgroup):
                self.assertGreaterEqual(count, 150)

    def test_series_are_unique_prefixed_and_complete(self):
        self.assertTrue(self.series)
        self.assertEqual(len(self.series), len(set(self.series)))
        for key, item in self.series.items():
            with self.subTest(key=key):
                self.assertTrue(key.startswith("jud_"))
                self.assertTrue(item.get("labels"))
                self.assertTrue(all(str(label).strip() for label in item["labels"]))
                values = item.get("values")
                datasets = item.get("datasets")
                self.assertTrue(values or datasets)
                numeric_values = values if values is not None else [
                    value for dataset in datasets for value in dataset.get("values", [])
                ]
                self.assertTrue(numeric_values)
                self.assertTrue(all(
                    isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                    for value in numeric_values
                ))
                meta = item.get("meta", {})
                self.assertEqual(meta.get("category"), CATEGORY)
                self.assertIn(meta.get("subgroup"), SUBGROUPS.values())
                explain = meta.get("explain", {})
                self.assertTrue(all(explain.get(part, "").strip() for part in ("what", "read", "why")))
                self.assertIn("njdg", item.get("source", "").lower())


if __name__ == "__main__":
    unittest.main()
