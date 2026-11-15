#!/usr/bin/env python3
"""
Adds the "Empires of Ancient India" group and updates all subgroup artworks in data/catalog.json.
Also updates group-explainers.json with the 13th group explainer.
"""

import json
import os

CATALOG_PATH = 'data/catalog.json'
EXPLAINERS_PATH = 'frontend/src/data/group-explainers.json'

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

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
    ("Indus Valley Civilisation", "Metropolises & Major Urban Centers"): "indus-valley.svg",
    ("Indus Valley Civilisation", "Artifacts, Statuary & Material Culture"): "ivc-artifacts.svg",
    ("Indus Valley Civilisation", "Maritime Trade & International Artifacts"): "indus-trade.svg",
    ("Indus Valley Civilisation", "Indus Script & Alphabet Decoding"): "indus-script.svg",
    ("Indus Valley Civilisation", "Chronology, Settlement Geography & Legacy"): "ivc-excavations.svg",
}

for cat in catalog['categories']:
    for sub in cat.get('subgroups', []):
        key = (cat['name'], sub['name'])
        if key in ART_MAP:
            sub['art'] = ART_MAP[key]

# 2. Check or add "Empires of Ancient India"
empire_cat_exists = any(c['name'] == 'Empires of Ancient India' for c in catalog['categories'])
if not empire_cat_exists:
    empires_category = {
        "name": "Empires of Ancient India",
        "slug": "empires-of-ancient-india",
        "order": len(catalog['categories']),
        "title": "Empires of Ancient India",
        "description": "Geospatial evolution of imperial boundaries, decisive battlefields, and original script epigraphs from the 16 Mahajanapadas to the Classical Golden Ages (600 BCE – 850 CE).",
        "badges": ["Ancient History", "Epigraphy", "Geopolitics", "Military History"],
        "color": "#facc15",
        "icon": "pillar",
        "art": "ancient-empires.svg",
        "subgroups": [
            {
                "name": "16 Mahajanapadas & Early Republics",
                "slug": "16-mahajanapadas-early-republics",
                "order": 0,
                "title": "16 Mahajanapadas & Early Republics (c. 600–345 BCE)",
                "description": "Second urbanisation in the Gangetic plain, the balance of power between monarchies (Rajyas) and oligarchic republics (Gana-Sanghas) like the Vajjian Confederacy.",
                "art": "mahajanapadas.svg"
            },
            {
                "name": "Magadha Ascendancy: Haryanka, Shishunaga & Nanda",
                "slug": "magadha-ascendancy-haryanka-shishunaga-nanda",
                "order": 1,
                "title": "Magadha Ascendancy: Haryanka, Shishunaga & Nanda (544–322 BCE)",
                "description": "First unification of northern India under the Haryanka, Shishunaga, and Nanda dynasties with massive standing armies and war elephant divisions.",
                "art": "magadha-nanda.svg"
            },
            {
                "name": "Alexander the Great's Campaign & Macedonian Limit",
                "slug": "alexander-the-great-s-campaign-macedonian-limit",
                "order": 2,
                "title": "Alexander the Great's Campaign & Macedonian Limit (327–325 BCE)",
                "description": "The Macedonian invasion of Punjab, Battle of the Hydaspes against King Porus, mutiny at the Beas, and voyage down the Indus.",
                "art": "alexander-campaign.svg"
            },
            {
                "name": "Mauryan Empire & Pan-Indian Hegemony",
                "slug": "mauryan-empire-pan-indian-hegemony",
                "order": 3,
                "title": "Mauryan Empire & Pan-Indian Hegemony (322–185 BCE)",
                "description": "Chandragupta Maurya, Chanakya's Arthashastra, defeat of Seleucus I Nicator, and Ashoka's pan-Indian Dhamma state across 5 million square kilometers.",
                "art": "maurya-empire.svg"
            },
            {
                "name": "Post-Mauryan & Indo-Greek Kingdoms",
                "slug": "post-mauryan-indo-greek-kingdoms",
                "order": 4,
                "title": "Post-Mauryan & Indo-Greek Kingdoms (185 BCE–10 CE)",
                "description": "Greco-Indian synthesis in Gandhara and Punjab under King Menander (Milinda), the Shunga dynasty in Magadha, and the Heliodorus Garuda pillar at Vidisha.",
                "art": "indo-greek.svg"
            },
            {
                "name": "Satavahana Empire & Deccan Maritime Ascendancy",
                "slug": "satavahana-empire-deccan-maritime-ascendancy",
                "order": 5,
                "title": "Satavahana Empire & Deccan Maritime Ascendancy (2nd C. BCE–220 CE)",
                "description": "Gautamiputra Satakarni's destruction of the Western Kshatrapas, control of the three oceans (Tri-Samudra-Toya), and maritime commerce with Rome.",
                "art": "satavahana-empire.svg"
            },
            {
                "name": "Kushan Empire & The Silk Road Synthesis",
                "slug": "kushan-empire-the-silk-road-synthesis",
                "order": 6,
                "title": "Kushan Empire & The Silk Road Synthesis (30–375 CE)",
                "description": "Trans-Eurasian superpower under Kanishka I spanning from Bactria and the Oxus River to Mathura and Varanasi; Fourth Buddhist Council in Kashmir.",
                "art": "kushan-empire.svg"
            },
            {
                "name": "Gupta Empire: Classical Golden Age",
                "slug": "gupta-empire-classical-golden-age",
                "order": 7,
                "title": "Gupta Empire: Classical Golden Age (319–550 CE)",
                "description": "The golden age of Indian science (Aryabhata), literature (Kalidasa), mathematics, and military zenith under Samudragupta and Chandragupta II Vikramaditya.",
                "art": "gupta-empire.svg"
            },
            {
                "name": "Vardhana Empire of Harsha",
                "slug": "vardhana-empire-of-harsha",
                "order": 8,
                "title": "Vardhana Empire of Harsha (606–647 CE)",
                "description": "Imperial court of Kannauj, patron of Nalanda, Xuanzang's pilgrimage, and the Battle of Narmada against Chalukya King Pulakeshin II.",
                "art": "harsha-empire.svg"
            },
            {
                "name": "Classical Southern Dynasties: Chola, Chera, Pandya & Pallava",
                "slug": "classical-southern-dynasties-chola-chera-pandya-pallava",
                "order": 9,
                "title": "Classical Southern Dynasties: Chola, Chera, Pandya & Pallava (300 BCE–850 CE)",
                "description": "Sangam literature in Tamil, maritime trade from Muziris and Poompuhar to Alexandria and Rome, and monolithic rock architecture of Mamallapuram.",
                "art": "southern-dynasties.svg"
            }
        ]
    }
    catalog['categories'].append(empires_category)
else:
    for c in catalog['categories']:
        if c['name'] == 'Empires of Ancient India':
            c['slug'] = 'empires-of-ancient-india'
            for sub in c.get('subgroups', []):
                import re, unicodedata
                def to_slug(val):
                    s = unicodedata.normalize('NFKD', str(val or ''))
                    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
                    s = re.sub(r'[^a-z0-9]+', '-', s.lower())
                    return s.strip('-')
                if not sub.get('slug'):
                    sub['slug'] = to_slug(sub['name'])

# 3. Add Indicators for Empires of Ancient India
EMPIRE_INDICATORS = [
    {
        "key": "ancient_empires_territorial_span",
        "title": "Maximum Territorial Extent of Ancient Indian Empires",
        "subtitle": "Estimated imperial land area in million square kilometers at peak zenith",
        "frequency": "historical",
        "color": "#facc15",
        "suffix": " M km²",
        "source_url": "https://asi.nic.in",
        "details": "Comparative territorial extent across classical Indian dynasties based on historical GIS surveys by the Archaeological Survey of India (ASI) and Cambridge Ancient History.",
        "category": "Empires of Ancient India",
        "subgroup": "Mauryan Empire & Pan-Indian Hegemony",
        "position": 0,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Historical Atlas of South Asia",
            "labels": ["Mauryan Empire (Ashoka)", "Gupta Empire (Vikramaditya)", "Kushan Empire (Kanishka)", "Harsha's Empire (Vardhana)", "Nanda Empire", "Satavahana Empire", "Indo-Greek Kingdom (Menander)", "Alexander's Macedonian Realm (in India)", "Vajji Confederacy", "Magadha (Bimbisara)"],
            "datasets": [
                {
                    "label": "Territorial Area (Million km²)",
                    "values": [5.0, 3.5, 2.5, 1.8, 1.5, 1.3, 1.1, 0.8, 0.4, 0.2]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_military_infantry",
        "title": "Documented Imperial Standing Armies: Infantry Strength",
        "subtitle": "Foot soldier division sizes recorded in classical Greek, Roman, and Indian epigraphs",
        "frequency": "historical",
        "color": "#ef4444",
        "suffix": " soldiers",
        "source_url": "https://asi.nic.in",
        "details": "Standing infantry forces documented by Megasthenes (Indica), Pliny the Elder (Natural History), Quintus Curtius Rufus, and Xuanzang.",
        "category": "Empires of Ancient India",
        "subgroup": "Magadha Ascendancy: Haryanka, Shishunaga & Nanda",
        "position": 1,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Classical Epigraphic Records",
            "labels": ["Mauryan Empire (Megasthenes)", "Nanda Empire (Curtius)", "Harsha's Army (Xuanzang)", "Satavahanas (Pliny)", "Alexander's Punjab Army", "King Porus (Hydaspes)", "Kalinga Army (Pliny)", "Vajjian Gana-Sangha"],
            "datasets": [
                {
                    "label": "Infantry Strength",
                    "values": [600000, 200000, 100000, 100000, 45000, 30000, 60000, 40000]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_war_elephants",
        "title": "Imperial War Elephant Corps in Ancient Indian Armies",
        "subtitle": "Armored war pachyderm divisions documented across ancient battle accounts",
        "frequency": "historical",
        "color": "#f59e0b",
        "suffix": " war elephants",
        "source_url": "https://asi.nic.in",
        "details": "War elephant divisions recorded during the Alexander invasion, Seleucid treaty, and Gangetic imperial campaigns.",
        "category": "Empires of Ancient India",
        "subgroup": "Alexander the Great's Campaign & Macedonian Limit",
        "position": 2,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Classical Greek Historians",
            "labels": ["Mauryan Empire", "Nanda Empire", "Harsha's Army", "Gangaridai (Bengal)", "Satavahana Empire", "Kalinga Army", "King Porus (Hydaspes)"],
            "datasets": [
                {
                    "label": "Armored War Elephants",
                    "values": [9000, 6000, 5000, 4000, 1500, 1000, 200]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_inscriptions_count",
        "title": "Cataloged Epigraphic Inscriptions and Edicts by Imperial Era",
        "subtitle": "Surviving stone edicts, pillar inscriptions, and copper plates cataloged in Epigraphia Indica",
        "frequency": "historical",
        "color": "#10b981",
        "suffix": " inscriptions",
        "source_url": "https://asi.nic.in",
        "details": "Count of official royal edicts, cave grants, and prasastis cataloged by the Archaeological Survey of India.",
        "category": "Empires of Ancient India",
        "subgroup": "Gupta Empire: Classical Golden Age",
        "position": 3,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Epigraphia Indica & Archaeological Survey of India",
            "labels": ["Gupta Classical Epigraphs", "Sangam Hero Stones & Inscriptions", "Ashokan Mauryan Edicts", "Kushan Mathura/Gandhara Epigraphs", "Satavahana Rock Inscriptions", "Indo-Greek Bilingual Inscriptions", "Harsha's Copper Plates", "Heliodorus / Post-Mauryan Pillars"],
            "datasets": [
                {
                    "label": "Cataloged Inscriptions",
                    "values": [240, 210, 180, 150, 120, 45, 35, 25]
                }
            ]
        }
    },
    {
        "key": "ancient_empires_reign_durations",
        "title": "Dynastic Longevity of Classical Indian Imperial Houses",
        "subtitle": "Duration of imperial rule in years from dynasty foundation to decline",
        "frequency": "historical",
        "color": "#38bdf8",
        "suffix": " years",
        "source_url": "https://asi.nic.in",
        "details": "Comparative chronological lifespan of major classical dynasties across the ancient subcontinent.",
        "category": "Empires of Ancient India",
        "subgroup": "Satavahana Empire & Deccan Maritime Ascendancy",
        "position": 4,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Epigraphia Indica",
            "labels": ["Satavahana Empire", "Kushan Empire", "Gupta Empire", "Indo-Greek Kingdom", "Mauryan Empire", "Shunga Dynasty", "Harsha's Vardhana Rule", "Nanda Empire"],
            "datasets": [
                {
                    "label": "Dynastic Lifespan (Years)",
                    "values": [450, 345, 230, 195, 137, 112, 41, 23]
                }
            ]
        }
    },
    {
        "key": "mahajanapadas_political_systems",
        "title": "16 Mahajanapadas: Distribution of Monarchies and Gana-Sangha Republics",
        "subtitle": "Geographic classification of Vedic Mahajanapadas into Monarchical Rajyas and Republican Sanghas",
        "frequency": "historical",
        "color": "#eab308",
        "suffix": " realms",
        "source_url": "https://asi.nic.in",
        "details": "Classification of the sixteen great realms documented in the Anguttara Nikaya and Digha Nikaya into monarchical and republican polities.",
        "category": "Empires of Ancient India",
        "subgroup": "16 Mahajanapadas & Early Republics",
        "position": 5,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Epigraphia Indica",
            "labels": ["Monarchical Rajyas (Magadha, Kosala, Vatsa, Avanti)", "Gana-Sanghas & Republics (Vajji, Malla)", "North-Western Janapadas (Gandhara, Kamboja)", "Central & Peninsular Janapadas (Chedi, Matsya, Surasena, Ashmaka)"],
            "datasets": [
                {
                    "label": "Number of Recorded Realms",
                    "values": [8, 2, 2, 4]
                }
            ]
        }
    },
    {
        "key": "indogreek_numismatic_coin_types",
        "title": "Indo-Greek Bilingual Numismatic Coin Hoards",
        "subtitle": "Bilingual Greek and Kharosthi/Brahmi royal coinage hoards discovered across Gandhara and Punjab",
        "frequency": "historical",
        "color": "#a855f7",
        "suffix": " hoards",
        "source_url": "https://asi.nic.in",
        "details": "Major coin hoards and bilingual silver tetradrachms cataloged across Taxila, Pushkalavati, Mir Zakah, and Chaman.",
        "category": "Empires of Ancient India",
        "subgroup": "Post-Mauryan & Indo-Greek Kingdoms",
        "position": 6,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Epigraphia Indica",
            "labels": ["Menander I Soter (Taxila & Punjab Hoards)", "Demetrius I Aniketos (Gandhara Hoards)", "Eucratides I Megas (Bactria-Kabul Hoards)", "Apollodotus I (Sindh & Gujarat Hoards)", "Antialcidas Nikephoros (Vidisha & Taxila)", "Agathocles Dikaios (Bilingual Brahmi Types)"],
            "datasets": [
                {
                    "label": "Cataloged Coin Specimens",
                    "values": [480, 210, 185, 160, 125, 95]
                }
            ]
        }
    },
    {
        "key": "kushan_silkroad_monasteries",
        "title": "Kushan Imperial Buddhist Monasteries and Silk Road Emporia",
        "subtitle": "Excavated Buddhist monastic stupas and Silk Road trading posts from Bactria to the Gangetic plain",
        "frequency": "historical",
        "color": "#06b6d4",
        "suffix": " complexes",
        "source_url": "https://asi.nic.in",
        "details": "Cataloged archaeological sites spanning the Kushan imperial heartland under Kanishka I and Huvishka.",
        "category": "Empires of Ancient India",
        "subgroup": "Kushan Empire & The Silk Road Synthesis",
        "position": 7,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & UNESCO World Heritage Centre",
            "labels": ["Gandhara Valley (Peshawar & Takht-i-Bahi)", "Taxila & Margalla Basin (Dharmarajika)", "Mathura & Yamuna Basin (Kankali Tila)", "Bagram (Kapisa Royal Ivory & Glass Hoard)", "Bactria & Oxus Basin (Surkh Kotal & Termez)", "Kashmir Basin (Harwan Fourth Buddhist Council)"],
            "datasets": [
                {
                    "label": "Excavated Monastic Complexes",
                    "values": [142, 98, 76, 54, 42, 28]
                }
            ]
        }
    },
    {
        "key": "harsha_imperial_assemblies",
        "title": "Harsha's Imperial Convocations: Royal and Scholarly Attendance",
        "subtitle": "Documented attendance of vassal kings, Buddhist monks, and Vedic scholars recorded by Xuanzang",
        "frequency": "historical",
        "color": "#ec4899",
        "suffix": " attendees",
        "source_url": "https://asi.nic.in",
        "details": "Official historical records of the Kannauj Assembly and the quinquennial Prayag Mahamoksha Parishad documented by Xuanzang and Banabhatta.",
        "category": "Empires of Ancient India",
        "subgroup": "Vardhana Empire of Harsha",
        "position": 8,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Epigraphia Indica",
            "labels": ["Prayag Mahamoksha Assembly (Ascetics & Monks)", "Nalanda Mahavihara (Resident Scholars)", "Kannauj Assembly (Buddhist Monks)", "Kannauj Assembly (Vedic Scholars & Brahmins)", "Kannauj Assembly (Tributary Vassal Kings)"],
            "datasets": [
                {
                    "label": "Documented Attendees",
                    "values": [10000, 10000, 3000, 3000, 20]
                }
            ]
        }
    },
    {
        "key": "sangam_maritime_ports_trade",
        "title": "Ancient Tamil Maritime Ports and Roman Mediterranean Trade Hubs",
        "subtitle": "Documented Sangam era coastal emporia with Roman amphorae and Mediterranean coinage hoards",
        "frequency": "historical",
        "color": "#14b8a6",
        "suffix": " artifacts",
        "source_url": "https://asi.nic.in",
        "details": "Archaeological finds of Mediterranean amphorae, rouletted ware, and Roman imperial aurei along the Coromandel and Malabar coasts.",
        "category": "Empires of Ancient India",
        "subgroup": "Classical Southern Dynasties: Chola, Chera, Pandya & Pallava",
        "position": 9,
        "series": {
            "chart_type": "bar",
            "index_axis": "y",
            "source": "Archaeological Survey of India & Epigraphia Indica",
            "labels": ["Muziris (Chera - Roman Gold Aurei Hoards)", "Poompuhar / Kaveripattinam (Chola Port)", "Arikamedu / Poduke (Roman Amphorae & Glass)", "Korkai (Pandya Pearl & Maritime Port)", "Mamallapuram (Pallava Harbor & Temples)", "Alagankulam (Pandya Mediterranean Coins)"],
            "datasets": [
                {
                    "label": "Cataloged Roman & Mediterranean Artifacts",
                    "values": [380, 310, 290, 240, 190, 175]
                }
            ]
        }
    }
]

existing_ind_map = {ind['key']: i for i, ind in enumerate(catalog['indicators'])}
for ind in EMPIRE_INDICATORS:
    if ind['key'] in existing_ind_map:
        catalog['indicators'][existing_ind_map[ind['key']]] = ind
    else:
        catalog['indicators'].append(ind)
        existing_ind_map[ind['key']] = len(catalog['indicators']) - 1

# Save catalog
with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Updated {CATALOG_PATH} with {len(catalog['categories'])} categories and {len(catalog['indicators'])} indicators.")

# 4. Update group-explainers.json using build_explainers
from build_explainers import main as build_explainers_main
build_explainers_main()
