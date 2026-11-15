#!/usr/bin/env python3
"""
Consolidates Indus Valley Civilisation and Empires of Ancient India into
exactly ONE comprehensive subgroup article each in data/catalog.json.
Assigns all respective indicators to their consolidated subgroup.
"""

import json

CATALOG_PATH = 'data/catalog.json'

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# 1. Update Indus Valley Civilisation category
for cat in catalog['categories']:
    if cat['slug'] == 'indus-valley-civilisation' or cat['name'] == 'Indus Valley Civilisation':
        cat['name'] = 'Indus Valley Civilisation'
        cat['slug'] = 'indus-valley-civilisation'
        cat['title'] = 'Indus Valley Civilisation'
        cat['description'] = 'Comprehensive archaeological atlas of 49+ excavations, urban planning, metallurgy, maritime trade networks, undeciphered script concordance, and material culture (c. 3300 – 1300 BCE).'
        cat['art'] = 'indus-valley.svg'
        cat['subgroups'] = [
            {
                "name": "The Indus Valley Civilisation Comprehensive Excavation Map",
                "slug": "the-indus-valley-civilisation-comprehensive-excavation-map",
                "order": 0,
                "title": "The Indus Valley Civilisation Comprehensive Excavation Map & Epigraphy",
                "description": "Comprehensive GIS excavation atlas across 49+ sites and 9 countries, Harappan urban planning, script concordance, metallurgy, maritime trade networks, and material culture.",
                "art": "indus-valley.svg"
            }
        ]

    elif cat['slug'] == 'empires-of-ancient-india' or cat['name'] == 'Empires of Ancient India':
        cat['name'] = 'Empires of Ancient India'
        cat['slug'] = 'empires-of-ancient-india'
        cat['title'] = 'Empires of Ancient India'
        cat['description'] = 'Interactive geospatial dynastic atlases from the 16 Mahajanapadas to the Classical Golden Ages (600 BCE – 850 CE), including Alexander the Great\'s trans-continental empire, changing territorial boundaries, decisive battles, and original script epigraphs in Brahmi, Sanskrit, Greek, and Tamil.'
        cat['art'] = 'ancient-empires.svg'
        cat['subgroups'] = [
            {
                "name": "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions",
                "slug": "empires-of-ancient-india-atlas",
                "order": 0,
                "title": "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions",
                "description": "Interactive dynastic atlases mapping 10 major imperial eras, territorial boundary shifts, decisive battlefields, and epigraphic records in original ancient scripts with official citations.",
                "art": "ancient-empires.svg"
            }
        ]

# 2. Update Indicators
IVC_SUBGROUP_NAME = "The Indus Valley Civilisation Comprehensive Excavation Map"
IVC_SUBGROUP_SLUG = "the-indus-valley-civilisation-comprehensive-excavation-map"

EMP_SUBGROUP_NAME = "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions"
EMP_SUBGROUP_SLUG = "empires-of-ancient-india-atlas"

for ind in catalog['indicators']:
    if ind.get('category') == 'Indus Valley Civilisation':
        ind['subgroup'] = IVC_SUBGROUP_NAME
        ind['subgroup_slug'] = IVC_SUBGROUP_SLUG
    elif ind.get('category') == 'Empires of Ancient India':
        ind['subgroup'] = EMP_SUBGROUP_NAME
        ind['subgroup_slug'] = EMP_SUBGROUP_SLUG

with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print("Successfully consolidated categories and updated indicators in catalog.json.")
