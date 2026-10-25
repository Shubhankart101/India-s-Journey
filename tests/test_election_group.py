import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ElectionGroupTests(unittest.TestCase):
    def test_us_elections_is_a_standalone_group_with_two_subgroups(self):
        page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        definitions = (ROOT / "docs" / "additional-chart-definitions.js").read_text(encoding="utf-8")
        self.assertIn('data-group="U.S. Elections"', page)
        self.assertIn('<option value="U.S. Elections">U.S. Elections</option>', page)
        self.assertIn("<option>U.S. Presidential Elections</option>", page)
        self.assertIn("<option>U.S. Federal Campaign Finance</option>", page)
        self.assertIn("place(['us_presidential_electoral_votes'], 'U.S. Elections'", definitions)
        self.assertIn("office.subgroup,", definitions)
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

    def test_subgroup_filters_are_derived_from_rendered_chart_placements(self):
        app = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        self.assertIn("const groupToSubgroups = { all: [] };", app)
        self.assertIn("const group = card.dataset.category;", app)
        self.assertIn("const subgroup = card.dataset.subgroup;", app)
        self.assertIn("groupToSubgroups[group].push(subgroup);", app)
        self.assertIn(".filter(([, groups]) => groups.size === 1)", app)


if __name__ == "__main__":
    unittest.main(verbosity=2)
