# All States and UTs via RBI handbook

- **Commit:** [`617d61c`](https://github.com/Shubhankart101/India-s-Journey/commit/617d61c60ee14958230548554b82bdde35919381)
- **Commit message:** Cover all States/UTs via RBI handbook layer; expand election indices
- **Date:** 2026-10-31
- **Size:** 17 files changed, +29102 / -3855 lines

## What it delivered

RBI Handbook layer covering every State/UT; expanded election indices.

### From the commit body

> - Add scripts/rbi_state_layer.py: generic RBI State handbook parser producing
>   ~140 all-State/UT rankings, regional/band pies and All-India trends for
>   Payments & Banking, Public Health, Social and State Performance
> - Root cause: 28-State whitelist and hand-typed partial lists dropped UTs;
>   notes now report coverage out of 36 States/UTs
> - Fix PMJDY name matching (now 36/36)
> - Elections: 112 -> 208 indices incl. cross-state comparisons
> - Tests and docs updated
> 
> Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## Where the change landed

| Area | Files |
|---|---|
| `docs` | 6 |
| `scripts` | 4 |
| `data` | 3 |
| `tests` | 3 |
| `(root)` | 1 |

## Largest additions

| File | Lines added |
|---|---|
| `data/chart-latest.json` | 8704 |
| `docs/data.js` | 8704 |
| `docs/data/chart-latest.json` | 8704 |
| `docs/app.js` | 2118 |
| `scripts/rbi_state_layer.py` | 635 |
| `scripts/build_election_indices.py` | 83 |

Previous: [Django + React web app](./23-67d111c-django-react-web-app.md)
