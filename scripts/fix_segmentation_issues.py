"""Execute 3 segmentation fixes approved by user:

1. DELETE YaDY3x (leaked __PROBE_A__ Items contains اكستنشن, count=0)
2. RENAME two 'AM | Exclude | Bots' segments for disambiguation:
   - XUf7Wy (pattern-match on email/name)  ->  'AM | Exclude | Bots (pattern)'
   - Wu33h2 (behavioral zero-engagement)   ->  'AM | Exclude | Bots (behavioral)'
3. PATCH RraB6N 'AM | Exclude | Clean #4':
   - replace dead metric Xf2suC (API Placed Order)     -> RFkPcF (Shopify Placed Order)
   - replace dead metric VsAyY9 (API Started Checkout) -> UDbxB2 (Shopify Checkout Started)
   Both API metrics have zero events since 2024-07-18.

Then poll RraB6N for its new profile_count.
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
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (i + 1)); continue
            return {'__error__': True, 'code': e.code, 'body': e.read().decode()}
    return {'__error__': True, 'code': 429}

def rename(sid, new_name):
    return http('PATCH', f'https://a.klaviyo.com/api/segments/{sid}/', {
        'data': {'type': 'segment', 'id': sid, 'attributes': {'name': new_name}}
    })

# ==================== 1. DELETE YaDY3x ====================
print('=== 1. Deleting leaked probe YaDY3x ===')
r = http('DELETE', 'https://a.klaviyo.com/api/segments/YaDY3x/')
if r and r.get('__error__'):
    print(f'  FAIL [{r["code"]}]: {r.get("body","")[:200]}')
else:
    print('  deleted')

# ==================== 2. RENAME bots ====================
print('\n=== 2. Renaming Bots segments ===')
for sid, new in [
    ('XUf7Wy', 'AM | Exclude | Bots (pattern)'),
    ('Wu33h2', 'AM | Exclude | Bots (behavioral)'),
]:
    r = rename(sid, new)
    if r and r.get('__error__'):
        print(f'  {sid} FAIL [{r["code"]}]: {r.get("body","")[:200]}')
    else:
        print(f'  {sid} -> "{new}"')

# ==================== 3. PATCH RraB6N ====================
print('\n=== 3. Patching RraB6N Clean #4 (dead metrics) ===')

# Rebuild full definition with metric_id swaps
NEW_DEFN = {
    'condition_groups': [
        {'conditions': [{
            'type': 'profile-marketing-consent',
            'consent': {'channel': 'email', 'can_receive_marketing': True,
                        'consent_status': {'subscription': 'any', 'filters': None}}
        }]},
        {'conditions': [{
            'type': 'profile-property', 'property': 'created',
            'filter': {'type': 'date', 'operator': 'at-least', 'unit': 'day', 'quantity': 180}
        }]},
        # SL8pK9 Received Email > 0
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'SL8pK9', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'greater-than', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
        # WXZdnJ Opened Email = 0
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'WXZdnJ', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'equals', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
        # VNAnuS Clicked Email = 0
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'VNAnuS', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'equals', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
        # U2auYp Active on Site (API) = 0  -- leaving as-is; both API & Klaviyo fire
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'U2auYp', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'equals', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
        # XB2fZm Viewed Product = 0
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'XB2fZm', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'equals', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
        # FIX: VsAyY9 API Started Checkout (dead) -> UDbxB2 Shopify Checkout Started
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'UDbxB2', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'equals', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
        # FIX: Xf2suC API Placed Order (dead) -> RFkPcF Shopify Placed Order
        {'conditions': [{
            'type': 'profile-metric', 'metric_id': 'RFkPcF', 'measurement': 'count',
            'measurement_filter': {'type': 'numeric', 'operator': 'equals', 'value': 0},
            'timeframe_filter': {'type': 'date', 'operator': 'in-the-last', 'unit': 'week', 'quantity': 72},
            'metric_filters': None
        }]},
    ]
}

r = http('PATCH', 'https://a.klaviyo.com/api/segments/RraB6N/', {
    'data': {'type': 'segment', 'id': 'RraB6N',
             'attributes': {'definition': NEW_DEFN}}
})
if r and r.get('__error__'):
    print(f'  PATCH FAIL [{r["code"]}]: {r.get("body","")[:500]}')
    sys.exit(1)
else:
    print('  patched')

# ==================== POLL NEW COUNT ====================
print('\n=== Waiting for RraB6N to reprocess ===')
time.sleep(30)
for _ in range(30):
    r = http('GET', 'https://a.klaviyo.com/api/segments/RraB6N?additional-fields[segment]=profile_count')
    if r.get('__error__'):
        time.sleep(10); continue
    a = r['data']['attributes']
    p, c = a.get('is_processing'), a.get('profile_count')
    if not p and c is not None:
        print(f'  RraB6N (Clean #4) new profile_count = {c}  (was 2859 with broken filter)')
        break
    print(f'  processing... (so far c={c})')
    time.sleep(10)
else:
    print('  TIMEOUT: still processing. Poll later.')

print('\nDONE.')
