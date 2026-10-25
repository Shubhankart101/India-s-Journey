# Project documentation

India's Journey is a static, source-linked dashboard. This documentation distinguishes automatically refreshed observations from snapshots and from data that is not yet available as a reproducible public series.

- [Election coverage](ELECTIONS.md): ECI results, the separate U.S. Elections group, FEC finance indicators, refreshes and coverage gaps.
- [Tourism and heritage](TOURISM-AND-HERITAGE.md): World Bank visitor indicators and UNESCO inscription-date methods.
- [Public data API](API.md): documented static JSON resources, Swagger UI, and endpoint checks.
- [Sources and limitations](SOURCES-AND-LIMITATIONS.md): source-by-source coverage for services, demographics, energy prices, and elections.
- [Pipelines and deployment](PIPELINES.md): collection schedules, file flow, deployment, and failure behavior.

## Quick start

From the repository root, preview the site with:

```powershell
python -m http.server 8000 --directory docs
```

The live dashboard reads generated public data from `docs/data/` or the deployed `data/` directory. To refresh live or historical election data locally, run:

```powershell
python scripts/collect_election_results.py
python scripts/collect_historical_elections.py
```

Both election collectors use only the Python standard library. The historical archive reader is deliberately limited to parseable, public ECI detailed-result XLSX workbooks; its observed coverage is published with the output.

For a local API/UI preview, run `python -m http.server 8000 --directory docs` and open `http://localhost:8000/api.html`. The 20,000-word-per-group-and-subgroup article target is not represented as completed content: that volume requires a separate, source-by-source editorial process, and the dashboard does not generate repetitive filler to claim a word-count target.
