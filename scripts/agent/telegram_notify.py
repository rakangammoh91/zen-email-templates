"""Send a Telegram message via bot API.

Reads TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from env.
Supports:
  python -m scripts.agent.telegram_notify --text "hello"
  python -m scripts.agent.telegram_notify --from-anomalies path/to/anomalies.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

MAX_LEN = 3800  # Telegram hard limit is 4096; keep headroom


def send(text: str) -> None:
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
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()
    print("Telegram sent.")


def format_anomalies(result: dict) -> str:
    status = result["status"]
    icon = {"ok": "✅", "warning": "⚠️", "critical": "🚨"}[status]
    lines = [f"{icon} *Zen Hair flows · {result['tag']}*"]
    lines.append(f"Status: *{status.upper()}*")
    lines.append(f"Snapshot: `{result['latest_snapshot']}`")
    if result.get("prior_snapshot"):
        lines.append(f"Compared to: `{result['prior_snapshot']}`")
    lines.append("")
    findings = result.get("findings", [])
    if not findings:
        lines.append("_No issues. Every tracked flow is inside thresholds._")
    else:
        for f in findings:
            sev = {"critical": "🚨", "warning": "⚠️"}[f["severity"]]
            metric = f["metric"].replace("_", " ")
            if "value_pct" in f:
                detail = f"{f['value_pct']}% (thr {f['threshold_pct']}%)"
            elif "value_pp" in f:
                detail = f"-{f['value_pp']}pp (thr {f['threshold_pp']}pp)"
            else:
                detail = ""
            line = f"{sev} *{f['flow_name']}* · {metric} · {detail}"
            if f.get("action"):
                line += f"\n   → *{f['action']}*"
            lines.append(line)
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--text")
    p.add_argument("--from-anomalies")
    args = p.parse_args()

    if args.from_anomalies:
        with open(args.from_anomalies, encoding="utf-8") as f:
            result = json.load(f)
        send(format_anomalies(result))
    elif args.text:
        send(args.text)
    else:
        raise SystemExit("Provide --text or --from-anomalies")


if __name__ == "__main__":
    main()
