"""Create a GitHub issue per alert surfaced by detect_anomalies.

Runs inside GitHub Actions: GITHUB_TOKEN + GITHUB_REPOSITORY are auto-provided.
For local testing, set GH_TOKEN + GH_REPO.

Deduplication: if an open issue with the same title already exists, skip
(avoid spamming when the same regression persists across multiple runs).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def gh_api(method: str, path: str, body: dict | None = None) -> dict | list:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY") or os.getenv("GH_REPO")
    if not token or not repo:
        raise RuntimeError("GITHUB_TOKEN + GITHUB_REPOSITORY required")
    url = f"https://api.github.com/repos/{repo}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "zen-hair-agent",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def existing_open_titles(label: str) -> set[str]:
    q = urllib.parse.urlencode({"state": "open", "labels": label, "per_page": 100})
    issues = gh_api("GET", f"/issues?{q}")
    return {i["title"] for i in issues if isinstance(i, dict)}


def issue_title(finding: dict) -> str:
    sev_icon = {"critical": "🚨", "warning": "⚠️"}[finding["severity"]]
    return f"{sev_icon} {finding['flow_name']} · {finding['metric'].replace('_', ' ')}"


def issue_body(finding: dict, snapshot_name: str) -> str:
    lines = [
        f"**Flow:** `{finding['flow_id']}` — {finding['flow_name']}",
        f"**Metric:** `{finding['metric']}`",
        f"**Severity:** {finding['severity']}",
        f"**Snapshot:** `{snapshot_name}`",
        "",
        "### Values",
    ]
    for k in ("value_pct", "value_pp", "threshold_pct", "threshold_pp",
              "latest_pct", "prior_pct", "latest_sar", "prior_sar"):
        if k in finding:
            lines.append(f"- `{k}`: {finding[k]}")
    if finding.get("action"):
        lines.append("")
        lines.append(f"### ⚠️ ACTION REQUIRED\n\n**{finding['action']}**")
    lines.extend([
        "",
        "### Next steps",
        "",
        "1. Open a Claude session: `/continue` and reference this issue",
        f"2. Inspect the raw snapshot: `data/flow-reports/{snapshot_name}`",
        "3. Decide and commit the fix — log rationale in the flow's `decisions.md`",
        "4. Close this issue with the commit",
    ])
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--anomalies", required=True)
    args = p.parse_args()

    with open(args.anomalies, encoding="utf-8") as f:
        result = json.load(f)

    findings = result.get("findings", [])
    if not findings:
        print("No findings — nothing to open.")
        return

    label = "flow-alert"
    try:
        existing = existing_open_titles(label)
    except Exception as e:
        print(f"Could not list existing issues ({e}) — proceeding without dedup.")
        existing = set()

    snapshot = result.get("latest_snapshot", "unknown")
    opened = 0
    for f in findings:
        title = issue_title(f)
        if title in existing:
            print(f"  skip (already open): {title}")
            continue
        sev_label = {"critical": "alert-critical", "warning": "alert-warning"}[f["severity"]]
        body = issue_body(f, snapshot)
        try:
            gh_api("POST", "/issues", {
                "title": title,
                "body": body,
                "labels": [label, sev_label],
            })
            opened += 1
            print(f"  opened: {title}")
        except Exception as e:
            print(f"  FAILED: {title} — {e}")

    print(f"Opened {opened} / {len(findings)} issues.")


if __name__ == "__main__":
    main()
