# Scenario [N]: [Short descriptive title]

## Skill Tested
`/checkin` | `/weekly-plan` | `/log-session` (or combination)

## Type
Happy path | Edge case | Ambiguous | Baseline

## Purpose
One sentence: what does this scenario test that other scenarios don't?

## Setup / Preconditions
- Program: [name], Week [N] of [total] ([odd/even]-week pattern)
- Today: **[Day] [Date]** — [planned session or rest/cardio day]
- Plan state: [exists/missing], [N] training days ([list: e.g., Tue T, Thu S, Fri H])
- Completed sessions this week: [list or "none"]
- Training log: [relevant recent entries]
- Strava (last 48h): [activities or "none"]
- Weather: [conditions if relevant]

## Athlete Input
```
1. Sleep last night: [answer]
2. Leg soreness (0-10): [answer]
3. Energy (1-5): [answer]
[Any additional athlete messages, e.g., "I want to train today instead"]
```

## Actual System Output
> [Paste the full system output here as a blockquote. This is required — it shows the grader exactly what the system produced.]

## Tests

### [Group name] Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | [Specific observable check] | [What the output should contain or do] | |

### [Additional test groups as needed]

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| N | ... | ... | |

## Decision Logic Verified
- [Rule applied] → [outcome] (reference CLAUDE.md section if applicable)
- [Threshold check]: [value] [operator] [threshold] → [result]
- [Why this decision is correct for this scenario]

## What This Scenario Tests That Others Don't
- **[Capability]**: [one line explaining why this is unique]
- **[Capability]**: [one line]

## Data State After Scenario

### training_log.ndjson
- [Changed / Unchanged] — [details]

### current_week_plan.json
- [Changed / Unchanged] — [details of status, schedule, or field changes]

---
<!--
CHECKLIST before marking scenario complete:
- [ ] Purpose is one clear sentence
- [ ] Preconditions are specific enough to reproduce (dates, data state, Strava)
- [ ] Athlete input is exact (quoted, not paraphrased)
- [ ] Actual system output is pasted (blockquote)
- [ ] Every test row has: number, what to verify, expected behavior, Y/N result
- [ ] Decision logic references CLAUDE.md rules by name
- [ ] "What this tests that others don't" has at least 1 bullet
- [ ] Data state shows before→after for all affected files
- [ ] Screenshot attached if available (![alt](filename.png))
-->
