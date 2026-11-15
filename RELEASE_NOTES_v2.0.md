# India's Journey — Release v2.0.0
**Major Milestone Release: Ancient Civilizations, Imperial Atlases, Epigraphy & Mechanical Chronometry**

*Released: November 15, 2026*

---

## 🌟 Executive Summary

Release v2.0 represents the most expansive architectural and content leap in **India's Journey** since inception. This release transforms the platform from a contemporary socio-economic data explorer into a holistic five-millennium living atlas of the Indian subcontinent.

### Key Highlights
1. **Empires of Ancient India (600 BCE – 850 CE)**: A new foundational category with 10 illustrated subgroup eras, dynamic territorial GIS boundaries, battle sites, and epigraphic inscriptions in Sanskrit, Ashokan Brahmi, Ancient Greek, and Sangam Tamil.
2. **Indus Valley Civilisation (IVC) Corpus**: 49+ excavation sites across 9 countries with official ASI monographs, artifact distribution GIS, and a computational **Indus Script Decryption Workbench** modeled on `indusscript.net`.
3. **Split-Flap Mechanical Chronometer & Live IST Horological Watch**: Solari split-flap board tracking elapsed time since August 15, 1947 00:00:00 IST with years, months, days, hours, minutes, and seconds, accompanied by a live analog/digital New Delhi Standard Observatory watch face.
4. **Bespoke Animated SVG Art for All Subgroups**: Every subgroup across all 13 groups features a dedicated, animated SVG illustration with responsive preview banners.
5. **UI & Theme Hardening**: Complete fix for Military (`MIL`) theme header clipping, overflow, and unwanted border stripes; full accessibility of all 13 groups via a sticky horizontal quick-jump bar; and resolution of script decoder object lookups.

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
| `HEAD` | `fix(v2.0): bake slugs into categories, fix asset URL resolution on GitHub Pages, polish split-flap crease, and isolate header decorations` | Defensive category slugification, resilient assetUrl, hairline split-flap crease, and military mode header line isolation |

---

## 🏛️ Comprehensive Feature Breakdown

### 1. Empires of Ancient India (Category #13)
- **10 Historical Subgroups & Eras**:
  1. *Mahajanapadas & Republics (600–321 BCE)*
  2. *Magadha Empire & The Nandas (544–322 BCE)*
  3. *Alexander the Great's Campaign (327–325 BCE)* — Special Macedonian boundary limit
  4. *Mauryan Empire & Ashoka's Pan-Indian Hegemony (322–185 BCE)*
  5. *Indo-Greek Kingdom & Menander I (180 BCE – 10 CE)*
  6. *Satavahana Dynasty & Deccan Sovereignty (230 BCE – 220 CE)*
  7. *Kushan Empire & Kanishka the Great (30–375 CE)*
  8. *Gupta Empire Golden Age (320–550 CE)*
  9. *Harsha's Empire (606–647 CE)*
  10. *Southern Dynasties: Cholas, Cheras, Pandyas & Pallavas (300 BCE – 850 CE)*
- **Epigraphic Inscriptions**: Verified in Ashokan Brahmi, Sanskrit (Devanagari), Ancient Greek (Bactrian bilingual), and Old Tamil (Sangam).
- **Interactive Battle Atlas**: Interactive GIS boundaries depicting imperial expansion, capital moves (Pataliputra, Purushapura, Ujjain, Kanchipuram), and famous conflicts (Hydaspes, Kalinga, Eran, Narmada).

### 2. Indus Valley Civilisation & Epigraphy Decoder
- **Archaeological Corpus**: 49+ excavation sites across 9 countries (India, Pakistan, Afghanistan, Oman, UAE, Bahrain, Kuwait, Iraq, Iran).
- **Official ASI & Scholarly Monographs**: Linked citations from Sir John Marshall, Ernest Mackay, M.S. Vats, S.R. Rao, R.S. Bisht, and J.M. Kenoyer.
- **Indus Script Decryption Workbench**:
  - Sign concordance of Mahadevan & Parpola sign lists.
  - Interactive right-to-left epigraphic reader.
  - Interactive seal builder allowing users to assemble sign sequences.
  - Linguistic hypothesis comparative matrix (Dravidian Rebus, Indo-Aryan, Non-Linguistic).

### 3. Chronometer & Live IST Watch
- **Split-Flap Countdown Board**:
  - 6 mechanical flap units: **Years**, **Months**, **Days**, **Hours**, **Minutes**, **Seconds**.
  - Solid mechanical cards with central crease lines and side hinge notches.
  - Eliminates duplicate text rendering and centers cleanly on all displays.
- **Precision Live IST Watch**:
  - Rotating 360-degree analog hands with sub-second sweeping ticks.
  - Dual analog-digital display anchored to New Delhi Standard Time (UTC+05:30).

### 4. Subgroup Illustrated Artworks
- All subgroups now feature bespoke animated SVGs in both `frontend/public/art` and `docs/art`.
- Replaced obscured dark tiles with dedicated illustrated top banners on each subgroup card.
- Absolute asset URL resolution prevents broken paths on nested client routes.

### 5. UI Polish & Theme Fixes
- **Military Mode (`MIL`)**:
  - Stripped redundant tricolor overlay line, leaving a clean brass accent border (`#d4a72c`).
  - Constrained `.theme-select` height and fixed `Stardos Stencil` font padding to prevent buttons from overflowing.
- **Top Header**:
  - Removed temporary standalone buttons from the main navigation, integrating IVC and Ancient Empires into their proper group hierarchies.
- **Explore Group Quick-Jump**:
  - Added a sticky horizontal pill bar atop the Explore page for 1-click navigation across all 13 groups.

---

## 🧪 Verification & Test Suite

| Test Suite | Result | Details |
| :--- | :--- | :--- |
| **Vitest (Frontend)** | **127 / 127 PASS** | 17 test suites covering routing, chronometer, decoder, maps, and themes |
| **Pytest (Unit & Pipeline)** | **279 / 279 PASS** | 100% test pass rate across data ingest, election results, and geographic atlases |
| **Django Test Suite** | **117 / 117 PASS** | Authentication, indicator APIs, export, and permissions verified |
| **Static Build** | **SUCCESS** | Clean bundle generation in `docs/` and `frontend/dist/` |

---
*Maintained by the India's Journey Engineering Team.*
