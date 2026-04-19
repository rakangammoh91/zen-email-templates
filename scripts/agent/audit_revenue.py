"""Revenue attribution — flows vs. campaigns vs. other, and RPAS.

Pulls the most recent weekly + monthly snapshots to sum flow + campaign revenue,
then computes share vs. total Placed Order revenue from metric-aggregates.

Usage:
    python -m scripts.agent.audit_revenue --days 30 --out /tmp/revenue.json
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
THRESHOLDS = yaml.safe_load((REPO / "config" / "thresholds.yml").read_text(encoding="utf-8"))
REGISTRY = yaml.safe_load((REPO / "registry" / "flows.yml").read_text(encoding="utf-8"))


def _latest_snapshot(tag: str) -> dict | None:
    d = REPO / "data" / "flow-reports"
    if not d.exists():
        return None
    files = sorted(d.glob(f"*-{tag}.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    client = KlaviyoClient()
    tz = REGISTRY["account"]["timezone"]
    metric_id = THRESHOLDS["revenue"]["conversion_metric_id"]
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=args.days)

    # Total store revenue (Placed Order) via metric aggregate
    total_rev = 0.0
    order_count = 0
    try:
        agg = client.metric_aggregate(
            metric_id=metric_id,
            measurements=["sum_value", "count"],
            interval="day",
            timezone=tz,
            start_iso=start.strftime("%Y-%m-%dT00:00:00%z") or start.isoformat(),
            end_iso=end.strftime("%Y-%m-%dT00:00:00%z") or end.isoformat(),
        )
        data = (agg.get("data") or {}).get("attributes") or {}
        for m in data.get("data") or []:
            measurements = m.get("measurements") or {}
            for v in measurements.get("sum_value") or []:
                total_rev += float(v or 0)
            for v in measurements.get("count") or []:
                order_count += int(v or 0)
    except Exception as e:
        print(f"  metric_aggregate failed: {e}", file=sys.stderr)

    # Flow-attributed revenue — prefer the freshest 30d-ish snapshot
    snap = None
    for tag in ("audit", "monthly", "weekly"):
        snap = _latest_snapshot(tag)
        if snap:
            break
    flow_rev = 0.0
    flow_breakdown: list[dict] = []
    if snap:
        for row in snap.get("flows") or []:
            stats = row.get("statistics") or row
            rev = stats.get("conversion_value") or 0
            flow_rev += rev
            flow_breakdown.append({
                "flow_id": row.get("flow_id"),
                "name": row.get("flow_name") or row.get("name"),
                "revenue": round(rev, 2),
                "recipients": stats.get("recipients"),
            })
    flow_breakdown.sort(key=lambda r: r["revenue"], reverse=True)

    # RPAS — denominator: active subscriber count from latest segment snapshot
    seg_dir = REPO / "data" / "segment-snapshots"
    active_subs = None
    if seg_dir.exists():
        snaps = sorted(seg_dir.glob("*.json"))
        if snaps:
            try:
                ss = json.loads(snaps[-1].read_text(encoding="utf-8"))
                eng = ss.get("engaged_90d") or ss.get("engaged_30d") or ss.get("master_list")
                active_subs = (eng or {}).get("profile_count")
            except Exception:
                pass

    flow_share_pct = (flow_rev / total_rev * 100) if total_rev else 0
    other_rev = max(total_rev - flow_rev, 0)
    rpas = (total_rev / active_subs) if active_subs else None

    findings: list[dict] = []
    min_share = THRESHOLDS["revenue"]["min_flow_revenue_share_pct"]
    if total_rev > 0 and flow_share_pct < min_share:
        findings.append({
            "severity": "warning",
            "kind": "low_flow_share",
            "value_pct": round(flow_share_pct, 1),
            "threshold_pct": min_share,
            "action": (
                f"Flows only drive {flow_share_pct:.1f}% of revenue — mostly non-email or campaigns. "
                "Investment priority: finish [RG] flow swaps to lift automation-driven revenue."
            ),
        })

    if rpas is not None:
        target = THRESHOLDS["revenue"]["rpas_monthly_target_sar"]
        if rpas < target:
            findings.append({
                "severity": "info",
                "kind": "rpas_below_target",
                "value_sar": round(rpas, 2),
                "target_sar": target,
                "action": "Raise RPAS via: (a) finish rebuilt flows, (b) resend winners to non-openers, (c) tighten sunset flow.",
            })
        else:
            findings.append({
                "severity": "info",
                "kind": "rpas_healthy",
                "value_sar": round(rpas, 2),
                "target_sar": target,
                "action": "On target — hold the line and scale acquisition.",
            })

    # Top 3 flow revenue drivers
    for r in flow_breakdown[:3]:
        if r["revenue"] > 0:
            findings.append({
                "severity": "info",
                "kind": "top_revenue_flow",
                "flow_id": r["flow_id"],
                "name": r["name"],
                "revenue": r["revenue"],
                "action": f"Protect {r['name']} — {r['revenue']:.0f} SAR over {args.days}d. Stricter alert tolerance.",
            })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": args.days,
        "total_revenue_sar": round(total_rev, 2),
        "total_orders": order_count,
        "flow_revenue_sar": round(flow_rev, 2),
        "flow_share_pct": round(flow_share_pct, 2),
        "other_revenue_sar": round(other_rev, 2),
        "active_subscribers": active_subs,
        "rpas_sar": round(rpas, 3) if rpas is not None else None,
        "top_flows": flow_breakdown[:10],
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
