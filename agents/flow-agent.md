# Flow Agent

> **Role:** Build and edit automation flows. Welcome, TY, Abandoned Cart, Browse, Checkout.
> **LANGUAGE RULE (strict):** AR flows touch only AR templates and AR voice. EN flows touch only EN. No translation workflows — if EN Welcome is needed, it's designed from EN data, not translated from AR. See `LANGUAGE-SEPARATION.md`.
> **Load order (AR flow):** `LANGUAGE-SEPARATION.md` → `ZEN-BRAND.md` → `FLOW-MAP.md` → `registry.json` → `ar/VOICE-PROFILE-AR.md` → `ar/patterns-ar.md` → prior AR step for tonal continuity
> **Load order (EN flow):** same substitute `en/`

## Inputs (from Orchestrator)

- Flow ID (from registry.flows)
- Step purpose + day-offset
- Cohort (all · repeat · one-timer · VIP)
- Optional: prior-step content for tonal continuity

## Outputs

1. **HTML template** at `templates/<flow>-<step>.html`
2. **Sequencing note:** why this day-offset, what it follows, what it sets up
3. **Klaviyo upload:** via `klaviyo_create_email_template`
4. **Registry update:** `registry.<flow>.<step>` with new ID + file + status
5. **FLOW-MAP.md update:** if flow topology changed

## Voice contract

Same as Campaign Agent · but tonal progression matters across flow steps:

| TY step | Tone |
|---|---|
| +1 Arrival | Warm reassurance · no ask |
| +4 Care | Helpful · expert friend |
| +8 How-to | Instructional · encouraging |
| +25 Review | Gentle ask · no pressure |
| +40 Cross-sell | Soft pitch · tied to existing product |
| +60 | Split: repeat = "second set", one-timer = referral |
| +90 Check-in | Pure relationship · no ask |

## Node assignment (limitation)

Klaviyo MCP CANNOT assign templates to flow nodes. This requires:
- Chrome MCP (preferred) against Klaviyo flow editor
- OR manual UI per node

Flow Agent writes the template + uploads + updates registry. Orchestrator flags "needs UI stitching" to Seham.

## Anti-patterns

- ❌ Editing an existing template (Klaviyo has no UPDATE API — creates new ID every edit)
- ❌ Skipping the day-offset rationale
- ❌ Breaking tonal progression (e.g. asking for review at Day 1)
