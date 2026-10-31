from __future__ import annotations

import unittest

from scripts.generate_public_charts import build_composition_series


class CompositionChartTests(unittest.TestCase):
    def test_builds_only_valid_parts_of_whole_snapshots(self):
        states = [f"State {index}" for index in range(28)]
        state_values = [10.0] * 8 + [1.0] * 20
        series = {
            "agriculture_gdp_share": {"labels": ["2024"], "values": [20], "source": "WB agriculture"},
            "industry_gdp_share": {"labels": ["2024"], "values": [30], "source": "WB industry"},
            "services_gdp_share": {"labels": ["2024"], "values": [40], "source": "WB services"},
            "state_gsdp_share": {"labels": states, "values": state_values, "source": "RBI state shares"},
            "urban_population_share": {"labels": ["2023", "2024"], "values": [35, 36], "source": "WB urban"},
            "net_energy_imports_share": {"labels": ["2024"], "values": [40], "source": "WB energy"},
            "defence_budget_share": {"labels": ["2024"], "values": [13], "source": "Union Budget"},
            "credit_card_spends": {"labels": ["2023", "2024"], "values": [12, 15], "source": "RBI credit"},
            "debit_card_spends": {"labels": ["2023", "2024"], "values": [8, 5], "source": "RBI debit"},
        }

        charts = build_composition_series(series)

        self.assertEqual(set(charts), {
            "gdp_sector_composition",
            "state_gsdp_composition",
            "urban_rural_population_composition",
            "energy_supply_composition",
            "defence_budget_composition",
            "card_spending_composition",
        })
        for key, chart in charts.items():
            with self.subTest(chart=key):
                self.assertEqual(chart["chartType"], "doughnut")
                self.assertEqual(len(chart["labels"]), len(chart["values"]))
                self.assertTrue(all(value >= 0 for value in chart["values"]))
        self.assertEqual(sum(charts["gdp_sector_composition"]["values"]), 100)
        self.assertEqual(sum(charts["state_gsdp_composition"]["values"]), 100)
        self.assertEqual(charts["urban_rural_population_composition"]["labels"], ["Urban population", "Rural population"])
        self.assertIn("2024", charts["card_spending_composition"]["note"])

    def test_does_not_create_state_share_pie_for_incomplete_coverage(self):
        charts = build_composition_series({
            "state_gsdp_share": {
                "labels": ["State A", "State B"],
                "values": [60, 30],
            }
        })
        self.assertNotIn("state_gsdp_composition", charts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
