# Zen Hair · Comprehensive Email Audit · 2026-04-19

_Generated 2026-04-19T22:26:43.632062+00:00 UTC_

---

## Executive summary

**Overall status:** 🔴 CRITICAL
- Critical: 2  ·  Warnings: 9  ·  Info: 22

- Revenue (30d): 213,086 SAR · Orders: 168 · Flow share: 5.2%
- RPAS (revenue / active sub): 27.05 SAR
- List size: 0 profiles (VIP Offer List)
- Campaigns sent (90d): 99

## This month's top 3 actions

1. **[CRITICAL]** _CAMPAIGNS_ — Investigate subject/content — complaint rate exceeds kill-switch. Pause resend cohorts.
2. **[CRITICAL]** _METRICS_ — Zero 'Started Checkout' events in 30d. Check tracking: Shopify → Klaviyo integration, JS snippet on site.
3. **[WARNING]** _CAMPAIGNS_ — Review targeting — sending to wrong segment or frequency too high.

---

## 1. Flow performance

Live flow performance (last 30 days):

| Flow | Recipients | Open | Click | Unsub | Bounce | RPR |
|---|---:|---:|---:|---:|---:|---:|
| AM · AR · Welcome | 1,692 | 26.65% | 0.35% | 0.118% | 2.07% | 2.95 |
| AM · AR · Browse Abandonment | 1,430 | 29.16% | 1.12% | 0.000% | 1.89% | 2.76 |
| AM · AR · Referral | 897 | 32.55% | 1.11% | 0.111% | 0.33% | 0.00 |
| AM · AR · Abandoned Cart | 609 | 36.12% | 0.33% | 0.164% | 1.64% | 3.61 |
| AM · AR · Site-abandonment | 245 | 24.49% | 0.41% | 0.000% | 4.08% | 0.00 |
| AM · AR · Abandoned Checkout | 208 | 31.73% | 0.96% | 0.000% | 0.96% | 0.00 |
| AM · AR · Customer Thank You | 78 | 42.31% | 0.00% | 1.282% | 2.56% | 0.00 |

## 2. Campaign performance

99 campaigns in last 90 days. Top 5 by revenue:

| Campaign | Recipients | Open | Click | Revenue (SAR) |
|---|---:|---:|---:|---:|
| AM | March 26, 2026 - Be Your Own Kind of Beautiful | AR | No Discount | 4,002 | 71.76% | 0.12% | 5,845 |
| AM | March 14, 2026 - Real women. Real hair. Real results. | AR | Discount | 4,670 | 67.60% | 0.19% | 4,960 |
| AM | March 4, 2026 - How to Make Zen Hair Last Longer | AR | No Discount | 4,970 | 65.41% | 0.08% | 3,843 |
| AM | April 14, 2026 - Summer Humidity Ruins Hair | AR | No Discount | 4,763 | 62.71% | 0.25% | 3,669 |
| AM | February 6, 2026 - Will Hair Extension Damage Your Hair? | Arabic | No Discount | 4,388 | 62.09% | 0.18% | 3,427 |

## 3. List & segment health

**Master list:** VIP Offer List — 0 profiles
**Engaged (90d):** 7,876
**Unengaged:** 4,019

**Total segments:** 62

## 4. Deliverability infrastructure

**Domain:** `zenhairshop.com`

- **SPF:** ✅ — v=spf1 include:spf.titan.email include:mailer.myclickfunnels.com ~all
  - Missing includes: `sendgrid.net, _spf.klaviyo.com`
- **DKIM** `kl1._domainkey`: ❌
- **DKIM** `kl2._domainkey`: ✅
- **DMARC:** policy=`none` · record: `v=DMARC1;p=none;sp=none;adkim=r;aspf=r;pct=100`

## 5. Per-email breakdown

Flagged emails:

- **AM · AR · Abandoned Cart** / `SvndpM` — Review content or cadence — this email is fatiguing recipients.
- **AM · AR · Referral** / `SXrSW3` — Message SXrSW3 in AM · AR · Referral opens 16.0pp below strongest. Candidate for subject rewrite.
- **AM · AR · Referral** / `X5mWcz` — Review content or cadence — this email is fatiguing recipients.

## 6. Top-level metric trajectory

| Metric | 30d total | Last 7d | Prior 7d | WoW |
|---|---:|---:|---:|---:|
| Placed Order | 4 | 4 | 0 | — |
| Started Checkout | 0 | 0 | 0 | — |
| Viewed Product | 86 | 86 | 0 | — |
| Active on Site | 54 | 54 | 0 | — |
| Subscribed to Email Marketing | 18 | 18 | 0 | — |
| Unsubscribed from Email Marketing | 3 | 3 | 0 | — |
| Bounced Email | 8 | 8 | 0 | — |

## 7. Revenue attribution

**Total store revenue (30d):** 213,086 SAR  ·  168 orders
**Flow-attributed:** 11,150 SAR (5.2%)
**Other sources:** 201,936 SAR
**RPAS:** 27.05 SAR / active sub

Top revenue-driving flows:
- AM · AR · Welcome — 4,997 SAR
- AM · AR · Browse Abandonment — 3,952 SAR
- AM · AR · Abandoned Cart — 2,202 SAR
- AM · AR · Referral — 0 SAR
- AM · AR · Site-abandonment — 0 SAR

## Full findings log

| Sev | Area | Kind | Action |
|---|---|---|---|
| critical | campaigns | spam_complaint | Investigate subject/content — complaint rate exceeds kill-switch. Pause resend cohorts. |
| critical | metrics | metric_dark | Zero 'Started Checkout' events in 30d. Check tracking: Shopify → Klaviyo integration, JS snippet on site. |
| warning | campaigns | unsubscribe | Review targeting — sending to wrong segment or frequency too high. |
| warning | campaigns | unsubscribe | Review targeting — sending to wrong segment or frequency too high. |
| warning | campaigns | bounce | Clean list; run find_bouncers + apply_suppressions before next send. |
| warning | deliverability | spf_missing_include | Add to SPF record for zenhairshop.com: include: sendgrid.net, _spf.klaviyo.com. Edit existing TXT record; do NOT create second SPF. |
| warning | deliverability | dkim_missing | DKIM selector kl1._domainkey.zenhairshop.com not resolving. In Klaviyo → Account → Domains & Hosting, verify sending domain; Klaviyo will show CNAME targets to add. |
| warning | deliverability | dmarc_weak_policy | DMARC policy is 'none'. Upgrade to 'quarantine' once SPF+DKIM reports show clean alignment for 2+ weeks. |
| warning | per_email | high_unsub_email | Review content or cadence — this email is fatiguing recipients. |
| warning | per_email | high_unsub_email | Review content or cadence — this email is fatiguing recipients. |
| warning | revenue | low_flow_share | Flows only drive 5.2% of revenue — mostly non-email or campaigns. Investment priority: finish [RG] flow swaps to lift automation-driven revenue. |
| info | campaigns | open_underperform | Subject '' underperformed median by 28.2pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 30.2pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 27.5pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 11.4pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 27.7pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 27.3pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 28.6pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 19.0pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 43.1pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 17.0pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 17.0pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 23.9pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 27.6pp. Rewrite subject pattern. |
| info | campaigns | open_underperform | Subject '' underperformed median by 16.4pp. Rewrite subject pattern. |
| info | campaigns | top_performer | Winner — AM \| March 26, 2026 - Be Your Own Kind of Beautiful \| AR \| No Discount. Extract subject/content patterns; use as template. |
| info | campaigns | top_performer | Winner — AM \| March 14, 2026 - Real women. Real hair. Real results. \| AR \| Discount. Extract subject/content patterns; use as template. |
| info | campaigns | top_performer | Winner — AM \| March 4, 2026 - How to Make Zen Hair Last Longer \| AR \| No Discount. Extract subject/content patterns; use as template. |
| info | per_email | weak_email_in_flow | Message SXrSW3 in AM · AR · Referral opens 16.0pp below strongest. Candidate for subject rewrite. |
| info | revenue | rpas_healthy | On target — hold the line and scale acquisition. |
| info | revenue | top_revenue_flow | Protect AM · AR · Welcome — 4997 SAR over 30d. Stricter alert tolerance. |
| info | revenue | top_revenue_flow | Protect AM · AR · Browse Abandonment — 3952 SAR over 30d. Stricter alert tolerance. |
| info | revenue | top_revenue_flow | Protect AM · AR · Abandoned Cart — 2202 SAR over 30d. Stricter alert tolerance. |

---

_Generated by `scripts/agent/comprehensive_audit.py` — tune thresholds in `config/thresholds.yml`._