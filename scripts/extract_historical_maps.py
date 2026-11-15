import glob
import os
import re

os.makedirs('frontend/public/maps/historical', exist_ok=True)
os.makedirs('docs/maps/historical', exist_ok=True)

map_mapping = {
    'south_asia_indus_civilisation.html': 'indus-civilisation.svg',
    'south_asia_vedic_era.html': 'later-vedic.svg',
    'south_asia_mahajanapadas_era.html': 'mahajanapadas.svg',
    'south_asia_mauryan_era.html': 'mauryan-empire.svg',
    'south_asia_post_mauryan_era.html': 'post-mauryan-indo-greek.svg',
    'south_asia_satavahana_era.html': 'satavahana-empire.svg',
    'south_asia_sangam_age.html': 'sangam-age.svg',
    'south_asia_kushan_era.html': 'kushan-empire.svg',
    'south_asia_gupta_era.html': 'gupta-empire.svg',
    'south_asia_harsha_era.html': 'harsha-empire.svg',
    'south_asia_chalukya_rashtrakuta_era.html': 'chalukya-rashtrakuta.svg',
    'south_asia_pallava_era.html': 'pallava-empire.svg',
    'south_asia_chola_era.html': 'chola-empire.svg',
    'south_asia_kingdoms_pala_era.html': 'pala-empire.svg',
    'south_asia_later_deccan_era.html': 'later-deccan.svg',
    'south_asia_delhi_sultanate_era.html': 'delhi-sultanate.svg',
    'south_asia_vijayanagara_era.html': 'vijayanagara-empire.svg',
    'south_asia_mughal_era.html': 'mughal-empire.svg',
    'south_asia_maratha_era.html': 'maratha-confederacy.svg',
    'south_asia_regional_powers_18c.html': 'regional-powers-18c.svg',
    'south_asia_sena_era.html': 'sena-empire.svg'
}

count = 0
for src_file, out_name in map_mapping.items():
    src_path = os.path.join('temp_repo', src_file)
    if not os.path.exists(src_path):
        print(f"Skipping {src_file}, not found")
        continue
    content = open(src_path, encoding='utf-8', errors='ignore').read()
    m = re.search(r'(<svg[^>]*class="map"[^>]*>.*?</svg>)', content, re.DOTALL)
    if not m:
        # try any svg
        m = re.search(r'(<svg[^>]*>.*?</svg>)', content, re.DOTALL)
    if m:
        svg_code = m.group(1)
        # Ensure xmlns is present
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_code:
            svg_code = svg_code.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ')
        
        # Write to frontend and docs
        p1 = os.path.join('frontend/public/maps/historical', out_name)
        p2 = os.path.join('docs/maps/historical', out_name)
        with open(p1, 'w', encoding='utf-8') as f:
            f.write(svg_code)
        with open(p2, 'w', encoding='utf-8') as f:
            f.write(svg_code)
        count += 1
        print(f"Saved {out_name} ({len(svg_code)//1024} KB)")

print(f"Successfully extracted {count} historical SVG maps!")
