---
name: klaviyo-flow-auditor
description: Use when building, editing, or QA-ing a Klaviyo flow in the Zen Hair account. Covers the full per-email settings checklist, template-swap recovery, Smart Sending / UTM rules, and pre-swap baseline capture.
---

# Klaviyo Flow Auditor

Apply this skill before marking any `[RG]` flow ready for Draft → Live promotion.

## Pre-build: read the source of truth

1. `registry/flows.yml` — confirm the flow ID, replacement target, and tier
2. `config/thresholds.yml` — know the alert thresholds
3. `docs/flows-performance-log.md` — capture the replaced flow's current 30d baseline (needed for the swap-events table later)
4. The master Excel (`zen-hair-subject-lines-v3-confidence-MERGED.xlsx`) — always the source of truth for subjects/previews

## Per-email settings (verify every single email)

| Setting | Required value | Where |
|---|---|---|
| Sender name | `سهام · زن هير` | Email details → Sender |
| Sender email | `info@zenhairshop.com` | Email details → Sender |
| Reply-to | Sender address | Email details → Reply-to |
| Smart Sending | **OFF** (`Skip recently emailed profiles` unchecked) | Email details → Settings |
| UTM Tracking | **OFF** (`Enable UTM Tracking` unchecked) | Email details → Settings |
| Transactional | No | Email details → Settings |
| A/B Test | None (unless explicitly planned) | Email editor |

**Smart Sending OFF** rationale: high-intent flows (Browse Abandoned, Abandoned Checkout) should deliver every email even inside the 16h dedupe window.

**UTM Tracking OFF** rationale: GAM analytics pipeline doesn't consume Klaviyo UTMs; they pollute Shopify referrer attribution.

## Template-swap recovery

If you hit the "wrong radio" bug (template gets wiped to default text):

1. Back to content overview
2. Three-dot on the email → Change template
3. Click the **Drag-and-drop** radio (coord ≈ 718, 372) — not the HTML radio
4. Library opens → search the saved template ID (e.g. `XjRtUh`) → Use template

If a preview field won't commit via `form_input` (React state doesn't update):
1. Click the field directly
2. `Ctrl+A` → `Delete`
3. `type` the new value
4. `Tab` to blur and force commit

Verify via `javascript_tool` query of the DOM before moving on.

## Arabic content check

Invoke the `zen-hair-arabic-voice` skill. Every subject and preview must pass its checklist before committing.

## Subject-body continuity check

Read the body hero headline. Does the subject echo it, build curiosity around it, or set it up? If the subject and hero are unrelated — rewrite the subject. See `flows/browse-abandoned-ar/decisions.md` for the E2 example.

## Pre-Draft-to-Live checklist

- [ ] All emails have Smart Sending OFF
- [ ] All emails have UTM Tracking OFF
- [ ] All subjects have correct kasra marks
- [ ] All previews committed to React state (verify via DOM)
- [ ] Flow structure is linear unless intentionally branched
- [ ] Wait timings match master cadence
- [ ] No leftover A/B tests unless planned
- [ ] Sender name + email consistent across all emails
- [ ] Decision log updated in `flows/<slug>/decisions.md`
- [ ] Pre-swap baseline captured in `docs/flows-performance-log.md` swap-events table

## Promotion to Live

1. Update status in `registry/flows.yml`: `status: live` on the [RG] flow
2. Commit with message `feat: promote <flow-slug> to live`
3. The `swap-detector` workflow will open the post-swap measurement issue
4. After 30 days: pull last_30_days, fill in the post-swap row, write verdict

## Things to never automate

- Draft → Live promotion (human call)
- Subject rewrites (judgment)
- Paying for flow rebuilds with production user traffic before QA
