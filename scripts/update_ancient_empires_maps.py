import json

data_path = 'frontend/src/data/ancient-empires.json'
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

map_refs = {
    'mahajanapadas': {
        'svg': 'maps/historical/mahajanapadas.svg',
        'title': "The Sixteen Mahājanapadas — India's First Republics & Kingdoms (c. 600–345 BCE)"
    },
    'magadha-nanda': {
        'svg': 'maps/historical/later-vedic.svg',
        'title': "The Later Vedic Age — Janapadas of the Gangetic Plain (c. 1100–600 BCE)"
    },
    'alexander-campaign': {
        'svg': 'maps/historical/post-mauryan-indo-greek.svg',
        'title': "After the Mauryas — Shungas, Greeks and Sakas (c. 185 BCE–50 CE)"
    },
    'maurya-empire': {
        'svg': 'maps/historical/mauryan-empire.svg',
        'title': "The First Empire — India under the Mauryas (c. 322–185 BCE)"
    },
    'indo-greek-shunga': {
        'svg': 'maps/historical/post-mauryan-indo-greek.svg',
        'title': "After the Mauryas — Shungas, Greeks and Sakas (c. 185 BCE–50 CE)"
    },
    'satavahana-empire': {
        'svg': 'maps/historical/satavahana-empire.svg',
        'title': "The Deccan Bridge — the Sātavāhana Age (c. 100 BCE–220 CE)"
    },
    'kushan-empire': {
        'svg': 'maps/historical/kushan-empire.svg',
        'title': "The Crossroads Empire — India under the Kushans (c. 30–375 CE)"
    },
    'gupta-empire': {
        'svg': 'maps/historical/gupta-empire.svg',
        'title': "India in the Gupta Golden Age (c. 320–550 CE)"
    },
    'harsha-empire': {
        'svg': 'maps/historical/harsha-empire.svg',
        'title': "North India in the Age of Harshavardhana (c. 600–650 CE)"
    },
    'classical-southern-dynasties': {
        'svg': 'maps/historical/chola-empire.svg',
        'title': "The Imperial Cholas — Rājarāja I & Rājendra I (c. 985–1150 CE)"
    }
}

for emp in data['empires']:
    eid = emp['id']
    if eid in map_refs:
        emp['historical_map_svg'] = map_refs[eid]['svg']
        emp['historical_map_title'] = map_refs[eid]['title']

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated ancient-empires.json with historical_map_svg references!")
