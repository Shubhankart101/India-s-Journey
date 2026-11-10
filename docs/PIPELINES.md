# Data pipelines and deployment

## Dataset producer inventory

`python scripts/update_all_data.py` runs the registered producers in dependency order, then exports the catalogue and builds explainers. Use `--only <producer-or-dataset> [<name> ...]` to select a pipeline; `--offline` or `--skip-network` disables all network producers and uses complete local caches; `--dry-run` prints the plan without changing files. A failed producer restores its previous output, and a summary lists changed, unchanged, skipped and failed steps. Dataset filenames and producer names are both accepted by `--only`.

| Dataset | Source | Producer | Cadence | Command |
| --- | --- | --- | --- | --- |
| `atlas-series.json` | Lok Sabha, epic and faith atlas outputs | `build_atlas_series.py` | After atlas builds | `python scripts/build_atlas_series.py` |
| `borrowing.json` | RBI Handbook of Statistics on the Indian Economy | `build_borrowing.py` | Annual | `python scripts/build_borrowing.py` |
| `catalog.json` | Dashboard definitions and published snapshots | `export_catalog.mjs` | After data builds | `node scripts/export_catalog.mjs` |
| `chart-latest.json` | World Bank, RBI, MoSPI, UNESCO, NJDG and other official sources | `generate_public_charts.py` | Daily | `python scripts/generate_public_charts.py` |
| `economic-survey-monthly.json` | Ministry of Finance Economic Survey | `fetch_economic_survey_monthly.py` | Monthly | `python scripts/fetch_economic_survey_monthly.py` |
| `election-indices.json` | Recent Indian election results | `build_election_indices.py` | On election data refresh | `python scripts/build_election_indices.py` |
| `election-results.json` | ECI results and U.S. National Archives | `collect_election_results.py` | Every 3 hours on counting days | `python scripts/collect_election_results.py` |
| `epic-kingdoms.json` | Curated epic places and verified public-text verses | `build_epic_atlas.py` | On content update | `python scripts/build_epic_atlas.py` |
| `faith-journeys.json` | Curated journeys plus public text verse sources | `build_faith_journeys.py` | On source update | `python scripts/pull_faith_verses.py` then `python scripts/build_faith_journeys.py` |
| `fiscal-series.json` | Union Budget and RBI fiscal datasets | `build_fiscal_layer.py` | After fiscal inputs | `python scripts/build_fiscal_layer.py` |
| `historical-elections.json` | ECI statistical reports and detailed-result workbooks | `collect_historical_elections.py` | Monthly | `python scripts/collect_historical_elections.py` |
| `indian-matrix-latest.json` | Indian Matrix public article feed | `collect_indian_matrix.py` | Daily | `python scripts/collect_indian_matrix.py` |
| `latest.json` | PolityPolicy homepage status | `check_site_status.py` | Daily | `python scripts/check_site_status.py` |
| `latest-status.json` | PolityPolicy homepage status | `check_site_status.py` | Daily | `python scripts/check_site_status.py` |
| `lok-sabha-atlas.json` | ECI-derived constituency history and recent ECI results | `build_lok_sabha_atlas.py` | After election results | `python scripts/build_lok_sabha_atlas.py` |
| `lwe-insurgency.json` | PIB, ORF and ICFS reports | `build_lwe_insurgency.py` | On report release | `python scripts/build_lwe_insurgency.py` |
| `ncrb-and-analyses.json` | NCRB and Indian Matrix | `collect_ncrb_and_analyses.py` | Monthly | `python scripts/collect_ncrb_and_analyses.py` |
| `niti-reports.json` | NITI Aayog reports and transcribed report tables | `build_niti_reports.py` | On report release | `python scripts/build_niti_reports.py` |
| `pew-india-reports.json` | Pew Research Center India report catalogue | `collect_pew_india_reports.py` | Weekly | `python scripts/collect_pew_india_reports.py` |
| `pew-snapshots.json` | Pew Research Center surveys | `collect_pew_snapshots.py` | Weekly | `python scripts/collect_pew_snapshots.py` |
| `recent-indian-elections.json` | ECI results and India Votes Data | `collect_recent_indian_elections.py` | Daily | `python scripts/collect_recent_indian_elections.py` |
| `scripture-verses.json` | Reviewed scripture corpus | No standalone producer; editorial input consumed by `build_scripture_verses.py` | As reviewed | `python scripts/build_scripture_verses.py` (builds site bundles; does not generate this corpus) |
| `source_publishers.json` | Curated publisher/host mapping | No standalone producer; manually maintained and checked by `audit_sources.py` | As reviewed | `python scripts/audit_sources.py` (validation only) |
| `sports.json` | Official sports federation and ranking snapshots | `refresh_sports_sources.py` / `build_sports_data.py` | Weekly | `python scripts/refresh_sports_sources.py`; offline: `python scripts/build_sports_data.py` |
| `state_fiscal.json` | RBI Handbook of Statistics on Indian States and RBI State Finances | `build_state_fiscal.py` | Annual | `python scripts/build_state_fiscal.py` |
| `substack-latest.json` | PolityPolicy public article feed | `collect_substack.py` | Weekly | `python scripts/collect_substack.py` |
| `union_budget.json` | Union Budget: Budget at a Glance PDFs | `build_union_budget.py` | Annual | Network: `python scripts/build_union_budget.py --fetch`; cached: `python scripts/build_union_budget.py` |
| `us-campaign-finance.json` | Federal Election Commission | `collect_us_campaign_finance.py` | Daily | `python scripts/collect_us_campaign_finance.py` |
| `voter-roll.json` | ECI, Census and World Bank sources | `build_voter_roll.py` | On ECI revision | `python scripts/build_voter_roll.py` |

The `data/raw/`, `data/raw_fiscal/`, `data/epic-sources/`, `data/faith-sources/` and `data/journey-sources/` directories are gitignored caches and are not included in the repository. Network-mode updates fetch missing raw election CSVs, Union Budget PDFs, RBI HTML tables and faith verses; journey source pages are fetched lazily into the ignored cache. `--offline` never fetches; it runs cache-backed builders only when their required inputs are present, otherwise it logs a skip and preserves published data. The curated `data/epic-sources/{mahabharata,ramayana}.json` inputs have no canonical downloadable mirror; those atlas steps are skipped if the local editorial cache is absent. `scripture-verses.json` and `source_publishers.json` are intentional hand-maintained inputs, not generated snapshots.

The scheduled [Monthly Data Refresh](../.github/workflows/data-refresh.yml) workflow runs the orchestrator and proposes updates as a pull request; it can also be started manually in offline mode. The individual workflows below remain available for more frequent source-specific refreshes. The static site is built from the React frontend by `npm run build:static`; deployment workflows should not stage legacy `docs/data/` copies.


## Scheduled collectors

| Workflow | Cron (UTC) | Cadence rationale | Main outputs |
| --- | --- | --- | --- |
| [Daily PolityPolicy Update](../.github/workflows/daily-politypolicy-update.yml) | `30 2 * * *` | Articles, market/payment and FEC filings change daily | Article snapshots, Indian Matrix feed, FEC campaign finance, public-source and World Bank charts |
| [Weekly Substack Article Update](../.github/workflows/weekly-substack-articles.yml) | Weekly | README reading list | README article list |
| [Weekly Pew Research Update](../.github/workflows/weekly-pew-research-update.yml) | `0 4 * * 1` | Pew publishes India reports irregularly, at most a few per month | Pew snapshots and report catalog |
| [Monthly Economic Review Update](../.github/workflows/monthly-economic-review-update.yml) | `0 4 5,15,25 * *` | Monthly Economic Review/appendix tables are released monthly on varying dates | `data/economic-survey-monthly.json` |
| [NCRB Crime Data Update](../.github/workflows/ncrb-crime-data-update.yml) | `30 5 1 * *` | *Crime in India* is annual; a monthly check catches the release | `data/ncrb-and-analyses.json` |
| [Election Results Update](../.github/workflows/election-results-update.yml) | Every 3 hours | Live counting days | `data/election-results.json` |
| [Historical Election Archive Update](../.github/workflows/historical-election-archive-update.yml) | Monthly | Statistical reports are published after elections | `data/historical-elections.json` |
| [Recent Indian Election Data Update](../.github/workflows/recent-indian-elections-update.yml) | `15 8 * * *` | Picks up newly declared results | `data/recent-indian-elections.json`, `data/election-indices.json` |
| [Sports Data Update](../.github/workflows/sports-data-update.yml) | `15 4 * * 2` | Rankings and match records change after each international window; a weekly check is enough | `data/sports_sources/*.json`, `data/sports.json` |
| [Weekly Legal Data Update](../.github/workflows/legal-data-update.yml) | `30 4 * * 3` | NJDG docket totals change daily; a weekly snapshot captures pendency and disposition movement | `data/legal/njdg_snapshot.json`, `data/legal/njdg_history.json`, judiciary chart series |

Every workflow that changes chart data also runs `node scripts/export_catalog.mjs` and commits `data/catalog.json`. The Django container imports that catalogue when it starts (`manage.py import_catalog`), so the web app shows the same data as the static site after its next deploy.

## Pipelines by group

| Explore group | Builder script(s) | Workflow | Schedule (UTC) |
| --- | --- | --- | --- |
| Economic | `generate_public_charts.py` (World Bank, markets, RBI), `fetch_economic_survey_monthly.py`, `collect_indian_matrix.py` | Daily PolityPolicy Update, Monthly Economic Review Update | Daily 02:30; 5th/15th/25th 04:00 |
| Industry Trends & Performance | `manufacturing_layer.py` (MOSPI IIP, SIAM) | Daily PolityPolicy Update | Daily 02:30 |
| Mining & Natural Resources | `mining_layer.py` (MOSPI WPI and IIP), `official_indicator_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Payments & Digital Banking | `generate_public_charts.py`, `rbi_state_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| State Performance & Regional Health | `rbi_state_layer.py`, `derived_pie_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Public Health & Epidemiology | `official_indicator_layer.py`, `rbi_state_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Social | `official_indicator_layer.py`, `mospi_layer.py` (PLFS, AISHE, Women & Men), `rbi_state_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Environment & Climate | `mospi_layer.py` (EnviStats), `official_indicator_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Agriculture & Food | `mospi_layer.py`, `official_indicator_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Defence & Strategic | `generate_public_charts.py`, `official_indicator_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Crime & Security | `collect_ncrb_and_analyses.py` | NCRB Crime Data Update | 1st of month 05:30 |
| Pew Research | `collect_pew_snapshots.py`, `collect_pew_india_reports.py` | Weekly Pew Research Update | Monday 04:00 |
| Elections (India) | `collect_election_results.py`, `collect_recent_indian_elections.py`, `build_election_indices.py`, `collect_historical_elections.py` | Election Results Update, Recent Indian Election Data Update, Historical Election Archive Update | Every 3 h; daily 08:15; 1st of month 07:00 |
| U.S. Elections | `collect_us_campaign_finance.py` (FEC), `collect_election_results.py` (National Archives) | Daily PolityPolicy Update, Election Results Update | Daily 02:30; every 3 h |
| Tourism & Heritage | `generate_public_charts.py` (World Bank, UNESCO), `tourism_comparison_layer.py` | Daily PolityPolicy Update | Daily 02:30 |
| Innovation & Technology | `innovation_layer.py` (World Bank WDI: WIPO patents/designs, UNESCO R&D, ITU digital, high-tech trade, entrepreneurship) | Daily PolityPolicy Update | Daily 02:30 |
| Extra subgroups in 12 groups | `expansion_layer.py` (World Bank WDI, `xp_*` keys), `derived_groups_layer.py` (Pew, Elections, U.S. Elections; derived from committed data, `dg_*` keys) | Daily PolityPolicy Update | Daily 02:30 |
| Sports, Cricket, Hockey, Football | `refresh_sports_sources.py` → `sports_fetch/{individual,cricket,hockey,football}.py` → `build_sports_data.py` | Sports Data Update | Tuesday 04:15 |
| Judiciary & Pending Cases | `legal_fetch/njdg.py` -> `legal_layer.py` (Supreme Court, High Courts, district and subordinate courts) | Weekly Legal Data Update | Wednesday 04:30 |
| NITI Aayog report indices (health, fiscal health, MPI, SEQI, export preparedness, innovation) | `build_niti_reports.py` (reads `scripts/niti_report_tables.json` plus scores listed in the script) -> `data/niti-reports.json` | Manual, when NITI Aayog publishes a new edition | On release |
| Maoist / LWE insurgency indices (PIB, ORF, ICFS) | `build_lwe_insurgency.py` -> `data/lwe-insurgency.json` | Manual, when a new report is published | On release |

Each source has its own failure handling. If a source fails, the previous series or snapshot is kept, so a broken site never empties a chart.

### Innovation and expansion layers

`scripts/innovation_layer.py` publishes 131 series (keys `innov_*`) in nine Innovation & Technology subgroups: Patents & IP, Industrial Designs & IP Filings, Research & Development, Scientific Publications & Talent, High-Tech Trade & Manufacturing, IP Royalties & Technology Payments, Digital Technology Adoption, Startups & New Business, and Global Innovation Benchmarks. `scripts/expansion_layer.py` adds about 300 World Bank series as two or three new subgroups in each of the twelve non-sports groups, and `scripts/derived_groups_layer.py` derives about 130 more for Pew Research, Elections and U.S. Elections from the committed snapshots. All three run inside `generate_public_charts.py` after the RBI state layer; a failed call keeps the previously published series. Their tests live in `tests/test_innovation_layer.py`, `tests/test_expansion_layer.py` and `tests/test_derived_groups_layer.py`.

### Judiciary & Pending Cases pipeline

`scripts/legal_fetch/njdg.py` visits the official Supreme Court, High Courts and district/subordinate-courts NJDG portals, then uses their `home/fetchStateData`, `home/newPendDashboard` and `home/updateInstitutionDisp` AJAX actions. It writes normalized response tables and series arrays to `data/legal/njdg_snapshot.json`; `data/legal/njdg_history.json` appends dated portal pendency snapshots. `scripts/legal_layer.py` builds the three Judiciary & Pending Cases subgroups from that committed snapshot and can merge them into both chart JSON files without running the network-heavy public-chart generator (`python -m scripts.legal_layer --merge`). The weekly workflow validates the layer and refreshes the public catalog and static chart bundles.

### Static React API snapshots

The static deployment is built from the shared React frontend. `npm run build:static` runs `scripts/export_static_api.mjs`, which exports the Django-compatible category, indicator, article, search-index, stats, and legacy-alias payloads from `data/catalog.json` into `docs/api/`, then Vite builds the app into `docs/`. Client-side filtering and pagination preserve the API response shape without a server. Generated snapshots are rebuilt in both the Netlify build and GitHub Pages workflow.
### Sports pipeline

`scripts/refresh_sports_sources.py` runs one fetcher module per sport family and writes `data/sports_sources/{cricket,hockey,football,individual_sports}.json`. Each producer runs on its own. If one fails, its previous series are kept and listed under `stale` in the snapshot. `scripts/build_sports_data.py` then builds `data/sports.json` from the snapshots only. The workflow runs `tests/test_sports_data.py` before committing, and the tests reject wiki sources, empty subgroups and player indices without both past and current players. See [SPORTS.md](SPORTS.md) and [`scripts/sports_fetch/README.md`](../scripts/sports_fetch/README.md).

Workflows that rebuild `chart-latest.json` share the `daily-public-data` concurrency group, so they never race; each fetches and rebases before pushing. [Deploy Interactive Dashboard](../.github/workflows/deploy-dashboard.yml) runs after any of them succeeds.

The Lok Sabha 2024 rows are read from the official ECI *Constituency-Wise Detailed Result* workbook (statistical report 33) with party names from report 3; the job installs `xlrd` and `openpyxl`. Rows are de-duplicated on year, type, state, seat, candidate, party and votes so that namesake candidates in one seat are not merged. `scripts/build_election_indices.py` then derives 208 series (`data/election-indices.json`): seat, vote, margin, winner-share, candidate-field and party/independent/NOTA doughnuts for Lok Sabha 2024 (national and per State/UT) and every 2022–2026 Assembly election, plus cross-state comparisons (NOTA share, close contests, median margin, candidates per seat, largest-party dominance, parties winning seats) and latest-Assembly seat and States-led-by-party pies, and validation tests require all 543 seats and the official party tallies before anything is committed.

The election collector uses Python's standard library, stores source URLs and collection status, and records collection errors in the JSON metadata. If a source fails, prior cached records for that source are retained when available and the status is marked `partial`.

The historical collector downloads public detailed-result XLSX workbooks from ECI statistical-report pages, parses only recognized candidate/constituency/vote columns, and copies its source into the Pages data directory. Unavailable PDFs and unrecognized layouts remain uncovered and are not presented as empty election returns. The daily chart builder also refreshes World Bank tourism data and reconstructs UNESCO inscription indicators from current property pages.

The daily pipeline downloads the FEC candidate-summary bulk files for the 2018, 2020, 2022, 2024 and 2026 cycles, validates their ZIP members and row layout, and aggregates four reported financial measures by candidate party (President) or candidate office state (House and Senate), plus 10 composition pies per cycle (party, incumbency and funding-source mixes). It publishes 115 series in `data/us-campaign-finance.json`; it does not estimate votes, turnout, or public contributions. An unexpected source format or failed download stops collection instead of publishing empty or zero-filled data.

`scripts/official_indicator_layer.py` adds 30 World Bank line indicators and 13 composition pies across the Economic, Industry, Payments, State services, Health, Defence, Mining, Social and Tourism groups. It also adds 17 `EXPLAINED_INDICATORS`, covering environment, agriculture, social and health. Each series carries a `meta` block (title, subtitle, category, subgroup, colour, unit, and for explained series `explain: {what, read, why}`), so the dashboard registers it without hand-written definitions. A failed World Bank call keeps the previously published series.

`scripts/mospi_layer.py` (also run by the daily chart builder) adds 46 explained series from the MoSPI API platform (`api.mospi.gov.in`, legacy-TLS context, pages of at most 200 rows).

Sources:
- EnviStats India (`/api/env/getEnvStatsRecords`);
- Women & Men in India (`/api/gender/getGenderRecords`);
- AISHE (`/api/aishe/getAisheRecords`);
- PLFS (`/api/plfs/getData`).

The specs are declarative. Each declares one of three chart kinds: a national line, a latest-period State/UT ranking, or a latest-period composition. Specs can also sum months into annual totals. The layer handles these source quirks:
- a national total filed under a State name is relabelled All India;
- `(P)` and `*` year markers are stripped, and the note records those years as provisional;
- projected periods are excluded;
- mislabelled units (oilseeds and sugarcane are in lakh tonnes) carry a caveat.

If an indicator fails, its previous series is kept.

`scripts/export_catalog.mjs` turns `meta.explain` into "What it shows — / How to read it — / Why it matters —" paragraphs in each indicator's `details`, which the React indicator page renders as explainer tiles.

The daily chart builder also runs `scripts/tourism_comparison_layer.py` (World Bank arrivals and receipts for India and the most-visited countries) and `scripts/manufacturing_layer.py`. The manufacturing layer reads annual sectoral and monthly IIP rows from the paginated MOSPI API (`api.mospi.gov.in/api/iip`, base 2011-12, legacy-TLS context) plus the SIAM historical production table. If a source fails, the layer keeps the previously published series.

`scripts/rbi_state_layer.py` (also run by the daily chart builder) adds about 140 all-State/UT series from the RBI *Handbook of Statistics on Indian States* (`rbi.org.in/Scripts/PublicationsView.aspx?id=23449+N`, ~40 tables). A generic parser handles split year chunks, sub-columns (Rural/Urban, Male/Female), transposed tables and numbered names, and `canonical_state()` maps every spelling to the 28 States and 8 Union Territories. Each table yields a State/UT ranking, a regional-share or band-distribution doughnut and an All-India trend across Payments & Digital Banking (bank branches, deposits, credit, C-D ratio, RRBs, NPS/APY), Public Health (IMR, birth/death rates, life expectancy, hospitals and beds), Social (literacy, GER, poverty, unemployment, welfare) and State Performance (GSDP, fiscal ratios, own tax, industry, power, roads). Every note states how many of the 36 States/UTs the source reports and names the missing ones; if a table fails, the previous series are kept.

`scripts/mining_layer.py` (also run by the daily chart builder) adds the Mining & Natural Resources deep-dive. It pages through the MOSPI WPI API (`api.mospi.gov.in/api/wpi/getWpiRecords`, `group_code` 1103000000 minerals, 1104000000 crude petroleum & natural gas, 1201000000 coal) for monthly item prices since April 2012, and the MOSPI IIP API for annual and monthly mining output. Rankings, price-change bands and rising-vs-falling pies are recomputed on every run from the latest month, and the previous series are kept if MOSPI is unavailable.

Substack blocks RSS requests from some GitHub-hosted runner IPs with HTTP 403. `scripts/rss_utils.fetch_rss_or_none()` turns a blocked or unreachable feed into a workflow `::warning::`. The collectors then keep the previously committed article snapshot, and the rest of the daily pipeline (public charts, World Bank, FEC) still runs. Before this change, one blocked feed stopped the whole daily job and left every chart stale.

## Data flow

1. Collectors write source snapshots under `data/` and `scripts/export_catalog.mjs` produces the canonical `data/catalog.json`.
2. Django imports that catalogue for the web app. The static deployment runs `npm run build:static` to generate React-compatible JSON responses under `docs/api/` and bundle the same React UI into `docs/`.
3. Supporting datasets and assets are copied from `frontend/public/` into `docs/`; theme, maps, and atlas UI are shared with the web app.
4. Netlify builds and publishes `docs/`; the Pages workflow publishes the same output as the backup mirror.
## Running and checking locally

```powershell
python scripts/collect_election_results.py
python scripts/collect_historical_elections.py
python scripts/collect_recent_indian_elections.py
python scripts/build_election_indices.py
python scripts/collect_us_campaign_finance.py
python -m unittest discover -s tests -p 'test_historical_elections.py' -v
python -m unittest discover -s tests -p 'test_tourism_heritage.py' -v
python -m unittest discover -s tests -p 'test_static_api.py' -v
```

To run the dashboard endpoint tests:

```powershell
python -m unittest tests.test_dashboard_endpoints
```

Network collection requires access to the public ECI and National Archives pages. Parser tests use local fixtures and do not require network access.

## Continuous integration

[`webapp-ci.yml`](../.github/workflows/webapp-ci.yml) runs on every push and pull request that touches `webapp/`, `frontend/`, the catalogue, or the `Dockerfile`:

| Job | What it checks |
| --- | --- |
| **Django tests + OpenAPI schema** | `check --deploy` with production settings, no missing migrations, the full Django test suite (API, OAuth, Swagger, error pages), `spectacular --validate --fail-on-warn` (the schema is uploaded as an artifact), and `import_catalog` |
| **React unit tests + build** | Vitest suite and production build |
| **Playwright end-to-end** | Builds the SPA, starts Django in production mode, and runs the e2e suites on desktop Chrome and Pixel 7. The report is uploaded on failure |
| **Docker image builds** | Builds the production image (not pushed) |

See [TESTING.md](TESTING.md) for details.

## Monitoring and backup

| Workflow | Cron (UTC) | Purpose |
| --- | --- | --- |
| [Uptime monitor](../.github/workflows/uptime-monitor.yml) | `*/30 * * * *` | Checks the Netlify dashboard and the GitHub Pages mirror with retries (plus `<app_url>/api/health/` when an `app_url` is given on a manual run). Opens an `outage` issue listing failed sites and linking the copy still up, and closes it on recovery |
| [Deploy Interactive Dashboard](../.github/workflows/deploy-dashboard.yml) | After the collectors | Publishes `docs/` to GitHub Pages as the backup mirror of the Netlify site (Netlify redeploys itself on every push) |

See [BACKUP.md](BACKUP.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
