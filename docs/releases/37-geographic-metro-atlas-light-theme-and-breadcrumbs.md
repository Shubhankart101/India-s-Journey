# Release 37: Geographic Metro Atlas ("Where It Actually Runs"), Live IST Train Simulation for 17 Cities, Default Light Theme, Accessible Breadcrumbs & Map De-Cluttering

**Date:** 15 November 2026  
**Commit Type:** Feature / Enhancement / Architectural Alignment  
**Branch:** `main`

---

## 1. Executive Summary

Release 37 delivers major architectural and visual upgrades requested by users:
1. **Delhi Metro "Where It Actually Runs" & 17 Cities Metro Atlas**: Complete cartographic overhaul mapping transit lines along their true geographic curvatures across River Yamuna and NCR terrain, accompanied by a live Indian Standard Time (IST) train simulation engine inspired by `Dtensor/metro-live` and `RomanGolovanov/ametro`.
2. **Default Light Theme**: The application theme defaults to light mode (`data-theme="light"`) with crisp contrast, clean borders, and accessible typography.
3. **Accessible Breadcrumb Navigation**: Implemented `<Breadcrumbs />` at the top of pages adhering to WCAG 2.1 AA specifications.
4. **Ancient Empires Map Layer Selectors & Label De-Cluttering**: Fixed map toolbar responsiveness by adding `pointer-events: auto` to layer filters and implemented smart label rendering (`Labels: Smart / All`), showing capital cities and active items by default to prevent label collisions over northern India.
5. **Home Page Hero Typography & Pulse Dashboard**: Enriched hero font sizes ("A living atlas · 1947 to today" badge and "India, in perspective." with orange-to-cyan gradient), with the 21 High Frequency Indicators Pulse Dashboard serving as the primary interactive workbench.
6. **Quote & Content Semantic Relevance**: Disentangled unrelated indices from shared sections (e.g. separating Smoking Prevalence from Immunisation, and isolating North East Insurgency from J&K and historical Punjab militancy).
7. **Azure Low-Budget Deployment Readiness**: Configured with Terraform for an Azure B1ms App Service + Azure Database for PostgreSQL Flexible Server Burstable B1ms profile strictly capped within the ₹12,500/month infrastructure budget.

---

## 2. Key Capabilities & Technical Specifications

### A. Delhi Metro & All 17 Cities Rapid Transit Atlas
- **True Physical Geography**:
  - Vector course of River Yamuna flowing North-to-South-East (Wazirabad barrage through Kashmere Gate, ITO, Nizamuddin, Okhla, and Kalindi Kunj into UP/Haryana).
  - Ring Road (Mahatma Gandhi Marg), Outer Ring Road, and interstate NCR administrative borders.
- **Complete Line Coverage**:
  - Red Line (Line 1): Rithala to Shaheed Sthal (Ghaziabad)
  - Yellow Line (Line 2): Samaypur Badli to Millennium City Centre (Gurugram)
  - Blue Line (Line 3 & 4): Dwarka Sector 21 to Noida Electronic City and Vaishali
  - Green Line (Line 5): Brig. Hoshiar Singh (Bahadurgarh) to Inderlok & Kirti Nagar
  - Violet Line (Line 6): Kashmere Gate to Raja Nahar Singh (Ballabhgarh)
  - Pink Line (Ring Line 7): 59 km Majlis Park to Shiv Vihar ring corridor
  - Magenta Line (Line 8): Janakpuri West to Botanical Garden via IGI Terminal 1
  - Airport Express Line (Orange Line): New Delhi to Yashobhoomi Dwarka Sector 25
  - Rapid Metro Gurugram: Cyber City loop
  - Aqua Line: Noida Sector 51 to Greater Noida Depot
  - Grey Line (Line 9): Dwarka to Dhansa Bus Stand
  - Phase 4 Under Construction: Golden/Silver Line (Aerocity to Tughlakabad), Magenta North Extension (Janakpuri West to RK Ashram), and Pink Line ring completion
  - Namo Bharat RRTS: Sarai Kale Khan to Meerut South (160 km/h)
- **Live IST Clock Engine**:
  - Live clock synchronized to `Asia/Kolkata` (UTC+5:30).
  - Headway calculation: Peak (08:00–11:30 & 17:00–20:30, 2.5–3.5 min), Off-peak (5–7 min), and Night Maintenance.
  - Animated trains traversing lines with pulsing glow and direction indicators.
- **17 Indian Metro Cities**:
  1. Delhi-NCR (DMRC & RRTS)
  2. Mumbai (Maha Mumbai Metro & Line 3 Aqua Underground)
  3. Bengaluru (Namma Metro Purple, Green, Yellow)
  4. Kolkata (KMRCL Blue Line & Underwater Hooghly Green Line)
  5. Chennai (CMRL Blue & Green Corridors)
  6. Hyderabad (L&T Metro Red, Blue, Green)
  7. Ahmedabad-Gandhinagar (GMRC North-South & East-West)
  8. Pune (MahaMetro Purple & Aqua)
  9. Kochi (KMRL Rail & Water Metro)
  10. Lucknow (UPMRC Red Line)
  11. Kanpur (UPMRC Orange Line)
  12. Agra (UPMRC Yellow Line)
  13. Jaipur (JMRC Pink Line)
  14. Nagpur (MahaMetro Orange & Aqua)
  15. Noida-Greater Noida (NMRC Aqua Line)
  16. Navi Mumbai (CIDCO Line 1)
  17. Bhopal & Indore (MP Metro / Bhoj Metro)
- **Attribution & Sources**:
  - Metro and base geography: © OpenStreetMap contributors, ODbL 1.0.
  - Phase 4 and Phase 5 alignments: Delhi Metro Rail Corporation, influencezone.delhimetrorail.com.
  - Counts cross-checked against DMRC’s network table and Wikipedia’s line table, August 2026.
  - Live IST schematic engine inspired by `Dtensor/metro-live` and `RomanGolovanov/ametro`.

### B. Ancient Empires Atlas De-Cluttering & Selectors
- **Responsive Layer Toolbar**: Added `pointer-events: auto;` to `.map-layer-selector` and `.mls-btn` with `flex-wrap: wrap;` so selector buttons respond instantaneously to clicks.
- **Smart Labels**: Default view renders labels for imperial capitals and selected/hovered sites while maintaining markers for all sites, preventing overlapping label tangles over the Gangetic plain. A toggle button (`🏷️ Labels: Smart / All`) allows users to display all 22+ labels on demand.

### C. Default Light Theme & Accessible Breadcrumbs
- `frontend/src/theme.js` updated so `readStored()` falls back to `'light'` by default.
- `frontend/index.html` initializes with `data-theme="light"` and `#f5f5f7` theme-color.
- Created `frontend/src/components/Breadcrumbs.jsx` with ARIA breadcrumb semantics (`Home > Explore > [Group] > [Subgroup]`).

### D. Semantic Integrity of Subgroup Content
- **Insurgency & Militancy**: Cleanly partitioned into 4 distinct sections:
  1. North East Insurgency: Fatalities, Incidents & Trajectory
  2. Jammu & Kashmir Security: Casualties, Incidents & Counter-Terrorism
  3. Historical Punjab Militancy (1981–1995)
  4. Left-Wing Extremism: Casualties, Security Operations & Infrastructure
- **Public Health**: Separated Adult Smoking Prevalence from Child Immunisation (DPT/Measles) into dedicated sections with contextual descriptions.

---

## 3. Verification & Test Results

- **Vitest Suite**: 18 test files, 132 tests passed (100%).
- **Python Unittest Suite**: 100 tests passed (100%).
- **Vite Static Build**: Successfully compiled to `docs/build/` with static asset bundling.
