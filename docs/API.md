# APIs and Swagger UI

The project has two APIs:

1. The **Django REST API** of the web app, with interactive **Swagger UI at `/api/docs/`**. See the next section.
2. **Static JSON resources** on GitHub Pages, documented with their own Swagger UI at [`api.html`](api.html). This is also the API of the backup site.

## Web app REST API (`/api/`)

| Tool | URL |
| --- | --- |
| Swagger UI (try every endpoint) | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI 3 schema (YAML; add `?format=json` for JSON) | `/api/schema/` |
| Index of endpoints, with docs and backup links | `/api/` |

Swagger UI has *Try it out* enabled for every operation, and its UI assets are served locally by `drf-spectacular-sidecar`. It sends the session cookie and CSRF header automatically. To call the saved-chart endpoints from Swagger, sign in at `/login` in the same browser first.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/health/` | public, CORS `*` | Liveness check: `{"status": "ok", "indicators": n, "backup_url": ...}` |
| GET | `/api/stats/` | public | Catalogue totals and last refresh |
| GET | `/api/categories/` | public | Groups with subgroup counts |
| GET | `/api/indicators/` | public | Search and filter (`q`, `category`, `subgroup`, `chart`, `live`, `sort`, `page`, `page_size` ≤ 100) |
| GET | `/api/indicators/{key}/` | public | Full series with related indicators |
| GET | `/api/indicators/{key}/download/?format=csv\|json` | public | File download |
| GET | `/api/compare/?keys=a,b,c` | public | Up to four aligned series |
| GET | `/api/articles/` | public | Articles and reports (`kind`, `q`) |
| GET | `/api/auth/providers/` | public | Configured sign-in providers (Google, Microsoft) with their login URLs |
| GET | `/api/auth/csrf/` | public | Sets the `csrftoken` cookie |
| GET | `/api/auth/me/` | public | The current user, or `null` |
| POST | `/api/auth/logout/` | session + CSRF | Sign out |
| GET, POST | `/api/saved/` | session (+ CSRF for POST) | List or save charts |
| DELETE | `/api/saved/{key}/` | session + CSRF | Remove a saved chart |

Sign-in itself happens outside the JSON API: a POST to `/accounts/{google,microsoft}/login/` starts the OAuth redirect. See [AUTHENTICATION.md](AUTHENTICATION.md).

Errors are always JSON under `/api/`, including unknown paths:
`{"detail": "...", "status_code": 404, "backup_site": "https://shubhankart101.github.io/India-s-Journey/", "status_page": ".../status.html"}`.
Lists are paginated (`count`, `next`, `previous`, `results`), with at most 100 items per page.

`test_docs_and_errors.py` checks that the schema documents exactly these paths and that the documented response fields match the real payloads. CI also runs `manage.py spectacular --validate --fail-on-warn`.

## Static JSON resources (GitHub Pages)

This section documents the static GitHub Pages project, which has no backend. The Swagger UI at [`api.html`](api.html) documents read-only `GET` access to the project's JSON files. It does not expose mutation endpoints or guarantee an API service-level objective.

## Interactive checks

1. Open the [API explorer](api.html).
2. Choose **Run all endpoint checks** to fetch every documented JSON file from the current deployment and validate its JSON response.
3. Expand an operation in Swagger UI and choose **Try it out** for an individual resource.

## Documented resources

| Resource | Contents |
| --- | --- |
| `/data/chart-latest.json` | Generated chart series and provenance |
| `/data/election-results.json` | Current ECI and U.S. election snapshots |
| `/data/historical-elections.json` | Candidate-level records parsed from available ECI workbooks; partial coverage |
| `/data/recent-indian-elections.json` | 2024 Lok Sabha results for all 543 seats plus recent Assembly elections, 2022?2026 |
| `/data/us-campaign-finance.json` | FEC candidate-finance aggregates for Presidential and Congressional candidates across five filing cycles, 2018?2026 |
| `/data/election-indices.json` | 112 Lok Sabha 2024 and State Assembly seat/vote doughnut indices derived from official ECI results, each with a `meta` block |
| `/data/economic-survey-monthly.json` | Monthly indicators collated from Economic Survey tables |
| `/data/ncrb-and-analyses.json` | NCRB and public-safety data |
| `/data/pew-india-reports.json` | Public Pew India report catalog |
| `/data/pew-snapshots.json` | Dated survey snapshots |
| `/data/indian-matrix-latest.json` | Public Indian Matrix article feed |
| `/data/substack-latest.json` | Public Polity and Policy article feed |

The OpenAPI source is [`openapi.json`](openapi.json). Tests check that every specification path maps to a parseable source JSON file and that the deployment copy matches it. The automated daily endpoint workflow also exercises the deployed dashboard and live-source checks.

## Local preview

From the repository root, run `python -m http.server 8000 --directory docs`, then open `http://localhost:8000/api.html`. The Swagger specification's server URL points to the public GitHub Pages deployment; the on-page all-resource check uses the local `data/` directory when served locally.
