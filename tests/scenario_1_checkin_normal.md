# Scenario 1: Normal Check-in + Log Session (Happy Path)

## Skill Tested
`/checkin` followed by `/log-session`

## Type
Happy path

## Purpose
Validates the core end-to-end workflow: check in with good readiness, confirm the planned session, train, log the session — the most common daily use case.

## Setup / Preconditions
- Program: Leg Drive, Week 2 of 8 (even-week pattern), started 2026-02-02
- Today: **Tuesday Feb 10** — planned T (Technique) session
- Plan state: exists, 3 training days (Tue T, Thu S, Fri H)
- Completed sessions this week: none (last session was Fri Feb 7, Week 1 H)
- Training log: 4 entries from Week 1
- Strava (last 48h): no activities
- Weather: not checked (no cardio suggestion for today)

## Athlete Input
```
1. Sleep last night: ok
2. Leg soreness (0-10): 2
3. Energy (1-5): 3
```

## Actual System Output

> **Program:** Leg Drive | **Week 2 of 8** | **Tuesday, 2026-02-10**
>
> **Today: T (Technique) — confirmed**
>
> Snatch Pull + Snatch 6x(1+1) — no straps. High pull at light weight, speed pull at working weight.
> Snatch Deadlift 6x3
> Single Leg Squat 3x10 each
> Lu Raises 3x12
>
> **Why:** Readiness is good (sleep ok, soreness 2, energy 3). T session as planned — first session of the week, no interference.
>
> **Stop rules:**
> - If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean
> - If form still degrades after dropping → switch to mini or stop after priorities
>
> **Time-flex:**
> - Short on time? Drop: Lu Raises. Keep snatch complex + snatch DL.
> - Extra time? Add: Snatch balance 3x1, Ab Wheel 3x10

## Tests

### Check-in Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Context line displayed | "Program: Leg Drive \| Week 2 of 8 \| Tuesday, Feb 10" | Y |
| 2 | Correct session confirmation | Confirm **T (Technique)** as planned (no adjustment needed) | Y |
| 3 | Exercises from even-week Tuesday | Snatch Pull + Snatch 6x1+1, Snatch Deadlift 6x3, Single Leg Squat, Lu Raises | Y |
| 4 | Exercise notes from program.json | "No straps. High pull at light weight, speed pull at working weight" on snatch complex | Y |
| 5 | Output format — time-flex suggestions | "Short on time?" and "Extra time?" sections present | Y |
| 6 | Output format — stop rules | Exactly 2 stop rules listed | Y |
| 7 | No unnecessary adjustment | Session confirmed as planned (readiness OK for T) | Y |
| 8 | Strava check — no interference | No cardio flagged, no unlogged gym sessions flagged | Y |

### Log Session Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 9 | Asks only missing info | Only RPE and post-session soreness (sleep already known from check-in) | Y |
| 10 | Exercises logged correctly | Snatch Pull + Snatch 6x(1+1) @40kg, Snatch DL 6x3 @60kg, SL Squat 3x10 @15kg DB, Lu Raises 3x8 @5kg | Y |
| 11 | All marked completed | All 4 exercises `"completed": true` | Y |
| 12 | Skipped = None | No prescribed exercises missed | Y |
| 13 | Log entry appended | New entry added to `training_log.ndjson` without overwriting existing entries (5 total) | Y |
| 14 | Weekly plan updated | Tuesday status changed from `"planned"` to `"completed"` in `current_week_plan.json` | Y |
| 15 | Upcoming session mentioned | References Thursday S session (Goblet Squat, Front Squat, Rack Drives) | Y |
| 16 | Cardio suggestion mentioned | Z2 bike on Wednesday noted | Y |
| 17 | Output format — log confirmation | Performed list with checkmarks, Skipped section, Stats line, Log line | Y |

## Decision Logic Verified
- Soreness 2 < 6 + sleep ok (not bad) + energy 3 > 2 = readiness OK → confirm planned session (no switch)
- T session is appropriate even when slightly tired (technique is always fine)
- No hard cardio in last 24-36h = no interference protection needed
- Recommended order T → S → H followed (T first this week)

## What This Scenario Tests That Others Don't
- **Full end-to-end flow**: only scenario that tests both `/checkin` and `/log-session` together
- **Happy path confirmation**: verifies the system doesn't over-adjust when readiness is fine
- **Log accuracy**: confirms exercises, weights, RPE, and plan status update after logging

## Data State After Scenario

### training_log.ndjson
- 5 entries total (4 from Week 1 + 1 new)
- New entry: 2026-02-10, Week 2, Tuesday, T, RPE 7, sleep ok, soreness 4

### current_week_plan.json
- Tuesday: status = "completed"
- Thursday: status = "planned"
- Friday: status = "planned"
