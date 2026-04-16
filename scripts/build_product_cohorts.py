"""Step 1: Delete all __PROBE__ segments.
Step 2: Build 6 production product cohorts (AR/EN × Ponytail/Clip/Tape).
Step 3: Poll counts and print final summary.
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

# ===== Probe segments to delete =====
PROBES = ['QT8Fzv', 'TqYCb5', 'U9ebbs', 'X6epvY', 'SCtNQd', 'T6ekL4',
          'VThitY', 'UyBWTk', 'XgyUfv', 'XurF9a']

# ===== Product cohort definitions =====
# metric_id XFDwkK = Shopify Ordered Product
PRODUCTS = {
    'ponytail':  {'id': '6926370701357', 'sku_prefix': 'BWRK20PT', 'name_ar': 'اكستنشن ذيل حصان'},
    'clip_in':   {'id': '6926371979309', 'sku_prefix': 'LS209CLP', 'name_ar': 'اكستنشن كلبسات'},
    'tape_in':   {'id': '6926374633517', 'sku_prefix': 'US18PS',   'name_ar': 'اكستنشن تيب'},
}

COHORTS = [
    ('ar', 'ponytail', 'AR | Bought Ponytail'),
    ('ar', 'clip_in',  'AR | Bought Clip-in Extensions'),
    ('ar', 'tape_in',  'AR | Bought Tape-in Extensions'),
    ('en', 'ponytail', 'EN | Bought Ponytail'),
    ('en', 'clip_in',  'EN | Bought Clip-in Extensions'),
    ('en', 'tape_in',  'EN | Bought Tape-in Extensions'),
]

def http(method, url, body=None):
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {'__error__': True, 'code': e.code, 'body': body}

def delete(sid):
    return http('DELETE', f'https://a.klaviyo.com/api/segments/{sid}/')

def list_processing():
    """Count segments currently processing."""
    url = 'https://a.klaviyo.com/api/segments/?filter=equals(is_processing,true)&fields[segment]=is_processing'
    r = http('GET', url)
    if r and not r.get('__error__'):
        return len(r.get('data', []))
    return 0

def wait_for_slot(max_active=4):
    """Wait until fewer than max_active segments are processing."""
    while True:
        n = list_processing()
        if n < max_active:
            return
        print(f'    [waiting: {n} segments processing]')
        time.sleep(15)

def create_cohort(lang, prod_key, name):
    pid = PRODUCTS[prod_key]['id']
    defn = {
        'condition_groups': [
            {'conditions': [{
                'type': 'profile-property',
                'property': "properties['$locale_language']",
                'filter': {'type': 'string', 'operator': 'equals', 'value': lang}
            }]},
            {'conditions': [{
                'type': 'profile-metric',
                'metric_id': 'XFDwkK',  # Ordered Product (Shopify)
                'measurement': 'count',
                'measurement_filter': {'type': 'numeric', 'operator': 'greater-than', 'value': 0},
                'timeframe_filter': {'type': 'date', 'operator': 'alltime'},
                'metric_filters': [{
                    'property': 'ProductID',
                    'filter': {'type': 'string', 'operator': 'equals', 'value': pid}
                }]
            }]}
        ]
    }
    payload = {'data': {'type': 'segment', 'attributes': {'name': name, 'definition': defn, 'is_starred': False}}}
    r = http('POST', 'https://a.klaviyo.com/api/segments/', payload)
    if r.get('__error__'):
        print(f'  CREATE FAILED [{name}]: {r["body"][:300]}')
        return None
    return r['data']['id']

def get_count(seg_id):
    r = http('GET', f'https://a.klaviyo.com/api/segments/{seg_id}?additional-fields[segment]=profile_count')
    if r.get('__error__'):
        return None, None
    a = r['data']['attributes']
    return a.get('is_processing'), a.get('profile_count')

# === STEP 1: delete probes ===
print('=== STEP 1: deleting probe segments ===')
for p in PROBES:
    r = delete(p)
    if r and r.get('__error__'):
        print(f'  {p}: skip ({r["code"]})')
    else:
        print(f'  {p}: deleted')

# === STEP 2: create cohorts (wait for slot before each) ===
print('\n=== STEP 2: creating 6 product cohorts ===')
created = {}
for lang, prod, name in COHORTS:
    wait_for_slot(4)
    sid = create_cohort(lang, prod, name)
    if sid:
        print(f'  {lang}_{prod} -> {sid}  "{name}"')
        created[(lang, prod)] = {'id': sid, 'name': name, 'product_id': PRODUCTS[prod]['id']}
    time.sleep(1)

# === STEP 3: poll ===
print('\n=== STEP 3: polling counts ===')
time.sleep(30)
for attempt in range(25):
    all_done = True
    for (lang, prod), info in created.items():
        p, c = get_count(info['id'])
        info['processing'] = p
        info['count'] = c
        if p or c is None:
            all_done = False
    print(f'\n--- Poll {attempt} ---')
    for (lang, prod), info in created.items():
        print(f'  {lang}_{prod} ({info["id"]}): processing={info.get("processing")} count={info.get("count")}')
    if all_done:
        break
    time.sleep(20)

# === SUMMARY ===
print('\n\n=== FINAL SUMMARY ===')
for (lang, prod), info in created.items():
    print(f'  {info["name"]:<45} id={info["id"]}  count={info.get("count")}')

# Write out the registry snippet
out = {}
for (lang, prod), info in created.items():
    out.setdefault(lang, {})[f'bought_{prod}'] = {
        'id': info['id'],
        'name': info['name'],
        'product_id': info['product_id'],
        'profile_count': info.get('count')
    }
print('\nRegistry snippet:')
print(json.dumps(out, indent=2, ensure_ascii=False))
with open('tmp_cohort_build.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('\nSaved to tmp_cohort_build.json')
