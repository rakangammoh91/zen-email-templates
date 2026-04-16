"""Dump the full RraB6N definition so we know what to fix.
Also verify whether metric Xf2suC still returns any events.
"""
import os, sys, json, urllib.request
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

KEY = os.getenv('KLAVIYO_PRIVATE_API_KEY')
HEADERS = {'Authorization': f'Klaviyo-API-Key {KEY}', 'accept': 'application/vnd.api+json', 'revision': '2024-10-15'}

def http_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# 1. Full RraB6N definition
seg = http_get('https://a.klaviyo.com/api/segments/RraB6N?additional-fields%5Bsegment%5D=profile_count')
a = seg['data']['attributes']
print(f'NAME: {a.get("name")}')
print(f'COUNT: {a.get("profile_count")}')
print(f'UPDATED: {a.get("updated")}')
print('\nFULL DEFINITION:')
print(json.dumps(a.get('definition'), ensure_ascii=False, indent=2))

# 2. Lookup Xf2suC metric
print('\n\n--- METRIC Xf2suC ---')
try:
    m = http_get('https://a.klaviyo.com/api/metrics/Xf2suC')
    ma = m['data']['attributes']
    print(f'NAME: {ma.get("name")}')
    print(f'INTEGRATION: {ma.get("integration")}')
    print(f'CREATED: {ma.get("created")}')
    print(f'UPDATED: {ma.get("updated")}')
except Exception as e:
    print(f'ERROR: {e}')

# 3. All metrics index (to see what the intended metric might be)
print('\n\n--- ALL METRICS ---')
m = http_get('https://a.klaviyo.com/api/metrics/')
for d in m['data']:
    a = d['attributes']
    print(f'  {d["id"]:<10} {a.get("integration",{}).get("name","?"):<15} {a.get("name")}')
