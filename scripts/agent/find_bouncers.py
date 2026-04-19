"""Fetch Bounced Email events from the last N days, aggregate by profile,
write a CSV of repeat bouncers (candidates for suppression).

Output: data/suppression-candidates/YYYY-MM-DD.csv
Columns: email, profile_id, bounce_count, first_bounce, last_bounce, flows_affected

A profile appears only if it bounced >= MIN_BOUNCES times in the window.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import urllib.parse
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .klaviyo_client import KlaviyoClient

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "data" / "suppression-candidates"

BOUNCED_METRIC_NAMES = {"Bounced Email"}


def find_bounced_metric_id(client: KlaviyoClient) -> str:
    url = "/metrics/"
    while url:
        data = client.get(url)
        for m in data.get("data", []):
            name = m.get("attributes", {}).get("name")
            if name in BOUNCED_METRIC_NAMES:
                return m["id"]
        url = data.get("links", {}).get("next")
        if url and url.startswith("http"):
            url = url.replace("https://a.klaviyo.com/api", "")
        time.sleep(0.3)
    raise RuntimeError("No 'Bounced Email' metric found in account")


def fetch_bounce_events(client: KlaviyoClient, metric_id: str, days: int):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    params = {
        "filter": f'and(equals(metric_id,"{metric_id}"),greater-than(datetime,{since}))',
        "include": "profile",
        "fields[profile]": "email",
        "page[size]": 200,
    }
    url = f"/events/?{urllib.parse.urlencode(params)}"
    events_count = 0
    while url:
        data = client.get(url)
        # Build profile-id → email lookup from included
        email_by_profile = {}
        for inc in data.get("included", []):
            if inc.get("type") == "profile":
                email_by_profile[inc["id"]] = inc.get("attributes", {}).get("email")
        for ev in data.get("data", []):
            prof = ev.get("relationships", {}).get("profile", {}).get("data", {})
            pid = prof.get("id")
            if not pid:
                continue
            attrs = ev.get("attributes", {})
            yield {
                "profile_id": pid,
                "email": email_by_profile.get(pid),
                "datetime": attrs.get("datetime"),
                "event_properties": attrs.get("event_properties") or {},
            }
            events_count += 1
        nxt = data.get("links", {}).get("next")
        if nxt:
            # Klaviyo returns absolute URL — strip base for our client
            url = nxt.replace("https://a.klaviyo.com/api", "")
        else:
            url = None
        time.sleep(0.3)
    print(f"  fetched {events_count} bounce events", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--min-bounces", type=int, default=2)
    args = p.parse_args()

    client = KlaviyoClient()
    print(f"Discovering 'Bounced Email' metric ID...")
    metric_id = find_bounced_metric_id(client)
    print(f"  metric_id = {metric_id}")

    print(f"Pulling bounce events from last {args.days} days...")
    by_profile: dict[str, dict] = defaultdict(lambda: {
        "bounce_count": 0,
        "first_bounce": None,
        "last_bounce": None,
        "email": None,
        "flows": set(),
    })
    for ev in fetch_bounce_events(client, metric_id, args.days):
        pid = ev["profile_id"]
        rec = by_profile[pid]
        rec["bounce_count"] += 1
        rec["email"] = ev["email"]
        dt = ev["datetime"]
        if dt:
            if rec["first_bounce"] is None or dt < rec["first_bounce"]:
                rec["first_bounce"] = dt
            if rec["last_bounce"] is None or dt > rec["last_bounce"]:
                rec["last_bounce"] = dt
        props = ev["event_properties"] or {}
        flow = props.get("Flow") or props.get("$flow") or props.get("flow_name")
        if flow:
            rec["flows"].add(str(flow))

    candidates = [
        (pid, rec) for pid, rec in by_profile.items()
        if rec["bounce_count"] >= args.min_bounces and rec["email"]
    ]
    candidates.sort(key=lambda kv: -kv[1]["bounce_count"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = OUT_DIR / f"{today}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["email", "profile_id", "bounce_count", "first_bounce", "last_bounce", "flows_affected"])
        for pid, rec in candidates:
            w.writerow([
                rec["email"], pid, rec["bounce_count"],
                rec["first_bounce"] or "", rec["last_bounce"] or "",
                "; ".join(sorted(rec["flows"])),
            ])
    print(f"Wrote {len(candidates)} candidates to {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
