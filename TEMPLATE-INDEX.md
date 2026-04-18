# Template Index — Email Marketer Cheat Sheet

**Last updated:** 2026-04-18
**Location:** `ar/templates/` (all files)
**Language:** Arabic (RTL, Tajawal font)

Naming pattern: `[flow-name]-[step]-[timing]-[variant].html`
Alphabetical sort groups every flow together. Just `ls` the folder.

---

## 1. Welcome Flow (5 steps · new subscriber)

Trigger: Klaviyo list subscription. Delay between steps: see column.

| Step | File | When | Purpose |
|------|------|------|---------|
| W1 | `welcome-1-intro.html` | Immediate | Founder intro + WELCOME10 code |
| W2 | `welcome-2-bestseller.html` | +1 day | Best-seller (9-piece clip-in) |
| W3 | `welcome-3-colors.html` | +3 days | Color matching + WhatsApp help |
| W4 | `welcome-4-howto.html` | +5 days | How-to-wear / social proof |
| W5 | `welcome-5-urgency.html` | +7 days | WELCOME10 expires in 48h + referral |

**Archive (do not send):** `welcome-1-intro-archive-msa.html`, `welcome-1-intro-archive-b.html`, `welcome-1-intro-archive-c.html` — pre-A+ versions kept for reference only.

---

## 2. Abandoned Checkout Flow (4 steps × 3 variants)

Trigger: Started Checkout, no Placed Order. Pick ONE variant (v1/v2/v3) to run; A/B-test others.

| Step | Timing | v1 | v2 | v3 |
|------|--------|----|----|----|
| AC1 | +1 hour | `abandoned-checkout-1-1h-v1.html` | `abandoned-checkout-1-1h-v2.html` | `abandoned-checkout-1-1h-v3.html` |
| AC2 | +24 hours | `abandoned-checkout-2-24h-v1.html` | `abandoned-checkout-2-24h-v2.html` | `abandoned-checkout-2-24h-v3.html` |
| AC3 | +48 hours | `abandoned-checkout-3-48h-v1.html` | `abandoned-checkout-3-48h-v2.html` | `abandoned-checkout-3-48h-v3.html` |
| AC4 | +72 hours | `abandoned-checkout-4-72h-v1.html` | `abandoned-checkout-4-72h-v2.html` | `abandoned-checkout-4-72h-v3.html` |

---

## 3. Post-Purchase Flow (5 steps · first-order nurture)

Trigger: Placed Order. Day 21 and Day 28 have 20-second and 24-second video variants — pick one per step.

| Step | File | When | Purpose |
|------|------|------|---------|
| PP1 | `post-purchase-1-day1.html` | Day 1 | Order confirmation vibe |
| PP2 | `post-purchase-2-day3.html` | Day 3 | Shipping/tracking |
| PP3 | `post-purchase-3-day10.html` | Day 10 | Care tips |
| PP4 | `post-purchase-4-day21-20s.html` OR `post-purchase-4-day21-24s.html` | Day 21 | Styling video (pick one video length) |
| PP5 | `post-purchase-5-day28-20s.html` OR `post-purchase-5-day28-24s.html` | Day 28 | Second-look cross-sell |

---

## 4. Thank-You Flow (post-delivery · 8 touches over 90 days)

Trigger: Fulfilled/delivered. Day 60 has two cohort splits.

| Step | File | When | Purpose |
|------|------|------|---------|
| TY1 | `thank-you-1-day1.html` | Day 1 | Arrival reassurance |
| TY2 | `thank-you-2-day4.html` | Day 4 | Care guide |
| TY3 | `thank-you-3-day8.html` | Day 8 | How-to-wear video |
| TY4 | `thank-you-4-day16.html` | Day 16 | Styling inspo |
| TY5 | `thank-you-5-day25.html` | Day 25 | Written review ask |
| TY6 | `thank-you-6-day40.html` | Day 40 | Ponytail cross-sell |
| TY7a | `thank-you-7a-day60-repeat.html` | Day 60 | Second-set offer (repeat buyers) |
| TY7b | `thank-you-7b-day60-referral.html` | Day 60 | Referral 150+150 (one-timers) — **rework pending** |
| TY8 | `thank-you-8-day90.html` | Day 90 | Check-in |

---

## Klaviyo IDs

All Klaviyo template IDs and flow IDs are in `registry.json`. Search by filename.

## Sort Shortcut

```bash
ls ar/templates/  # alphabetical = grouped by flow
```
