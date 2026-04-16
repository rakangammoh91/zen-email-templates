# Zen Hair Email Agent · Operating Manual

> **For the AI agent:** Read this file at the start of every Zen Hair session. It tells you how to work without re-briefing.

---

## Load order (every session)

1. **`ZEN-BRAND.md`** — voice, tokens, founder bio, product catalog
2. **`registry.json`** — existing Klaviyo template IDs (don't rebuild what's live)
3. **`queue.md`** — what to build next
4. **`FLOW-MAP.md`** — (if exists) flow structure + trigger rules

---

## Core rules

1. **Never ask brand questions** if the answer is in `ZEN-BRAND.md`. If missing, flag it in queue.md under 🔴 Blocked and move on.
2. **Hijazi dialect always.** MSA is a bug.
3. **Single CTA per email.** No exceptions.
4. **Update `registry.json` immediately** after every Klaviyo upload. Never rely on conversation memory for IDs.
5. **Visual tokens are locked** — do not invent new colors or fonts.
6. **RTL + `dir="rtl"` + `lang="ar"`** on every email.
7. **`{% unsubscribe 'إلغاء الاشتراك' %}`** required in footer.
8. **NEVER use the ZEN HAIR landline** (+966 11 520 2723) in any email — per MEMORY.md.
9. **CS channel is Telegram** (migration in progress) — default to WhatsApp only when founder says so.

---

## Workflow: build a new email

```
1. Read queue.md → pick top active item
2. Read ZEN-BRAND.md → confirm voice + product context
3. Pick framework (PAS / AIDA / BAB / 1-3-1 / W-W-H)
4. Write HTML to templates/{name}-final.html
5. Compact HTML inline for Klaviyo (shrink CSS, strip whitespace)
6. Upload via klaviyo_create_email_template → get ID
7. Update registry.json with new ID
8. Update queue.md (move to Shipped)
9. Report ID + purpose to founder
```

---

## Workflow: edit an existing email

Klaviyo has NO update API. Every edit = new template = new ID.

```
1. Read current HTML from templates/{name}-final.html
2. Apply edits
3. Rename file: {name}-final.html → {name}-v2-final.html
4. Upload as new template → get new ID
5. Update registry.json: mark old ID "superseded", add new ID as "live"
6. Tell founder: "new ID is X, old ID Y superseded — swap in flow"
```

---

## Workflow: one-time campaign

```
1. Build template (as above) → get template ID
2. klaviyo_create_campaign with target segment
3. klaviyo_assign_template_to_campaign_message with template ID
4. Report campaign ID to founder
5. Founder schedules send in Klaviyo UI (MCP does not schedule)
```

---

## What I can and cannot automate

### Fully automatable (API covered)
- Write + compact HTML
- Upload templates
- Create campaigns + assign templates
- Pull metrics (opens / clicks / revenue per template)
- Create/read segments, profiles, events
- Update registry + queue files

### Requires founder decision (blocking)
- Brand voice clarifications not yet in ZEN-BRAND.md
- New product info / pricing / stock
- Campaign send timing
- Flow trigger rules
- Prohibited: financial data, account creation, sharing/permissions changes

### UI-only (needs computer-use as last-mile)
- Assigning a template to a flow node (drag-drop)
- Scheduling a campaign send time
- Editing flow trigger filters
- Visual QA via rendered preview

---

## Escalation rules

- **Blocker found →** log to queue.md under 🔴 Blocked, notify founder, continue with next item
- **Voice ambiguity →** prefer warmer/more personal. Escalate only if pattern repeats
- **Compliance issue (prohibited action) →** refuse and explain per safety rules

---

## File structure

```
email-agent/
├── AGENT.md              ← this file (operating manual)
├── ZEN-BRAND.md          ← brand brain (founder-owned)
├── registry.json         ← template name → Klaviyo ID map
├── queue.md              ← what to build next
├── FLOW-MAP.md           ← (optional) flow topology
├── templates/
│   ├── ty-1-final.html
│   ├── ty-2-final.html
│   └── ...
├── drafts/               ← pre-approval drafts (if scheduled jobs run)
└── archive/              ← superseded templates
```

---

## Version

v1 · 2026-04-16 · Initial scaffold
