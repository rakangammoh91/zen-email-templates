# Browse Abandoned AR Flow — v1 Spec

**Flow:** `[RG] AR | Browse Abandoned`
**Flow ID:** `WKnDMV`
**Trigger:** Viewed Product (Metric)
**Market:** Arabic · Zen Hair
**Status at build:** Draft
**Built:** 2026-04-19
**Master source of truth:** `zen-hair-subject-lines-v3-confidence-MERGED.xlsx`

---

## Final flow structure

| # | Node | Value | Day | Status |
|---|------|-------|-----|--------|
| 1 | Trigger | Viewed Product | — | ✅ |
| 2 | Wait | 4 hours | — | ✅ |
| 3 | E1 · T+4h | `لفتكِ شي؟` | Day 0 | Draft |
| 4 | Wait | 1 day | — | ✅ |
| 5 | E2 · T+24h | `مو متأكدة وش يناسبكِ؟` | Day 1 | Draft |
| 6 | Wait | 2 days | — | ✅ |
| 7 | E3 · T+72h | `آخر إيميل منّي · وعد` | Day 3 | Draft |
| 8 | Wait | 2 days | — | ✅ |
| 9 | E4 · T+5d | `كودكِ ينتهي بكرة` | Day 5 | Draft |
| 10 | End | — | — | ✅ |

**Structure notes:**
- Linear flow — no conditional split
- No A/B test on any message
- Cadence: T+4h → T+24h → T+72h → T+5d (matches master)

---

## Per-email config

All 4 emails share these settings:

| Field | Value |
|-------|-------|
| Sender name | `سهام · زن هير` |
| Sender email | info@zenhairshop.com |
| Reply-to | Uses sender address |
| Smart Sending | **OFF** (Skip recently emailed profiles unchecked) |
| UTM Tracking | **OFF** (Enable UTM Tracking unchecked) |
| A/B Test | None |
| Transactional | No |

### E1 · T+4h (msg `YxNxiq`)
- Template: **XWSwwU** (saved)
- Subject: `لفتكِ شي؟`
- Preview: `لسّا موجود · رجعي له`

### E2 · T+24h (msg `VqHidh`)
- Template: **RWzPnQ** (saved)
- Subject: `مو متأكدة وش يناسبكِ؟` *(rewritten on 2026-04-19 — see decision log)*
- Preview: `ابعثي صورة شعركِ · أنا أختار`

### E3 · T+72h (msg `WA8979`)
- Template: **XjRtUh** (saved)
- Subject: `آخر إيميل منّي · وعد`
- Preview: `خذي وقتكِ · بدون ضغط`

### E4 · T+5d (msg `YjW2ne`)
- Template: **Xdfd4e** (saved — Code Reminder)
- Subject: `كودكِ ينتهي بكرة`
- Preview: `١٠٪ + هدية مجانية · جاهزة لكِ`

---

## What was broken & how it was fixed

| Issue | Root cause | Fix |
|-------|-----------|-----|
| E1 wait was 1 hour, not 4h | Default template value | Edited time delay node to 4 hours |
| A/B test on E1 | Legacy artifact | Removed A/B test wrapper |
| E2 template wrong + subject drifted | Old auto-generated HTML | Changed template → Drag-and-drop → library → Email: saved → searched `RWzPnQ` → Use template; re-applied master subject |
| E1 subject missing kasra (`لفتكِ` vs `لفتك`) | Typo from earlier session | Retyped with Arabic kasra diacritic |
| E3 template was default text after a bad radio click | Hit wrong radio in template swap dialog — wiped to default | Back to content overview → three-dot → Change template → Drag-and-drop radio (precise coord 718, 372) → library opened → swapped in `XjRtUh` |
| E3 preview field appeared non-editable | React state didn't commit via form_input | Clicked field → Ctrl+A → Delete → type directly → Tab to blur |
| E3 wait was 1 day (Day 2), should be 2 days (Day 3 = T+72h) | Master cadence mismatch | Time delay node: 1 day → 2 days |
| E4 template was default | Never applied | Swapped to saved `Xdfd4e` (Code Reminder) |
| Conditional split present | Legacy branch | Three-dot on split → Delete → selected "No path" (empty branch) → Delete path; flow collapsed cleanly to linear preserving E3/E4 positions |
| Flow-level settings unclear | No flow-wide UI for Smart Sending / UTM | Applied per-email in Email details panel (Smart Sending & UTM checkboxes live under Settings section) |
| Smart Sending ON (E4) | Template default | Unchecked `Skip recently emailed profiles` per email |
| UTM Tracking ON (E1, E2, E3) | Template default | Unchecked `Enable UTM Tracking` per email |

---

## E2 subject-line decision (2026-04-19)

**Problem:** Master had E2 subject `ابعثي صورة شعركِ` (Send your hair photo) — frontloaded the ASK instead of the benefit. Body content actually leads with the color-match *problem*.

### E2 body recap
- **Hero:** `مو متأكدة وش يناسبكِ؟` (Not sure what suits you?)
- **Body:** 12 colors · 100% natural · one suits you exactly · send a hair photo on WhatsApp, I'll pick for you
- **Social proof:** Noura/Jeddah — "this color came out 100% like my hair"
- **CTA:** `ارجعي للي شفتيه` (Go back to what you viewed)
- **PS:** `الصورة تكفي · حتى لو كنتِ بالبجامة` (A photo is enough · even in pajamas)

### Subject candidates considered

| # | Subject | Approach | Chars | Notes |
|---|---------|----------|-------|-------|
| 1 | `مو متأكدة وش يناسبكِ؟` | Curiosity · mirrors hero | 22 | **CHOSEN** |
| 2 | `١٢ لون · وحدة تناسبكِ` | Direct benefit · specific | 20 | Strong backup |
| 3 | `خليني أختارلكِ اللون` | Personal · help-offer | 20 | |
| 4 | `أختارلكِ لونكِ · مجاناً` | Benefit + free | 22 | |
| 5 | `نورة طلبت «هذا» · طلع ١٠٠٪` | Social proof · curiosity | 27 | |

### Why option 1 won
- **Content match:** Mirrors hero headline exactly — subject-to-body continuity
- **Tone:** Friend's question, not a command — matches Siham's first-person voice
- **Open-rate logic:** Curiosity-gap subjects historically outperform direct-ask subjects on re-engagement flows
- **Preview pairing:** Keeps the "send photo" ask in preview so the body feels like the natural next step

### Final E2
- Subject: `مو متأكدة وش يناسبكِ؟`
- Preview: `ابعثي صورة شعركِ · أنا أختار`

---

## Settings rationale

**Smart Sending OFF on all 4:** Browse Abandoned is high-intent; we want every email delivered even if the user got another Zen Hair email in the last 16h.

**UTM Tracking OFF on all 4:** GAM analytics pipeline doesn't consume Klaviyo UTM params — they pollute referrer data and create duplicate source attribution in Shopify. Keep URLs clean.

**Flow status Draft:** Not going live from this session — QA handoff first.

---

## References
- Master Excel: `C:\Users\User\Desktop\zen-hair-subject-lines-v3-confidence-MERGED.xlsx`
- Klaviyo flow: https://www.klaviyo.com/flow/WKnDMV/edit
- Brand voice: kasra marks on 2nd-person feminine forms (`لفتكِ`, `كودكِ`, `شعركِ`), middle dot `·` as soft divider, first-person Siham signature
