# Scenario 2: Check-in When Today's Training Already Completed

## Skill Tested
`/checkin`

## Type
Edge case

## Purpose
Tests that the system detects an already-completed session and skips the full check-in flow — avoids redundant questions and duplicate recommendations.

## Setup / Preconditions
- Program: Leg Drive, Week 2 of 8 (even-week pattern), started 2026-02-02
- Today: **Tuesday Feb 10** — T session already completed and logged
- Plan state: exists, 3 training days (Tue T, Thu S, Fri H)
- Completed sessions this week: Tuesday T (RPE 7, all exercises done)
- Training log: 5 entries (4 from Week 1 + today's T)
- Strava (last 48h): WeightTraining on 2/10 (matches logged T)
- Weather: not relevant

## Athlete Input
```
(none — athlete runs /checkin after already training)
```

## Actual System Output

> **Program:** Leg Drive | **Week 2 of 8** | **Tuesday, 2026-02-10**
>
> You've already completed today's T session — nice work. Snatch Pull + Snatch, Snatch DL, Single Leg Squat, Lu Raises. RPE 7.
>
> **Up next:**
> - **Wednesday:** Bike Z2, 30-45 min (weather permitting)
> - **Thursday:** S (Strength) — Goblet Squat, Front Squat 5x5, Rack Drives 4x3 + DB Row 3x15 carry-over
> - **Friday:** H (Heavy) — Snatch + Clean & Jerk heavy singles

## Tests

### Check-in Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Context line displayed | "Program: Leg Drive \| Week 2 of 8 \| Tuesday, Feb 10" | Y |
| 2 | Detects session already completed | Does NOT ask sleep/soreness/energy questions — recognizes today's T is done | Y |
| 3 | References logged session | Mentions today's completed T session (exercises, RPE, or summary) | Y |
| 4 | Points to next session | References Thursday S session (Goblet Squat, Front Squat 5x5, Rack Drives) | Y |
| 5 | Mentions carry-over | DB Row 3x15 carry-over on Thursday noted | Y |
| 6 | Cardio suggestion | Mentions Wednesday Bike Z2 (30-45 min) as next activity | Y |
| 7 | No session recommendation generated | Does NOT output a full session prescription (exercises, stop rules, time-flex) | Y |
| 8 | No adjustment logic triggered | Does NOT attempt to switch or modify a session type | Y |

## Decision Logic Verified
- Plan status = `"completed"` for today → skip check-in questions entirely
- Training log confirms session already recorded for today's date → no duplicate prompt
- Next planned session (Thursday S) surfaced as lookahead
- Cardio suggestion for off-day (Wednesday) included
- No stop rules or time-flex output needed (not prescribing a session)

## What This Scenario Tests That Others Don't
- **Duplicate detection**: system recognizes a completed session and short-circuits the full check-in flow
- **Graceful no-op**: instead of erroring or re-prescribing, it summarizes what was done and previews what's next
- **Question suppression**: verifies the 3 readiness questions are skipped when not needed

## Data State After Scenario

### training_log.ndjson
- Unchanged (no new entry — athlete didn't train again)

### current_week_plan.json
- Unchanged:
  - Tuesday: status = "completed"
  - Thursday: status = "planned"
  - Friday: status = "planned"
