"""Build AR/EN | Buyers 365d — broader re-activation/promo cohort.
Same pattern as buyers_90d (US9JzM, W3yztD) with timeframe = 365d.
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

def http(method, url, body=None, retries=5):
    data = json.dumps(body).encode('utf-8') if body else None
    for i in range(retries):
        req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read()) if resp.status != 204 else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (i + 1))
                continue
            return {'__error__': True, 'code': e.code, 'body': e.read().decode()}
    return {'__error__': True, 'code': 429, 'body': 'rate-limited'}

def count_processing():
    r = http('GET', 'https://a.klaviyo.com/api/segments/?filter=equals(is_processing,true)&fields[segment]=is_processing')
    if r and not r.get('__error__'):
        return len(r.get('data', []))
    return 0

def wait_slot(max_active=3):
    while True:
        n = count_processing()
        if n < max_active:
            return
        print(f'  waiting: {n} processing')
        time.sleep(15)

def create_buyers_365(name, lang):
    defn = {
        'condition_groups': [
            {'conditions': [{
                'type': 'profile-property',
                'property': "properties['$locale_language']",
                'filter': {'type': 'string', 'operator': 'equals', 'value': lang}
            }]},
            {'conditions': [{
                'type': 'profile-metric',
                'metric_id': 'RFkPcF',  # Placed Order (Shopify canonical)
                'measurement': 'count',
                'measurement_filter': {'type': 'numeric', 'operator': 'greater-than', 'value': 0},
                'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'day', 'quantity': 365}
            }]}
        ]
    }
    payload = {'data': {'type': 'segment', 'attributes': {'name': name, 'definition': defn, 'is_starred': False}}}
    r = http('POST', 'https://a.klaviyo.com/api/segments/', payload)
    if r.get('__error__'):
        print(f'CREATE FAILED: {r["body"][:300]}')
        return None
    return r['data']['id']

def get_count(sid, retries=15):
    for i in range(retries):
        r = http('GET', f'https://a.klaviyo.com/api/segments/{sid}?additional-fields[segment]=profile_count')
        if r.get('__error__'):
            time.sleep(8)
            continue
        a = r['data']['attributes']
        p = a.get('is_processing')
        c = a.get('profile_count')
        if not p and c is not None:
            return c
        time.sleep(8)
    return None

results = {}

# AR
wait_slot(3)
ar_id = create_buyers_365('AR | Buyers 365d', 'ar')
print(f'AR | Buyers 365d: {ar_id}')
if ar_id:
    results['ar'] = {'id': ar_id, 'name': 'AR | Buyers 365d'}

# EN
wait_slot(3)
en_id = create_buyers_365('EN | Buyers 365d', 'en')
print(f'EN | Buyers 365d: {en_id}')
if en_id:
    results['en'] = {'id': en_id, 'name': 'EN | Buyers 365d'}

# Poll counts
print('\nWaiting 30s then polling...')
time.sleep(30)
for lang, info in results.items():
    c = get_count(info['id'])
    info['profile_count'] = c
    print(f'  {info["name"]:<25} id={info["id"]}  count={c}')

with open('tmp_buyers_365d.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\nSaved tmp_buyers_365d.json')
