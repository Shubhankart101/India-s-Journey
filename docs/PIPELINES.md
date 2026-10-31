# Data pipelines and deployment

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

Workflows that rebuild `chart-latest.json` share the `daily-public-data` concurrency group, so they never race; each fetches and rebases before pushing. [Deploy Interactive Dashboard](../.github/workflows/deploy-dashboard.yml) runs after any of them succeeds.

The Lok Sabha 2024 rows are read from the official ECI *Constituency-Wise Detailed Result* workbook (statistical report 33) with party names from report 3; the job installs `xlrd` and `openpyxl`. Rows are de-duplicated on year, type, state, seat, candidate, party and votes so that namesake candidates in one seat are not merged. `scripts/build_election_indices.py` then derives 208 series (`data/election-indices.json`): seat, vote, margin, winner-share, candidate-field and party/independent/NOTA doughnuts for Lok Sabha 2024 (national and per State/UT) and every 2022?2026 Assembly election, plus cross-state comparisons (NOTA share, close contests, median margin, candidates per seat, largest-party dominance, parties winning seats) and latest-Assembly seat and States-led-by-party pies, and validation tests require all 543 seats and the official party tallies before anything is committed.

The election collector uses Python's standard library, stores source URLs and collection status, and records collection errors in the JSON metadata. If a source fails, prior cached records for that source are retained when available and the status is marked `partial`.

The historical collector downloads public detailed-result XLSX workbooks from ECI statistical-report pages, parses only recognized candidate/constituency/vote columns, and copies its source into the Pages data directory. Unavailable PDFs and unrecognized layouts remain uncovered and are not presented as empty election returns. The daily chart builder also refreshes World Bank tourism data and reconstructs UNESCO inscription indicators from current property pages.

The daily pipeline downloads the FEC candidate-summary bulk files for the 2018, 2020, 2022, 2024 and 2026 cycles, validates their ZIP members and row layout, and aggregates four reported financial measures by candidate party (President) or candidate office state (House and Senate), plus 10 composition pies per cycle (party, incumbency and funding-source mixes). It publishes 115 series in `data/us-campaign-finance.json`; it does not estimate votes, turnout, or public contributions. An unexpected source format or failed download stops collection instead of publishing empty or zero-filled data.

`scripts/official_indicator_layer.py` adds 30 World Bank line indicators and 13 composition pies across the Economic, Industry, Payments, State services, Health, Defence, Mining, Social and Tourism groups. Each series carries a `meta` block (title, subtitle, category, subgroup, colour, unit), so the dashboard registers it without hand-written definitions. A failed World Bank call keeps the previously published series.

The daily chart builder also runs `scripts/tourism_comparison_layer.py` (World Bank arrivals and receipts for India and the most-visited countries) and `scripts/manufacturing_layer.py`. The manufacturing layer reads annual sectoral and monthly IIP rows from the paginated MOSPI API (`api.mospi.gov.in/api/iip`, base 2011-12, legacy-TLS context) plus the SIAM historical production table. If a source fails, the layer keeps the previously published series.

`scripts/rbi_state_layer.py` (also run by the daily chart builder) adds about 140 all-State/UT series from the RBI *Handbook of Statistics on Indian States* (`rbi.org.in/Scripts/PublicationsView.aspx?id=23449+N`, ~40 tables). A generic parser handles split year chunks, sub-columns (Rural/Urban, Male/Female), transposed tables and numbered names, and `canonical_state()` maps every spelling to the 28 States and 8 Union Territories. Each table yields a State/UT ranking, a regional-share or band-distribution doughnut and an All-India trend across Payments & Digital Banking (bank branches, deposits, credit, C-D ratio, RRBs, NPS/APY), Public Health (IMR, birth/death rates, life expectancy, hospitals and beds), Social (literacy, GER, poverty, unemployment, welfare) and State Performance (GSDP, fiscal ratios, own tax, industry, power, roads). Every note states how many of the 36 States/UTs the source reports and names the missing ones; if a table fails, the previous series are kept.

`scripts/mining_layer.py` (also run by the daily chart builder) adds the Mining & Natural Resources deep-dive. It pages through the MOSPI WPI API (`api.mospi.gov.in/api/wpi/getWpiRecords`, `group_code` 1103000000 minerals, 1104000000 crude petroleum & natural gas, 1201000000 coal) for monthly item prices since April 2012, and the MOSPI IIP API for annual and monthly mining output. Rankings, price-change bands and rising-vs-falling pies are recomputed on every run from the latest month, and the previous series are kept if MOSPI is unavailable.

Substack blocks RSS requests from some GitHub-hosted runner IPs with HTTP 403. `scripts/rss_utils.fetch_rss_or_none()` turns a blocked or unreachable feed into a workflow `::warning::`. The collectors then keep the previously committed article snapshot, and the rest of the daily pipeline (public charts, World Bank, FEC) still runs. Before this change, one blocked feed stopped the whole daily job and left every chart stale.

## Data flow

1. A collector writes a JSON snapshot under `data/`.
2. The Pages deployment copies the snapshot to `site/data/`.
3. The browser merges `election-results.json`, `us-campaign-finance.json` and `election-indices.json` into dashboard chart data; any series with `meta` becomes a card in its stated group/subgroup. The historical-election explorer fetches its candidate-level archive and recent constituency snapshot only when Elections is selected.
4. Source timestamps and notes remain attached to chart data. ECI's provisional-results caveat appears in the indicator description and generated series note.
5. `docs/openapi.json` documents deployed static GET resources; `docs/api.html` offers Swagger UI and an all-resource JSON check.

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

[`webapp-ci.yml`](../.github/workflows/webapp-ci.yml) runs on every push and pull request that touches `webapp/`, `frontend/`, the catalogue, the `Dockerfile` or `render.yaml`:

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
| [Uptime monitor](../.github/workflows/uptime-monitor.yml) | `*/30 * * * *` | Skipped unless the `APP_URL` repository variable is set. Pings `APP_URL/api/health/` with cold-start retries. Opens an `outage` issue linking the GitHub Pages backup, and closes it on recovery |
| [Deploy Interactive Dashboard](../.github/workflows/deploy-dashboard.yml) | After the collectors | Publishes `docs/`, which is both the static dashboard and the backup site with [`status.html`](status.html) |

See [BACKUP-AND-STATUS.md](BACKUP-AND-STATUS.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
