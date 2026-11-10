# Release 32: India in Maps, fiscal and faith journeys, and ten display modes

- **Commit:** [`9e65ede`](https://github.com/Shubhankart101/India-s-Journey/commit/9e65ede799453b1e3092470c8653d8f1ff4fba4a)
- **Date:** 2026-11-05
- **Catalogue:** 11 groups, 133 subgroups and 3,031 indicators at release validation

## Summary

Release 32 expands India's Journey from a collection of public-data charts into a browsable atlas of state indicators, elections, public finance, epics and faith journeys. It consolidates the catalogue into 11 top-level groups while preserving legacy group/subgroup query aliases, adds maps and long-form explainers, and brings the same data and interactive features to the static site and Django + React app.

## Highlights

### Eleven groups and navigation

| Group | Subgroups | Indicators |
|---|---:|---:|
| Economy & Markets | 8 | 180 |
| Public Finance & States | 6 | 148 |
| Industry, Energy & Technology | 12 | 308 |
| Infrastructure & Mobility | 13 | 285 |
| People, Health & Society | 11 | 251 |
| Environment, Agriculture & Food | 4 | 79 |
| Security, Justice & Defence | 35 | 874 |
| Elections & Democracy | 19 | 461 |
| Culture, Heritage & Sport | 9 | 176 |
| Epics, Faiths & Journeys | 6 | 19 |
| India in Maps | 10 | 250 |
| **Total** | **133** | **3,031** |

The consolidated names group related legacy categories; old group and subgroup query strings continue to map to their new locations. The home screen's scrolling chip marquee was replaced with group cards.

### Maps and elections

- **India in Maps** adds compact state maps to relevant cards and interactive map views with state/UT details, a colour scale and a Map/Bar switch.
- The **Lok Sabha atlas (1952–2024)** provides election-by-election state history, with sourced party and result details.
- The **SSR/SIR voter-roll explainer** covers Special Summary Revision and Special Intensive Revision, key stages and forms. It is educational information, not an application or voter-registration service.

### Public finance and fiscal views

New views include the **State Finances Matrix**, GDP explorer, **Spending by function**, state head-to-head comparisons, **Union Budget anatomy** and **How India Borrows**. These present state fiscal comparisons, spending composition, Union receipts/expenditure and borrowing context using the cited RBI, budget and state-finance sources.

### Epic and faith atlases

- The Mahabharata and Ramayana epic atlas provides **Kingdoms**, **Allegiance** and **Route** views.
- Journey maps trace the Vedas and Upanishads, Panchatantra, Buddha, Mahavira and the ten Sikh Gurus.
- Hindu, Buddhist, Jain and Sikh scripture verses appear in original languages with English translations across indicator cards, maps and explainers. General epic verses are explicitly labelled as general verses.

### Themes, explainers and performance

- The initial five display modes were **Light**, **Dark**, **Newspaper**, **Pamphlet** and **Military** in both static and Django/React experiences. The [follow-up below](#follow-up) adds five more. Newspaper and Pamphlet use 1947-inspired vintage chrome; Military is an olive-drab, khaki and brass edition. All modes use theme-aware chart and map colours.
- The Explore page's group grid now uses the same illustrated group cards (icons and India outline) as the home page.
- Article-style group and subgroup explainers add context and interpretation. Source lists use concise publisher chips, with overflow sources expandable.
- Off-screen charts and content load lazily to reduce initial work. Both site variants use the common catalogue export and shared data builders for feature and content parity.

### Fixes and source quality

- Corrected the header logo and repaired mojibake in interface text.
- Kept the Pamphlet theme button visible while Newspaper mode is active.
- Replaced the home-page chip marquee with group cards and de-cluttered explainer source chips.
- Removed baked-in art captions from page backdrops (no more floating titles over content) and kept compact journey-map cards from overlapping card text.
- Every subgroup now resolves to background art (falling back to its group art) and a scripture verse from the existing verse pool.
- Added `scripts/update_all_data.py`, a single data-refresh orchestrator (`--only`, `--offline`, `--skip-network`), plus a monthly `data-refresh` workflow; see `docs/PIPELINES.md`.
- Slimmed the repository: raw source caches (`data/raw*/`, `data/*-sources/`, report PDFs) are gitignored and re-fetched by the pipelines.
- Audited and corrected source attributions. `python scripts/audit_sources.py` reported **0 errors across 3,031 indicators** at release validation.

## Data sources and caveats

Sources are linked on the cards and in the generated data. The release draws on public datasets and official releases including RBI, MOSPI/eSankhyiki, Union and State budget documents, Election Commission of India records, and published scripture/epic text pages. The Lok Sabha geography layer uses the DataMeet States boundary data derived from Survey of India outlines (CC BY 2.5 IN); the build script simplifies the layer for browser use.

- The Lok Sabha historical atlas includes a CC0 constituency dataset. The 1984/85 and 1991/92 polling periods are each merged as one atlas year; turnout is missing for 2014–2024 in the underlying dataset; two-member constituencies affect seat totals for 1952 and 1957.
- Epic shlokas were checked against the cited online pages, not the BORI Critical Edition. A general verse is labelled as such and is not represented as a quotation tied to a specific place.
- Fiscal and voter-roll data follow the coverage and release schedules of their respective publishers. The SSR/SIR visualizer is an explainer, not an ECI service. Sources may revise historical observations; each chart's note remains authoritative for its coverage and limitations.
- New NITI Aayog report indices (Health Index 2019-20, Fiscal Health Index FY2023, National MPI 2023, SEQI 2016-17, Export Preparedness Index 2022, India Innovation Index 2021) and Maoist / LWE indices from PIB, ORF and ICFS reports were added in the Health, Public Finance, Economy, Industry & Technology, People and Security groups. Planning Commission Five-Year Plan series are not yet included.

## Validation

Release QA recorded **276 passing pytest tests**, **127 passing Vitest tests** and **117 passing Django tests**, plus a Playwright sweep of both the Django app and the static build in the five original modes at 1440px and 390px (no overflow, mojibake or page errors). The web-app CI also runs production Django checks, migration checks, OpenAPI validation, a frontend build, Docker smoke checks and memory checks. The source-attribution audit returned zero errors for the release catalogue.

## Deployment notes

- The static dashboard is hosted on **Netlify**, with **GitHub Pages** as a mirror.
- **Render** is configured as the continuing Django + React deployment through [`render.yaml`](../../render.yaml), a Render Blueprint.
- **Fly.io** is paused; its deployment workflow is manual-only (`workflow_dispatch`). Render is the continuing web-app deployment target. See [Deployment](../DEPLOYMENT.md) for current hosting details.

## Upgrade notes

1. Regenerate the catalogue using the normal export pipeline; do not hand-edit `data/catalog.json`.
2. For an existing Django deployment, install the current dependencies, run `manage.py migrate`, then `manage.py import_catalog` to load the 11-group catalogue.
3. Rebuild the React frontend and static assets using the project build scripts before deploying. The static and Django versions should use matching generated data.
4. Existing group/subgroup query URLs are handled by the legacy alias maps. Review application code that assumes the former category names or ordering before relying on database IDs or names.
5. Fly.io deployments are manual-only if needed; use the Render Blueprint for the ongoing app deployment.

## Known issues and interpretation limits

- Election years with combined polling and missing turnout are described above; the atlas should not be treated as a complete substitute for original ECI reports.
- Epic place identifications and route geometry are interpretive and approximate; verify individual citations and map notes when using them.
- Public data publishers update at different intervals, and historical values can be revised. A displayed series may have gaps or a different observation frequency from the workflow that checks its source.

Previous: [Water, logistics, expanded air and rail data, interactive charts](./31-aeb4153-water-logistics-and-interactive-charts.md)

## Follow-up
- Added Parliamentary, Desi, Air Force, Navy and Police display modes (10 total) to the pill selector on both platforms.
- Home page mini maps restored; asset paths now respect the GitHub Pages base path.
