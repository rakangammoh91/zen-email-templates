# QA Report · Ponytail Launch · 2026-04-16

**Campaign:** Ponytail Launch (language A/B — AR + EN arms)
**Scheduled send:** Sat 2026-04-18, 20:00 Asia/Amman
**QA performed:** 2026-04-16 by QA Agent
**Files under test:**
- `C:\Users\User\projects\email-agent\ar\drafts\ponytail-launch.html`
- `C:\Users\User\projects\email-agent\en\drafts\ponytail-launch.html`

**QA method:** Static HTML structural analysis + HTTP HEAD/GET validation of every external URL (hero image, logo, CTA destination, footer links).
**Note on tooling:** `Claude_Preview` MCP was unavailable — its required `.claude/launch.json` must live in the harness cwd (`C:\Program Files\Git`), which is read-only. Visual render via browser MCP was skipped because the blockers below were already definitive from source + HTTP checks. Server at `localhost:3000` confirmed both templates serve HTTP 200, so render-path itself is not the issue.

---

## Final verdicts

| Template | Verdict |
|---|---|
| AR `ar/drafts/ponytail-launch.html` | **BLOCKED** — shared asset blockers only (hero 404, CTA 404). Structurally clean. |
| EN `en/drafts/ponytail-launch.html` | **BLOCKED** — same asset blockers PLUS `<title>` / `SUBJECT` mismatch. |

Neither template is READY-TO-SHIP in current state. Both can ship once the three shared fixes land; EN needs one additional fix.

---

## Pass/fail matrix

| Check | AR | EN | Notes |
|---|---|---|---|
| Direction set correctly (AR=RTL, EN=LTR) | PASS | PASS | AR: `<html dir="rtl">` + `<body dir="rtl">`. EN: `<html dir="ltr">`; body inherits (OK for LTR). |
| Language attribute | PASS | PASS | `lang="ar"` / `lang="en"`. |
| Font stack matches spec | PASS | PASS | AR: `Tajawal, -apple-system, Segoe UI, Tahoma, Arial, sans-serif`. EN: `-apple-system, Segoe UI, Roboto, Tahoma, Arial, sans-serif` (Western). |
| Hero image loads | **FAIL** | **FAIL** | Both reference `https://www.zenhairshop.com/cdn/shop/files/ponytail-hero.jpg` → HTTP 404 (confirmed with HEAD + GET + UA). Will render as broken-image icon in every inbox. **BLOCKER.** |
| Logo image loads | PASS | N/A | AR uses `zen-hair-logo_de0f75e2...png` → HTTP 200. EN does not use an image logo (text "Zen Hair" wordmark). |
| All images have `alt` text | PASS | PASS | AR: 3 imgs, all have alt (`Zen Hair`, `بوني تيل`, `Zen Hair`). EN: 1 img, alt=`Zen Hair clip-in ponytail`. |
| CTA button present & tappable | PASS* | PASS* | Single dark pill button, ~260px min-width, ~52–56px padded height — well above mobile tap-target minimum. Text-decoration:none applied on `.btn` in EN (not underlined through global `a{underline}`). \* destination URL is broken, see next row. |
| CTA destination resolves | **FAIL** | **FAIL** | Both point at `https://www.zenhairshop.com/products/ponytail` → HTTP 404. EN variant appends `?utm_source=klaviyo&utm_medium=email&utm_campaign=ponytail_launch_en` — still 404. **BLOCKER.** |
| `{% unsubscribe %}` tag present (single) | PASS | PASS | AR: `{% unsubscribe 'إلغاء الاشتراك' %}` (1x). EN: `{% unsubscribe 'Unsubscribe' %}` (1x). |
| Sender footer present | PASS | PASS | AR: logo + store/contact/Instagram links + `© Zen Hair · المملكة العربية السعودية` + unsubscribe. EN: `Zen Hair · info@zenhairshop.com` + "you're receiving this because…" + unsubscribe. |
| Single CTA button | PASS | PASS | Exactly one `a[href*='/products/ponytail']` in each. |
| Single P.S. | PASS | PASS | Both have one `P.S.` block immediately after the sign-off. |
| 600px container | PASS | PASS | AR: `max-width:600px` on container tables (4 occurrences). EN: `.container { width:600px; max-width:100% }` — standard email pattern, equivalent. |
| Mobile-responsive breakpoint | PASS | PASS | AR: `@media only screen and (max-width:600px)` resets H1 + body padding. EN: `@media screen and (max-width:620px)` collapses container to 100% + shrinks H1 + shrinks CTA padding. |
| No console errors | PASS | PASS | Pure HTML, zero JS, zero inline event handlers. Console will be silent by construction. |
| Subject matches HTML comment header | PASS | **FAIL** | AR: header `SUBJECT: رسالة من سهام · بوني تيل جديد` == `<title>`. EN: header `SUBJECT: Thin ponytail? This 2-minute fix.` ≠ `<title>Your ponytail, in 2 minutes.` — inconsistency between header directive and document title. |
| Preview text matches HTML comment header | PASS | PASS | AR: header `PREVIEW: يوم شعركِ مو متعاون — هذا الحل بدقيقة` == hidden preheader div. EN: header `PREVIEW: The clip-in that doubles your pony in seconds.` == `.preheader` div. |
| `role="presentation"` on layout tables | PASS | PASS | AR: 6/6. EN: 4/4. |
| Founder identity consistent | PASS | PASS | AR: `سهام · شريكة مؤسِّسة · زن هير`. EN: `Seham · Co-Founder · Zen Hair`. Matches LANGUAGE-SEPARATION §6. No Rakan references in EN. |

---

## Blockers (must fix before Saturday send)

1. **Hero image 404** (shared, both templates)
   `https://www.zenhairshop.com/cdn/shop/files/ponytail-hero.jpg` does not exist on the Shopify CDN. Either the asset has not been uploaded yet or the filename is a placeholder. **Fix:** upload the ponytail hero shot to Shopify and update the `<img src>` in both templates to the real CDN URL. Verify with a fresh HEAD request returning `200 image/jpeg`.
2. **CTA destination 404** (shared, both templates)
   `https://www.zenhairshop.com/products/ponytail` returns 404. The product either is not published yet, sits at a different handle, or is in draft. **Fix:** publish the product (or confirm handle — e.g. `/products/ponytail-clip-in`) and update both CTAs. EN also carries a UTM string — preserve it on the corrected URL. The AR CTA has no UTM; consider adding one parallel to EN for attribution parity, but this is a nice-to-have, not a blocker.
3. **EN subject / title mismatch** (EN only)
   Header comment states `SUBJECT: Thin ponytail? This 2-minute fix.` but `<title>Your ponytail, in 2 minutes.</title>`. Pick one and align both — rule in AGENT-PROTOCOL requires subject match with HTML comment header. Most likely the `<title>` is stale from a previous draft and should be updated to match the header SUBJECT.

## Non-blocking observations

- EN uses a text wordmark for the brand ("Zen Hair") in the top-left header while AR uses the 48px logo PNG. Not a violation of any rule — both brand-appropriate — but worth noting for visual consistency if the founder prefers one style across both arms.
- EN breakpoint is 620px vs AR at 600px. Spec does not mandate a specific value; both collapse to a fluid single column on phones.
- EN footer email `info@zenhairshop.com` is visible in the body; AR footer does not show a contact email (uses "تواصلي معنا" link instead). Intentional per language, acceptable.
- Hero image in AR is constrained to `width:100%;max-width:504px;border-radius:16px` (padded inset look). EN hero is `width:100%` edge-to-edge with no border-radius. Stylistic divergence is intentional per language-separation; no action.

## Recommendation

Once the three blockers are fixed, re-run this QA and both templates should move to READY-TO-SHIP. Estimated fix time: under 30 minutes if the hero asset and published product URL are available — well inside the Saturday 8pm Asia/Amman deadline.
