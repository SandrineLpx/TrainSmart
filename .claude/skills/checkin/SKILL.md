---
name: checkin
description: Quick pre-workout check-in. Reads your weekly plan, checks how you feel, and confirms or adjusts today's session. Use right before training — takes 10 seconds.
---

# Pre-Workout Check-in

Fast confirmation before training. Reads the weekly plan, asks how you feel, confirms or adjusts.

## Inputs

- Athlete readiness inputs: sleep, leg soreness, energy
- Optional extra context volunteered by athlete
- Current weekly plan (`data/current_week_plan.json`)
- Supporting context: training log, PRs, Strava (if available), weather (if cardio is suggested)

## Outputs

- Today's recommended session type/intensity (confirm or adjust)
- Exercise-level adjustments with stop rules and time-flex options
- Plan update in `data/current_week_plan.json` when schedule/session changes

## Workflow

### Step 0: Show context

Read `data/current_week_plan.json` (contains `program_name`, `total_weeks`, `week_number`). Display one line:

```
**Program:** [program_name] | **Week [week_number] of [total_weeks]** | **[Today's day], [date]**
```

Do NOT read `program.json` here — the plan already has everything needed.

### Step 1: Ask (3 questions only)

```
Pre-workout check:
1. Sleep last night: good / ok / bad
2. Leg soreness (0-10):
3. Energy (1-5):
```

If the athlete volunteers extra info, use it. Don't ask for more.

### Step 2: Gather data (in parallel)

1. **Weekly plan** → already loaded in Step 0. Find today's session. If no plan exists → offer: (1) run `/weekly-plan` or (2) quick fallback (read `program.json` + apply decision rules).
2. **Training log** → Read `data/training_log.ndjson`. Check completed vs. missed sessions this week + recent cardio (48h).
3. **PRs** → Read `data/prs.json`. Used in Step 4 to show target weights per CLAUDE.md "Weight Guidance".
4. **Strava** (days_back=2) → Classify per CLAUDE.md "Strava Activity Types". If unavailable or returns `"status": "not_configured"`, skip silently and rely on training log for recent activity data.
5. **Weather** (days=1) → Only if today has a cardio suggestion in the plan.

### Step 3: Decide

Apply CLAUDE.md "Session Selection Decision Rules". If readiness is BAD (soreness ≥ 6 OR bad sleep + energy ≤ 2): S→mini-S/T, H→mini-T/recovery, Condensed→drop extras. T is always OK.

**Missed sessions:** If a planned session has no matching log entry and no Strava activity for that date, flag it. Ask if it was skipped or just unlogged. If skipped: mark it `"skipped"` in the plan, carry over 1-2 key exercises (cut accessories), and ask: "Want to keep [N] sessions this week or adjust to [N-1]?"
**Hard cardio in last 24-36h:** apply protection rule from plan, or switch to T/mini.
**Not a planned day:** Ask the athlete what they want to do:
1. **Pull forward next session** — carry over the next planned session to today (move it, mark original day as `"moved"`). Apply readiness adjustments as normal.
2. **Just log training** — skip session planning, keep the weekly plan as-is. Athlete will use `/log-session` afterward to record whatever they do.
3. **Add a hybrid (T2) session** — add an extra session for the week (e.g., training 4 days instead of 3). Build a T2 per CLAUDE.md rules: jerk technique + snatch balance or clean + jerk work, only when readiness/freshness is good and weekly logs show uncovered priority work. If readiness is bad, suggest option 1 or 2 instead.

### Step 3b: Time-flex suggestions

**Short on time?** Drop: accessories → carry-overs → lower-priority strength. Never drop main lift(s).
**Extra time?** Add: carry-overs → skipped-day accessories → back-off sets.
Keep each list to 2-3 items with exercise names.

### Step 4: Output

Format per templates in `references/skill_schemas.md` (confirming / adjusting / no-plan). Always include 2 stop rules from CLAUDE.md + time-flex lines. Show target weights per CLAUDE.md "Weight Guidance" for exercises with a matching PR. When readiness is bad, use the low end of the range.

### Step 5: Update plan if changed

If today was **not in the schedule** or the recommended session **differs from the plan** (type or intensity changed):
- Read `data/current_week_plan.json`, update the `schedule` array (add today's entry or modify the existing one), and write it back.
- If a session was pulled forward from another day, mark that day's status as `"moved"`.
- This keeps the plan in sync so the next `/checkin` sees accurate state.
- Skip this step if the session matches the plan exactly.


## Failure Modes and Fallbacks

- Missing weekly plan file: offer `(1) /weekly-plan` or `(2) quick fallback for today`
- Strava unavailable/not configured: continue using training log only
- Weather unavailable: skip weather-based cardio gating and continue
- Tool/read errors on optional data: continue with available inputs; do not block the check-in

## Constraints

- Max 3 questions
- Never recommend S or H when soreness ≥ 6
- Always include 2 stop rules (CLAUDE.md)
- Use the weekly plan — don't recalculate from scratch
- If tools fail, continue without them
