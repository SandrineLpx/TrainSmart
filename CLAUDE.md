# Train Smart — Olympic Weightlifting Optimization System

## Athlete Profile
- Olympic weightlifter, trains ~3 days/week (days vary)
- Uses a flexible T/S/H session system (Technique/Strength/Heavy — sessions can be moved across days)
- Supplements with outdoor cardio: bike, run, ski, yoga
- Location: Kirkland, WA 98034
- Tracks all activities on Strava (cardio, gym WL sessions, yoga)

## Current Program
- File: `data/program.json` (parsed from Leg Drive.xlsx)
- 8-week periodized program, 5 prescribed days/week (Mon-Fri)
- Program start date: 2026-02-02
- To find current week: `week = ((today - 2026-02-02).days // 7) + 1`, clamped to 1-8
- Odd weeks (1,3,5,7): Clean & Jerk Mon, Yoyo Snatch Tue, BTN Jerks Wed, Front Squat Thu, Power Snatch + Power C&J Fri
- Even weeks (2,4,6,8): BTN Thrusters Mon, Snatch Pull Tue, Hang Clean Wed, Goblet+FS Thu, Snatch + C&J Fri
- Volume tapers across weeks (sets: 6→6→4→4→3→3 on main lifts)

## Training Log
- File: `data/training_log.ndjson` (NDJSON format — one JSON object per line)
- Updated by the `/log-session` skill after each session (append-only, no read+rewrite)
- Each line records: date, week, session type, exercises performed, RPE, sleep, soreness
- To read: use Read tool, parse each line as independent JSON

## T/S/H Session System

Session types (used for scheduling and logging):
- **T (Technique)**: Snatch pulls, snatch technique, pulls — maps to Tuesday program exercises
- **S (Strength)**: Squats, jerks, leg drive — maps to Monday + Thursday program exercises
- **H (Heavy)**: Heavy singles, competition lifts — maps to Friday program exercises
- **Wednesday** is a hybrid (jerk technique + snatch balance or clean + jerk work)

Each session can be run at different intensities:
- **Light (mini)**: Only the 1-2 main lifts, reduced sets — use when fatigued
- **Normal**: As prescribed in program.json
- **Condensed**: As prescribed + key exercises pulled from skipped program days

## Non-Negotiable Rules
1. Priority order: Olympic lifts > leg/trunk strength > endurance
2. Cut accessories FIRST, then lower-body volume, and ONLY LAST reduce main lift intensity
3. No unnecessary grinding: if technique degrades or fatigue is high, switch to mini or technique work

## Stop Rules (apply to ALL sessions)
- If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean
- If form still degrades after dropping → switch to mini or stop after priorities

## Session Selection Decision Rules
- If **leg soreness ≥ 6** OR **sleep bad + energy ≤ 2** → T (or mini-T) or active recovery
- If **hard run or hard ski < 24-36h** → avoid heavy S and H → do T or mini
- If no heavy work in **5-7 days** and status OK → prioritize H
- Otherwise use recommended order: **T → S → H**

## Weather Preferences
- File: `data/preferences.json`
- Outdoor training OK when: rain probability < 40%, temp > 4°C (40°F), wind < 25 mph
- Display temperatures as Celsius first with Fahrenheit in parentheses: e.g., "11°C (52°F)"
- Use the weather MCP tool (`get_forecast`) to check conditions

## Output Format (for all session recommendations)
- **Today:** T / S / H / mini-T / mini-S / mini-H / active recovery
- **Adjustments:** (max 3 bullets)
- **Why:** (max 2 lines)
- **Stop rules:** (exactly 2 rules)

## Skill Workflow
1. **Start of week:** Run `/weekly-plan` — reviews last week, asks how many days, saves schedule to `data/current_week_plan.json`
2. **Before each session:** Run `/checkin` — reads the weekly plan, asks 3 quick questions (sleep, soreness, energy), confirms or adjusts today's session
3. **After each session:** Run `/log-session` — records what was done, compares to prescription, updates the training log

## Strava Activity Types

The athlete tracks all training on Strava. When reading Strava data, classify activities:
- **Run, NordicSki, BackcountrySki** → hard cardio, interference signal (avoid heavy S/H next day)
- **Ride** → easy cardio (low interference unless >90 min)
- **WeightTraining** → gym WL session. Cross-reference with training log — if no matching log entry, remind to `/log-session`
- **Yoga** → recovery/mobility, positive readiness signal
- **Walk, Hike** → ignore (no impact)

## Personal Records
- File: `data/prs.json`
- Tracks PRs for: Snatch, Power Snatch, Clean, Power Clean, Jerk, Clean & Jerk, Back Squat, Front Squat, Deadlift, Snatch Balance, Snatch Deadlift
- When `/log-session` records a weight that exceeds the current PR for a tracked exercise, update `prs.json` with the new weight and date
- Only compare against PR-tracked exercises (competition lifts, power variants, strength lifts)
- When a new PR is set, include it in the log confirmation output (e.g., "PR! Snatch 59kg (was 57kg)")

## Data File Paths
- Program: `data/program.json`
- Training log: `data/training_log.ndjson` (NDJSON — one JSON object per line, append-only)
- Weekly plan: `data/current_week_plan.json`
- Personal records: `data/prs.json`
- Preferences: `data/preferences.json`
- Strava config: `data/strava_config.json`
