# Project documentation

India's Journey is a React dashboard served in two ways: by Django with its REST API, and as a static build for Netlify and GitHub Pages. Both builds use the same React UI and data catalogue; the static build reads generated JSON snapshots from `docs/api/` and supporting data from `docs/data/`, `docs/maps/` and `docs/art/`.

**Data**
- [Election coverage](ELECTIONS.md): ECI results, the separate U.S. Elections group, FEC finance indicators, refreshes and coverage gaps.
- [Tourism and heritage](TOURISM-AND-HERITAGE.md): World Bank visitor indicators and UNESCO inscription-date methods.
- [Sources and limitations](SOURCES-AND-LIMITATIONS.md): source-by-source coverage for services, demographics, energy prices, and elections.
- [Pipelines and deployment](PIPELINES.md): collection schedules, file flow, CI jobs, monitoring, and failure behavior.
- [Sports, Cricket, Hockey and Football](SPORTS.md): official sources, past-vs-current player indices, the weekly sports refresh, and known gaps.

**Web app**
- [Architecture](ARCHITECTURE.md): components, request routing and design decisions.
- [Architecture diagrams](diagrams/architecture.drawio): five-page editable draw.io file.
- [APIs and Swagger](API.md): Django REST endpoints and the static API snapshots.
- [Authentication](AUTHENTICATION.md): Google and Microsoft sign-in setup.
- [Static site and backup](BACKUP.md): Netlify, GitHub Pages, and uptime monitoring.
- [Deployment](DEPLOYMENT.md): static and web-app deployment instructions.
- [Testing](TESTING.md): Django, Vitest, Playwright and static-site suites.
- [Contributing](../CONTRIBUTING.md), [Security](../SECURITY.md).

## Quick start

Build and preview the static React site from the repository root:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build:static
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. The build exports the static API snapshots from `data/catalog.json` into `docs/api/`. Legacy `.html` entry URLs redirect into the React app. To refresh live or historical election data locally, run the collectors documented in [Pipelines](PIPELINES.md).