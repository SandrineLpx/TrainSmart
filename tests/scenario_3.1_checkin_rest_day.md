# Scenario 3.1: Check-in on a Rest / Cardio Day

## Skill Tested
`/checkin`

## Type
Edge case

## Purpose
Tests that the system correctly handles a non-lifting day: surfaces the cardio suggestion with weather gating, previews the next lifting session, and does not prescribe a weightlifting session.

## Setup / Preconditions
- Program: Leg Drive, Week 2 of 8 (even-week pattern), started 2026-02-02
- Today: **Wednesday Feb 11** — not a planned lifting day
- Plan state: exists, 3 training days (Tue T, Thu S, Fri H)
- Completed sessions this week: Tuesday T
- Training log: 5 entries (4 from Week 1 + Tuesday's T)
- Strava (last 48h): WeightTraining on 2/10 (matches logged T)
- Weather: checked (cardio suggestion for today triggers weather fetch)

## Athlete Input
```
1. Sleep last night: good
2. Leg soreness (0-10): 3
3. Energy (1-5): 4
```

## Actual System Output

> **Program:** Leg Drive | **Week 2 of 8** | **Wednesday, 2026-02-11**
>
> Today is a rest/cardio day — no lifting planned.
>
> **Cardio suggestion:** Bike Z2, 30-45 min
> Weather: 11°C (52°F), 0% rain, 6 mph wind — good for an outdoor ride.
>
> **Heads up:** If the ride is hard or long (>60 min), your legs may feel it tomorrow for Thursday's S session (Front Squat 5x5, Rack Drives). Keep it easy Z2.
>
> **Up next:**
> - **Thursday:** S (Strength) — Goblet Squat, Front Squat 5x5, Rack Drives 4x3 + DB Row 3x15 carry-over
> - **Friday:** H (Heavy) — Snatch + Clean & Jerk heavy singles

![Screenshot](3.1_resteDay.png)

## Tests

### Check-in Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Context line displayed | "Program: Leg Drive \| Week 2 of 8 \| Wednesday, Feb 11" | Y |
| 2 | Identifies rest/cardio day | Recognizes today is NOT a planned lifting day — states it clearly | Y |
| 3 | Still asks readiness questions | Asks sleep/soreness/energy (useful for tracking and informing tomorrow's session) | Y |
| 4 | Cardio suggestion surfaced | Mentions Bike Z2 (30-45 min) from the weekly plan's cardio_suggestions | Y |
| 5 | Weather check performed | Fetches weather for today (cardio day with outdoor suggestion) | Y |
| 6 | Weather-gated recommendation | If weather is good → confirm outdoor ride; if bad → suggest indoor alternative or skip | Y |
| 7 | Next lifting session previewed | References Thursday S session (Goblet Squat, Front Squat 5x5, Rack Drives) | Y |
| 8 | Carry-overs mentioned | DB Row 3x15 carry-over on Thursday noted | Y |
| 9 | No full session prescription | Does NOT output stop rules, time-flex, or adjustment bullets (no lifting session to prescribe) | Y |
| 10 | No session type recommended | Does NOT recommend T/S/H/mini — today is rest/cardio | Y |
| 11 | Protection rule awareness | Notes that hard cardio today could affect tomorrow's S session (per protection_rule in plan) | Y |

## Decision Logic Verified
- Today not in `schedule[].date` as a lifting day → no session prescription
- Today IS in `cardio_suggestions[].date` → surface the cardio suggestion
- Cardio day triggers weather check (per SKILL.md Step 2, rule 4)
- Protection rule from weekly plan applies: if hard ride/run today, check legs at next check-in
- Readiness questions still useful — data feeds into tomorrow's Thu S decision
- No stop rules or time-flex needed (not prescribing a lifting session)

## What This Scenario Tests That Others Don't
- **Rest day behavior**: only scenario where today has no lifting session at all
- **Weather MCP integration**: only scenario that triggers the weather tool (cardio day with outdoor suggestion)
- **Cross-day awareness**: system warns about tomorrow's impact without being asked
- **Output suppression**: verifies stop rules and time-flex are correctly omitted on non-lifting days

## Data State After Scenario

### training_log.ndjson
- Unchanged (no lifting session logged)

### current_week_plan.json
- Unchanged:
  - Tuesday: status = "completed"
  - Thursday: status = "planned"
  - Friday: status = "planned"
