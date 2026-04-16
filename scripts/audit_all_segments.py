"""Pull ALL segments in the account with profile counts + definitions.
Audit for duplicates, gaps, quality issues.
"""
import os, sys, json, urllib.request, time
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

KEY = os.getenv('KLAVIYO_PRIVATE_API_KEY')
HEADERS = {'Authorization': f'Klaviyo-API-Key {KEY}', 'accept': 'application/vnd.api+json', 'revision': '2024-10-15'}

def http_get(url, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (i + 1)); continue
            raise

# Paginate all segments (no additional-fields since that needs per-segment fetch)
all_segs = []
url = 'https://a.klaviyo.com/api/segments/'
while url:
    d = http_get(url)
    all_segs.extend(d['data'])
    url = d.get('links', {}).get('next')
    time.sleep(0.5)

print(f'Total segments: {len(all_segs)}')

# For each segment, get count + definition
enriched = []
for i, s in enumerate(all_segs):
    sid = s['id']
    try:
        d = http_get(f'https://a.klaviyo.com/api/segments/{sid}?additional-fields%5Bsegment%5D=profile_count')
        a = d['data']['attributes']
        enriched.append({
            'id': sid,
            'name': a.get('name'),
            'created': a.get('created'),
            'updated': a.get('updated'),
            'is_processing': a.get('is_processing'),
            'profile_count': a.get('profile_count'),
            'definition': a.get('definition')
        })
        if (i+1) % 10 == 0:
            print(f'  fetched {i+1}/{len(all_segs)}')
    except Exception as e:
        print(f'  {sid} error: {e}')
    time.sleep(0.6)

# Sort by created desc
enriched.sort(key=lambda x: x.get('created') or '', reverse=True)

# Dump to file for analysis
with open('tmp_all_segments.json', 'w', encoding='utf-8') as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)
print(f'\nSaved {len(enriched)} segments to tmp_all_segments.json')

# Print compact table
print(f'\n{"Count":>7}  {"ID":<8}  {"Created":<10}  Name')
print('-' * 100)
for s in enriched:
    c = s.get('profile_count')
    c_str = str(c) if c is not None else ('proc' if s.get('is_processing') else '?')
    print(f'{c_str:>7}  {s["id"]:<8}  {(s.get("created") or "")[:10]:<10}  {(s.get("name") or "")[:80]}')
