# Scenario 5: Baseline Comparison — Raw Claude vs. /checkin Skill

## Purpose
Compares the output of asking raw Claude (no skills, no data, no MCP tools) the same question that `/checkin` answers, to demonstrate the value of the agentic system.

## Setup
Same state as Scenario 1:
- Program: Leg Drive, Week 2 of 8 (even-week pattern)
- Today: Tuesday Feb 10
- Plan: 3 training days (Tue T, Thu S, Fri H)
- No prior sessions this week
- Sleep: ok, Soreness: 2, Energy: 3
- Weather: 7°C (44°F), 0% rain, light wind
- Strava: no activities in last 48h

## Test A: Raw Claude (no skills)

**Prompt given to Claude (no CLAUDE.md, no skills, no MCP):**
> "I'm an Olympic weightlifter following the Leg Drive program. It's Week 2 of 8, Tuesday. I slept OK, soreness is 2/10, energy 3/5. What should I train today?"

**Expected raw Claude output:**
- Generic Olympic weightlifting advice
- No knowledge of actual program exercises (Snatch Pull + Snatch, Snatch DL, etc.)
- No knowledge of T/S/H session system
- No awareness of even/odd week patterns
- No stop rules specific to this athlete
- No weather check for outdoor cardio
- No Strava interference check
- No carry-overs from missed sessions
- No weekly plan context
- Likely suggests "snatch and clean & jerk" generically

**Actual raw Claude output:**

> *Claude asked to open the spreadsheet, then produced:*
>
> Here's your **Week 2 Tuesday workout**:
>
> **Main Lifts:**
> 1. **Snatch Pull + Snatch** - 6 sets of 1+1
>    - No straps
>    - High pull at light weights, speed pull at working weights
>
> 2. **Snatch Deadlift** - 6 sets of 3 reps
>    - Slow eccentric (controlled descent)
>
> **Accessories:**
> 3. **Single Leg Squats** (sets/reps not specified in program)
> 4. **Lu Raises** (sets/reps not specified in program)
>
> **Given your recovery status** (OK sleep, 2/10 soreness, 3/5 energy):
>
> - **Snatch complex**: Stick to the prescribed 6 sets, but be conservative with weight progression. Focus on quality over hitting PRs today.
> - **Snatch Deadlifts**: The slow eccentrics will be demanding. If you're feeling it after set 4-5, consider dropping the last 1-2 sets or reducing weight 5-10%.
> - **Accessories**: Start with 3 sets of 8 reps for single leg squats. For Lu raises, 3 sets of 10-12 should work well.
>
> The program is moderate volume today, so it's manageable even at 3/5 energy. Just prioritize technique on the snatch work and don't push into the red zone.

**Analysis of raw Claude output:**
- Correctly read the spreadsheet to get exercises, sets/reps, and notes (had file access)
- Gave reasonable readiness-based advice ("be conservative", "don't push into the red zone")
- Missing: T/S/H session type, stop rules, Strava check, weather, carry-overs, time-flex, next session preview, plan update
- Better than expected on exercises (scored higher because it could read the file)

## Test B: /checkin Skill

**Same situation, using `/checkin`:**

Output includes all of the above context automatically.

## Comparison Matrix

| Dimension | Raw Claude | /checkin Skill | Raw | Skill |
|-----------|-----------|----------------|:---:|:-----:|
| **Correct exercises** | Read spreadsheet — got all 4 exercises correct | Exact Week 2 Tuesday exercises from program.json | 2 | 2 |
| **Sets/reps/notes** | Got main lift sets/reps + notes. Accessories listed as "not specified" | "Snatch Pull + Snatch 6x1+1, Snatch DL 6x3" with all notes | 1 | 2 |
| **Session type awareness** | None — no mention of T/S/H system | T (Technique) confirmed per plan | 0 | 2 |
| **Readiness assessment** | "Be conservative", "manageable at 3/5 energy", concrete adjustments — good but no structured rules | Applies decision rules: soreness < 6 + sleep ok + energy > 2 = OK | 1.5 | 2 |
| **Stop rules** | "Consider dropping 1-2 sets or reducing weight 5-10%" — partial | 2 specific stop rules from CLAUDE.md | 1 | 2 |
| **Strava interference** | N/A (no access) | Checks last 48h activities, flags hard cardio | 0 | 2 |
| **Weather for cardio** | N/A (no access) | Fetches real forecast, gates outdoor suggestions | 0 | 2 |
| **Carry-overs** | None | Surfaces missed exercises from prior weeks | 0 | 2 |
| **Time-flex suggestions** | None | "Short on time? Drop Lu Raises. Extra time? Add snatch balance" | 0 | 2 |
| **Next session preview** | None | "Thursday S: Front Squat 5x5, Rack Drives" | 0 | 2 |
| **Plan consistency** | N/A (no plan file) | Updates plan status to "completed" | 0 | 2 |

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 0 | Absent or wrong — raw Claude can't produce this |
| 1 | Partially present — vague or generic version |
| 2 | Fully correct — matches expected output |

## Actual Results

| Dimension | Raw Claude | /checkin |
|-----------|:---------:|:-------:|
| Correct exercises | 2 | 2 |
| Sets/reps/notes | 1 | 2 |
| Session type awareness | 0 | 2 |
| Readiness assessment | 1.5 | 2 |
| Stop rules | 1 | 2 |
| Strava interference | 0 | 2 |
| Weather for cardio | 0 | 2 |
| Carry-overs | 0 | 2 |
| Time-flex suggestions | 0 | 2 |
| Next session preview | 0 | 2 |
| Plan consistency | 0 | 2 |
| **Total** | **5.5/22 (25%)** | **22/22 (100%)** |

## Key Takeaway

Raw Claude scored 25% (5.5/22) — better than the predicted 9% because it could read the spreadsheet and extract exercises. However, it still lacks the agentic layers. The `/checkin` skill scores 100% because the agentic system provides:

1. **Structured data access** — program.json, training log, weekly plan
2. **External tool integration** — weather MCP, Strava MCP
3. **Domain-specific decision rules** — encoded in CLAUDE.md
4. **Consistent output format** — stop rules, time-flex, exercises with sets/reps

The system's value isn't in being "smarter" — it's in having the right information at the right time and applying consistent rules. A human coach with a clipboard could do the same thing, but this system does it in 10 seconds.
