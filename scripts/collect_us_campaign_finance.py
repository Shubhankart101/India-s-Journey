from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (ROOT / "data" / "us-campaign-finance.json", ROOT / "docs" / "data" / "us-campaign-finance.json")
USER_AGENT = "IndiaJourney public-data dashboard"
CYCLES = (2018, 2020, 2022, 2024, 2026)
OFFICES = {
    "P": ("President", "party"),
    "S": ("Senate", "state"),
    "H": ("House", "state"),
}
MEASURES = {
    "receipts": ("Total receipts", 5),
    "disbursements": ("Total disbursements", 7),
    "cash_on_hand": ("Cash on hand at close of period", 10),
    "debts_owed": ("Debts owed by committee", 16),
}
STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
}


def source_url(cycle: int) -> str:
    return f"https://www.fec.gov/files/bulk-downloads/{cycle}/weball{cycle % 100:02d}.zip"


def series_key(cycle: int, office: str, measure: str) -> str:
    return f"us_fec_{cycle}_{office.lower()}_{measure}"


def _candidate_summary_rows(archive_bytes: bytes, cycle: int) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        expected_name = f"weball{cycle % 100:02d}.txt"
        if expected_name not in archive.namelist():
            raise ValueError(f"FEC {cycle} archive does not contain {expected_name}")
        with archive.open(expected_name) as stream:
            text = stream.read().decode("latin-1")
    rows = list(csv.reader(io.StringIO(text), delimiter="|"))
    if not rows or any(len(row) != 30 for row in rows):
        raise ValueError(f"FEC {cycle} candidate summary has an unexpected row format")
    return rows


def build_cycle_series(cycle: int, rows: list[list[str]]) -> dict[str, dict]:
    totals: dict[tuple[str, str, str], float] = defaultdict(float)
    for row in rows:
        office = row[0][:1].upper()
        if office not in OFFICES:
            continue
        bucket = row[4].strip().upper() if office == "P" else row[18].strip().upper()
        if office == "P":
            if not bucket:
                continue
        elif bucket not in STATE_CODES:
            continue
        for measure, (_, column) in MEASURES.items():
            try:
                amount = float(row[column] or 0)
            except ValueError as error:
                raise ValueError(f"FEC {cycle} contains an invalid {measure} value") from error
            totals[(office, measure, bucket)] += amount

    series: dict[str, dict] = {}
    for office, (office_label, scope) in OFFICES.items():
        buckets = sorted({
            bucket for row_office, _, bucket in totals if row_office == office
        })
        if not buckets:
            raise ValueError(f"FEC {cycle} candidate summary has no {office_label} records")
        scope_label = "Parties" if scope == "party" else "States and District of Columbia"
        highest_label = "Highest party" if scope == "party" else "Highest state"
        for measure, (measure_label, _) in MEASURES.items():
            values = [round(totals[(office, measure, bucket)], 2) for bucket in buckets]
            key = series_key(cycle, office, measure)
            series[key] = {
                "labels": buckets,
                "values": values,
                "chartType": "bar",
                "indexAxis": "y",
                "scope": "category" if scope == "party" else "state",
                "scopeLabel": scope_label,
                "highestLabel": highest_label,
                "source": source_url(cycle),
                "note": (
                    f"{cycle} FEC candidate-summary totals for {office_label} candidates. "
                    f"{measure_label} are summed by {('candidate party' if scope == 'party' else 'candidate office state')}. "
                    "These are campaign-finance aggregates, not votes, turnout, or public contributions alone. "
                    "FEC summaries may be revised as amended reports are processed."
                ),
            }
    return series


def build_receipt_composition_series(cycle: int, receipts: dict[str, dict]) -> dict[str, dict]:
    base = receipts[series_key(cycle, "P", "receipts")]
    return {
        series_key(cycle, "P", "receipt_composition"): {
            **base,
            "chartType": "doughnut",
            "note": (
                f"Share of reported Presidential-office candidate receipts by party in the {cycle} "
                "FEC filing cycle. 2018, 2022 and 2026 are midterm years, not Presidential election years. "
                "Receipts are campaign-finance totals, not votes or public contributions alone."
            ),
        }
    }


PARTY_NAMES = {"DEM": "Democratic", "REP": "Republican", "LIB": "Libertarian", "GRE": "Green", "IND": "Independent"}
INCUMBENCY = {"I": "Incumbents", "C": "Challengers", "O": "Open-seat candidates"}
FUNDING_COLUMNS = (
    ("Individual contributions", 17),
    ("Other committees (PACs)", 25),
    ("Party committees", 26),
    ("Candidate's own contributions", 11),
    ("Candidate loans", 12),
    ("Other loans", 13),
    ("Transfers from authorized committees", 6),
)
COMPOSITION_SUBGROUP = "U.S. Campaign Funding Composition"
COMPOSITION_SPECS = (
    ("H", "party_receipts"), ("H", "incumbency_receipts"), ("H", "funding_mix"), ("H", "party_candidates"),
    ("S", "party_receipts"), ("S", "incumbency_receipts"), ("S", "funding_mix"), ("S", "party_candidates"),
    ("P", "funding_mix"), ("P", "party_candidates"),
)


def _amount(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def _party(code: str) -> str:
    return PARTY_NAMES.get(code.strip().upper(), "Other parties")


def build_composition_series(cycle: int, rows: list[list[str]]) -> dict[str, dict]:
    sums: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in rows:
        office = row[0][:1].upper()
        if office not in OFFICES:
            continue
        receipts = _amount(row[5])
        party = _party(row[4])
        sums[(office, "party_receipts")][party] += receipts
        sums[(office, "party_candidates")][party] += 1
        status = INCUMBENCY.get(row[2].strip().upper())
        if status:
            sums[(office, "incumbency_receipts")][status] += receipts
        listed = 0.0
        for label, column in FUNDING_COLUMNS:
            amount = _amount(row[column])
            sums[(office, "funding_mix")][label] += amount
            listed += amount
        sums[(office, "funding_mix")]["Other receipts"] += max(0.0, receipts - listed)

    titles = {
        "party_receipts": ("Receipts by Party", "Share of {office} candidate receipts by party", " USD"),
        "incumbency_receipts": ("Receipts: Incumbents vs Challengers", "{office} candidate receipts by incumbency status", " USD"),
        "funding_mix": ("Where the Money Came From", "{office} candidate receipts by funding source", " USD"),
        "party_candidates": ("Candidates by Party", "{office} candidates filing FEC summaries, by party", " candidates"),
    }
    series: dict[str, dict] = {}
    for office, measure in COMPOSITION_SPECS:
        office_label = OFFICES[office][0]
        points = sorted(
            ((label, round(value, 2)) for label, value in sums[(office, measure)].items() if value > 0),
            key=lambda point: -point[1],
        )
        if not points:
            raise ValueError(f"FEC {cycle} {office_label} {measure} composition has no positive parts")
        title, subtitle, unit = titles[measure]
        series[series_key(cycle, office, measure)] = {
            "labels": [label for label, _ in points],
            "values": [value for _, value in points],
            "chartType": "doughnut",
            "scope": "category",
            "source": source_url(cycle),
            "note": (
                f"{cycle} FEC candidate-summary file, {office_label} candidates. "
                + ("Funding sources use the FEC individual, other-committee, party, candidate, loan and transfer columns; "
                   "'Other receipts' is total receipts minus those listed sources. " if measure == "funding_mix" else "")
                + "Campaign-finance aggregates, not votes. FEC summaries may be revised as amended reports are processed."
            ),
            "meta": {
                "title": f"{cycle} {office_label}: {title}",
                "subtitle": subtitle.format(office=office_label),
                "frequency": "Daily FEC refresh",
                "color": "#58a6ff",
                "suffix": unit,
                "category": "U.S. Elections",
                "subgroup": COMPOSITION_SUBGROUP,
            },
        }
    return series


def collect_cycle(cycle: int) -> dict[str, dict]:
    request = Request(source_url(cycle), headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        archive_bytes = response.read()
    rows = _candidate_summary_rows(archive_bytes, cycle)
    return {**build_cycle_series(cycle, rows), **build_composition_series(cycle, rows)}


def build_payload(cycles: tuple[int, ...] = CYCLES) -> dict:
    series: dict[str, dict] = {}
    for cycle in cycles:
        series.update(collect_cycle(cycle))
        series.update(build_receipt_composition_series(cycle, series))
    expected_count = len(cycles) * (len(OFFICES) * len(MEASURES) + 1 + len(COMPOSITION_SPECS))
    if len(series) != expected_count:
        raise ValueError(f"Expected {expected_count} FEC series, collected {len(series)}")
    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "Federal Election Commission candidate summary bulk files",
        "cycles": list(cycles),
        "collection_status": "ok",
        "series": series,
    }


def main() -> None:
    payload = json.dumps(build_payload(), indent=2) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(f"Collected {len(json.loads(payload)['series'])} FEC campaign-finance series")


if __name__ == "__main__":
    main()
