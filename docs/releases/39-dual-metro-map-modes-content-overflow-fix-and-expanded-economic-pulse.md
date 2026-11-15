# Release 39: Dual Metro Map Representations, Content Overflow Rectification & Expanded High-Frequency Economic Pulse

## Overview
This release implements the two distinct cartographic and schematic representations requested for all 17 Indian metro cities, eliminates horizontal layout overflow on the content side of the Metro subgroup, and dramatically expands the live high-frequency Economic Pulse dashboard on the home page from 21 to 34 macro indicators matching `politypolicy.com/pulse/`.

---

## Key Deliverables

### 1. Dual Map Representations for All 17 Metro Cities
Commuters and analysts can now toggle between two authentic visual modes for every single Indian rapid transit network:

#### Kind A: Pure White Schematic Transit Diagram (`metrosafar.com/maps` style)
- **Visual Canvas:** Pure crisp white background (`#ffffff`), dark charcoal typography (`#0f172a`), and high-contrast vector lines.
- **Top-Left Floating Legend Box:** Displays the official city route map title (e.g. `Delhi Metro Route Map`), color-coded line bars, and complete transit symbology:
  - `◯ Station` (standard node)
  - `⊚ Interchange` (multi-line junction)
  - `🚆 Railways` (Indian Railways suburban/mainline integration)
  - `✈️ Airport` (airport express link)
  - `🚌 ISBT` (Inter-State Bus Terminal)
- **Clean Octolinear Geometry:** Standardized 45° angles and horizontal lines with directional labels protected by crisp white contrast halos (`stroke="#ffffff" strokeWidth="4.5"`).
- **Branding Badge:** Bottom-right `Metro सफर metrosafar.com` badge with transit logo insignia.

#### Kind B: Geographic Cartography ("Mapped Where It Actually Runs" · `politypolicy.com/DelhiMetro` style)
- **Visual Canvas:** Warm physical terrain parchment (`#fff8f0` / `#faf5ee`), natural river meanders (River Yamuna in Delhi, Hooghly in Kolkata, Mithi in Mumbai, Musi in Hyderabad, etc.), and arterial highway networks.
- **Top-Left Layer Toggles:**
  - `Whole Network` (shows complete active and future corridors)
  - `--- Under Construction` (isolates and highlights Phase 4 / Phase 5 expansion lines)
  - `All Lines` (corridor-specific isolation)
- **Top-Right Floating "PLAN A JOURNEY" Card:**
  - Header: Burgundy bar (`#4a1525` / `#5c1d2e`) with `‹ PLAN A JOURNEY` title and collapse/expand toggle.
  - Interactive `FROM` and `TO` station selectors with instant swap button `⇅`.
  - Action button: `Find The Route` in warm rose (`#b85d77`).
  - Route diagnostic readout: travel time (e.g. `24 min`), distance (`14.2 km`), station count, interchanges, token fare, and smart card discount fare.
  - Clickable station mapping: commuters can click any station on the canvas to assign origin or destination.
- **Bottom-Left Attribution:** OpenStreetMap contributors (ODbL) and official DMRC / MoHUA KML attribution.

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
