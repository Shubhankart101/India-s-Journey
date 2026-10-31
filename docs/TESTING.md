# Testing

| Layer | Tool | Location | Command |
| --- | --- | --- | --- |
| Django API, auth, errors, Swagger | Django `TestCase` | [`webapp/indicators/tests/`](../webapp/indicators/tests) | `cd webapp && python manage.py test indicators` |
| OpenAPI schema | drf-spectacular | n/a | `cd webapp && python manage.py spectacular --validate --fail-on-warn --file openapi-schema.yml` |
| React components and flows | Vitest + Testing Library | `frontend/src/**/*.test.{js,jsx}` | `cd frontend && npm test` |
| Full stack in a real browser | Playwright (desktop Chrome + Pixel 7) | [`frontend/e2e/`](../frontend/e2e) | `cd frontend && npm run build && npm run test:e2e` |
| Static site and collectors | `unittest` | [`tests/`](../tests) | `python -m unittest discover -s tests` |

CI runs all of these. See [Pipelines](PIPELINES.md#continuous-integration).

## Backend suites

- **`test_api.py`**:
  - indicator list, search, filters, ordering and pagination;
  - detail pages with related indicators, comparison, and CSV/JSON downloads;
  - categories, stats and articles;
  - saved charts (requires sign-in, per-user isolation, CSRF);
  - the SPA fallback.
- **`test_oauth.py`**:
  - only Google and Microsoft are offered, and only when configured, either through the environment or an admin `SocialApp`;
  - an unconfigured provider redirects to `/login`;
  - a POST with CSRF is required, a GET does not start a login, and every attempt gets a fresh `state`;
  - the authorize URLs use PKCE and `select_account`; the Microsoft tenant is configurable;
  - Google and Microsoft callbacks are simulated end to end (token exchange, profile), creating a user and returning to `next`; an off-site `next` is ignored;
  - returning users get the same account; a verified Google email links an existing account; an unverified Microsoft email **never** takes one over;
  - state mismatch, token-exchange failure, profile failure and user cancellation each show the error page;
  - password signup, password login and password reset are impossible, and the allauth login and signup pages redirect to the SPA.
- **`test_docs_and_errors.py`**:
  - the schema covers exactly the 15 API paths, and documented parameters and responses match the live payloads;
  - every documented GET endpoint responds;
  - Swagger UI and ReDoc are served from local static files (no CDN);
  - HTML and JSON 404/403/500/503 pages carry the backup links;
  - hostile input, pagination limits, 405s, gzip, cookie flags and clickjacking headers;
  - concurrent schema requests succeed;
  - CORS is enabled only on `/api/health/`.
- **`test_catalog.py`**: `import_catalog` and `refresh_data`:
  - re-imports are idempotent, keep saved charts and prune stale indicators;
  - duplicate keys roll back the whole import;
  - non-numeric values, downsampled previews and date parsing are handled;
  - the repository's own `data/catalog.json` imports.

## Frontend suites

- `pages.test.jsx`: each page renders, plus empty, loading and error states.
- `flows.test.jsx`: filters synced to the URL; compare and save flows; OAuth-only sign-in (POST forms, CSRF field, safe `next`, error messages, no password fields).
- `api-and-charts.test.jsx`: the API client (CSRF, errors, the `api:unreachable` event) and chart data shaping.
- `format.test.js`: Indian vs. international number formatting.
- `resilience.test.jsx`: `ErrorBoundary`, `OfflineBanner` and the backup links.

## End-to-end

`playwright.config.js` starts Django in **production mode** (`DJANGO_DEBUG=0`) on port 8010. It runs from a temporary SQLite database with the catalogue imported and dummy OAuth client IDs. The suites are:

- `site.spec.js`:
  - home, explore (search survives a reload), indicator chart with CSV download, compare, and deep links on hard refresh;
  - SPA 404, JSON API 404 and server-rendered pages all link to the backup site;
  - health check.
- `auth.spec.js`:
  - exactly two OAuth buttons and no password form; each button reaches the provider's authorize URL, checked through the `Location` header without leaving the test;
  - password endpoints don't exist, and allauth login/signup redirect to the SPA;
  - saved charts require sign-in.
- `swagger.spec.js`: Swagger UI lists the endpoints and executes a live request; ReDoc and the raw schema are served.
- `responsive.spec.js`: tab bar on mobile and top navigation on desktop; no page scrolls sideways.

Set `E2E_BASE_URL=https://staging.example` to run the suites against a deployed app instead. Use `PYTHON=python3` to choose the interpreter.

## Testing the API by hand

Open `/api/docs/` (Swagger UI). Every operation has *Try it out* enabled, and the CSRF header is sent automatically, so the saved-chart endpoints work once you are signed in. ReDoc is at `/api/redoc/` and the raw schema at `/api/schema/`.
