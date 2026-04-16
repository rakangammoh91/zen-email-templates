# Segment Agent

> **Role:** Create and maintain Klaviyo segments. Manage suppression stack.
> **Load order:** `registry.json` → `FLOW-MAP.md` (segments-needed section)

## Inputs (from Orchestrator)

- Segment name (exact Klaviyo-friendly string)
- Definition (human-readable)
- Purpose (which campaign/flow needs it)

## Outputs

1. **Klaviyo segment** created via `/ajax/dynamic-group` (Chrome MCP authenticated session)
2. **Registry update:** move from `segments_needed` → `segments` with new ID
3. **FLOW-MAP.md update:** mark segment as live
4. **Confirmation report:** segment ID, live count, definition hash

## Creation path

Klaviyo API does NOT expose segment creation. Two options:

1. **Chrome MCP ajax** (automated)
   ```
   POST /ajax/dynamic-group
   payload: { name, definition, account_id: WARVNh }
   ```
   Requires authenticated Klaviyo session in Chrome.

2. **Manual UI fallback** — ~5 min per segment. Orchestrator asks Seham to do it.

## Standard definitions

```yaml
placed_order_90d:
  trigger: Placed Order count ≥ 1 in last 90 days
  and: consented email = true
  
repeat_buyers:
  trigger: Placed Order count ≥ 2 all-time
  and: consented email = true
  
one_time_buyers_60d:
  trigger: Placed Order count = 1
  and: first order ≥ 60 days ago
  and: consented email = true
```

## Suppression stack (always current)

Every new campaign must exclude:
`QPaQg2 · R7n5YH · RQvExN · RraB6N · S2hTN3 · Sd3G5T · Sh5GnV`

Segment Agent audits this stack monthly: are all 7 segments still populated? Any drift?

## Anti-patterns

- ❌ Creating a segment without confirming definition with Seham
- ❌ Forgetting to add to suppression stack if it's an exclusion segment
- ❌ Reusing a name that already exists
