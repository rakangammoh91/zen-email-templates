"""When a flow regresses on open-rate WoW, pre-assemble a rewrite brief so the
next Claude session has everything it needs in one place.

Writes: flows/<slug>/proposed-rewrites/YYYY-MM-DD.md

The file is a *prompt* — not finished copy. It includes:
- The regression metrics (latest vs prior)
- Current subject + preview for each email in the flow
- The 5 approach templates (curiosity · benefit · help · urgency · social proof)
- A pointer to the Arabic voice skill and the flow's decisions.md

Claude reads this in the next session and fills in actual Arabic candidates.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "registry" / "flows.yml"
FLOWS_DIR = REPO_ROOT / "flows"


def load_registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def slug_for(flow_id: str, registry: dict) -> str | None:
    for f in registry.get("flows", []):
        if f.get("id") == flow_id:
            return f.get("slug")
    return None


def parse_email_files(flow_dir: Path) -> list[dict]:
    """Pull subject + preview from each emails/*.md file."""
    out = []
    emails_dir = flow_dir / "emails"
    if not emails_dir.exists():
        return out
    for path in sorted(emails_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        subject = _extract_field(text, "Subject")
        preview = _extract_field(text, "Preview")
        out.append({"file": path.name, "subject": subject, "preview": preview})
    return out


def _extract_field(text: str, field: str) -> str | None:
    # Matches **Field:** `value` or - **Field:** `value`
    m = re.search(rf"\*\*{field}:\*\*\s*`([^`]+)`", text)
    return m.group(1) if m else None


APPROACH_TEMPLATES = [
    ("Curiosity · mirrors body hero", "Look at the hero headline of the email; rewrite it as a question the reader hasn't had answered."),
    ("Direct benefit · specific", "Name the product outcome in numerals (12 colors, 10%, 3 minutes)."),
    ("Personal help-offer", "First-person Siham voice — `خليني أساعدكِ` / `أختارلكِ`."),
    ("Urgency · time-bound", "Deadline today/tonight/tomorrow — only if there's a real offer behind it."),
    ("Social proof · curiosity", "Named customer + outcome — `نورة طلبت X · طلع ١٠٠٪`."),
]


def write_brief(flow: dict, finding: dict, snapshot_name: str) -> Path | None:
    slug = flow.get("slug")
    if not slug:
        return None
    flow_dir = FLOWS_DIR / slug
    if not flow_dir.exists():
        # Flow not yet scaffolded — skip
        return None

    emails = parse_email_files(flow_dir)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = flow_dir / "proposed-rewrites"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date}.md"

    lines = [
        f"# Rewrite brief · {flow['name']} · {date}",
        "",
        f"**Flow ID:** `{flow['id']}` · **Slug:** `{slug}`",
        f"**Trigger:** {finding['metric']}",
        f"**Snapshot:** `{snapshot_name}`",
        "",
        "## Regression",
        "",
    ]
    for k in ("value_pp", "threshold_pp", "latest_pct", "prior_pct",
              "value_pct", "threshold_pct", "latest_sar", "prior_sar"):
        if k in finding:
            lines.append(f"- `{k}`: {finding[k]}")
    lines += [
        "",
        "## Current subjects",
        "",
        "| Email | Subject | Preview |",
        "|-------|---------|---------|",
    ]
    if emails:
        for e in emails:
            lines.append(f"| `{e['file']}` | {e['subject'] or '—'} | {e['preview'] or '—'} |")
    else:
        lines.append("| _no email files found_ | | |")

    lines += [
        "",
        "## Rewrite approaches (pick one or more per email)",
        "",
    ]
    for i, (name, hint) in enumerate(APPROACH_TEMPLATES, 1):
        lines.append(f"### {i}. {name}")
        lines.append(f"_{hint}_")
        lines.append("")
        lines.append("- [ ] Candidate: ")
        lines.append("")

    lines += [
        "## Rules (apply before shipping)",
        "",
        "- Run through `skills/zen-hair-arabic-voice/SKILL.md` checklist",
        "- Verify kasra on every 2nd-person feminine form",
        "- Middle-dot `·` for separators",
        "- Subject must mirror or set up the body hero",
        "- Arabic-Indic numerals in Arabic context",
        "",
        "## Decision log",
        "",
        f"Once a candidate wins, add a dated entry to [../decisions.md](../decisions.md) and update the email file.",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--anomalies", required=True)
    args = p.parse_args()

    with open(args.anomalies, encoding="utf-8") as f:
        result = json.load(f)

    registry = load_registry()
    flows_by_id = {f["id"]: f for f in registry.get("flows", [])}

    snapshot = result.get("latest_snapshot", "unknown")
    regression_metrics = {"open_rate_wow_drop", "rpr_wow_drop"}

    written = 0
    for finding in result.get("findings", []):
        if finding["metric"] not in regression_metrics:
            continue
        flow = flows_by_id.get(finding["flow_id"])
        if not flow:
            continue
        path = write_brief(flow, finding, snapshot)
        if path:
            print(f"  wrote: {path.relative_to(REPO_ROOT)}")
            written += 1

    print(f"Wrote {written} rewrite brief(s).")


if __name__ == "__main__":
    main()
