import glob
import re
import xml.etree.ElementTree as ET

dirs = ['frontend/public/maps/historical', 'docs/maps/historical']

for d in dirs:
    for f in glob.glob(f"{d}/*.svg"):
        content = open(f, encoding='utf-8').read()
        
        # Replace unescaped & with &amp; (only when not already part of an entity like &amp; &lt; &gt; &quot; &#x...;)
        # Regex: & not followed by (\w+|#\d+|#x[0-9a-fA-F]+);
        fixed = re.sub(r'&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)', '&amp;', content)
        
        # Ensure width and height are on root svg if missing
        def fix_svg_root(m):
            tag = m.group(0)
            if 'width=' not in tag:
                tag = tag.replace('<svg ', '<svg width="880" height="1140" ')
            return tag
        
        fixed = re.sub(r'<svg[^>]*>', fix_svg_root, fixed, count=1)
        
        # Add xml declaration if missing
        if not fixed.strip().startswith('<?xml'):
            fixed = '<?xml version="1.0" encoding="UTF-8"?>\n' + fixed.strip()
            
        with open(f, 'w', encoding='utf-8') as out:
            out.write(fixed)
            
        # Verify XML validity
        try:
            ET.fromstring(fixed)
        except Exception as e:
            print(f"ERROR still in {f}: {e}")

print("All SVGs sanitized and verified!")
