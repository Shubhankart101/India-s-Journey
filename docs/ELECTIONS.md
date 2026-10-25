# Election data coverage

The Elections group separates different electoral systems and source types. It does not combine Indian candidate votes with U.S. Electoral College votes or describe them as directly comparable.

## Current Indian results

The live collector follows ECI's currently published results landing page and parses the constituency tables it exposes. The official site identifies these results as provisional until final Form 20 returns are available.

- Source: [ECI results portal](https://results.eci.gov.in/).
- Schedule: every three hours through [Election Results Update](../.github/workflows/election-results-update.yml).
- Scope: currently published constituencies discovered from the live portal; this is not a full election archive.
- Measures: candidate votes, reported vote shares, leading-candidate vote share, and vote margins derived from the same constituency candidate table.

## Historical Indian candidate results

The monthly [Historical Election Archive Update](../.github/workflows/historical-election-archive-update.yml) follows public ECI statistical-report pages and downloads public XLSX files whose names identify detailed results. It extracts rows only when candidate, constituency and total-vote columns can be identified, keeps the report URL on every row, and records collection failures in the JSON metadata.

The committed snapshot currently contains **20,041 candidate observations from 16 ECI workbooks** for **2021–2023 across 15 States/UTs**. The collector scans 82 election-related catalog entries; most do not yet yield a supported candidate-results workbook, so the output records partial coverage rather than completeness. Workbook layouts vary, many archive reports are PDFs or lack a supported detailed-result spreadsheet, and this snapshot does not yet contain a verified historical Lok Sabha constituency series. Never interpret a missing State, year or seat as zero votes.

The dashboard's historical explorer lets readers choose an available election type, year, State/UT and constituency. Candidate rows, chart values and reported electorate use Indian-number formatting. Vote shares are shown only when they appear in the source workbook; they are not reconstructed from partial totals.

- Source catalog: [ECI statistical reports](https://old.eci.gov.in/statistical-report/statistical-reports/).
- Refresh: monthly; run `python scripts/collect_historical_elections.py` for a manual collection.
- Output: `data/historical-elections.json` and the deployed `data/historical-elections.json`.
- Tests: `python -m unittest discover -s tests -p 'test_historical_elections.py' -v`.

## SSR and SIR electoral-roll revisions

ECI voter services and Chief Electoral Officer notices publish Special Summary Revision (SSR) and Special Intensive Revision (SIR) instructions, schedules and occasional roll statistics. The project links the official [ECI voter services portal](https://voters.eci.gov.in/) but does **not** yet publish a complete, comparable State/constituency time series of additions, deletions, claims, objections and final elector totals for SSR/SIR. The public notices are not a consistent machine-readable historical feed; no missing totals are inferred from current elector counts. A dedicated index requires extraction from the official revision tables and explicit year/State/roll-stage coverage.

## United States: Presidential elections

The dashboard reads winner and main-opponent Electoral College totals for U.S. Presidential elections from 2000 through 2024.

- Source: [National Archives Electoral College results](https://www.archives.gov/electoral-college).
- Measure: Electoral College votes, not popular votes or ballots cast.

## United States: House elections

House candidate returns are not included. Official House results are reported by State; no complete federal candidate-results source was verified in this project. Third-party aggregations are not substituted and labelled as official.
