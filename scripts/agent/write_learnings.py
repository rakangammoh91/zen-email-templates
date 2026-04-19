"""After a weekly snapshot, compute trends across the last N weekly files
and append a dated bullet list to the Learnings section of the perf log.

Template-based, deterministic — no LLM. Flags:
- Biggest open-rate mover (up or down)
- Biggest RPR mover
- Closest-to-threshold flow (early warning)
- Flow trending down 3 weeks in a row
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "data" / "flow-reports"
LOG_PATH = REPO_ROOT / "docs" / "flows-performance-log.md"
LEARNINGS_HEADING = "## Learnings · running notes"


def load_weekly_history(n: int = 4) -> list[dict]:
    files = sorted(REPORTS_DIR.glob("*-weekly.json"))
    out = []
    for p in files[-n:]:
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def flows_by_id(snapshot: dict) -> dict[str, dict]:
    return {f["flow_id"]: f for f in snapshot.get("flows", [])}


def pct(v) -> float:
    return 0.0 if v is None else float(v) * 100.0


def compute_insights(history: list[dict]) -> list[str]:
    if len(history) < 2:
        return ["Not enough history yet — first insight lands after week 2."]

    latest = history[-1]
    prior = history[-2]
    latest_by = flows_by_id(latest)
    prior_by = flows_by_id(prior)

    # Biggest open-rate mover
    open_moves = []
    rpr_moves = []
    for fid, f in latest_by.items():
        if fid not in prior_by:
            continue
        l_open = pct(f["statistics"].get("open_rate"))
        p_open = pct(prior_by[fid]["statistics"].get("open_rate"))
        if (f["statistics"].get("recipients") or 0) >= 50:
            open_moves.append((fid, f["flow_name"], l_open - p_open, l_open, p_open))
        l_rpr = float(f["statistics"].get("revenue_per_recipient") or 0)
        p_rpr = float(prior_by[fid]["statistics"].get("revenue_per_recipient") or 0)
        if p_rpr > 0:
            rpr_moves.append((fid, f["flow_name"], l_rpr - p_rpr, l_rpr, p_rpr))

    insights: list[str] = []

    if open_moves:
        up = max(open_moves, key=lambda x: x[2])
        down = min(open_moves, key=lambda x: x[2])
        if up[2] > 0.5:
            insights.append(f"Biggest open-rate gain: **{up[1]}** +{up[2]:.2f}pp ({up[4]:.2f}% → {up[3]:.2f}%).")
        if down[2] < -0.5:
            insights.append(f"Biggest open-rate drop: **{down[1]}** {down[2]:.2f}pp ({down[4]:.2f}% → {down[3]:.2f}%).")

    if rpr_moves:
        rpr_up = max(rpr_moves, key=lambda x: x[2])
        if rpr_up[2] > 0.1:
            insights.append(f"Biggest RPR gain: **{rpr_up[1]}** +{rpr_up[2]:.2f} SAR ({rpr_up[4]:.2f} → {rpr_up[3]:.2f}).")

    # Trending-down 3 weeks in a row
    if len(history) >= 3:
        for fid, f in latest_by.items():
            if (f["statistics"].get("recipients") or 0) < 50:
                continue
            series = []
            for snap in history[-3:]:
                byid = flows_by_id(snap)
                if fid in byid:
                    series.append(pct(byid[fid]["statistics"].get("open_rate")))
            if len(series) == 3 and series[0] > series[1] > series[2]:
                insights.append(
                    f"3-week downtrend on open rate: **{f['flow_name']}** "
                    f"({series[0]:.1f}% → {series[1]:.1f}% → {series[2]:.1f}%) — investigate."
                )

    # Closest-to-threshold bounce rate (early warning)
    bounce_flags = []
    for fid, f in latest_by.items():
        if (f["statistics"].get("recipients") or 0) < 50:
            continue
        bounce = pct(f["statistics"].get("bounce_rate"))
        protected = bool(f.get("protected"))
        thr = 1.5 if protected else 3.0
        if bounce > 0 and bounce / thr > 0.6:  # within 60% of threshold
            bounce_flags.append((f["flow_name"], bounce, thr))
    if bounce_flags:
        bounce_flags.sort(key=lambda x: -x[1])
        name, b, thr = bounce_flags[0]
        insights.append(f"Watch: **{name}** bounce {b:.2f}% (threshold {thr:.1f}%) — approaching limit.")

    if not insights:
        insights.append("No notable movement this week — all tracked flows within normal variance.")

    return insights


def append_to_log(insights: list[str]) -> None:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    block_lines = [f"- `{date}` (auto-digest)"]
    for ins in insights:
        block_lines.append(f"  - {ins}")
    block = "\n".join(block_lines)

    text = LOG_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        idx = next(i for i, line in enumerate(lines) if line.strip() == LEARNINGS_HEADING)
    except StopIteration:
        # Append at end if section missing
        LOG_PATH.write_text(text.rstrip() + f"\n\n{LEARNINGS_HEADING}\n\n{block}\n", encoding="utf-8")
        return

    # Find first bullet under the heading and insert above it (newest on top)
    insert_at = idx + 1
    while insert_at < len(lines) and not lines[insert_at].startswith("- "):
        insert_at += 1
    new_lines = lines[:insert_at] + [block] + lines[insert_at:]
    LOG_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--history-weeks", type=int, default=4)
    args = p.parse_args()

    history = load_weekly_history(args.history_weeks)
    if not history:
        print("No weekly snapshots — nothing to learn from.")
        return

    insights = compute_insights(history)
    append_to_log(insights)
    print(f"Appended {len(insights)} insight(s) to Learnings.")
    for i in insights:
        print(f"  - {i}")


if __name__ == "__main__":
    main()
