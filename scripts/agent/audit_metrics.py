"""Top-level Klaviyo metric trajectory — catches site/tracking breakage.

Pulls daily volume for core metrics (Placed Order, Started Checkout,
Viewed Product, Active on Site, Subscribed to Email Marketing) over the last
30 days and flags: (a) metric went dark, (b) >50% drop in latest 7d vs prior 7d.

Usage:
    python -m scripts.agent.audit_metrics --days 30 --out /tmp/metrics.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from .klaviyo_client import KlaviyoClient

REPO = Path(__file__).resolve().parents[2]
REGISTRY = yaml.safe_load((REPO / "registry" / "flows.yml").read_text(encoding="utf-8"))

# Names we look for — order = priority
TARGET_METRIC_NAMES = [
    "Placed Order",
    "Started Checkout",
    "Viewed Product",
    "Active on Site",
    "Subscribed to Email Marketing",
    "Unsubscribed from Email Marketing",
    "Bounced Email",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    client = KlaviyoClient()
    tz = REGISTRY["account"]["timezone"]

    print("Discovering metric IDs…")
    all_metrics = client.list_metrics()
    name_to_id = {}
    for m in all_metrics:
        n = (m.get("attributes") or {}).get("name")
        if n in TARGET_METRIC_NAMES and n not in name_to_id:
            name_to_id[n] = m["id"]

    end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=args.days)

    metric_rows: list[dict] = []
    findings: list[dict] = []
    for name in TARGET_METRIC_NAMES:
        mid = name_to_id.get(name)
        if not mid:
            continue
        try:
            agg = client.metric_aggregate(
                metric_id=mid,
                measurements=["count"],
                interval="day",
                timezone=tz,
                start_iso=start.isoformat(),
                end_iso=end.isoformat(),
            )
            data = (agg.get("data") or {}).get("attributes") or {}
            series = data.get("data") or []
            counts = []
            for pt in series:
                c = (pt.get("measurements") or {}).get("count") or [0]
                counts.append(int(c[0] if c else 0))
            total = sum(counts)
            # Split into latest-7 vs prior-7 for WoW
            latest7 = sum(counts[-7:])
            prior7 = sum(counts[-14:-7]) if len(counts) >= 14 else 0
            wow_pct = ((latest7 - prior7) / prior7 * 100) if prior7 else None
            metric_rows.append({
                "name": name,
                "id": mid,
                "total_30d": total,
                "latest_7d": latest7,
                "prior_7d": prior7,
                "wow_change_pct": round(wow_pct, 1) if wow_pct is not None else None,
            })
            # Findings
            if total == 0:
                findings.append({
                    "severity": "critical",
                    "kind": "metric_dark",
                    "metric": name,
                    "action": (
                        f"Zero '{name}' events in {args.days}d. "
                        "Check tracking: Shopify → Klaviyo integration, JS snippet on site."
                    ),
                })
            elif wow_pct is not None and wow_pct < -50 and prior7 >= 20:
                findings.append({
                    "severity": "warning",
                    "kind": "metric_sharp_drop",
                    "metric": name,
                    "wow_pct": round(wow_pct, 1),
                    "latest_7d": latest7,
                    "prior_7d": prior7,
                    "action": (
                        f"'{name}' dropped {wow_pct:.0f}% WoW. "
                        "Check: site down? Integration broken? Catalog issue?"
                    ),
                })
        except Exception as e:
            print(f"  {name} failed: {e}", file=sys.stderr)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": args.days,
        "metrics": metric_rows,
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
