# Netlify primary site

- **Commit:** [`cc83baf`](https://github.com/Shubhankart101/India-s-Journey/commit/cc83baf7c2db36bcefce14c3ad056ecd458300ce)
- **Commit message:** Make Netlify the primary static site with GitHub Pages as its backup
- **Date:** 2026-10-31
- **Size:** 32 files changed, +143 / -306 lines

## What it delivered

Netlify is the primary static host with GitHub Pages as backup.

### From the commit body

> Remove the Render config and the static status page. The web app now links to the Netlify dashboard as its backup and to GitHub Pages as the mirror (BACKUP_MIRROR_URL replaces BACKUP_STATUS_URL). Docs, diagrams, OpenAPI servers, workflows and tests updated.
> 
> Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## Where the change landed

| Area | Files |
|---|---|
| `docs` | 13 |
| `frontend` | 6 |
| `webapp` | 6 |
| `.github` | 3 |
| `(root)` | 3 |
| `tests` | 1 |

## Largest additions

| File | Lines added |
|---|---|
| `docs/BACKUP.md` | 42 |
| `README.md` | 17 |
| `docs/DEPLOYMENT.md` | 16 |
| `docs/ARCHITECTURE.md` | 8 |
| `webapp/indicators/tests/test_docs_and_errors.py` | 8 |
| `frontend/src/test/resilience.test.jsx` | 7 |

Previous: [63 explained official datasets](./26-5d9dbd5-63-explained-official-datasets.md)
