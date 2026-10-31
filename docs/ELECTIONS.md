# Election data coverage

The dashboard separates **Elections** (Indian results) from **U.S. Elections** (U.S. National Archives results and FEC campaign-finance aggregates). It does not combine Indian candidate votes with U.S. Electoral College votes or describe campaign finances as election outcomes.

## Current Indian results

The live collector follows ECI's currently published results landing page and parses the constituency tables it exposes. The official site identifies these results as provisional until final Form 20 returns are available.

- Source: [ECI results portal](https://results.eci.gov.in/).
- Schedule: every three hours through [Election Results Update](../.github/workflows/election-results-update.yml).
- Scope: currently published constituencies discovered from the live portal; this is not a full election archive.
- Measures: candidate votes, reported vote shares, leading-candidate vote share, and vote margins derived from the same constituency candidate table.
- Charts also include a provisional party-lead share across currently published constituencies and a vote-composition doughnut for each published constituency. The historical constituency explorer includes live Lok Sabha by-election results alongside the archive and shows both candidate-vote bars and an interactive candidate-vote doughnut for the selected seat. Each doughnut shows its five highest-vote candidates separately and combines remaining candidates (including NOTA where present); the scope is never presented as a complete State tally.

## Historical Indian candidate results

The monthly [Historical Election Archive Update](../.github/workflows/historical-election-archive-update.yml) follows public ECI statistical-report pages and downloads public XLSX files whose names identify detailed results. It extracts rows only when candidate, constituency and total-vote columns can be identified, keeps the report URL on every row, and records collection failures in the JSON metadata.

The committed snapshot currently contains **20,041 candidate observations from 16 ECI workbooks** for **2021–2023 across 15 States/UTs**. The collector scans 82 election-related catalog entries; most do not yet yield a supported candidate-results workbook, so the output records partial coverage rather than completeness. Workbook layouts vary, many archive reports are PDFs or lack a supported detailed-result spreadsheet, and this snapshot does not yet contain a verified historical Lok Sabha constituency series. Currently published Lok Sabha by-elections appear separately from the historical archive and must not be mistaken for general-election coverage of all parliamentary seats. Never interpret a missing State, year or seat as zero votes.

The dashboard's historical explorer lets readers choose an available election type, year, State/UT and constituency. Candidate rows, chart values and reported electorate use Indian-number formatting. Vote shares are shown only when they appear in the source workbook; they are not reconstructed from partial totals.

- Source catalog: [ECI statistical reports](https://old.eci.gov.in/statistical-report/statistical-reports/).
- Refresh: monthly; run `python scripts/collect_historical_elections.py` for a manual collection.
- Output: `data/historical-elections.json` and the deployed `data/historical-elections.json`.
- Tests: `python -m unittest discover -s tests -p 'test_historical_elections.py' -v`.

## Recent Indian constituency results

`data/recent-indian-elections.json` adds **41,465 candidate observations** from 21 source files. Lok Sabha 2024 is read from the official ECI [statistical report 33](https://www.eci.gov.in/) (*Constituency-Wise Detailed Result*), with party names from report 3; State Assembly results come from ECI-derived CSV files in [thecont1/india-votes-data](https://github.com/thecont1/india-votes-data), pinned to commit `7d8cf637f83d223b178d11659103a1f52647367a`. Rows are de-duplicated on candidate, party and votes so namesake candidates in one seat (for example Karur and Pollachi) are kept separately. Party tallies match ECI: Lok Sabha 2024 BJP 240, INC 99, SP 37, AITC 29, DMK 22. Coverage is:

- **Lok Sabha 2024:** all 543 parliamentary constituencies across 36 States/UTs.
- **Assembly 2022:** Goa, Manipur, Punjab, Uttar Pradesh and Uttarakhand.
- **Assembly 2023:** Karnataka, Meghalaya, Nagaland and Tripura.
- **Assembly 2024:** Haryana, Jammu and Kashmir, Jharkhand and Maharashtra.
- **Assembly 2025:** Bihar and Delhi.
- **Assembly 2026:** Assam, Kerala, Puducherry, Tamil Nadu and West Bengal.

Assembly EVM and postal votes are added. Source CSVs do not publish vote-share percentages, so shares are calculated from listed candidate totals and marked `*` in the explorer. Surat's uncontested 2024 Lok Sabha winner has no vote count; it is shown as not reported, not zero, and no vote pie is drawn. The [Recent Indian Election Data Update](../.github/workflows/recent-indian-elections-update.yml) checks daily, validates all 543 Lok Sabha seats, and commits only changed source data. This is recent coverage, not every Indian election ever held; pre-2024 Lok Sabha constituency history remains unavailable in this static archive.

### Election pie indices

`scripts/build_election_indices.py` derives **112 interactive doughnut indices** (`data/election-indices.json`) in three Elections subgroups: *Lok Sabha 2024 — National* (8: seats and votes by party, victory-margin bands, winner vote-share bands, candidates per seat, NOTA share, seats by State/UT, party vs independent votes), *Lok Sabha 2024 — States* (44: seat and vote pies for 22 multi-seat States/UTs) and *State Assembly Results 2022–2026* (60: seat and vote pies for each Assembly election). Click a slice to hide it, hover for value and share, and use the Bar/Pie toggle on any additive card; the centre shows the total.

## SSR and SIR electoral-roll revisions

ECI voter services and Chief Electoral Officer notices publish Special Summary Revision (SSR) and Special Intensive Revision (SIR) instructions, schedules and occasional roll statistics. The project links the official [ECI voter services portal](https://voters.eci.gov.in/) but does **not** yet publish a complete, comparable State/constituency time series of additions, deletions, claims, objections and final elector totals for SSR/SIR. The public notices are not a consistent machine-readable historical feed; no missing totals are inferred from current elector counts. A dedicated index requires extraction from the official revision tables and explicit year/State/roll-stage coverage.

## United States: Presidential elections and campaign finance

The standalone **U.S. Elections** group contains:

- **U.S. Presidential Elections:** National Archives winner and main-opponent Electoral College totals for Presidential elections from 2000 through 2024. These are electoral votes, not popular votes or ballots cast.
- **U.S. Presidential Campaign Finance:** 20 FEC indicators—receipts, disbursements, cash on hand and debts—aggregated by party for Presidential-office candidates in the 2018, 2020, 2022, 2024 and 2026 filing cycles. 2018, 2022 and 2026 are midterm years, not Presidential elections; cycle labels describe campaign-finance filing cycles, not election years for the office.
- **U.S. Congressional Campaign Finance:** 40 FEC indicators for House and Senate candidates—four measures, two offices and five cycles—aggregated by candidate office state.
- **U.S. Campaign Funding Composition:** 50 FEC doughnuts (10 per cycle) splitting candidates and receipts by party, receipts by incumbents vs challengers, and where the money came from (individual contributions, PACs, party committees, candidate contributions and loans, transfers, other) for each office.
- Interactive doughnut summaries show winner, main opponent, and other/unassigned Electoral College votes for each Presidential election, plus Presidential-office candidate receipts by party for each FEC filing cycle.

Campaign-finance aggregates are not vote counts or turnout. Presidential party totals are not state-by-state results; Senate and House state totals are not results for a particular seat.

Electoral College source: [National Archives Electoral College results](https://www.archives.gov/electoral-college).

FEC source: [candidate summary files](https://www.fec.gov/campaign-finance-data/candidate-summary-file-description/) and [cycle-specific bulk downloads](https://www.fec.gov/data/browse-data/?tab=candidates). Candidate totals include principal campaign committees and other authorized committees. FEC summaries update as reports are received and may change when amendments are processed. The dashboard checks the files daily; this is not a live result feed.

U.S. popular vote by state, voter registration, turnout and constituency-level House returns are not included. No official, consistent dataset for these measures has been added, and FEC financial summaries are not a substitute.

## ECI live-result interpretation

The live ECI constituency tables include a separate `Total` row. It is the constituency-wide vote total, not a candidate, and is excluded from candidate rankings, winner share, margins and party-lead counts. Party-lead counts cover only the currently published constituencies in that snapshot; they are not complete election seat totals. Candidate vote shares are shown only when the ECI table reports them.

## Scraper design reference

The [india-votes-data project](https://github.com/thecont1/india-votes-data) was reviewed as a design reference for constituency-result collection and normalized candidate records. Its database/API architecture does not fit this static site, so no scraper code was copied. The recent-results importer uses its published ECI-derived CSV data, retains source-file URLs and commit provenance, and converts it to this site's static JSON format. The repository is MIT-licensed.
