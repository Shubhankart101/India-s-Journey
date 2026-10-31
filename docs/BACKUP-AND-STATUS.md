# Backup site and status page

The Django app runs on Render. If it is down, asleep (free plan) or being deployed, visitors can still use the **static GitHub Pages dashboard** at <https://shubhankart101.github.io/India-s-Journey/>, mirrored on Netlify at <https://indiasjourney.netlify.app>. Both are built from the same collectors and the same `docs/data/*.json` files, so the backup always has the same data as the app.

## Where users are sent to the backup

| Situation | What the user sees |
| --- | --- |
| Django error (404, 403, 500, 503), HTML request | `templates/errors/error.html`, with **Open the backup dashboard** and **Check app status** links |
| Django error, `/api/*` or JSON request | JSON `{"detail": ..., "status_code": ..., "backup_site": ..., "status_page": ...}` |
| React route crashes | `ErrorBoundary`, with "Open backup site" and "Reload" buttons |
| API unreachable, or 502/503/504 | `OfflineBanner` at the top of every page, plus backup links in `ErrorState` |
| Browser offline | `OfflineBanner` |
| Unknown front-end route | `NotFound` page with backup links |
| Render maintenance mode | Render redirects every request to `BACKUP_SITE_URL` (Render dashboard: **Settings ? Maintenance mode**) |
| The whole host is unreachable | The [uptime monitor](../.github/workflows/uptime-monitor.yml) opens an `outage` issue that links to the backup |

The app's footer always links to **Backup site** and **Status**.

## Configuration

| Setting | Default | Used by |
| --- | --- | --- |
| `BACKUP_SITE_URL` (Django) | `https://shubhankart101.github.io/India-s-Journey/` | Error templates, JSON errors, `/api/` index |
| `BACKUP_STATUS_URL` (Django) | `<BACKUP_SITE_URL>/status.html` | Error templates and JSON |
| `VITE_BACKUP_URL` / `VITE_BACKUP_STATUS_URL` (build time) | Same as above | React `BackupLinks`, `ErrorBoundary`, `OfflineBanner` |

## Status page

[`docs/status.html`](status.html) is deployed with the Pages site. It calls the app's `GET /api/health/` from the browser; that endpoint allows any origin and is never cached. It shows one of three states:
- **Up**: includes the response time and catalogue size;
- **Slow / waking up**: a free-tier cold start;
- **Down**.

It also links to open `outage` issues. Use `status.html?app=https://your-host` to check a different deployment.

## Uptime monitor

[`uptime-monitor.yml`](../.github/workflows/uptime-monitor.yml) runs every 30 minutes and can also be started by hand:

1. It requests `${APP_URL}/api/health/` up to five times, 20 s apart, so a cold start is not reported as an outage.
2. If every attempt fails, it opens an issue labelled `outage` with links to the backup and status pages. If such an issue is already open, it adds a comment instead.
3. When the app is healthy again, it closes the open outage issues with a recovery comment.

The monitor only runs when the repository variable `APP_URL` is set (the app runs locally by default, so it is skipped until the app is hosted). `BACKUP_SITE_URL` overrides the backup link. Create both under **Settings ? Secrets and variables ? Actions ? Variables**; the workflow creates the `outage` label on first use if it is missing.
