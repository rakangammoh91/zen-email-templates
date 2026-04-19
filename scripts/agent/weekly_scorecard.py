"""Render the weekly flow scorecard for Telegram.

Reads the two latest `*-weekly.json` snapshots, computes WoW open-rate delta,
and sends a compact pre-formatted table to Telegram.

Usage:
    python -m scripts.agent.weekly_scorecard
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from . import telegram_notify

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]
SNAP_DIR = REPO / "data" / "flow-reports"
REGISTRY = yaml.safe_load((REPO / "registry" / "flows.yml").read_text(encoding="utf-8"))


def _load_weekly() -> tuple[dict | None, dict | None]:
    files = sorted(SNAP_DIR.glob("*-weekly.json"))
    latest = json.loads(files[-1].read_text(encoding="utf-8")) if files else None
    prior = json.loads(files[-2].read_text(encoding="utf-8")) if len(files) >= 2 else None
    return latest, prior


def _registry_by_id() -> dict[str, dict]:
    return {f["id"]: f for f in REGISTRY["flows"]}


def _stat(row: dict, key: str) -> float:
    s = (row.get("statistics") or {}) if isinstance(row.get("statistics"), dict) else {}
    return float(s.get(key) or row.get(key) or 0)


def _short(name: str, max_len: int = 18) -> str:
    n = name.replace("AM · AR · ", "").replace("AM · AR ·", "")
    return n if len(n) <= max_len else n[: max_len - 1] + "…"


def render() -> str:
    latest, prior = _load_weekly()
    if not latest:
        return "🟢 *Zen Hair Weekly Scorecard*\n_No weekly snapshot yet._"

    reg = _registry_by_id()
    prior_by_id = {}
    if prior:
        prior_by_id = {
            (r.get("flow_id") or r.get("id")): r for r in (prior.get("flows") or [])
        }

    rows = latest.get("flows") or []
    rows_sorted = sorted(rows, key=lambda r: _stat(r, "recipients"), reverse=True)

    # Header
    lines: list[str] = []
    lines.append(f"📊 *Zen Hair · Weekly Scorecard*")
    lines.append(f"`{latest.get('pulled_at','?')[:10]}`  ·  timeframe: {latest.get('timeframe','?')}")
    lines.append("")
    # Monospaced table inside ``` for Telegram alignment
    lines.append("```")
    lines.append(f"{'Flow':<19} {'Sent':>5} {'Open':>6} {'Unsub':>6} {'RPR':>5} {'Δ Open':>7}")
    lines.append("-" * 53)

    tot_recip = tot_open_unique = 0.0
    tot_unsub = 0.0
    for r in rows_sorted:
        fid = r.get("flow_id") or r.get("id")
        reg_entry = reg.get(fid, {})
        is_protected = reg_entry.get("protected")
        name = _short(reg_entry.get("name") or r.get("flow_name") or fid or "?")
        if is_protected:
            name = (name + " 🛡")[:19]

        recip = _stat(r, "recipients")
        open_r = _stat(r, "open_rate") * 100
        unsub_r = _stat(r, "unsubscribe_rate") * 100
        rpr = _stat(r, "revenue_per_recipient")
        rpr_str = f"{rpr:.2f}" if rpr else "—"

        prior_row = prior_by_id.get(fid)
        delta_str = "—"
        if prior_row:
            prior_open = _stat(prior_row, "open_rate") * 100
            delta = open_r - prior_open
            if abs(delta) >= 0.1:
                delta_str = f"{delta:+.1f}pp"

        lines.append(
            f"{name:<19} {int(recip):>5} {open_r:>5.1f}% {unsub_r:>5.2f}% {rpr_str:>5} {delta_str:>7}"
        )
        tot_recip += recip
        tot_open_unique += _stat(r, "opens_unique")
        tot_unsub += _stat(r, "unsubscribes")

    lines.append("-" * 53)
    port_open = (tot_open_unique / tot_recip * 100) if tot_recip else 0
    port_unsub = (tot_unsub / tot_recip * 100) if tot_recip else 0
    lines.append(
        f"{'Portfolio':<19} {int(tot_recip):>5} {port_open:>5.1f}% {port_unsub:>5.2f}%"
    )
    lines.append("```")
    lines.append("")
    lines.append("🛡 = protected flow (stricter thresholds)")
    return "\n".join(lines)


def main() -> int:
    text = render()
    telegram_notify.send(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
