# Project documentation

India's Journey has two parts: a static, source-linked dashboard on Netlify at <https://indiasjourney.netlify.app> (with a GitHub Pages backup mirror), and a Django + React web app built from the same data. The static site also serves as the backup when the app is down. This documentation distinguishes automatically refreshed observations from snapshots and from data that is not yet available as a reproducible public series.

**Data**
- [Election coverage](ELECTIONS.md): ECI results, the separate U.S. Elections group, FEC finance indicators, refreshes and coverage gaps.
- [Tourism and heritage](TOURISM-AND-HERITAGE.md): World Bank visitor indicators and UNESCO inscription-date methods.
- [Sources and limitations](SOURCES-AND-LIMITATIONS.md): source-by-source coverage for services, demographics, energy prices, and elections.
- [Pipelines and deployment](PIPELINES.md): collection schedules, file flow, CI jobs, monitoring, and failure behavior.
- [Sports, Cricket, Hockey and Football](SPORTS.md): official sources, past-vs-current player indices, the weekly sports refresh, and known gaps.

**Web app**
- [Architecture](ARCHITECTURE.md): components, request routing and design decisions.
- [Architecture diagrams](diagrams/architecture.drawio): five-page editable draw.io file (overview, pipeline, static site, web app, deployment).
- [APIs and Swagger](API.md): the Django REST API (Swagger at `/api/docs/`) and the static JSON resources.
- [Authentication](AUTHENTICATION.md): Google and Microsoft (Outlook) sign-in only, and how to set up each provider.
- [Static site and backup](BACKUP.md): Netlify as the primary static site, the GitHub Pages mirror, how the app links to them, and the uptime monitor.
- [Deployment](DEPLOYMENT.md): Netlify, the GitHub Pages backup, optional app hosting, environment variables and post-deploy checks.
- [Testing](TESTING.md): Django, Vitest, Playwright and static-site suites.
- [Contributing](../CONTRIBUTING.md), [Security](../SECURITY.md).

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
