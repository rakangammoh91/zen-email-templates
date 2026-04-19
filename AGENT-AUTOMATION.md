# Zen Hair · Email Marketing Agent · Automation Runbook

Companion to `AGENT.md` (which covers how a Claude session operates against this repo). This file covers the **cloud automation layer**: cron jobs, secrets, alerting, and the hybrid build-vs-monitor architecture.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub repo = single source of truth                        │
│  ├── registry/flows.yml      (machine-readable inventory)    │
│  ├── flows/<slug>/           (flow-as-folder specs)          │
│  ├── data/flow-reports/      (append-only JSON snapshots)    │
│  ├── scripts/agent/          (Python: pull, detect, notify)  │
│  └── .github/workflows/      (cron in the cloud)             │
└─────────────────────────────────────────────────────────────┘
        ▲                    │                        │
        │                    ▼                        ▼
  ┌───────────┐       ┌──────────────┐        ┌─────────────┐
  │ Obsidian  │       │ Telegram bot │        │ Klaviyo API │
  │ (Git plug)│       │ (alerts)     │        │ (read-only) │
  └───────────┘       └──────────────┘        └─────────────┘
```

**Why this shape:**
- GitHub Actions = free cron that runs even when your laptop is off
- Git = the database (every pull is a commit, time-travel for free)
- Telegram = your output channel (matches user preference; per MEMORY.md)
- Obsidian Git plugin pulls the same repo → vault auto-mirrors with zero work
- Claude Code + MCP handle the interactive work (rebuilds, subject rewrites)

---

## Setup (one-time)

### 1. GitHub secrets

Repo → Settings → Secrets and variables → Actions → New repository secret:

| Name | Source |
|---|---|
| `KLAVIYO_PRIVATE_API_KEY` | Klaviyo → Account → API keys → new **read-only** key |
| `TELEGRAM_BOT_TOKEN` | @BotFather → `/newbot` |
| `TELEGRAM_CHAT_ID` | message your bot → `curl https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id` |

Read-only Klaviyo scope is deliberate — cloud automation must not be able to mutate the account.

### 2. Enable workflows

Repo → Actions. Each workflow appears; click each and enable:
- `daily-health`
- `weekly-snapshot`
- `monthly-rollup`
- `watchdog`

Dispatch `weekly-snapshot` manually once to verify the whole chain: pull → detect → append → Telegram → commit.

### 3. Local env (for running scripts from laptop)

`.env`:
```
KLAVIYO_PRIVATE_API_KEY=pk_...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Smoke test:
```bash
pip install -r scripts/agent/requirements.txt
python -m scripts.agent.pull_flow_report --timeframe last_7_days --tag weekly
python -m scripts.agent.detect_anomalies --tag weekly
python -m scripts.agent.telegram_notify --text "Agent test ping"
```

### 4. Obsidian sync

Install **Obsidian Git** plugin. Configure:
- Remote: `https://github.com/rakangammoh91/zen-email-templates`
- Branch: `main`
- Auto-pull: 5 min
- Pull on startup: yes

Vault auto-mirrors `docs/` on every push — zero manual sync.

---

## Cadence

All times Asia/Amman. Cron in YAML is UTC.

| When | What | Commits? | Telegram? |
|---|---|---|---|
| Daily 08:00 | bounce / unsub / spam check (last_1_days) | only on alert | only on alert |
| Monday 07:00 | weekly snapshot + WoW delta | yes | always (digest) |
| 1st of month 07:00 | 30d rollup + auto strategy-review issue | yes | issue link |
| 1st of month 08:00 | **comprehensive audit** (flows + campaigns + segments + deliverability + revenue + metrics) | yes | exec summary |
| Tuesday 09:00 | watchdog on missing weekly snapshot | no | only if stale |

---

## What's automated vs. what's judgment

**Automated read-only (cloud, zero human touch):**
- Data pulls from Klaviyo (`pull_flow_report`)
- Threshold-based regression detection (`detect_anomalies`)
- Telegram digests and alerts (`telegram_notify`)
- Performance log appends (`append_log`)
- Auto-learnings digest every week (`write_learnings`)
- Auto GitHub issue per alert (`open_issues`) — deduplicated by title
- Auto rewrite brief on subject regressions (`propose_rewrites`) — writes
  `flows/<slug>/proposed-rewrites/YYYY-MM-DD.md` with current subjects,
  regression data, and 5 approach templates ready for next session
- Bounce-candidate discovery (`find_bouncers`) — 2+ bounces/30d → CSV
- Freshness watchdog
- Monthly strategy-review issue creation
- **Comprehensive monthly audit** (`comprehensive_audit`) — runs 7 audit modules
  and writes a professional markdown report to `docs/audits/YYYY-MM-DD-full-audit.md`
  with executive summary, top-3 actions, and prescribed action per finding.
  Covers: flows, campaigns, segments + list health, deliverability
  infrastructure (SPF/DKIM/DMARC DNS), per-email weak links, top-level metric
  trajectory, and revenue attribution (flow share + RPAS).

**Automated scoped-write (Tier 1 — dry-run by default):**
- Profile suppressions (`apply_suppressions`) — reads the bouncer CSV and
  calls Klaviyo `profile-suppression-bulk-create-jobs/`. Cron always runs
  **dry-run** (writes a decision log only). Passing `--live` manually is
  the only way to actually suppress. Reversible via Klaviyo UI.

**Not automated (intentionally — requires a Claude session):**
- Flow rebuilds in the Klaviyo UI
- Subject-line rewrites — agent *proposes*, session *decides*
- Draft → Live promotion
- Pausing a flow on spam alert (Telegram tells you — you pause)
- Live profile suppression — dry-run ships; live requires manual `--live`

---

## Data model

### `registry/flows.yml` (machine-readable inventory)

The source of truth for what exists and what's tracked. Automation reads `flows[*].id` and filters by `status: live` + `track_performance != false`. Baseline metrics per flow are used by the monthly swap-event measurement.

### `config/thresholds.yml` (alert rules)

One YAML file edits the whole alerting layer. Kill-switch is `spam_complaint_rate_pct: 0.1`. Protected flows (`Xkg5DZ` Abandoned Cart) use half the tolerance — regressions there have higher blast radius.

### `data/flow-reports/*.json` (snapshot history)

Append-only. File naming: `YYYY-MM-DD-{daily|weekly|monthly|baseline}.json`. Each snapshot is self-describing (embeds the timeframe, metric ID, and per-flow metadata) so you can replay history without external context.

### `docs/flows-performance-log.md` (human-readable log)

Auto-appended by `scripts/agent/append_log.py`. Weekly/monthly sections fill top-down; oldest at the bottom.

---

## Adding a new flow

1. Add entry to `registry/flows.yml` with `status: draft`, `tier: rebuilt`, pointing at the `replaces:` ID
2. Scaffold: `mkdir -p flows/<slug>/emails`
3. Write `spec.md`, per-email markdown, `decisions.md`
4. Build in Klaviyo UI with Claude (interactive session)
5. Run `skills/klaviyo-flow-auditor` checklist
6. When QA passes: flip `status: live` + commit — swap-detector captures the baseline

---

## Kill-switch procedure (critical alert)

1. Telegram: `🚨 PAUSE FLOW <name>` with flow ID
2. **You** pause the flow in Klaviyo (not the bot — destructive action stays human)
3. Open a post-mortem issue in the repo
4. Log root cause in `flows/<slug>/decisions.md`
5. Fix, test, resume — append resolution note

---

## Failure modes & what protects against them

| Failure | Protection |
|---|---|
| GitHub Action fails silently | `watchdog.yml` pings Telegram on missing weekly snapshot |
| Klaviyo rate-limit 429 | `KlaviyoClient` exponential backoff + retry |
| Klaviyo 5xx | Retry w/ backoff |
| Stale API key | `pull_flow_report` raises clear error → workflow red → you get GH Actions failure email |
| Corrupted snapshot | Append-only history; revert one commit |
| Telegram bot down | Snapshots still commit; alert queued; next run re-fires |
| Laptop off | Irrelevant — it all runs in GitHub's cloud |

---

## Future extensions (roadmap)

- `swap-detector.yml` — auto-detect `status: draft → live` and create post-swap measurement issue at T+30d
- Campaign-level tracking (right now: flows only)
- Segment-health monitor (reach pool + unsub trajectory)
- Auto-generated monthly comparison PDF for client reports
- Per-email stat breakout (currently we roll up at flow level)
