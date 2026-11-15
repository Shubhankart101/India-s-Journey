# India's Journey — Release v2.0.0
**Major Milestone Release: Ancient Civilizations, Imperial Atlases, Epigraphy & Mechanical Chronometry**

*Released: November 15, 2026*

---

## 🌟 Executive Summary

Release v2.0 represents the most expansive architectural, geospatial, and content leap in **India's Journey** since inception. This release transforms the platform from a contemporary socio-economic data explorer into a holistic five-millennium living atlas of the Indian subcontinent.

### Key Highlights
1. **Consolidated Archaeological & Imperial Subgroup Articles**: Both *Indus Valley Civilisation* and *Empires of Ancient India* are unified into single comprehensive subgroup articles with integrated interactive workbenches, eliminating navigation clutter and 1-card intermediate grids.
2. **Authentic Geospatial Boundaries & Alexander the Great's Trans-Continental Atlas**: Replaced approximate polygons with high-precision territorial boundaries aligned to `world-asia.json`'s equirectangular projection coordinates (`x = lon * 10`, `y = -lat * 10`). Includes Alexander the Great's trans-continental empire (Macedonia, Egypt, Levant, Mesopotamia, Persia, Bactria to Punjab and the Indus) with dedicated viewbox, animated campaign march route, battle markers, and capital pins.
3. **Living Historical Artwork Carousel**: Dynamic live cycling carousel banner inside both ancient groups showcasing all 16 bespoke SVGs (5 for IVC, 11 for Ancient Empires) with pause-on-hover, selector pills, and live rotating status.
4. **Indus Valley Excavation Atlas & Script Decryption Workbench**: 49 cataloged excavations across 9 countries with official ASI monographs, un-cluttered site markers (prominent labels for 8 metropolises with hover tooltips for all others), and an integrated computational Indus Script decipherment engine.
5. **Split-Flap Mechanical Chronometer & Live IST Horological Watch**: Solari split-flap board tracking elapsed time since August 15, 1947 00:00:00 IST with years, months, days, hours, minutes, and seconds, accompanied by a live analog/digital New Delhi Standard Observatory watch face.
6. **Theme & UI Hardening**: Complete fix for Military (`MIL`) mode header clipping and green line bleed, asset URL resolution preventing 404s on GitHub Pages (`/India-s-Journey/`), and direct card linking to single-subgroup articles.

---

## 📜 Commit History & Change Log

| Commit | Summary | Scope |
| :--- | :--- | :--- |
| `9e3d9a0` | `feat(v2.0): add Empires of Ancient India group, IVC excavation atlas & decoder, split-flap chronometer, live IST watch, and bespoke subgroup art` | Major feature additions, database models, SVG art suite, and React components |
| `97e562a` | `feat: add comprehensive Indus Valley group, indusscript.net translator workbench, and fix military theme header clipping` | IVC data models, decoder frontend, and responsive CSS fixes |
| `78f3faa` | `feat: add Indus Valley Civilisation group, interactive atlas & script decoder, independence clock, subgroup artwork, and fix theme switcher overflow` | Initial chronometer and theme switcher bounds hardening |
| `15aab99` | `Fix header overflow and theme pill clipping in military mode across viewports` | Military mode typography adjustments and overflow handling |
| `1cf9f7e` | `Fix card overflow, align Pew collection placement, update test suites, and rebuild static dashboard` | Layout stabilization, test suite expansion, and static assets |
| `0a423ab` | `fix(v2.0): resolve split-flap timer layout, fix script decoder crash, render subgroup art banners, and make ancient empires accessible on group list` | Split-flap digit card deduplication, decoder array mappings, and subgroup banner art |
| `08f7992` | `fix: restore Indus Valley and Empires of Ancient India in catalog.json and harden export_catalog pipeline` | Pipeline hardening to protect enrichment scripts from scheduled automation overrides |
| `9423daf` | `fix(v2.0): bake slugs into categories, fix asset URL resolution on GitHub Pages, polish split-flap crease, and isolate header decorations` | Defensive category slugification, resilient assetUrl, hairline split-flap crease, and military mode header line isolation |
| `Current` | `feat(v2.0): consolidate IVC and Ancient Empires into unified subgroup articles, authentic geospatial dynastic atlases, and live artwork carousel` | Unified subgroup architecture, precision geospatial empire polygons, Alexander trans-continental map, IVC map decluttering, live art carousel, and legacy alias routing |

---

## 🏛️ Comprehensive Feature Breakdown

### 1. Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions
- **Unified Subgroup Architecture**: Consolidated into one comprehensive subgroup article: `"Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions"` (`empires-of-ancient-india-atlas`).
- **Authentic Geospatial Coordinates**: Bounded to equirectangular coordinates:
  - Pan-Indian viewbox: `600 -380 380 330` covering Kashmir, Punjab, Gandhara, Bengal, Gujarat, Maharashtra, Deccan, and Tamil Nadu.
  - Alexander the Great's trans-continental viewbox: `160 -480 600 290` stretching from Greece and Egypt to the Beas (Hyphasis) and Indus.
- **10 Historical Dynasties & Eras**:
  1. *16 Mahajanapadas & Early Republics (600–345 BCE)*
  2. *Magadha Ascendancy: Haryanka, Shishunaga & Nanda (544–322 BCE)*
  3. *Alexander the Great: Trans-Continental Empire & Indian Frontier (334–323 BCE)*
  4. *Mauryan Empire & Pan-Indian Hegemony (322–185 BCE)*
  5. *Post-Mauryan & Indo-Greek Kingdoms (185 BCE – 10 CE)*
  6. *Satavahana Empire & Deccan Maritime Ascendancy (1st C. BCE – 220 CE)*
  7. *Kushan Empire & The Silk Road Synthesis (30–375 CE)*
  8. *Gupta Empire: The Classical Golden Age (319–550 CE)*
  9. *Vardhana Empire of Harsha (606–647 CE)*
  10. *Classical Southern Dynasties: Chola, Chera, Pandya & Pallava (300 BCE – 850 CE)*
- **Original Script Epigraphs**:
  - Ashokan Brahmi: Rummindei Minor Pillar Inscription
  - Classical Sanskrit: Allahabad Stone Pillar Inscription (Prayag Prashasti) & Banskhera Plate
  - Ancient Greek: Inscriptions of Alexander and the Altars at the Hyphasis
  - Old Tamil (Sangam): Purananuru (poem 192 by Kaniyan Pungundranar)
  - Prakrit: Heliodorus Pillar at Vidisha & Nasik Cave 3 Inscription of Gautamiputra Satakarni
  - Bactrian (Greek script): Rabatak Inscription of Kanishka I
- **Living Artwork Carousel**: Cycles dynamically through all 11 bespoke SVG artworks (`ancient-empires.svg`, `mahajanapadas.svg`, `magadha-nanda.svg`, `alexander-campaign.svg`, `maurya-empire.svg`, `indo-greek.svg`, `satavahana-empire.svg`, `kushan-empire.svg`, `gupta-empire.svg`, `harsha-empire.svg`, `southern-dynasties.svg`).

### 2. Indus Valley Civilisation: Excavations, Urbanism & Script
- **Unified Subgroup Architecture**: Consolidated into one comprehensive subgroup article: `"The Indus Valley Civilisation Comprehensive Excavation Map"` (`the-indus-valley-civilisation-comprehensive-excavation-map`).
- **Interactive Dual Workbench**:
  - `[🗺️ Comprehensive Excavation Map]`: 49 cataloged excavations across 9 countries with ASI Memoirs, Cell, and Nature citations.
  - `[🔤 Script Decryption & Concordance Workbench]`: Mahadevan 1977 & Parpola CISI sign concordances, interactive seal builder, and right-to-left epigraphic reader.
- **Uncluttered GIS Cartography**:
  - Permanent labels reserved for the 8 great metropolises (*Rakhigarhi, Mohenjo-daro, Harappa, Dholavira, Ganweriwala, Kalibangan, Lothal, Banawali*).
  - All other 41 sites rendered as styled interactive nodes with category color coding and floating hover tooltips.
  - Interactive details drawer with excavation monographs, artifacts, and international trade links (Mesopotamia, Dilmun, Magan).
- **Living Artwork Carousel**: Cycles dynamically through all 5 bespoke IVC SVG artworks (`indus-valley.svg`, `ivc-artifacts.svg`, `indus-trade.svg`, `indus-script.svg`, `ivc-excavations.svg`).

### 3. Chronometer & Live IST Horological Watch
- **Split-Flap Historical Chronometer**:
  - 6 mechanical flap units: **Years**, **Months**, **Days**, **Hours**, **Minutes**, **Seconds**.
  - Central hairline split-flap crease and side hinge notches styled after Solari Udine split-flap airport boards.
  - Zero-padded dual flap cards with UTC-anchored IST calendar calculations.
- **Precision Live IST Watch**:
  - 360-degree analog sweeping second hand and hour/minute markers.
  - Real-time New Delhi Standard Time (UTC+05:30) observatory watch face.

### 4. Technical & Pipeline Hardening
- **Automated Catalog Pipeline**: `export_catalog.mjs` and `export_static_api.mjs` safely maintain both ancient categories, single-subgroup mapping, and automatic `docs/build` cleanup.
- **Legacy URL Redirection**: All previous subgroup URLs gracefully alias and resolve to the unified subgroup articles via `legacy-aliases.json`.
- **Test Suite Verification**:
  - Vitest: **17 test files, 127/127 tests passing** (100%).
  - Django: **117/117 unit and API tests passing** (100%).
  - Production static build compiles cleanly with zero errors.
