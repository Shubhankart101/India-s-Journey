#!/usr/bin/env python3
"""
Adds/updates the "Indus Valley Civilisation" category in data/catalog.json and group-explainers.json
as a SINGLE unified subgroup article:
  "The Indus Valley Civilisation Comprehensive Excavation Map"
All 5 IVC indicators belong to this single subgroup.
"""

import json

CATALOG_PATH = 'data/catalog.json'
EXPLAINERS_PATH = 'frontend/src/data/group-explainers.json'

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open(EXPLAINERS_PATH, 'r', encoding='utf-8') as f:
    explainers = json.load(f)

SUBGROUP_NAME = "The Indus Valley Civilisation Comprehensive Excavation Map"
SUBGROUP_SLUG = "the-indus-valley-civilisation-comprehensive-excavation-map"

# 1. Ensure category in catalog
ivc_category = {
    "name": "Indus Valley Civilisation",
    "slug": "indus-valley-civilisation",
    "order": 11,
    "title": "Indus Valley Civilisation",
    "description": "Comprehensive archaeological atlas of 49+ excavations, urban planning, metallurgy, maritime trade networks, undeciphered script concordance, and material culture (c. 3300 – 1300 BCE).",
    "badges": ["Archeology", "Bronze Age", "Epigraphy", "Maritime Trade"],
    "color": "#d4a72c",
    "icon": "citadel",
    "art": "indus-valley.svg",
    "subgroups": [
        {
            "name": SUBGROUP_NAME,
            "slug": SUBGROUP_SLUG,
            "order": 0,
            "title": "The Indus Valley Civilisation Comprehensive Excavation Map & Epigraphy",
            "description": "Comprehensive GIS excavation atlas across 49+ sites and 9 countries, Harappan urban planning, script concordance, metallurgy, maritime trade networks, and material culture.",
            "art": "indus-valley.svg"
        }
    ]
}

existing_cat = next((c for c in catalog['categories'] if c['name'] == 'Indus Valley Civilisation' or c.get('slug') == 'indus-valley-civilisation'), None)
if existing_cat:
    existing_cat.update(ivc_category)
else:
    ivc_category['order'] = len(catalog['categories'])
    catalog['categories'].append(ivc_category)

# 2. Indicators
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
        "subgroup": SUBGROUP_NAME,
        "subgroup_slug": SUBGROUP_SLUG,
        "position": 0,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archeological Survey of India & Harappa Archaeological Research Project",
            "labels": ["Rakhigarhi (Haryana)", "Mohenjo-daro (Sindh)", "Harappa (Punjab)", "Dholavira (Gujarat)", "Ganweriwala (Punjab)", "Kalibangan (Rajasthan)", "Lothal (Gujarat)"],
            "datasets": [
                {
                    "label": "Settlement Footprint (Hectares)",
                    "values": [350, 300, 150, 100, 80, 50, 15]
                }
            ]
        }
    },
    {
        "key": "ivc_steatite_seals_by_site",
        "title": "Cataloged Harappan Inscribed Seals by Excavation Site",
        "subtitle": "Number of inscribed steatite, terracotta, and faience seals in Corpus of Indus Seals",
        "frequency": "archeological",
        "color": "#38bdf8",
        "suffix": " seals",
        "source_url": "https://asi.nic.in",
        "details": "Distribution of inscribed seals and tablets cataloged in the Corpus of Indus Seals and Inscriptions (CISI). Mohenjo-daro and Harappa account for over 85% of all recovered glyptic epigraphs.",
        "category": "Indus Valley Civilisation",
        "subgroup": SUBGROUP_NAME,
        "subgroup_slug": SUBGROUP_SLUG,
        "position": 1,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Mahadevan Concordance (ASI 1977) & Parpola CISI (Vols 1-3)",
            "labels": ["Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Dholavira", "Chanhudaro", "Other Sites (Combined)"],
            "datasets": [
                {
                    "label": "Cataloged Inscribed Objects",
                    "values": [2150, 1420, 245, 120, 95, 68, 142]
                }
            ]
        }
    },
    {
        "key": "ivc_international_trade_distance",
        "title": "Maritime and Overland Trade Distances from Indus Ports",
        "subtitle": "Kilometres travelled by Harappan merchant expeditions to ancient trade partners",
        "frequency": "historical",
        "color": "#10b981",
        "suffix": " km",
        "source_url": "https://asi.nic.in",
        "details": "Estimated nautical and caravan route distances connecting Indus trade hubs like Lothal and Sutkagan Dor with ancient Gulf and Near Eastern civilizations.",
        "category": "Indus Valley Civilisation",
        "subgroup": SUBGROUP_NAME,
        "subgroup_slug": SUBGROUP_SLUG,
        "position": 2,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "National Institute of Oceanography (Goa) & Possehl Seafaring Studies",
            "labels": ["Meluhha to Mesopotamia (Ur/Kish)", "Lothal to Dilmun (Bahrain/Failaka)", "Makran Coast to Magan (Oman)", "Indus Plains to Shortugai (Oxus River Lapis Mines)", "Gujarat Ports to Susa (Elam)"],
            "datasets": [
                {
                    "label": "Route Distance (km)",
                    "values": [2500, 1850, 950, 1200, 2200]
                }
            ]
        }
    },
    {
        "key": "ivc_top_script_signs_frequency",
        "title": "High-Frequency Signs in the Undeciphered Indus Script",
        "subtitle": "Absolute sign occurrences in the Mahadevan Concordance corpus of 4,000+ texts",
        "frequency": "epigraphic",
        "color": "#f59e0b",
        "suffix": " times",
        "source_url": "https://indusscript.net",
        "details": "Frequency of occurrence of the most common signs in the Indus script corpus according to Iravatham Mahadevan's ASI Concordance (1977).",
        "category": "Indus Valley Civilisation",
        "subgroup": SUBGROUP_NAME,
        "subgroup_slug": SUBGROUP_SLUG,
        "position": 3,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Iravatham Mahadevan, The Indus Script: Texts, Concordance and Tables (ASI 1977)",
            "labels": ["M-342 (Jar / Vessel Sign)", "M-267 (Bearer / Arrow Sign)", "M-59 (Chevrons / Pincer)", "M-176 (Harrow / Combs)", "M-99 (Fish Sign)", "M-391 (Terminal Strokes)"],
            "datasets": [
                {
                    "label": "Corpus Occurrences",
                    "values": [1395, 680, 520, 480, 410, 395]
                }
            ]
        }
    },
    {
        "key": "ivc_radiocarbon_phases",
        "title": "Chronological Span of Indus Civilisation Cultural Phases",
        "subtitle": "Duration in years based on calibrated radiocarbon (C14) dating",
        "frequency": "chronological",
        "color": "#a855f7",
        "suffix": " yrs",
        "source_url": "https://asi.nic.in",
        "details": "Calibrated chronological sequence of the Indus tradition from Early Regionalization through Mature Urban Climax to Late Post-Urban Localization.",
        "category": "Indus Valley Civilisation",
        "subgroup": SUBGROUP_NAME,
        "subgroup_slug": SUBGROUP_SLUG,
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

# Merge/update indicators in catalog
cat_inds_map = {i['key']: i for i in catalog['indicators']}
for ind in ivc_indicators:
    cat_inds_map[ind['key']] = ind
catalog['indicators'] = list(cat_inds_map.values())

with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

# 3. Update group-explainers.json
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
        "subgroupCount": 1,
        "verse": {
            "id": "rv-10-75",
            "source": "Rigveda 10.75 (Nadistuti Sukta)",
            "text": "सिन्धोः प्रभावे तद् अस्य वर्धते यत् स्तोतृभ्यः शंस्यं राध एति",
            "transliteration": "sindhoh prabhave tad asya vardhate",
            "meaning": "By the mighty power of the Indus, may fortune flourish and abundance flow unto the singers."
        },
        "subgroups": [
            {
                "name": SUBGROUP_NAME,
                "headline": "The Indus Valley Civilisation Comprehensive Excavation Map, Urbanism & Script",
                "dek": "49 cataloged excavations across 9 countries with exact GPS coordinates, excavated structures, material culture, script decipherment concordance, and peer-reviewed monograph citations.",
                "format": "map",
                "paragraphs": [
                    "Harappan civilization demonstrated continent-wide standardization: uniform 4:2:1 fired brick proportions, standardized binary-decimal chert weights, right-to-left epigraphy, and civic drainage networks spanning 1.5 million square kilometres without signs of monarchical palaces or standing military garrisons.",
                    "The decipherment of the Indus script remains a paramount computational and archaeological objective, with over 4,000 cataloged inscriptions demonstrating sign entropy consistent with natural human languages."
                ],
                "watch": "ASI Rakhigarhi excavations, Dholavira UNESCO World Heritage hydraulic preservation, and computational positional n-gram analyses of Indus script inscriptions.",
                "sources": [
                    "Archaeological Survey of India (ASI)",
                    "Corpus of Indus Seals and Inscriptions (CISI)",
                    "Iravatham Mahadevan Concordance (ASI 1977)"
                ],
                "indicatorCount": 5,
                "sections": [
                    {
                        "title": "Urban Planning & Hydraulic Genius",
                        "text": "Every major Harappan city was laid out on an aligned orthogonal grid with cardinal orientations. Standardized fired bricks with a strict 4:2:1 dimensional ratio were utilized across hundreds of settlements spanning thousands of kilometres.",
                        "keys": ["ivc_urban_settlement_area"]
                    },
                    {
                        "title": "Standardized Metrology & Glyptic Art",
                        "text": "Indus weights followed a binary system in lower denominations (1, 2, 4, 8, 16, 32, 64) and decimal in higher denominations (160, 200, 320, 640), accurate to fractions of a gram.",
                        "keys": ["ivc_steatite_seals_by_site"]
                    },
                    {
                        "title": "Long-Distance Maritime Trade Corridors",
                        "text": "Indus merchant guilds sailed over 2,500 km across the Arabian Sea, trading textiles, timber, ivory, and etched carnelian for Mesopotamian wool, tin, and silver.",
                        "keys": ["ivc_international_trade_distance"]
                    },
                    {
                        "title": "Sign Concordance & Positional Entropy",
                        "text": "Sign M-342 (the Jar/Vessel sign) occurs over 1,390 times, almost exclusively at the terminal (leftmost) position of texts, functioning as an inflectional or patronymic suffix.",
                        "keys": ["ivc_top_script_signs_frequency"]
                    },
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

explainers['groups'] = [g for g in explainers['groups'] if g['name'] != 'Indus Valley Civilisation']
explainers['groups'].append(ivc_explainer)

with open(EXPLAINERS_PATH, 'w', encoding='utf-8') as f:
    json.dump(explainers, f, indent=2, ensure_ascii=False)

print(f"Updated {CATALOG_PATH} and {EXPLAINERS_PATH} with unified Indus Valley subgroup.")
