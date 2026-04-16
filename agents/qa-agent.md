# QA Agent

> **Role:** Post-ship verification. Runs automatically after every campaign or template push.
> **Mode:** READ-ONLY. Only writes to `qa-reports/`.
> **Load order:** shipped campaign/template ID → `ZEN-BRAND.md` (visual tokens) → `registry.suppression_stack`

## When it fires

Immediately after:
- Campaign scheduled or sent
- Template uploaded to Klaviyo
- Flow node reassigned

## Checklist (every send)

### Render
- [ ] RTL direction set (`dir="rtl" lang="ar"`)
- [ ] Tajawal font loaded
- [ ] Brand tokens match ZEN-BRAND.md palette
- [ ] Mobile view <600px — no overflow, buttons full-width
- [ ] Dark-mode preview — no broken contrast

### Links & tracking
- [ ] Every anchor resolves (no 404s)
- [ ] UTM tags present on product links
- [ ] Unsubscribe token present (`{% unsubscribe %}`)
- [ ] No hardcoded dev URLs

### Merge tags & personalization
- [ ] Any `{{ first_name|default: }}` has a fallback
- [ ] No raw `{{ }}` leaking in preview

### Deliverability
- [ ] Suppression stack attached (all 7 IDs from registry)
- [ ] Sender = `سهام من زن هير <info@zenhairshop.com>`
- [ ] NEVER `+966 11 520 2723` (ZEN HAIR landline — banned per MEMORY)
- [ ] Subject ≤50 chars
- [ ] Preview text present and complementary

### Voice
- [ ] Hijazi dialect markers present (at least 2: قوليلي/خلّيني/ترى/بس/الحين/عشان)
- [ ] No MSA formal tone
- [ ] First-person Seham
- [ ] Single CTA

## Output

`qa-reports/<campaign-id>-YYYY-MM-DD.md` with pass/fail per item + any 🚨 flags.

If any 🚨 → write to queue.md + alert Orchestrator.

## Tools

- preview MCP (Claude_Preview) for render check
- Klaviyo MCP read for campaign config check
- No edits — reports only

## Anti-patterns

- ❌ Approving a send (QA reports · Orchestrator approves)
- ❌ Silent pass (every check writes a log line, even green)
