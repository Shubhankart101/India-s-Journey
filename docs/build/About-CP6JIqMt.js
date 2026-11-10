import{r as e}from"./rolldown-runtime-XKyaHtl9.js";import{_ as t,g as n}from"./charts-B6pdgxOd.js";import{r,t as i}from"./vendor-CMZuCPfa.js";import{A as a,C as o,S as s,c,h as l,k as u,l as d,o as f,w as p,x as m}from"./index-DWy4F2Hx.js";var h=e(t(),1),g=`<div align="center">

# India's Journey

**India, in perspective.** A public-data atlas of India, from 1947 to today.

[![11 groups](https://img.shields.io/badge/groups-11-138808?style=flat-square)](#groups)
[![3,031 indicators](https://img.shields.io/badge/indicators-3%2C031-ff9933?style=flat-square)](#groups)
[![10 display modes](https://img.shields.io/badge/display%20modes-10-9b1b30?style=flat-square)](#themes)
[![Release 32](https://img.shields.io/badge/release-32-c2185b?style=flat-square)](docs/releases/32-9e65ede-india-in-maps-and-display-themes.md)

[![Static dashboard](https://img.shields.io/badge/Explore-Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)](https://indiasjourney.netlify.app)
[![Web app](https://img.shields.io/badge/Web%20app-Render-0c6b4f?style=for-the-badge)](https://indias-journey.onrender.com)
[![GitHub Pages mirror](https://img.shields.io/badge/Backup-GitHub%20Pages-2088FF?style=for-the-badge&logo=github&logoColor=white)](https://shubhankart101.github.io/India-s-Journey/)
[![Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2ea44f?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/Shubhankart101/India-s-Journey/actions)

</div>

<a id="contents"></a>
## Contents

[Explore live](#explore-live) | [About](#about) | [Groups](#groups) | [Features](#features) | [Themes](#themes) | [Sources and caveats](#sources-and-caveats) | [Architecture](#architecture) | [Documentation](#documentation) | [Run locally](#run-locally) | [Testing](#testing) | [Deployment](#deployment) | [Release notes](#release-notes) | [Credits and licence](#credits-and-licence)

<a id="explore-live"></a>
## Explore live

<details>
<summary>Choose a dashboard view</summary>

| View | Open |
|---|---|
| Browse indicators | [Explore the catalogue](https://indiasjourney.netlify.app/#/explore) |
| India in Maps | [Open the map atlas](https://indiasjourney.netlify.app/#/explore?category=india-in-maps) |
| Lok Sabha elections | [Open election history](https://indiasjourney.netlify.app/#/elections) |
| Voter-roll guide | [Open the SSR/SIR explainer](https://indiasjourney.netlify.app/#/voter-list-sir-ssr) |
| Sources | [Browse data sources](https://indiasjourney.netlify.app/#/sources) |

</details>

<a id="about"></a>
## About

India's Journey is an independent dashboard for exploring long-run public indicators, state comparisons, maps, elections, fiscal data and cultural journeys. Indicator cards retain their source links, units, frequency and caveats. The static site and Django + React application share the exported catalogue and generated data.

<a id="groups"></a>
## Groups
The catalogue contains **3,031 indicators across 11 groups and 133 subgroups**. Counts below are computed from \`data/catalog.json\` (\`indicators\` assigned to each category; subgroups listed on that category).

<details open>
<summary>Show all 11 groups and catalogue counts</summary>

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

</details>

<a id="features"></a>
## Features

<details open>
<summary>Atlases, explainers and data tools</summary>

- **India in Maps:** compact state maps on relevant indicator cards and restored home-page mini maps, with an interactive full map, accessible state readouts and map/bar views.
- **Lok Sabha atlas (1952–2024):** explore election results by year and State/UT, including state-by-state political history.
- **Electoral-roll explainer:** an interactive guide to SSR (Special Summary Revision) and SIR (Special Intensive Revision), timelines, eligibility and forms. It is an explainer, not an application.
- **Fiscal views:** State Finances Matrix, GDP explorer, spending by function, state head-to-head comparisons, Union Budget anatomy and How India Borrows.
- **Epic atlas:** switch between **Kingdoms**, **Allegiance** and **Route** for the Mahabharata and Ramayana.
- **Faith and story journeys:** maps for the Vedas and Upanishads, Panchatantra, Buddha, Mahavira and the ten Sikh Gurus.
- **Article-style explainers** add context, methodology and source notes to groups and subgroups. Publisher chips are concise, with additional sources expandable.
- **Scripture verses:** Hindu, Buddhist, Jain and Sikh traditions are represented in original languages with English translations on indicator cards, maps and explainers.
- **Sources audit:** \`scripts/audit_sources.py\` checks exported indicator attribution. The release-32 audit found **0 errors across 3,031 indicators**.
- **Performance:** charts are loaded on demand, with lazy rendering for off-screen content; the home page uses group cards instead of the former scrolling chip marquee.
- **Static/Django parity:** catalogue remapping and shared data builders keep group names, map and atlas datasets aligned between the static site and the Django-served React app. Legacy group and subgroup query parameters resolve through compatibility aliases.

</details>

<a id="themes"></a>
## Themes

<details>
<summary>Ten display modes</summary>

Choose **Light**, **Dark**, **Newspaper**, **Pamphlet**, **Military**, **Parliamentary**, **Desi**, **Air Force**, **Navy** or **Police** from the theme selector. Newspaper and Pamphlet use a 1947-inspired vintage treatment; the other modes draw on their namesake Indian institutions and styles. All ten are available across the static and Django/React interfaces, and chart/map colours adapt with the selected mode.

</details>

<a id="sources-and-caveats"></a>
## Sources and caveats

<details>
<summary>Data sources and interpretation notes</summary>

The catalogue combines public datasets and official releases, including World Bank indicators, RBI publications, MOSPI and its eSankhyiki APIs, Union and State budget documents, the Election Commission of India, and other source links shown with the relevant indicators. Scripture and epic quotations link to the consulted text pages; translations and place identifications are documented with the relevant content.

- The Lok Sabha historical atlas uses a CC0 constituency dataset alongside sourced election data. The 1984/85 and 1991/92 polling periods are each represented as a merged year; turnout is unavailable for 2014–2024 in the atlas source. Seat totals for 1952 and 1957 are affected by two-member constituencies.
- Epic shlokas were checked against cited online text pages, not the Bhandarkar Oriental Research Institute (BORI) Critical Edition. General epic verses are labelled as general rather than presented as place-specific quotations.
- Coverage, update dates and definitions vary by publisher. A source's refresh schedule does not imply the underlying observations are equally frequent. Read the source and caveat on each card before comparing values.
- NITI Aayog report indices (state and UT rankings, built by \`scripts/build_niti_reports.py\`): Health Index Round IV 2019-20, Fiscal Health Index 2025 (FY2023), National MPI Progress Review 2023, School Education Quality Index 2019, Export Preparedness Index 2022 and India Innovation Index 2021. Planning Commission Five-Year Plan series and the SDG India Index are not yet included.
- Maoist / Left-Wing Extremism indices (\`scripts/build_lwe_insurgency.py\`) from the PIB backgrounder "Naxal-Free India" (Aug 2026), ORF's "Reclaiming the Heartland" and ICFS's "Closing the Red Corridor": affected districts, incidents, fatalities, civilians killed, attacks on infrastructure, surrenders, security build-up, roads, towers, banking, schooling and central funding. Unlabelled chart values and conflicting figures are omitted or flagged in each card's note.

</details>

<a id="architecture"></a>
## Architecture

\`\`\`mermaid
flowchart LR
  S[Public and official sources] --> C[Collectors and dataset builders]
  C --> D[Generated JSON and chart data]
  D --> X[Catalog export and legacy URL remapping]
  X --> J[data/catalog.json]
  D --> W[Static site in docs/]
  J --> I[Django catalog import]
  I --> A[Read-only API]
  A --> R[React web app]
  G[GitHub Actions] --> C
  G --> P[Pages and Netlify deployment]
  G --> H[Web-app CI and deployment]
\`\`\`

The static site reads generated assets under \`docs/\`. \`scripts/export_catalog.mjs\` produces the shared \`data/catalog.json\`; Django imports it for the API and React frontend. Scheduled workflows refresh data and re-export the catalogue. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PIPELINES.md](docs/PIPELINES.md) and [docs/diagrams/architecture.drawio](docs/diagrams/architecture.drawio).

<a id="run-locally"></a>
## Run locally

### Static dashboard

From the repository root:

\`\`\`powershell
python -m http.server 8772 --directory docs
\`\`\`

Open <http://localhost:8772>.

### Django + React web app

Install dependencies and build the frontend from the repository root, then migrate and import the catalogue:

\`\`\`powershell
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r webapp\\requirements.txt
cd frontend
npm install
npm run build
cd ..\\webapp
..\\.venv\\Scripts\\python.exe manage.py migrate
..\\.venv\\Scripts\\python.exe manage.py import_catalog
..\\.venv\\Scripts\\python.exe manage.py runserver
\`\`\`

Open <http://localhost:8000>. To work on the React frontend with its dev server instead, run \`npm run dev\` from \`frontend\` while Django is running; the frontend proxies API requests to Django. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for configuration.

<a id="testing"></a>
## Testing

Release 32 validation included **276 passing pytest tests**, **127 passing Vitest tests**, **117 passing Django tests**, and Playwright checks. CI also validates the OpenAPI schema and builds/smoke-tests the container. Run the relevant suites locally:

\`\`\`powershell
python -m pytest tests -q --ignore=tests\\test_dashboard_endpoints.py
cd webapp
..\\.venv\\Scripts\\python.exe manage.py test indicators
cd ..\\frontend
npm test
npm run test:e2e
\`\`\`

See [docs/TESTING.md](docs/TESTING.md) and [Web app CI](.github/workflows/webapp-ci.yml).

<a id="deployment"></a>
## Deployment

- **Static dashboard:** Netlify is configured for \`docs/\`; GitHub Pages provides a mirror. See [\`netlify.toml\`](netlify.toml) and [the Pages workflow](.github/workflows/deploy-dashboard.yml).
- **Django + React:** [\`render.yaml\`](render.yaml) is the Render Blueprint. Select **New > Blueprint** in Render and point it at this repository; it builds the Docker app and has a health check at \`/api/health/\`.
- **Fly.io:** paused; its deployment workflow is manual-only. Render is the continuing web-app deployment target. See [deployment options](docs/DEPLOYMENT.md).

Free-tier container filesystems may be ephemeral; configure persistent storage if application data must survive redeploys. The indicator catalogue is re-imported from source data at startup.

<a id="release-notes"></a>
## Release notes

See the [release index](docs/releases/README.md) for the full history and [release 32](docs/releases/32-9e65ede-india-in-maps-and-display-themes.md) for the maps, regrouping, fiscal and cultural atlases, themes and fixes in this release.

<a id="documentation"></a>
## Documentation

<details>
<summary>Browse project guides</summary>

Start with the [documentation index](docs/README.md), then open a focused guide:

| Topic | Guides |
|---|---|
| Data and interpretation | [Sources and limitations](docs/SOURCES-AND-LIMITATIONS.md), [Elections](docs/ELECTIONS.md), [India in Maps](docs/INDIA-IN-MAPS.md), [Tourism and heritage](docs/TOURISM-AND-HERITAGE.md), [Sports](docs/SPORTS.md) |
| Transport and infrastructure | [Air travel](docs/AIR-TRAVEL-AND-CIVIL-AVIATION.md), [Indian Railways](docs/INDIAN-RAILWAYS.md), [Water transport](docs/WATER-TRANSPORT.md), [Logistics and freight](docs/LOGISTICS-AND-FREIGHT.md) |
| Build and operate | [Architecture](docs/ARCHITECTURE.md), [API](docs/API.md), [Pipelines](docs/PIPELINES.md), [Testing](docs/TESTING.md), [Deployment](docs/DEPLOYMENT.md), [Static site and backup](docs/BACKUP.md), [Authentication](docs/AUTHENTICATION.md) |

</details>

<a id="credits-and-licence"></a>
## Credits and licence

This is an independent dashboard built from the public sources cited in the catalogue. Acknowledgements for [PolityPolicy](https://politypolicy.com/), [Polity and Policy on Substack](https://politypolicy.substack.com/) and [Indian Matrix](https://substack.com/@indianmatrix) are provided for attribution and public-data storytelling context; the project does not reproduce their interactive chart rendering. Thanks also to the public agencies and data publishers linked throughout the site.

No \`LICENSE\` or \`LICENCE\` file is currently present in the repository; no project-code reuse licence is asserted here. Third-party data and assets remain subject to their own terms. See [docs/SOURCES-AND-LIMITATIONS.md](docs/SOURCES-AND-LIMITATIONS.md) for source notes and limitations.

[Back to top](#contents)
`,_=n(),v=[[``,`All publishers`],[`indian_matrix`,`Indian Matrix`],[`polity_policy`,`Polity and Policy`],[`pew`,`Pew Research Center`]],y=i.parse(g).replace(/\sid="([^"]+)"/g,` id="readme-$1"`).replace(/href="#([^"]+)"/g,`href="#readme-$1"`).replace(/href="(?!https?:|mailto:|#)([^"]+)"/g,`href="https://github.com/Shubhankart101/India-s-Journey/blob/main/$1"`);function b(e){let t=e.target.closest?.(`a[href^="#readme-"]`),n=t&&document.getElementById(t.hash.slice(1));n&&e.currentTarget.contains(n)&&(e.preventDefault(),n.scrollIntoView({behavior:`smooth`,block:`start`}))}function x(){d(`About`);let e=f(e=>m.stats(e),[]),[t,n]=(0,h.useState)(``),[i,g]=(0,h.useState)(``),x=c(i.trim(),300),[S,C]=(0,h.useState)({kind:``,q:``,page:1}),[w,T]=(0,h.useState)([]);(0,h.useEffect)(()=>{C(e=>e.kind===t&&e.q===x?e:{kind:t,q:x,page:1})},[t,x]);let{page:E}=S,D=e=>C(t=>({...t,page:e(t.page)})),O=f(e=>m.articles({kind:S.kind,q:S.q,page:E,page_size:20},e).then(e=>({...e,page:E})),[S]);return(0,h.useEffect)(()=>{O.data&&T(e=>O.data.page===1?O.data.results:[...e,...O.data.results])},[O.data]),(0,_.jsxs)(_.Fragment,{children:[(0,_.jsxs)(`section`,{className:`page-hero with-art`,children:[(0,_.jsx)(u,{art:a}),(0,_.jsx)(`p`,{className:`eyebrow`,children:`About the atlas`}),(0,_.jsxs)(`h1`,{children:[`Understand the data, `,(0,_.jsx)(`span`,{className:`gradient-text`,children:`not just the line.`})]}),e.data&&(0,_.jsxs)(`p`,{className:`muted`,children:[e.data.indicators.toLocaleString(`en-IN`),` indicators · `,e.data.subgroups,` subgroups · last refresh `,l(e.data.last_refresh)||`pending`]})]}),(0,_.jsxs)(`section`,{className:`section two-col`,id:`about`,children:[(0,_.jsxs)(`div`,{children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`The idea behind the atlas`}),(0,_.jsx)(`h2`,{children:`Big change is easier to see, one signal at a time.`}),(0,_.jsx)(`p`,{children:`India’s story isn’t a single headline or a single number. This independent, public-data project brings together long-run indicators and current snapshots so you can explore what changed, when it changed, and how the evidence is measured.`}),(0,_.jsx)(`p`,{children:`Start with a theme, search for an indicator and narrow the period. Hover for exact values, zoom into a moment, or open any chart for the full series, notes and cited source. Every chart keeps its frequency and limitations visible; unavailable data is never filled with an estimate.`})]}),(0,_.jsxs)(`div`,{children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`Reading the numbers`}),(0,_.jsx)(`h2`,{children:`How numbers are shown`}),(0,_.jsx)(`p`,{children:`Values in U.S. dollars use the international system (thousand, million, billion). Everything else uses the Indian system (lakh, crore).`}),(0,_.jsx)(`p`,{children:`Pie charts show the largest eleven slices and fold the rest into “Other”. Additive categorical charts can switch between pie and bar views.`})]})]}),(0,_.jsxs)(`section`,{className:`section`,children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`Evidence before inference`}),(0,_.jsx)(`h2`,{children:`Public data. Clear provenance.`}),(0,_.jsx)(`p`,{className:`muted`,children:`Each graph links to its underlying source and explains its unit and cadence. Some indicators are annual, some are survey snapshots, and some are assembled from official tables. Read the chart note before comparing unlike measures.`}),(0,_.jsxs)(`div`,{className:`about-steps`,children:[(0,_.jsxs)(`div`,{className:`card about-step`,children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`1 · Choose`}),(0,_.jsx)(`strong`,{children:`Pick a group.`}),(0,_.jsx)(`span`,{className:`muted`,children:`Eleven groups cover the economy, industry, health, environment, agriculture, security, elections and more. Each has subgroups.`})]}),(0,_.jsxs)(`div`,{className:`card about-step`,children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`2 · Inspect`}),(0,_.jsx)(`strong`,{children:`Hover, zoom, switch.`}),(0,_.jsx)(`span`,{className:`muted`,children:`Hover for exact values, zoom in, and switch between line, bar and pie views where the data allows.`})]}),(0,_.jsxs)(`div`,{className:`card about-step`,children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`3 · Verify`}),(0,_.jsx)(`strong`,{children:`Open the source.`}),(0,_.jsx)(`span`,{className:`muted`,children:`Open any chart for the full series, the method and the cited publisher behind each indicator.`})]})]})]}),(0,_.jsx)(`section`,{className:`section two-col`,children:(0,_.jsxs)(`div`,{children:[(0,_.jsx)(`h2`,{children:`Using the data`}),(0,_.jsxs)(`p`,{children:[`Every indicator has its own page with a CSV and JSON download. The same data is available from the `,(0,_.jsx)(`a`,{href:`/api`,children:`API explorer`}),`.`]}),(0,_.jsx)(`p`,{children:`Compare indicators side by side without an account.`}),(0,_.jsx)(`p`,{children:`The complete project README is included below.`})]})}),(0,_.jsxs)(`section`,{className:`section about-readme`,id:`project-readme`,onClick:b,children:[(0,_.jsx)(`h2`,{children:`Project README`}),(0,_.jsx)(`div`,{dangerouslySetInnerHTML:{__html:y}})]}),(0,_.jsxs)(`section`,{className:`section`,id:`pew-research`,children:[(0,_.jsx)(`span`,{className:`eyebrow`,children:`Pew Research indices`}),(0,_.jsx)(`h2`,{children:`Browse the Pew collections`}),(0,_.jsx)(`p`,{className:`muted`,children:`The Pew indicators are grouped under People, Health & Society. Open either subgroup to see its indices and survey snapshots.`}),(0,_.jsx)(`p`,{children:(0,_.jsx)(r,{to:`/explore/people-health-society/pew-research-public-opinion-on-india`,children:`Public opinion on India`})}),(0,_.jsx)(`p`,{children:(0,_.jsx)(r,{to:`/explore/people-health-society/pew-research-reports-survey-snapshots`,children:`Reports and survey snapshots`})})]}),(0,_.jsxs)(`section`,{className:`section`,id:`articles`,children:[(0,_.jsx)(`h2`,{children:`Articles and reports`}),(0,_.jsxs)(`div`,{className:`filter-row`,children:[(0,_.jsx)(`select`,{"aria-label":`Publisher`,value:t,onChange:e=>n(e.target.value),children:v.map(([e,t])=>(0,_.jsx)(`option`,{value:e,children:t},e))}),(0,_.jsxs)(`label`,{className:`search`,children:[(0,_.jsx)(`span`,{className:`sr-only`,children:`Search articles`}),(0,_.jsx)(`input`,{type:`search`,placeholder:`Search article titles`,value:i,onChange:e=>g(e.target.value)})]})]}),O.error&&(0,_.jsx)(o,{error:O.error,onRetry:O.reload}),!O.loading&&!O.error&&w.length===0&&(0,_.jsx)(s,{children:`No articles match.`}),(0,_.jsx)(`ul`,{className:`article-list`,children:w.map(e=>(0,_.jsxs)(`li`,{children:[(0,_.jsx)(`a`,{href:e.url,target:`_blank`,rel:`noopener noreferrer`,children:e.title}),(0,_.jsxs)(`small`,{className:`muted`,children:[e.publisher,` · `,l(e.published_at||e.published)]})]},e.url))}),O.loading&&(0,_.jsx)(p,{label:`Loading articles…`}),O.data?.next&&!O.loading&&(0,_.jsx)(`div`,{className:`center`,children:(0,_.jsx)(`button`,{type:`button`,className:`btn btn-primary`,onClick:()=>D(e=>e+1),children:`Load more`})})]})]})}export{x as default};