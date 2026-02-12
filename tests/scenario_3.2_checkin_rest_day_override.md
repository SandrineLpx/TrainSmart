# Scenario 3.2: Check-in on Rest Day — Athlete Overrides to Train + Adds 4th Session

## Skill Tested
`/checkin`

## Type
Edge case

## Purpose
Tests the system's ability to handle mid-week plan changes: athlete overrides a rest day, requests an extra session, and the system restructures the weekly plan on the fly.

## Setup / Preconditions
- Program: Leg Drive, Week 2 of 8 (even-week pattern), started 2026-02-02
- Today: **Wednesday Feb 11** — not a planned lifting day (cardio suggestion: Bike Z2)
- Plan state: exists, 3 training days (Tue T, Thu S, Fri H)
- Completed sessions this week: Tuesday T
- Training log: 5 entries (4 from Week 1 + Tuesday's T)
- Strava (last 48h): WeightTraining on 2/10 (matches logged T), no cardio
- Weather: checked (cardio suggestion for today)

## Athlete Input
```
1. Sleep last night: good
2. Leg soreness (0-10): 4
3. Energy (1-5): 4
(after rest day response) "I will train this morning instead"
(after session recommendation) "I will do 4 sessions this week"
```

## Actual System Output

> **Program:** Leg Drive | **Week 2 of 8** | **Wednesday, 2026-02-11**
>
> Today is a rest/cardio day — Bike Z2 suggested (30-45 min). Weather looks good.
>
> **Up next:** Thursday S (Front Squat 5x5, Rack Drives, DB Row carry-over).

*After athlete overrides:*

> **Today: S (Strength) — pulled forward from Thursday**
>
> Goblet Squat 3x10, Front Squat 5x5, Rack Drives 4x3, BTN Pullups 3x10, Lu Raises 3x12 + DB Row 3x15 carry-over.
>
> **Why:** Readiness is good (sleep good, soreness 4, energy 4). Pulling S to Wed gives better spacing — Wed S → Fri H instead of back-to-back Thu S → Fri H.
>
> **Stop rules:**
> - If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean
> - If form still degrades after dropping → switch to mini or stop after priorities

*After 4th session request:*

> Updated layout: **Tue T (done) → Wed S → Thu T2 → Fri H**
>
> Thursday now picks up Wed program day: Hang power clean + 2 jerks 6x(1+1+1), Jerk Recovery 6x(1+1), Cossack squats 3x10. Warm up with push press.
>
> Want me to update the weekly plan?

## Tests

### Check-in Tests — Initial Rest Day Response

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Context line displayed | "Program: Leg Drive \| Week 2 of 8 \| Wednesday, Feb 11" | Y |
| 2 | Identifies rest/cardio day | Recognizes today is NOT a planned lifting day | Y |
| 3 | Still asks readiness questions | Asks sleep/soreness/energy (3 questions only) | Y |
| 4 | Cardio suggestion surfaced | Mentions Bike Z2 (30-45 min) | Y |
| 5 | Weather check performed | Fetches weather (outdoor cardio day) | Y |
| 6 | Next lifting session previewed | References Thursday S session | Y |

### Check-in Tests — Override to Train

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 7 | Accepts override gracefully | Does not push back or re-ask — proceeds to recommend a session | Y |
| 8 | Recommends correct session type | Next unfinished session is S (Thursday) — recommends pulling S forward | Y |
| 9 | Readiness validates for S | Soreness 4 < 6, sleep good, energy 4 > 2 → S is OK | Y |
| 10 | No interference flagged | Strava shows only Tue WeightTraining (matches logged T) — no hard cardio | Y |
| 11 | Full session prescription output | Exercises listed, adjustments, why, stop rules, time-flex — all present | Y |
| 12 | Stop rules present | Exactly 2 stop rules from CLAUDE.md | Y |
| 13 | Time-flex suggestions present | "Short on time?" and "Extra time?" sections with exercise names | Y |
| 14 | Spacing rationale | Mentions Wed S → Fri H is better spacing than back-to-back Thu/Fri | Y |

### Check-in Tests — 4th Session Addition

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 15 | Accepts 4-session request | Does not push back — proposes a 4-day layout | Y |
| 16 | 4th session sourced correctly | Picks up Wed program day (Hang Power Clean + 2 Jerks) — exercises not yet covered this week | Y |
| 17 | 4th session typed as T2/hybrid | Classified as T2 or hybrid, not S or H (it's clean/jerk technique work) | Y |
| 18 | 4th session placed on Thursday | Slots into Thu (the day freed up by pulling S to Wed) | Y |
| 19 | Schedule layout correct | Tue T (done) → Wed S → Thu T2 → Fri H | Y |
| 20 | Cardio suggestion moved | Bike Z2 removed from Wed, only Sat/Sun cardio remains | Y |
| 21 | Asks before updating plan | Confirms "Want me to update the weekly plan?" before writing | Y |

### Plan Update Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 22 | training_days_planned updated | Changed from 3 to 4 | Y |
| 23 | Wed S entry added to schedule | New entry: day=Wednesday, type=S, status=planned, notes mention pulled forward | Y |
| 24 | Thu entry replaced | Changed from S to T2, exercises = Hang power clean + 2 jerks, Jerk Recovery, Cossack squats | Y |
| 25 | Thu exercises match program.json | Week 2 Wednesday: Hang power clean + 2 jerks 6x(1+1+1), Jerk Recovery 6x(1+1), Cossack squats 3x10 | Y |
| 26 | Thu notes include warm-up tip | "Warm up with push press" from program.json notes | Y |
| 27 | Fri H unchanged | Same key_exercises, status still "planned" | Y |
| 28 | Tue T unchanged | Status still "completed" | Y |
| 29 | Wed cardio suggestion removed | Only Sat/Sun cardio suggestion remains in cardio_suggestions array | Y |
| 30 | Protection rule updated | Mentions monitoring soreness across Wed-Thu-Fri back-to-back block | Y |
| 31 | Notes updated | Reflects 4-session change and rationale | Y |
| 32 | Carry-over preserved | DB Row 3x15 still on Wed S (carried from original Thu S) | Y |

## Decision Logic Verified
- Rest day override: athlete explicitly requests training → recommend next unfinished session (S)
- Readiness check: soreness 4 + sleep good + energy 4 → S is appropriate (no downgrade needed)
- No hard cardio interference in last 24-36h
- Session order T → S → H maintained (T done Tue, S pulled to Wed)
- 4th session: Wed program day (Hang Clean + Jerks) is the most valuable uncovered day — hybrid technique work
- Thu placement creates T → S → T2 → H flow with technique buffer before heavy day
- Plan update only after athlete confirms

## What This Scenario Tests That Others Don't
- **Rest day override**: athlete contradicts the plan — system adapts instead of insisting
- **Dynamic plan restructuring**: 3-day plan becomes 4-day mid-week with correct exercise sourcing
- **Session sourcing logic**: 4th session correctly pulls from an uncovered program day (Wednesday)
- **Plan file mutation**: largest data change — updates schedule, cardio, protection rule, notes, and training_days_planned
- **Multi-turn conversation**: 3 phases (rest day → override → 4th session) in a single `/checkin` interaction

## Data State After Scenario

### training_log.ndjson
- Unchanged (session not yet completed — athlete hasn't trained yet)

### current_week_plan.json
- training_days_planned: 4
- Schedule: Tue T (completed) → Wed S (planned) → Thu T2 (planned) → Fri H (planned)
- Cardio: only Sat/Sun suggestion remains
- Protection rule: updated for 3-day lifting block
