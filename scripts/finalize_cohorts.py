"""Create missing EN | Bought Tape-in + confirm all 6 counts."""
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

EXISTING = {
    'ar_ponytail': ('U7dEVT', 'AR | Bought Ponytail', '6926370701357'),
    'ar_clip_in':  ('Y9PXSG', 'AR | Bought Clip-in Extensions', '6926371979309'),
    'ar_tape_in':  ('XsbEUF', 'AR | Bought Tape-in Extensions', '6926374633517'),
    'en_ponytail': ('YwXft9', 'EN | Bought Ponytail', '6926370701357'),
    'en_clip_in':  ('Smq3Ch', 'EN | Bought Clip-in Extensions', '6926371979309'),
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

def create(name, lang, pid):
    defn = {
        'condition_groups': [
            {'conditions': [{
                'type': 'profile-property',
                'property': "properties['$locale_language']",
                'filter': {'type': 'string', 'operator': 'equals', 'value': lang}
            }]},
            {'conditions': [{
                'type': 'profile-metric',
                'metric_id': 'XFDwkK',
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
        print(f'CREATE FAILED: {r["body"][:300]}')
        return None
    return r['data']['id']

def get_count(sid, retries=10):
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

# Wait for slot, create missing segment
wait_slot(3)
en_tape = create('EN | Bought Tape-in Extensions', 'en', '6926374633517')
print(f'EN | Bought Tape-in Extensions: {en_tape}')
if en_tape:
    EXISTING['en_tape_in'] = (en_tape, 'EN | Bought Tape-in Extensions', '6926374633517')

# Get all counts
print('\nFetching final counts (with retries through rate limits)...')
results = {}
for key, (sid, name, pid) in EXISTING.items():
    c = get_count(sid)
    results[key] = {'id': sid, 'name': name, 'product_id': pid, 'profile_count': c}
    print(f'  {name:<45} id={sid}  count={c}')

with open('tmp_cohort_final.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\nSaved tmp_cohort_final.json')
