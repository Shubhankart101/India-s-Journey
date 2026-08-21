# 📊 India's Journey | Public Data Dashboard

<p align="center">
	<a href="https://shubhankart101.github.io/India-s-Journey/"><img src="https://img.shields.io/badge/🚀%20Live%20dashboard-2088FF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Live dashboard"></a>
	<a href="https://github.com/Shubhankart101/India-s-Journey/actions"><img src="https://img.shields.io/badge/✅%20Build%20and%20tests-success-2ea44f?style=for-the-badge&logo=githubactions&logoColor=white" alt="Build and tests"></a>
	<a href="https://datahelpdesk.worldbank.org/knowledgebase/articles/889392"><img src="https://img.shields.io/badge/🌍%20Public%20data-World%20Bank-6f42c1?style=for-the-badge" alt="Public data sources"></a>
</p>

## 🧭 About This Dashboard

This independent project was created to make India’s economic, social, and infrastructure signals easier to explore through long-run interactive graphs. It brings together public APIs and official portals, keeps each indicator’s frequency and limitations visible, and gives every live value a traceable source.

With sincere thanks to [PolityPolicy](https://politypolicy.com/), [Tushar Gupta’s Polity and Policy Substack](https://politypolicy.substack.com/), and [Indian Matrix](https://substack.com/@indianmatrix) for the inspiring work that encouraged this visual, thoughtful approach to public information. The dashboard now has a dedicated **Inspiration** section separate from the general About text, so PolityPolicy attribution is not mixed in with dashboard mechanics.

Special appreciation to Indian Matrix for the work that helped motivate the market-and-public-indicators view. The dashboard organizes indicators into four top-level groups: Economic, Social, **Pew Research**, and Crime & Security, each split into contextual subgroups (13 total: Macroeconomics, Monetary Policy, Trade & External, Markets, Infrastructure, Production & Commodities, Media & Publications, Demographics, Welfare, Public opinion, Violence & Crime, Terrorism, Maoism/LWE). Pew Research is a dedicated group so that survey-based indicators are never mixed in with official administrative or macroeconomic series. Selecting a group narrows the subgroup dropdown to only the subgroups that belong to it. Multi-dataset charts (for example, the combined market-indices view) display a legend; single-series charts do not, to reduce clutter.

**Charts are only shown once both a Group and a Subgroup are explicitly selected.** Before that, the chart area shows a prompt instead of every indicator at once. This keeps the view purposeful and, critically, means the From/To date-range dropdowns are always scoped to the exact indices in the selected subgroup rather than the union of every series on the dashboard — so the available dateline changes to match the indices you're actually looking at.

Indian Matrix is now represented by a weekly publication-cadence graph and a right-side article rail sourced from its public RSS feed. It lives under Economic → Media & Publications, distinct from the Pew Research group.

Pew Research Center India has its own dedicated top-level group (subgroup: Public opinion) and is represented three ways: a dated public-report catalog and yearly report-cadence graph, and three **survey-snapshot** cards (global power, US-India relations, economic confidence) that plot individually-verified, dated percentages from a single cited Pew report as discrete labelled points rather than a fabricated continuous trend. Two Pew cards (leadership, technology adoption) remain intentionally pending because no comparable verified India percentages were found for those topics.

The About panel also includes a right-side reading rail populated from the public Polity and Policy RSS snapshot. The weekly pipeline refreshes article titles, dates, and URLs; the Pages deployment copies that snapshot into the dashboard so the buttons stay linked to the latest available public articles.

An interactive mixed-frequency dashboard built from original public-source data. It does not copy or mirror PolityPolicy's interactive chart rendering.

## 🚀 Open Dashboard

<a href="https://shubhankart101.github.io/India-s-Journey/"><img src="https://img.shields.io/badge/Open%20interactive%20dashboard-2088FF?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Open interactive dashboard"></a>

The static dashboard reads the complete available history for each live series and presents charts in a full-width vertical sequence. It supports chart tooltips, zoom, pan, reset, indicator search, Economic/Social/Crime & Security group filtering, subgroup filtering, live/pending filters, data-driven From/To period controls, frequency labels, and expandable three-paragraph indicator context.

The From/To controls are populated from the actual observations returned by the APIs. Economic Survey Statistical Appendix tables 9.1–9.4 now provide collated monthly GST, UPI, IIP, forex, exchange-rate, power, e-way bill, rail freight, port cargo, core-industry, crude-oil, fuel-consumption, export, and import observations through the daily pipeline. The extractor checks the 2022-23, 2023-24, 2024-25, and latest Survey editions, merges overlapping `YYYY-MM` observations, and keeps the official Survey tables as provenance. The dashboard does not fabricate monthly points by interpolation.

The fuel graph is a **fuel consumption** activity series, not a retail fuel price index. **Indian crude oil basket price** is provided separately as the available Economic Survey fuel-price indicator. WPI is sourced from the official OEA monthly workbook and cached by the daily pipeline.

Fiscal deficit is now populated as an annual percentage-of-GDP series from Economic Survey table 2.4 Excel editions. It is not presented as a monthly rupee series because the official table does not provide that frequency cleanly.

World Bank series generally reach back to 1960, so the live charts now include data before 2011 where observations exist. The modern API does not provide a consistent pre-1947 India history; pre-independence charts would require separate historical datasets with different definitions and sources.

Security context is represented separately: the live homicide-rate series uses the World Bank indicator, the MHA LWE card uses the official 2004-2025 aggregate deaths figure, and the terrorism chart uses India rows from Our World in Data with Global Terrorism Database provenance. These are not combined into a fabricated 1947-present incident count.

The Crime & Security group also includes an NCRB source-status card. NCRB Crime in India editions are available, but a consistent all-time machine-readable series has not been identified; definitions and classifications must be reconciled before plotting historical totals. `data.gov.in`'s NCRB catalog pages were checked and did not return a stable dataset at time of writing.

The LWE civilian/security-force/perpetrator casualty breakdown is now populated (2000-2025) from the South Asia Terrorism Portal's (SATP) "Maoist Insurgency" fatality tables, a clean, consistently-formatted, clearly-labelled secondary source. MHA's own public page only publishes the 2004-2025 aggregate (8,956 killed) without this breakdown, and SATP uses a different classification and provisional news-based tally, so the two figures are not summed or treated as the same series; the MHA aggregate card and the three SATP breakdown cards are both retained, separately sourced and labelled.

## 🧪 Testing

[`tests/test_dashboard_endpoints.py`](tests/test_dashboard_endpoints.py) is a live-endpoint test suite (no mocks) that verifies, against the deployed `DASHBOARD_URL`:

- Every data JSON file (`chart-latest`, `economic-survey-monthly`, `substack-latest`, `indian-matrix-latest`, `pew-india-reports`, `pew-snapshots`, `ncrb-and-analyses`) is served with HTTP 200 and contains its expected top-level keys.
- Every live World Bank indicator API used by the dashboard returns at least 2 usable observations.
- Official source portals (GST, CGA, MOSPI, RBI, OEA) are reachable or return an expected auth-gated status.
- The HTML page includes the expected filter controls, group/subgroup options, and references section.
- The current cache-busted `app.js` bundle is served and contains `updateCards`.

Run it locally against the live site with:

```bash
python -m unittest tests/test_dashboard_endpoints.py -v
```

Or point it at a local preview server with `DASHBOARD_URL=http://localhost:8000 python -m unittest tests/test_dashboard_endpoints.py -v`.

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
- [Intentional homicide rate API](https://api.worldbank.org/v2/country/IND/indicator/VC.IHR.PSRC.P5?format=json&per_page=100)
- [MHA Left-Wing Extremism Division](https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division)
- [Global Terrorism Database](https://www.start.umd.edu/gtd/)
- [Pew Research Center Global Attitudes](https://www.pewresearch.org/global/) for India public-opinion research and survey findings.
- [Pew Research Center: India, Global Optimism, Local Fears (2008)](https://www.pewresearch.org/global/2008/12/04/india/) for the cited survey-snapshot percentages used in the Pew economy-confidence, US-relations, and global-power cards.
- [South Asia Terrorism Portal - Maoist Insurgency fatalities](https://www.satp.org/datasheet-terrorist-attack/fatalities/india-maoistinsurgency) for the civilian/security-force/perpetrator breakdown used by the three SATP-sourced LWE casualty cards; a secondary, non-official source with its own classification, distinct from the MHA aggregate.
- [NCRB Crime in India](https://ncrb.gov.in/crime-in-india.html) for official crime statistics and year-wise table references.
- [Economic Survey statistical appendix](https://www.indiabudget.gov.in/economicsurvey/doc/Statistical-Appendix-in-English.pdf) for collated monthly HFI tables.
- [Economic Survey table 9.1](https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab9.1.pdf) for monthly GST and related high-frequency indicators.
- [Economic Survey table 9.2](https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab9.2.pdf) for monthly UPI and IIP indicators.
- [Economic Survey table 9.3](https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab9.3.pdf) for monthly forex reserves.
- [Economic Survey table 9.4](https://www.indiabudget.gov.in/economicsurvey/doc/stat/tab9.4.pdf) for monthly exchange rate and external indicators.

### Indian government and public sources

- [GST portal](https://www.gst.gov.in/) for GST collections.
- [Controller General of Accounts](https://cga.nic.in/) for Union fiscal accounts.
- [MOSPI](https://www.mospi.gov.in/) for IIP and official statistics.
- [RBI DBIE](https://data.rbi.org.in/DBIE/#/dbie/home) for monetary, banking, and exchange-rate data.
- [Office of the Economic Adviser](https://eaindustry.nic.in/) for WPI.
- [NPCI UPI statistics](https://www.npci.org.in/what-we-do/upi/product-statistics) for UPI activity.
- [PolityPolicy.com](https://politypolicy.com/), [Polity and Policy RSS](https://politypolicy.substack.com/feed), and [Indian Matrix](https://substack.com/@indianmatrix) for attribution and public-data storytelling context.

### Runtime libraries

- [Chart.js 4.4.4](https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js)
- [Hammer.js 2.0.8](https://cdn.jsdelivr.net/npm/hammerjs@2.0.8)
- [chartjs-plugin-zoom 2.0.1](https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js)

</details>

## 🙏 Attribution

Inspired by the public-data storytelling and visual exploration at [PolityPolicy.com](https://politypolicy.com/), [Polity and Policy on Substack](https://politypolicy.substack.com/), and [Indian Matrix](https://substack.com/@indianmatrix). This is an independent dashboard using original charts generated from the public sources listed above. The live dashboard now has a dedicated Inspiration section that separates PolityPolicy attribution from the general About text.

## ⚙️ Automation

The [weekly workflow](.github/workflows/weekly-substack-articles.yml) and [daily workflow](.github/workflows/daily-politypolicy-update.yml) regenerate public-source data and dashboard assets, including `scripts/collect_ncrb_and_analyses.py` and `scripts/collect_pew_snapshots.py`. Each card displays its actual release frequency; source adapters that need a stable public export are shown as pending rather than populated with estimates.

## 🛠️ Local Preview

```bash
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000` in a browser.
