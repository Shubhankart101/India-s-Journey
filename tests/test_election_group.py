import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ElectionGroupTests(unittest.TestCase):
    def test_us_elections_separates_results_from_presidential_and_congressional_finance(self):
        page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        definitions = (ROOT / "docs" / "additional-chart-definitions.js").read_text(encoding="utf-8")
        self.assertIn('data-group="U.S. Elections"', page)
        self.assertIn('<option value="U.S. Elections">U.S. Elections</option>', page)
        self.assertIn("<option>U.S. Presidential Elections</option>", page)
        self.assertIn("<option>U.S. Presidential Campaign Finance</option>", page)
        self.assertIn("<option>U.S. Congressional Campaign Finance</option>", page)
        self.assertIn("place(['us_presidential_electoral_votes'], 'U.S. Elections'", definitions)
        self.assertIn("subgroup: 'U.S. Presidential Campaign Finance'", definitions)
        self.assertIn("subgroup: 'U.S. Congressional Campaign Finance'", definitions)
        self.assertIn("U.S. Congressional Campaign Finance", app)
        self.assertIn("const groupToSubgroups = { all: [] };", app)

    def test_new_world_bank_indicators_have_values_and_correct_placements(self):
        payload = json.loads((ROOT / "data" / "chart-latest.json").read_text(encoding="utf-8"))
        definitions = (ROOT / "docs" / "additional-chart-definitions.js").read_text(encoding="utf-8")
        keys = (
            "agricultural_employment_share",
            "urban_population_growth",
            "net_energy_imports_share",
            "lower_secondary_completion",
            "government_health_spending_per_capita",
            "safely_managed_drinking_water",
        )
        for key in keys:
            series = payload["series"][key]
            self.assertGreater(len(series["labels"]), 10, key)
            self.assertEqual(len(series["labels"]), len(series["values"]), key)
            self.assertIn("World Bank API", series["source"], key)
            self.assertIn(key, definitions)

    def test_us_campaign_finance_series_are_complete_and_separate_from_results(self):
        payload = json.loads((ROOT / "data" / "us-campaign-finance.json").read_text(encoding="utf-8"))
        app = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        definitions = (ROOT / "docs" / "additional-chart-definitions.js").read_text(encoding="utf-8")
        series = payload["series"]
        self.assertEqual(len(series), 52)
        for key, item in series.items():
            with self.subTest(series=key):
                self.assertEqual(len(item["labels"]), len(item["values"]))
                self.assertTrue(item["values"])
        for cycle in (2018, 2020, 2022, 2024):
            key = f"us_fec_{cycle}_p_receipt_composition"
            self.assertEqual(series[key]["chartType"], "doughnut")
            self.assertGreater(sum(series[key]["values"]), 0)
        self.assertIn("U.S. Congressional Campaign Finance", app)
        self.assertIn("U.S. Presidential Campaign Finance", app)
        self.assertIn("U.S. Congressional Campaign Finance", definitions)
        self.assertIn("U.S. Presidential Campaign Finance", definitions)
        self.assertIn("U.S. Presidential Elections", definitions)

    def test_part_of_whole_chart_definitions_have_matching_data(self):
        payload = json.loads((ROOT / "data" / "chart-latest.json").read_text(encoding="utf-8"))
        election = json.loads((ROOT / "data" / "election-results.json").read_text(encoding="utf-8"))
        expected = (
            "gdp_sector_composition",
            "state_gsdp_composition",
            "urban_rural_population_composition",
            "energy_supply_composition",
            "disease_burden_composition",
            "defence_budget_composition",
            "card_spending_composition",
        )
        for key in expected:
            with self.subTest(chart=key):
                item = payload["series"][key]
                self.assertEqual(item["chartType"], "doughnut")
                self.assertEqual(len(item["labels"]), len(item["values"]))
                if key == "card_spending_composition":
                    self.assertGreater(sum(item["values"]), 0)
                else:
                    self.assertAlmostEqual(sum(item["values"]), 100, places=1)
        self.assertEqual(
            election["series"]["india_live_party_seats_composition"]["chartType"],
            "doughnut",
        )
        for index in range(1, len(election["india_constituencies"]) + 1):
            pie = election["series"][f"india_live_constituency_vote_composition_{index}"]
            self.assertEqual(pie["chartType"], "doughnut")
            self.assertEqual(len(pie["labels"]), len(pie["values"]))
        for year in range(2000, 2025, 4):
            pie = election["series"][f"us_presidential_electoral_composition_{year}"]
            self.assertEqual(sum(pie["values"]), 538)

    def test_subgroup_filters_are_derived_from_rendered_chart_placements(self):
        app = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        self.assertIn("const groupToSubgroups = { all: [] };", app)
        self.assertIn("const group = card.dataset.category;", app)
        self.assertIn("const subgroup = card.dataset.subgroup;", app)
        self.assertIn("groupToSubgroups[group].push(subgroup);", app)
        self.assertIn(".filter(([, groups]) => groups.size === 1)", app)


if __name__ == "__main__":
    unittest.main(verbosity=2)
