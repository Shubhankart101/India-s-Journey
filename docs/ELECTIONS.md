# Election data coverage

## India: Lok Sabha and State Assemblies

The collector follows the Election Commission of India (ECI) results landing-page redirect, discovers the currently published Assembly and Lok Sabha by-election result pages, and reads constituency-wise candidate tables. Each retained constituency record includes election type, constituency, State/UT when provided, candidate, party, total votes, vote share, and the ECI source URL.

- Source: [ECI results portal](https://results.eci.gov.in/).
- Schedule: every three hours through [Election Results Update](../.github/workflows/election-results-update.yml).
- Display: candidate vote totals for up to the 30 highest-vote candidates in currently published constituencies. The JSON snapshot retains all parsed candidate rows.
- Derived indices: candidate vote totals, reported candidate vote shares, leading-candidate vote share, vote margin over the runner-up, and leading constituencies by party. Constituency margins are calculated from the same current ECI candidate totals.
- Status: ECI's displayed results are provisional until Form 20. This chart is not a certified final-result series.
- Scope limitation: the current portal is discovered dynamically and is not a verified archive of all historical Lok Sabha and State Assembly elections. Historical constituency-level Indian results are not claimed as complete.

## United States: Presidential elections

The dashboard reads the winner and main opponent Electoral College totals for U.S. Presidential elections from 2000 through 2024 from the National Archives.

- Source: [National Archives Electoral College results](https://www.archives.gov/electoral-college).
- Frequency: each election cycle (the collector checks the published archive every three hours).
- Measure: Electoral College votes, not popular votes or ballots cast.

## United States: House elections

House candidate returns are not included. The United States does not have a single verified federal results feed for all House districts in the source set reviewed; official returns are reported by state. Fundraising reports, turnout estimates, and third-party aggregations are not substituted and labelled as official House results.

## Comparability

The Indian series is candidate-level votes in currently published by-election constituencies; the U.S. series is national Electoral College votes in completed Presidential elections. These are separate subgroups and measures, not a normalized head-to-head comparison. The dashboard does not infer turnout, vote share, or historical continuity beyond source observations.
