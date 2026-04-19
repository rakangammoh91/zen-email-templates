"""Audit segments + lists — profile counts, engagement ratios, net reach.

Writes JSON snapshot. If prior snapshots exist, computes net-reach trajectory.

Usage:
    python -m scripts.agent.audit_segments --out /tmp/segments.json
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
SNAP_DIR = REPO / "data" / "segment-snapshots"
THRESHOLDS = yaml.safe_load((REPO / "config" / "thresholds.yml").read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    client = KlaviyoClient()

    print("Listing segments…")
    segments = client.list_segments()
    print(f"  {len(segments)} segments")
    print("Listing lists…")
    lists = client.list_lists()
    print(f"  {len(lists)} lists")

    seg_rows = [
        {
            "id": s["id"],
            "name": (s.get("attributes") or {}).get("name"),
            "profile_count": (s.get("attributes") or {}).get("profile_count"),
            "is_active": (s.get("attributes") or {}).get("is_active"),
            "created": (s.get("attributes") or {}).get("created"),
        }
        for s in segments
    ]
    # Enrich the most interesting segments with profile_count (per-segment API call)
    interesting = [
        s for s in seg_rows
        if any(kw in (s.get("name") or "").lower() for kw in
               ["engaged", "active", "unengaged", "never", "suppressed", "vip", "buyers"])
    ]
    for s in interesting:
        s["profile_count"] = client.get_segment_profile_count(s["id"])
    list_rows = [
        {
            "id": l["id"],
            "name": (l.get("attributes") or {}).get("name"),
            "profile_count": (l.get("attributes") or {}).get("profile_count"),
            "opt_in_process": (l.get("attributes") or {}).get("opt_in_process"),
        }
        for l in lists
    ]

    # Try to identify engaged / unengaged / suppressed by name heuristics
    def _find(rows: list[dict], *keywords: str) -> dict | None:
        kws = [k.lower() for k in keywords]
        for r in rows:
            name = (r.get("name") or "").lower()
            if all(k in name for k in kws):
                return r
        return None

    engaged_30 = _find(seg_rows, "engaged", "30") or _find(seg_rows, "active", "30")
    engaged_90 = _find(seg_rows, "engaged", "90") or _find(seg_rows, "active", "90")
    unengaged = _find(seg_rows, "unengaged") or _find(seg_rows, "never", "opened")
    suppressed = _find(seg_rows, "suppressed")

    # Master list: the largest non-VIP list (VIP/offer/test lists skew detection)
    def _is_master_candidate(r: dict) -> bool:
        n = (r.get("name") or "").lower()
        return not any(s in n for s in ("vip", "test", "offer", "internal", "admin"))
    candidates = [r for r in list_rows if _is_master_candidate(r) and (r.get("profile_count") or 0) > 0]
    master_list = max(candidates, key=lambda r: r.get("profile_count") or 0) if candidates \
        else (max(list_rows, key=lambda r: r.get("profile_count") or 0) if list_rows else None)
    total_profiles = master_list.get("profile_count") if master_list else None

    findings: list[dict] = []

    if unengaged and total_profiles:
        unengaged_count = unengaged.get("profile_count") or 0
        unengaged_pct = 100.0 * unengaged_count / total_profiles if total_profiles else 0
        if unengaged_pct > THRESHOLDS["list_health"]["unengaged_pct_sunset_trigger"]:
            findings.append({
                "severity": "warning",
                "kind": "unengaged_large",
                "value_pct": round(unengaged_pct, 1),
                "threshold_pct": THRESHOLDS["list_health"]["unengaged_pct_sunset_trigger"],
                "action": (
                    f"{unengaged_count:,} unengaged profiles = {unengaged_pct:.1f}% of list. "
                    "Build a sunset flow → final re-engagement email → suppress non-responders."
                ),
            })

    # Trajectory vs prior snapshot
    prior = _load_prior()
    if prior and master_list:
        prior_total = (prior.get("master_list") or {}).get("profile_count")
        if prior_total:
            delta = total_profiles - prior_total
            findings.append({
                "severity": "info",
                "kind": "reach_delta",
                "delta": delta,
                "prior": prior_total,
                "current": total_profiles,
                "action": (
                    "Acquisition gap — investigate signup sources."
                    if delta < 0
                    else "Healthy growth — keep acquisition channels steady."
                ),
            })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "segments": seg_rows,
        "lists": list_rows,
        "master_list": master_list,
        "engaged_30d": engaged_30,
        "engaged_90d": engaged_90,
        "unengaged": unengaged,
        "suppressed": suppressed,
        "findings": findings,
    }
    # Always write a dated snapshot for trend tracking
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    snap_name = datetime.now(timezone.utc).strftime("%Y-%m-%d") + ".json"
    (SNAP_DIR / snap_name).write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    _write(out, args.out)
    return 0


def _load_prior() -> dict | None:
    if not SNAP_DIR.exists():
        return None
    snaps = sorted(SNAP_DIR.glob("*.json"))
    if len(snaps) < 1:
        return None
    try:
        return json.loads(snaps[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def _write(out: dict, path: str | None) -> None:
    text = json.dumps(out, indent=2, default=str)
    if path:
        Path(path).write_text(text, encoding="utf-8")
        print(f"Wrote {path}")
    else:
        sys.stdout.write(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
