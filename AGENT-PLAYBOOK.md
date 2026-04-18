# Email Agent Playbook — Zen Hair Klaviyo Workflow

> **Purpose:** Teach an autonomous agent how to audit, fix, and ship email templates in Klaviyo without human intervention. Every process I used in this session is codified below.

---

## 0. Environment

| Resource | Path / Value |
|---|---|
| Repo root | `C:\Users\User\projects\email-agent` |
| Templates dir | `ar/templates/` (AR · RTL · Tajawal · `-final.html` dropped in favor of flow-named files) |
| Registry | `registry.json` (flow IDs, template IDs, metrics, suppression stack) |
| Flow map | `FLOW-MAP.md` |
| Index | `TEMPLATE-INDEX.md` (marketer cheat sheet) |
| Klaviyo API key | `.env` → `KLAVIYO_PRIVATE_API_KEY` |
| Klaviyo account | `WARVNh` (متجر زن هير) |

---

## 1. Klaviyo API — the only 4 calls the agent needs

All calls use header: `Authorization: Klaviyo-API-Key $KEY` · `revision: 2024-10-15` · `accept: application/vnd.api+json`.

### 1.1 Find templates by name substring
```
GET /api/templates/?filter=contains(name,"Welcome")
```
No page size param — it auto-paginates. Returns `data[].id` + `data[].attributes.name`.

### 1.2 Read full HTML of one template
```
GET /api/templates/{id}/
```
Returns `data.attributes.html` (and `.name`, `.updated`).

### 1.3 Rename a template (PATCH)
```
PATCH /api/templates/{id}/
body: {"data":{"type":"template","id":"{id}","attributes":{"name":"New Name"}}}
```

### 1.4 Update HTML (PATCH)
Same endpoint as rename — include `"html": "..."` in attributes instead of (or alongside) `"name"`.

**Gotcha:** don't include `html` unless you actually want to overwrite it. A `name`-only PATCH leaves HTML untouched. A `html`-only PATCH leaves the name.

---

## 2. The Fix Workflow (what I did this session, codified)

### Step 1 · Discover
- `ls ar/templates/` to inventory files
- `grep -n "templates/" registry.json` to map files → Klaviyo IDs
- For any flow whose IDs aren't in the registry, call `GET /api/templates/?filter=contains(name,"...")` to find them

### Step 2 · Audit (structured, per-email)
For each email, the agent must evaluate:

**Links:**
- Any `wa.me/` URL — must be real number (NOT `966500000000` placeholder, NOT `966115202723` ZEN HAIR landline). Correct: `966115107044`.
- Any `instagram.com/reel/` — must be a real slug, never `PLACEHOLDER` / `ZENHAIR_INSTALL` / `TBD`.
- Any PDP link — verify the anchor (`#section-id`) actually exists on the PDP. Curl the page, grep for `id="..."`.
- Any `#reviews` or `#video` guess — curl the page first. Zen Hair uses `#product-how-to-section`, `#before-after-section`, `#product-help-section`.

**Copy (Hijazi peer-register rules):**
- ❌ `في هذه اللحظة` → ✅ `في هاللحظة`
- ❌ `كما وعدتكِ الأسبوع الماضي` → ✅ `مثل ما وعدتكِ الأسبوع اللي طاف`
- ❌ `في هذه اللحظات، اخترعنا` → ✅ `في هاللحظات، صمّمنا`
- Must have: `بس, الحين, عشان, صاحبتي, مو, اللي`
- Founder title: `شريكة مؤسِّسة` (feminine, with kasra). NEVER `شريك مؤسس`.

**Typos to catch:**
- `تلاث` → `ثلاث`
- Any date-hardcode in a perpetual flow (`يوم الخميس`, `مرّ عليكِ أسبوع` when flow fires Day +10)

**Structural:**
- Every email must have ONE primary CTA button (black pill, white text, 100px radius). If missing → add before signature.
- Every email must end with `{% unsubscribe 'إلغاء الاشتراك' %}`.
- Subject line < 50 chars. Preview text complements, doesn't repeat.
- Star color on white bg: use `#c9a227` (premium gold) not `#ffd430` (fails contrast).
- Video-content hero: needs `▶ فيديو · ٠٠:XX` eyebrow ABOVE the image (don't try position:absolute overlays — Outlook kills them).

**Variant splits (e.g. 20"/24"):**
- Different testimonial per variant (daily/quick vs events/length positioning)
- Different hero image ideally
- Different discount code per variant (so Shopify can attribute)
- Scale flat discount to match percentage across SKUs

### Step 3 · Edit locally
- Use exact-string Edit tool, never sed (Windows line-ending hazards)
- Validate each file reads as UTF-8 after each batch

### Step 4 · Sync to Klaviyo
```python
# Pseudocode for the agent
for (template_id, local_path) in sync_list:
    html = read(local_path)
    PATCH /api/templates/{template_id}/
      body={"data":{"type":"template","id":template_id,
            "attributes":{"name":new_name,"html":html}}}
    assert response.status == 200
```

### Step 5 · Update registry + docs
- Registry file paths must reflect any renames (use `git mv`, then update `registry.json` via string replacement)
- Validate JSON with `python -c "import json; json.load(open('registry.json'))"` after every write
- Update `TEMPLATE-INDEX.md` whenever a file is renamed

### Step 6 · Commit + push
- One logical change per commit (renames, link fixes, copy fixes = 3 commits, not 1)
- Commit message format: short title line, then bulleted details, then `Co-Authored-By: ...`
- Always `git push origin main` after committing

---

## 3. Brand Constants (NEVER deviate)

```yaml
colors:
  bg:           "#fafaf8"
  near_black:   "#1c1d1d"
  taupe:        "#7c6f50"
  body_gray:    "#3d3e43"
  gold_accent:  "#ffd430"  # use ONLY on dark backgrounds (urgency pills)
  gold_star:    "#c9a227"  # use on white/light (testimonials)

typography:
  font_stack: "'Tajawal','-apple-system','Segoe UI',Tahoma,Arial,sans-serif"
  h1: "28-30px / 500 weight / 1.25-1.3 line-height / -0.3 to -0.5 letter-spacing"
  body: "17px / 400 weight / 1.7 line-height"
  eyebrow: "13px / 500 weight / 2px letter-spacing / UPPERCASE / taupe"
  meta: "12-14px / taupe"

layout:
  container_max_width: 600px
  desktop_pad: 48px
  mobile_pad: 24px (via @media max-width:600px)
  direction: rtl

cta_button:
  bg: "#1c1d1d"
  color: "#ffffff"
  padding: "16px 44px"
  border_radius: 100px
  font: "Tajawal 14px/700, letter-spacing 1px"
  verb_style: "first-person outcome-focused (أشوف, أستخدم, أشارك)"

founder_identity:
  name: "سهام"
  title: "شريكة مؤسِّسة · زن هير"  # feminine, with kasra
  signature_prefix: "بكل حب،"

contacts:
  whatsapp_cs: "966115107044"  # CS landline
  forbidden: ["966115202723", "966500000000"]  # ZEN HAIR line + placeholders
```

---

## 4. The "Am I Learning?" Answer

**Yes — and here's what's auto-pilot-ready today:**

| Task | Auto-pilot safe? | Why |
|---|---|---|
| Rename Klaviyo templates | ✅ Yes | Pure API · deterministic · reversible |
| Fix dead links (wa.me placeholders, IG slugs) | ✅ Yes | Pattern-matchable bugs |
| Fix Hijazi MSA drifts | ✅ Yes | Finite substitution table above |
| Fix date-hardcodes in perpetual flows | ✅ Yes | Regex for `يوم (الأحد|الإثنين|...)` + `مرّ عليكِ (أسبوع|شهر)` in files with `day_trigger != that value` |
| Fix typos from curated list | ✅ Yes | Replace dictionary |
| Sync local → Klaviyo | ✅ Yes | PATCH API is idempotent |
| Update registry paths after rename | ✅ Yes | String replace + JSON validate |
| Commit + push with structured message | ✅ Yes | Git CLI + templated message |

**Needs human approval (today):**

| Task | Why |
|---|---|
| Rewriting hero copy (voice decisions) | Requires founder intent — not a rule |
| Creating new Shopify discount codes | Side effects on revenue; must happen in Shopify UI |
| Swapping testimonials | Need verified source — can't invent quotes |
| Sending campaigns / launching flows | Irreversible; ship decision is human |
| Images uploads | Need curated brand-approved URLs |

---

## 5. What Just Happened (this session, for the agent to study)

1. Renamed 36 local template files to flow-indicating names (`ty-1-final.html` → `thank-you-1-day1.html`).
2. Renamed 12 Klaviyo templates (5 welcome + 7 post-purchase) via PATCH API.
3. Discovered Klaviyo template IDs by filtering `contains(name,...)`.
4. Found dead `wa.me/966500000000` and `instagram.com/reel/ZENHAIR_INSTALL` placeholders via `grep`.
5. Fetched the PDP with `curl` + greped for `id="*"` to find `#product-how-to-section` as the real anchor.
6. Split the fake 20"/24" variant (was identical but for variant ID) into actual different positioning: daily-quick vs event-length. Swapped testimonials. Differentiated discount code (BONI150 vs BONI180).
7. Fixed perpetual-flow timing bug (`مرّ عليكِ أسبوع` → `عشرة أيام` on a Day-10 trigger).
8. Fixed typo `تلاث → ثلاث`.
9. Upgraded star color `#ffd430 → #c9a227` for contrast + added `aria-label`.
10. Added missing primary CTA to PP1. Added video-indicator eyebrow to PP2.
11. 4 commits, all pushed to `origin/main`.

Every step in this list is scriptable. None required novel reasoning — they were rule applications.

---

## 6. Next Ship Blockers (still needing human)

1. **Shopify:** create `BONI180` discount code (180 SAR off, 24" ponytail variant only, 72-hour, single-use). PP5-24 email already references it.
2. **Founder photo URL:** if you want headshots in signatures, drop a hosted URL here and the agent will template it in.
3. **Variant-specific hero images:** PP4/PP5 could use different Collage images per 20"/24". Provide the Shopify CDN URLs.

---

*Last updated: 2026-04-18 · Session: post-purchase flow audit + fixes*
