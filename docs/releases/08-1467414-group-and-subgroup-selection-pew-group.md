# Group and subgroup selection, Pew group

- **Commit:** [`1467414`](https://github.com/Shubhankart101/India-s-Journey/commit/146741403ac4fff8722a82fa4c16564706d8e1e1)
- **Commit message:** Require Group+Subgroup selection to show charts; add dedicated Pew Research group
- **Date:** 2026-08-22
- **Size:** 5 files changed, +57 / -21 lines

## What it delivered

Charts shown only after choosing a group and subgroup; dedicated Pew Research group.

### From the commit body

> - Charts only render once both a Group and a Subgroup are explicitly chosen,
>   showing a prompt otherwise; From/To date range now always scopes to the
>   exact indices in that selection instead of the global union
> - Add a dedicated top-level 'Pew Research' group (subgroup: Public opinion)
>   so all 6 Pew cards are never mixed with official economic/social data
> - Move Indian Matrix into its own 'Media & Publications' subgroup under
>   Economic to avoid colliding with the new Pew-only 'Public opinion' name
> - Extend the always-visible-when-pending bypass (previously Crime & Security
>   only) to the Pew Research group too, since several Pew cards are
>   intentionally pending
> - Update static HTML group/subgroup <select> options and add .chart-prompt
>   styling

## Where the change landed

| Area | Files |
|---|---|
| `docs` | 3 |
| `(root)` | 1 |
| `tests` | 1 |

## Largest additions

| File | Lines added |
|---|---|
| `tests/test_dashboard_endpoints.py` | 26 |
| `docs/app.js` | 18 |
| `docs/index.html` | 6 |
| `README.md` | 5 |
| `docs/styles.css` | 2 |

Previous: [Pew India subgroups and references](./07-a4968b7-pew-india-subgroups-and-references.md)
