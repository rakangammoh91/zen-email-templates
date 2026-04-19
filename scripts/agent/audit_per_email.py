"""Per-email breakdown inside each live flow — identifies the weak link.

Pulls flow_values_report grouped by flow_message_id (no aggregation), then
for each flow surfaces the weakest email by open rate and by unsub rate.

Usage:
    python -m scripts.agent.audit_per_email --days 30 --out /tmp/per_email.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .klaviyo_client import KlaviyoClient

REPO = Path(__file__).resolve().parents[2]
REGISTRY = yaml.safe_load((REPO / "registry" / "flows.yml").read_text(encoding="utf-8"))

STATS = [
    "recipients", "opens_unique", "clicks_unique", "conversions",
    "conversion_value", "bounced", "unsubscribes", "spam_complaints",
    "open_rate", "click_rate", "conversion_rate", "bounce_rate",
    "unsubscribe_rate", "spam_complaint_rate", "revenue_per_recipient",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    client = KlaviyoClient()
    flows = [
        f for f in REGISTRY["flows"]
        if f.get("status") == "live" and f.get("track_performance") is not False
    ]
    ids = [f["id"] for f in flows]
    timeframe_key = f"last_{args.days}_days" if args.days in (1, 7, 30, 90, 365) else "last_30_days"

    rep = client.flow_values_report(
        flow_ids=ids,
        statistics=STATS,
        timeframe_key=timeframe_key,
        conversion_metric_id=REGISTRY["conversion_metric"]["id"],
    )
    results = ((rep.get("data") or {}).get("attributes") or {}).get("results") or []

    by_flow: dict[str, list[dict]] = {}
    for r in results:
        g = r.get("groupings") or {}
        fid = g.get("flow_id")
        mid = g.get("flow_message_id") or g.get("send_channel") or "unknown"
        vals = r.get("statistics") or {}
        by_flow.setdefault(fid, []).append({
            "flow_message_id": mid,
            **{k: vals.get(k) for k in STATS},
        })

    findings: list[dict] = []
    for flow in flows:
        fid = flow["id"]
        msgs = by_flow.get(fid) or []
        # Only flag if ≥2 messages and the flow has real volume
        sendy = [m for m in msgs if (m.get("recipients") or 0) >= 50]
        if len(sendy) < 2:
            continue
        weakest_open = min(sendy, key=lambda m: m.get("open_rate") or 0)
        strongest_open = max(sendy, key=lambda m: m.get("open_rate") or 0)
        gap_pp = ((strongest_open.get("open_rate") or 0) - (weakest_open.get("open_rate") or 0)) * 100
        if gap_pp >= 10:
            findings.append({
                "severity": "info",
                "kind": "weak_email_in_flow",
                "flow_id": fid,
                "flow_name": flow.get("name"),
                "weak_msg_id": weakest_open["flow_message_id"],
                "weak_open_pct": round((weakest_open.get("open_rate") or 0) * 100, 2),
                "strong_open_pct": round((strongest_open.get("open_rate") or 0) * 100, 2),
                "gap_pp": round(gap_pp, 1),
                "action": (
                    f"Message {weakest_open['flow_message_id']} in {flow.get('name')} "
                    f"opens {gap_pp:.1f}pp below strongest. Candidate for subject rewrite."
                ),
            })
        # Highest unsub
        worst_unsub = max(sendy, key=lambda m: m.get("unsubscribe_rate") or 0)
        if (worst_unsub.get("unsubscribe_rate") or 0) * 100 > 0.5:
            findings.append({
                "severity": "warning",
                "kind": "high_unsub_email",
                "flow_id": fid,
                "flow_name": flow.get("name"),
                "msg_id": worst_unsub["flow_message_id"],
                "unsub_pct": round((worst_unsub.get("unsubscribe_rate") or 0) * 100, 3),
                "action": "Review content or cadence — this email is fatiguing recipients.",
            })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": args.days,
        "messages_by_flow": by_flow,
        "findings": findings,
    }
    text = json.dumps(out, indent=2, default=str)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
