"""Append the latest snapshot as a new row block to docs/flows-performance-log.md.

Inserts under the matching section (Weekly Snapshots / Monthly Rollups) so the
markdown stays append-only and diff-friendly.
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


def pct(v) -> str:
    if v is None:
        return "—"
    return f"{float(v) * 100:.2f}%"


def money(v) -> str:
    if v is None or float(v) == 0:
        return "—"
    return f"{float(v):.2f}"


def build_table(snapshot: dict, prior: dict | None = None) -> str:
    prior_by_id = {f["flow_id"]: f for f in (prior or {}).get("flows", [])}
    rows = [
        "| Flow | ID | Recipients | Open | Click | Conv | RPR | Δ open vs prior |",
        "|------|----|-----------:|-----:|------:|-----:|----:|-----------------|",
    ]
    for flow in snapshot["flows"]:
        s = flow["statistics"] or {}
        rec = int(s.get("recipients") or 0)
        if rec == 0:
            continue
        latest_open = (s.get("open_rate") or 0) * 100
        delta = "—"
        if flow["flow_id"] in prior_by_id:
            p = prior_by_id[flow["flow_id"]]["statistics"] or {}
            p_open = (p.get("open_rate") or 0) * 100
            if p_open > 0:
                d = latest_open - p_open
                sign = "+" if d >= 0 else ""
                delta = f"{sign}{d:.2f}pp"
        rows.append(
            f"| {flow['flow_name']} | `{flow['flow_id']}` | {rec:,} | "
            f"{pct(s.get('open_rate'))} | {pct(s.get('click_rate'))} | "
            f"{pct(s.get('conversion_rate'))} | {money(s.get('revenue_per_recipient'))} | {delta} |"
        )
    return "\n".join(rows)


def latest_two(tag: str) -> tuple[Path, Path | None]:
    snaps = sorted(REPORTS_DIR.glob(f"*-{tag}.json"))
    if not snaps:
        raise SystemExit(f"No snapshots for tag={tag}")
    return snaps[-1], (snaps[-2] if len(snaps) >= 2 else None)


def insert_under_section(markdown: str, section_heading: str, new_block: str) -> str:
    """Insert `new_block` immediately after the section heading line."""
    lines = markdown.splitlines()
    try:
        idx = next(i for i, line in enumerate(lines) if line.strip() == section_heading)
    except StopIteration:
        # Section not found — append at end
        return markdown.rstrip() + "\n\n" + section_heading + "\n\n" + new_block + "\n"
    insert_at = idx + 1
    # Skip blank line right after heading if present
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1
    return "\n".join(lines[:insert_at] + [new_block, ""] + lines[insert_at:])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tag", required=True, choices=["weekly", "monthly"])
    args = p.parse_args()

    latest_path, prior_path = latest_two(args.tag)
    with open(latest_path, encoding="utf-8") as f:
        latest = json.load(f)
    prior = None
    if prior_path:
        with open(prior_path, encoding="utf-8") as f:
            prior = json.load(f)

    pulled = datetime.fromisoformat(latest["pulled_at"].replace("Z", "+00:00"))
    date_str = pulled.strftime("%Y-%m-%d")
    table = build_table(latest, prior)

    if args.tag == "weekly":
        heading_line = "## Weekly snapshots"
        block = f"### Week of {date_str}\n\n{table}"
    else:
        heading_line = "## Monthly rollups"
        month = pulled.strftime("%Y-%m")
        block = f"### {month} (pulled {date_str})\n\n{table}"

    markdown = LOG_PATH.read_text(encoding="utf-8")
    updated = insert_under_section(markdown, heading_line, block)
    LOG_PATH.write_text(updated, encoding="utf-8")
    print(f"Appended {args.tag} block for {date_str} under {heading_line}")


if __name__ == "__main__":
    main()
