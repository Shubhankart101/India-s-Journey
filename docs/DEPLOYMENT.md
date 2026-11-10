# Deployment

There are two deployments, plus a backup mirror:

| Target | How | Trigger |
| --- | --- | --- |
| **Static dashboard on Netlify** (primary, <https://indiasjourney.netlify.app>) | [`netlify.toml`](../netlify.toml) builds the React static site and publishes `docs/` | Every push to `main` |
| Backup mirror on GitHub Pages (<https://shubhankart101.github.io/India-s-Journey/>) | [`deploy-dashboard.yml`](../.github/workflows/deploy-dashboard.yml) publishes the same `docs/` | Push to `main`, or after any collector workflow |
| Django + React web app | The root [`Dockerfile`](../Dockerfile), deployed to Render ([`render.yaml`](../render.yaml)), Fly.io ([`fly.toml`](../fly.toml)) or any container host | Render: auto on push (live host). Fly.io: paused; [`fly-deploy.yml`](../.github/workflows/fly-deploy.yml) is manual-only |

See [BACKUP.md](BACKUP.md) for how the app and the two static copies point to each other.

## Hosting the web app (optional)

The app is a single Docker image that listens on `$PORT`, so it runs on any container host. Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=<your-host>` and `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-host>`, plus the OAuth variables, and register `https://<your-host>/accounts/{google,microsoft}/login/callback/` with each provider (see [AUTHENTICATION.md](AUTHENTICATION.md)). Free tiers change often; check each provider's current limits before relying on them.

| Option | What you host | Free tier (Oct 2026) | Trade-offs |
| --- | --- | --- | --- |
| **Netlify** (`netlify.toml`, live) | Static dashboard in `docs/` | Free static hosting | Static only; the primary public site |
| **GitHub Pages** (live) | Static dashboard in `docs/` | Free for public repositories | Static only; the backup mirror of Netlify |
| **Google Cloud Run** | Full app from the `Dockerfile` | Monthly free request/CPU allowance | Scales to zero (cold starts); needs a billing account; `/tmp` storage only |
| **Render** (`render.yaml`) | Full app from the `Dockerfile` | Free web service: 512 MB RAM, 0.1 CPU, 750 instance-hours/month | Sleeps after 15 minutes idle (~1 minute cold start); no disk on the free plan |
| **Fly.io** (`fly.toml`) | Full app from the `Dockerfile` | Trial credit only for new accounts; then pay-as-you-go | Card required; machines stop when idle, so a 512 MB machine costs only while it runs |

On Render and Fly.io you don't need to set `DJANGO_ALLOWED_HOSTS` or `DJANGO_CSRF_TRUSTED_ORIGINS` for the default domain: `settings.py` adds `$RENDER_EXTERNAL_HOSTNAME` and `$FLY_APP_NAME.fly.dev` automatically. Set them only for a custom domain.

### Render (live web app)

The live Django + React app runs on Render's free plan because the Fly.io trial credit ran out. One-click setup:

<a href="https://render.com/deploy?repo=https://github.com/Shubhankart101/India-s-Journey"><img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render"></a>

1. In Render, choose **New → Blueprint** (or click the button above), connect this repository and pick `main`. Render reads [`render.yaml`](../render.yaml) and creates the `indias-journey` web service on the free plan, with a generated `DJANGO_SECRET_KEY`. No card is required.
2. Wait for the first build (about 5–8 minutes) and open `https://indias-journey.onrender.com` (Render adds a suffix if the name is taken; update `WEB_APP_URL` in `frontend/src/config.js` and the static footers if so).
3. Later pushes redeploy automatically, but only when `Dockerfile`, `webapp/`, `frontend/` or `data/catalog.json` change, so the frequent static-site and collector commits don't use up the free build minutes.
4. The free service sleeps after 15 idle minutes; the React client retries gateway errors while it wakes, and the static site on Netlify/GitHub Pages stays up regardless.

To deploy without the blueprint: **New → Web Service**, choose the repo, runtime **Docker**, plan **Free**, health check path `/api/health/`, and add `DJANGO_SECRET_KEY` and `WEB_CONCURRENCY=1`.

### Fly.io (paused)

Fly.io is no longer the live host: the trial credit is used up, so [`fly-deploy.yml`](../.github/workflows/fly-deploy.yml) now runs only when triggered manually. The steps below still work if the account is topped up.

<a href="https://india-s-journey.fly.dev"><img src="https://img.shields.io/badge/Open%20the%20web%20app%20on%20Fly.io-8B5CF6?style=for-the-badge&logo=flydotio&logoColor=white" alt="Open the web app on Fly.io"></a>

The Django + React app is deployed at <https://india-s-journey.fly.dev> on the existing `india-s-journey` app in Singapore (`sin`). Its machine is `shared-cpu-1x` with 512 MB RAM; `fly.toml` is configured to match.

1. Install `flyctl` (`iwr https://fly.io/install.ps1 -useb | iex` on Windows, or `curl -L https://fly.io/install.sh | sh`) and authenticate with `fly auth login`.
2. From the repository root, verify access to the existing app with `fly status --app india-s-journey`. Do not run `fly launch`; that would create a different app.
3. Ensure the app has a `DJANGO_SECRET_KEY` secret. If needed, generate a value with `python -c "import secrets; print(secrets.token_urlsafe(50))"`, then set it with `fly secrets set DJANGO_SECRET_KEY=<generated-value> --app india-s-journey`. Never commit or publish the value.
4. Deploy with `fly deploy --app india-s-journey`. The configuration keeps the machine in `sin` and at 512 MB.
5. The `/api/health/` check sends `Host = "india-s-journey.fly.dev"`. Fly runs service checks over the private network using the machine IP as the host; setting the public hostname lets Django validate the request without allowing arbitrary hosts.
6. To deploy from Actions, run `fly tokens create deploy`, save the token as the repository secret `FLY_API_TOKEN`, and trigger [`fly-deploy.yml`](../.github/workflows/fly-deploy.yml) manually (it no longer runs on push).

### Netlify

The static React dashboard is live at **<https://indiasjourney.netlify.app>** and mirrored on GitHub Pages. It uses the same React application as Django, with static API snapshots generated into `docs/api/` during deployment. Internal routes use hash-based URLs, so both hosts can serve the site without route rewrites; the legacy `.html` pages redirect old bookmarks into the app.

[`netlify.toml`](../netlify.toml) runs `npm ci --prefix frontend` and `npm run build:static --prefix frontend`, then publishes `docs/`. Configure new Netlify sites with an empty base directory; the repository config supplies the build and publish settings. The Pages workflow runs the same static build before deployment.
**Persistent data on free tiers.** None of these free plans keeps a disk, so SQLite (user accounts and saved charts) resets on redeploy or restart. The indicator catalogue is re-imported on every start, so the dashboards are unaffected.

**Cloud Run example:**

```bash
gcloud run deploy indias-journey --source . --region asia-south1 --allow-unauthenticated \
  --set-env-vars DJANGO_ALLOWED_HOSTS=<service>.run.app,DJANGO_CSRF_TRUSTED_ORIGINS=https://<service>.run.app,DJANGO_SECRET_KEY=<random>
```

## The container

- **Stage 1:** `node:22-slim` builds the React app with `npm ci` and `npm run build`.
- **Stage 2:** `python:3.12-slim` installs the Django requirements, runs `collectstatic` (whitenoise, compressed and hashed), and bakes `data/catalog.json` into the image's SQLite database (`migrate` + `import_catalog`).
- **On start:** `migrate`, then `import_catalog --if-changed` (skipped when the baked catalogue is already loaded, so a stopped Fly.io machine wakes in seconds instead of re-importing thousands of rows before gunicorn listens), then gunicorn with `$WEB_CONCURRENCY` workers (default 2; Render and Fly.io set 1) on `$PORT`.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | A long random value |
| `DJANGO_DEBUG` | no (`false` in the image) | Never enable in production |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | for custom domains | Comma-separated. Render and Fly.io default domains are added automatically |
| `WEB_CONCURRENCY` | no (`2` in the image) | Gunicorn workers; use `1` on 512 MB plans |
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
