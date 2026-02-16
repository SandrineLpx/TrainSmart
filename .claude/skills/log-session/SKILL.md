---
name: log-session
description: Log a completed training session. Records what you did, compares to the program prescription, and updates your training log. Use after training.
---

# Session Logger

Record a completed session to `data/training_log.ndjson`. Compare against prescription. Check for new PRs.

## Inputs

- Log date (`today` or explicit `YYYY-MM-DD`)
- Session type/intensity and exercises performed (or `as prescribed`)
- Readiness and context fields: RPE, sleep, soreness, optional notes
- Program + PR reference files: `data/program.json`, `data/prs.json`

## Outputs

- One appended NDJSON log entry in `data/training_log.ndjson`
- Updated PR values in `data/prs.json` when a new PR is detected
- Logging confirmation output (including PR callouts if applicable)

## Workflow

### Step 0: Detect date and confirm log date

Read system date/time and show `Today: YYYY-MM-DD`.
- Default `log_date` = today
- If athlete says they are backfilling, use their provided date as `log_date`
- If `/checkin` was missed, continue and log normally

### Step 1: Ask the athlete (all at once)

1. **Log date:** `today` or `YYYY-MM-DD` (if blank/`today`, use detected date)
2. **Session type:** T / S / H / T2 / mini-T / mini-S / mini-H / cardio / recovery (+ intensity)
3. **Exercises performed:** what you did, or "as prescribed". Cardio: activity + duration + intensity.
4. **RPE (1-10)** | 5. **Sleep:** good/ok/bad | 6. **Leg soreness (0-10)** | 7. **Notes (optional)**

### Step 2: Load program + compare

Read `data/program.json`. Calculate week number from `log_date` per CLAUDE.md formula (not always from today). Match performed exercises against prescription. "as prescribed" -> all completed. Unmatched extras -> bonus entries. Cardio -> no comparison.

### Step 3: Build + save

Build entry as a single-line JSON object per schema in `references/skill_schemas.md`. Append it to `data/training_log.ndjson` using Bash: `echo '<json>' >> data/training_log.ndjson`. **Append only - never read+rewrite the file.**

### Step 4: Check PRs

Read `data/prs.json`. Compare logged weights against PR-tracked exercises (CLAUDE.md "Personal Records"). If exceeded -> update `prs.json`.

### Step 5: Output

Format per template in `references/skill_schemas.md`. Include new PRs if any.


## Failure Modes and Fallbacks

- `/checkin` not run earlier: continue and log normally
- Unknown/unmatched exercise names: log as performed; mark unmatched as extras
- Missing sets/reps in user input: use prescribed count when available
- PR file missing/unreadable: still append session log; skip PR update and note it

## Constraints

- Append only - never read+rewrite the log file
- If sets not specified, use prescribed count
- Each entry must be valid JSON on a single line (NDJSON format)
- If `/checkin` was missed, still log the session without warning/blocking
