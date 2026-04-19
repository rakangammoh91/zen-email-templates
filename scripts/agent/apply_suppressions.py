"""Suppress profiles listed in the latest suppression-candidates CSV.

SAFETY: defaults to --dry-run. You must explicitly pass --live to actually
call Klaviyo's suppression API. Every run writes a decision log regardless
of dry/live mode.

Klaviyo endpoint:
  POST /api/profile-suppression-bulk-create-jobs/
  body: data.type = "profile-suppression-bulk-create-job"
        data.attributes.profiles.data = [{type:"profile", attributes:{email:"..."}}]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .klaviyo_client import KlaviyoClient

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
CAND_DIR = REPO_ROOT / "data" / "suppression-candidates"
LOG_DIR = REPO_ROOT / "data" / "suppression-log"


def latest_candidates_csv() -> Path | None:
    files = sorted(CAND_DIR.glob("*.csv"))
    return files[-1] if files else None


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def suppress_batch(client: KlaviyoClient, emails: list[str]) -> dict:
    body = {
        "data": {
            "type": "profile-suppression-bulk-create-job",
            "attributes": {
                "profiles": {
                    "data": [
                        {"type": "profile", "attributes": {"email": e}}
                        for e in emails
                    ]
                }
            }
        }
    }
    return client.post("/profile-suppression-bulk-create-jobs/", body)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", help="override candidates CSV path")
    p.add_argument("--live", action="store_true", help="actually call Klaviyo — default is dry-run")
    p.add_argument("--batch-size", type=int, default=100)
    args = p.parse_args()

    path = Path(args.csv) if args.csv else latest_candidates_csv()
    if not path or not path.exists():
        print("No candidates CSV found. Run find_bouncers.py first.")
        return

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    emails = [r["email"] for r in rows if r.get("email")]
    print(f"Candidates in {path.name}: {len(emails)} emails")
    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"Mode: {mode}")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    log_path = LOG_DIR / f"{ts}-{mode.lower()}.json"
    log: dict = {
        "timestamp": ts,
        "mode": mode,
        "source_csv": str(path.relative_to(REPO_ROOT)),
        "total_candidates": len(emails),
        "batches": [],
    }

    if not args.live:
        log["note"] = "DRY-RUN — no Klaviyo API calls made. Pass --live to execute."
        log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
        print(f"Dry-run complete. Log: {log_path.relative_to(REPO_ROOT)}")
        print("To actually suppress, re-run with --live")
        return

    client = KlaviyoClient()
    success = 0
    failed = 0
    for batch in chunks(emails, args.batch_size):
        try:
            resp = suppress_batch(client, batch)
            job_id = resp.get("data", {}).get("id")
            log["batches"].append({"count": len(batch), "job_id": job_id, "ok": True})
            success += len(batch)
            print(f"  suppressed batch of {len(batch)} (job {job_id})")
        except Exception as e:
            log["batches"].append({"count": len(batch), "error": str(e), "ok": False})
            failed += len(batch)
            print(f"  FAILED batch of {len(batch)}: {e}")

    log["success"] = success
    log["failed"] = failed
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Done. Success: {success}  Failed: {failed}")
    print(f"Log: {log_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
