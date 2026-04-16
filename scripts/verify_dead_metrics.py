"""Check if Xf2suC (API Placed Order) and VsAyY9 (API Started Checkout)
actually fire any events. If they do, we can't treat them as 'dead'.

Use /api/events with filter on metric_id."""
import os, sys, json, urllib.request
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

KEY = os.getenv('KLAVIYO_PRIVATE_API_KEY')
HEADERS = {'Authorization': f'Klaviyo-API-Key {KEY}', 'accept': 'application/vnd.api+json', 'revision': '2024-10-15'}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

for mid, name in [
    ('Xf2suC', 'API Placed Order (suspected dead)'),
    ('RFkPcF', 'Shopify Placed Order (active)'),
    ('VsAyY9', 'API Started Checkout (suspected dead)'),
    ('UDbxB2', 'Shopify Checkout Started (active)'),
]:
    try:
        d = get(f'https://a.klaviyo.com/api/events/?filter=equals(metric_id,"{mid}")&page[size]=1&sort=-datetime')
        events = d.get('data', [])
        if events:
            e = events[0]['attributes']
            print(f'{mid}  {name}: LATEST = {e.get("datetime")}')
        else:
            print(f'{mid}  {name}: NO EVENTS EVER')
    except Exception as e:
        print(f'{mid}  {name}: ERR {e}')
