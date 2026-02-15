---
name: weekly-plan
description: Plan your training week. Sets how many days you'll train, picks the best days based on weather and schedule, and saves a tentative plan. Use at the start of each week (Sunday/Monday).
---

# Weekly Planner

Review last week, ask schedule preferences, build day-by-day schedule (WL + cardio), save to `data/current_week_plan.json`.

## Workflow

### Step 1: Ask the athlete (all at once)

```
Quick weekly planning:
1. Which days are you training this week? (e.g., "Tue, Thu, Sat" or "none")
2. Want to plan outdoor cardio? (yes/no — I'll check weather)
3. How are you feeling? Fatigue: low/medium/high, any pain?
4. Competition coming up? (date, or "no")
```

### Step 2: Gather data (in parallel)

1. **Last week's log** → Read `data/training_log.ndjson`. Summarize: sessions done, exercises completed vs. skipped, cardio, RPE avg, soreness trend.
2. **Program** → Read `data/program.json`. Calculate week number per CLAUDE.md formula. Look up prescribed exercises for all 5 days.
3. **PRs** → Read `data/prs.json`. Used in Step 3 to compute target weights per CLAUDE.md "Weight Guidance".
4. **Weather** (days=7) → Identify outdoor-suitable days per CLAUDE.md "Weather Preferences". Rank by quality.
5. **Strava** (days_back=7) → Classify per CLAUDE.md "Strava Activity Types". If unavailable, ask about recent cardio.

### Step 3: Build the schedule

Assign T/S/H/Hybrid per CLAUDE.md "T/S/H Session System". Priority when fewer than 5 days: T → S → H. (0=rest, 1=T, 2=T+S, 3=T+S+H, 4=+Hybrid, 5=full week). If no heavy work in 7+ days, prioritize H over S.

**Intensity:** default normal. Use condensed to pull 1-2 priority exercises from skipped days (cut accessories, max ~6 per session). Use light/mini when fatigued. See condensed example in `references/skill_schemas.md`.

**Weights:** For each exercise with a matching PR in `prs.json`, compute target weight range per CLAUDE.md "Weight Guidance" and show it inline (e.g., `Front Squat 5x5 @56-60kg`).

**Spacing:** ≥1 rest day between sessions when possible. Note carry-overs from last week.

**Cardio:** place on weather-suitable non-WL days. Bike Z2 OK adjacent to T/S. Hard run/ski never before H or heavy S.

**Competition taper:** D-10→D-5: reduce volume 20-40%. D-4→D-2: light technique. D-1: mini-T/mobility.

**Fatigue:** High/pain >5 → all mini. Medium → standard. Low → full.

### Step 4: Save the plan

Read then overwrite `data/current_week_plan.json`. Include `program_name` and `total_weeks` from program.json so `/checkin` can skip reading the program file. Schema in `references/skill_schemas.md`.

### Step 5: Output

Format per template in `references/skill_schemas.md`. Display temperatures as °C (°F) per CLAUDE.md.

## Constraints

- Never schedule more WL days than requested
- Always save to `data/current_week_plan.json` with `program_name` + `total_weeks`
- Maximum 1 protection rule
- Schedule is a suggestion — athlete can move sessions
- If weather/Strava unavailable, skip or use log data only
