# Zen Hair · Email Performance Auditor

> **Purpose:** Score every campaign and flow message against benchmarks. Flag keep/iterate/kill/escalate. Auto-queue rewrites.
> **Load order:** Read after `AGENT.md`, `ZEN-BRAND.md`, `FLOW-MAP.md`, `registry.json`.
> **Version:** v1 · 2026-04-16

---

## 1. Scoring Rubric (Hair & Beauty · KSA/GCC)

| Metric | 🟢 Strong | 🟡 OK | 🔴 Problem | 🚨 Escalate |
|---|---|---|---|---|
| **Open rate** | > 38% | 25–38% | < 25% | < 15% |
| **Click rate (CTR)** | > 2.5% | 1.2–2.5% | < 1.2% | < 0.5% |
| **Conversion rate** | > 3% | 1–3% | < 1% | < 0.3% |
| **Revenue per recipient** | > 2 SAR | 0.5–2 SAR | < 0.5 SAR | 0 SAR after 100+ sends |
| **Unsubscribe rate** | < 0.1% | 0.1–0.3% | 0.3–0.5% | > 0.5% 🚨 |
| **Spam complaint rate** | < 0.01% | 0.01–0.08% | — | > 0.1% 🚨 DELIVERABILITY RISK |
| **Bounce rate** | < 1% | 1–3% | 3–5% | > 5% 🚨 |

**Benchmark source:** Klaviyo industry H&B averages + calibration against Zen Hair's top-quartile sends.

---

## 2. Scoring Logic

For each email, compute a **Composite Score** (0–100):

```
Composite = (OpenScore × 0.25)
          + (CTRScore × 0.25)
          + (ConversionScore × 0.25)
          + (RevenueScore × 0.20)
          + (UnsubScore × 0.05)  [inverse]
```

**Each sub-score** = 0 at 🔴 floor, 50 at 🟡 midpoint, 100 at 🟢 strong, capped.

**Final verdict:**
- **Score ≥ 75** → 🟢 KEEP (protect · clone pattern)
- **Score 50–74** → 🟡 ITERATE (A/B test one element)
- **Score 25–49** → 🔴 REWRITE (proposal required)
- **Score < 25** → 🔴 KILL (remove from flow / archive)
- **Any 🚨 metric** → overrides verdict → ESCALATE

**Minimum sample:** 100 sends for statistical weight. Below that, mark "insufficient data · recheck next cycle."

---

## 3. Pattern Extraction

After scoring, extract patterns across the corpus:

### Subject-line patterns
- **Style:** question / statement / curiosity / urgency / personal-name / emoji
- **Length:** ≤20 / 21–35 / 36–50 / >50 chars
- **Dialect markers:** Hijazi signal words (قوليلي · خلّيني · صاحبتكِ · وصلكِ · ترى · بس · الحين)
- **Rank styles by average open rate** within the cohort

### Body patterns
- **CTA style:** first-person ("أبغى...") vs. second-person ("اطلبي...") vs. neutral
- **Button copy length:** ≤3 words / 4–6 / 7+
- **Framework:** PAS / AIDA / BAB / 1-3-1 / direct / W-W-H
- **Image usage:** hero + body / hero only / no images
- **Rank by CTR**

### Send-time patterns
- **Day-of-week × hour heatmap**
- **Best/worst combinations** by open rate AND by revenue
- **Account for Saudi prayer times** — avoid Maghrib hour sends

### Segment patterns
- **Performance per segment** (VIP / engaged-30d / full list / potential-purchasers)
- **Conversion lift per segment** vs. full-list baseline

### Flow-step patterns
- **Per flow:** rank steps by score · identify drop-off point
- **Day-offset sensitivity** — do longer gaps hurt or help?

---

## 4. Flag System (output)

Each email gets a flag + an action:

| Flag | Meaning | Action |
|---|---|---|
| 🟢 **KEEP** | Top performer · protect | Document the winning pattern. Clone for future builds. |
| 🟡 **ITERATE** | Decent · has headroom | Propose ONE A/B variable (subject / CTA / send time / image). |
| 🔴 **REWRITE** | Underperforming | Draft specific rewrite angle with rationale. Add to `queue.md`. |
| 🔴 **KILL** | Dead weight / zero revenue | Recommend archive. Ask founder approval. |
| 🚨 **ESCALATE** | Deliverability / compliance risk | Notify founder immediately, pause if unsubs spiking. |

---

## 5. Report Format

**Output path:** `audit-reports/YYYY-MM-DD.md`
**Also:** Auto-appends 🔴 items to `queue.md`

```
# Zen Hair · Audit · YYYY-MM-DD
Lookback: [X] days | Campaigns: [N] | Flow messages: [M]

## Top Line
Revenue from email: [X] SAR ([+/-Y]% vs prior)
Sent: [N] | Open: [X%] | CTR: [X%] | Unsub: [X%]
Overall health: 🟢/🟡/🔴

## 🟢 KEEP (Top 5 · clone these patterns)
[table: name | score | the winning pattern | recommendation]

## 🟡 ITERATE (A/B test candidates)
[table: name | score | proposed test | expected lift]

## 🔴 REWRITE / KILL
[table: name | score | issue | recommended action]

## 🚨 Escalations
[prose · urgent items only]

## Patterns Learned
### Subjects · Bodies · Send Times · Segments · Flows
[findings]

## Queue Additions (auto-appended)
[bulleted action items now in queue.md]
```

---

## 6. Execution Policy

| Situation | Agent does |
|---|---|
| 🟢 Top performer found | Document pattern in `patterns.md`. No action. |
| 🟡 Iterate candidate | Draft A/B proposal in `drafts/ab-[name].md`. Require approval. |
| 🔴 Rewrite needed | Draft replacement HTML in `drafts/`. Add to queue. Require approval. |
| 🔴 Kill needed | Propose archive. NEVER archive without explicit founder approval. |
| 🚨 Deliverability risk | Telegram alert immediately. Recommend pause. Do NOT pause without approval. |

**Never auto-ship changes.** Auditor proposes → founder approves → builder ships.

---

## 7. Cadence

- **Founding audit:** one-time · 180-day lookback · full corpus
- **Ongoing:** weekly · Sunday 9am Asia/Amman · last 7d + rolling 30d + rolling 90d
- **On-demand:** founder can trigger "audit now" anytime

---

## 8. What the auditor CANNOT tell you

- **WHY** a campaign won (needs qualitative judgment — subject + moment + audience context)
- **Whether** to kill a brand pillar even if it underperforms (strategic call)
- **Creative direction** for a rewrite — it proposes angles, founder picks
- **Seasonal / one-off anomalies** without manual annotation (Ramadan, White Friday, launch weeks)

Auditor surfaces signal. Founder interprets and decides.
