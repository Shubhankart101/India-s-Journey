import glob, os, re, xml.etree.ElementTree as ET

def clean_svg(data):
    # 1. Background full-size rects (sky, ground bars, lower overlays, vignettes, grains)
    # Remove rects with full dimensions (1200x600, 1600x900, 1200x660, 1220x110 ground, 100%x100%)
    # or rects filling with sky, lower, vignette, grain, ground gradients
    data = re.sub(
        r'<rect[^>]+(?:fill=["\'](?:url\(#(?:sky|lower|vignette|grain|map-lower|map-vignette|map-grain|ground|dawn|evening|poll|lotus|rail|lin\d)[^)]*\)|#[0-9a-fA-F]{3,8})["\'][^>]+(?:width=["\'](?:1200|1600|1220|100%)["\']|height=["\'](?:600|900|660|110|100%)["\'])|width=["\'](?:1200|1600|100%)["\'][^>]+height=["\'](?:600|900|660|100%)["\'][^>]+fill=["\'][^"\']+["\'])[^>]*\/?>',
        '',
        data
    )

    # Catch any remaining standalone full-canvas rects
    data = re.sub(
        r'<rect\s+width=["\'](?:1200|1600|100%)["\']\s+height=["\'](?:600|900|660|100%)["\'][^>]*\/?>',
        '',
        data
    )
    data = re.sub(
        r'<rect\s+x=["\']-?\d+["\']\s+y=["\'](?:500|520|0)["\']\s+width=["\'](?:1200|1220|1600)["\']\s+height=["\'](?:110|100|600|900)["\'][^>]*\/?>',
        '',
        data
    )

    # 2. Remove bottom text headers inside SVG that duplicate the HTML title/subtitle
    # e.g. <text x="600" y="495"...>Title</text>
    # <text x="600" y="538"...>SUBTITLE</text>
    # <text x="600" y="488"...>Economy</text>
    # <text x="600" y="535"...>INDIA • PUBLIC DATA ATLAS</text>
    # <text x="48" y="570"...>...</text>
    # <text x="50" y="612"...>...</text>
    data = re.sub(
        r'<text\s+[^>]*y=["\'](?:488|495|535|538|570|612|620)["\'][^>]*>.*?<\/text>',
        '',
        data,
        flags=re.DOTALL
    )
    # Generic INDIA • PUBLIC DATA ATLAS text
    data = re.sub(
        r'<text[^>]*>.*?INDIA\s+[•\u2022\u00b7]\s+PUBLIC DATA ATLAS.*?<\/text>',
        '',
        data,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Clean empty comments or leftover whitespace
    data = re.sub(r'<!--\s*(?:Background sky|Bottom vignette and title|Foreground shapes &amp; bespoke art)?\s*-->', '', data)
    return data

def main():
    art_dirs = ['frontend/public/art', 'docs/art', 'frontend/dist/art']
    files = glob.glob('frontend/public/art/*.svg')
    print(f"Processing {len(files)} SVGs...")

    cleaned_count = 0
    errors = 0

    for fpath in files:
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8') as f:
            orig = f.read()

        cleaned = clean_svg(orig)

        # Validate with XML parser
        try:
            ET.fromstring(cleaned)
        except Exception as e:
            print(f"Error parsing cleaned {fname}: {e}")
            errors += 1
            continue

        # Write to all art directories
        for adir in art_dirs:
            if os.path.exists(adir):
                target = os.path.join(adir, fname)
                with open(target, 'w', encoding='utf-8') as out:
                    out.write(cleaned)

        cleaned_count += 1

    print(f"Done! Cleaned: {cleaned_count}, Errors: {errors}")

if __name__ == '__main__':
    main()
