#!/usr/bin/env python3
"""
Adds the "Empires of Ancient India" group and updates all subgroup artworks in data/catalog.json.
Consolidates Empires of Ancient India into ONE unified subgroup article:
  "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions"
Also updates group-explainers.json with the unified subgroup explainer.
"""

import json
import os

CATALOG_PATH = 'data/catalog.json'
EXPLAINERS_PATH = 'frontend/src/data/group-explainers.json'

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open(EXPLAINERS_PATH, 'r', encoding='utf-8') as f:
    explainers = json.load(f)

# 1. Update existing subgroup artworks to bespoke files
ART_MAP = {
    ("Economy & Markets", "Savings, Investment & Media"): "savings-investment.svg",
    ("Public Finance & States", "Union Budget: Receipts, Spending & Deficits"): "union-receipts.svg",
    ("Public Finance & States", "How India Borrows & Shares Revenue"): "borrowing-debt.svg",
    ("Public Finance & States", "State Fiscal Explorer & Welfare"): "state-fiscal-welfare.svg",
    ("Culture, Heritage & Sport", "Hockey"): "hockey-india.svg",
    ("Culture, Heritage & Sport", "Football"): "football-india.svg",
    ("Security, Justice & Defence", "Supreme Court · Civil · Pending & 2018–21"): "supreme-civil.svg",
    ("Security, Justice & Defence", "Supreme Court · Civil · 2022–26"): "supreme-civil.svg",
    ("Security, Justice & Defence", "Supreme Court · Criminal · Pending & 2018–21"): "supreme-criminal.svg",
    ("Security, Justice & Defence", "Supreme Court · Criminal · 2022–26"): "supreme-criminal.svg",
    ("Indus Valley Civilisation", "The Indus Valley Civilisation Comprehensive Excavation Map"): "indus-valley.svg",
}

for cat in catalog['categories']:
    for sub in cat.get('subgroups', []):
        key = (cat['name'], sub['name'])
        if key in ART_MAP:
            sub['art'] = ART_MAP[key]

# 2. Add or update "Empires of Ancient India"
EMP_SUBGROUP_NAME = "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions"
EMP_SUBGROUP_SLUG = "empires-of-ancient-india-atlas"

empires_category = {
    "name": "Empires of Ancient India",
    "slug": "empires-of-ancient-india",
    "order": 12,
    "title": "Empires of Ancient India",
    "description": "Geospatial evolution of imperial boundaries, decisive battlefields, and original script epigraphs from the 16 Mahajanapadas to the Classical Golden Ages (600 BCE – 850 CE).",
    "badges": ["Ancient History", "Epigraphy", "Geopolitics", "Military History"],
    "color": "#facc15",
    "icon": "pillar",
    "art": "ancient-empires.svg",
    "subgroups": [
        {
            "name": EMP_SUBGROUP_NAME,
            "slug": EMP_SUBGROUP_SLUG,
            "order": 0,
            "title": "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions",
            "description": "Interactive dynastic atlases mapping 10 major imperial eras, territorial boundary shifts, decisive battlefields, and epigraphic records in original ancient scripts with official citations.",
            "art": "ancient-empires.svg"
        }
    ]
}

existing_emp = next((c for c in catalog['categories'] if c['name'] == 'Empires of Ancient India' or c.get('slug') == 'empires-of-ancient-india'), None)
if existing_emp:
    existing_emp.update(empires_category)
else:
    empires_category['order'] = len(catalog['categories'])
    catalog['categories'].append(empires_category)

# 3. Empire Indicators (All 10 attached to the single unified subgroup)
empire_indicators = [
    {
        "key": "ancient_empires_territorial_span",
        "title": "Peak Territorial Extent of Ancient Indian Empires",
        "subtitle": "Estimated maximum land area in million square kilometres (sq km)",
        "frequency": "historical",
        "color": "#facc15",
        "suffix": " M km²",
        "source_url": "https://asi.nic.in",
        "details": "Comparative territorial surface area at imperial zenith based on epigraphic distribution and historical geographical syntheses.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 0,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Schwartzberg Historical Atlas of South Asia & ASI Epigraphy Branch",
            "labels": ["Mauryan Empire (Ashoka)", "Gupta Empire (Chandragupta II)", "Kushan Empire (Kanishka I)", "Harsha's Empire", "Satavahana Empire", "Nanda Empire", "Indo-Greek Kingdom"],
            "datasets": [
                {
                    "label": "Territorial Span (Million km²)",
                    "values": [5.0, 3.5, 3.0, 2.5, 2.2, 1.8, 1.2]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_military_infantry",
        "title": "Documented Standing Army Infantry Strength of Classical Empires",
        "subtitle": "Number of regular infantry troops recorded in classical and epigraphic chronicles",
        "frequency": "military",
        "color": "#ef4444",
        "suffix": " troops",
        "source_url": "https://asi.nic.in",
        "details": "Infantry size recorded by contemporary Roman, Greek, Chinese, and Indian chroniclers (Pliny, Megasthenes, Curtius, Xuanzang).",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 1,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Megasthenes Indica & Pliny Naturalis Historia",
            "labels": ["Mauryan Empire (Chandragupta)", "Nanda Empire of Magadha", "Harsha's Imperial Host", "Alexander's Macedonian Host (Asia)", "Satavahana Forces"],
            "datasets": [
                {
                    "label": "Standing Infantry",
                    "values": [600000, 200000, 100000, 40000, 100000]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_war_elephants",
        "title": "Imperial War Elephant Corps in Indian Warfare",
        "subtitle": "Number of trained battle elephants deployed by imperial armies",
        "frequency": "military",
        "color": "#3b82f6",
        "suffix": " elephants",
        "source_url": "https://asi.nic.in",
        "details": "War elephants formed the decisive arm of ancient Indian statecraft (Gaja-bala), celebrated in Kautilya's Arthashastra and chronicled by Greek historians.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 2,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Arthashastra & Curtius Rufus History of Alexander",
            "labels": ["Mauryan Empire (Peak)", "Nanda Empire", "Harsha's Vardhana Army", "King Porus (Hydaspes)", "Seleucus I Treaty Transfer"],
            "datasets": [
                {
                    "label": "War Elephants",
                    "values": [9000, 4000, 5000, 200, 500]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_inscriptions_count",
        "title": "Cataloged Official Imperial Inscriptions by Dynasty",
        "subtitle": "Number of published stone, pillar, cave, and copper plate royal charters in CII and Epigraphia Indica",
        "frequency": "epigraphic",
        "color": "#10b981",
        "suffix": " inscriptions",
        "source_url": "https://asi.nic.in",
        "details": "Epigraphic corpus cataloged by the Archaeological Survey of India (ASI) Epigraphy Branch across Corpus Inscriptionum Indicarum (CII).",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 3,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India Epigraphy Branch & CII Volumes",
            "labels": ["Chola Dynasty (Imperial)", "Gupta & Later Gupta", "Mauryan Edicts (Ashoka)", "Badami Chalukyas", "Pallavas of Kanchi", "Satavahanas", "Harshavardhana"],
            "datasets": [
                {
                    "label": "Cataloged Royal Inscriptions",
                    "values": [12000, 320, 185, 210, 165, 85, 12]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_reign_durations",
        "title": "Dynastic Lifespan of Ancient Indian Imperial Houses",
        "subtitle": "Total duration of unbroken imperial rule in years",
        "frequency": "historical",
        "color": "#a855f7",
        "suffix": " years",
        "source_url": "https://asi.nic.in",
        "details": "Total chronological span of primary dynastic houses from foundation to imperial eclipse.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 4,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Nilakanta Sastri & Majumdar Dynastic Chronology",
            "labels": ["Satavahana Dynasty", "Pallava Dynasty", "Kushan Empire", "Gupta Empire", "Mauryan Empire", "Shunga Dynasty", "Harsha's Reign"],
            "datasets": [
                {
                    "label": "Imperial Duration (Years)",
                    "values": [450, 400, 345, 231, 137, 112, 41]
                }
            ]
        }
    },
    {
        "key": "mahajanapadas_political_systems",
        "title": "State Formations of the 16 Mahajanapadas (c. 600 BCE)",
        "subtitle": "Breakdown between monarchies (Rajyas) and oligarchic republics (Gana-Sanghas)",
        "frequency": "historical",
        "color": "#eab308",
        "suffix": " states",
        "source_url": "https://asi.nic.in",
        "details": "Classification of Iron Age polities listed in the Anguttara Nikaya and Jaina texts into hereditary monarchical states vs clan-based republican confederacies.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 5,
        "series": {
            "chart_type": "doughnut",
            "source": "Anguttara Nikaya & Rhys Davids Buddhist India",
            "labels": ["Monarchies (Rajyas - Magadha, Kosala, Vatsa, etc.)", "Republics / Gana-Sanghas (Vajji, Malla)", "Tribal Frontier Polities (Kamboja, Assaka)"],
            "datasets": [
                {
                    "label": "Number of Polities",
                    "values": [11, 3, 2]
                }
            ]
        }
    },
    {
        "key": "indogreek_numismatic_coin_types",
        "title": "Bilingual Coinage and Hellenistic Kings of Bactria & India",
        "subtitle": "Known Greek and Indo-Greek sovereigns who issued bilingual currency",
        "frequency": "numismatic",
        "color": "#06b6d4",
        "suffix": " kings",
        "source_url": "https://asi.nic.in",
        "details": "Number of documented Indo-Greek monarchs known almost exclusively through their magnificent bilingual silver tetradrachms and drachms (Greek obverse, Kharosthi reverse).",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 6,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Osmund Bopearachchi, Monnaies greco-bactriennes et indo-grecques (1991)",
            "labels": ["Bilingual Indo-Greek Kings (Punjab/Gandhara)", "Greco-Bactrian Kings (North of Hindu Kush)", "Indo-Scythian Kings (Sakas)", "Indo-Parthian Kings (Gondophares)"],
            "datasets": [
                {
                    "label": "Documented Monetary Sovereigns",
                    "values": [34, 8, 14, 6]
                }
            ]
        }
    },
    {
        "key": "kushan_silkroad_monasteries",
        "title": "Buddhist Monasteries along Kushan Trade Corridors",
        "subtitle": "Excavated viharas and stupa complexes along northern Silk Road and Uttarapatha routes",
        "frequency": "archeological",
        "color": "#f43f5e",
        "suffix": " complexes",
        "source_url": "https://asi.nic.in",
        "details": "Distribution of monumental Buddhist rock-cut and structural monasteries patronized by the Kushan court.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 7,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "UNESCO Silk Roads Archaeological Inventory & ASI Gandhara Survey",
            "labels": ["Gandhara & Taxila Basin", "Mathura & Yamuna Valley", "Bactria & Oxus River Basin", "Kashmir Valley", "Begram / Kapisa Valley"],
            "datasets": [
                {
                    "label": "Excavated Monastic Complexes",
                    "values": [120, 45, 38, 25, 22]
                }
            ]
        }
    },
    {
        "key": "harsha_imperial_assemblies",
        "title": "Dignitaries and Kings Attending Harsha's Kannauj Assembly (643 CE)",
        "subtitle": "Recorded attendance of vassal monarchs, Buddhist scholars, and Vedic Brahmins",
        "frequency": "historical",
        "color": "#8b5cf6",
        "suffix": " attendees",
        "source_url": "https://asi.nic.in",
        "details": "Chronicle recorded by Xuanzang (Hiuen Tsang) documenting the extraordinary 20-king assembly convened by Emperor Harshavardhana at Kannauj.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 8,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Xuanzang, Si-Yu-Ki: Buddhist Records of the Western World",
            "labels": ["Vassal Kings (incl. Bhaskaravarman of Kamarupa)", "Eminent Buddhist Scholars & Monks", "Learned Vedic Brahmins & Jains", "Royal War Elephants in Procession"],
            "datasets": [
                {
                    "label": "Recorded Numbers",
                    "values": [20, 3000, 2000, 300]
                }
            ]
        }
    },
    {
        "key": "sangam_maritime_ports_trade",
        "title": "Roman Amphorae and Coin Hoards in Southern Dynastic Ports",
        "subtitle": "Excavated Mediterranean artifact assemblages along Coromandel and Malabar coasts",
        "frequency": "archeological",
        "color": "#14b8a6",
        "suffix": " hoards",
        "source_url": "https://asi.nic.in",
        "details": "Quantification of Roman gold aurei hoards and Mediterranean amphorae fragments excavated at Muziris, Arikamedu, Korkai, and Kaveripattinam, confirming the Periplus of the Erythraean Sea.",
        "category": "Empires of Ancient India",
        "subgroup": EMP_SUBGROUP_NAME,
        "subgroup_slug": EMP_SUBGROUP_SLUG,
        "position": 9,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "R. Nagaswamy, Roman Karur & ASI Arikamedu Reports",
            "labels": ["Chera Ports (Muziris / Karur Hoards)", "Chola Ports (Kaveripattinam / Arikamedu)", "Pandya Ports (Madurai / Korkai)", "Pallava Ports (Mamallapuram / Kanchi)"],
            "datasets": [
                {
                    "label": "Documented Roman Coin Hoards",
                    "values": [42, 28, 19, 11]
                }
            ]
        }
    }
]

# Merge/update indicators in catalog
cat_inds_map = {i['key']: i for i in catalog['indicators']}
for ind in empire_indicators:
    cat_inds_map[ind['key']] = ind
catalog['indicators'] = list(cat_inds_map.values())

with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

# 4. Update group-explainers.json
empires_explainer = {
    "name": "Empires of Ancient India",
    "article": {
        "pattern": "imperial-dynasties",
        "headline": "Dynastic Borders, Battlefields & Sacred Epigraphy (600 BCE – 850 CE)",
        "dek": "Across fourteen centuries from the Later Vedic dawn to the Classical Golden Ages, South Asia forged continent-spanning empires, codified political economy in the Arthashastra, repelled Mediterranean invasions, and inscribed profound moral charters upon living rock in Brahmi, Sanskrit, Greek, and Sangam Tamil.",
        "paragraphs": [
            "The geopolitical evolution of ancient India was defined by the perpetual dialectic between imperial centralization (Samrajya) and vibrant regional sovereignty. Following the urbanization of the 16 Mahajanapadas, the Mauryan Empire established the first pan-Indian state, governing over 50 million people under an administration of exceptional institutional complexity.",
            "Alexander the Great's brief incursion into the Punjab in 326 BCE catalyzed profound cross-cultural syntheses, giving rise to the bilingual Indo-Greek kingdoms of Menander and the trans-continental Kushan Empire that united the Silk Roads of Central Asia with the sacred shrines of Mathura and Varanasi.",
            "Under the Gupta Empire, the Deccan Satavahanas, Harsha of Kannauj, and the Classical Southern dynasties (Cholas, Cheras, Pandyas, Pallavas, and Chalukyas), peninsular India became the maritime hub of the Indian Ocean, producing enduring monuments of architectural majesty from Ajanta and Ellora to Mamallapuram and Thanjavur."
        ],
        "watch": "ASI epigraphic digitisation in Epigraphia Indica, underwater archaeology at Muziris and Poompuhar, and spatial GIS corridor modeling of ancient Dakshinapatha and Uttarapatha highways.",
        "sources": [
            "Archaeological Survey of India (ASI) Memoirs & Epigraphia Indica",
            "Corpus Inscriptionum Indicarum (CII), Volumes I to IV",
            "The History and Culture of the Indian People (R.C. Majumdar, Vols II–III)",
            "A Political History of Ancient India (H.C. Raychaudhuri)"
        ],
        "indicatorCount": 10,
        "subgroupCount": 1,
        "verse": {
            "id": "git-4-7",
            "source": "Bhagavad Gita 4.7 & Ashokan 12th Rock Edict",
            "text": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत । अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम् ॥",
            "transliteration": "yada yada hi dharmasya glanir bhavati bharata",
            "meaning": "Whenever righteousness wanes and unrighteousness rises up, O Bharata, then do I manifest Myself upon the earth."
        },
        "subgroups": [
            {
                "name": EMP_SUBGROUP_NAME,
                "headline": "Dynastic Atlases, Battles & Inscriptions (600 BCE – 850 CE)",
                "dek": "Interactive geospatial atlases mapping shifting imperial frontiers, decisive battlefields, and epigraphic records in Ashokan Brahmi, Classical Sanskrit, Ancient Greek, and Sangam Tamil.",
                "format": "map",
                "paragraphs": [
                    "Explore the complete chronological sweep of ancient Indian sovereignty across 10 defined imperial eras: from the balance of power among the 16 Mahajanapadas, to Mahapadma Nanda's standing army, Alexander the Great's trans-continental campaign limit, Ashoka's pan-Indian Dhamma state, Menander's Indo-Greek synthesis, Gautamiputra Satakarni's maritime dominion, Kanishka's Silk Road superpower, the Gupta Golden Age, Harshavardhana's Kannauj court, and the Sangam maritime thalassocracies of the deep South.",
                    "Each imperial era features multi-phase territorial boundaries, interactive battle locations with military commanders and casualty chronicles, capital cities, and primary epigraphic inscriptions preserved in their original scripts with scholarly translations."
                ],
                "watch": "ASI epigraphic revisions, satellite remotesensing of ancient frontier fortifications, and numismatic hoards.",
                "sources": [
                    "Archaeological Survey of India (ASI)",
                    "Corpus Inscriptionum Indicarum (CII)",
                    "Epigraphia Indica"
                ],
                "indicatorCount": 10,
                "sections": [
                    {
                        "title": "Imperial Territorial Extent & Hegemony",
                        "text": "The Mauryan Empire at its peak under Ashoka the Great covered approximately 5 million square kilometres, making it one of the largest states on the planet in the 3rd century BCE, followed by the Gupta Empire (3.5 million km²) and the Kushans (3.0 million km²).",
                        "keys": ["ancient_empires_territorial_span"]
                    },
                    {
                        "title": "Standing Armies & Military Formations",
                        "text": "Classical Indian warfare relied upon the four-fold army (Chaturanga-bala): infantry, cavalry, chariots, and war elephants. Greek historians Pliny and Megasthenes recorded that Chandragupta Maurya maintained a standing host of 600,000 infantry, 30,000 cavalry, and 9,000 war elephants.",
                        "keys": ["ancient_empires_military_infantry", "ancient_empires_war_elephants"]
                    },
                    {
                        "title": "Epigraphic Records & Royal Charters",
                        "text": "Over 25,000 royal inscriptions have been cataloged by the Archaeological Survey of India. The Imperial Cholas alone left over 12,000 temple wall inscriptions detailing land surveys, revenue rates, and naval conquests, while Ashoka's rock edicts preserved the earliest deciphered writing in Brahmi and Kharosthi.",
                        "keys": ["ancient_empires_inscriptions_count", "ancient_empires_reign_durations"]
                    },
                    {
                        "title": "Statecraft, Numismatics & Trans-Eurasian Commerce",
                        "text": "From the punch-marked silver karshapanas of the Mahajanapadas to the refined bilingual silver drachms of Indo-Greek King Menander, the gold dinars of Kanishka, and Roman aurei hoards excavated at southern ports like Muziris and Arikamedu, ancient India formed the pivot of Eurasian trade networks.",
                        "keys": ["mahajanapadas_political_systems", "indogreek_numismatic_coin_types", "kushan_silkroad_monasteries", "harsha_imperial_assemblies", "sangam_maritime_ports_trade"]
                    }
                ]
            }
        ]
    }
}

explainers['groups'] = [g for g in explainers['groups'] if g['name'] != 'Empires of Ancient India']
explainers['groups'].append(empires_explainer)

with open(EXPLAINERS_PATH, 'w', encoding='utf-8') as f:
    json.dump(explainers, f, indent=2, ensure_ascii=False)

print(f"Updated {CATALOG_PATH} and {EXPLAINERS_PATH} with unified Empires of Ancient India subgroup.")
