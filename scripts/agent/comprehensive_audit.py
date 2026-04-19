"""Comprehensive monthly audit — runs every audit module, assembles a single
professional markdown report, and writes an executive summary for Telegram.

Report goes to: docs/audits/YYYY-MM-DD-full-audit.md
Exec summary:   /tmp/exec_summary.txt  (consumed by telegram_notify)

Usage:
    python -m scripts.agent.comprehensive_audit
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDITS_DIR = REPO / "docs" / "audits"
TMP = Path("/tmp") if Path("/tmp").exists() else REPO / "tmp"
TMP.mkdir(exist_ok=True)


def _run(module: str, extra_args: list[str], out_path: Path) -> dict | None:
    print(f"[run] {module} {' '.join(extra_args)}")
    try:
        subprocess.run(
            [sys.executable, "-m", f"scripts.agent.{module}", "--out", str(out_path), *extra_args],
            check=True, cwd=str(REPO),
        )
        return json.loads(out_path.read_text(encoding="utf-8"))
    except subprocess.CalledProcessError as e:
        print(f"  [warn] {module} exited non-zero: {e}", file=sys.stderr)
    except Exception as e:
        print(f"  [warn] {module} failed: {e}", file=sys.stderr)
    return None


def main() -> int:
    now = datetime.now(timezone.utc)
    date = now.strftime("%Y-%m-%d")

    # Run all modules
    # pull_flow_report writes to data/flow-reports/<date>-<tag>.json — handle specially
    try:
        subprocess.run(
            [sys.executable, "-m", "scripts.agent.pull_flow_report",
             "--timeframe", "last_30_days", "--tag", "audit"],
            check=True, cwd=str(REPO),
        )
        flow_file = REPO / "data" / "flow-reports" / f"{date}-audit.json"
        flow_snap = json.loads(flow_file.read_text(encoding="utf-8")) if flow_file.exists() else None
    except Exception as e:
        print(f"  [warn] pull_flow_report failed: {e}", file=sys.stderr)
        flow_snap = None
    campaigns = _run("audit_campaigns", ["--days", "90"], TMP / "campaigns.json")
    segments = _run("audit_segments", [], TMP / "segments.json")
    deliver = _run("audit_deliverability", [], TMP / "deliverability.json")
    per_email = _run("audit_per_email", ["--days", "30"], TMP / "per_email.json")
    metrics = _run("audit_metrics", ["--days", "30"], TMP / "metrics.json")
    revenue = _run("audit_revenue", ["--days", "30"], TMP / "revenue.json")

    # Build report
    lines: list[str] = []
    lines.append(f"# Zen Hair · Comprehensive Email Audit · {date}")
    lines.append("")
    lines.append(f"_Generated {now.isoformat()} UTC_")
    lines.append("")
    lines.append("---")
    lines.append("")

    all_findings: list[dict] = []
    for section, data in [
        ("flows", flow_snap),
        ("campaigns", campaigns),
        ("segments", segments),
        ("deliverability", deliver),
        ("per_email", per_email),
        ("metrics", metrics),
        ("revenue", revenue),
    ]:
        if data and isinstance(data.get("findings"), list):
            for f in data["findings"]:
                f["_section"] = section
            all_findings.extend(data["findings"])

    # ---- Executive summary ----
    critical = [f for f in all_findings if f.get("severity") == "critical"]
    warnings = [f for f in all_findings if f.get("severity") == "warning"]
    infos = [f for f in all_findings if f.get("severity") == "info"]
    status = "🚨 CRITICAL" if critical else ("⚠️ WARNING" if warnings else "✅ HEALTHY")

    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"**Overall status:** {status}")
    lines.append(f"- Critical: {len(critical)}  ·  Warnings: {len(warnings)}  ·  Info: {len(infos)}")
    lines.append("")
    if revenue:
        lines.append(
            f"- Revenue (30d): {revenue.get('total_revenue_sar', 0):,.0f} SAR "
            f"· Orders: {revenue.get('total_orders', 0):,} "
            f"· Flow share: {revenue.get('flow_share_pct', 0):.1f}%"
        )
        if revenue.get("rpas_sar") is not None:
            lines.append(f"- RPAS (revenue / active sub): {revenue['rpas_sar']:.2f} SAR")
    if segments and segments.get("master_list"):
        ml = segments["master_list"]
        size = ml.get('profile_count') or 0
        lines.append(f"- List size: {size:,} profiles ({ml.get('name')})")
    if campaigns:
        lines.append(f"- Campaigns sent (90d): {campaigns.get('campaign_count', 0)}")
    lines.append("")

    # ---- Top 3 actions ----
    def _priority_score(f: dict) -> int:
        return {"critical": 3, "warning": 2, "info": 1}.get(f.get("severity", ""), 0)
    top_actions = sorted(
        [f for f in all_findings if f.get("action")],
        key=_priority_score, reverse=True,
    )[:3]
    lines.append("## This month's top 3 actions")
    lines.append("")
    for i, f in enumerate(top_actions, 1):
        sev = f.get("severity", "info").upper()
        sec = f.get("_section", "").upper()
        lines.append(f"{i}. **[{sev}]** _{sec}_ — {f.get('action')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ---- Section renderers ----
    def _render_section(title: str, data: dict | None, renderer) -> None:
        lines.append(f"## {title}")
        lines.append("")
        if not data:
            lines.append("_Module failed to run. Check workflow logs._")
            lines.append("")
            return
        renderer(data)
        lines.append("")

    def _flows(d):
        rows = d.get("flows") or []
        lines.append("Live flow performance (last 30 days):")
        lines.append("")
        lines.append("| Flow | Recipients | Open | Click | Unsub | Bounce | RPR |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        def _stat(r, k): return (r.get("statistics") or {}).get(k) or r.get(k) or 0
        for r in sorted(rows, key=lambda r: _stat(r, "recipients"), reverse=True):
            name = r.get("flow_name") or r.get("name") or "?"
            lines.append(
                f"| {name} | {int(_stat(r,'recipients')):,} "
                f"| {_stat(r,'open_rate')*100:.2f}% "
                f"| {_stat(r,'click_rate')*100:.2f}% "
                f"| {_stat(r,'unsubscribe_rate')*100:.3f}% "
                f"| {_stat(r,'bounce_rate')*100:.2f}% "
                f"| {_stat(r,'revenue_per_recipient'):.2f} |"
            )

    def _campaigns(d):
        cs = d.get("campaigns") or []
        if not cs:
            lines.append("_No campaigns sent in window._")
            return
        lines.append(f"{len(cs)} campaigns in last {d.get('window_days', 90)} days. Top 5 by revenue:")
        lines.append("")
        lines.append("| Campaign | Recipients | Open | Click | Revenue (SAR) |")
        lines.append("|---|---:|---:|---:|---:|")
        for r in cs[:5]:
            lines.append(
                f"| {r.get('name','?')} | {int(r.get('recipients') or 0):,} "
                f"| {(r.get('open_rate') or 0)*100:.2f}% "
                f"| {(r.get('click_rate') or 0)*100:.2f}% "
                f"| {(r.get('conversion_value') or 0):,.0f} |"
            )

    def _segments(d):
        ml = d.get("master_list") or {}
        lines.append(f"**Master list:** {ml.get('name', '?')} — {int(ml.get('profile_count') or 0):,} profiles")
        if d.get("engaged_90d"):
            e = d["engaged_90d"]
            lines.append(f"**Engaged (90d):** {int(e.get('profile_count') or 0):,}")
        if d.get("unengaged"):
            u = d["unengaged"]
            lines.append(f"**Unengaged:** {int(u.get('profile_count') or 0):,}")
        lines.append("")
        lines.append(f"**Total segments:** {len(d.get('segments') or [])}")

    def _deliver(d):
        lines.append(f"**Domain:** `{d.get('domain')}`")
        lines.append("")
        spf = d.get("spf") or {}
        lines.append(f"- **SPF:** {'✅' if spf.get('value') else '❌'} — {spf.get('value') or 'MISSING'}")
        if spf.get("includes_missing"):
            lines.append(f"  - Missing includes: `{', '.join(spf['includes_missing'])}`")
        for dk in d.get("dkim") or []:
            sym = "✅" if dk.get("valid") else "❌"
            lines.append(f"- **DKIM** `{dk.get('selector')}`: {sym}")
        dmarc = d.get("dmarc") or {}
        lines.append(f"- **DMARC:** policy=`{dmarc.get('policy') or 'NONE'}` · record: `{dmarc.get('value') or 'MISSING'}`")

    def _per_email(d):
        issues = [f for f in (d.get("findings") or []) if f.get("kind") in {"weak_email_in_flow", "high_unsub_email"}]
        if not issues:
            lines.append("_No weak-link emails flagged._")
            return
        lines.append("Flagged emails:")
        lines.append("")
        for f in issues:
            lines.append(f"- **{f.get('flow_name')}** / `{f.get('weak_msg_id') or f.get('msg_id')}` — {f.get('action')}")

    def _metrics(d):
        lines.append("| Metric | 30d total | Last 7d | Prior 7d | WoW |")
        lines.append("|---|---:|---:|---:|---:|")
        for m in d.get("metrics") or []:
            wow = m.get("wow_change_pct")
            wow_str = f"{wow:+.1f}%" if wow is not None else "—"
            lines.append(
                f"| {m['name']} | {m.get('total_30d', 0):,} "
                f"| {m.get('latest_7d', 0):,} | {m.get('prior_7d', 0):,} | {wow_str} |"
            )

    def _revenue(d):
        lines.append(f"**Total store revenue (30d):** {d.get('total_revenue_sar', 0):,.0f} SAR  ·  {d.get('total_orders', 0):,} orders")
        lines.append(f"**Flow-attributed:** {d.get('flow_revenue_sar', 0):,.0f} SAR ({d.get('flow_share_pct', 0):.1f}%)")
        lines.append(f"**Other sources:** {d.get('other_revenue_sar', 0):,.0f} SAR")
        if d.get("rpas_sar") is not None:
            lines.append(f"**RPAS:** {d['rpas_sar']:.2f} SAR / active sub")
        lines.append("")
        lines.append("Top revenue-driving flows:")
        for r in (d.get("top_flows") or [])[:5]:
            lines.append(f"- {r.get('name')} — {r.get('revenue', 0):,.0f} SAR")

    _render_section("1. Flow performance", flow_snap, _flows)
    _render_section("2. Campaign performance", campaigns, _campaigns)
    _render_section("3. List & segment health", segments, _segments)
    _render_section("4. Deliverability infrastructure", deliver, _deliver)
    _render_section("5. Per-email breakdown", per_email, _per_email)
    _render_section("6. Top-level metric trajectory", metrics, _metrics)
    _render_section("7. Revenue attribution", revenue, _revenue)

    # ---- All findings table ----
    lines.append("## Full findings log")
    lines.append("")
    if not all_findings:
        lines.append("_No findings — everything in spec._")
    else:
        lines.append("| Sev | Area | Kind | Action |")
        lines.append("|---|---|---|---|")
        for f in sorted(all_findings, key=_priority_score, reverse=True):
            action = (f.get("action") or "").replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {f.get('severity','info')} | {f.get('_section','')} | "
                f"{f.get('kind','')} | {action} |"
            )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("_Generated by `scripts/agent/comprehensive_audit.py` — tune thresholds in `config/thresholds.yml`._")

    # Write report
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = AUDITS_DIR / f"{date}-full-audit.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote report to {report_path}")

    # Exec summary for Telegram (short)
    summary = [
        f"{status}  ·  Zen Hair Email Audit  ·  {date}",
        f"Critical: {len(critical)}  ·  Warn: {len(warnings)}  ·  Info: {len(infos)}",
    ]
    if revenue:
        summary.append(f"Revenue 30d: {revenue.get('total_revenue_sar', 0):,.0f} SAR ({revenue.get('flow_share_pct', 0):.0f}% flows)")
    summary.append("")
    summary.append("Top 3 actions:")
    for i, f in enumerate(top_actions, 1):
        summary.append(f"{i}. [{f.get('severity','').upper()}] {f.get('action','')[:200]}")
    (TMP / "exec_summary.txt").write_text("\n".join(summary), encoding="utf-8")
    print(f"Wrote exec summary to {TMP / 'exec_summary.txt'}")

    return 2 if critical else (1 if warnings else 0)


if __name__ == "__main__":
    raise SystemExit(main())
