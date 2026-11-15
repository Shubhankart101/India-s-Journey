# Release 39: Dual Metro Map Representations, Content Overflow Rectification & Expanded High-Frequency Economic Pulse

## Overview
This release implements the two distinct cartographic and schematic representations requested for all 17 Indian metro cities, eliminates horizontal layout overflow on the content side of the Metro subgroup, and dramatically expands the live high-frequency Economic Pulse dashboard on the home page from 21 to 34 macro indicators matching `politypolicy.com/pulse/`.

---

## Key Deliverables

### 1. Dual Map Representations for All 17 Metro Cities
Commuters and analysts can now toggle between two authentic visual modes for every single Indian rapid transit network, sourced directly from the original platforms:

#### Kind A: Official Vector Schematic Transit Diagram (`metrosafar.com/maps`)
- **Direct Asset Integration:** Bundles the official high-resolution vector SVG route maps sourced directly from `metrosafar.com/assets/<city>-metro-map.svg` across all 17 operational Indian metro networks. Every single station, interchange, branch line, and depot is plotted in complete detail.
- **Visual Canvas:** Pure crisp white background (`#ffffff`), dark charcoal typography (`#0f172a`), official route colors, and leader lines.
- **Interactive Stage (`MetroSafarSvgViewer.jsx`):**
  - Smooth pan and drag with mouse and touch gestures.
  - Smooth zoom controls: Zoom In (`+`), Zoom Out (`−`), and Reset (`↺`).
  - **Live Station Search:** Search any station across the network with instant glowing highlight and automatic camera centering.
  - **Download SVG:** One-click download of the complete original SVG map for high-resolution offline use.
  - Official `Metro सफ़र (metrosafar.com)` attribution insignia and route legend card.

#### Kind B: Authentic Geographic Cartography ("Mapped Where It Actually Runs" · `politypolicy.com/DelhiMetro`)
- **Direct Engine & GeoJSON Integration (`PolityPolicyMetroCanvas.jsx`):**
  - Built directly upon the authentic 2.0 MB GeoJSON dataset (`delhi_metro_pack.json`) and Web Mercator Canvas 2D engine from `politypolicy.com/DelhiMetro`.
  - **All 290 Stations Plotted Accurately:** Plots every single station node at its precise geographic GPS latitude and longitude coordinates.
  - **Physical Base Cartography:** Renders true OpenStreetMap physical terrain: River Yamuna, River Hindon, canals, arterial roads (Ring Road, Outer Ring Road), Indian Railways tracks, and NCT district borders.
  - **Phase 4 & Phase 5 Future Alignments:** Displays under-construction corridors and DMRC official influence zones.
- **Top-Left Layer Toggles:**
  - `Whole Network` (shows complete active and future corridors)
  - `--- Under Construction` (isolates and highlights Phase 4 / Phase 5 expansion lines)
  - `All Lines` (isolates active operational lines)
- **Top-Right Floating "PLAN A JOURNEY" Route Planner Card:**
  - Collapsible / minimizable card (`‹ PLAN A JOURNEY` / `−` / `+`) so it never obscures the map view.
  - Autocomplete station selectors covering all 290 stations with instant swap (`⇅`).
  - Authentic Dijkstra shortest-path solver returning duration, distance (km), hop count, interchange stations, and DMRC token vs smart card fares.
  - Interactive station callouts: click any station on the map to trigger "Set As From" or "Set As To".
- **Bottom-Left Attribution:** OpenStreetMap contributors (ODbL) and official DMRC KML documentation.

---

### 2. Subgroup Content Overflow Rectification
All layout elements on the content side of the Metro subgroup have been completely constrained to prevent horizontal spillover:
- **Workbench Grid:** Updated `.metro-workbench-grid` track definitions to use `minmax(0, 1.55fr) minmax(0, 1fr)` instead of fixed fr tracks, preventing child min-content overflow.
- **Dossier Panel:** Added `min-width: 0; max-width: 100%; box-sizing: border-box; overflow-x: hidden; word-break: break-word; overflow-wrap: anywhere;`.
- **Primary Source Cards:** Fixed `.article-primary-sources-grid` to `repeat(auto-fit, minmax(min(100%, 280px), 1fr))` with `box-sizing: border-box`.
- **Stat Highlight Boxes:** Fixed `.article-stat-highlights` to `repeat(auto-fit, minmax(min(100%, 160px), 1fr))` with `overflow-wrap: break-word`.
- **Directory Matrix & Planner:** Ensured tables and form grids enforce `overflow-x: auto; -webkit-overflow-scrolling: touch; max-width: 100%;`.

---

### 3. Expanded High-Frequency Economic Pulse Dashboard (`politypolicy.com/pulse/`)
Expanded `PulseDashboard.jsx` on the Home page from 21 to **34 high-frequency macro indicators**, organized across 5 analytical pillars:

1. **Activity & Demand / Real Economy:**
   - Manufacturing PMI (S&P Global)
   - Services PMI (S&P Global)
   - National Power Demand (CEA / Grid-India)
   - Railway Freight Loading (Ministry of Railways)
   - Passenger Vehicle Sales (SIAM / FADA)
   - Two-Wheeler Sales (SIAM)
   - Commercial Vehicle Sales (MHCV & LCV - SIAM / Vahan)
   - Domestic Tractor Sales (TMA / FADA)
   - Diesel (HSD) Consumption (PPAC / MoPNG)
   - Petrol (MS) Consumption (PPAC / MoPNG)
   - Aviation Turbine Fuel / ATF Demand (PPAC)
   - FASTag Electronic Toll Collections (₹ Cr / Txns - NHAI / IHMCL / NPCI)
   - Core Industries 8-Sector Index (DPIIT / MoCI)
   - Domestic Air Passenger Traffic (DGCA)
   - Domestic Coal Output (Ministry of Coal / CIL)
   - Cement Output Index (Office of Economic Adviser)
   - Finished Steel Consumption (Joint Plant Committee)
   - Crude Steel Production (World Steel / JPC)
2. **Prices & Inflation:**
   - CPI Combined Headline Inflation (MOSPI / NSO)
   - CPI Food & Beverage Inflation (MOSPI / NSO)
   - Wholesale Price Index / WPI (Office of Economic Adviser)
3. **Fiscal & Tax Accounts:**
   - Gross GST Collections (Ministry of Finance / GSTN)
   - Net Direct Tax Collections (CBDT / Ministry of Finance)
4. **Monetary, Banking & Credit:**
   - Foreign Exchange Reserves (Reserve Bank of India)
   - Bank Non-Food Credit Growth (RBI WSS)
   - Aggregate Bank Deposits (RBI WSS)
   - 10-Year Benchmark G-Sec Yield (RBI / CCIL)
   - Exchange Rate USD/INR (RBI Reference Rate)
   - UPI Digital Payments Volume & Value (NPCI)
5. **External Trade & Resilience:**
   - Merchandise Exports (Ministry of Commerce)
   - Merchandise Imports & Trade Deficit (Ministry of Commerce)
   - Services Exports (RBI / MoCI)
   - Major Ports Cargo Traffic (IPA / Ministry of Ports)
   - Foreign Portfolio Inflows / FPI Net Flows (NSDL / SEBI)

---

## Verification & Test Results
- **Vitest Unit Tests:** All 19 test files (140 tests) pass 100% in `frontend`.
- **Python Unit Tests:** All 100 tests pass 100% via `python -m unittest discover tests`.
- **Static API & Build:** Static distribution bundle compiled successfully into `docs/build/`.
