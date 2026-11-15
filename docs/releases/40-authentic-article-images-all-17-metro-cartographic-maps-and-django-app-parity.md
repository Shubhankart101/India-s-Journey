# Release 40: Authentic Article Covers, Cartographic Terrain for All 17 Metros & Django Web App Parity

## Overview
This release resolves critical UI and infrastructure enhancements across the application:
1. **Authentic Editorial Article Lead Images:** Completely replaces all synthetic SVG vector cartoons on the Articles page (`#/articles`) with authentic, publisher-sourced photography and lead artwork extracted directly from live Substack feeds (`<enclosure url="...">`), Indian Matrix, and Pew Research Center OpenGraph metadata (`og:image`).
2. **True Cartographic Terrain Maps for All 17 Indian Metro Networks:** Expands the physical terrain canvas engine (`PolityPolicyMetroCanvas.jsx`) from Delhi-only to all 17 operational Indian metro networks (Mumbai, Bengaluru, Kolkata, Chennai, Hyderabad, Kochi, Ahmedabad, Pune, Lucknow, Kanpur, Agra, Jaipur, Nagpur, Noida, Navi Mumbai, Bhopal-Indore, and Delhi-NCR). Every single city now renders real OpenStreetMap-derived physical terrain (rivers, bays, seas, lakes, arterial expressways), GPS-aligned station locations, and interactive Dijkstra shortest-path route planning.
3. **Full-Fledged Django Web App Parity:** Extends Django models, migrations, serializers, and catalog importers with `image_url` support to maintain 100% parity with static API distributions and front-end expectations.
4. **Resilient ReDoc API Explorer Runtime:** Implements a cascading multi-CDN fallback architecture for ReDoc script loading to ensure zero runtime script failures across isolated network environments.

---

## Key Deliverables

### 1. Authentic Article Lead Images (Zero Synthetic SVGs)
- **Direct Publisher Extraction:**
  - Enriched `scripts/collect_substack.py` and `scripts/collect_indian_matrix.py` to parse `<enclosure url="...">` and `<media:content>` tags from RSS/Atom feeds, capturing high-resolution publisher images directly from Substack CDN (`substack-post-media.s3.amazonaws.com` and `substackcdn.com`).
  - Added `scripts/enrich_article_images.py` to extract high-resolution cover photos for articles across Polity & Policy, Indian Matrix, and Pew Research Center.
  - Sourced authentic photography for seminal pieces, including:
    - *What's Next for Modi After the Midterms?* (Official Substack lead image)
    - *Delhi Police And Virtue Of A Disproportionate Response* (Authentic photo of Delhi Police deployment)
    - *Captain Smit Machchhar Saves The Day* (Authentic naval officer photograph)
    - *How IDBI Embalmed Nehruvian Socialism* (Authentic industrial bank archive photograph)
    - *From 'Gunda Raj' to Industrial Engine: UP Law & Order Turnaround* (Authentic infrastructure photo)
    - *What We Know About Eligible Voters Who Are Naturalized U.S. Citizens* (Pew Research original demographic chart image)
- **Frontend Refinement (`frontend/src/pages/Articles.jsx`):**
  - Updated `getArticleCover(article)` to strictly prioritize `article.image_url` and `AUTHENTIC_ARTICLE_IMAGES` mappings.
  - Eliminated fallback to synthetic cartoon vectors (`modi-midterms.svg`, `delhi-police.svg`, `captain-machchhar.svg`, `central-bank.svg`, `counter-terror.svg`).

---

### 2. Physical Cartographic Terrain Maps for All 17 Metro Cities
- **Comprehensive City Cartographic Packs (`frontend/src/data/metro/all_city_packs.js`):**
  - Engineered geographic packs for all 17 Indian metro networks with true GPS latitude/longitude station coordinates, line segments, interchange nodes, arterial expressways, and natural waterways.
  - **Waterways & Physical Terrain per City:**
    - **Mumbai:** Arabian Sea, Mithi River, Mahim Bay, Thane Creek, Sanjay Gandhi National Park.
    - **Bengaluru:** Vrishabhavathi, Bellandur Lake, Sankey Tank, Outer Ring Road (ORR), Hosur Road, NICE Road.
    - **Kolkata:** Hooghly River, Circular Canal, Eastern Metropolitan Bypass (EM Bypass), Belghoria Expressway.
    - **Chennai:** Cooum River, Adyar River, Buckingham Canal, Bay of Bengal, Anna Salai (Mount Road).
    - **Hyderabad:** River Musi, Hussain Sagar Lake, Inner Ring Road, Nehru Outer Ring Road (ORR).
    - **Kochi:** Arabian Sea, Vembanad Lake, Periyar River, Kochi Backwaters, Edappally Canal, NH 544.
    - **Ahmedabad & Gandhinagar:** Sabarmati River, Riverfront Promenade, SG Highway, Sardar Patel Ring Road.
    - **Pune:** Mula River, Mutha River, Sangam Confluence, Mumbai-Pune Bypass, Karve Road.
    - **Lucknow:** Gomti River, Shaheed Path, Lohia Path, Faizabad Road.
    - **Kanpur:** Ganga River, GT Road, Mall Road, Canal Road.
    - **Agra:** Yamuna River, Taj East Drain, Fatehabad Road, MG Road.
    - **Jaipur:** Dravyavati River (Amanishah Nullah), JLN Marg, Ajmer Road, Tonk Road.
    - **Nagpur:** Nag River, Ambazari Lake, Wardha Road, Great Nag Road.
    - **Noida & Greater Noida:** Yamuna River, Hindon River, Noida-Greater Noida Expressway, Yamuna Expressway.
    - **Navi Mumbai:** Thane Creek, Panvel Creek, Sion-Panvel Highway, Palm Beach Road.
    - **Bhopal & Indore:** Upper Lake (Bada Talab), Kaliasot River, VIP Road, Hoshangabad Road; Kahn (Khan) River, AB Road, Super Corridor.
    - **Delhi-NCR:** River Yamuna, River Hindon, Najafgarh Drain, Ring Road, Outer Ring Road, GT Road.
- **Dynamic Terrain Canvas Engine (`PolityPolicyMetroCanvas.jsx`):**
  - Updated canvas renderer to accept dynamic `cityId` props, dynamically loading the corresponding city pack via `getCityPack(cityId)`.
  - Automatic Web Mercator coordinate projections and dynamic viewport bounding-box calculation fitting each metropolitan area.
  - Smooth 2D canvas rendering with pan, drag, pinch-to-zoom, station hover tooltips, and interactive "Set As From" / "Set As To" station callouts.
  - Interactive Dijkstra shortest-path journey planner calculating hop counts, interchanges, travel duration (minutes), and fare estimates for all 17 cities.
- **Atlas Integration (`MetroAtlas.jsx`):**
  - Enabled Cartographic Terrain mode for every city without fallback banners or placeholders.

---

### 3. Full-Fledged Django Web Application Parity
- **Database Schema & Models (`webapp/indicators/models.py`):**
  - Added `image_url = models.URLField(max_length=1000, blank=True, default='')` to the `Article` model.
  - Created and applied migration `webapp/indicators/migrations/0003_article_image_url.py`.
- **REST API Serializers (`webapp/indicators/serializers.py`):**
  - Updated `ArticleSerializer` to include `image_url` in serialized outputs, ensuring full REST API consistency.
- **Catalog Management & Synchronization (`webapp/indicators/catalog.py`):**
  - Updated `import_catalog` command to ingest `image_url` metadata from `data/catalog.json`.
  - Successfully imported 1,457 articles and 3,084 indicators into Django SQLite storage.
- **Static API Exporters:**
  - Updated `scripts/export_catalog.mjs` and `scripts/export_static_api.mjs` to ensure static API distributions in `docs/api/articles.json` maintain `image_url` properties.

---

### 4. Resilient ReDoc API Explorer Runtime
- **Multi-CDN Cascading Script Loader (`frontend/src/pages/Api.jsx`):**
  - Replaced single CDN script tag with a multi-source fallback loader querying:
    1. `https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js`
    2. `https://unpkg.com/redoc@2.1.5/bundles/redoc.standalone.js`
    3. `https://cdn.redoc.ly/redoc/v2.1.5/bundles/redoc.standalone.js`
  - Added embedded OpenAPI reference DOM fallback if all CDNs are unreachable, eliminating the "Redoc is not defined" error screen.

---

## Verification & Quality Assurance
- **Frontend Test Suite (Vitest):** 19 test files, 141 tests passing (100% pass rate).
- **Python Unit Test Suite:** 100 tests passing.
- **Django Test Suite:** 117 tests passing across authentication, API, downloads, rate limiting, and indicators.
- **Static Production Build:** Successfully compiled with Vite into `docs/` and `frontend/dist`.
