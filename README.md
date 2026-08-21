# PolityPolicy Daily Update Dashboard

A daily public-data monitor for [India, in Numbers](https://politypolicy.com/). This project inventories publicly accessible stories, Pulse trackers, collections, sister sites, and visible tracker headlines. It does not collect GitHub-account metrics.

## Daily Site Dashboard

<!-- METRICS:START -->

> Last refreshed: **2026-08-21T14:28:05+00:00**

> Collection status: **partial_or_blocked**
> Collector notes: HTTP 403: Forbidden; HTTP 403: Forbidden

| Public site signal | Count |
| --- | ---: |
| Pulse trackers | 0 |
| Interactive/latest story pages | 0 |
| Collections/categories | 0 |
| Sister sites | 0 |

### Pulse Tracker Headlines

| Tracker | HTTP status | Visible headline snippet |
| --- | ---: | --- |
| No trackers detected | - | - |

### Latest Public Story Links

| Page |
| --- |
| No story links detected |

[Latest raw snapshot](data/latest.json) and [Historical snapshots](data/history)

<!-- METRICS:END -->

## What Is Collected

- Public Pulse tracker pages and their current visible headline snippets
- Latest and interactive-story links visible from the homepage
- Public category and collection links
- Sister-site links visible from the homepage
- Page title, source URL, HTTP status, and collection timestamp for each tracker
- A dated JSON snapshot in [data/history](data/history)

## Refresh Schedule

The dashboard refreshes daily at 02:30 UTC and can also be run manually from the [Actions tab](../../actions/workflows/daily-politypolicy-update.yml). Historical snapshots are retained rather than overwritten.

## Scope and Data Ethics

The monitor only reads public HTML exposed by `politypolicy.com` and records a compact index of visible site metadata and headline text. It does not bypass access controls, copy complete underlying datasets, or present itself as an official source. Use the links in each snapshot to reach the original PolityPolicy visualization and its cited official source.

## Repository Layout

```text
.github/workflows/daily-politypolicy-update.yml  Daily public-site collection
data/latest.json                                  Most recent site snapshot
data/history/YYYY-MM-DD.json                      Preserved dated snapshots
```
