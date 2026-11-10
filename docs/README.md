# Project documentation

India's Journey is a React dashboard served in two ways: by Django with its REST API, and as a static build for Netlify and GitHub Pages. Both builds use the same React UI and data catalogue; the static build reads generated JSON snapshots from `docs/api/` and supporting data from `docs/data/`, `docs/maps/` and `docs/art/`.

Start with the [project overview](../README.md), browse the guides below, or open the [release history](releases/README.md).

<details open>
<summary>Data and interpretation</summary>

- [Sources and limitations](SOURCES-AND-LIMITATIONS.md): source-by-source coverage, definitions and caveats.
- [Election coverage](ELECTIONS.md): ECI results, the separate U.S. Elections group, FEC finance indicators, refreshes and gaps.
- [Tourism and heritage](TOURISM-AND-HERITAGE.md): World Bank visitor indicators and UNESCO inscription-date methods.
- [Sports, Cricket, Hockey and Football](SPORTS.md): official sources, past-vs-current player indices, refreshes and known gaps.

</details>

<details>
<summary>Atlases and infrastructure</summary>

- [India in Maps](INDIA-IN-MAPS.md): map data, interactions, themes and asset workflow.
- [Air travel and civil aviation](AIR-TRAVEL-AND-CIVIL-AVIATION.md): aviation indicators, sources and coverage.
- [Indian Railways](INDIAN-RAILWAYS.md): railway datasets and indicator methods.
- [Water transport](WATER-TRANSPORT.md): ports, shipping and inland-waterway coverage.
- [Logistics and freight](LOGISTICS-AND-FREIGHT.md): freight modes, infrastructure and comparisons.

</details>

<details>
<summary>Application and operations</summary>

- [Architecture](ARCHITECTURE.md): components, request routing and design decisions.
- [Architecture diagrams](diagrams/architecture.drawio): editable system diagrams.
- [API and Swagger](API.md): Django REST endpoints and static API snapshots.
- [Pipelines](PIPELINES.md): collection schedules, file flow, CI jobs and monitoring.
- [Deployment](DEPLOYMENT.md): static and web-app deployment instructions.
- [Static site and backup](BACKUP.md): Netlify, GitHub Pages and uptime monitoring.
- [Authentication](AUTHENTICATION.md): Google and Microsoft sign-in setup.
- [Testing](TESTING.md): Django, Vitest, Playwright and static-site suites.
- [Contributing](../CONTRIBUTING.md) and [Security](../SECURITY.md).

</details>

## Quick start

Build and preview the static React site from the repository root:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build:static
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. The build exports the static API snapshots from `data/catalog.json` into `docs/api/`. Legacy `.html` entry URLs redirect into the React app. To refresh live or historical election data locally, run the collectors documented in [Pipelines](PIPELINES.md).