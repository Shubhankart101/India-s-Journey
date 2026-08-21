# PolityPolicy-Inspired Public Data Dashboard

An interactive, weekly refreshed dashboard built from original public-source data. It does not copy or mirror PolityPolicy's interactive chart rendering.

## Open Dashboard

<a href="https://shubhankart101.github.io/PolityPolicyUpdate/"><img src="https://img.shields.io/badge/Open%20interactive%20dashboard-2088FF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Open interactive dashboard"></a>

The static dashboard reads the latest generated data and supports chart tooltips, zoom, pan, reset, and source links.

## Sources

- [World Bank Open Data API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) for India CPI inflation, GDP growth, trade share, foreign reserves, domestic credit, and industrial growth.
- [Polity and Policy public RSS feed](https://politypolicy.substack.com/feed) for weekly publication cadence and article links.

## Attribution

Inspired by the public-data storytelling and visual exploration at [PolityPolicy.com](https://politypolicy.com/) and [Polity and Policy on Substack](https://politypolicy.substack.com/). This is an independent dashboard using original charts generated from the public sources listed above.

## Automation

The [weekly workflow](.github/workflows/weekly-substack-articles.yml) refreshes public-source data, regenerates chart assets and dashboard data, and preserves snapshots in `data/`.

## Local Preview

```bash
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000` in a browser.
