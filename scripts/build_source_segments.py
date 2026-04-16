"""Build 3 production subscriber-source segments via list membership.

1. Source | Organic Site Signup  — member of Ri2yYm (main sign-up form)
2. Source | Free Sample Funnel   — member of XVHa6u OR WXdiNn OR TZgyzu (OR'd)
3. Source | Paid Funnel (GHL)    — member of SZ7nKa OR Sq7Aex (OR'd)

Use profile-group-membership condition type. Within one condition_group,
multiple conditions are OR'd.
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
                time.sleep(10 * (i + 1)); continue
            return {'__error__': True, 'code': e.code, 'body': e.read().decode()}
    return {'__error__': True, 'code': 429}

def count_processing():
    r = http('GET', 'https://a.klaviyo.com/api/segments/?filter=equals(is_processing,true)&fields[segment]=is_processing')
    return len(r.get('data', [])) if r and not r.get('__error__') else 0

def wait_slot(max_active=3):
    while count_processing() >= max_active:
        time.sleep(12)

def list_membership(list_id):
    return {
        'type': 'profile-group-membership',
        'is_member': True,
        'group_ids': [list_id]
    }

def create_segment(name, condition_groups):
    r = http('POST', 'https://a.klaviyo.com/api/segments/', {
        'data': {'type': 'segment', 'attributes': {
            'name': name,
            'definition': {'condition_groups': condition_groups},
            'is_starred': False
        }}
    })
    if r.get('__error__'):
        print(f'CREATE FAILED [{name}]: {r["body"][:300]}')
        return None
    return r['data']['id']

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

# === 1. Organic Site Signup — just Ri2yYm membership ===
wait_slot(3)
organic_id = create_segment(
    'Source | Organic Site Signup',
    [{'conditions': [list_membership('Ri2yYm')]}]
)
print(f'Source | Organic Site Signup: {organic_id}')

# === 2. Free Sample Funnel — OR'd membership ===
wait_slot(3)
sample_conds = [list_membership(lid) for lid in ['XVHa6u', 'WXdiNn', 'TZgyzu']]
sample_id = create_segment(
    'Source | Free Sample Funnel',
    [{'conditions': sample_conds}]
)
print(f'Source | Free Sample Funnel: {sample_id}')

# === 3. Paid Funnel (GHL) ===
wait_slot(3)
ghl_conds = [list_membership(lid) for lid in ['SZ7nKa', 'Sq7Aex']]
ghl_id = create_segment(
    'Source | Paid Funnel (GHL)',
    [{'conditions': ghl_conds}]
)
print(f'Source | Paid Funnel (GHL): {ghl_id}')

# === poll counts ===
print('\nPolling counts...')
time.sleep(30)
results = {}
for name, sid in [
    ('Source | Organic Site Signup', organic_id),
    ('Source | Free Sample Funnel', sample_id),
    ('Source | Paid Funnel (GHL)', ghl_id),
]:
    if sid:
        c = get_count(sid)
        results[name] = {'id': sid, 'profile_count': c}
        print(f'  {name:<35} {sid}  count={c}')

with open('tmp_source.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
