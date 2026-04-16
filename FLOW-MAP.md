# Zen Hair · Klaviyo Flow Map (Live)

> **Source:** Pulled from Klaviyo API on 2026-04-16.
> **Account:** متجر زن هير (WARVNh) · SAR · Asia/Amman · sender: سهام من زن هير <info@zenhairshop.com>

---

## 🟢 Live Arabic Flows

| Flow | ID | Trigger | Purpose |
|---|---|---|---|
| **Welcome Flow (Arabic)** | `RpUXJv` | Added to List | Subscriber onboarding · Welcome E1–E4 |
| **Customer Thank You Flow (Arabic)** | `UcxCCH` | Metric | Post-purchase · **TY #1–#8 live here** |
| **Referral Flow (Arabic)** | `TqHqU2` | Metric | Referral program · legacy |
| **Browse Abandonment (Arabic)** | `VKsTPF` | Metric | Browsed but didn't add to cart |
| **Site-abandonment (Arabic)** | `UQqPVR` | Metric | Entered site but didn't engage |
| **Abandoned Cart (Arabic)** | `Xkg5DZ` | Metric | Added to cart but didn't checkout |
| **Abandoned Checkout (Arabic)** | `Xu8gx8` | Metric | Reached checkout but didn't pay |
| **Fulfilled Order (Arabic)** | `Ugfkcj` | Metric | Post-shipment notifications |

## 🔴 English Flows (archive candidates)

| Flow | ID | Status |
|---|---|---|
| Welcome Flow (English) | `XVkXi4` | Live · archive? |
| Site-abandonment (English) | `RTdRCz` | Live · archive? |
| Browse Abandonment (English) | `SnVUkb` | Live · archive? |
| Abandoned Checkout (English) | `Y6saqP` | Live · archive? |

## ⚠ Drafts to delete

| Flow | ID |
|---|---|
| Essential Flow Recommendation_ | `SbGFTW` |
| Essential Flow Recommendation_ | `U8aHXY` |

---

## Flow-to-Template Assignment (TY flow · UcxCCH)

| Step | Day | Template | Klaviyo ID | Status |
|---|---|---|---|---|
| 1 | +1 | ty-1 Arrival | Xa8dGZ | ready to assign |
| 2 | +4 | ty-2 Care guide | WJ9rUe | ready to assign |
| 3 | +8 | ty-3 Video how-to | Th8rtT | ready to assign |
| 4 | +25 | ty-5 Review ask | Spp7Kh | ready to assign |
| 5 | +40 | ty-6 Ponytail cross-sell | QS3vmG | ready to assign |
| 6a | +60 | ty-7a Second set (IF repeat) | TwisrJ | ready to assign · needs conditional split |
| 6b | +60 | ty-7b Referral (IF one-timer) | Y5SMxB | rework pending |
| 7 | +90 | ty-8 Check-in | TKmHq7 | ready to assign |

**⚠ Needs computer-use:** Assigning these 8 templates to the 8 nodes in `UcxCCH` — Klaviyo MCP cannot do this, only the UI can.

---

## Recommended Segments to Create (missing)

For current work we need three new segments. None exist yet.

| Segment Name | Purpose | Definition |
|---|---|---|
| `Placed Order · last 90d` | Ponytail Launch target | `Placed Order` count ≥ 1 in last 90 days + consented email |
| `Repeat Buyers` | TY Flow split at Day 60 | `Placed Order` count ≥ 2 all-time + consented email |
| `One-time Buyers at 60d` | TY Flow split at Day 60 | `Placed Order` count = 1 AND first order ≥ 60 days ago + consented email |

**Creation path:** Klaviyo API does NOT expose segment creation. Two options:
1. Chrome MCP + authenticated session → `/ajax/dynamic-group` POST (per MEMORY.md note)
2. Manual creation in Klaviyo UI (5 min each)

---

## Existing Segments (pulled from API)

| Segment | ID | Purpose |
|---|---|---|
| VIP Customers | `SdJBtU` | Placed Order > 5 all-time |
| Potential Purchasers | `RAHyRh` | Viewed Product recently, no purchase |
| AI \| Target \| Engaged 30 Days | `RS4wxS` | Opened + clicked in last 30d |
| AM \| Exclude \| Suppressed | `QPaQg2` | Bounce/unsubscribe suppression |
| AM \| Exclude \| Unengaged | `R7n5YH` | 10+ sends, 0 opens/clicks |
| AM \| Exclude \| Suppress | `RQvExN` | 5+ sends, 0 engagement in 90d |
| AM \| Exclude \| Clean #4 | `RraB6N` | Deep-clean aged profiles |
| AM \| Exclude \| Bounced | `S2hTN3` | Hard/soft bounce threshold |
| AM \| Exclude \| Jobs | `Sd3G5T` | jobs@ / careers@ / hr@ / recruit@ |
| AM \| Exclude \| Noreply | `Sh5GnV` | noreply@ addresses |

The `AM | Exclude | *` segments should be stacked in every campaign as **suppression filters**.

---

## Standard Campaign Suppression Stack

For every campaign, suppress:
- `QPaQg2` AM | Exclude | Suppressed
- `R7n5YH` AM | Exclude | Unengaged
- `RQvExN` AM | Exclude | Suppress
- `RraB6N` AM | Exclude | Clean #4
- `S2hTN3` AM | Exclude | Bounced
- `Sd3G5T` AM | Exclude | Jobs
- `Sh5GnV` AM | Exclude | Noreply

This protects sender reputation across every send.
