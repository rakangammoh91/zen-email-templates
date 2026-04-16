"""Clean up geo probe segments and build 2 production geography segments.

Production segments:
1. Geo | KSA (Saudi Arabia only) — hero market 13,495 profiles
2. Geo | GCC ex-KSA (UAE, Kuwait, Bahrain, Qatar, Oman — OR'd) — ~2,740 profiles

Everything else (including ROW) can be composed via exclusion at campaign time.
"""
import os, sys, json, urllib.request, time
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

KEY = os.getenv('KLAVIYO_PRIVATE_API_KEY')
HEADERS = {
    'Authorization': f'Klaviyo-API-Key {KEY}',
    'accept': 'application/vnd.api+json',
    'content-type': 'application/vnd.api+json',
    'revision': '2024-10-15'
}

# Probe segments to delete
PROBES_TO_DELETE = [
    'UqUGaC',  # earlier country probe
    'YpQYPi',  # $country=SA probe
    'X5bDeE',  # $region=SA probe
    'VdUfvR',  # __PROBE__ country=Saudi Arabia
    'V9gZat',  # UAE probe
    'RtMXN7',  # Kuwait probe
    'TbAAXc',  # Bahrain probe
    'YueZ9f',  # Qatar probe
    'RFEJFL',  # Egypt probe
    'RwqdYY',  # UK probe
]

def http(method, url, body=None, retries=5):
    data = json.dumps(body).encode('utf-8') if body else None
    for i in range(retries):
        req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read()) if resp.status != 204 else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (i + 1)); continue
            return {'__error__': True, 'code': e.code, 'body': e.read().decode()}
    return {'__error__': True, 'code': 429}

def count_processing():
    r = http('GET', 'https://a.klaviyo.com/api/segments/?filter=equals(is_processing,true)&fields[segment]=is_processing')
    return len(r.get('data', [])) if r and not r.get('__error__') else 0

def wait_slot(max_active=3):
    while count_processing() >= max_active:
        time.sleep(12)

def get_count(sid, retries=20):
    for _ in range(retries):
        r = http('GET', f'https://a.klaviyo.com/api/segments/{sid}?additional-fields[segment]=profile_count')
        if r.get('__error__'):
            time.sleep(8); continue
        a = r['data']['attributes']
        p, c = a.get('is_processing'), a.get('profile_count')
        if not p and c is not None:
            return c
        time.sleep(8)
    return None

# === STEP 1: Delete probes ===
print('=== Deleting probe segments ===')
for p in PROBES_TO_DELETE:
    r = http('DELETE', f'https://a.klaviyo.com/api/segments/{p}/')
    if r and r.get('__error__'):
        print(f'  {p}: skip ({r["code"]})')
    else:
        print(f'  {p}: deleted')

# === STEP 2: Build production segments ===
print('\n=== Building production geo segments ===')

# 1. Geo | KSA
wait_slot(3)
ksa_defn = {
    'condition_groups': [{'conditions': [{
        'type': 'profile-property',
        'property': "properties['$country']",
        'filter': {'type': 'string', 'operator': 'equals', 'value': 'Saudi Arabia'}
    }]}]
}
r = http('POST', 'https://a.klaviyo.com/api/segments/', {
    'data': {'type': 'segment', 'attributes': {
        'name': 'Geo | KSA (Saudi Arabia)',
        'definition': ksa_defn,
        'is_starred': False
    }}
})
ksa_id = r['data']['id'] if not r.get('__error__') else None
print(f'Geo | KSA (Saudi Arabia): {ksa_id}')

# 2. Geo | GCC ex-KSA — UAE OR Kuwait OR Bahrain OR Qatar OR Oman (OR via same condition_group)
wait_slot(3)
gcc_conditions = [
    {'type': 'profile-property', 'property': "properties['$country']",
     'filter': {'type': 'string', 'operator': 'equals', 'value': c}}
    for c in ['United Arab Emirates', 'Kuwait', 'Bahrain', 'Qatar', 'Oman']
]
gcc_defn = {'condition_groups': [{'conditions': gcc_conditions}]}
r = http('POST', 'https://a.klaviyo.com/api/segments/', {
    'data': {'type': 'segment', 'attributes': {
        'name': 'Geo | GCC ex-KSA',
        'definition': gcc_defn,
        'is_starred': False
    }}
})
gcc_id = r['data']['id'] if not r.get('__error__') else None
print(f'Geo | GCC ex-KSA: {gcc_id}')
if not gcc_id:
    print(f'  error: {r.get("body", "")[:300]}')

# === STEP 3: poll counts ===
print('\n=== Polling final counts ===')
time.sleep(30)
results = {}
for name, sid in [('Geo | KSA (Saudi Arabia)', ksa_id), ('Geo | GCC ex-KSA', gcc_id)]:
    if sid:
        c = get_count(sid)
        results[name] = {'id': sid, 'profile_count': c}
        print(f'  {name:<30} {sid}  count={c}')

with open('tmp_geo_segments.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
