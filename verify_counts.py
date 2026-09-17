import json
import re

app_js = open('docs/app.js', encoding='utf-8').read()
data_js = open('docs/data.js', encoding='utf-8').read()

prefix = 'window.INDIA_DASHBOARD_DATA = '
suffix = ';\n'
data = json.loads(data_js[len(prefix):-len(suffix)])
series = data.get('series', {})

def_keys = re.findall(r"^\s*\[['\"]([^'\"]+)['\"]", app_js, re.MULTILINE)
print('Total indicator definitions in app.js:', len(def_keys))
print('Total series in data.js:', len(series))

missing_in_data = [k for k in def_keys if k not in series]
print('Missing in data.js:', missing_in_data)

non_live = []
for k in def_keys:
    s = series.get(k)
    is_live = s and not s.get('error') and (s.get('values') or s.get('datasets'))
    if not is_live:
        non_live.append(k)

print('Non-live indicators count:', len(non_live))
if non_live:
    print('Non-live indicators:', non_live)
