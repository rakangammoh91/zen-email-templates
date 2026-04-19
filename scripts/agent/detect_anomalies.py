"""Compare the latest snapshot against the prior one of the same tag.

Exit codes:
  0 = all green
  1 = warnings only (bounce/unsub/open-rate regression)
  2 = CRITICAL (spam complaint → kill-switch candidate)

Prints human-readable findings on stdout + a machine-readable JSON on --json-out.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "data" / "flow-reports"
THRESHOLDS_PATH = REPO_ROOT / "config" / "thresholds.yml"


def load_thresholds() -> dict:
    with open(THRESHOLDS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def snapshots_by_tag(tag: str) -> list[Path]:
    return sorted(REPORTS_DIR.glob(f"*-{tag}.json"))


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pct(v) -> float:
    """Klaviyo returns rates as fractions (0.2978) — convert to percent."""
    if v is None:
        return 0.0
    return float(v) * 100.0


def evaluate(tag: str, verbose: bool = True) -> dict:
    thresh = load_thresholds()
    a = thresh["alerts"]
    min_rec = thresh.get("min_recipients_for_alert", 50)
    prot_mult = a.get("protected_multiplier", 0.5)

    snaps = snapshots_by_tag(tag)
    if not snaps:
        return {"status": "no_data", "findings": []}

    latest = load(snaps[-1])
    prior = load(snaps[-2]) if len(snaps) >= 2 else None
    prior_by_id = {f["flow_id"]: f for f in prior["flows"]} if prior else {}

    findings: list[dict] = []
    worst_severity = 0  # 0 ok, 1 warn, 2 crit

    for flow in latest["flows"]:
        fid = flow["flow_id"]
        name = flow["flow_name"]
        stats = flow["statistics"] or {}
        protected = flow.get("protected", False)
        mult = prot_mult if protected else 1.0

        recipients = int(stats.get("recipients") or 0)
        if recipients < min_rec:
            continue  # sample too small

        spam = pct(stats.get("spam_complaint_rate"))
        bounce = pct(stats.get("bounce_rate"))
        unsub = pct(stats.get("unsubscribe_rate"))
        open_rate = pct(stats.get("open_rate"))
        rpr = float(stats.get("revenue_per_recipient") or 0)

        # CRITICAL: spam
        if spam > a["spam_complaint_rate_pct"] * mult:
            findings.append({
                "severity": "critical",
                "flow_id": fid, "flow_name": name,
                "metric": "spam_complaint_rate",
                "value_pct": round(spam, 3),
                "threshold_pct": a["spam_complaint_rate_pct"] * mult,
                "action": "PAUSE FLOW",
            })
            worst_severity = max(worst_severity, 2)

        # WARN: bounce
        if bounce > a["bounce_rate_pct"] * mult:
            findings.append({
                "severity": "warning", "flow_id": fid, "flow_name": name,
                "metric": "bounce_rate",
                "value_pct": round(bounce, 2),
                "threshold_pct": a["bounce_rate_pct"] * mult,
            })
            worst_severity = max(worst_severity, 1)

        # WARN: unsubscribe
        if unsub > a["unsubscribe_rate_pct"] * mult:
            findings.append({
                "severity": "warning", "flow_id": fid, "flow_name": name,
                "metric": "unsubscribe_rate",
                "value_pct": round(unsub, 2),
                "threshold_pct": a["unsubscribe_rate_pct"] * mult,
            })
            worst_severity = max(worst_severity, 1)

        # WoW regressions (only if we have a prior snapshot)
        if prior_by_id.get(fid):
            p_stats = prior_by_id[fid]["statistics"] or {}
            p_open = pct(p_stats.get("open_rate"))
            p_rpr = float(p_stats.get("revenue_per_recipient") or 0)

            open_drop_pp = p_open - open_rate
            if open_drop_pp > a["open_rate_wow_drop_pp"] * mult:
                findings.append({
                    "severity": "warning", "flow_id": fid, "flow_name": name,
                    "metric": "open_rate_wow_drop",
                    "value_pp": round(open_drop_pp, 2),
                    "threshold_pp": a["open_rate_wow_drop_pp"] * mult,
                    "latest_pct": round(open_rate, 2),
                    "prior_pct": round(p_open, 2),
                })
                worst_severity = max(worst_severity, 1)

            if p_rpr > 0:
                rpr_drop = (p_rpr - rpr) / p_rpr * 100.0
                if rpr_drop > a["rpr_wow_drop_pct"] * mult:
                    findings.append({
                        "severity": "warning", "flow_id": fid, "flow_name": name,
                        "metric": "rpr_wow_drop",
                        "value_pct": round(rpr_drop, 2),
                        "threshold_pct": a["rpr_wow_drop_pct"] * mult,
                        "latest_sar": round(rpr, 2),
                        "prior_sar": round(p_rpr, 2),
                    })
                    worst_severity = max(worst_severity, 1)

    status = ["ok", "warning", "critical"][worst_severity]
    result = {
        "status": status,
        "tag": tag,
        "latest_snapshot": snaps[-1].name,
        "prior_snapshot": snaps[-2].name if len(snaps) >= 2 else None,
        "findings": findings,
    }

    if verbose:
        if findings:
            for f in findings:
                print(f"  [{f['severity'].upper()}] {f['flow_name']} · {f['metric']} · {f}")
        else:
            print(f"  all green ({tag})")

    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tag", required=True)
    p.add_argument("--json-out", help="write JSON result to this path")
    args = p.parse_args()

    result = evaluate(args.tag)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    if result["status"] == "critical":
        sys.exit(2)
    if result["status"] == "warning":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
