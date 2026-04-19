---
name: zen-hair-arabic-voice
description: Use when writing or editing Arabic email copy for Zen Hair (متجر زن هير). Encodes Siham's first-person feminine voice, kasra discipline on 2nd-person feminine verbs, and the middle-dot divider style.
---

# Zen Hair · Arabic Voice Skill

Apply this whenever you're writing, editing, or QA-ing Arabic email copy for the Zen Hair Klaviyo account (WARVNh).

## Voice

- **First-person feminine, Siham speaking to one woman.** Never `عملاؤنا الكرام`, never plural formal.
- **Conversational** — `لفتكِ شي؟` not `هل لفت انتباهكِ شيء`.
- **Friend-offering-help tone**, not commanding.

## Kasra discipline (non-negotiable)

Arabic 2nd-person feminine verb and pronoun endings take a kasra (ِ) to disambiguate gender. The master spreadsheet treats these as meaningful typography. A missing kasra = a bug.

| ✅ Correct | ❌ Wrong |
|-----------|----------|
| `لفتكِ شي؟` | `لفتك شي؟` |
| `كودكِ ينتهي بكرة` | `كودك ينتهي بكرة` |
| `شعركِ` | `شعرك` |
| `يناسبكِ` | `يناسبك` |
| `لونكِ` | `لونك` |
| `خذي وقتكِ` | `خذي وقتك` |

When you type Arabic subjects or preview text through any tool (form fields, Klaviyo UI, code), verify the kasra is actually present in the DOM — some input methods silently drop it.

## Divider style

Use the middle dot `·` (U+00B7) as a soft separator in subjects and previews, never a comma or hyphen.

- ✅ `آخر إيميل منّي · وعد`
- ✅ `١٠٪ + هدية مجانية · جاهزة لكِ`
- ❌ `آخر إيميل منّي - وعد`
- ❌ `آخر إيميل منّي، وعد`

## Numerals

Prefer Arabic-Indic numerals in subjects/previews when the rest of the line is Arabic:

- ✅ `١٢ لون · وحدة تناسبكِ`
- ✅ `١٠٪ + هدية مجانية`
- ⚠️ Only use Western numerals when they appear inside a code or URL context.

## Subject-body continuity

Every subject must map to what the email body actually opens with. If the hero headline says "not sure what suits you?" the subject should mirror that question — not frontload the CTA.

When a subject doesn't match the body, either rewrite the subject or change the body. Don't ship the mismatch. See `flows/browse-abandoned-ar/decisions.md` for an applied example.

## Signature

All transactional + flow emails come from:

- Sender name: `سهام · زن هير`
- Sender email: `info@zenhairshop.com`
- Never use the store number `+966 11 520 2723` in copy (per account-wide memory).

## Quality checklist before committing any Arabic copy

- [ ] Every 2nd-person feminine form has a kasra
- [ ] Middle-dot `·` used for separators
- [ ] Subject mirrors the hero/opening of the body
- [ ] Arabic-Indic numerals in Arabic context
- [ ] No plural-formal constructions
- [ ] Sender name + email match `سهام · زن هير` / info@zenhairshop.com
