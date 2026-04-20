# Zen Hair · Flows Performance Log

**Account:** متجر زن هير (WARVNh) · SAR · Asia/Amman
**Conversion metric:** Placed Order (`RFkPcF`)
**Cadence:** Weekly snapshot (last_7_days) · Monthly rollup (last_30_days)
**Purpose:** Build a longitudinal record of flow performance so we can (a) catch regressions fast and (b) learn which subject/content/cadence changes actually move the needle.

---

## How to use this log

1. **Weekly (Mondays):** run `klaviyo_get_flow_report` with `timeframe: last_7_days` for all live flows. Append a new row under the weekly section per flow.
2. **Monthly (1st of month):** run same with `last_30_days`. Append under monthly section.
3. **When a [RG] flow swaps into live:** add a "swap event" note with date + pre-swap 30d baseline so we can measure lift.
4. **Alerts (act same day):**
   - Open rate drop > 5pp WoW
   - Bounce rate > 3%
   - Unsubscribe rate > 0.5%
   - Spam complaint rate > 0.1% → **pause flow**

---

## 2026-04-19 · 30-day baseline snapshot

All [FINAL] live Arabic flows. This is the pre-[RG]-swap baseline — the yardstick we measure rebuilt flows against.

| Flow | ID | Recipients | Open rate | Click rate | Conv rate | RPR (SAR) | Notes |
|------|-----|-----------:|----------:|-----------:|----------:|----------:|-------|
| AM · AR · Welcome | `RpUXJv` | 1,773 | 27.25% | — | — | 2.88 | Largest volume |
| AM · AR · Customer Thank You | `UcxCCH` | 80 | 43.59% | — | — | — | Small sample, strong open |
| AM · AR · Browse Abandonment | `VKsTPF` | 1,435 | 29.78% | — | — | 2.81 | Baseline for `WKnDMV` swap |
| AM · AR · Site-abandonment | `UQqPVR` | 254 | 24.59% | — | — | — | Weakest open rate — investigate |
| AM · AR · Abandoned Cart | `Xkg5DZ` | 612 | 37.10% | — | — | 3.66 | Best RPR |
| AM · AR · Abandoned Checkout | `Xu8gx8` | 213 | 32.06% | — | — | — | Baseline for `TEkrGC` swap |
| AM · AR · Fulfilled Order | `Ugfkcj` | — | — | — | — | — | Transactional — excluded from perf tracking |
| AM · AR · Referral | `TqHqU2` | 923 | 32.75% | — | — | — | |

**Portfolio-level observations (baseline):**
- Overall opens 24–44% — healthy for Arabic re-engagement market
- Abandoned Cart (`Xkg5DZ`) is the RPR leader at 3.66 SAR/recipient — the format to protect
- Site-abandonment (`UQqPVR`) is the weakest open-rate performer — candidate for rebuild after Checkout + Browse + Welcome + Thank You swaps land
- Welcome (`RpUXJv`) drives the most volume — subject/content changes here have the largest absolute revenue impact

---

## Swap events

_(Log each [RG] → [FINAL] replacement here with pre-swap and post-swap 30d metrics.)_

| Date | Flow swapped | Old ID | New ID | Pre-swap 30d open | Pre-swap 30d RPR | Post-swap 30d open | Post-swap 30d RPR | Verdict |
|------|--------------|--------|--------|------------------:|-----------------:|-------------------:|------------------:|---------|
| _TBD_ | Browse Abandoned | `VKsTPF` | `WKnDMV` | 29.78% | 2.81 | — | — | pending |
| _TBD_ | Abandoned Checkout | `Xu8gx8` | `TEkrGC` | 32.06% | — | — | — | pending |
| _TBD_ | Welcome | `RpUXJv` | `UeYeck` | 27.25% | 2.88 | — | — | pending |
| _TBD_ | Thank You / Post-Purchase | `UcxCCH` | `QSFHaw` | 43.59% | — | — | — | pending |

---

## Weekly snapshots

### Week of 2026-04-20

| Flow | ID | Recipients | Open | Click | Conv | RPR | Δ open vs prior |
|------|----|-----------:|-----:|------:|-----:|----:|-----------------|
| AM · AR · Browse Abandonment | `VKsTPF` | 465 | 27.74% | 1.08% | 0.22% | 2.22 | -0.37pp |
| AM · AR · Welcome | `RpUXJv` | 317 | 24.92% | 0.63% | 0.00% | — | +0.76pp |
| AM · AR · Referral | `TqHqU2` | 234 | 30.34% | 1.28% | 0.00% | — | +1.44pp |
| AM · AR · Abandoned Cart | `Xkg5DZ` | 172 | 29.65% | 0.00% | 0.00% | — | -0.51pp |
| AM · AR · Abandoned Checkout | `Xu8gx8` | 92 | 36.96% | 1.09% | 0.00% | — | +2.98pp |
| AM · AR · Site-abandonment | `UQqPVR` | 51 | 25.49% | 0.00% | 0.00% | — | +1.35pp |
| AM · AR · Customer Thank You | `UcxCCH` | 19 | 31.58% | 0.00% | 0.00% | — | -1.75pp |

### Week of 2026-04-19

| Flow | ID | Recipients | Open | Click | Conv | RPR | Δ open vs prior |
|------|----|-----------:|-----:|------:|-----:|----:|-----------------|
| AM · AR · Browse Abandonment | `VKsTPF` | 523 | 28.11% | 1.15% | 0.19% | 1.97 | — |
| AM · AR · Welcome | `RpUXJv` | 356 | 24.16% | 0.56% | 0.00% | — | — |
| AM · AR · Referral | `TqHqU2` | 256 | 28.91% | 1.17% | 0.00% | — | — |
| AM · AR · Abandoned Cart | `Xkg5DZ` | 189 | 30.16% | 0.53% | 0.00% | — | — |
| AM · AR · Abandoned Checkout | `Xu8gx8` | 103 | 33.98% | 1.94% | 0.00% | — | — |
| AM · AR · Site-abandonment | `UQqPVR` | 58 | 24.14% | 0.00% | 0.00% | — | — |
| AM · AR · Customer Thank You | `UcxCCH` | 21 | 33.33% | 0.00% | 0.00% | — | — |

_(Append newest on top. Format: one table per week.)_

### Week of YYYY-MM-DD

| Flow | ID | Recipients | Open | Click | Conv | RPR | Δ vs prior week |
|------|-----|-----------:|-----:|------:|-----:|----:|-----------------|
| _first snapshot pending_ | | | | | | | |

---

## Monthly rollups

_(Append newest on top.)_

### 2026-04 (baseline captured 2026-04-19)

See "30-day baseline snapshot" above.

---

## Learnings · running notes

_(Anything we decide based on the numbers goes here, dated. One line per insight.)_

- `2026-04-20` (auto-digest)
  - Biggest open-rate gain: **AM · AR · Abandoned Checkout** +2.98pp (33.98% → 36.96%).
  - Biggest open-rate drop: **AM · AR · Abandoned Cart** -0.51pp (30.16% → 29.65%).
  - Biggest RPR gain: **AM · AR · Browse Abandonment** +0.25 SAR (1.97 → 2.22).
  - Watch: **AM · AR · Site-abandonment** bounce 5.88% (threshold 3.0%) — approaching limit.
- `2026-04-19` — Baseline captured. Browse Abandoned `VKsTPF` at 29.78% open / 2.81 RPR is the bar `WKnDMV` must clear. Hypothesis: curiosity-gap E2 subject (`مو متأكدة وش يناسبكِ؟`) + Smart Sending OFF should lift opens on mid-flow emails where legacy got suppressed by the 16h dedupe window.
