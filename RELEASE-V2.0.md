# Release v2.0: Ancient Empires of India, Indus Valley Civilisation Atlas, Subgroup Artwork & Independence Chronometer

**Release Version:** 2.0.0 (Release 33)  
**Catalogue Status:** 13 Top-Level Groups · 148 Subgroups · 3,081 Indicators · 1,457 Articles  
**Validation:** 279/279 Pytest Passed · 127/127 Vitest Passed · 117/117 Django Passed  

---

## Executive Summary

India's Journey v2.0 is a milestone upgrade bringing ancient Indian epigraphy, archaeological excavation atlases, and temporal chronometry into the platform:

1. **Empires of Ancient India (600 BCE – 850 CE):**
   - 10 historical eras mapped with GIS boundary polygons, territory expansion phases, 28+ battle sites with crossed swords `⚔️`, and authentic epigraphs in their original languages and scripts:
     - **16 Mahajanapadas & Early Republics:** Vedic Sanskrit in Devanagari (`त्रयो धर्मस्कन्धा यज्ञोऽध्ययनं दानमिति प्रथमः...`)
     - **Magadha Ascendancy (Haryanka, Shishunaga & Nanda):** Puranic Sanskrit (`सर्वक्षत्रप्रमथनो नन्दः पृथिवीं कृत्स्नामेकच्छत्रां पालयिष्यति...`)
     - **Alexander the Great's Campaign (Special Mention):** Classical Greek (`«Ἐπὶ δὲ τὸν Ὑδάσπην ἧκεν, ἵνα Πῶρος ὁ τῶν Ἰνδῶν βασιλεὺς μετὰ πάσης τῆς δυνάμεως ἔμενεν...»`)
     - **Mauryan Empire & Pan-Indian Hegemony:** Ashokan Prakrit in Brahmi script (`𑀤𑁂𑀯𑀸𑀦𑀁𑀧𑀺𑀬𑁂𑀦 𑀧𑀺𑀬𑀤𑀲𑀺𑀦𑀸 𑀮𑀸𑀚𑀺𑀦𑀸 𑀯𑀺𑀚𑀺𑀢𑁂𑀲𑀼...`)
     - **Post-Mauryan & Indo-Greek Kingdoms:** Bilingual Greek (`ΒΑΣΙΛΕΩΣ ΣΩΤΗΡΟΣ ΜΕΝΑΝΔΡΟΥ`) and Heliodorus Garuda Pillar Sanskrit (`दमस् त्यागॊ अप्रमादस् तेषु त्रिषु अम्रितं पदं...`)
     - **Satavahana Empire & Deccan Maritime Ascendancy:** Prakrit/Sanskrit (`त्रिसमुद्रतोयपीतवाहनस दक्षिणापथपतेः...`)
     - **Kushan Empire & The Silk Road Synthesis:** Bactrian Greek script (`ΒΑΓΟΛΑΓΓΟ... ΚΑΝΗϸΚΙ...`) & Sanskrit
     - **Gupta Empire (Classical Golden Age):** Classical Sanskrit (`सर्वराजोच्छेत्तुः पृथिव्यामप्रतिरथस्य चतुरुदधिपयःस्वादितयशसः...` - Prayag Prashasti)
     - **Vardhana Empire of Harsha:** Classical Sanskrit (`सर्वद्वीपप्रथितकीर्तिः परममाहेश्वरो महाराज-हर्षवर्धनः...`)
     - **Classical Southern Dynasties (Chola, Chera, Pandya, Pallava):** Sangam Classical Tamil (`யாதும் ஊரே யாவரும் கேளிர்...` - Purananuru 192)

2. **Indus Valley Civilisation Group & Decluttered Atlas:**
   - 49 excavated sites categorized into 5 smart tiers: All Sites, 8 Metropolises, 5 Ports, 6 Craft Hubs, and 3 Overseas Gulf Enclaves (Failaka, Ras al-Jinz, Umm an-Nar).
   - Metropolis-only default labeling with interactive hover tooltips prevents map text clutter.
   - Comprehensive archaeological excavation dossier with official ASI memoirs, excavator citations, and carbon dating horizons.
   - Indus Script decryption workbench referenced from [indusscript.net](https://indusscript.net) with 35+ core sign graphemes, frequency distributions across 3,500+ steatite seals, and interactive phonetic decipherment tools.

3. **Mechanical Split-Flap Independence Chronometer & Live IST Watch:**
   - Split-flap dual-digit counter on the Home hero tracking elapsed time since **15 August 1947, 00:00:00 IST** across all 6 time units: `YEARS` : `MONTHS` : `DAYS` : `HOURS` : `MINUTES` : `SECONDS`.
   - Real-time month-boundary calendar calculations taking into account leap years and calendar days.
   - Live analog Indian Standard Time (IST UTC+5:30) watch dial with hour, minute, and second hands, 24-spoke Ashoka Chakra hub, and digital readout.

4. **Bespoke Subgroup Artwork (SVG):**
   - Fixed the CSS stacking bug where `.explore-tile` opaque background was covering `::before` artwork.
   - Created 21 bespoke animated vector SVGs in `frontend/public/art/` and `docs/art/`.

5. **Clean Navigation & Theme Improvements:**
   - Reverted top navigation to the clean standard 7 tabs (`Home`, `Explore`, `Sources`, `Compare`, `About`, `Articles`, `API`).
   - Fixed Military mode header overflow and theme switcher wrapping across small viewports.

---

## Detailed Commit Log

- `HEAD`: Release 33 (v2.0) - Ancient Empires, Indus Valley Atlas, Subgroup Artwork, Independence Chronometer & IST Watch
- `97e562a`: feat: add comprehensive Indus Valley group, indusscript.net translator workbench, and fix military theme header clipping
- `78f3faa`: feat: add Indus Valley Civilisation group, interactive atlas & script decoder, independence clock, subgroup artwork, and fix theme switcher overflow
- `15aab99`: Fix header overflow and theme pill clipping in military mode across viewports
- `1cf9f7e`: Fix card overflow, align Pew collection placement, update test suites, and rebuild static dashboard
- `150285b`: Refresh daily public data
- `910ff21`: Refresh daily public data
- `90a6101`: Refresh daily public data
- `dae9ca5`: Refresh official NJDG court data
- `180862c`: Refresh daily public data
- `86d842c`: Add Articles navigation and page
- `17d0f36`: Fix Pew report indices and embed README in About
- `8e3877f`: Expose Pew indices and README in About
- `888916f`: Update interactive README and docs
- `37c771f`: Add 10 display modes, fix home mini maps and Pages asset paths
- `508b44c`: Fix post-merge data: restore WPI series, sources and sports builder output
- `2769065`: Merge remote data refreshes into release 32
- `d330d8d`: Release 32: India in Maps, articles, elections atlas, epics & faith journeys, five display themes

---

## Test Verification

- `python -m pytest tests`: 279 / 279 passed (100%)
- `npm --prefix frontend test`: 17 / 17 test files, 127 / 127 tests passed (100%)
- `python webapp/manage.py test indicators`: 117 / 117 passed (100%)
- `npm --prefix frontend run build:static`: Succeeded (production bundles in `docs/build`)
