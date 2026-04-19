"""Pull a flow performance snapshot and write it to data/flow-reports/.

Usage:
  python -m scripts.agent.pull_flow_report --timeframe last_7_days
  python -m scripts.agent.pull_flow_report --timeframe last_30_days --tag monthly
  python -m scripts.agent.pull_flow_report --timeframe last_1_days --tag daily

Output: data/flow-reports/YYYY-MM-DD-<tag>.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .klaviyo_client import KlaviyoClient

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "registry" / "flows.yml"
REPORTS_DIR = REPO_ROOT / "data" / "flow-reports"

STATISTICS = [
    "recipients",
    "opens",
    "opens_unique",
    "open_rate",
    "clicks",
    "clicks_unique",
    "click_rate",
    "click_to_open_rate",
    "bounced",
    "bounce_rate",
    "unsubscribes",
    "unsubscribe_rate",
    "spam_complaints",
    "spam_complaint_rate",
    "conversions",
    "conversion_rate",
    "conversion_value",
    "revenue_per_recipient",
    "delivered",
    "delivery_rate",
]


def load_registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def tracked_flows(registry: dict) -> list[dict]:
    out = []
    for flow in registry.get("flows", []):
        if flow.get("track_performance") is False:
            continue
        if flow.get("status") != "live":
            continue
        out.append(flow)
    return out


def pull(timeframe: str, tag: str) -> Path:
    registry = load_registry()
    conv_metric = registry["conversion_metric"]["id"]
    flows = tracked_flows(registry)
    flow_ids = [f["id"] for f in flows]

    if not flow_ids:
        raise SystemExit("No tracked flows in registry.")

    client = KlaviyoClient()
    print(f"Pulling {timeframe} for {len(flow_ids)} flows...")
    resp = client.flow_values_report(flow_ids, STATISTICS, timeframe, conv_metric)

    # Klaviyo returns rows grouped by flow_message (one row per email in a flow).
    # Aggregate to flow level: sum counts, recompute rates as weighted averages.
    by_id = {f["id"]: f for f in flows}
    results = resp.get("data", {}).get("attributes", {}).get("results", [])

    COUNT_FIELDS = {"recipients", "opens", "opens_unique", "clicks", "clicks_unique",
                    "bounced", "unsubscribes", "spam_complaints", "conversions",
                    "delivered", "conversion_value"}
    # rate = numerator / denominator (recipients, unless otherwise noted)
    RATE_NUMERATORS = {
        "open_rate": "opens_unique",
        "click_rate": "clicks_unique",
        "click_to_open_rate": "clicks_unique",  # denom = opens_unique
        "bounce_rate": "bounced",
        "unsubscribe_rate": "unsubscribes",
        "spam_complaint_rate": "spam_complaints",
        "conversion_rate": "conversions",
        "delivery_rate": "delivered",
    }

    agg: dict[str, dict] = {}
    for row in results:
        fid = row.get("groupings", {}).get("flow_id")
        if not fid:
            continue
        vals = row.get("statistics", {}) or {}
        bucket = agg.setdefault(fid, {k: 0 for k in COUNT_FIELDS})
        for k in COUNT_FIELDS:
            v = vals.get(k)
            if v is not None:
                bucket[k] = bucket.get(k, 0) + float(v)

    def safe_div(num: float, den: float) -> float:
        return (num / den) if den else 0.0

    enriched = []
    for fid, counts in agg.items():
        meta = by_id.get(fid, {})
        rec = counts.get("recipients", 0)
        opens_u = counts.get("opens_unique", 0)
        stats = {
            **counts,
            "open_rate": safe_div(opens_u, rec),
            "click_rate": safe_div(counts.get("clicks_unique", 0), rec),
            "click_to_open_rate": safe_div(counts.get("clicks_unique", 0), opens_u),
            "bounce_rate": safe_div(counts.get("bounced", 0), rec),
            "unsubscribe_rate": safe_div(counts.get("unsubscribes", 0), rec),
            "spam_complaint_rate": safe_div(counts.get("spam_complaints", 0), rec),
            "conversion_rate": safe_div(counts.get("conversions", 0), rec),
            "delivery_rate": safe_div(counts.get("delivered", 0), rec),
            "revenue_per_recipient": safe_div(counts.get("conversion_value", 0), rec),
        }
        enriched.append(
            {
                "flow_id": fid,
                "flow_name": meta.get("name"),
                "tier": meta.get("tier"),
                "protected": bool(meta.get("protected")),
                "statistics": stats,
            }
        )
    enriched.sort(key=lambda x: -(x["statistics"].get("recipients") or 0))

    snapshot = {
        "pulled_at": datetime.now(timezone.utc).isoformat(),
        "timeframe": timeframe,
        "tag": tag,
        "conversion_metric_id": conv_metric,
        "flows": enriched,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = REPORTS_DIR / f"{today}-{tag}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out.relative_to(REPO_ROOT)} ({len(enriched)} flows)")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--timeframe", required=True, help="e.g. last_1_days, last_7_days, last_30_days")
    p.add_argument("--tag", required=True, help="filename suffix: daily|weekly|monthly|baseline")
    args = p.parse_args()
    pull(args.timeframe, args.tag)


if __name__ == "__main__":
    main()
