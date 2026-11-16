# Deployment

There are two deployments, plus a backup mirror:

| Target | How | Trigger |
| --- | --- | --- |
| **Static dashboard on Netlify** (primary, <https://indiasjourney.netlify.app>) | [`netlify.toml`](../netlify.toml) builds the React static site and publishes `docs/` | Every push to `main` |
| Backup mirror on GitHub Pages (<https://shubhankart101.github.io/India-s-Journey/>) | [`deploy-dashboard.yml`](../.github/workflows/deploy-dashboard.yml) publishes the same `docs/` | Push to `main`, or after any collector workflow |
| Django + React web app | The root [`Dockerfile`](../Dockerfile), deployed to Microsoft Azure ([`terraform/`](../terraform/)) | Azure: via [`.github/workflows/azure-deploy.yml`](../.github/workflows/azure-deploy.yml) or Terraform |

See [BACKUP.md](BACKUP.md) for how the app and the two static copies point to each other.

## Hosting the web app

The app is a single Docker image that listens on `$PORT`, so it runs on any container host. Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=<your-host>` and `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-host>`, plus the OAuth variables, and register `https://<your-host>/accounts/{google,microsoft}/login/callback/` with each provider (see [AUTHENTICATION.md](AUTHENTICATION.md)).

| Option | What you host | Tier | Trade-offs |
| --- | --- | --- | --- |
| **Netlify** (`netlify.toml`, live) | Static dashboard in `docs/` | Free static hosting | Static only; the primary public site |
| **GitHub Pages** (live) | Static dashboard in `docs/` | Free for public repositories | Static only; the backup mirror of Netlify |
| **Microsoft Azure** (`terraform/`) | Full app on Linux App Service B1 | Basic B1 tier (~Rs. 1,100/mo) | Persistent `/home` SSD storage, 1 vCPU, 1.75 GB RAM; fits well within Rs. 12,500/mo budget |

On Azure you don't need to set `DJANGO_ALLOWED_HOSTS` or `DJANGO_CSRF_TRUSTED_ORIGINS` for the default domain: `settings.py` adds `$WEBSITE_HOSTNAME` (`.azurewebsites.net`) and `.azurecontainerapps.io` automatically. Set them only for a custom domain.

### Microsoft Azure (Modular Terraform & CI/CD)

The Django + React app is deployed to Microsoft Azure Linux App Service (Basic B1 tier: 1 vCPU, 1.75 GB RAM) in `centralindia` (Pune) for approximately **Rs. 1,100 / month**, safely within a **Rs. 12,500 / month** budget.

Infrastructure is structured into clean reusable Terraform modules under [`terraform/modules/`](../terraform/modules/):
- `resource_group`: Centralized Azure Resource Group management
- `service_plan`: Linux App Service Plan with validated B1/B2 SKU
- `web_app`: Containerized Linux Web App with persistent `/home/data/` SQLite storage, health check at `/api/health/`, and gthread concurrency
- `budget`: Consumption budget safeguard enforcing the Rs. 12,500/mo limit with automated email notifications at 80% and 100%

1. Ensure Azure CLI (`az`) and Terraform (>= 1.5.0) are installed, and run `az login`.
2. Navigate to `terraform/` and run `terraform init` and `terraform apply` (or run `./scripts/azure-deploy.ps1`).
3. Automated continuous deployment runs via [`.github/workflows/azure-deploy.yml`](../.github/workflows/azure-deploy.yml) using your Azure Web App publish profile.




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
- **On start:** `migrate`, then `import_catalog --if-changed` (skipped when the baked catalogue is already loaded, so container cold starts wake in seconds instead of re-importing thousands of rows before gunicorn listens), then gunicorn with `$WEB_CONCURRENCY` workers (default 2; or configured in `webapp/gunicorn.conf.py`) on `$PORT`.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | A long random value |
| `DJANGO_DEBUG` | no (`false` in the image) | Never enable in production |
| `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` | for custom domains | Comma-separated. Render and Azure default domains are added automatically |
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
