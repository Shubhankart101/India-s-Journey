# Judiciary, Innovation and Sports groups

- **Commit:** [`b9b871c`](https://github.com/Shubhankart101/India-s-Journey/commit/b9b871cfe6c31201e9365802a32ee6fe33034f72)
- **Commit message:** Add Judiciary & Pending Cases group, Innovation group, sports groups and site-wide parity updates
- **Date:** 2026-11-01
- **Size:** 187 files changed, +460083 / -12169 lines

## What it delivered

New groups and site-wide parity updates.

### From the commit body

> - Judiciary & Pending Cases: 764 NJDG charts (Supreme Court 178, High Courts 258,
>   Lower Courts 328) from the official National Judicial Data Grid portals, with a
>   weekly fetch workflow, tests and new animated court artwork
> - Innovation & Technology group (131 charts), 306 expansion and 134 derived charts
> - Sports, Cricket, Hockey and Football groups from official sources
> - Explore, Compare and footer parity between the static site and the Django app
> - file:// bundles so every group shows when opening docs/ from disk
> - Data refresh, dead-code removal and documentation updates
> 
> Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

## Where the change landed

| Area | Files |
|---|---|
| `frontend` | 69 |
| `docs` | 67 |
| `scripts` | 17 |
| `data` | 15 |
| `tests` | 7 |
| `webapp` | 6 |

## Largest additions

| File | Lines added |
|---|---|
| `data/legal/njdg_snapshot.json` | 109897 |
| `data/chart-latest.json` | 108633 |
| `docs/data/chart-latest.json` | 108633 |
| `docs/data.js` | 108280 |
| `docs/app.js` | 2929 |
| `data/sports_sources/cricket.json` | 2703 |

Previous: [Netlify primary site](./27-cc83baf-netlify-primary-site.md)
