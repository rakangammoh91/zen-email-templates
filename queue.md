# Build Queue · Zen Hair Email Agent

> **How this works:** Agent reads this file at session start. Top of list = next build. Every item is tagged `[AR]`, `[EN]`, or `[SHARED]`. See `LANGUAGE-SEPARATION.md`.

---

## 🚨 From 2026-04-16 Audit (active risk mitigation)

- [ ] **[AR] Apply `ar.buyers_90d_engaged_60d` gate to all future AR broadcasts** — replaces the original engaged-30d gate proposal. Deliverability agent found recency filter (opened ≥1 last 60d OR clicked ≥1 last 90d) is the right rule. Validate after 2 broadcasts, then ratify permanently.
- [ ] **[AR] Post-mortem: Eid + Post-Ramadan unsub spikes** → Analyzer Agent (low priority now — rule change above addresses root cause)
- [ ] **[EN] Investigate Mar 13 spam complaint** (0.125%) — single-complaint event but crosses 🚨 line. Analyzer Agent.
- [ ] **[EN] Investigate Mar 6 "a message from Rakan" 1.00% CTR → 0 revenue** — landing experience may have broken

## 🔴 From 2026-04-16 Audit (rewrites · language-separated)

- [ ] **[AR] Rewrite all large AR broadcasts** to Seham Hijazi voice (founder approval per template) — use VOICE-PROFILE-AR.md
- [ ] **[EN] Keep EN flows live** (founder directive) — rewrite to EN voice when EN pattern library has n≥10 per cluster. Use VOICE-PROFILE-EN.md
- [ ] **[AR] TY Flow A/B test** — first-person Hijazi CTA vs second-person (flow has 43.1% open but ~0% CTR)

## 🔴 Blocked (waiting on founder strategic input)

- [ ] **[AR] TY #7b rework** — blockers: (1) one-sided vs two-sided decision · (2) code format · (3) landing URL
- [ ] **[SHARED] ZEN-BRAND.md fill-in** — commercial rules + customer profile sections (voice is now data-extracted; these fields are not)
- [ ] **[SHARED] Create 2 buyer segments** — `ar.buyers_90d_engaged_60d` + `en.buyers_90d_engaged_60d` (Chrome MCP or manual UI)
- [ ] **[AR] Create split segments** — `ar.repeat_buyers` + `ar.one_time_buyers_60d` for TY flow Day 60 conditional split

---

## 🟡 Active — Ponytail Launch language A/B

- [ ] **[AR] Refine `ar/drafts/ponytail-launch.html`** against patterns-ar.md
  - Subject style: question or curiosity (NOT statement-only) · ≤35 chars · no emoji
  - Founder-authority lever allowed (AR: proven 2–3× CTR lift)
  - CTA: first-person Hijazi (`أبغى أشوف`)
  - Send: Saturday or Monday evening (per patterns-ar.md)
  - Segment: `ar.buyers_90d_engaged_60d`

- [ ] **[EN] Draft `en/drafts/ponytail-launch.html`** from VOICE-PROFILE-EN.md + patterns-en.md
  - Subject: `Thin ponytail? This 2-minute fix.` (structural match to Nov 10 RPR 4.28 winner) · 21–35 chars · optional soft emoji
  - Preview: `The clip-in that doubles your pony in seconds.`
  - CTA: `Get my ponytail look →` (imperative + outcome)
  - Sign-off: `Seham · Co-Founder · Zen Hair`
  - DO NOT use founder-authority subject (EN: proven CTR but 0 revenue — unproven)
  - Segment: `en.buyers_90d_engaged_60d`

- [ ] **[SHARED] A/B test plan** — language split · same slot · same offer · single variable = language

---

## 🟢 Queued · language-separated

- [ ] **[AR] Welcome v10 E3** · Founder story (رسالة من سهام)
- [ ] **[AR] Welcome v10 E4** · Founder demo (شعري أنا)
- [ ] **[AR] Browse Abandonment rewrite** · Hijazi voice, founder tone
- [ ] **[EN] Welcome flow rewrite** · ONLY after EN body corpus exists (first EN campaign = body-starter data)
- [ ] **[EN] Browse Abandonment EN version** · same gate

---

## ⚪ Ideas / Later

- [ ] [AR] Post-review thank-you micro-flow (fires when review submitted)
- [ ] [SHARED] Win-back at Day 180 for silent customers (language auto-detected)
- [ ] [AR] Pre-Ramadan readiness broadcast
- [ ] [AR] "Seham reads reviews" weekly digest (curated UGC)
- [ ] [EN] Weekly digest EN-localized once AR version is proven

---

## Shipped ✅

- [x] [AR] TY #1 → Xa8dGZ
- [x] [AR] TY #2 → WJ9rUe
- [x] [AR] TY #3 → Th8rtT
- [x] [AR] TY #5 → Spp7Kh
- [x] [AR] TY #6 → QS3vmG
- [x] [AR] TY #7a → TwisrJ
- [x] [AR] TY #7b → Y5SMxB (rework pending)
- [x] [AR] TY #8 → TKmHq7
