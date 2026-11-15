# Release 35: Metro in Maps Atlas, High-Frequency Pulse Dashboard, Substack Editorial Articles & Interactive API Platform

**Date:** 2026-11-15  
**Scope:** Interactive Urban Transit Atlas (16 Indian Cities), Real-Time Macro Pulse Dashboard, Substack Editorial Layout, OpenAPI 3.0 Platform Overhaul, Comparative Peer Infographics, and Meticulous Source Documentation.

---

## 1. Executive Summary

Release 35 brings five major architectural and user-experience upgrades across India's Journey:
1. **Interactive API & Developer Platform (`/api`):** Completely overhauled the API page into a first-class, Layout-integrated developer workbench. Features an embedded Swagger UI, ReDoc viewer, syntax-highlighted OpenAPI 3.0 specification with instant search, schema download, and an interactive live endpoint playground that executes requests against both live Django backends and static JSON mirrors.
2. **"Metro in Maps" Urban Transit Workbench (`/explore/india-in-maps/metro-in-maps`):** Created a comprehensive geospatial rapid rail atlas covering all 16 operational and under-construction city metro systems in India (Delhi-NCR, Mumbai, Bengaluru, Kolkata, Chennai, Hyderabad, Ahmedabad, Pune, Kochi & Water Metro, UP Metros). Follows the Indus Valley Civilisation and Ancient Empires article format with interactive SVG vector maps, clickable station inspectors, quoted memoirs from Dr. E. Sreedharan, civil engineering feats (Hooghly underwater tunnel, Mumbai underground Aqua Line 3 basalt rock tunneling), and decadal ridership statistics.
3. **High-Frequency Macroeconomic Pulse Dashboard (Home Page):** Replaced the static group cards list on the home page with an interactive real-time pulse dashboard mirroring `politypolicy.com/pulse/`. Tracks 21 live high-frequency signals (CPI, GST, UPI, PMI, FX Reserves, Rail Freight, Power Demand, Auto Sales) with animated sparklines, YoY/MoM changes, reporting period badges, and economic pillar filters.
4. **Editorial Substack Articles Redesign (`/articles`):** Transformed the `/articles` section into the clean editorial layout titled *"From The Substack"*, featuring responsive 3-column cards with top cover artwork, wine-red uppercase dates (`4 NOV 2026`), bold editorial serif titles, and direct external links.
5. **Comparative Peer Infographics Format:** Introduced rich decadal benchmark comparisons modeled after `infographics.politypolicy.com/g/india-agri-growth-top-exporters-2014-2024` for agriculture, electronics manufacturing, and UPI digital payments.

---

## 2. Detailed Technical Breakdown

### 2.1 Interactive API Platform & Schema Resolution
- **Route Integration:** Moved `<Route path="api" element={<Api />} />` inside `<Route element={<Layout />}>` in `frontend/src/App.jsx`, ensuring full site branding, header navigation, and theme compatibility.
- **Tabbed Developer Console:**
  - **Open Swagger UI:** Embedded Swagger UI sandbox loading `openapi.json` via SwaggerUIBundle with deep linking.
  - **ReDoc:** Three-panel clean technical reference documentation.
  - **OpenAPI 3.0 Schema:** Searchable, syntax-highlighted JSON viewer with "Copy Schema" and "Download openapi.json" buttons.
  - **API Index & Playground:** Interactive request runner for `/api/categories/`, `/api/indicators/`, `/api/stats/`, `/api/articles/`, and `/api/health/` with live status code badges and millisecond latency timers.
- **Schema Build Pipeline:** Updated `scripts/export_static_api.mjs` to generate and preserve `docs/api/openapi.json` and `docs/openapi.json` (53 KB schema generated with `drf-spectacular`).

### 2.2 Metro in Maps Atlas (`india-in-maps/metro-in-maps`)
- **Dataset (`frontend/src/data/metro-networks.json`):**
  - Mapped 16 city systems, 994 km of active routes, 11.2 million daily commuters, and 3.8 million metric tons of annual CO2e emissions avoided.
  - Dedicated dossiers for Delhi DMRC & Namo Bharat RRTS, Mumbai MMRDA/MMRC Line 3, Bengaluru Namma Metro Purple/Green/Yellow, Kolkata Green Line underwater Hooghly tunnel, Chennai CMRL, Hyderabad HMRL, Kochi Rail and battery-electric Water Metro, Ahmedabad GMRC GIFT City corridor, Pune Maha Metro, and UPMRC.
- **Interactive Component (`MetroAtlas.jsx` & `MetroAtlas.css`):**
  - City selection pill navigation.
  - Interactive SVG vector transit maps with line color coding, station hover tooltips, and interchange pulse rings.
  - Station Inspector showing line intersections, daily footfall, depth/elevation, and GPS coordinates.
  - Article-sized historical chronicles, civil engineering breakdowns, and quoted primary memoirs.

### 2.3 High-Frequency Pulse Dashboard (`frontend/src/components/PulseDashboard.jsx`)
- 21 high-frequency macro indicators:
  1. CPI Combined Inflation (4.85% YoY)
  2. Gross GST Collections (₹1.87 Lakh Cr)
  3. UPI Digital Payment Volume (15.04 Billion transactions)
  4. Manufacturing PMI (57.5 Expansion)
  5. Services PMI (58.9 Expansion)
  6. Foreign Exchange Reserves ($688.2 Billion)
  7. Bank Non-Food Credit Growth (+14.8% YoY)
  8. National Power Demand (152.4 Billion Units)
  9. Indian Railways Freight Loading (136.2 Million Tonnes)
  10. Passenger Vehicle Sales (356,800 units)
  11. Two-Wheeler Sales (1.84 Million units)
  12. Diesel Consumption (7.65 MT)
  13. Petrol Consumption (3.24 MT)
  14. Wholesale Price Index Inflation (2.36%)
  15. 10-Year Benchmark G-Sec Yield (6.82%)
  16. USD/INR Exchange Rate (₹84.25)
  17. Merchandise Exports ($34.58 Billion)
  18. Core Sector Output Growth (+3.6% YoY)
  19. Domestic Air Passenger Traffic (13.8 Million)
  20. Major Port Cargo Traffic (68.4 MT)
  21. Finished Steel Consumption (11.8 MT)
- Responsive filter bar: Activity & Demand, Prices & Inflation, Fiscal & Tax, Monetary & Banking, Trade & External.

### 2.4 Substack Editorial Articles Page
- Implemented layout matching `media_1794752837498_c86f0423.jpg`.
- Clean "From The Substack" header with burgundy "See All Writing ↗" link.
- 3-column card grid with cover art (`modi-midterms.svg`, `delhi-police.svg`, `captain-machchhar.svg`), uppercase wine-red dates (`4 NOV 2026`, `12 OCT 2026`, `1 OCT 2026`), and bold serif titles.

### 2.5 Comparative Peer Infographics
- Modeled after `infographics.politypolicy.com/g/india-agri-growth-top-exporters-2014-2024`.
- Integrated `PeerInfographic.jsx` in agricultural, industrial, and payments subgroups.
- Added comparative data tables, global share percentages, decadal CAGR expansion numbers, and strategic paradox callout blocks.

---

## 3. Sources & Documentation Updates
Updated `frontend/src/pages/Sources.jsx` with official publishers:
- Ministry of Housing and Urban Affairs (MoHUA) & Metro Rail Authorities (DMRC, MMRDA, BMRCL, KMRL, CMRL, KMRCL, UPMRC, NCRTC).
- High-Frequency Data Providers: S&P Global, GSTN, PPAC, Central Electricity Authority (CEA), SIAM, NPCI.
- Peer Trade Databases: WTO International Trade Statistics, APEDA, FAOSTAT, ACI Worldwide.

---

## 4. Verification & Testing
- Unit and Explainer Tests: `python -m unittest discover tests` and `pytest tests/test_subgroup_articles.py tests/test_group_explainers.py` (100% pass).
- Frontend Vitest Test Suite: `npm test` (all tests passing).
- Static Production Build: `node scripts/export_static_api.mjs && vite build --mode static` successfully compiled.
