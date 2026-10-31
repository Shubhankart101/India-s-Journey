from __future__ import annotations

import io
import json
import unittest
import zipfile
from pathlib import Path

from scripts.collect_us_campaign_finance import (
    COMPOSITION_SPECS,
    MEASURES,
    _candidate_summary_rows,
    build_composition_series,
    build_cycle_series,
    build_receipt_composition_series,
    series_key,
)


def candidate_row(
    candidate_id: str,
    party: str,
    state: str,
    receipts: float,
    disbursements: float,
    cash_on_hand: float,
    debts_owed: float,
) -> list[str]:
    row = [""] * 30
    row[0] = candidate_id
    row[1] = "Test Candidate"
    row[4] = party
    row[5] = str(receipts)
    row[7] = str(disbursements)
    row[10] = str(cash_on_hand)
    row[16] = str(debts_owed)
    row[18] = state
    return row


class UsCampaignFinanceTests(unittest.TestCase):
    def test_parses_official_pipe_delimited_candidate_summary_zip(self):
        row = candidate_row("H0CA00001", "DEM", "CA", 100, 70, 30, 5)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("weball24.txt", "|".join(row) + "\n")

        parsed = _candidate_summary_rows(stream.getvalue(), 2024)

        self.assertEqual(parsed, [row])

    def test_aggregates_house_by_office_state_and_president_by_party(self):
        rows = [
            candidate_row("H0CA00001", "DEM", "CA", 100, 70, 30, 5),
            candidate_row("H0CA00002", "REP", "CA", 40, 25, 15, 3),
            candidate_row("S0CA00001", "DEM", "CA", 50, 35, 15, 2),
            candidate_row("P00000001", "DEM", "CA", 200, 150, 50, 10),
            candidate_row("P00000002", "DEM", "NY", 300, 250, 50, 20),
        ]

        series = build_cycle_series(2024, rows)

        house = series[series_key(2024, "H", "receipts")]
        president = series[series_key(2024, "P", "receipts")]
        self.assertEqual(house["labels"], ["CA"])
        self.assertEqual(house["values"], [140])
        self.assertEqual(house["scope"], "state")
        self.assertEqual(president["labels"], ["DEM"])
        self.assertEqual(president["values"], [500])
        self.assertEqual(president["scope"], "category")
        self.assertEqual(len(series), len(MEASURES) * 3)
        self.assertTrue(president["source"].endswith("/2024/weball24.zip"))
        composition = build_receipt_composition_series(2024, series)[
            series_key(2024, "P", "receipt_composition")
        ]
        self.assertEqual(composition["chartType"], "doughnut")
        self.assertEqual(composition["values"], president["values"])

    def test_builds_party_incumbency_and_funding_source_pies(self):
        rows = []
        for candidate_id, party, status, receipts, individual in (
            ("H0CA00001", "DEM", "I", 100, 60), ("H0CA00002", "REP", "C", 40, 30),
            ("S0CA00001", "DEM", "O", 50, 50), ("S0TX00001", "LIB", "C", 10, 10),
            ("P00000001", "DEM", "C", 200, 150), ("P00000002", "XYZ", "C", 20, 5),
        ):
            row = candidate_row(candidate_id, party, "CA", receipts, 0, 0, 0)
            row[2] = status
            row[17] = str(individual)
            rows.append(row)
        series = build_composition_series(2024, rows)
        self.assertEqual(len(series), len(COMPOSITION_SPECS))
        house_party = series[series_key(2024, "H", "party_receipts")]
        self.assertEqual(dict(zip(house_party["labels"], house_party["values"])), {"Democratic": 100, "Republican": 40})
        incumbency = series[series_key(2024, "H", "incumbency_receipts")]
        self.assertEqual(dict(zip(incumbency["labels"], incumbency["values"])), {"Incumbents": 100, "Challengers": 40})
        funding = series[series_key(2024, "H", "funding_mix")]
        self.assertEqual(dict(zip(funding["labels"], funding["values"])), {"Individual contributions": 90, "Other receipts": 50})
        president = series[series_key(2024, "P", "party_candidates")]
        self.assertEqual(dict(zip(president["labels"], president["values"])), {"Democratic": 1, "Other parties": 1})
        self.assertEqual(house_party["meta"]["category"], "U.S. Elections")
        self.assertEqual(house_party["chartType"], "doughnut")

    def test_rejects_unrecognized_candidate_summary_shape(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("weball24.txt", "too|few|columns\n")
        with self.assertRaisesRegex(ValueError, "unexpected row format"):
            _candidate_summary_rows(stream.getvalue(), 2024)

    def test_published_snapshot_contains_115_sourced_series(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / "data" / "us-campaign-finance.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["collection_status"], "ok")
        self.assertEqual(payload["cycles"], [2018, 2020, 2022, 2024, 2026])
        self.assertEqual(len(payload["series"]), 115)
        self.assertEqual(sum(1 for item in payload["series"].values() if item.get("meta")), 50)
        for key, series in payload["series"].items():
            self.assertTrue(key.startswith("us_fec_"), key)
            self.assertTrue(series["source"].startswith("https://www.fec.gov/"), key)
            self.assertTrue(series["labels"], key)
            self.assertEqual(len(series["labels"]), len(series["values"]), key)
        for cycle in (2018, 2020, 2022, 2024, 2026):
            pie = payload["series"][f"us_fec_{cycle}_p_receipt_composition"]
            self.assertEqual(pie["chartType"], "doughnut")
            self.assertGreater(sum(pie["values"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
