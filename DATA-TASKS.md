# Data-First Bootstrap · What we need to measure before shipping

> **Purpose:** Before the agent acts, it needs baseline data. This is the founding data-extraction plan.
> **Owner:** Analyzer Agent + Auditor Agent (both read-only)
> **Cadence:** One-time bootstrap · then continuous refresh weekly

---

## 1. Voice extraction (replaces ZEN-BRAND.md §2 TODO)

**Goal:** Quantified voice profile pulled from winning emails, not founder self-description.

**Inputs:**
- Top-10 campaigns by composite score (CTR + revenue + conversion) in last 180d
- Top-5 flow emails by CTR (TY flow, Welcome, etc.)

**Extract:**
| Signal | Method |
|---|---|
| Dialect marker frequency | Count: قوليلي · خلّيني · ترى · بس · الحين · عشان · صاحبتكِ · وصلكِ |
| Average sentence length | Words per sentence |
| Subject length distribution | Chars (≤20 / 21–35 / 36–50 / 50+) |
| CTA grammar | First-person (أبغى) vs second-person (اطلبي) vs neutral ratio |
| Sign-off pattern | "— سهام" variants |
| P.S. usage rate | % emails with P.S. |
| Image-to-text ratio | Hero-only vs hero+body vs text-only |
| Button copy length | Average words in CTA |

**Output:** `VOICE-PROFILE.md` with measured values + the source email IDs that produced them.

---

## 2. Customer behavior baselines (replaces segment guesses)

**Goal:** Define segments at actual inflection points in the data.

**Queries needed:**

| Question | Data source | Output |
|---|---|---|
| Median days between 1st and 2nd order | Shopify + Klaviyo Placed Order metric | Optimal "repeat buyer" window |
| Open-rate decay curve post-purchase (Day 1→90) | TY Flow report · per-step | Natural drop-off points |
| Revenue cliff for one-timers | Shopify order data by customer | When to trigger referral push |
| Engagement half-life for new subs | Welcome Flow + broadcast response | Welcome length |
| % profiles that open ≥1 email in 30/60/90d | Klaviyo Profiles API | Engagement segment thresholds |
| Cart-to-checkout conversion by time-gap | Abandoned flow data | Optimal reminder cadence |

**Output:** `BEHAVIORAL-BASELINES.md` — all segment definitions derived from these numbers.

---

## 3. Pattern library bootstrap

**Goal:** Fill `patterns.md` with T4-confidence findings before the agent starts making recommendations.

**Method (one pass):**
1. Export all campaign send data (last 180d)
2. Cluster by: subject style × body framework × segment × send-time
3. For each cluster with n≥10, calculate: open, CTR, conversion, revenue per recipient
4. Rank clusters
5. Label each cluster: 🟢 proven winner · 🟡 mixed · 🔴 proven loser
6. Write to `patterns.md` with confidence tags

**Output:** `patterns.md` — Campaign Agent's playbook.

---

## 4. Deliverability baseline

**Goal:** Know the floor, detect drift.

| Metric | Calculation | Alert threshold |
|---|---|---|
| 30d rolling unsub rate | Sum unsubs / sum sends | 🚨 if >0.3% |
| 30d rolling bounce rate | Sum bounces / sum sends | 🚨 if >3% |
| 30d rolling spam rate | Sum complaints / sum sends | 🚨 if >0.08% |
| Engaged ratio | Opens 30d / total active subs | 🚨 if <25% |

**Output:** `deliverability-baseline.md` · updated weekly by Auditor.

---

## 5. Revenue attribution

**Goal:** Know which emails actually make money, not which ones get opened.

| Breakdown | Source |
|---|---|
| Revenue per email (shipped) | Klaviyo campaign report `attributed_revenue` |
| Revenue per flow step | Klaviyo flow report |
| Revenue per segment | Klaviyo segment × campaign join |
| Revenue by send hour | Campaign reports aggregated |
| Revenue by subject-line style cluster | Join with pattern library |

**Output:** lives in `patterns.md` + weekly audit.

---

## 6. Execution order (priority)

1. **Voice extraction** — blocks all content work
2. **Pattern bootstrap** — blocks all copywriting
3. **Behavioral baselines** — blocks all segment creation
4. **Deliverability baseline** — safety net, runs parallel
5. **Revenue attribution** — ongoing via weekly audit

Steps 1–4 can be done in one multi-agent parallel sweep today.

---

## 7. What each task produces

```
VOICE-PROFILE.md           ← Analyzer · extracts from top performers
BEHAVIORAL-BASELINES.md    ← Analyzer · extracts from customer data
patterns.md                ← Analyzer · ongoing, bootstrapped now
deliverability-baseline.md ← Auditor · updated weekly
audit-reports/*.md         ← Auditor · weekly
overrides.md               ← Orchestrator · logs founder vetoes
```

All of these are **derived files**. They are rebuilt from data, not hand-written. If you delete them, they regenerate on the next audit cycle.

---

## 8. Version

v1 · 2026-04-16
