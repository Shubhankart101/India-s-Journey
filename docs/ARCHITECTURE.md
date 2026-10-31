# Architecture

```
                 scheduled GitHub Actions collectors (see PIPELINES.md)
                                    |
                                    v
            data/*.json  --->  docs/data/*.json  --->  GitHub Pages (static dashboard, backup)
                 |                                           ^
   scripts/export_catalog.mjs                                | links on every error page,
                 v                                           | footer, status page, outage issues
          data/catalog.json                                  |
                 |  manage.py import_catalog                 |
                 v                                           |
   +-------------------- Render (Docker) ------------------------------+
   |  gunicorn + Django 5 + DRF          whitenoise (static + SPA)     |
   |   /api/*       JSON API (drf-spectacular -> /api/docs/ Swagger)   |
   |   /accounts/*  django-allauth: Google, Microsoft (Outlook) only   |
   |   /admin/      Django admin (staff password login)                |
   |   /*           React + Vite SPA (frontend/dist)                   |
   |  SQLite (DJANGO_SQLITE_PATH, optional persistent disk)            |
   +-------------------------------------------------------------------+
                 ^ deployed from render.yaml (or any Docker host, see DEPLOYMENT.md)
```

## Components

| Path | Role |
| --- | --- |
| `scripts/`, `.github/workflows/*update*.yml` | Collectors that fetch official sources and write `data/` |
| `docs/` | Static GitHub Pages dashboard: Home, Explore, About, API, Status. Also the backup site |
| `scripts/export_catalog.mjs` | Evaluates the dashboard's chart definitions and writes `data/catalog.json` |
| `scripts/generate_art.py` | Generates the animated per-group and per-subgroup SVG illustrations into `docs/assets/` and `frontend/public/art/` |
| `frontend/src/components/ArtBackdrop.jsx` | Cross-fading, parallax page backdrop used by the Home, Explore, Indicator and About pages |
| `frontend/src/components/Motion.jsx` | Interaction layer: scroll progress, glassy header, scroll-in reveals, cursor spotlight, count-up stats, typewriter, subgroup marquee, back-to-top |
| `netlify.toml` | Publishes `docs/` on Netlify (no build step) |
| `webapp/journey/` | Django project: settings, root URLs, WSGI |
| `webapp/indicators/` | Models (Group, Subgroup, Indicator, Article, SavedChart), import commands, API views, OAuth adapters, error handlers |
| `webapp/templates/` | Server-rendered error pages and allauth overrides, all with backup links |
| `frontend/` | React 19 SPA (React Router, lazy-loaded Chart.js); Vitest unit tests and Playwright e2e tests |

## Request routing

| Path | Handled by |
| --- | --- |
| `/api/â€¦` | DRF views. Unknown `/api/*` paths return a JSON 404 even when `DEBUG` is on |
| `/api/docs/`, `/api/redoc/`, `/api/schema/` | Swagger UI, ReDoc, OpenAPI 3 schema. The UI assets come from `drf-spectacular-sidecar`, with no CDN |
| `/accounts/â€¦` | django-allauth. `/accounts/login/` and `/accounts/signup/` redirect to the SPA's `/login` |
| `/admin/` | Django admin |
| anything else | `frontend/dist/index.html`. React Router renders the page, or its own 404 |

## Key decisions

- **OAuth only.** There are no password hashes for site users. Login is a POST with CSRF, using PKCE and minimal scopes. See [AUTHENTICATION.md](AUTHENTICATION.md).
- **Session authentication with CSRF** for the SPA and Swagger. They share an origin, so no tokens are stored in the browser.
- **The schema view is serialized with a lock.** drf-spectacular's generator is not thread-safe under gunicorn threads.
- **The health endpoint is public and readable cross-origin** (`Access-Control-Allow-Origin: *`, `no-store`), so the static status page can call it. No other endpoint sends CORS headers.
- **Degradation is visible.** The offline banner, error boundary and error pages all point to the static backup, which uses the same data.
- **SQLite** keeps operations simple; the catalogue can be rebuilt from `data/catalog.json` on every boot. Only users and saved charts need persistence, which a Render disk provides.
