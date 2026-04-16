# Zen Hair · Deliverability Baseline
> Updated: 2026-04-16 · refreshed weekly by Auditor
> Source: Klaviyo `campaign_report` + `flow_report` · last 90 days · `Placed Order` conversion metric (RFkPcF)
> Scope: 98 campaigns (recipients ≥ 100 each) · 8 live flows · channel = email

---

## Current Floor (rolling averages · campaigns + flows, weighted by sends)

| Metric | 7d | 30d | 90d | Status |
|---|---|---|---|---|
| Unsubscribe rate | 0.063% | **0.226%** | 0.136% | 7d 🟢 · 30d 🟡 · 90d 🟡 |
| Bounce rate | 0.26% | 0.17% | 0.51% (campaigns) / 2.02% (flows) | 🟢 on campaigns · 🟡 on flows |
| Spam complaint rate | 0.000% | 0.0009% | 0.0027% | 🟢 across the board |
| Delivery rate | 99.74% | 99.83% | 99.49% | 🟢 |

**Campaign-only aggregates (the load-bearing numbers · campaigns = 95%+ of send volume):**

| Window | Campaigns | Recipients | Delivered | Bounced | Unsubs | Spam |
|---|---|---|---|---|---|---|
| 7d  | 10 | 39,600 | 39,496 | 104 | 25 | 0 |
| 30d | 34 | 107,814 | 107,626 | 188 | 244 | 1 |
| 90d | 98 | 334,331 | 332,631 | 1,700 | 455 | 9 |

**Flow-only aggregates (90d, live Arabic flows):**

| Flow | Recipients | Bounce rate | Unsub rate | Spam |
|---|---|---|---|---|
| Arabic Welcome (RpUXJv) | 6,251 | 2.05% 🟡 | 0.08% | 0 |
| Arabic Browse Abandonment (VKsTPF) | 5,224 | 2.05% 🟡 | 0.11% | 0 |
| Arabic Referral (TqHqU2) | 2,423 | 2.27% 🟡 | 0.17% | 0 |
| Arabic Abandoned Cart (Xkg5DZ) | 2,148 | 1.63% 🟡 | 0.19% | 0 |
| English Welcome archive (XVkXi4) | 933 | 1.39% 🟡 | 0.21% | 0 |
| Arabic Abandoned Checkout (Xu8gx8) | 767 | 2.48% 🟡 | 0.13% | 0 |
| Arabic Site Abandonment (UQqPVR) | 667 | 1.95% 🟡 | 0.60% 🚨 | 0 |
| Arabic Customer TY (UcxCCH) | 231 | 2.60% 🟡 | 0.87% 🚨 | 0 |

> Flow bounce rates are 5–8× campaign rates. Low volume keeps absolute count small, but the ratio is drifting — the two smallest flows (TY + Site Abandonment) have unsub rates above the 0.5% escalate line. Sample size is still borderline (n < 700 for each) so flag as watch-list, not breach.

---

## Distribution (per-campaign, 90d · n = 98, recipients ≥ 100)

| Metric | Min | P25 | Median | P75 | Max |
|---|---|---|---|---|---|
| Unsubscribe rate | 0.000% | 0.043% | **0.101%** | 0.153% | 1.319% |
| Bounce rate | 0.000% | 0.000% | **0.045%** | 0.131% | 14.471% |
| Spam complaint rate | 0.000% | 0.000% | 0.000% | 0.000% | 0.125% |

**Interpretation:** Median campaign is 🟢 on all three metrics. Healthy floor is confirmed. The 90d aggregates are dragged up by a small number of outliers listed below — two of them big list-cleaning events (heavy bounce) and two of them list-fatigue events (high unsub on a Ramadan/Eid broadcast pair).

---

## Breaches (individual sends that crossed 🚨 thresholds · last 90d)

| Date | Campaign | Metric | Value | Notes / Action |
|---|---|---|---|---|
| 2026-01-17 | Jan 17 · "Can You Tell She's Wearing Extensions?" · AR | Bounce | **14.47%** 🚨 | Massive list-cleaning event on AR list. 4,471 recipients. Old/stale segment included. |
| 2026-01-17 | Jan 17 · same send · EN | Bounce | **10.92%** 🚨 | Same event, EN side. 861 recipients. |
| 2026-03-20 | Mar 20 · Eid Mubarak · AR | Unsub | **1.319%** 🚨 | 4,777 recipients · 63 unsubs in one send. Holiday broadcast to broad list. |
| 2026-03-24 | Mar 24 · Post Ramadan · AR | Unsub | **0.769%** 🚨 | 4,811 recipients · 37 unsubs. Follow-up to Eid send — audience fatigue. |
| 2026-03-13 | Mar 13 · How to make your extensions last twice as long · EN | Spam | **0.125%** 🚨 | 800 recipients · 1 spam complaint. EN list discount email. Single complaint = borderline, but crossed threshold. |

**Action taken so far:** none auto-fired (no Telegram alert configured yet). Breaches are inferred retroactively from this audit. **Required:** escalate to founder on next review, propose suppression rebuild before next broadcast to the AR list >3k.

---

## Early-warning signals (7d worse than 30d?)

| Metric | 7d | 30d | Direction |
|---|---|---|---|
| Unsub rate | 0.063% | 0.226% | ✅ improving (7d better) |
| Bounce rate | 0.26% | 0.17% | ⚠️ 7d worse than 30d — mild drift |
| Spam rate | 0.000% | 0.0009% | ✅ improving |
| Delivery rate | 99.74% | 99.83% | ⚠️ 7d slightly worse |

**Read:** Unsubs have cooled off sharply post-Eid. Bounces ticked up in 7d — likely a segment that hasn't been cleaned since the Jan event. Not a 🚨 yet but worth watching the next broadcast. If next 7d bounce > 0.5% = 🔴.

---

## Alert thresholds (for weekly cron · restated from AUDITOR.md §1)

| Metric | 🟢 Strong | 🟡 OK | 🔴 Problem | 🚨 Escalate (auto-fire Telegram) |
|---|---|---|---|---|
| Unsubscribe rate | < 0.1% | 0.1–0.3% | 0.3–0.5% | **> 0.5%** |
| Spam complaint rate | < 0.01% | 0.01–0.08% | 0.08–0.1% | **> 0.1%** (deliverability risk) |
| Bounce rate | < 1% | 1–3% | 3–5% | **> 5%** |

**Auto-escalation rules (to be wired):**
1. Any individual send ≥ 100 recipients crossing any 🚨 threshold → Telegram ping within 1 hour of send-report finalization + pause recommendation for next scheduled broadcast to the same segment.
2. 7d rolling unsub > 30d rolling unsub by > 50% → warning ping (early drift).
3. 7d rolling bounce > 3% → warning ping (segment hygiene).
4. Any flow crossing 0.5% unsub over ≥500 recipients → flow-step review queued.

---

## Trend (last 4 weeks, campaign-weighted)

| Week ending | Sends | Unsub rate | Bounce rate | Spam rate | Direction |
|---|---|---|---|---|---|
| 2026-03-26 | ~18k | ~0.85% | ~0.10% | ~0.00% | 🚨 Eid spike |
| 2026-04-02 | ~22k | ~0.20% | ~0.15% | ~0.00% | ↓ recovering |
| 2026-04-09 | ~28k | ~0.10% | ~0.12% | ~0.00% | ↓ normalizing |
| 2026-04-16 | ~39.6k | **0.06%** | **0.26%** | 0.00% | ↓ unsub ↗ bounce |

Arrows: unsub ⬇⬇⬇ (excellent recovery) · bounce ➡⬆ (mild drift, watch) · spam ➡ (flat, excellent)

---

## Engaged ratio (30d)

Not computed this cycle — needs a `klaviyo_get_profiles` sample pass + opens metric aggregate. Deferred to next refresh. Placeholder target: 🟢 > 25% of active subscribers opening ≥1 email in 30d.

---

## Version

v1 · 2026-04-16 · Auditor founding pull · next refresh: 2026-04-23 (Sunday 9am Asia/Amman)
