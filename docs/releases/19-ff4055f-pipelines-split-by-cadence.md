# Pipelines split by cadence

- **Commit:** [`ff4055f`](https://github.com/Shubhankart101/India-s-Journey/commit/ff4055f409965c34ff64e9febcdf9fa320a55c8c)
- **Commit message:** Split pipelines by dataset cadence, add official ECI election pies, FEC composition and World Bank layers
- **Date:** 2026-10-31
- **Size:** 48 files changed, +26157 / -12730 lines

## What it delivered

Separate pipelines per dataset cadence, official ECI election pies, FEC and World Bank layers.

### From the commit body

> - Lok Sabha 2024 from official ECI report 33; fix namesake dedupe so tallies match ECI
> - 112 election doughnut indices, 50 FEC funding-composition pies, 30 World Bank lines + 13 composition pies
> - Bar/Pie toggle and centre-total doughnuts across groups
> - Weekly Pew, monthly Economic Review and NCRB workflows; recent-elections job rebuilds pies
> - API, docs, README and tests updated; asset cache-buster bumped
> 
> Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## Where the change landed

| Area | Files |
|---|---|
| `docs` | 13 |
| `assets` | 12 |
| `.github` | 7 |
| `tests` | 6 |
| `scripts` | 5 |
| `data` | 4 |

## Largest additions

| File | Lines added |
|---|---|
| `data/chart-latest.json` | 7299 |
| `docs/data.js` | 7299 |
| `docs/data/chart-latest.json` | 7299 |
| `data/us-campaign-finance.json` | 1547 |
| `docs/data/us-campaign-finance.json` | 1547 |
| `scripts/build_election_indices.py` | 188 |

Previous: [Interactive composition charts](./18-0d94fdf-interactive-composition-charts.md)
