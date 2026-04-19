# Zen Hair · Flows Registry

**Account:** متجر زن هير (WARVNh) · SAR · Asia/Amman
**Sender:** `سهام · زن هير` <info@zenhairshop.com>
**Last sync:** 2026-04-19

---

## [RG] Rebuilt Arabic flows (our work)

| Flow | ID | Status | Trigger | Emails | Doc | Last updated |
|------|-----|--------|---------|--------|-----|--------------|
| **[RG] AR · Browse Abandoned** | `WKnDMV` | Draft | Viewed Product | 4 (T+4h · T+24h · T+72h · T+5d) | [spec](browse-abandoned-ar-flow-v1-spec.md) | 2026-04-19 |
| **[RG] AR · Abandoned Checkout** | `TEkrGC` | Draft | Checkout Started | 4 (T+1h · T+24h · T+48h · T+72h) | [spec](abandoned-checkout-flow-v1-spec.md) | 2026-04-18 |
| **[RG] AR · Welcome · Founder Voice** | `UeYeck` | Draft | Added to List | 5 (W1–W5) | — | 2026-04-18 |
| **[RG] AR · Post-Purchase** | `QSFHaw` | Draft | Placed Order | — | — | 2026-04-19 |

## [FINAL] Live Arabic flows (legacy — monitored, will be replaced)

| Flow | ID | Status | Trigger | Replacement | Replace after |
|------|-----|--------|---------|-------------|---------------|
| AM · AR · Welcome | `RpUXJv` | Live | Added to List | [RG] `UeYeck` | Draft → QA → swap |
| AM · AR · Customer Thank You | `UcxCCH` | Live | Metric | [RG] `QSFHaw` | Build + QA |
| AM · AR · Browse Abandonment | `VKsTPF` | Live | Metric | [RG] `WKnDMV` | QA → swap |
| AM · AR · Site-abandonment | `UQqPVR` | Live | Metric | TBD | — |
| AM · AR · Abandoned Cart | `Xkg5DZ` | Live | Metric | TBD | — |
| AM · AR · Abandoned Checkout | `Xu8gx8` | Live | Metric | [RG] `TEkrGC` | QA → swap |
| AM · AR · Fulfilled Order | `Ugfkcj` | Live | Metric | — | — |
| AM · AR · Referral | `TqHqU2` | Live | Metric | — | — |

## Legacy English (archive candidates)

| Flow | ID | Status |
|------|-----|--------|
| AM · EN · Welcome | `XVkXi4` | Live · archive |
| AM · EN · Site-abandonment | `RTdRCz` | Live · archive |
| AM · EN · Browse Abandonment | `SnVUkb` | Live · archive |
| AM · EN · Abandoned Checkout | `Y6saqP` | Live · archive |

## Draft clutter (delete)

| Flow | ID |
|------|-----|
| Essential Flow Recommendation_ | `SbGFTW` |
| Essential Flow Recommendation_ | `U8aHXY` |

---

## Learning cadence

- **Weekly:** Re-pull `klaviyo_get_flow_report` last_7_days → append to `flows-performance-log.md`
- **Monthly:** Compare [RG] vs [FINAL] side-by-side on open rate / CTR / conversion rate / RPR
- **Triggers to investigate:** open rate drop >5pp week-over-week, bounce rate >3%, unsubscribe rate >0.5%
- **Kill switches:** spam complaint rate >0.1% → pause flow immediately
