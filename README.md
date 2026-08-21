# PolityPolicy-Inspired Public Data Dashboard

An interactive mixed-frequency dashboard built from original public-source data. It does not copy or mirror PolityPolicy's interactive chart rendering.

## Open Dashboard

<a href="https://shubhankart101.github.io/PolityPolicyUpdate/"><img src="https://img.shields.io/badge/Open%20interactive%20dashboard-2088FF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Open interactive dashboard"></a>

The static dashboard reads the latest generated data and supports chart tooltips, zoom, pan, reset, search, live/pending filters, frequency labels, and expandable indicator notes.

## Sources

- [World Bank Open Data API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) for the live CPI, trade, foreign-reserve, bank-credit, industrial, exchange-rate, GDP-per-capita, population, unemployment, current-account, and broad-money series. These are open international indicators populated from country and official statistical sources.
- [GST portal](https://www.gst.gov.in/) for GST collections.
- [Ministry of Statistics and Programme Implementation](https://www.mospi.gov.in/) for IIP.
- [Reserve Bank of India DBIE](https://data.rbi.org.in/DBIE/#/dbie/home) for the rupee and banking data.
- [Office of Economic Adviser](https://eaindustry.nic.in/) for WPI.
- [NPCI UPI statistics](https://www.npci.org.in/what-we-do/upi/product-statistics) for UPI activity.

## Attribution

Inspired by the public-data storytelling and visual exploration at [PolityPolicy.com](https://politypolicy.com/) and [Polity and Policy on Substack](https://politypolicy.substack.com/). This is an independent dashboard using original charts generated from the public sources listed above.

## Automation

The [weekly workflow](.github/workflows/weekly-substack-articles.yml) and [daily workflow](.github/workflows/daily-politypolicy-update.yml) regenerate public-source data and dashboard assets. Each card displays its actual release frequency; source adapters that need a stable public export are shown as pending rather than populated with estimates.

## Local Preview

```bash
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000` in a browser.
