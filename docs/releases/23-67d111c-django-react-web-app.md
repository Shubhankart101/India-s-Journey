# Django + React web app

- **Commit:** [`67d111c`](https://github.com/Shubhankart101/India-s-Journey/commit/67d111c125245528e48091018b434ec9797911ce)
- **Commit message:** Add Django + React web app with tests, CI and Render deploy
- **Date:** 2026-10-31
- **Size:** 79 files changed, +6829 / -3 lines

## What it delivered

Backend API, React frontend, tests, CI and deployment config.

### From the commit body

> - Django REST API (SQLite): indicators, search/filters, compare, downloads, auth, saved charts, admin
> - React (Vite) SPA: per-indicator pages, compare, accounts, mobile tab bar, lazy charts
> - Catalogue exporter bridges docs/ data into Django; scheduled workflows re-export it
> - 45 Django tests, 57 Vitest tests; webapp CI workflow; Dockerfile + render.yaml
> 
> Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## Where the change landed

| Area | Files |
|---|---|
| `frontend` | 42 |
| `webapp` | 25 |
| `(root)` | 5 |
| `.github` | 5 |
| `data` | 1 |
| `scripts` | 1 |

## Largest additions

| File | Lines added |
|---|---|
| `frontend/package-lock.json` | 2075 |
| `webapp/indicators/views.py` | 293 |
| `webapp/indicators/tests/test_api.py` | 253 |
| `frontend/src/pages/Indicator.jsx` | 222 |
| `webapp/indicators/catalog.py` | 222 |
| `scripts/export_catalog.mjs` | 216 |

Previous: [MOSPI mining layer](./22-6868f73-mospi-mining-layer.md)
