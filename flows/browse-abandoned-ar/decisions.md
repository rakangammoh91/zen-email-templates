# Browse Abandoned AR · Decision log

Append-only. One entry per non-trivial decision.

---

## 2026-04-19 · E2 subject rewrite

**Problem:** Master subject was `ابعثي صورة شعركِ` (Send your hair photo) — frontloaded the ASK. Body leads with the color-match *problem*, not the action.

**Candidates considered:**

| # | Subject | Approach | Chars |
|---|---------|----------|------:|
| 1 ✅ | `مو متأكدة وش يناسبكِ؟` | Curiosity · mirrors hero | 22 |
| 2 | `١٢ لون · وحدة تناسبكِ` | Direct benefit | 20 |
| 3 | `خليني أختارلكِ اللون` | Personal help-offer | 20 |
| 4 | `أختارلكِ لونكِ · مجاناً` | Benefit + free | 22 |
| 5 | `نورة طلبت «هذا» · طلع ١٠٠٪` | Social proof | 27 |

**Winner: #1.** Mirrors hero headline exactly, reads as a friend's question, curiosity-gap outperforms direct-ask on re-engagement flows. Preview `ابعثي صورة شعركِ · أنا أختار` keeps the photo ask present as the natural next step.

---

## 2026-04-19 · Flow structural cleanup

- **Linearized** — removed legacy conditional split (no content inside, left from copy)
- **All waits corrected** to match master: 4h → 1d → 2d → 2d
- **All templates swapped in** from saved versions: XWSwwU · RWzPnQ · XjRtUh · Xdfd4e
- **Smart Sending OFF** on all 4 (was ON on E4 by template default)
- **UTM Tracking OFF** on all 4 (was ON on E1/E2/E3)

Rationale:
- Smart Sending off = Browse Abandoned is high-intent, we want every email delivered even inside the 16h dedupe window
- UTM off = GAM attribution pipeline doesn't consume Klaviyo UTMs; they pollute Shopify referrer data

---

## Pre-swap baseline (for measuring lift after go-live)

Legacy flow `VKsTPF` · 30-day snapshot on 2026-04-19:

- Recipients: 1,435
- Open rate: **29.78%**
- RPR: **2.81 SAR**

**Target for `WKnDMV` after 30 days live:** open rate ≥ 32%, RPR ≥ 3.00 SAR.
