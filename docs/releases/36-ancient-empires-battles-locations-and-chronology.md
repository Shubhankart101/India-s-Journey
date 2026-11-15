# Release 36: Ancient Empires Geospatial Battles, Historical Locations & Dynastic Chronology

**Release Date:** 2026-11-15  
**Scope:** Empires of Ancient India Atlas (`/explore?category=empires-of-ancient-india`)  
**Components:** `AncientEmpiresAtlas.jsx`, `AncientEmpiresAtlas.css`, `frontend/src/data/ancient-empires.json`

---

## 1. Executive Summary

This release expands the **Empires of Ancient India** interactive geospatial atlas to full historical density across all 10 imperial eras (600 BCE – 850 CE). Every empire now features an exhaustive corpus of decisive battlefields with tactical dossiers, major imperial metropolises, fortresses, universities, and oceanic ports, and chronological dynastic milestones, all rendered directly onto the SVG map canvas with layer filtering and two-way synchronisation with the imperial dossier sidebar.

---

## 2. Dynastic Coverage & Data Metric Growth

| Empire / Historical Era | Battles | Locations & Citadels | Milestones | Primary Epigraphs / Sources |
|---|:---:|:---:|:---:|:---:|
| **1. 16 Mahājanapadas & Early Republics** (c. 600–345 BCE) | 6 | 16 | 8 | Anguttara Nikaya, Digha Nikaya, Jataka |
| **2. Magadha Ascendancy (Haryanka, Shishunaga & Nanda)** (c. 544–322 BCE) | 6 | 12 | 8 | Hathigumpha Inscription, Diodorus Siculus, Puranas |
| **3. Alexander the Great: Macedonian Campaign & Indian Frontier** (334–323 BCE) | 10 | 14 | 8 | Arrian Anabasis, Plutarch, Curtius Rufus |
| **4. Mauryan Empire & Pan-Indian Hegemony** (322–185 BCE) | 6 | 15 | 9 | Ashoka Major Rock Edict XIII, Megasthenes Indika |
| **5. Post-Mauryan & Indo-Greek Kingdoms** (c. 185 BCE – 10 CE) | 6 | 12 | 7 | Heliodorus Garuda Pillar, Patanjali Mahabhasya |
| **6. Satavahana Empire & Deccan Maritime Ascendancy** (c. 100 BCE – 225 CE) | 6 | 13 | 6 | Gautami Balashri Nashik Prasasti, Naneghat Inscriptions |
| **7. Kushan Empire & The Silk Road Synthesis** (c. 30–375 CE) | 6 | 12 | 8 | Rabatak Inscription, Hou Hanshu, Kanishka Casket |
| **8. Gupta Empire: The Classical Golden Age** (c. 320–550 CE) | 7 | 12 | 8 | Allahabad Pillar Inscription, Bhitari Inscription |
| **9. Vardhana Empire of Harsha** (606–647 CE) | 6 | 12 | 6 | Aihole Inscription, Bana's Harshacharita, Xuanzang |
| **10. Classical Southern Dynasties (Chola, Chera, Pandya & Pallava)** | 8 | 13 | 8 | Brihadisvara Inscriptions, Tirumalai Inscriptions, Sangam poems |
| **Total Across Atlas** | **67 Battles** | **131 Locations** | **76 Milestones** | **Complete Epigraphic Concordance** |

---

## 3. Geospatial Mapping & Map Canvas Interactivity

1. **Map Layer Selector Toolbar:**
   - `🌐 All Markers`: Renders all decisive battlefields, imperial capitals, and regional metropolises simultaneously.
   - `⚔ Battles Only`: Isolates military clashes, sieges, and campaigns with crossed swords pins.
   - `🏛 Locations Only`: Isolates capitals, citadels, universities, and commercial seaports.

2. **Categorical SVG Marker Badging:**
   - `★` **Imperial Capitals:** Gold marker (`#facc15`) with radiating pulse ring upon selection.
   - `🏛` **Fortified Citadels & Administrative Seats:** Amber marker (`#fb923c`).
   - `⚓` **Maritime Oceanic Ports:** Cyan marker (`#38bdf8`) highlighting ancient Indo-Roman and Southeast Asian trade hubs (Muziris, Barygaza, Sopara, Tamralipti, Puhar, Korkai).
   - `📜` **Universities, Monasteries & Academies:** Purple marker (`#c084fc`) locating premier seats of higher learning (Taxila, Nalanda, Nagarjunakonda, Kanheri).
   - `☸` **Sacred Sanctuaries & Edict Pillars:** Emerald marker (`#34d399`) identifying major Ashokan edict sites and pilgrimage complexes (Sarnath, Lumbini, Sanchi, Deogarh).
   - `⚔` **Decisive Battlefields:** Crimson marker (`#ef4444`) with crossed swords glyph and pulse ring.

3. **Two-Way Workbench Synchronisation:**
   - Clicking any pin on the map centers/highlights the marker and switches the dossier tab to reveal its tactical summary, belligerents, administrative role, or archaeological record.
   - Clicking any entry in the dossier cards auto-highlights the corresponding pin on the geospatial map canvas.

4. **Dedicated Dossier Tab: `🏛 Locations & Cities`:**
   - Integrated alongside `📜 Overview`, `📖 History & Quotes`, `⚔ Battles`, `⏳ Milestones`, and `📚 Sources`.
   - Equipped with quick type filters: `All Sites`, `★ Capitals`, `🏛 Citadels`, `⚓ Ports`, `📜 Academies`, and `☸ Sacred Sites`.

---

## 4. Verification & Testing

- Vitest suite: 18 test files, 132 tests passing (100% pass rate).
- Python test suite: 100 unittest tests and 6 pytest tests passing (100% pass rate).
- Static build (`npm run build:static`): compiled cleanly with static API export (3,084 indicators, 1,457 articles).
