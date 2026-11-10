# APIs and Swagger UI

The project has two APIs:

1. The **Django REST API** of the web app, with interactive **Swagger UI at `/api/docs/`**. See the next section.
2. **Static JSON resources** on the Netlify site (mirrored on GitHub Pages), documented with their own Swagger UI at [`api.html`](api.html). This is also the API of the backup site.

## Web app REST API (`/api/`)

| Tool | URL |
| --- | --- |
| API overview page | `/api` |
| Swagger UI (try every endpoint) | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI 3 schema (YAML; add `?format=json` for JSON) | `/api/schema/` |
| Index of endpoints, with docs and backup links | `/api/` |

Swagger UI has *Try it out* enabled for every operation, and its UI assets are served locally by `drf-spectacular-sidecar`. It sends the session cookie and CSRF header automatically. The web app's sign-in and saved-chart UI is currently disabled; the backend session endpoints remain available for a future release.

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
`{"detail": "Not found.", "backup_url": "https://indiasjourney.netlify.app/"}`.
Lists are paginated (`count`, `next`, `previous`, `results`), with at most 100 items per page.

`test_docs_and_errors.py` checks that the schema documents exactly these paths and that the documented response fields match the real payloads. CI also runs `manage.py spectacular --validate --fail-on-warn`.

## Static API (Netlify and GitHub Pages)

The static site uses the same React API client as Django. During `npm run build:static`, `scripts/export_static_api.mjs` writes `categories.json`, `indicators.json`, `articles.json`, `search-index.json`, `stats.json`, and legacy group aliases under `docs/api/`. The client fetches these snapshots and applies search, filters, sorting, pagination, indicator detail, compare, and downloads in the browser. Results are derived from the same `data/catalog.json` used by Django; static snapshots update on deployment.

Supporting source datasets and map assets remain available under `docs/data/`, `docs/maps/`, and `docs/art/`. The old `/api.html` and other legacy pages are small redirects; the React API page is at `/#/api` on the static hosts. The Django Swagger UI remains available only on the web app at `/api/docs/`.

## Local preview

From the repository root, build and serve the static site:

```powershell
npm.cmd --prefix frontend run build:static
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/#/api`. Static-site tests verify that the generated snapshots and legacy redirect stubs are present.