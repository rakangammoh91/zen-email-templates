# Abandoned Checkout Flow v1 — Build Spec

**Owner:** Growth / Lifecycle
**Created:** 2026-04-15
**Status:** Templates shipped to Klaviyo · Flow wiring + Shopify config pending ops build

---

## 1. Strategy summary

9-fig DTC escalation curve — **soft → social proof → friction kill → discount**. Single path (no cart-value branch). WhatsApp runs in parallel as concierge layer, not as a separate flow branch.

| Email | T+ | Subject (AR) | Primary CTA | Discount? | Color |
|-------|----|----|----|----|----|
| #1 The Nudge | +1h | شي نسيتيه؟ | أكمل طلبي ← | ❌ | Black |
| #2 Objection Crusher | +24h | ٤.٨ ★ من ١٥,٠٠٠ تقييم | أرجع لسلّتي ← | ❌ | Black |
| #3 Friction Kill | +48h | شحن مجاني · إرجاع ١٤ يوم | كلّمي خبيرتنا على واتساب | ❌ | **Green #25D366** |
| #4 Last Call | +72h | ٢٤ ساعة · ١٠٪ + هدية مجانية | أستخدم كودي ← (SAVE10) | ✅ 10% + gift | Black + green secondary |

**Why no discount for 72 hours?** Protects margin and doesn't train full-price buyers to wait. 60–70% of abandoners recover before discount fires.

---

## 2. Klaviyo flow — template IDs

| Step | Klaviyo Template ID | File |
|----|----|----|
| AC #1 | `US56fq` | `templates/ac-1-final.html` |
| AC #2 | `TshYgu` | `templates/ac-2-final.html` |
| AC #3 | `SvmaiD` | `templates/ac-3-final.html` |
| AC #4 | `ViwC4y` | `templates/ac-4-final.html` |

---

## 3. Klaviyo flow wiring

### Trigger
- **Metric:** `Checkout Started` (Shopify)
- **Additional filter:** `Started Checkout at least 1 time in the last 30 days`

### Flow filters (apply globally to the whole flow)
- `Placed Order zero times since starting this flow` — exits the profile the moment they buy
- `Has email` is true
- `Can receive marketing` is true
- Exclude profiles in segment: `Active customers last 30 days` (optional, reduces annoyance to repeat buyers mid-cart)

### Sequence
```
[Trigger: Checkout Started]
    ↓
[Wait 1 hour]
    ↓
[Email: AC #1 · US56fq · Subject: شي نسيتيه؟]
    ↓
[Wait 23 hours]   ← brings total to T+24h
    ↓
[Email: AC #2 · TshYgu · Subject: ٤.٨ ★ من ١٥,٠٠٠ تقييم]
    ↓
[Wait 24 hours]   ← T+48h
    ↓
[Email: AC #3 · SvmaiD · Subject: شحن مجاني · إرجاع ١٤ يوم]
    ↓
[Wait 24 hours]   ← T+72h
    ↓
[Email: AC #4 · ViwC4y · Subject: ٢٤ ساعة · ١٠٪ + هدية مجانية]
    ↓
[End of flow]
```

### Smart Sending
- Enable **Smart Sending** on all 4 emails (prevents sending if they received another campaign/flow in the last 16h).

### Send time
- **No quiet-hours restriction** (AC is time-sensitive). If concerned about Saudi overnight sends, enable quiet hours 00:00–07:00 AST.

### Subject / preview text
All subjects + preview text are set inside the Klaviyo template — no extra configuration needed at the flow step level.

---

## 4. Shopify SAVE10 config (critical — must be built BEFORE flow goes live)

The flow's #4 email promises **10% off + free mystery gift worth SAR 70**. This requires **TWO Shopify discounts that stack**:

### Discount A — `SAVE10` (code-based, 10% off)
| Field | Value |
|---|---|
| Method | **Discount code** |
| Code | `SAVE10` |
| Type | Percentage |
| Value | `10%` |
| Applies to | Entire order |
| Minimum purchase | None (or SAR 299 if you want to protect smallest-cart margin) |
| Customer eligibility | All customers |
| Usage limits | ✅ Limit to one use per customer · ❌ no total limit |
| **Combinations** | ✅ **Allow "Buy X Get Y" discounts to combine with this code** |
| Active dates | Indefinite (you'll archive old codes quarterly) |

### Discount B — Free Gift (automatic, Buy X Get Y)
| Field | Value |
|---|---|
| Method | **Automatic discount** |
| Name (internal) | `AC4 Free Gift — Mystery SAR 70` |
| Type | Buy X get Y |
| Customer buys | **Any product** · quantity `1` · minimum purchase `SAR 299` (or match your AC recovery threshold) |
| Customer gets | **1 of** [select mystery gift product] · at **100% off** |
| Set maximum uses per order | `1` |
| Customer eligibility | All customers |
| **Combinations** | ✅ **Allow "Discount codes" to combine with this automatic discount** |
| Active dates | Indefinite |

### Why two discounts?
Shopify doesn't let one code deliver both a percentage discount AND a free product in a single entity. The standard pattern is: code-based percentage discount + automatic Buy X Get Y, with **both configured to combine**. When the customer clicks the AC #4 link and lands with `SAVE10` auto-applied, the automatic gift rule also fires (as long as cart ≥ threshold), and both stack.

### Mystery gift product setup
1. Pick a low-COGS accessory — clip set, silk scarf, mini brush, travel pouch, etc. — retail ≈ SAR 70.
2. Create as hidden Shopify product (not in any collection, no SEO, price can be SAR 70 for the "worth SAR 70" anchor).
3. Set inventory tracking **off** OR keep stock high enough to never run out during flow.
4. Tag the product internally: `ac4-gift` for reporting.

### The "auto-apply" link in AC #4
The CTA in Email #4 uses:
```
https://www.zenhairshop.com/discount/SAVE10?redirect=/cart
```
Shopify's `/discount/<code>` endpoint applies the code to the session and redirects to `/cart` with the discount pre-loaded. Combined with the automatic Buy X Get Y rule, the customer sees: 10% off applied + mystery gift added — before they even click checkout.

---

## 5. WhatsApp deep links

All WhatsApp CTAs point to:
```
https://wa.me/966115107044
```

Pre-filled messages (URL-encoded):

**AC #2, AC #4 general inquiry:**
```
مرحباً، عندي سؤال قبل ما أطلب
→ https://wa.me/966115107044?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D8%8C%20%D8%B9%D9%86%D8%AF%D9%8A%20%D8%B3%D8%A4%D8%A7%D9%84%20%D9%82%D8%A8%D9%84%20%D9%85%D8%A7%20%D8%A3%D8%B7%D9%84%D8%A8
```

**AC #3 hesitation-specific:**
```
مرحباً، ترددت في طلب. ممكن مساعدة؟
→ https://wa.me/966115107044?text=%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%D8%8C%20%D8%AA%D8%B1%D8%AF%D8%AF%D8%AA%20%D9%81%D9%8A%20%D8%B7%D9%84%D8%A8.%20%D9%85%D9%85%D9%83%D9%86%20%D9%85%D8%B3%D8%A7%D8%B9%D8%AF%D8%A9%D8%9F
```

The pre-fill lets CS agents see the customer's mental state (hesitation vs general question) the moment they reply, routing concierge tone appropriately.

---

## 6. Dynamic cart block (optional upgrade — AC #1 only)

The `ac-1-final.html` template ships with a **static fallback cart card**. To show the actual abandoned line items, replace the static `<tr>` inside `ac-1-final.html` (the one with the Collage webp + "إكستنشن شعر طبيعي · ٩ قطع" label) with the Klaviyo dynamic loop:

```liquid
{% for item in event.extra.line_items %}
  <tr><td align="center" style="padding:16px 28px;">
    <img src="{{ item.image_url }}" width="140" style="border-radius:12px;">
    <div style="font-family:'Tajawal',Arial,sans-serif;font-weight:500;font-size:15px;color:#1c1d1d;margin-top:12px;">{{ item.title }}</div>
    <div style="font-family:'Tajawal',Arial,sans-serif;font-weight:400;font-size:13px;color:#7c6f50;margin-top:4px;">
      {{ item.quantity }} × {{ item.line_price|money }}
    </div>
  </td></tr>
{% endfor %}
```

⚠️ **Field names depend on the Shopify → Klaviyo event payload in your account.** Confirm in Klaviyo → Analytics → Metrics → `Checkout Started` → sample event → `extra` object before swapping in. If field names differ (e.g. `items` vs `line_items`), adjust the loop key.

---

## 7. QA checklist (before flow goes live)

- [ ] All 4 templates preview correctly in Klaviyo (Arabic RTL renders, no broken images)
- [ ] All CTA URLs click through to the correct destination (cart / discount / wa.me)
- [ ] `SAVE10` code works end-to-end at zenhairshop.com/discount/SAVE10
- [ ] Mystery gift auto-adds when SAVE10 session + cart ≥ threshold
- [ ] Both discounts confirmed **combinable** in Shopify Discount settings
- [ ] WhatsApp pre-fills render the Arabic text correctly on mobile WA (test on iOS + Android)
- [ ] Flow filter "Placed Order zero times since starting this flow" is ON (prevents emailing after purchase)
- [ ] Smart Sending is ON for all 4 emails
- [ ] Send 1 end-to-end test to a seeded email with a real abandoned cart
- [ ] Verify unsubscribe renders Arabic text

---

## 8. Success metrics (review after 14 days live)

| Metric | Target |
|---|---|
| AC flow placed-order rate (orders ÷ profiles entering flow) | **10–15%** |
| AC #1 CTR | 8–12% |
| AC #4 CTR (discount email) | 6–10% |
| AC flow revenue per recipient | SAR 25–60 |
| Unsubscribe rate per email | <0.3% |

If placed-order rate <8% after 14 days: test moving discount earlier to AC #3 (T+48h), reduce to 3 emails, or add SMS on T+4h.

If unsub >0.5% on any one email: that email needs subject line + hook rework.
