"""Print definitions of suspected-duplicate segments in compact form."""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

segs = json.load(open('tmp_all_segments.json', encoding='utf-8'))
suspects = {
    'YzbgxD': 'AI VIP Buyers',
    'VjjgUC': 'AI High AOV',
    'SdJBtU': 'Legacy VIP',
    'VrThHy': 'AM Engaged 60D',
    'UkesRj': 'AI Engaged 60 Days',
    'TRNF9C': 'AM Engaged 30D',
    'RS4wxS': 'AI Engaged 30 Days',
    'XUf7Wy': 'AM Bots (new)',
    'Wu33h2': 'AM Bots (old)',
    'R7n5YH': 'AM Unengaged (old)',
    'XBK6Hv': 'AM Unengaged (new)',
    'XDzbbr': 'AI Never Engaged',
    'V6fa8Q': 'AM Bounce',
    'S2hTN3': 'AM Bounced (in stack)',
    'RQvExN': 'AM Suppress (in stack)',
    'QPaQg2': 'AM Suppressed (in stack)',
    'UHwkSH': 'Clean #1',
    'TZS3UG': 'Clean #2',
    'VbgSNy': 'Clean #3',
    'RraB6N': 'Clean #4',
    'YaDY3x': 'PROBE LEAK',
}

for s in segs:
    sid = s['id']
    if sid not in suspects:
        continue
    print(f'=== {sid}  count={s.get("profile_count")}  "{s["name"]}" ({suspects[sid]}) ===')
    defn = s.get('definition') or {}
    cgs = defn.get('condition_groups') or []
    for gi, cg in enumerate(cgs):
        for ci, c in enumerate(cg.get('conditions', [])):
            t = c.get('type')
            if t == 'profile-metric':
                mid = c.get('metric_id')
                meas = c.get('measurement')
                mf = c.get('measurement_filter') or {}
                tf = c.get('timeframe_filter') or {}
                mfs = c.get('metric_filters') or []
                mf_str = f'{mf.get("operator")}={mf.get("value")}'
                tf_str = f'{tf.get("operator")} {tf.get("quantity","")}{tf.get("unit","")}'.strip()
                mfs_str = f' metric_filters={len(mfs)}' if mfs else ''
                print(f'  g{gi}.c{ci}: metric={mid} measure={meas} {mf_str} timeframe={tf_str}{mfs_str}')
            elif t == 'profile-property':
                prop = c.get('property', '?')
                f = c.get('filter') or {}
                print(f'  g{gi}.c{ci}: property={prop} {f.get("operator")}={f.get("value")}')
            elif t == 'profile-group-membership':
                print(f'  g{gi}.c{ci}: list_membership is_member={c.get("is_member")} groups={c.get("group_ids")}')
            elif t == 'profile-predictive-analytics':
                print(f'  g{gi}.c{ci}: predictive dim={c.get("dimension")} mfilter={c.get("measurement_filter")}')
            elif t == 'profile-marketing-consent':
                print(f'  g{gi}.c{ci}: marketing-consent {c.get("consent")} on {c.get("channel")}')
            else:
                print(f'  g{gi}.c{ci}: type={t} raw={json.dumps(c,ensure_ascii=False)[:200]}')
    print()
