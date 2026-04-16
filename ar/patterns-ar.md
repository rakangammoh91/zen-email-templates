# Zen Hair · AR Pattern Library (Data-Extracted)

> ⚠️ **This pattern library applies ONLY to Arabic (AR) sends. Patterns here MUST NOT be applied to the other language without independent validation. See LANGUAGE-SEPARATION.md.**

> Bootstrapped from 180d of AR campaign data · updated weekly by Auditor→Analyzer
> Updated: 2026-04-16
> Source: Klaviyo `get_campaign_report` · window 2025-10-18 → 2026-04-16 · conversion metric = Placed Order (`RFkPcF`) · timezone Asia/Amman

---

## Method (AR cohort only)

- **Corpus:** AR-only subset of the 186 sent email campaigns in the last 180 days, all ≥100 recipients. AR cohort is the majority of the corpus — large-segment AR alone is n=95.
- **Signals pulled:** recipients, open_rate, click_rate, conversion_rate, conversion_value, revenue_per_recipient, unsubscribe_rate, spam_complaint_rate.
- **Clustering dimensions (within AR):** subject style (question / statement / curiosity / urgency / emoji, non-exclusive) · subject length (≤20 / 21–35 / 36–50 / 50+ chars) · segment size (small <1k · medium 1–3k · large 3k+) · send day-of-week · send hour bucket (morning 5–12 · afternoon 12–17 · evening 17–22 · late 22–5).
- **Scoring rubric (AUDITOR.md §2):** Composite 0–100 from open / CTR / conversion / revenue / inverse-unsub. 🟢 ≥75 · 🟡 50–74 · 🔴 <50.
- **Confidence:** `high` n≥20 · `medium` n=10–19 · `low` n<10 (flagged hypothesis only).
- **AR baseline (weighted across AR cohort):** conservatively at or slightly below the blended 0.31 SAR RPR; AR large-segment RPR sits at 0.26 SAR, and AR subject-length buckets sit between 0.14–0.32 RPR.
- **Language detection:** Arabic script in subject → AR; else the campaign-name tag (`| Arabic |`) is used.
- **Caveat:** Subject-style clusters only cover the AR campaigns where the API returned subject text (most recent 90-ish days). Older AR campaigns count in segment/send-time clusters but not subject-style clusters.
- **Emoji rule (AR-specific):** NO emoji in AR subjects. Emoji reads as "promotional blast" in Hijazi voice and the bootstrap sweep showed AR emoji subjects hurt open (-4pp) and RPR (-42%). This rule is independent of the EN emoji rule — do NOT port EN emoji findings here.

---

## 🟢 Proven winners (T4+ confidence, n≥10 within AR)

_None at T4+ confidence within the AR cohort today._

The AR corpus has one high-n cluster (AR × large segment, n=95) but it grades 🟡 because creative is inconsistent. No AR cluster with n≥10 currently clears the 🟢 composite ≥75 bar on a standalone-AR basis. This is itself the most important AR finding: **AR has no proven winner yet. Every AR recommendation below is either mixed or a hypothesis.**

The founding audit's conclusion stands: **AR creative (voice/framework) is the bottleneck.** Fix the voice first (see `ar/VOICE-PROFILE-AR.md`), then re-score.

---

## 🟡 Mixed / needs test (n≥10 but inconsistent)

### 1. AR × large segment (3k+) — 🟡 MIXED
- **Criteria:** lang=AR, recipients 3,000+.
- **Sample size:** n=95 (high confidence — this is the largest single AR cluster).
- **Metrics:** Open **63.2%** · CTR 0.15% · Conv 0.018% · RPR **0.26 SAR** · Unsub **0.105%** (at the 🟡/🔴 border).
- **Verdict:** this cluster contains BOTH the 48 zero-revenue sends AND the top AR performers (e.g., March 26 `Be Your Own Kind of Beautiful` RPR 1.46). The list is warm — opens are strong — but creative is inconsistent. Unsub rate sits at the 🟡 ceiling because of the Eid / Post-Ramadan unsub spikes (1.32% and 0.77%) pulling the average.
- **Proposed test:** A/B on every future AR large-segment send: (a) apply `engaged_30d` gate (`RS4wxS`) vs (b) current audience. Expected: +30–60% RPR on gated variant; unsub cut in half.

### 2. AR subject length 36–50 chars — 🟡 MIXED
- **Criteria:** lang=AR, subject 36–50 chars.
- **Sample size:** n=24 (high).
- **Metrics:** Open 55.4% · CTR 0.15% · RPR 0.15 SAR · Unsub 0.11%.
- **Verdict:** below AR baseline; the 21–35 AR bucket (n=21) isn't meaningfully better (RPR 0.19, unsub 0.19%). AR subject length is not yet carrying signal — all AR subject-length buckets underperform.
- **Proposed test:** take a short Hijazi-voice AR subject (≤25 chars, peer register, e.g. built from `صاحبتك`) and run against the standard MSA-toned AR subject. Hypothesis: AR voice register matters more than AR length.

---

## 🔴 Proven losers (n≥10 within AR, consistent underperformance)

### 3. Large AR full-list sends around Eid / post-holiday — 🔴 KILL (already escalated)
- **Criteria:** large AR broadcasts without segment gate on or around a holiday transition.
- **Sample size:** n=6 with unsub >0.4% in the window (cluster flagged as a kill pattern despite n<10 because the severity — unsub 6.5× the deliverability floor — is itself the signal).
- **Metrics:** Average RPR 0.16, average unsub **0.65%** (6.5× the 🚨 floor).
- **Examples:** Mar 20 Eid Mubarak (unsub 1.32%), Mar 24 Post Ramadan (0.77%), Mar 18 ends tonight (0.46%).
- **Recommendation:** **kill the pattern.** Freeze untargeted AR broadcasts during holiday windows. Apply `engaged_30d` exclusion at minimum. Already in audit queue; this confirms with n.

---

## Hypotheses (n<10 — not yet patterns)

| Hypothesis | Cluster criteria | n | Observed | Needs |
|---|---|---|---|---|
| Subjects 50+ chars outperform in AR | AR, subject 50+ chars | 5 | RPR 0.32, open 68.9% (best AR length bucket) | Counter-intuitive but repeatable? Test 5 more long-form AR subjects |
| Short Hijazi peer-register AR subject wins | AR, ≤25 chars, peer register (`صاحبتك`) | 0 observed | hypothesis only — no sends match criteria yet | Ship 10+ AR sends with short Hijazi subjects and score |

---

## Segment × revenue efficiency (AR cohort only)

AR revenue per recipient by segment size cluster. Note: the original corpus-wide table showed small n=82 and medium n=2 — both of which were EN cohort. AR cohort, therefore, has no observed small- or medium-segment sends in the 180d window.

| Segment size | n (AR) | RPR | Notes |
|---|---|---|---|
| small (<1k) | **0** | — | **Data gap: no AR small-segment sends in window.** Build an AR engaged-30d or AR VIP segment and start measuring. |
| medium (1k–3k) | **0** | — | **Data gap: no AR medium-segment sends in window.** The founding audit open question — "should we build an AR VIP segment equivalent to the EN engaged mid-segment?" — remains open; AR side has zero data. |
| large (3k+) | 95 | 0.26 SAR | Only AR cluster with real data. 🟡 mixed per cluster #1 above. |

**Winner:** none yet — AR currently has only the large-segment sample. **The single biggest AR program gap** is the absence of any small/medium AR segment data. Without building an AR engaged or AR VIP segment and running sends through it, AR has no upside lever to pull.

---

## Send-time × open heatmap (AR cohort only)

**Data gap:** the 180d send-time heatmap was computed on the blended (AR+EN) corpus. Per LANGUAGE-SEPARATION.md §5, send-time patterns do NOT cross languages — AR Sat-evening may differ from EN Sat-evening. Until the heatmap is re-computed on the AR cohort alone, **there are no AR-specific proven send-time slots.**

Interim guidance (hypothesis, needs AR-only re-scoring):
- AR large-segment sends have historically clustered on evenings 17–22 Asia/Amman, but this is habit, not measured AR-specific lift.
- AR send-time recommendations are **not to be ported from the blended heatmap or from the EN pattern library** until AR-only re-scoring is complete.

**Action for next weekly refresh:** Auditor to emit an AR-only heatmap (DOW × hour · AR cohort only) and feed it back into this file.

---

## Cross-cluster insights (within AR)

1. **AR has no proven winner.** This is the headline. Every AR recommendation in the library is 🟡 mixed or hypothesis-grade. Campaign Agent must treat every AR send as a test, not as a template.

2. **AR voice is the bottleneck, not AR length.** All four AR length buckets sit in RPR 0.14–0.32; the 50+ char bucket (n=5) is marginally best. The lift is not going to come from tweaking AR subject length — it is going to come from rewriting AR broadcasts into Seham's Hijazi peer-register voice (see `ar/VOICE-PROFILE-AR.md`).

3. **Holiday broadcasts to ungated AR list are the single biggest AR deliverability risk.** 6 AR sends · avg unsub 0.65%. Agent policy must treat any send marked "Eid / Ramadan / Post-Ramadan / Holiday" + segment-type=large + lang=AR as a blocked pattern requiring explicit engaged-30d gate or founder override.

4. **The AR program is running blind on segment size and send-time.** No small-segment AR data. No medium-segment AR data. No AR-only heatmap. Until these gaps close, every AR "best practice" is under-evidenced.

5. **Open rate is NOT predictive of revenue in AR either.** The AR large cluster opens at 63.2% (strong) but converts at 0.018% and RPR 0.26 SAR (weak). Stop optimizing AR subject lines for open; the AR list already opens. Every AR test must measure CTR and RPR.

6. **AR unsubscribe baseline: 0.105% (AR large-segment cluster).** Do NOT use the blended 0.10% as the AR baseline — AR unsub sits slightly higher and is pulled by holiday spikes. Flag any AR send above 0.20% unsub as a review candidate.

---

## Version

v1 · 2026-04-16 · split from `patterns.md` v1 per LANGUAGE-SEPARATION.md · AR cohort only · next refresh Sunday 2026-04-19 09:00 Asia/Amman with Auditor weekly cycle.
