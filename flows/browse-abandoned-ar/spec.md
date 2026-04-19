# Browse Abandoned AR — Flow Spec

**Klaviyo ID:** `WKnDMV` · **Status:** Draft · **Replaces:** `VKsTPF`
**Built:** 2026-04-19 · **Last edited:** 2026-04-19

Canonical spec: [`docs/browse-abandoned-ar-flow-v1-spec.md`](../../docs/browse-abandoned-ar-flow-v1-spec.md)

## Flow shape

```
Viewed Product → Wait 4h → E1 → Wait 1d → E2 → Wait 2d → E3 → Wait 2d → E4 → End
```

| # | Email | File | Day |
|---|-------|------|-----|
| E1 | T+4h · `لفتكِ شي؟` | [emails/e1-lifted-your-eye.md](emails/e1-lifted-your-eye.md) | Day 0 |
| E2 | T+24h · `مو متأكدة وش يناسبكِ؟` | [emails/e2-not-sure.md](emails/e2-not-sure.md) | Day 1 |
| E3 | T+72h · `آخر إيميل منّي · وعد` | [emails/e3-last-email.md](emails/e3-last-email.md) | Day 3 |
| E4 | T+5d · `كودكِ ينتهي بكرة` | [emails/e4-code-expires.md](emails/e4-code-expires.md) | Day 5 |

## Flow-wide settings

- Smart Sending **OFF** (high-intent trigger, deliver every time)
- UTM Tracking **OFF** (GAM analytics doesn't consume Klaviyo UTMs)
- A/B Test **None**
- Sender `سهام · زن هير` <info@zenhairshop.com>

Decisions → [decisions.md](decisions.md)
