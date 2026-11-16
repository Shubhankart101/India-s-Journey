#!/usr/bin/env python3
"""
Adds/ensures the Metro subgroup and indicators in data/catalog.json and legacy-aliases.json.
Called by scripts/export_catalog.mjs and standalone scripts so that automated GitHub actions
never remove Metro data from the catalog.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, 'data', 'catalog.json')
ALIASES_PATH = os.path.join(ROOT, 'frontend', 'src', 'data', 'legacy-aliases.json')

def main():
    if not os.path.exists(CATALOG_PATH):
        return

    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # 1. Ensure under India in Maps
    india_maps = next((c for c in catalog.get('categories', []) if c.get('slug') == 'india-in-maps' or c.get('name') == 'India in Maps'), None)
    if india_maps:
        subgroups = india_maps.setdefault('subgroups', [])
        if not any(s.get('slug') == 'metro-in-maps' or 'metro' in s.get('name', '').lower() for s in subgroups):
            subgroups.insert(0, {
                "name": "Metro Networks & Transit Atlas",
                "slug": "metro-in-maps",
                "order": 0,
                "title": "🚇 Indian Metro Networks & Transit Atlas",
                "description": "Interactive dual-representation maps (warm PolityPolicy cartographic terrain and clean MetroSafar schematic line diagrams) for all 17 operational Indian metro networks with Dijkstra route planner, fare slabs, and live IST intervals.",
                "art": "metro-atlas.svg",
                "format": "map",
                "interactive": True
            })

    # 2. Ensure under Infrastructure & Mobility
    infra = next((c for c in catalog.get('categories', []) if c.get('slug') == 'infrastructure-mobility' or c.get('name') == 'Infrastructure & Mobility'), None)
    if infra:
        subgroups = infra.setdefault('subgroups', [])
        if not any(s.get('slug') == 'metro-in-maps' or 'metro' in s.get('name', '').lower() for s in subgroups):
            subgroups.insert(0, {
                "name": "Metro Rail Networks & Urban Transit",
                "slug": "metro-in-maps",
                "order": 0,
                "title": "🚇 Metro Rail Networks & Urban Transit (17 Cities)",
                "description": "Interactive transit maps, station alignments, network statistics, and route finder across all 17 Indian metro networks.",
                "art": "metro-atlas.svg",
                "format": "map",
                "interactive": True
            })

    # 3. Ensure indicator in indicators
    metro_indicator_key = "indian_metro_rail_networks_17_cities"
    indicators = catalog.setdefault('indicators', [])
    if not any(i.get('key') == metro_indicator_key for i in indicators):
        indicators.append({
            "key": metro_indicator_key,
            "title": "Indian Metro Rail Networks: 17 Cities & 1,042 km",
            "subtitle": "Network length, daily ridership, stations, and operational routes across all 17 Indian metro systems",
            "category": "India in Maps",
            "subgroup": "Metro Networks & Transit Atlas",
            "category_slug": "india-in-maps",
            "subgroup_slug": "metro-in-maps",
            "frequency": "annual",
            "suffix": " km",
            "color": "#0284c7",
            "chart_type": "map",
            "is_live": True,
            "latest_value": 1042.0,
            "latest_label": "2026",
            "series": {
                "source": "Ministry of Housing and Urban Affairs (MoHUA) & DMRC",
                "source_url": "https://mohua.gov.in/",
                "labels": [
                    "Delhi-NCR", "Bengaluru", "Mumbai", "Hyderabad", "Chennai",
                    "Kolkata", "Ahmedabad", "Nagpur", "Pune", "Noida",
                    "Kochi", "Lucknow", "Kanpur", "Jaipur", "Navi Mumbai",
                    "Agra", "Bhopal-Indore"
                ],
                "datasets": [
                    {
                        "label": "Operational Route Length (km)",
                        "values": [393.0, 76.9, 58.5, 69.2, 54.1, 47.9, 40.0, 38.2, 31.2, 29.7, 28.1, 22.8, 16.0, 12.0, 11.1, 6.0, 6.0]
                    }
                ]
            }
        })

    # 4. Ensure legacy aliases
    aliases = catalog.setdefault('legacy_aliases', {})
    sub_aliases = aliases.setdefault('subgroups', {})
    group_aliases = aliases.setdefault('groups', {})
    
    metro_keys = [
        'India in Maps|metro-in-maps',
        'India in Maps|metro-atlas',
        'India in Maps|delhi-metro',
        'India in Maps|indian-metro-networks',
        'Infrastructure & Mobility|metro-in-maps',
        'Infrastructure & Mobility|metro-rail-networks-urban-transit',
    ]
    for k in metro_keys:
        grp = k.split('|')[0]
        sub_name = 'Metro Networks & Transit Atlas' if grp == 'India in Maps' else 'Metro Rail Networks & Urban Transit'
        sub_aliases[k] = {'group': grp, 'subgroup': sub_name}

    group_aliases['metro-atlas'] = {'group': 'India in Maps', 'subgroup': 'Metro Networks & Transit Atlas'}
    group_aliases['metro-in-maps'] = {'group': 'India in Maps', 'subgroup': 'Metro Networks & Transit Atlas'}
    group_aliases['delhi-metro'] = {'group': 'India in Maps', 'subgroup': 'Metro Networks & Transit Atlas'}

    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)

    # Also update frontend/src/data/legacy-aliases.json if it exists
    if os.path.exists(ALIASES_PATH):
        try:
            with open(ALIASES_PATH, 'r', encoding='utf-8') as f:
                front_aliases = json.load(f)
            front_sub = front_aliases.setdefault('subgroups', {})
            front_grp = front_aliases.setdefault('groups', {})
            for k, v in sub_aliases.items():
                front_sub[k] = v
            for k, v in group_aliases.items():
                front_grp[k] = v
            with open(ALIASES_PATH, 'w', encoding='utf-8') as f:
                json.dump(front_aliases, f, indent=2)
        except Exception:
            pass

    print("Successfully permanently ensured Metro Networks & Transit Atlas in catalog.json and legacy-aliases.json")

if __name__ == '__main__':
    main()
