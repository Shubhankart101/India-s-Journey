# Release 38: Indian Metro Networks Transit Guide, Route Planner & API ReDoc Runtime Fix

**Release Date:** November 2026  
**Milestone:** Complete Curated Directory & Route Engine (`digitalcreator-dev/indian-metro-networks`), Live IST Schematic Transit (`Dtensor/metro-live`), Physical Yamuna Cartography (`influencezone.delhimetrorail.com`), and ReDoc Dynamic Loader Fix.

---

## 1. Executive Summary

Release 38 addresses two critical operational capabilities:
1. **Permanent Resolution of `Redoc is not defined` Runtime Error:** Completely re-engineered the script loading architecture in `frontend/src/pages/Api.jsx` for both ReDoc and Swagger UI. Implemented dynamic script injection with `onload`/`onerror` handlers and an instant, offline-capable fallback OpenAPI 3.0 specification viewer that parses endpoints, parameters, and responses natively if CDN resources are slow, blocked, or offline.
2. **Indian Metro Networks Full Implementation (`digitalcreator-dev/indian-metro-networks`):** Expanded the Metro Rail Workbench (`MetroAtlas.jsx` & `MetroAtlas.css`) into an authoritative transit guide, route planning engine, and curated system directory across all 17 operational Indian metro networks, integrating physical geography (River Yamuna, Ring Roads, DMRC Phase 4/5 influence zones) and real-time IST clock-synced train simulations (`Dtensor/metro-live`).

---

## 2. API Explorer & ReDoc Dynamic Script Architecture

### Root Cause Analysis
In `frontend/src/pages/Api.jsx`, `redocIframeSrcDoc` formerly embedded `<script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>` followed immediately by `<script>Redoc.init(...)</script>`. In an iframe with `srcDoc`, browsers parse and execute inline scripts synchronously before external scripts have finished fetching over the network, throwing `ReferenceError: Redoc is not defined`.

### Architectural Solution
- **Dynamic Script Loader with Handlers:** Scripts are injected via `document.createElement('script')` with explicit `script.onload`, `script.onerror`, and a fast polling verification loop.
- **Loading Skeleton & Progress Indication:** An animated CSS spinner and branded initialization banner inform the user while the specification viewer initializes.
- **Embedded Offline Fallback Documentation:** If the external CDN takes longer than 3 seconds or fails, the container automatically transitions to a native reference viewer rendering every API path (`/api/stats/`, `/api/categories/`, `/api/indicators/`, `/api/compare/`, `/api/articles/`, `/api/health/`), complete with method badges, summaries, parameter tables, and response status codes.
- **Identical Hardening for Swagger UI:** Implemented symmetric bundle/preset coordination for `SwaggerUIBundle` and `SwaggerUIStandalonePreset`.

---

## 3. Indian Metro Networks: Curated Directory & Transit Guide

Collating from official transit records and open-source benchmarks:
- **Base Geography:** © OpenStreetMap contributors, ODbL 1.0.
- **Alignments & Influence Zones:** Delhi Metro Rail Corporation (`influencezone.delhimetrorail.com`).
- **Network Verification:** DMRC network table and Wikipedia line directory (August 2026).
- **Live IST Engine:** `Dtensor/metro-live` (pure CSS/SVG train animation against Asia/Kolkata clock).
- **Transit Systems Directory:** `digitalcreator-dev/indian-metro-networks` and `RomanGolovanov/ametro`.

### Five Integrated Workbench Tabs

#### Tab 1: 🗺️ Geographic Alignment ("Where It Actually Runs") & High-Resolution Vector Canvas
- **Spacious 1400×1100 Non-Colliding Layout (metrosafar.com/maps):** Expanded spatial coordinates for Delhi-NCR and across all 17 cities, completely eliminating text collisions and unreadable label overlaps in central interchanges (e.g. Rajiv Chowk, Mandi House, Central Secretariat, Hauz Khas, and Kashmere Gate each maintain 80–140px clearance with intelligent label anchors and contrast backing halos).
- **Interactive Map Controls:** Station search bar with real-time text highlight, zoom (+ / − / ↺ reset), smooth click-and-drag panning, and one-click SVG map export.
- **Physical Barriers & Corridors:** River Yamuna with all 4 rapid transit bridge crossings, Najafgarh Drain, Ring Road (Mahatma Gandhi Marg), Outer Ring Road, and inter-state borders.
- **Phase 4 & Phase 5 Alignments:** Golden/Silver Line (Aerocity to Tughlakabad), Janakpuri West to RK Ashram, and Majlis Park to Maujpur.
- **Namo Bharat RRTS:** Semi-high speed 160 km/h regional rapid transit corridor from Sarai Kale Khan through Anand Vihar to Meerut.

#### Tab 2: 🚇 Live Transit Schematic
- Synchronized with the live IST clock (Asia/Kolkata).
- Active train simulation markers traversing lines in both directions (UP/DOWN).
- Real-time headway detection:
  - **Peak Hours (08:00–11:00 & 17:00–20:00 IST):** 2.5–3.5 minute headway (High Frequency Active).
  - **Standard Hours (06:00–23:00 IST):** 5–7 minute headway (Normal Service).
  - **Late Night (23:00–06:00 IST):** 10–15 minute maintenance interval.
- Multilingual station labels in regional scripts (Hindi, Kannada, Bengali, Tamil, Telugu, Marathi, Gujarati, Malayalam).

#### Tab 3: 🧭 Route Planner & Fare Finder
- Interactive Origin and Destination station selectors for any of the 17 cities.
- One-click swap button and presets for popular commuter journeys (e.g., *IGI Airport T3 ↔ Rajiv Chowk*, *Whitefield ↔ Majestic*, *Howrah ↔ Salt Lake Sector V*).
- **Graph Pathfinding (BFS):** Calculates the exact shortest path, number of intermediate stops, and interchange transfer stations.
- **Fare Slab Computation:**
  - `0 – 2 km`: ₹10 (Smart Card: ₹9)
  - `2 – 5 km`: ₹20 (Smart Card: ₹18)
  - `5 – 12 km`: ₹30 (Smart Card: ₹27)
  - `12 – 21 km`: ₹40 (Smart Card: ₹36)
  - `21 – 32 km`: ₹50 (Smart Card: ₹45)
  - `> 32 km`: ₹60 (Smart Card: ₹54)
- **Live Next Departure Countdown:** Synced directly to the active IST seconds and line headway.

#### Tab 4: 📖 Curated Directory & System Matrix
- Multi-city comparative directory covering all 17 operational rapid transit networks in India.
- Search and filtering by city, operator, or track gauge (Standard Gauge 1,435 mm vs Broad Gauge 1,676 mm).
- Metrics tracked per network: Operator, state, launch year, route length (km), stations, daily ridership, track gauge, traction power, rolling stock fleet, and ticketing integration.

#### Tab 5: 📜 Commuter Guide & Passenger Rules
- **Ticketing & Mobility:** National Common Mobility Card (NCMC) open-loop RuPay card interoperability, WhatsApp QR mobile ticketing bots, 10% peak / 20% off-peak smart card discounts, and tourist passes.
- **Women-Only Coaches:** First coach in the direction of travel strictly reserved for women commuters. ₹250 penalty under Section 64 of the Metro Railways Act.
- **Luggage Allowance:** 15 kg maximum per passenger (60 × 45 × 25 cm dimensional envelope).
- **Platform Safety & Emergency Amenities:** Emergency Stop Plunger (ESP) posts, Passenger Emergency Alarm (PEA) audio links, and AED defibrillators at all Station Control Rooms.

---

## 4. Test Verification & Build Integrity

| Test Suite | Total Tests | Passed | Success Rate |
| :--- | :--- | :--- | :--- |
| **Vitest Unit & Integration Suites** | 138 tests | 138 passed | **100%** |
| `src/test/metro-atlas.test.jsx` (New) | 6 tests | 6 passed | **100%** |
| `src/test/pages.test.jsx` (API Explorer) | 31 tests | 31 passed | **100%** |
| **Python Unit Test Suite** | 100 tests | 100 passed | **100%** |
| **Production Static Build** (`npm run build:static`) | 43 bundles | Complete | **0 errors (578 ms)** |
