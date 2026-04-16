# Zen Hair Agent · Language Separation Rule

> **Rule:** Arabic and English are two independent programs that happen to share a brand identity.
> Evidence, patterns, voice, segments, and performance history **never cross languages**.
> Founder directive · 2026-04-16

---

## 1. The Hard Rule

**A pattern, voice signal, or segment rule proven in one language cohort MAY NEVER be applied to the other without being independently validated in that language's own data.**

The bootstrap sweep already confirmed this rule is not optional:

| Signal | AR verdict | EN verdict |
|---|---|---|
| Emoji in subject | ❌ Hurts (-4pp open, -42% RPR) | ✅ Helps (60% of winners use soft emoji) |
| Founder-authority subject | ✅ 2–3× CTR + real revenue | ⚠️ 2–3× CTR but **0 conversions / 0 revenue** |
| Peer register (`صاحبتك`) | ✅ Top signature | N/A — different language, different register |
| Short-breath sentences | ✅ 9.2 avg | ✅ ≤11 subject words — survives translation at subject level only |
| Segment size | Large broadcasts acceptable with recency gate | **Must** stay small (<1k) |

Mixing these would have led to emoji-free EN (bad) or emoji-heavy AR (worse).

---

## 2. File Layout (post-separation)

```
/                                    (shared — brand-wide only)
  AGENT.md                           shared operating manual
  AGENT-PROTOCOL.md                  inter-agent contract
  AUDITOR.md                         scoring manual (shared rubric)
  PRINCIPLES.md                      data-first constitution
  DATA-TASKS.md                      bootstrap plan
  LANGUAGE-SEPARATION.md             this file
  ZEN-BRAND.md                       visual tokens + sender (shared only)
  FLOW-MAP.md                        Klaviyo topology (both languages listed, clearly tagged)
  registry.json                      source of truth (language tag per entry)
  queue.md                           tasks tagged [AR] or [EN]
  deliverability-baseline.md         split per language inside

/ar/                                 AR program
  VOICE-PROFILE-AR.md                AR voice (data-extracted)
  patterns-ar.md                     AR pattern library
  drafts/                            AR drafts
  templates/                         AR shipped templates
  audit-reports/                     AR weekly audits

/en/                                 EN program (mirror)
  VOICE-PROFILE-EN.md
  patterns-en.md
  drafts/
  templates/
  audit-reports/

/agents/                             agent specs (shared)

/shared/                             cross-language-only
  overrides.md                       founder veto log
  post-mortems/                      cross-language investigations (rare)
```

---

## 3. Per-Agent Enforcement

### Campaign Agent
- **Always** loads the voice profile AND pattern library for the target language ONLY
- **Forbidden** to quote winners from the other language as precedent
- Drafts written to `/ar/drafts/` or `/en/drafts/` — never the root

### Flow Agent
- AR flows edit only AR templates · EN flows edit only EN templates
- No translation workflow — if EN needs a new Welcome flow, it gets designed from EN data, not translated from AR
- Registry entries tagged `language: "ar"` or `language: "en"`

### Segment Agent
- Every segment carries a language filter when relevant
- AR segments and EN segments never share an ID
- Suppression stack is shared (unsubscribed is unsubscribed in any language)

### Auditor Agent
- Weekly cron produces **two separate report files**:
  - `/ar/audit-reports/YYYY-MM-DD.md`
  - `/en/audit-reports/YYYY-MM-DD.md`
- Plus one top-line summary at root `audit-reports/YYYY-MM-DD-summary.md` for cross-view
- Never computes "blended" metrics without also breaking down by language

### Analyzer Agent
- Two pattern libraries, always. Never one combined.
- Cross-language comparison is allowed but must be framed as "here's what differs," not "here's what we can share"

### QA Agent
- Validates language: RTL for AR, LTR for EN
- Font stack differs — Tajawal for AR, may include a Western font for EN
- Subject/preview language must match the template language

---

## 4. Cross-Language Coordination (the only allowed overlap)

These are cross-language concerns · kept at root level:

| Shared | Why |
|---|---|
| Brand colors + fonts (Tajawal for AR, Latin fallback for EN) | Visual identity is one brand |
| Sender name + email | `سهام من زن هير <info@zenhairshop.com>` for both |
| Suppression stack (unsubscribed/bounced/spam) | A complainer in any language should never receive any language again |
| Product catalog + pricing | Same SKUs, same prices |
| Klaviyo account (WARVNh) | One account, two tracks inside |
| Deliverability IP reputation | Shared sender = shared reputation |
| Founder identity: **Seham · Co-Founder** | One person, both languages |

---

## 5. What NOT to share

| ❌ Never cross-apply |
|---|
| Subject-line style winners |
| Emoji rules |
| Send-time patterns (AR Sat-eve may differ from EN Sat-eve) |
| Body framework choice (PAS/AIDA/BAB) |
| CTA grammar (imperative vs first-person) |
| Segment size thresholds |
| A/B test results |
| Unsubscribe rate baselines |
| Open/CTR benchmarks |

---

## 6. The Rakan Decision (2026-04-16)

EN campaigns previously used two founder names (Seham + Rakan). Founder directive:
- **Seham · Co-Founder** is the single canonical identity across both languages
- Rakan references in EN are **retired**
- Sign-off per language:
  - AR: `سهام · شريكة مؤسِّسة · زن هير`
  - EN: `Seham · Co-Founder · Zen Hair`

---

## 7. Migration Log (2026-04-16)

- [x] Renamed `VOICE-PROFILE.md` → `ar/VOICE-PROFILE-AR.md`
- [x] Moved `VOICE-PROFILE-EN.md` → `en/VOICE-PROFILE-EN.md`
- [x] Split `patterns.md` → `ar/patterns-ar.md` + `en/patterns-en.md` (Analyzer agent)
- [x] Moved `drafts/ponytail-launch.html` → `ar/drafts/ponytail-launch.html`
- [x] Moved all `templates/*.html` → `ar/templates/` (all existing shipped templates are AR)
- [x] `registry.json` restructured: `flows.ar` / `flows.en`, `segments.ar` / `segments.en` / `segments.shared`, every template entry carries `language` field
- [x] `queue.md` · every item tagged `[AR]`, `[EN]`, or `[SHARED]`
- [x] Agent specs updated with language-enforcement clauses (Campaign, Flow, Analyzer, Auditor)
- [x] Weekly cron rewritten: produces `ar/audit-reports/` + `en/audit-reports/` + optional cross-view summary
- [x] Founder identity canonicalized: **Seham · Co-Founder** across both languages · Rakan references retired

---

## 8. Version

v1 · 2026-04-16 · founder directive "Arabic totally separated from English"
