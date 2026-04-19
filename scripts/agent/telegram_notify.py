"""Send a Telegram message via bot API.

Reads TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from env.
Supports:
  python -m scripts.agent.telegram_notify --text "hello"
  python -m scripts.agent.telegram_notify --from-anomalies path/to/anomalies.json
  python -m scripts.agent.telegram_notify --from-audit /tmp/exec_summary.txt

Color code used across all messages:
  🔴 CRITICAL  — act now / kill-switch risk
  🟠 WARNING   — act this week
  🟡 INFO      — worth knowing / optimization
  🟢 HEALTHY   — green, nothing to do
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

MAX_LEN = 3800

SEV_ICON = {
    "critical": "🔴",
    "warning": "🟠",
    "info": "🟡",
    "ok": "🟢",
    "healthy": "🟢",
}


def send(text: str, parse_mode: str = "Markdown") -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram creds missing — printing to stdout instead:")
        print(text)
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text[:MAX_LEN],
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()
    print("Telegram sent.")


def _sev_icon(sev: str) -> str:
    return SEV_ICON.get((sev or "").lower(), "•")


def format_anomalies(result: dict) -> str:
    status = (result.get("status") or "ok").lower()
    header_icon = SEV_ICON.get(status, "•")
    tag = result.get("tag", "").upper()
    lines: list[str] = []
    lines.append(f"{header_icon} *Zen Hair Flows · {tag} Check*")
    lines.append(f"Status: *{status.upper()}*  ·  Snapshot: `{result.get('latest_snapshot','?')}`")
    if result.get("prior_snapshot"):
        lines.append(f"vs. `{result['prior_snapshot']}`")
    lines.append("")

    findings = result.get("findings", [])
    if not findings:
        lines.append("🟢 *All tracked flows inside thresholds.*")
        return "\n".join(lines)

    # Group by severity
    by_sev = {"critical": [], "warning": [], "info": []}
    for f in findings:
        by_sev.setdefault(f.get("severity", "info"), []).append(f)

    for sev in ("critical", "warning", "info"):
        items = by_sev.get(sev) or []
        if not items:
            continue
        icon = _sev_icon(sev)
        lines.append(f"{icon} *{sev.upper()}* ({len(items)})")
        for f in items:
            metric = (f.get("metric") or "").replace("_", " ")
            if "value_pct" in f:
                detail = f"{f['value_pct']}% (thr {f.get('threshold_pct','?')}%)"
            elif "value_pp" in f:
                detail = f"-{f['value_pp']}pp (thr {f.get('threshold_pp','?')}pp)"
            else:
                detail = ""
            lines.append(f"  • *{f.get('flow_name','?')}* · {metric} · {detail}")
            if f.get("action"):
                lines.append(f"    → {f['action']}")
        lines.append("")

    return "\n".join(lines).strip()


def format_audit_summary(exec_text: str) -> str:
    """Re-format the exec_summary.txt from comprehensive_audit into
    the color-coded Telegram format.

    exec_summary.txt shape:
      <status>  ·  Zen Hair Email Audit  ·  <date>
      Critical: N  ·  Warn: N  ·  Info: N
      Revenue 30d: X SAR (Y% flows)
      <blank>
      Top 3 actions:
      1. [CRITICAL] ...
      2. [WARNING] ...
      3. [INFO] ...
    """
    lines_in = exec_text.splitlines()
    if not lines_in:
        return exec_text

    # Normalize header
    out: list[str] = []
    header = lines_in[0]
    lower = header.lower()
    if "critical" in lower:
        icon = "🔴"
    elif "warning" in lower:
        icon = "🟠"
    else:
        icon = "🟢"
    out.append(f"{icon} *Zen Hair · Monthly Audit*")

    # Copy counters & revenue lines (skip the original status header)
    for ln in lines_in[1:]:
        s = ln.strip()
        if not s:
            out.append("")
            continue
        if s.lower().startswith("top 3 actions"):
            out.append("*Top 3 actions*")
            continue
        # Replace [CRITICAL]/[WARNING]/[INFO] bracket with colored icon
        for key in ("CRITICAL", "WARNING", "INFO"):
            tag = f"[{key}]"
            if tag in s:
                s = s.replace(tag, _sev_icon(key.lower()))
                break
        out.append(s)
    return "\n".join(out).strip()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--text")
    p.add_argument("--from-anomalies")
    p.add_argument("--from-audit", help="Path to exec_summary.txt from comprehensive_audit")
    args = p.parse_args()

    if args.from_anomalies:
        with open(args.from_anomalies, encoding="utf-8") as f:
            result = json.load(f)
        send(format_anomalies(result))
    elif args.from_audit:
        text = open(args.from_audit, encoding="utf-8").read()
        send(format_audit_summary(text))
    elif args.text:
        send(args.text)
    else:
        raise SystemExit("Provide --text, --from-anomalies, or --from-audit")


if __name__ == "__main__":
    main()
