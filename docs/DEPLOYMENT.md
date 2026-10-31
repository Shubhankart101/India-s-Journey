# Deployment

There are two deployments, plus a backup mirror:

| Target | How | Trigger |
| --- | --- | --- |
| **Static dashboard on Netlify** (primary, <https://indiasjourney.netlify.app>) | [`netlify.toml`](../netlify.toml) publishes `docs/` as-is | Every push to `main` |
| Backup mirror on GitHub Pages (<https://shubhankart101.github.io/India-s-Journey/>) | [`deploy-dashboard.yml`](../.github/workflows/deploy-dashboard.yml) publishes the same `docs/` | Push to `main`, or after any collector workflow |
| Django + React web app | Runs locally; optionally deploy the root [`Dockerfile`](../Dockerfile) to any container host | Manual |

See [BACKUP.md](BACKUP.md) for how the app and the two static copies point to each other.

## Hosting the web app (optional)

The app is a single Docker image that listens on `$PORT`, so it runs on any container host. Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=<your-host>` and `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-host>`, plus the OAuth variables, and register `https://<your-host>/accounts/{google,microsoft}/login/callback/` with each provider (see [AUTHENTICATION.md](AUTHENTICATION.md)). Free tiers change often; check each provider's current limits before relying on them.

| Option | What you host | Free tier (Oct 2026) | Trade-offs |
| --- | --- | --- | --- |
| **Netlify** (`netlify.toml`, live) | Static dashboard in `docs/` | Free static hosting | Static only; the primary public site |
| **GitHub Pages** (live) | Static dashboard in `docs/` | Free for public repositories | Static only; the backup mirror of Netlify |
| **Google Cloud Run** | Full app from the `Dockerfile` | Monthly free request/CPU allowance | Scales to zero (cold starts); needs a billing account; `/tmp` storage only |
### Netlify

The static dashboard is live at **<https://indiasjourney.netlify.app>** (Home, [Explore](https://indiasjourney.netlify.app/explore.html), [About](https://indiasjourney.netlify.app/about.html), [API](https://indiasjourney.netlify.app/api.html)). Every push to `main` redeploys it, and GitHub Pages mirrors it as the backup.

The repository root has no `index.html`, so Netlify needs to be told to publish `docs/`. Otherwise every URL shows Netlify's "Page not found". [`netlify.toml`](../netlify.toml) does this. It has no build command, adds a few security and cache headers, and `docs/404.html` serves as the not-found page.

1. In Netlify, choose **Add new site → Import an existing project**, pick this repository and the `main` branch. Leave the build command empty; `netlify.toml` supplies `publish = "docs"`.
2. If the site already exists, open **Site configuration → Build & deploy → Build settings** and make sure **Base directory** is empty and **Publish directory** is `docs`. Values set in the UI are overridden by `netlify.toml`. Then choose **Deploys → Trigger deploy → Clear cache and deploy site**.
3. New sites can start as **Private**: visitors get a password page or a 401. Choose **Make public** (or **Site configuration → Access & security → Visitor access**) to open it to everyone.

Netlify serves the static dashboard only. Sign-in, Compare, Saved and Swagger need the Django app, so it runs locally or on a container host.

Fly.io and Railway now offer only trial credit, and PythonAnywhere's free plan doesn't run Docker, so they are not listed.

**Persistent data on free tiers.** None of these free plans keeps a disk, so SQLite (user accounts and saved charts) resets on redeploy or restart. The indicator catalogue is re-imported on every start, so the dashboards are unaffected.

**Cloud Run example:**

```bash
gcloud run deploy indias-journey --source . --region asia-south1 --allow-unauthenticated \
  --set-env-vars DJANGO_ALLOWED_HOSTS=<service>.run.app,DJANGO_CSRF_TRUSTED_ORIGINS=https://<service>.run.app,DJANGO_SECRET_KEY=<random>
```

## The container

- **Stage 1:** `node:22-slim` builds the React app with `npm ci` and `npm run build`.
- **Stage 2:** `python:3.12-slim` installs the Django requirements and runs `collectstatic` (whitenoise, compressed and hashed).
- **On start:** `migrate`, then `import_catalog`, then gunicorn with 2 workers on `$PORT`.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | A long random value |
| `DJANGO_DEBUG` | no (`false` in the image) | Never enable in production |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | for custom domains | Comma-separated |
| `DJANGO_SQLITE_PATH` | with a disk | e.g. `/var/data/db.sqlite3`, so accounts survive redeploys |
| `DJANGO_SECURE_COOKIES` | no (default on when not DEBUG) | Secure session and CSRF cookies |
| `GOOGLE_CLIENT_ID` / `_SECRET` | to enable Google | |
| `MICROSOFT_CLIENT_ID` / `_SECRET`, `MICROSOFT_TENANT` | to enable Microsoft | The tenant defaults to `common` |
| `BACKUP_SITE_URL`, `BACKUP_MIRROR_URL` | no | Netlify backup and GitHub Pages mirror links on the error pages |
| `DJANGO_LOG_LEVEL` | no | Default `INFO` |

## After deploying

- `curl https://<host>/api/health/` returns `{"status": "ok", ...}`.
- `/api/docs/` loads Swagger UI.
- `/login` shows the configured provider buttons.
- Run the e2e suite against the deployment: `E2E_BASE_URL=https://<host> npx playwright test`.

## Outages

- Unplanned outages: the [uptime monitor](../.github/workflows/uptime-monitor.yml) checks Netlify and the GitHub Pages mirror, opens an `outage` issue and closes it on recovery. See [BACKUP.md](BACKUP.md).
- Free container plans reset SQLite on every deploy. Use a host with a persistent disk and set `DJANGO_SQLITE_PATH` to keep user accounts and saved charts.
