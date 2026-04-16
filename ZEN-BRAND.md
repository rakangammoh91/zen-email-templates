# Zen Hair · Brand Brain

> **Status:** Awaiting guidelines from founder. When you fill this in, the agent never asks brand questions again.
> **Last updated:** 2026-04-16

---

## 1. Company

- **Name:** Zen Hair (زن هير) · Klaviyo org: "متجر زن هير"
- **Klaviyo account:** `WARVNh`
- **Market:** Saudi Arabia (primary) · GCC (secondary)
- **Category:** Ecommerce · Health & Beauty · Haircare (premium human-hair extensions)
- **Founder / Voice:** Seham (سهام) — female co-founder, writes in first person
- **Website:** https://www.zenhairshop.com · Shopify backend: zenhair-shop.myshopify.com
- **WhatsApp CS:** +966 11 510 7044
- **IG:** @zenhairshop
- **Sender name:** سهام من زن هير
- **Sender email:** info@zenhairshop.com
- **Currency:** SAR
- **Timezone:** Asia/Amman

---

## 2. Voice & Tone

- **Dialect:** Saudi Hijazi (NOT MSA)
- **Signature words:** قوليلي · خلّيني · وصلكِ · خبّريني · تعالي · عشان · مو · بس · الحين · ترى
- **POV:** Always first-person Seham, never "we" corporate
- **Warmth level:** High — writes like a friend, not a brand
- **Forbidden tone:** Formal MSA · corporate jargon · discount-shouting (SALE!!!)

### Fill-in (TODO by founder)
- [ ] 3 words that describe the brand voice: ________________
- [ ] 3 words we NEVER want to sound like: ________________
- [ ] Signature phrases unique to Seham: ________________
- [ ] Things Seham would never say: ________________

---

## 3. Visual Tokens (locked)

```
Background        #fafaf8   (warm off-white)
Ink               #1c1d1d   (near-black)
Gold accent       #ffd430   (highlight / numerals / dividers)
WhatsApp green    #25D366   (CTA only)
Muted text        #7c6f50   (taupe · meta · P.S.)
Secondary ink     #3d3e43
Divider line      #e5e5e5
```

- **Font:** Tajawal (Google Fonts) · fallback -apple-system, Segoe UI, Tahoma, Arial
- **Direction:** RTL (`dir="rtl"`, `lang="ar"`)
- **Container widths:**
  - 560px = intimate / letter-style (TY #1, TY #8, Welcome founder voice)
  - 600px = standard product emails (TY #2, #3, #5, #6, #7a, #7b)
- **Button:** `border-radius: 100px` · padding 18–20px × 40–56px
- **H1:** 40–48px · weight 500 · letter-spacing -1.2 to -1.5px
- **Body:** 17–18px · line-height 1.9

---

## 4. Product Catalog

### Fill-in (TODO by founder)
- [ ] Current SKUs (name, price, stock status): ________________
- [ ] Color families offered: ________________
- [ ] Lengths offered: ________________
- [ ] Bestseller: ________________
- [ ] New arrival (ponytail / بوني تيل): on roadmap — TY #6 live

---

## 5. Customer Profile

### Fill-in (TODO by founder)
- [ ] Age bracket: ________________
- [ ] Income bracket: ________________
- [ ] Primary purchase trigger (wedding / daily / post-pregnancy / thinning): ________________
- [ ] Top 3 objections before buying: ________________
- [ ] Top 3 compliments after buying: ________________

---

## 6. Commercial Rules

- **Delivery window:** 2–4 days KSA via Aramex (per MEMORY.md)
- **Prices on waybills:** Low declared values, NEVER Shopify retail (per MEMORY.md)
- **Address source of truth:** WhatsApp-confirmed, NOT Shopify field (per MEMORY.md)
- **CS messaging channel:** Telegram (migration in progress, not WhatsApp)

---

## 7. Referral Mechanic (TY #7b)

- **Approach:** Unique discount code per customer (no app installed)
- **Code format:** TBD by founder — e.g. `SARAH150`
- **Value to friend:** 150 SAR off first order
- **Value to customer:** TBD — one-sided (gift framing) OR two-sided (manual credit when friend ships)
- **Fulfillment:** Manual — Seham issues codes via CS

### Fill-in (TODO by founder)
- [ ] One-sided or two-sided? ________________
- [ ] Code generation: manual per customer, or predictable pattern? ________________
- [ ] Landing page URL (if any): ________________

---

## 8. Flow Map

### Post-Purchase Thank You Flow
Trigger: Placed Order · Cohort: All buyers · Split at Day 60

| # | Day | Purpose | Klaviyo ID |
|---|-----|---------|-----------|
| 1 | +1 | Arrival reassurance | Xa8dGZ |
| 2 | +4 | Care guide (3 mistakes) | WJ9rUe |
| 3 | +8 | How-to-wear video | Th8rtT |
| 4 | — | DELETED (UGC ask) | — |
| 5 | +25 | Written review ask | Spp7Kh |
| 6 | +40 | Ponytail cross-sell | QS3vmG |
| 7a | +60 | Second set (if repeat buyer) | TwisrJ |
| 7b | +60 | Referral 150+150 (if one-timer) | Y5SMxB ⚠ rework pending |
| 8 | +90 | Check-in (no ask) | TKmHq7 |

### Welcome Flow (v10 · in progress)
| # | Trigger | Purpose | Klaviyo ID |
|---|---------|---------|-----------|
| E1 | Subscribe | Hello + brand intro | TBD |
| E2 | +2d | Product education | TBD |
| E3 | +4d | Founder story (سهام) | TODO |
| E4 | +7d | Founder demo (شعري أنا) | TODO |

### One-time Campaigns
- [ ] Ponytail Launch (broadcast to 90d buyers)

---

## 9. Segments (Klaviyo)

### Fill-in (TODO)
- [ ] "Placed Order last 90d" segment ID: ________________
- [ ] "Repeat buyers" segment ID: ________________
- [ ] "One-timers at Day 60" segment ID: ________________
- [ ] "Active subscribers (EN)" — archive target: ________________
- [ ] "Active subscribers (AR)": ________________

---

## 10. Archive / Cleanup Queue

- [ ] Legacy Abandoned Cart flow — archive
- [ ] English dormant flows — archive
- [ ] Old template versions post-rework (TY #7b Y5SMxB will be superseded)
