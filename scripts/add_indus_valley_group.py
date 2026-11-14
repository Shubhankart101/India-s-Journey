import json

CATALOG_PATH = 'data/catalog.json'
EXPLAINERS_PATH = 'frontend/src/data/group-explainers.json'

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open(EXPLAINERS_PATH, 'r', encoding='utf-8') as f:
    explainers = json.load(f)

# Check if Indus Valley Civilisation already exists
cat_exists = any(c['name'] == 'Indus Valley Civilisation' for c in catalog['categories'])
if not cat_exists:
    ivc_category = {
        "name": "Indus Valley Civilisation",
        "order": len(catalog['categories']),
        "title": "Indus Valley Civilisation",
        "description": "Urban planning, metallurgy, maritime trade networks, undeciphered script, and material culture of the Bronze Age Indus civilization (c. 3300 – 1300 BCE).",
        "badges": ["Archeology", "Bronze Age", "Epigraphy", "Maritime Trade"],
        "color": "#d4a72c",
        "icon": "citadel",
        "art": "indus-valley.svg",
        "subgroups": [
            {
                "name": "Metropolises & Major Urban Centers",
                "order": 0,
                "title": "Metropolises & Major Urban Centers",
                "description": "Grid plans, baked brick citadels, sophisticated drainage networks, and monumental water reservoirs across Mohenjo-daro, Harappa, Rakhigarhi, Dholavira, and Ganweriwala.",
                "art": "indus-valley.svg"
            },
            {
                "name": "Artifacts, Statuary & Material Culture",
                "order": 1,
                "title": "Artifacts, Statuary & Material Culture",
                "description": "Lost-wax bronze statuary (Dancing Girl), steatite sculpture (Priest-King), terracotta figurines, micro-beads, etched carnelian, and standardized binary-decimal chert weights.",
                "art": "ivc-artifacts.svg"
            },
            {
                "name": "Maritime Trade & International Artifacts",
                "order": 2,
                "title": "Maritime Trade & International Artifacts",
                "description": "The world's earliest tidal dockyard at Lothal, oceanic trade corridors across the Arabian Sea, and Harappan seals and weights recovered in Mesopotamia (Ur, Kish), Iran (Susa), and the Persian Gulf.",
                "art": "indus-trade.svg"
            },
            {
                "name": "Indus Script & Alphabet Decoding",
                "order": 3,
                "title": "Indus Script & Alphabet Decoding",
                "description": "Concordance of 400+ signs, right-to-left epigraphy, the Dholavira 10-glyph citadel signboard, positional entropy, and Dravidian, Indo-Aryan, and non-linguistic decipherment models.",
                "art": "indus-script.svg"
            },
            {
                "name": "Chronology, Settlement Geography & Legacy",
                "order": 4,
                "title": "Chronology, Settlement Geography & Legacy",
                "description": "From Early Harappan village regionalization (3300 BCE) through Mature urban integration to Late Harappan de-urbanization, monsoon shifts, and cultural continuity in historical India.",
                "art": "harappan-seals.svg"
            }
        ]
    }
    catalog['categories'].append(ivc_category)

# Add IVC Indicators
ivc_indicators = [
    {
        "key": "ivc_urban_settlement_area",
        "title": "Excavated Urban Settlement Area of Major Indus Cities",
        "subtitle": "Estimated maximum urban extent in hectares during Mature Harappan phase",
        "frequency": "archeological",
        "color": "#d4a72c",
        "suffix": " ha",
        "source_url": "https://asi.nic.in",
        "details": "Comparative urban footprint in hectares across primary Indus metropolises based on archeological surveys by ASI and international missions.",
        "category": "Indus Valley Civilisation",
        "subgroup": "Metropolises & Major Urban Centers",
        "position": 0,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archeological Survey of India & Harappa Archaeological Research Project",
            "labels": ["Rakhigarhi", "Mohenjo-daro", "Harappa", "Dholavira", "Ganweriwala", "Kalibangan", "Lothal", "Chanhudaro", "Banawali", "Surkotada"],
            "datasets": [
                {
                    "label": "Settlement Area (ha)",
                    "values": [350, 300, 150, 100, 80, 25, 20, 15, 12, 5]
                }
            ]
        }
    },
    {
        "key": "ivc_steatite_seals_by_site",
        "title": "Inscribed Steatite Seals Discovered by Major Archeological Site",
        "subtitle": "Count of cataloged Indus seals, tablets, and inscribed sealings",
        "frequency": "archeological",
        "color": "#38bdf8",
        "suffix": " seals",
        "source_url": "https://asi.nic.in",
        "details": "Distribution of inscribed seals and tokens across Indus Valley excavations cataloged in the Corpus of Indus Seals and Inscriptions (CISI).",
        "category": "Indus Valley Civilisation",
        "subgroup": "Artifacts, Statuary & Material Culture",
        "position": 1,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Corpus of Indus Seals and Inscriptions (Parpola & Joshi)",
            "labels": ["Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Dholavira", "Chanhudaro", "Rakhigarhi", "Foreign Sites (Ur, Susa, Kish, Failaka)"],
            "datasets": [
                {
                    "label": "Inscribed Seals Discovered",
                    "values": [2500, 1400, 213, 105, 80, 68, 45, 62]
                }
            ]
        }
    },
    {
        "key": "ivc_international_trade_distance",
        "title": "Ancient Maritime & Overland Trade Distances from Indus Ports",
        "subtitle": "Navigational and caravan trade distances from Lothal & Sutkagan Dor in kilometres",
        "frequency": "geographical",
        "color": "#fb923c",
        "suffix": " km",
        "source_url": "https://asi.nic.in",
        "details": "Oceanic and inland trade corridor distances connecting the Indus heartland to Dilmun, Magan, Elam, and Mesopotamia during the 3rd millennium BCE.",
        "category": "Indus Valley Civilisation",
        "subgroup": "Maritime Trade & International Artifacts",
        "position": 2,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "National Institute of Oceanography (NIO) & Possehl Maritime Studies",
            "labels": ["Lothal to Ras al-Jinz (Oman/Magan)", "Lothal to Failaka Island (Dilmun)", "Lothal to Ur (Mesopotamia)", "Harappa to Shortugai (Lapis Colony)", "Lothal to Susa (Elam)", "Sutkagan Dor to Bandar Abbas"],
            "datasets": [
                {
                    "label": "Distance (km)",
                    "values": [1280, 2150, 2600, 1150, 2400, 750]
                }
            ]
        }
    },
    {
        "key": "ivc_top_script_signs_frequency",
        "title": "Corpus Frequency of Top Indus Script Signs",
        "subtitle": "Total occurrences in the Mahadevan (1977) epigraphical concordance",
        "frequency": "epigraphical",
        "color": "#a855f7",
        "suffix": " occurrences",
        "source_url": "https://asi.nic.in",
        "details": "Frequency of the most recurrent signs across 4,124 cataloged Indus texts according to Iravatham Mahadevan's computer concordance.",
        "category": "Indus Valley Civilisation",
        "subgroup": "Indus Script & Alphabet Decoding",
        "position": 3,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "The Indus Script: Texts, Concordance and Tables (Mahadevan 1977)",
            "labels": ["Jar / Vessel Sign (M-342)", "Arrow / Spear Sign (M-48)", "Fish Sign (M-59)", "Double Stroke (M-102)", "Pincer / Bearer (M-211)", "Comb Sign (M-176)", "Horned Deity (M-1)", "Wheel / Sun Sign (M-391)", "Archer Sign (M-49)", "Diamond Sign (M-267)"],
            "datasets": [
                {
                    "label": "Corpus Occurrences",
                    "values": [1395, 620, 580, 310, 275, 230, 210, 185, 160, 145]
                }
            ]
        }
    },
    {
        "key": "ivc_radiocarbon_phases",
        "title": "Chronological Span of Indus Valley Civilisation Eras",
        "subtitle": "Span in years based on calibrated radiocarbon dating",
        "frequency": "chronological",
        "color": "#10b981",
        "suffix": " years span",
        "source_url": "https://asi.nic.in",
        "details": "Calibrated carbon-14 duration of the Early Harappan (regionalization), Mature Harappan (urban integration), and Late Harappan (localization) phases.",
        "category": "Indus Valley Civilisation",
        "subgroup": "Chronology, Settlement Geography & Legacy",
        "position": 4,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Possehl (2002) & Shaffer Radiocarbon Calibration Synthesis",
            "labels": ["Early Harappan (3300-2600 BCE)", "Mature Harappan (2600-1900 BCE)", "Late Harappan (1900-1300 BCE)"],
            "datasets": [
                {
                    "label": "Span (Years)",
                    "values": [700, 700, 600]
                }
            ]
        }
    }
]

# Append indicators if not present
existing_keys = {ind['key'] for ind in catalog['indicators']}
for ind in ivc_indicators:
    if ind['key'] not in existing_keys:
        catalog['indicators'].append(ind)

with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Updated {CATALOG_PATH}: categories={len(catalog['categories'])}, indicators={len(catalog['indicators'])}")

# Update group-explainers.json
exp_exists = any(g['name'] == 'Indus Valley Civilisation' for g in explainers['groups'])
if not exp_exists:
    ivc_explainer = {
        "name": "Indus Valley Civilisation",
        "article": {
            "pattern": "archeological-civilisation",
            "headline": "The Bronze Age Metropolis of the Indus",
            "dek": "Across 1.5 million square kilometres from the Oxus to the Arabian Sea, the Harappan world pioneered grid-iron urban planning, sanitary hydraulics, standard metrology, oceanic seafaring, and an enigmatic undeciphered script.",
            "paragraphs": [
                "The Indus Valley Civilisation (c. 3300 – 1300 BCE) represents one of the three foundational cradles of Afro-Eurasian urban civilisation alongside Egypt and Mesopotamia, yet it surpassed both in geographical extent, standardized metrology, and public sanitation.",
                "From the high citadels and Great Bath of Mohenjo-daro to the massive stone-cut rainwater reservoirs of Dholavira and the tidal lock-gates of Lothal, Harappan engineers developed a hydraulic civilization unequaled until the Roman empire.",
                "Overseas records from King Sargon of Akkad (c. 2334 BCE) document masted seafaring vessels docking at Mesopotamian quays bearing timber, carnelian beads, copper, and lapis lazuli from 'Meluhha'—the Sumerian designation for the Indus realm."
            ],
            "watch": "Epigraphic decipherment computational breakthroughs, Rakhigarhi ancient DNA paleogenomics, and underwater survey of submerged coastal ports in the Gulf of Khambhat.",
            "sources": [
                "Archeological Survey of India (ASI) Centennial Excavation Reports",
                "Corpus of Indus Seals and Inscriptions (CISI, Vols 1–3, Asko Parpola & Jagat Pati Joshi)",
                "The Indus Script: Texts, Concordance and Tables (Iravatham Mahadevan, ASI 1977)",
                "The Indus Civilization: A Contemporary Perspective (Gregory L. Possehl, 2002)"
            ],
            "indicatorCount": 5,
            "subgroupCount": 5,
            "verse": {
                "id": "rv-10-75",
                "source": "Rigveda 10.75 (Nadistuti Sukta)",
                "original": "सिन्धोः प्रभावे तद् अस्य वर्धते यत् स्तोतृभ्यः शंस्यं राध एति।",
                "translation": "By the mighty power of the Indus, may fortune flourish and abundance flow unto the singers."
            },
            "subgroups": [
                {
                    "name": "Metropolises & Major Urban Centers",
                    "headline": "Citadels, Grid Plans & The Great Baths",
                    "dek": "From Rakhigarhi (350 ha) and Mohenjo-daro to Dholavira's rock-cut hydraulic reservoirs, Harappan metropolises balanced civic order, covered sanitation, and civic architecture without monumental royal palaces or militaristic triumphal arches.",
                    "paragraphs": ["Urban sanitation was unparalleled in the ancient world, with covered street drains, soak-pits, private indoor baths, and multi-story brick residential architecture."],
                    "watch": "Ongoing excavations at Rakhigarhi mounds 4 and 7 revealing cemetery practices and elite residential quarters.",
                    "sources": ["ASI Reports", "HARP Excavations"],
                    "indicatorCount": 1,
                    "sections": [
                        {
                            "title": "Urban Planning & Hydraulic Genius",
                            "text": "Every major Harappan city was laid out on an aligned orthogonal grid with cardinal orientations. Standardized fired bricks with a strict 4:2:1 dimensional ratio were utilized across hundreds of settlements spanning thousands of kilometres.",
                            "keys": ["ivc_urban_settlement_area"]
                        }
                    ]
                },
                {
                    "name": "Artifacts, Statuary & Material Culture",
                    "headline": "Lost-Wax Bronzes, Priest-Kings & Micro-Beads",
                    "dek": "Indus metallurgy produced the naturalistic lost-wax bronze Dancing Girl, intricate steatite micro-bead necklaces, etched carnelian exported across the ancient world, and binary-decimal standard chert weights.",
                    "paragraphs": ["Harappan craft specialization reached industrialized scales, with specialized quarters at Chanhudaro and Lothal dedicated to lapidary bead drillings, shell bangle cutting, and copper smelting."],
                    "watch": "Trace-element isotopic sourcing of copper ingots and lapis lazuli beads.",
                    "sources": ["National Museum New Delhi", "Karachi Museum"],
                    "indicatorCount": 1,
                    "sections": [
                        {
                            "title": "Standardized Metrology & Glyptic Art",
                            "text": "Indus weights followed a binary system in lower denominations (1, 2, 4, 8, 16, 32, 64) and decimal in higher denominations (160, 200, 320, 640), accurate to fractions of a gram.",
                            "keys": ["ivc_steatite_seals_by_site"]
                        }
                    ]
                },
                {
                    "name": "Maritime Trade & International Artifacts",
                    "headline": "Lothal Dockyards & The Meluhha Shipping Network",
                    "dek": "Ancient Mesopotamian cuneiform tablets record trade with Dilmun (Bahrain/Kuwait), Magan (Oman), and Meluhha (Indus Valley). Harappan square steatite seals and etched carnelian beads have been excavated at Ur, Kish, Tell Asmar, and Susa.",
                    "paragraphs": ["The brick basin at Lothal (214 × 36 metres) featured a vertical sluice gate to trap water at high tide, allowing masted merchant vessels to load and unload cargo without grounding on mud flats."],
                    "watch": "Underwater marine archeology surveys along the Makran coast and Gulf of Kutch.",
                    "sources": ["NIO Goa", "British Museum Ur Excavation Archives"],
                    "indicatorCount": 1,
                    "sections": [
                        {
                            "title": "Long-Distance Maritime Trade Corridors",
                            "text": "Indus merchant guilds sailed over 2,500 km across the Arabian Sea, trading textiles, timber, ivory, and etched carnelian for Mesopotamian wool, tin, and silver.",
                            "keys": ["ivc_international_trade_distance"]
                        }
                    ]
                },
                {
                    "name": "Indus Script & Alphabet Decoding",
                    "headline": "The Undeciphered Script & Linguistic Models",
                    "dek": "With over 4,000 cataloged inscriptions averaging 4.6 signs in length, the Indus script remains one of archaeology's greatest unsolved enigmas. Statistical positional analysis confirms a right-to-left logo-syllabic writing system.",
                    "paragraphs": ["The discovery of the 10-glyph gypsum signboard inside Dholavira's citadel gateway confirmed the public civic usage of monumentally sized script characters."],
                    "watch": "Computational Markov models, neural decipherment, and bilingual inscription searches in Mesopotamia.",
                    "sources": ["Mahadevan Concordance", "Parpola CISI"],
                    "indicatorCount": 1,
                    "sections": [
                        {
                            "title": "Sign Concordance & Positional Entropy",
                            "text": "Sign M-342 (the Jar/Vessel sign) occurs over 1,390 times, almost exclusively at the terminal (leftmost) position of texts, functioning as an inflectional or patronymic suffix.",
                            "keys": ["ivc_top_script_signs_frequency"]
                        }
                    ]
                },
                {
                    "name": "Chronology, Settlement Geography & Legacy",
                    "headline": "Climatic Shifting & Cultural Transmutation",
                    "dek": "Rather than a sudden violent collapse, modern paleoclimatology and archeological settlement surveys demonstrate that shifting monsoon patterns caused the drying of the Saraswati/Ghaggar-Hakra river system, prompting eastward migration toward the Ganga-Yamuna Doab.",
                    "paragraphs": ["Harappan craft techniques, weights, religious motifs (Pashupati, Peepal leaf, swastika, yogic postures), and hydraulic awareness survived and deeply influenced classical Indian civilization."],
                    "watch": "Paleoclimatic speleothem records and satellite paleochannel mapping.",
                    "sources": ["Geological Survey of India", "Nature Geoscience"],
                    "indicatorCount": 1,
                    "sections": [
                        {
                            "title": "Settlement Transitions Across Eras",
                            "text": "From the Kot Diji and Amri early phases to the Mature urban climax and Ochre Coloured Pottery (OCP) / Painted Grey Ware (PGW) transitions, the Harappan legacy formed the deep substrate of Indian history.",
                            "keys": ["ivc_radiocarbon_phases"]
                        }
                    ]
                }
            ]
        }
    }
    explainers['groups'].append(ivc_explainer)

with open(EXPLAINERS_PATH, 'w', encoding='utf-8') as f:
    json.dump(explainers, f, indent=2, ensure_ascii=False)

print(f"Updated {EXPLAINERS_PATH}: groups={len(explainers['groups'])}")
