import unittest

from scripts.innovation_layer import CATEGORY, PEERS, SUBGROUPS, build_innovation_layer


def fake_get_json(url: str):
    code = url.split("/indicator/")[1].split("?")[0]
    seed = sum(map(ord, code)) % 7 + 1
    rows = []
    for index, iso in enumerate(PEERS):
        for year in range(1995, 2024):
            rows.append({"countryiso3code": iso, "date": str(year),
                         "value": (index + 2) * seed * (1 + 0.05 * (year - 1995)) * 10})
    return [{"page": 1}, rows]


def failing_get_json(url: str):
    raise OSError("network down")


class InnovationLayerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = build_innovation_layer(fake_get_json, {})

    def test_volume_and_subgroups(self):
        self.assertGreaterEqual(len(self.series), 110)
        for name in SUBGROUPS:
            count = sum(1 for s in self.series.values() if s["meta"]["subgroup"] == name)
            self.assertGreaterEqual(count, 8, name)

    def test_shape(self):
        for key, item in self.series.items():
            self.assertTrue(key.startswith("innov_"))
            meta = item["meta"]
            self.assertEqual(meta["category"], CATEGORY)
            self.assertIn(meta["subgroup"], SUBGROUPS)
            self.assertEqual(set(meta["explain"]), {"what", "read", "why"})
            self.assertTrue(all(meta["explain"].values()))
            if "datasets" in item:
                for dataset in item["datasets"]:
                    self.assertEqual(len(dataset["values"]), len(item["labels"]), key)
            else:
                self.assertEqual(len(item["values"]), len(item["labels"]), key)

    def test_previous_retained_on_failure(self):
        previous = {"innov_pat_res_trend": {"labels": ["2020"], "values": [1.0], "meta": {}}}
        result = build_innovation_layer(failing_get_json, previous)
        self.assertEqual(result, previous)


if __name__ == "__main__":
    unittest.main()
