"""Audit all email campaigns sent in a time window.

Ranks by revenue, flags underperformers vs. account median, and writes
findings with specific recommended actions.

Usage:
    python -m scripts.agent.audit_campaigns --days 90 --out /tmp/campaigns.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from .klaviyo_client import KlaviyoClient

REPO = Path(__file__).resolve().parents[2]
THRESHOLDS = yaml.safe_load((REPO / "config" / "thresholds.yml").read_text(encoding="utf-8"))
REGISTRY = yaml.safe_load((REPO / "registry" / "flows.yml").read_text(encoding="utf-8"))

STATS = [
    "recipients", "opens_unique", "clicks_unique", "conversions",
    "conversion_value", "bounced", "unsubscribes", "spam_complaints",
    "open_rate", "click_rate", "conversion_rate", "bounce_rate",
    "unsubscribe_rate", "spam_complaint_rate", "revenue_per_recipient",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    client = KlaviyoClient()
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat()
    print(f"Listing email campaigns since {since}…")
    campaigns = client.list_campaigns(channel="email", since_iso=since)
    # Only sent campaigns (have a send_time)
    sent = [
        c for c in campaigns
        if (c.get("attributes") or {}).get("send_time")
        and (c.get("attributes") or {}).get("status", "").lower() in {"sent", "sending"}
    ]
    print(f"  found {len(sent)} sent campaigns")

    if not sent:
        out = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "window_days": args.days,
            "campaign_count": 0,
            "findings": [],
            "campaigns": [],
        }
        _write(out, args.out)
        return 0

    ids = [c["id"] for c in sent]
    # Chunk to keep URL size sane
    chunks = [ids[i : i + 50] for i in range(0, len(ids), 50)]
    rows: list[dict] = []
    for chunk in chunks:
        rep = client.campaign_values_report(
            campaign_ids=chunk,
            statistics=STATS,
            timeframe_key=f"last_{args.days}_days",
            conversion_metric_id=REGISTRY["conversion_metric"]["id"],
        )
        results = ((rep.get("data") or {}).get("attributes") or {}).get("results") or []
        rows.extend(results)

    meta_by_id = {c["id"]: c.get("attributes") or {} for c in sent}
    campaigns_out: list[dict] = []
    for r in rows:
        cid = (r.get("groupings") or {}).get("campaign_id")
        if not cid:
            continue
        vals = r.get("statistics") or {}
        meta = meta_by_id.get(cid, {})
        campaigns_out.append({
            "id": cid,
            "name": meta.get("name", "(unnamed)"),
            "send_time": meta.get("send_time"),
            "subject": (meta.get("subject_line") or meta.get("subject") or ""),
            **{k: vals.get(k) for k in STATS},
        })

    campaigns_out.sort(key=lambda c: c.get("conversion_value") or 0, reverse=True)

    findings = _derive_findings(campaigns_out)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": args.days,
        "campaign_count": len(campaigns_out),
        "findings": findings,
        "campaigns": campaigns_out,
    }
    _write(out, args.out)
    return 0


def _derive_findings(campaigns: list[dict]) -> list[dict]:
    th = THRESHOLDS["campaigns"]
    findings: list[dict] = []
    if not campaigns:
        return findings

    # Median baselines
    opens = [c["open_rate"] for c in campaigns if c.get("open_rate") is not None]
    clicks = [c["click_rate"] for c in campaigns if c.get("click_rate") is not None]
    median_open = statistics.median(opens) if opens else 0.0
    median_click = statistics.median(clicks) if clicks else 0.0

    for c in campaigns:
        if (c.get("recipients") or 0) < th["min_recipients_for_alert"]:
            continue
        # Deliverability alerts
        if (c.get("spam_complaint_rate") or 0) * 100 > th["spam_complaint_rate_pct"]:
            findings.append({
                "severity": "critical",
                "campaign_id": c["id"],
                "name": c["name"],
                "kind": "spam_complaint",
                "value_pct": round((c["spam_complaint_rate"] or 0) * 100, 3),
                "threshold_pct": th["spam_complaint_rate_pct"],
                "action": "Investigate subject/content — complaint rate exceeds kill-switch. Pause resend cohorts.",
            })
        if (c.get("bounce_rate") or 0) * 100 > th["bounce_rate_pct"]:
            findings.append({
                "severity": "warning",
                "campaign_id": c["id"],
                "name": c["name"],
                "kind": "bounce",
                "value_pct": round((c["bounce_rate"] or 0) * 100, 3),
                "threshold_pct": th["bounce_rate_pct"],
                "action": "Clean list; run find_bouncers + apply_suppressions before next send.",
            })
        if (c.get("unsubscribe_rate") or 0) * 100 > th["unsubscribe_rate_pct"]:
            findings.append({
                "severity": "warning",
                "campaign_id": c["id"],
                "name": c["name"],
                "kind": "unsubscribe",
                "value_pct": round((c["unsubscribe_rate"] or 0) * 100, 3),
                "threshold_pct": th["unsubscribe_rate_pct"],
                "action": "Review targeting — sending to wrong segment or frequency too high.",
            })
        # Underperformance vs median
        open_gap = (median_open - (c.get("open_rate") or 0)) * 100
        if open_gap > th["open_rate_underperformance_pp"]:
            findings.append({
                "severity": "info",
                "campaign_id": c["id"],
                "name": c["name"],
                "kind": "open_underperform",
                "value_pct": round((c.get("open_rate") or 0) * 100, 2),
                "median_pct": round(median_open * 100, 2),
                "action": f"Subject '{c.get('subject', '')[:60]}' underperformed median by {open_gap:.1f}pp. Rewrite subject pattern.",
            })

    # Top winners (positive recommendations)
    top3 = sorted(campaigns, key=lambda c: c.get("conversion_value") or 0, reverse=True)[:3]
    for c in top3:
        if (c.get("conversion_value") or 0) > 0:
            findings.append({
                "severity": "info",
                "campaign_id": c["id"],
                "name": c["name"],
                "kind": "top_performer",
                "revenue": round(c.get("conversion_value") or 0, 2),
                "action": f"Winner — {c['name']}. Extract subject/content patterns; use as template.",
            })

    return findings


def _write(out: dict, path: str | None) -> None:
    text = json.dumps(out, indent=2, default=str)
    if path:
        Path(path).write_text(text, encoding="utf-8")
        print(f"Wrote {path}")
    else:
        sys.stdout.write(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
