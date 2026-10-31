# Data pipelines and deployment

## Scheduled collectors

| Workflow | Cadence | Main outputs |
| --- | --- | --- |
| [Daily PolityPolicy Update](../.github/workflows/daily-politypolicy-update.yml) | Daily | Article snapshots, public-source charts, monthly indicator extraction, FEC campaign-finance snapshots |
| [Weekly Substack Article Update](../.github/workflows/weekly-substack-articles.yml) | Weekly | Public article feeds |
| [Election Results Update](../.github/workflows/election-results-update.yml) | Every 3 hours | `data/election-results.json` |
| [Historical Election Archive Update](../.github/workflows/historical-election-archive-update.yml) | Monthly | `data/historical-elections.json` |
| [Recent Indian Election Data Update](../.github/workflows/recent-indian-elections-update.yml) | Daily | `data/recent-indian-elections.json` |

The election collector uses Python's standard library, stores source URLs and collection status, and records collection errors in the JSON metadata. If a source fails, prior cached records for that source are retained when available and the status is marked `partial`.

The historical collector downloads public detailed-result XLSX workbooks from ECI statistical-report pages, parses only recognized candidate/constituency/vote columns, and copies its source into the Pages data directory. Unavailable PDFs and unrecognized layouts remain uncovered and are not presented as empty election returns. The daily chart builder also refreshes World Bank tourism data and reconstructs UNESCO inscription indicators from current property pages.

The daily pipeline downloads the FEC candidate-summary bulk files for the 2018, 2020, 2022, 2024 and 2026 cycles, validates their ZIP members and row layout, and aggregates four reported financial measures by candidate party (President) or candidate office state (House and Senate). It publishes `data/us-campaign-finance.json`; it does not estimate votes, turnout, or public contributions. An unexpected source format or failed download stops collection instead of publishing empty or zero-filled data.

## Data flow

1. A collector writes a JSON snapshot under `data/`.
2. The Pages deployment copies the snapshot to `site/data/`.
3. The browser merges `election-results.json` and `us-campaign-finance.json` into dashboard chart data; the historical-election explorer fetches its candidate-level archive and recent constituency snapshot only when Elections is selected.
4. Source timestamps and notes remain attached to chart data. ECI's provisional-results caveat appears in the indicator description and generated series note.
5. `docs/openapi.json` documents deployed static GET resources; `docs/api.html` offers Swagger UI and an all-resource JSON check.

## Running and checking locally

```powershell
python scripts/collect_election_results.py
python scripts/collect_historical_elections.py
python scripts/collect_recent_indian_elections.py
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
