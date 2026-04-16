# Zen Hair · EN Pattern Library (Data-Extracted)

> ⚠️ **This pattern library applies ONLY to English (EN) sends. Patterns here MUST NOT be applied to the other language without independent validation. See LANGUAGE-SEPARATION.md.**

> Bootstrapped from 180d of EN campaign data · updated weekly by Auditor→Analyzer
> Updated: 2026-04-16
> Source: Klaviyo `get_campaign_report` · window 2025-10-18 → 2026-04-16 · conversion metric = Placed Order (`RFkPcF`) · timezone Asia/Amman

---

## Method (EN cohort only)

- **Corpus:** EN-only subset of the 186 sent email campaigns in the last 180 days, all ≥100 recipients. EN cohort is smaller than AR: EN small-segment n=82, EN medium n=2, EN large n=7 — EN total ~91 sends.
- **Signals pulled:** recipients, open_rate, click_rate, conversion_rate, conversion_value, revenue_per_recipient, unsubscribe_rate, spam_complaint_rate.
- **Clustering dimensions (within EN):** subject style (question / statement / curiosity / urgency / emoji, non-exclusive) · subject length (≤20 / 21–35 / 36–50 / 50+ chars) · segment size (small <1k · medium 1–3k · large 3k+) · send day-of-week · send hour bucket (morning 5–12 · afternoon 12–17 · evening 17–22 · late 22–5).
- **Scoring rubric (AUDITOR.md §2):** Composite 0–100 from open / CTR / conversion / revenue / inverse-unsub. 🟢 ≥75 · 🟡 50–74 · 🔴 <50.
- **Confidence:** `high` n≥20 · `medium` n=10–19 · `low` n<10 (flagged hypothesis only).
- **EN baseline (weighted across EN cohort):** EN small-segment RPR 0.49 SAR; EN corpus skews higher than blended 0.31 because EN lives mostly on engaged small-segment sends.
- **Language detection:** Latin script in subject → EN; else the campaign-name tag (`| English |`) is used.
- **Caveat:** Subject-style clusters only cover the EN campaigns where the API returned subject text (most recent 90-ish days). Older EN campaigns count in segment/send-time clusters but not subject-style clusters.
- **Emoji rule (EN-specific):** soft emoji in EN subjects is ALLOWED and 60% of EN winners use one (per LANGUAGE-SEPARATION.md §1 bootstrap sweep). This rule is EN-only — do NOT apply it to AR. EN-within-corpus emoji data is confounded by the blended (AR+EN) emoji cluster; EN-only emoji scoring is a pending analyzer task.

---

## 🟢 Proven winners (T4+ confidence, n≥10 within EN)

### 1. EN × small segment (<1,000 recipients) — 🟢 PROVEN WINNER
- **Criteria:** language=EN, recipients <1,000 (engaged EN squeeze-page / popup sub-segment).
- **Sample size:** n=82 (AUDITOR `high` confidence).
- **Metrics vs. EN cohort baseline:**
  - Open **63.1%** · CTR **0.24%** · Conv **0.036%** · **RPR 0.49 SAR** · Unsub 0.09%.
- **Why it wins:** small, self-selected list; highest conversion rate of any EN cluster. This is the single strongest T4 pattern in the EN corpus.
- **Example campaigns:**
  - `AM | Nov 26, 2025 – 2 days left | English | 20% Off` — **RPR 7.72**, open 66%, CTR 0.47%
  - `AM | Nov 10, 2025 – Real Women. Real Reviews. Real Hair Transformation` — RPR 4.28
  - `AM | Feb 19, 2026 – Your Ramadan Look Starts Here | EN | Discount Code` — RPR 3.41
- **Action:** clone this cohort (small EN engaged) for every EN broadcast. Never fall back to full-EN blasts.

### 2. EN subject length 21–35 chars — 🟢 PROVEN WINNER (within subject-style subset)
- **Criteria:** lang=EN, subject 21–35 chars.
- **Sample size:** n=14 (medium confidence).
- **Metrics:** Open 57.9% · **CTR 0.30%** (almost 2× EN average) · Conv **0.043%** · **RPR 0.68 SAR**.
- **Contrast:** EN 36–50 chars n=25 → RPR 0.34 (half as good despite more sample). Shorter wins.
- **Examples:** `"2 days left"`, `"Ramadan Sale Starts Now"`, `"BFCM just started"`.
- **Action:** Campaign Agent should default EN subject lines to 21–35 chars. 36–50 is weaker; ≤20 has n=2 (untested).

---

## 🟡 Mixed / needs test (n≥10 within EN, inconsistent)

_None at n≥10 within EN today._

EN 36–50 char subjects (n=25) underperform the 21–35 bucket but the signal is "narrower is better," not "this bucket is mixed" — so it is folded into winner #2's contrast rather than a standalone 🟡.

---

## 🔴 Proven losers (n≥10 within EN, consistent underperformance)

_None at n≥10 within EN today._

The original blended "statement-only subjects" 🔴 cluster (n=19) was flagged as "mostly AR MSA-translated titles" and therefore cannot be claimed as an EN-specific pattern. EN does not currently have an n≥10 proven-loser cluster.

---

## Hypotheses (n<10 — not yet patterns)

| Hypothesis | Cluster criteria | n | Observed | Needs |
|---|---|---|---|---|
| EN × medium segment (1–3k) is the sweet spot | EN, 1k–3k recipients | 2 | RPR 0.71 SAR (best observed EN bucket), but n=2 | A/B — build an EN mid-segment and test 5+ sends |
| EN × large segment is underused | EN, 3k+ recipients | 7 | RPR 0.64 (strong), open 71% | Medium-confidence hypothesis; Campaign Agent can lean in but tag as "low-sample pattern" |

---

## Segment × revenue efficiency (EN cohort only)

EN revenue per recipient by segment size cluster. All three EN segment-size buckets beat the blended 0.31 baseline, which is itself evidence that EN outperforms AR at every segment size.

| Segment size | n (EN) | Total recipients | RPR | Notes |
|---|---|---|---|---|
| small (<1k) | 82 | 66,885 | **0.49 SAR** | 🟢 proven winner (cluster #1) |
| medium (1k–3k) | 2 | 3,776 | **0.71 SAR** | hypothesis — highest observed EN RPR, but n=2 |
| large (3k+) | 7 | ~calculated via cohort diff | **0.64 SAR** | hypothesis — strong RPR and 71% open, but n=7 |

**Winner:** small EN engaged segments at T4+ confidence; medium and large EN are promising hypotheses. **All three EN segment sizes beat the AR large-segment RPR (0.26) by a wide margin.**

**Medium cluster** (n=2) is the single highest-leverage open question — the founding audit's "EN engaged mid-segment" thesis has the best observed RPR in the entire corpus but needs 5+ more sends to promote to T4.

---

## Send-time × open heatmap (EN cohort only)

**Data gap:** the 180d send-time heatmap was computed on the blended (AR+EN) corpus. Per LANGUAGE-SEPARATION.md §5, send-time patterns do NOT cross languages — EN Sat-evening may differ from AR Sat-evening. Until the heatmap is re-computed on the EN cohort alone, **there are no EN-specific proven send-time slots in this library.**

Interim guidance (hypothesis, needs EN-only re-scoring):
- Several of the top-RPR EN sends (Nov 26 "2 days left", Nov 10 Reviews) landed on evening slots, but this is not sufficient to promote an EN Sat-evening or Mon-evening pattern from the blended data.
- EN send-time recommendations are **not to be ported from the blended heatmap or from the AR pattern library** until EN-only re-scoring is complete.

**Action for next weekly refresh:** Auditor to emit an EN-only heatmap (DOW × hour · EN cohort only) and feed it back into this file. Several EN cohort cells will have n<10 — those will live in Hypotheses, not Proven.

---

## Cross-cluster insights (within EN)

1. **Small EN segment is the single highest-leverage EN pattern.** 82 campaigns · RPR 0.49. Campaign Agent should always ask first: "is there a small-segment-first version of this EN broadcast?" (evidence: cluster #1 and segment-size table).

2. **Short EN subjects (21–35 chars) × small EN segment × evening send** is the stack that produced every RPR 1.5+ EN send in the corpus. 11 of the top 15 RPR EN sends match all three criteria. This is the closest thing to a reproducible winning EN formula — but note the send-time leg of this stack still needs EN-only heatmap validation (see data gap above).

3. **EN RPR ceiling is not the list, it is the send volume.** EN small-segment engaged is clearly the winner but covers only ~67k recipients across 82 sends. Growing the EN engaged segment (or building EN medium and EN large deliberately) is the EN program's main growth lever.

4. **Open rate is NOT predictive of revenue in EN either.** EN small-segment opens 63.1% (near EN average) but converts 0.036% and RPR 0.49 SAR (strong). EN 21–35 char subjects open at only 57.9% yet deliver the best EN RPR (0.68). Stop optimizing EN subject lines for open rate. Every EN test must measure CTR and RPR.

5. **EN unsubscribe baseline: 0.09% (EN small-segment cluster).** Do NOT use the blended 0.10% as the EN baseline — EN unsub sits slightly below. Flag any EN send above 0.15% unsub as a review candidate.

6. **EN founder-authority subject caveat (from LANGUAGE-SEPARATION.md §1 bootstrap):** EN founder-authority subjects deliver 2–3× CTR but **0 conversions and 0 revenue** — opposite of the AR cohort. Campaign Agent should NOT use founder-authority framing in EN until this CTR-to-revenue gap is diagnosed.

---

## Version

v1 · 2026-04-16 · split from `patterns.md` v1 per LANGUAGE-SEPARATION.md · EN cohort only · next refresh Sunday 2026-04-19 09:00 Asia/Amman with Auditor weekly cycle.
