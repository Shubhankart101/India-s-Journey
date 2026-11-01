# Static site and backup

India's Journey has two deployments:

| What | Where | Role |
| --- | --- | --- |
| **Static dashboard** (`docs/`) | **Netlify: <https://indiasjourney.netlify.app>** | The public site, and the fallback when the web app is down |
| Backup mirror of the static dashboard | GitHub Pages: <https://shubhankart101.github.io/India-s-Journey/> | An identical copy of the Netlify site, used if Netlify is unavailable |
| Django + React web app | Runs locally (or on any Docker host) | Explore, Compare, Sources, API and Swagger |

Netlify publishes `docs/` as-is ([`netlify.toml`](../netlify.toml)). [`deploy-dashboard.yml`](../.github/workflows/deploy-dashboard.yml) publishes the same `docs/` folder to GitHub Pages. Both copies are built from the same collectors and `docs/data/*.json` files, so they always show the same data as the app.

## Where the web app sends users

| Situation | What the user sees |
| --- | --- |
| Django error (404, 403, 500, 503), HTML request | `templates/errors/error.html`, with **Open the backup dashboard** (Netlify) and **GitHub Pages mirror** links |
| Django error, `/api/*` or JSON request | JSON `{"detail": ..., "backup_url": ...}` |
| React route crashes | `ErrorBoundary`, with "Open backup site" and "Reload" buttons |
| API unreachable, or 502/503/504 | `OfflineBanner` at the top of every page, plus backup links in `ErrorState` |
| Browser offline | `OfflineBanner` |
| Unknown front-end route | `NotFound` page with backup links |

The app's footer always links to **Backup site** (Netlify) and **Mirror** (GitHub Pages).

## Configuration

| Setting | Default | Used by |
| --- | --- | --- |
| `BACKUP_SITE_URL` (Django) | `https://indiasjourney.netlify.app/` | Error templates, JSON errors, `/api/` index, `/api/health/` |
| `BACKUP_MIRROR_URL` (Django) | `https://shubhankart101.github.io/India-s-Journey/` | Error templates |
| `VITE_BACKUP_URL` / `VITE_BACKUP_MIRROR_URL` (build time) | Same as above | React `BackupLinks`, `ErrorBoundary`, `OfflineBanner`, footer |

## Uptime monitor

[`uptime-monitor.yml`](../.github/workflows/uptime-monitor.yml) runs every 30 minutes and can also be started by hand:

1. It requests the Netlify site and the GitHub Pages mirror up to five times each, 20 s apart, so a brief CDN hiccup is not reported as an outage.
2. If any site fails every attempt, it opens an issue labelled `outage` listing the failed sites, with links to both copies. If such an issue is already open, it adds a comment instead.
3. When every site is healthy again, it closes the open outage issues with a recovery comment.

The Django app runs locally, so it is not checked on schedule. To check a hosted copy, start the workflow by hand (**Actions → Uptime monitor → Run workflow**) and fill in `app_url`; it then also requests `<app_url>/api/health/`. No repository variables are needed, and the workflow creates the `outage` label on first use if it is missing.
