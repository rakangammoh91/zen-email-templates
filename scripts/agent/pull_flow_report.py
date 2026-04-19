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

    # Normalize: attach flow names so the snapshot is self-describing
    by_id = {f["id"]: f for f in flows}
    results = resp.get("data", {}).get("attributes", {}).get("results", [])
    enriched = []
    for row in results:
        fid = row.get("groupings", {}).get("flow_id")
        meta = by_id.get(fid, {})
        values = row.get("statistics", {})
        enriched.append(
            {
                "flow_id": fid,
                "flow_name": meta.get("name"),
                "tier": meta.get("tier"),
                "protected": bool(meta.get("protected")),
                "statistics": values,
            }
        )

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
