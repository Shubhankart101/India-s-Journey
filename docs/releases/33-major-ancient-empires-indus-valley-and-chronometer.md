# Release 33 (Major Release v2.0): Empires of Ancient India, Indus Valley Civilisation Atlas, Subgroup Artwork, and Independence Chronometer

- **Commit:** [`HEAD`](https://github.com/Shubhankart101/India-s-Journey)
- **Date:** 2026-11-15
- **Catalogue:** 13 groups, 148 subgroups, 3,081 indicators, 1,457 articles at release validation

## Summary

Release 33 (v2.0) is a major milestone expanding India's Journey into classical antiquity and epigraphy. It introduces two major top-level groups: **Empires of Ancient India** (spanning 600 BCE to 850 CE across 10 imperial eras with interactive changing boundaries, 28+ geo-referenced battlefields ⚔️, and authentic original script epigraphs) and **Indus Valley Civilisation** (with a decluttered 49-site excavation atlas, smart tier filtering, and an integrated Indus Script decryption workbench). It also revamps the Home hero with a mechanical split-flap **Independence Chronometer** (tracking Years, Months, Days, Hours, Minutes, and Seconds since 15 August 1947, 00:00:00 IST) paired with a live analog Indian Standard Time watch face, adds 21 bespoke animated SVGs for all subgroups, restores clean 7-link header navigation, and fixes theme overflow in Military mode.

---

## Detailed Commit Log (Releases 32 to 33)

Every commit leading up to this major release is cataloged below with its technical scope:

| Commit | Scope | Description |
|---|---|---|
| `HEAD` | Release 33 (v2.0) | Empires of Ancient India group, 10 imperial eras, decluttered IVC atlas, split-flap chronometer, live IST watch, 21 subgroup SVGs, clean nav, 279 pytest & 127 vitest passing |
| `97e562a` | Feature & UI | Add comprehensive Indus Valley group, indusscript.net translator workbench, and fix military theme header clipping |
| `78f3faa` | Feature & UI | Add Indus Valley Civilisation group, interactive atlas & script decoder, independence clock, subgroup artwork, and fix theme switcher overflow |
| `15aab99` | Bug Fix | Fix header overflow and theme pill clipping in military mode across mobile and desktop viewports |
| `1cf9f7e` | Bug Fix & QA | Fix card overflow, align Pew collection placement, update test suites, and rebuild static dashboard |
| `150285b` | Pipeline | Refresh daily public data |
| `910ff21` | Pipeline | Refresh daily public data |
| `90a6101` | Pipeline | Refresh daily public data |
| `dae9ca5` | Pipeline | Refresh official NJDG court data across High Courts and District Courts |
| `180862c` | Pipeline | Refresh daily public data |
| `86d842c` | Feature | Add Articles navigation and page with source classification (Indian Matrix, PolityPolicy, Pew, Other) |
| `17d0f36` | Feature & Docs | Fix Pew report indices and embed README in About |
| `8e3877f` | Feature | Expose Pew indices and README in About modal and static route |
| `888916f` | Docs | Update interactive README and documentation suite |
| `37c771f` | Feature & UI | Add 10 display modes, fix home mini maps, and correct GitHub Pages asset paths |
| `508b44c` | Bug Fix | Fix post-merge data: restore WPI series, sources, and sports builder output |
| `2769065` | Maintenance | Merge remote data refreshes into release 32 |
| `d330d8d` | Release 32 | India in Maps, articles, elections atlas, epics & faith journeys, five display themes |

---

## Highlights of Major Additions

### 1. Empires of Ancient India (600 BCE – 850 CE)

A new flagship group accessible from `/explore/empires-ancient-india` and the Home explore grid, cataloging ten imperial eras with interactive changing boundary polygons, 28 decisive battlefields marked with crossed swords `⚔️`, and authentic epigraphs in their original languages and scripts:

| Imperial Era | Period | Primary Religion / Ideology | Original Script & Epigraph / Shloka | Scholarly Source |
|---|---|---|---|---|
| **16 Mahajanapadas & Early Republics** | 600–345 BCE | Vedic Brahmanism / Early Sramanic | **Sanskrit (Devanagari):**<br>त्रयो धर्मस्कन्धा यज्ञोऽध्ययनं दानमिति प्रथमः...<br>*(Three are the branches of Dharma: sacrifice, study, and charity... — Chandogya Upanishad 2.23.1)* | Archaeological Survey of India; Anguttara Nikaya |
| **Magadha Ascendancy: Haryanka, Shishunaga & Nanda** | 544–322 BCE | Vedic & Ajivika / Jain patronage | **Sanskrit (Devanagari):**<br>सर्वक्षत्रप्रमथनो नन्दः पृथिवीं कृत्स्नामेकच्छत्रां पालयिष्यति...<br>*(Destroyer of all Kshatriyas, Nanda brought the entire earth under a single umbrella — Matsya Purana)* | Puranic Dynastic Lists & Curtius Rufus |
| **Alexander the Great's Campaign (Special Mention)** | 327–325 BCE | Hellenic Polytheism | **Ancient Greek:**<br>«Ἐπὶ δὲ τὸν Ὑδάσπην ἧκεν, ἵνα Πῶρος ὁ τῶν Ἰνδῶν βασιλεὺς μετὰ πάσης τῆς δυνάμεως ἔμενεν...»<br>*(To the Hydaspes he came, where Porus king of the Indians waited with all his army — Arrian, Anabasis of Alexander V.8)* | Arrian (Anabasis of Alexander) & Plutarch |
| **Mauryan Empire & Pan-Indian Hegemony** | 322–185 BCE | Buddhism / Dhamma | **Ashokan Prakrit in Brahmi Script:**<br>𑀤𑁂𑀯𑀸𑀦𑀁𑀧𑀺𑀬𑁂𑀦 𑀧𑀺𑀬𑀤𑀲𑀺𑀦𑀸 𑀮𑀸𑀚𑀺𑀦𑀸 𑀯𑀺𑀚𑀺𑀢𑁂𑀲𑀼 𑀲𑀯𑀢 𑀥𑀁𑀫𑀮𑀺𑀧𑀺 𑀮𑀺𑀔𑀺𑀢𑀸<br>*(Everywhere in the conquered dominions of King Priyadarsin, Beloved of the Gods, this Dhamma edict was inscribed — Major Rock Edict I)* | Corpus Inscriptionum Indicarum Vol. I (ASI) |
| **Post-Mauryan & Indo-Greek Kingdoms** | 185 BCE – 10 CE | Greco-Buddhist / Bhagavata Vaishnavism | **Bilingual Greek & Sanskrit Brahmi:**<br>Greek: ΒΑΣΙΛΕΩΣ ΣΩΤΗΡΟΣ ΜΕΝΑΝΔΡΟΥ<br>Brahmi: दमस् त्यागॊ अप्रमादस् तेषु त्रिषु अम्रितं पदं...<br>*(Restraint, renunciation, and vigilance: by these three immortal steps heaven is gained — Heliodorus Garuda Pillar at Vidisha, c. 113 BCE)* | Archaeological Survey of India Memoir No. 1 |
| **Satavahana Empire & Deccan Maritime Ascendancy** | 2nd C. BCE – 220 CE | Vedic & Buddhist | **Prakrit (Brahmi) / Sanskrit:**<br>वरवारणविक्रमचारुविक्रमस त्रिसमुद्रतोयपीतवाहनस दक्षिणापथपतेः...<br>*(Lord of Dakshinapatha whose cavalry drank the waters of the three oceans — Nashik Cave Inscription of Gautami Balashri)* | Epigraphia Indica Vol. VIII (ASI) |
| **Kushan Empire & The Silk Road Synthesis** | 30–375 CE | Sarvastivada Buddhism / Syncretic | **Bactrian (Greek Script) & Sanskrit:**<br>«ΒΑΓΟΛΑΓΓΟ... ΚΑΝΗϸΚΙ ΚΟϸΑΝΟ...»<br>महाराजस्य राजातिराजस्य देवपुत्रस्य कनिष्कस्य...<br>*(In the year of the Great King, King of Kings, Son of Heaven, Kanishka — Rabatak Inscription & Mathura Inscriptions)* | UNESCO Silk Roads Project & British Museum |
| **Gupta Empire: Classical Golden Age** | 319–550 CE | Classical Puranic Hinduism (Vaishnavism) | **Classical Sanskrit (Devanagari):**<br>सर्वराजोच्छेत्तुः पृथिव्यामप्रतिरथस्य चतुरुदधिपयःस्वादितयशसः धनद-वरुणेन्द्रान्तक-समस्य...<br>*(Exterminator of all rival kings, without equal upon earth, whose fame tasted the waters of the four oceans — Prayag Prashasti of Harishena, Allahabad Pillar)* | Corpus Inscriptionum Indicarum Vol. III (ASI) |
| **Vardhana Empire of Harsha** | 606–647 CE | Shaivism / Mahayana Buddhism | **Classical Sanskrit (Devanagari):**<br>सर्वद्वीपप्रथितकीर्तिः परममाहेश्वरो महाराज-हर्षवर्धनः... स्वहस्तो मम महाराजाधिराज-श्रीहर्षस्य<br>*(Whose fame is celebrated in all continents, devout worshipper of Mahesvara... Hand signature of Maharajadhiraja Sri Harsha — Madhuban & Banskhera Copper Plates)* | Epigraphia Indica Vol. IV & Harshacharita |
| **Classical Southern Dynasties (Chola, Chera, Pandya, Pallava)** | 300 BCE – 850 CE | Sangam / Shaivism & Vaishnavism | **Sangam Classical Tamil:**<br>யாதும் ஊரே யாவரும் கேளிர் தீதும் நன்றும் பிறர்தர வாரா...<br>*(To us all towns are one, all people our kin; good and evil come not from others — Purananuru 192)* | Tamil Nadu State Department of Archaeology |

---

### 2. Indus Valley Civilisation Comprehensive Group & Decluttered Atlas

- **Atlas Decluttering:** Filter 49 excavated sites across 5 categories (`All 4Metropolises`, `5 Ports`, `6 Craft Hubs`, `3 Overseas Gulf Enclaves`). Zoom controls (`+`, `-`, `Reset`) and region focus presets (`All Sites`, `Sindh & Punjab`, `Gujarat & Coast`, `Ghaggar-Hakra Basin`, `Overseas Hubs`) eliminate text overlapping.
- **Metropolis-First Labeling:** Only the primary metropolises (Mohenjo-daro, Harappa, Rakhigarhi, Dholavira, Ganweriwala, Lothal, Kalibangan, Chanhudaro) render permanent text labels on the map canvas; secondary sites display elegant tooltips on hover to prevent visual clutter.
- **Excavation Dossier:** Right-hand sliding drawer presents comprehensive ASI excavation history, excavator credits (Sir John Marshall, Daya Ram Sahni, R.D. Banerji, Dr. R.S. Bisht, Prof. Vasant Shinde), carbon-14 dating horizons, UNESCO status, and direct links to the script decoding workbench.
- **Decryption Workbench:** Direct phonetic transliteration tool referenced from [indusscript.net](https://indusscript.net) covering 35+ core sign graphemes (fish, jar, horned deity, unicorn, pipal leaf), bilingual comparative concordances, sign frequencies across 3,500+ steatite seals, and step-by-step seal decipherment walkthroughs.

---

### 3. Historical Independence Chronometer & Live IST Watch

- **Mechanical Split-Flap Chronometer:** Dual-digit split-flap countdown display in the Home hero with center horizontal flap crease and hinge notches, continuously calculating the live elapsed interval since **15 August 1947, 00:00:00 IST**:
  - `YEARS` : `MONTHS` : `DAYS` : `HOURS` : `MINUTES` : `SECONDS`
  - Real-time month-boundary calendar arithmetic handling leap years and varying month lengths.
- **Indian Standard Time (IST UTC+5:30) Analog Watch:**
  - Located directly below the flip-flap chronometer, featuring an authentic analog watch dial with 12 hour ticks, smooth sweep second hand, navy-blue hour/minute hands, and a 24-spoke Ashoka Chakra center hub.
  - Accompanied by a live digital readout formatted as `HH:MM:SS IST · UTC+05:30`.

---

### 4. Bespoke Vector Artwork for All Subgroups

- **Root Cause Fix:** Resolved the issue where subgroup cards appeared pitch black. In `frontend/src/styles.css`, `.explore-tile` had an opaque `background: var(--surface)` which obscured the `::before` pseudo-element background art. Setting `background-color: transparent` restored vivid full-card illustrations across all themes.
- **21 New Animated SVGs:** Created bespoke SVGs in `frontend/public/art/` and `docs/art/`:
  - `ancient-empires.svg`, `mahajanapadas.svg`, `magadha-nanda.svg`, `alexander-campaign.svg`, `maurya-empire.svg`, `indo-greek.svg`, `satavahana-empire.svg`, `kushan-empire.svg`, `gupta-empire.svg`, `harsha-empire.svg`, `southern-dynasties.svg`, `ivc-excavations.svg`, `ivc-architecture.svg`, `savings-investment.svg`, `union-receipts.svg`, `borrowing-debt.svg`, `state-fiscal-welfare.svg`, `hockey-india.svg`, `football-india.svg`, `supreme-civil.svg`, `supreme-criminal.svg`.

---

### 5. Header Navigation & Theme Fixes

- **Clean 7-Link Navigation:** Reverted header to standard 7 items: `Home`, `Explore`, `Sources`, `Compare`, `About`, `Articles`, `API`. Removed protruding top-level buttons for Indus Valley and Script Decryption, nesting them properly within `/explore/indus-valley-civilisation`.
- **Military Mode Theme Fix:** Fixed header button wrapping and theme switcher clipping in `styles.css` using `min-width: 0` and flex-wrap safeguards.

---

## Validation & Test Suite Results

| Test Suite | Tests Run | Result | Notes |
|---|---:|---|---|
| **Python Pytest Suite** | 279 | **279 Passed** (100%) | Covers GIS layers, group explainers, catalog export, scripture verses, atlases, source audits |
| **Frontend Vitest Suite** | 127 | **127 Passed** (100%) | Covers React 19 pages, navigation, map selectors, compare tray, scripture cards, theme switcher |
| **Django Indicator Tests** | 117 | **117 Passed** (100%) | Covers REST endpoints, catalog import, stats, compare API, auth views, download responses |
| **Static Build Verification** | 1 | **Passed** | `npm run build:static` bundles all static assets into `docs/build` without errors |

---

## Deployment & Upgrade Notes

1. Run `python scripts/add_ancient_empires_and_art.py` to ensure `data/catalog.json` contains all 13 groups and 3,081 indicators.
2. Run `python scripts/build_explainers.py` to compile `frontend/src/data/group-explainers.json`.
3. In Django, execute `python webapp/manage.py import_catalog` to synchronize the SQLite/PostgreSQL database with the new 13-group schema.
4. Run `npm --prefix frontend run build:static` to compile client assets into `docs/build`.
