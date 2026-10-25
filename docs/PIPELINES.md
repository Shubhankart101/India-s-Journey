# Data pipelines and deployment

## Scheduled collectors

| Workflow | Cadence | Main outputs |
| --- | --- | --- |
| [Daily PolityPolicy Update](../.github/workflows/daily-politypolicy-update.yml) | Daily | Article snapshots, public-source charts, monthly indicator extraction, generated dashboard data |
| [Weekly Substack Article Update](../.github/workflows/weekly-substack-articles.yml) | Weekly | Public article feeds |
| [Election Results Update](../.github/workflows/election-results-update.yml) | Every 3 hours | `data/election-results.json` |

The election collector uses Python's standard library, stores source URLs and collection status, and records collection errors in the JSON metadata. If a source fails, prior cached records for that source are retained when available and the status is marked `partial`.

## Data flow

1. A collector writes a JSON snapshot under `data/`.
2. The Pages deployment copies the snapshot to `site/data/`.
3. The browser loads `election-results.json` and merges its `series` into dashboard chart data.
4. Source timestamps and notes remain attached to chart data. ECI's provisional-results caveat appears in the indicator description and generated series note.

## Running and checking locally

```powershell
python scripts/collect_election_results.py
python -m unittest tests.test_election_results
```

To run the dashboard endpoint tests:

```powershell
python -m unittest tests.test_dashboard_endpoints
```

Network collection requires access to the public ECI and National Archives pages. Parser tests use local fixtures and do not require network access.
