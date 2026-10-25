# Project documentation

India's Journey is a static, source-linked dashboard. This documentation distinguishes automatically refreshed observations from snapshots and from data that is not yet available as a reproducible public series.

- [Election coverage](ELECTIONS.md): included ECI and U.S. National Archives series, refreshes, provisional status, and historical / House data gaps.
- [Sources and limitations](SOURCES-AND-LIMITATIONS.md): source-by-source coverage for services, demographics, energy prices, and elections.
- [Pipelines and deployment](PIPELINES.md): collection schedules, file flow, deployment, and failure behavior.

## Quick start

From the repository root, preview the site with:

```powershell
python -m http.server 8000 --directory docs
```

The live dashboard reads generated public data from `docs/data/` or the deployed `data/` directory. To refresh election data locally, run:

```powershell
python scripts/collect_election_results.py
```

The collector uses only the Python standard library and writes `data/election-results.json`.
