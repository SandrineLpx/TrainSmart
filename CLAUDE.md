# Train Smart — Olympic Weightlifting Optimization System

## Athlete Profile
- Olympic weightlifter, trains ~3 days/week (days vary)
- Uses a flexible T/S/H session system (Technique/Strength/Heavy — sessions can be moved across days)
- Supplements with outdoor cardio: bike, run, ski.
- Tracks all activities on Strava (cardio, gym WL sessions, yoga)

## Current Program
- File: `data/program.json` (parsed from Leg Drive.xlsx)
- Program start date and week calculation formula are in `data/preferences.json` (`program_start_date`)
- To find current week: `week = ((today - program_start_date).days // 7) + 1`, clamped to 1-8
- Read `data/program.json` for weekly exercises, sets, reps, and notes

## Training Log
- File: `data/training_log.ndjson` (NDJSON format — one JSON object per line)
- Updated by the `/log-session` skill after each session (append-only, no read+rewrite)
- Each line records: date, week, session type, exercises performed, RPE, sleep, soreness
- To read: use Read tool, parse each line as independent JSON

## T/S/H Session System

Session types (used for scheduling and logging):
- **T (Technique)**: Snatch pulls, snatch technique, pulls
- **S (Strength)**: Squats, jerks, leg drive
- **H (Heavy)**: Heavy singles, competition lifts
- **T2 (Hybrid)**: Jerk technique + snatch balance or clean + jerk work. Use as an optional 4th session when readiness/freshness is good and weekly logs show uncovered priority work

Session-to-program-day mapping is defined per week in `data/program.json` — read it to determine which exercises belong to each session type.

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
- Thresholds (rain, temp, wind) are in `data/preferences.json` under `outdoor_thresholds`
- Display temperatures as Celsius first with Fahrenheit in parentheses: e.g., "11°C (52°F)"
- Use the weather MCP tool (`get_forecast`) to check conditions

## Output Format (for all session recommendations)
- **Today:** T / S / H / mini-T / mini-S / mini-H / active recovery
- **Adjustments:** (max 3 bullets)
- **Why:** (max 2 lines)
- **Stop rules:** (exactly 2 rules)

## Date Rule
- At the start of `/checkin`, read the system date/time and use that date as "today" for plan matching and outputs.

## Skill Workflow
1. **Start of week:** Run `/weekly-plan` — reviews last week, asks which days you can train, saves schedule to `data/current_week_plan.json`
2. **Before each session:** Run `/checkin` — reads the weekly plan, asks 3 quick questions (sleep, soreness, energy), confirms or adjusts today's session
   - If no weekly plan exists (`data/current_week_plan.json` missing), `/checkin` offers: (1) run `/weekly-plan` now, or (2) a quick fallback for today.
3. **After each session:** Run `/log-session` — records what was done, compares to prescription, updates the training log

## Strava Activity Types

The athlete tracks all training on Strava. When reading Strava data, classify activities:
- **Run, NordicSki, BackcountrySki** → hard cardio, interference signal (avoid heavy S/H next day)
- **Ride** → easy cardio (low interference unless >90 min)
- **WeightTraining** → gym WL session. Cross-reference with training log — if no matching log entry, remind to `/log-session`
- **Yoga** → recovery/mobility, positive readiness signal
- **Walk, Hike** → ignore (no impact)

## Weight Guidance

When `/weekly-plan` or `/checkin` outputs exercises, read `data/prs.json` and compute target weights for PR-tracked exercises. Match the exercise name in the program to the closest PR entry.

**Rep-based percentage ranges** (of 1RM PR, based on standard strength training conventions):

| Reps | % of PR | Use case |
|------|---------|----------|
| 1 ("heavy singles") | 85-95% | H-day competition lifts |
| 1+1, 1+2 (complexes) | 75-85% | Technique complexes, C&J+Jerk |
| 2 | 80-88% | Pause squats, BTN thrusters |
| 3 | 75-85% | Front squat triples, rack drives |
| 5 | 70-80% | Front squat 5x5, strength work |
| 6+ | 60-70% | RDLs, goblet squats, accessories |

**Note-based overrides** (program notes take precedence):
- "heavy singles" / "as heavy as possible" → 90-95%
- "working weight" / "speed pull" → 70-80%
- "controlled eccentric" / "slow eccentric" → 70-80% (tempo reduces load)
- "Go heavy on these" → 85-95%

**Output format:** Show weight in kg after the set/rep scheme.
Example: `Front Squat 5x5 @56-60kg (75-80% of 75kg PR)`

**Rules:**
- Round to nearest 0.5kg
- Show as a range (low-high), not a single number — athlete picks based on feel
- If no matching PR exists for an exercise, omit the weight (don't guess)
- Accessories without a PR (Lu Raises, Cossack squats, etc.) → no weight shown
- When readiness is bad (soreness ≥ 6 or energy ≤ 2), use the low end of the range

## Personal Records
- File: `data/prs.json` — read it for the list of tracked exercises and current PRs
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
