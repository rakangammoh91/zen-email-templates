"""DNS-based deliverability check — SPF, DKIM, DMARC for the sending domain.

Pure stdlib DNS via socket → falls back to dnspython if installed.
No Klaviyo API call needed.

Usage:
    python -m scripts.agent.audit_deliverability --out /tmp/deliverability.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
THRESHOLDS = yaml.safe_load((REPO / "config" / "thresholds.yml").read_text(encoding="utf-8"))


def _txt_records(name: str) -> list[str]:
    """Resolve TXT records via nslookup (universally available on GH Actions + Windows)."""
    try:
        out = subprocess.check_output(
            ["nslookup", "-type=TXT", name], stderr=subprocess.STDOUT, timeout=15, text=True
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return [f"__ERROR__: {e}"]
    records: list[str] = []
    for line in out.splitlines():
        line = line.strip()
        if 'text =' in line or 'text=' in line or line.startswith('"'):
            # extract between quotes
            if '"' in line:
                parts = line.split('"')
                chunks = [p for i, p in enumerate(parts) if i % 2 == 1]
                if chunks:
                    records.append("".join(chunks))
    return records


def _cname(name: str) -> str | None:
    try:
        out = subprocess.check_output(
            ["nslookup", "-type=CNAME", name], stderr=subprocess.STDOUT, timeout=15, text=True
        )
    except Exception:
        return None
    for line in out.splitlines():
        line = line.strip()
        if "canonical name =" in line:
            return line.split("canonical name =")[-1].strip().rstrip(".")
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cfg = THRESHOLDS["deliverability"]
    domain = cfg["sending_domain"]
    findings: list[dict] = []

    # ---- SPF ----
    spf_records = [r for r in _txt_records(domain) if r.lower().startswith("v=spf1")]
    spf_value = spf_records[0] if spf_records else None
    spf_includes_ok = []
    spf_includes_missing = []
    if spf_value:
        for needed in cfg["spf_required_includes"]:
            if needed in spf_value:
                spf_includes_ok.append(needed)
            else:
                spf_includes_missing.append(needed)
        if spf_includes_missing:
            findings.append({
                "severity": "warning",
                "kind": "spf_missing_include",
                "domain": domain,
                "missing": spf_includes_missing,
                "current": spf_value,
                "action": (
                    f"Add to SPF record for {domain}: include: {', '.join(spf_includes_missing)}. "
                    "Edit existing TXT record; do NOT create second SPF."
                ),
            })
    else:
        findings.append({
            "severity": "critical",
            "kind": "spf_missing",
            "domain": domain,
            "action": f"No SPF record on {domain}. Add TXT: 'v=spf1 include:_spf.klaviyo.com ~all'.",
        })

    # ---- DKIM ----
    dkim_results = []
    for selector in cfg["dkim_selectors"]:
        full = f"{selector}.{domain}"
        recs = _txt_records(full)
        cname = _cname(full)
        joined = " ".join(recs).lower()
        valid = (
            "v=dkim1" in joined
            or ("k=rsa" in joined and "p=" in joined)
            or bool(cname and ("domainkey" in cname.lower() or "dkim" in cname.lower()))
        )
        dkim_results.append({"selector": selector, "records": recs, "cname": cname, "valid": valid})
        if not valid:
            findings.append({
                "severity": "warning",
                "kind": "dkim_missing",
                "selector": full,
                "action": (
                    f"DKIM selector {full} not resolving. "
                    "In Klaviyo → Account → Domains & Hosting, verify sending domain; "
                    "Klaviyo will show CNAME targets to add."
                ),
            })

    # ---- DMARC ----
    dmarc_records = [r for r in _txt_records(f"_dmarc.{domain}") if r.lower().startswith("v=dmarc1")]
    dmarc_value = dmarc_records[0] if dmarc_records else None
    dmarc_policy = None
    if dmarc_value:
        for token in dmarc_value.split(";"):
            token = token.strip()
            if token.lower().startswith("p="):
                dmarc_policy = token.split("=", 1)[1].strip().lower()
                break
    policy_rank = {"none": 0, "quarantine": 1, "reject": 2}
    min_rank = policy_rank.get(cfg["dmarc_min_policy"], 1)
    cur_rank = policy_rank.get(dmarc_policy or "", -1)

    if not dmarc_value:
        findings.append({
            "severity": "critical",
            "kind": "dmarc_missing",
            "domain": domain,
            "action": (
                f"No DMARC on _dmarc.{domain}. "
                "Start with: 'v=DMARC1; p=none; rua=mailto:dmarc@zenhairshop.com;' "
                "→ monitor 2 weeks → upgrade to p=quarantine."
            ),
        })
    elif cur_rank < min_rank:
        findings.append({
            "severity": "warning",
            "kind": "dmarc_weak_policy",
            "current": dmarc_policy,
            "minimum": cfg["dmarc_min_policy"],
            "record": dmarc_value,
            "action": (
                f"DMARC policy is '{dmarc_policy}'. Upgrade to '{cfg['dmarc_min_policy']}' "
                "once SPF+DKIM reports show clean alignment for 2+ weeks."
            ),
        })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domain": domain,
        "spf": {
            "value": spf_value,
            "includes_ok": spf_includes_ok,
            "includes_missing": spf_includes_missing,
        },
        "dkim": dkim_results,
        "dmarc": {"value": dmarc_value, "policy": dmarc_policy},
        "findings": findings,
    }
    text = json.dumps(out, indent=2, default=str)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
