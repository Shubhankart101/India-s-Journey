# 📊 India's Journey | Public Data Dashboard

<p align="center">
	<a href="https://shubhankart101.github.io/PolityPolicyUpdate/"><img src="https://img.shields.io/badge/🚀%20Live%20dashboard-2088FF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Live dashboard"></a>
	<a href="https://github.com/Shubhankart101/PolityPolicyUpdate/actions"><img src="https://img.shields.io/badge/✅%20Build%20and%20tests-success-2ea44f?style=for-the-badge&logo=githubactions&logoColor=white" alt="Build and tests"></a>
	<a href="https://datahelpdesk.worldbank.org/knowledgebase/articles/889392"><img src="https://img.shields.io/badge/🌍%20Public%20data-World%20Bank-6f42c1?style=for-the-badge" alt="Public data sources"></a>
</p>

## 🧭 About This Dashboard

This independent project was created to make India’s economic, social, and infrastructure signals easier to explore through long-run interactive graphs. It brings together public APIs and official portals, keeps each indicator’s frequency and limitations visible, and gives every live value a traceable source.

With thanks to [PolityPolicy](https://politypolicy.com/) and [Polity and Policy](https://politypolicy.substack.com/) for inspiring a visual, thoughtful approach to public information. This dashboard is independently built and uses its own charts and data pipeline.

An interactive mixed-frequency dashboard built from original public-source data. It does not copy or mirror PolityPolicy's interactive chart rendering.

## 🚀 Open Dashboard

<a href="https://shubhankart101.github.io/PolityPolicyUpdate/"><img src="https://img.shields.io/badge/Open%20interactive%20dashboard-2088FF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Open interactive dashboard"></a>

The static dashboard reads the complete available history for each live series and presents charts in a full-width vertical sequence. It supports chart tooltips, zoom, pan, reset, search, live/pending filters, full-history/2000/2011 window controls, frequency labels, and expandable three-paragraph indicator context. It currently contains 22 India-focused indicators, with 18 live open-data graphs and four official-source cards awaiting stable exports.

The History control filters the actual observations returned by each API. The current live World Bank indicators are annual, so the dashboard does not fabricate monthly points by interpolation. Monthly drill-down will be added when stable monthly exports are available from the relevant Indian government source.

World Bank series generally reach back to 1960, so the live charts now include data before 2011 where observations exist. The modern API does not provide a consistent pre-1947 India history; pre-independence charts would require separate historical datasets with different definitions and sources.

## 🔗 References

<details>
<summary>Open data sources, APIs, and official portals</summary>

### Live data APIs

- [World Bank API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
- [CPI inflation API](https://api.worldbank.org/v2/country/IND/indicator/FP.CPI.TOTL.ZG?format=json&per_page=100)
- [Trade share of GDP API](https://api.worldbank.org/v2/country/IND/indicator/NE.TRD.GNFS.ZS?format=json&per_page=100)
- [Foreign reserves API](https://api.worldbank.org/v2/country/IND/indicator/FI.RES.TOTL.CD?format=json&per_page=100)
- [Private-sector credit API](https://api.worldbank.org/v2/country/IND/indicator/FS.AST.PRVT.GD.ZS?format=json&per_page=100)
- [Industrial value-added API](https://api.worldbank.org/v2/country/IND/indicator/NV.IND.TOTL.KD.ZG?format=json&per_page=100)
- [Official exchange-rate API](https://api.worldbank.org/v2/country/IND/indicator/PA.NUS.FCRF?format=json&per_page=100)
- [GDP per capita API](https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.PCAP.CD?format=json&per_page=100)
- [Population API](https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL?format=json&per_page=100)
- [Unemployment API](https://api.worldbank.org/v2/country/IND/indicator/SL.UEM.TOTL.ZS?format=json&per_page=100)
- [Current-account balance API](https://api.worldbank.org/v2/country/IND/indicator/BN.CAB.XOKA.GD.ZS?format=json&per_page=100)
- [Broad-money API](https://api.worldbank.org/v2/country/IND/indicator/FM.LBL.BMNY.GD.ZS?format=json&per_page=100)
- [Tax-revenue API](https://api.worldbank.org/v2/country/IND/indicator/GC.TAX.TOTL.GD.ZS?format=json&per_page=100)
- [Government-consumption API](https://api.worldbank.org/v2/country/IND/indicator/NE.CON.GOVT.ZS?format=json&per_page=100)
- [Foreign-direct-investment API](https://api.worldbank.org/v2/country/IND/indicator/BX.KLT.DINV.WD.GD.ZS?format=json&per_page=100)
- [Domestic-savings API](https://api.worldbank.org/v2/country/IND/indicator/NY.GDS.TOTL.ZS?format=json&per_page=100)
- [Electricity-access API](https://api.worldbank.org/v2/country/IND/indicator/EG.ELC.ACCS.ZS?format=json&per_page=100)
- [Internet-users API](https://api.worldbank.org/v2/country/IND/indicator/IT.NET.USER.ZS?format=json&per_page=100)
- [Life-expectancy API](https://api.worldbank.org/v2/country/IND/indicator/SP.DYN.LE00.IN?format=json&per_page=100)

### Indian government and public sources

- [GST portal](https://www.gst.gov.in/) for GST collections.
- [Controller General of Accounts](https://cga.nic.in/) for Union fiscal accounts.
- [MOSPI](https://www.mospi.gov.in/) for IIP and official statistics.
- [RBI DBIE](https://data.rbi.org.in/DBIE/#/dbie/home) for monetary, banking, and exchange-rate data.
- [Office of the Economic Adviser](https://eaindustry.nic.in/) for WPI.
- [NPCI UPI statistics](https://www.npci.org.in/what-we-do/upi/product-statistics) for UPI activity.
- [PolityPolicy.com](https://politypolicy.com/) and [Polity and Policy RSS](https://politypolicy.substack.com/feed) for attribution and public publication context.

### Runtime libraries

- [Chart.js 4.4.4](https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js)
- [Hammer.js 2.0.8](https://cdn.jsdelivr.net/npm/hammerjs@2.0.8)
- [chartjs-plugin-zoom 2.0.1](https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js)

</details>

## 🙏 Attribution

Inspired by the public-data storytelling and visual exploration at [PolityPolicy.com](https://politypolicy.com/) and [Polity and Policy on Substack](https://politypolicy.substack.com/). This is an independent dashboard using original charts generated from the public sources listed above.

## ⚙️ Automation

The [weekly workflow](.github/workflows/weekly-substack-articles.yml) and [daily workflow](.github/workflows/daily-politypolicy-update.yml) regenerate public-source data and dashboard assets. Each card displays its actual release frequency; source adapters that need a stable public export are shown as pending rather than populated with estimates.

## 🛠️ Local Preview

```bash
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000` in a browser.
