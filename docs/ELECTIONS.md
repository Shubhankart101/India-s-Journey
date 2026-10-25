# Election data coverage

The dashboard separates **Elections** (Indian results) from **U.S. Elections** (U.S. National Archives results and FEC campaign-finance aggregates). It does not combine Indian candidate votes with U.S. Electoral College votes or describe campaign finances as election outcomes.

## Current Indian results

The live collector follows ECI's currently published results landing page and parses the constituency tables it exposes. The official site identifies these results as provisional until final Form 20 returns are available.

- Source: [ECI results portal](https://results.eci.gov.in/).
- Schedule: every three hours through [Election Results Update](../.github/workflows/election-results-update.yml).
- Scope: currently published constituencies discovered from the live portal; this is not a full election archive.
- Measures: candidate votes, reported vote shares, leading-candidate vote share, and vote margins derived from the same constituency candidate table.
- Charts also include a provisional party-lead share across currently published constituencies and a vote-composition doughnut for each published constituency. Each constituency chart shows its five highest-vote candidates separately and combines remaining candidates (including NOTA where present); the scope is never presented as a complete State tally.

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

## United States: Presidential elections and campaign finance

The standalone **U.S. Elections** group contains:

- **U.S. Presidential Elections:** National Archives winner and main-opponent Electoral College totals for Presidential elections from 2000 through 2024. These are electoral votes, not popular votes or ballots cast.
- **U.S. Presidential Campaign Finance:** 16 FEC indicators—receipts, disbursements, cash on hand and debts—aggregated by party for Presidential-office candidates in the 2018, 2020, 2022 and 2024 filing cycles. 2018 and 2022 are midterm years, not Presidential elections; cycle labels describe campaign-finance filing cycles, not election years for the office.
- **U.S. Congressional Campaign Finance:** 32 FEC indicators for House and Senate candidates—four measures, two offices and four cycles—aggregated by candidate office state.
- Interactive doughnut summaries show winner, main opponent, and other/unassigned Electoral College votes for each Presidential election, plus Presidential-office candidate receipts by party for each FEC filing cycle.

Campaign-finance aggregates are not vote counts or turnout. Presidential party totals are not state-by-state results; Senate and House state totals are not results for a particular seat.

Electoral College source: [National Archives Electoral College results](https://www.archives.gov/electoral-college).

FEC source: [candidate summary files](https://www.fec.gov/campaign-finance-data/candidate-summary-file-description/) and [cycle-specific bulk downloads](https://www.fec.gov/data/browse-data/?tab=candidates). Candidate totals include principal campaign committees and other authorized committees. FEC summaries update as reports are received and may change when amendments are processed. The dashboard checks the files daily; this is not a live result feed.

U.S. popular vote by state, voter registration, turnout and constituency-level House returns are not included. No official, consistent dataset for these measures has been added, and FEC financial summaries are not a substitute.

## ECI live-result interpretation

The live ECI constituency tables include a separate `Total` row. It is the constituency-wide vote total, not a candidate, and is excluded from candidate rankings, winner share, margins and party-lead counts. Party-lead counts cover only the currently published constituencies in that snapshot; they are not complete election seat totals. Candidate vote shares are shown only when the ECI table reports them.

## Scraper design reference

The [india-votes-data project](https://github.com/thecont1/india-votes-data) was reviewed as a design reference for constituency-result collection and normalized candidate records. Its database/API architecture does not fit this static site. No code or data from it was copied; this project's ECI collector and FEC pipeline use project-specific standard-library parsers and static JSON outputs. The repository is MIT-licensed.
