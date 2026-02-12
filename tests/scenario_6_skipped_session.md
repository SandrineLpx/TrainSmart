# Scenario 6: Check-in After Skipped Session (AI-Detected via Strava)

## Skill Tested
`/checkin`

## Type
Edge case

## Purpose
Tests proactive detection of a missed session via Strava + training log cross-reference, when the athlete does not volunteer the information — and validates the carry-over and plan-update logic.

## Setup / Preconditions
- Program: Leg Drive, Week 2 of 8 (even-week pattern), started 2026-02-02
- Today: **Thursday Feb 12** — planned T2 session (Hang Clean + Jerks)
- Plan state: exists, 4 training days (Tue T, Wed S, Thu T2, Fri H)
- Completed sessions this week: Tuesday T only
- Wednesday S session was **planned but not done** (status still `"planned"`)
- Training log: no entry for Feb 11
- Strava (last 48h): WeightTraining on Feb 10 (matches Tuesday log) — **no activity on Feb 11**
- AI must detect the gap from Strava + log cross-reference — athlete did NOT volunteer that info

## Athlete Input
```
1. Sleep last night: good
2. Leg soreness (0-10): 3
3. Energy (1-5): 4
(after AI flags missed Wed session) "I had class. I skipped Wednesday."
```

## Actual System Output

> **Program:** Leg Drive | **Week 2 of 8** | **Thursday, 2026-02-12**
>
> I notice Wednesday's S session (Front Squat, Rack Drives) doesn't have a log entry, and Strava shows no activity on Feb 11. Was it skipped or just unlogged?

*After athlete confirms skipped:*

> Got it — marking Wed as skipped. You planned 4 sessions this week but missed Wednesday. Want to keep 4 sessions (carry over key exercises) or adjust to 3 for the rest of the week?

*After athlete confirms keep schedule:*

> **Today: T2 (Hang Clean + Jerks) — confirmed**
>
> Hang power clean + 2 jerks 6x(1+1+1), Jerk Recovery 6x(1+1), Cossack squats 3x10. Warm up with push press.
>
> Front Squat 3x5 carried over from skipped Wed S — do after main work if time allows.
>
> **Why:** Readiness is good. T2 is independent of squat day. Front Squat is the only priority carry-over — accessories from S dropped.
>
> **Stop rules:**
> - If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean
> - If form still degrades after dropping → switch to mini or stop after priorities
>
> **Time-flex:**
> - Short on time? Drop: Cossack squats → Front Squat carry-over. Keep hang cleans + jerk recovery.
> - Extra time? Add: Rack Drives 3x3 (from skipped S) → Paused front squat back-offs

## Tests

### Check-in Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Context line displayed | "Program: Leg Drive \| Week 2 of 8 \| Thursday, Feb 12" | Y |
| 2 | Readiness questions asked | Sleep / soreness / energy (3 questions max) | Y |
| 3 | Strava cross-referenced | Fetched last 2 days of Strava, found no Wed activity | Y |
| 4 | Missed session detected without athlete volunteering | AI noticed Wed S was planned but no log entry + no Strava activity — flagged it proactively | Y |
| 5 | Asked about missed session | AI asked if Wed was skipped or just unlogged | Y |
| 6 | Thursday session confirmed | T2 (Hang Clean + Jerks) confirmed as planned — not replaced by S | Y |
| 7 | Front Squat carry-over added | Front Squat 3x5 carried over from skipped S session (priority exercise preserved) | Y |
| 8 | Accessories from skipped S dropped | Goblet Squat, Rack Drives, pullups, Lu Raises NOT carried over (accessories cut first per rules) | Y |
| 9 | Weekly plan updated — Wed | Wednesday status changed to `"skipped"` with note | Y |
| 10 | Weekly plan updated — Thu | Thursday carry_over updated with Front Squat | Y |
| 11 | Output format — stop rules | Exactly 2 stop rules listed | Y |
| 12 | Output format — time-flex | "Short on time?" and "Extra time?" sections present | Y |
| 13 | Time-flex extras reference skipped S exercises | "Extra time" suggestions include Rack Drives or other S-day exercises | Y |
| 14 | Ask about adjusting weekly volume | When a session is skipped mid-week, AI asks: "Want to keep 4 sessions or adjust to 3?" | Y |

## Decision Logic Verified
- No Strava activity on Wed + no training log entry → skipped session detected
- Readiness OK (good sleep, soreness 3, energy 4) → no intensity downgrade needed
- Skipped S session → carry over highest-priority exercise (Front Squat) per rule: cut accessories FIRST
- T2 session preserved (clean/jerk technique work is independent of squat day)
- Back-to-back Thu-Fri lifting noted in protection rule
- Volume adjustment question asked per updated checkin Step 3

## What This Scenario Tests That Others Don't
- **Proactive gap detection**: AI discovers the missed session from data, not from the athlete
- **Strava + log cross-reference**: combines two data sources to infer what happened
- **Carry-over prioritization**: only Front Squat carried over, all accessories dropped (CLAUDE.md priority order)
- **Skipped status handling**: tests the `"skipped"` plan status (not used in other scenarios)
- **Volume adjustment question**: tests the new mid-week volume renegotiation flow

## Improvement Applied
Test #14 originally failed — the AI carried over exercises but didn't ask about adjusting weekly volume. Fix applied to `/checkin` Step 3: when a skipped session is detected, the AI now asks "Want to keep [N] sessions or adjust to [N-1]?" This was the only test failure across all 7 scenarios.

## Data State After Scenario

### training_log.ndjson
- Unchanged (no new session logged yet — this is pre-workout check-in)

### current_week_plan.json
- Tuesday: status = `"completed"`
- Wednesday: status = `"skipped"`, notes = "Had class"
- Thursday: status = `"planned"`, carry_over = `["Front Squat 3x5 (from skipped Wed S session)"]`
- Friday: status = `"planned"`
