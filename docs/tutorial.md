# TrainSmart — An Agentic AI System for Olympic Weightlifting Training Optimization

**MSIS 549B – Agentic AI for Real-World Tasks (HW2)**
University of Washington, Foster School of Business — February 2026

- **GitHub:** [github.com/SandrineLpx/TrainSmart](https://github.com/SandrineLpx/TrainSmart)
- **Demo Video:** OneDrive Link

---

## 1. Problem Statement

### The Pain Point

I am an Olympic weightlifter following a coach-prescribed 5-day program on an 8-week periodized cycle. In practice, I train roughly 3 days per week. Between graduate school and frequent outdoor activities (skiing, cycling, hiking), the 5-day prescription rarely matches my available schedule. This mismatch leads to a daily dilemma:

- **Which session do I run today?** The program prescribes Monday through Friday, but I typically train Tuesday, Thursday, and Friday — or whatever days fit that week.
- **What intensity?** If I am sore from yesterday's ski or my sleep was poor, should I go lighter?
- **What exercises carry over?** If I skip Thursday's squat day, does Front Squat just disappear, or should it move to Friday?
- **When is outdoor cardio safe?** A hard run before a heavy day wrecks performance, but a road bike ride is fine.

Currently, I record my sessions in a logbook based on gut feeling, spending 5–10 minutes before each session deciding without a clear plan.

### Why an Agentic Workflow

A single LLM prompt cannot solve this problem, because the decision requires:

1. **Structured data access** — reading the current week's program, the training log, and the weekly plan.
2. **Persistent state** — the weekly plan must survive between sessions, and the training log must accumulate over weeks.
3. **Domain-specific rules** — stop rules, session selection thresholds, and priority ordering refined over years.
4. **Real-time external data** — weather (for cardio planning) and Strava activities (to detect interference from hard cardio).

An agentic system with multiple skills and MCP tools can orchestrate all of these in a 20-second pre-workout check-in.

### Tech Stack

| Component | Tool |
|-----------|------|
| LLM / IDE | Claude Code (VS Code extension), Claude Sonnet or Opus |
| Skill files | 3 Claude Code Skills (Markdown, in `.claude/skills/`) |
| MCP servers | 2 Python servers using FastMCP |
| Domain rules | `CLAUDE.md` — single source of truth |
| Language | Python 3.12+ |
| Data files | JSON + NDJSON (program, plan, log, PRs, preferences) |

---

## 2. System Design

### Architecture Overview

The system has three layers: `CLAUDE.md` provides domain rules loaded automatically as context; three skill files orchestrate the workflow; and two MCP servers plus local data files supply real-time and persistent data.

```
 CLAUDE.md
 Domain rules, decision logic, stop rules,
 session types, Strava classification, PRs
 |
 3 Skills (SKILL.md files)
 /weekly-plan -> /checkin -> /log-session
 (plan week) (confirm) (record session)
 | | |
 Weather MCP Strava MCP Data Files
 (Open-Meteo) (API v3) JSON / NDJSON
```

### CLAUDE.md — The Domain Brain

`CLAUDE.md` (~120 lines) contains all domain knowledge that skills reference but never duplicate:

- **Athlete profile:** 3 days/week, Kirkland WA, Strava-tracked
- **T/S/H session system:** Technique / Strength / Heavy, each with light/normal/condensed intensities
- **Session selection rules:** threshold-based (soreness >= 6 → no S/H; bad sleep + energy <= 2 → T only)
- **Stop rules:** 2 universal rules that appear in every session output
- **Priority order:** Olympic lifts > strength > endurance > accessories
- **Strava classification:** Run/Ski = interference; Ride = low impact; Yoga = recovery
- **Weather thresholds:** rain < 40%, temp > 4°C, wind < 25 mph

Skills reference `CLAUDE.md` by section name rather than repeating content. One edit to a threshold propagates to all three skills automatically.

### The Three Skills

| Skill | When | Input | Output | Files Written |
|-------|------|-------|--------|---------------|
| `/weekly-plan` | Start of week | Training days, fatigue, cardio preference | Day-by-day schedule + weather advisory | `current_week_plan.json` |
| `/checkin` | Before each session | Sleep, soreness (0-10), energy (1-5) | Session confirmation or adjustment + stop rules | `current_week_plan.json` (if changed) |
| `/log-session` | After each session | Session type, exercises, RPE | Log confirmation, skipped exercises, PRs | `training_log.ndjson`, `prs.json` |

### T/S/H Session System

| Type | Focus | Program Day | Priority |
|------|-------|-------------|----------|
| T (Technique) | Snatch pulls, snatch work | Tuesday | 1st — always safe |
| S (Strength) | Squats, jerks, leg drive | Monday + Thursday | 2nd |
| H (Heavy) | Competition lifts, heavy singles | Friday | 3rd |
| T2 (Hybrid) | Clean/jerk technique + uncovered priority work | 4th session only | 4th |

Day-count mapping: 0 days = rest week; 1 = T; 2 = T+S; 3 = T+S+H; 4 = T+S+H+T2; 5 = full program week.

Override rule: if no heavy work in 7+ days, prioritize H over S.

Every session type is available in three intensity levels: **Light (mini)** (1-2 primary lifts, fewer sets); **Normal** (standard prescription); **Condensed** (standard + key exercises from skipped days).

### MCP Servers

| Server | API | Auth | Purpose |
|--------|-----|------|---------|
| `weather_mcp.py` | Open-Meteo | None (free) | 7-day forecast; gates outdoor cardio suggestions. 12-hour cache. |
| `strava_mcp.py` | Strava API v3 | OAuth2 | Recent activities; detects hard cardio interference; flags unlogged gym sessions. 6-hour cache. |

### Data Files

| File | Format | Purpose |
|------|--------|---------|
| `data/program.json` | JSON | 8-week periodized program (parsed from coach's Excel) |
| `data/current_week_plan.json` | JSON | Active weekly schedule (written by `/weekly-plan`, read by `/checkin`) |
| `data/training_log.ndjson` | NDJSON | Append-only session log (one JSON object per line) |
| `data/prs.json` | JSON | Personal records for 11 tracked lifts |
| `data/preferences.json` | JSON | Location coordinates, weather thresholds |
| `data/strava_config.json` | JSON | OAuth tokens (gitignored) |

---

## 3. Building Process

### Tools and LLMs Used

The entire system was built in Claude Code (VS Code extension) using Claude Sonnet or Opus. Claude Code was used to generate skill files, write both MCP servers, write the Excel parser, iterate on prompts, and run benchmark scenarios. Python was used for MCP servers (fastmcp) and utility scripts (openpyxl for Excel parsing).

### Build Timeline

| Iteration | What Changed | Key Decision |
|-----------|-------------|--------------|
| 1 | Initial build: 3 skills, 2 MCP servers, data layer, CLAUDE.md | Split `/checkin` and `/weekly-plan` into separate skills |
| 2 | Session labels updated to T/S/H + intensity levels | Self-documenting labels over abstract ones |
| 3 | Strava SSL certificate fix | `certifi` SSL context applied consistently |
| 4 | Simplified weekly planning questions (5 → 4) | "Which days?" replaces two separate questions |
| 5 | Check-in context line + numbered no-plan fallback | Show program/week/date before asking anything |
| 6 | Prompt deduplication (−38% across all skills) | Skills reference CLAUDE.md instead of repeating it |
| 7 | Extract schemas to shared reference file (−49% cumulative) | JSON schemas + output templates → `references/skill_schemas.md` |
| 8 | MCP response caching | Weather: 12h TTL; Strava: 6h TTL + config cache |
| 9 | NDJSON training log | O(1) append instead of O(n) read-and-rewrite |
| 10 | Direct MCP server launch | Removed `cmd /c` wrapper from `.mcp.json` |
| 11 | Excel parser optimization | `read_only=True` + `values_only=True` for openpyxl |
| 12 | Cache artifact cleanup + encoding audit | Removed tracked `.pyc` files; verified UTF-8 |

### Estimated Build Time (from scratch)

| Step | Approx. Time |
|------|-------------|
| Architecture + data model | 2–3 hours |
| MCP/tool integration | 1–2 hours |
| Prompt iteration + refinement | 3–4 hours |
| Benchmark design + execution | 3–4 hours |
| Tutorial + appendices | 3–5 hours |

### Key Prompts Given to Claude Code

**Initial build (Iteration 1)**
```
I'm an olympic weightlifter, I follow a 5-day program from my coach but I only
train 3 days a week. I need a checkin skill that tells me what to train today
based on how I feel, a weekly planner, and a way to log sessions after. I also
have weather and strava data via MCP. Build the skills and CLAUDE.md.
```

**Skill split (mid-Iteration 1)**
```
checkin is too slow, it asks too many questions and re-fetches everything every
time. split it -- do the heavy planning once a week and just confirm before
each session.
```

**T/S/H rename (Iteration 2)**
```
rename A/B/C to something meaningful. T for technique, S for strength, H for
heavy. also add intensity levels -- light, normal, and condensed for when I
train fewer days but still want to cover everything.
```

**Prompt deduplication (Iteration 6)**
```
the skill files are way too long. they all repeat the strava classification,
stop rules, session types etc. CLAUDE.md is always loaded. Could we reference it
instead of copy-pasting without losing quality?
```

**Schema extraction (Iteration 7)**
```
move the JSON schemas and output templates out of the skill files into a shared
reference file. skills should just say 'format per skill_schemas.md'.
```

**NDJSON switch (Iteration 9)**
```
the training log is a JSON array, which means every write has to read the whole
file first. switch to NDJSON so log-session can just append a line.
```

### Frustrations and Bottlenecks

- **Windows SSL certificates.** The Strava MCP server failed with `SSL: CERTIFICATE_VERIFY_FAILED` on Windows. Fix: use the `certifi` CA bundle. Root cause: the SSL context was passed to token refresh but not to the activity fetch call.
- **MCP server launch on Windows.** Claude Code initially could not launch Python MCP servers directly and required a `cmd /c` wrapper. Iteration 10 confirmed direct launch works.
- **Prompt bloat.** After the initial build, each skill file was 120–210 lines because it repeated content from `CLAUDE.md`. Two iterations of deduplication reduced total skill size by ~69% (517 → ~162 lines). Subsequent feature additions grew them back to 259 lines — still a 50% net reduction.
- **Training log format.** The initial JSON array format required reading the entire file on every write. Switching to NDJSON made writes O(1).

---

## 4. Prompt Iterations

### Iteration A: One Skill vs. Three

- **Before (v1):** A single `/checkin` skill asked 5+ questions, gathered all data, ran full session selection logic. Every session required a full planning cycle.
- **After (v2):** Split into `/weekly-plan` (once per week, ~4 questions) and `/checkin` (before each session, 3 questions, reads cached plan). `/log-session` added as a post-session recorder.
- **Result:** Check-in time dropped from 60+ seconds to ~10 seconds.

### Iteration B: Session Labels and Intensity Levels

- **Before:** Abstract labels tied to program days. One intensity level: as prescribed.
- **After:** T/S/H types + three intensities (light, normal, condensed).
- **Result:** Session labels instantly communicate intent. The condensed option means fewer training days no longer means missing critical exercises.

### Iteration C: Prompt Deduplication (Iterations 6–7)

- **Before:** Each skill file (~185 lines for `/checkin`) repeated Strava classification, stop rules, and session types inline.
- **After:** Skills reference `CLAUDE.md` sections by name.

| Skill | v1 | After dedup (v7) | Current (v12) | Net |
|-------|----|-----------------|---------------|-----|
| checkin | 185 lines | ~65 lines | 97 lines | −48% |
| weekly-plan | 212 lines | ~58 lines | 94 lines | −56% |
| log-session | 120 lines | ~39 lines | 68 lines | −43% |
| **Total** | **517 lines** | **~162 lines** | **259 lines** | **−50%** |

### Prompt Quality Critique

**Strengths:**
- Skills are concise step-by-step workflows (5 steps each), not monolithic paragraphs.
- Decision rules are threshold-based and unambiguous (soreness >= 6, energy <= 2).
- Output format is constrained (max 3 adjustments, exactly 2 stop rules, structured time-flex).
- Fallback paths are explicit: no plan → numbered options; Strava unavailable → skip silently.

**Weaknesses:**
- Verbosity on rest days: the system often produces a full weather summary when a 2-line response would suffice.
- Stop rules are hardcoded as exactly 2 with no mechanism for session-specific variants.
- The condensed session logic relies on the model to correctly merge exercises from different program days, which could break for unusual program structures.

---

## 5. Real Usage and Iteration

The system was tested with real training data across 2 weeks of the current program ("Leg Drive").

### Example 1: Normal Check-in (Scenario 1)

**Context:** Week 3, Tuesday. First session of the week. Plan calls for T (Technique).

**Athlete input:**
1. Sleep last night: good
2. Leg soreness (0-10): 4
3. Energy (1-5): 4

**What worked:** Session confirmed in ~10 seconds. The system identified a Strava bike ride session (>48h ago, no interference), suggested a condensed workout incorporating an exercise from an unscheduled day. Stop rules always present. Time-flex gives options without overloading.

**What changed:** Nothing — the happy path worked as designed.

### Example 2: Rest Day Override + 4th Session (Scenario 3.2)

**Context:** Week 2, Wednesday. Not a planned lifting day — plan says Bike Z2.

| Phase | Input | Response |
|-------|-------|----------|
| Phase 1 | Sleep: good / Soreness: 4 / Energy: 4 | Rest/cardio day — Bike Z2 suggested. Up next: Thu S. |
| Phase 2 | "I will train this morning instead" | S session pulled forward from Thursday with spacing rationale. |
| Phase 3 | "I will do 4 sessions this week" | Updated layout: Tue T → Wed S → Thu T2 → Fri H |

**What worked:** The system adapted to an unplanned change, pulled the next logical session, gave a spacing rationale, and correctly sourced exercises for the added T2 session.

**What changed after this run:** Added Step 5 to `/checkin` — 'Update plan if changed.' The original skill confirmed sessions but did not write changes back to the plan file.

### Iteration Triggered by Real Usage

Scenario 6 revealed that `/checkin` did not ask about adjusting weekly volume when a session was skipped.

**Before:**
```
If skipped: mark it "skipped" in the plan, carry over 1-2 key exercises (cut accessories).
```

**After:**
```
If skipped: mark it "skipped" in the plan, carry over 1-2 key exercises (cut accessories),
and ask: "Want to keep [N] sessions this week or adjust to [N-1]?"
```

---

## 6. Benchmark Methodology and Findings

### Design

The benchmark evaluates `/checkin` (the most complex skill) across 8 scored scenarios covering the full decision space.

| # | Scenario Type | Tests |
|---|--------------|-------|
| 1 | Normal check-in + log session — Happy path | 17 |
| 2 | Already trained today — Edge case | 8 |
| 3.1 | Rest / cardio day — Edge case | 11 |
| 3.2 | Rest day override + 4th session — Edge case | 32 |
| 4 | Ambiguous / vague input — Ambiguous | 16 |
| 5 | Baseline comparison — Baseline | 11 |
| 6 | Skipped session detection — Edge case | 14 |
| 7 | Trained yesterday + plan/log mismatch — Edge case | 4 |

### Scoring Rubric

| Score | Meaning |
|-------|---------|
| 0 | Fail — wrong output, missing section, or incorrect behavior |
| 1 | Partial — correct intent but missing detail, wrong format, or incomplete |
| 2 | Pass — fully correct output matching expected behavior |

### Aggregate Results

| # | Scenario | Tests | Score |
|---|----------|-------|-------|
| 1 | Normal check-in + log session | 17 | 34/34 |
| 2 | Already trained today | 8 | 16/16 |
| 3.1 | Rest / cardio day | 11 | 22/22 |
| 3.2 | Rest day override + 4th session | 32 | 64/64 |
| 4 | Ambiguous / vague input | 16 | 32/32 |
| 5 | Baseline comparison | 11 | 22/22 vs 5.5/22 |
| 6 | Skipped session detection | 14 | 28/28 |
| 7 | Trained yesterday + plan/log mismatch | 4 | 8/8 |
| **Total** | | **113** | **226/226** |

### Concrete Example 1: Ambiguous Input (Scenario 4)

**Setup:** Week 2, Wednesday. Planned S session. Yesterday was a full T session (RPE 7 with Snatch Deadlifts).

**Athlete input (deliberately vague):**
- Sleep: "eh, woke up a couple times but got back to sleep"
- Soreness: "like a 5? maybe 6? hard to tell, quads are tight from yesterday"
- Energy: "I dunno, 3ish I guess"

**Key findings:**
- The system interpreted vague inputs without re-asking for exact numbers.
- At the soreness threshold, it chose a graduated response: adjust rather than binary confirm/downgrade.
- It connected "quads tight" to yesterday's specific exercises — contextual reasoning across sessions.
- It offered a final choice — emergent behavior not explicitly prescribed in the skill.

### Concrete Example 2: Baseline Comparison (Scenario 5)

Same input for both: Week 2 Tuesday, sleep ok, soreness 2, energy 3. Raw Claude received only a plain text prompt with no data access or skills.

| Dimension | Raw Claude | /checkin |
|-----------|-----------|---------|
| Correct exercises from program | 2 | 2 |
| Sets/reps/notes | 1 | 2 |
| Session type (T/S/H) awareness | 0 | 2 |
| Readiness assessment with rules | 1.5 | 2 |
| Stop rules | 1 | 2 |
| Strava interference check | 0 | 2 |
| Weather-gated cardio | 0 | 2 |
| Carry-overs from missed sessions | 0 | 2 |
| Time-flex suggestions | 0 | 2 |
| Next session preview | 0 | 2 |
| Plan status update | 0 | 2 |
| **Total** | **5.5/22 (25%)** | **22/22 (100%)** |

The key insight: the system's value is not in being "smarter" than raw Claude — it's in having the right information at the right time and applying consistent rules.

### Failure Analysis

**Hard failure (1):** Scenario 6, test #14. The AI detected a skipped session and carried over exercises but did not ask about adjusting weekly volume. Fixed and all 14 tests now pass.

**Soft issues observed:**
- Verbosity on rest days — full weather table when 2 lines would suffice.
- Borderline soreness — system does not state which exact number it used.
- Carry-over accumulation — if the same exercise is missed for multiple weeks, the list grows without aging out.
- No Strava fallback messaging — when Strava is unavailable, it silently skips with no transparency.

**Untested failure modes:**
- Strava token expiry mid-session.
- Program week overflow — what happens after week 8?
- Concurrent plan edits — if `/weekly-plan` and `/checkin` run simultaneously, last writer wins.

---

## 7. Reflection

### Why This Workflow

Training decision-making used to take 5–10 minutes each session, especially when adjusting a 5-day plan to a 3-day schedule or reviewing missed workouts. This system cuts that to a 20-second check-in. It tracks training logs and accounts for extra activities like long bike rides.

### What Worked Well

- **CLAUDE.md as single source of truth.** Domain rules live in one file. When I changed the soreness threshold, one edit propagated to all three skills.
- **Two-phase workflow (plan + check-in).** Planning once per week and confirming daily matches how athletes actually think.
- **MCP tools for real-time data.** Weather and Strava provide signals that static prompts cannot access.
- **Prompt deduplication.** Reducing skills by 50% net while preserving behavior was the highest-leverage improvement.

### What Did Not Work Well

- **Verbosity.** The system sometimes produces 300+ word outputs for simple confirmations.
- **No auto-scheduling.** Claude Code skills cannot run autonomously on a schedule. The system only works when the athlete manually invokes `/checkin`.
- **Carry-over debt.** If the same exercise is skipped across multiple weeks, the carry-over list accumulates without aging out.

### What the Benchmark Revealed

The baseline comparison was the most telling result. Raw Claude scored 25% — better than expected on exercises but zero on 8 of 11 dimensions. The agentic layers are where the value lives. The one hard failure demonstrated that benchmarking works as intended: it found a real gap, triggered a real fix, and the fix was verified by re-running the test.

### Would I Keep Using This System?

Yes. I have used it for 2 weeks of real training. The check-in is genuinely fast (10 seconds), exercise carry-over prevents things from falling through cracks, and the Strava integration catches interference I might overlook. Caveats: carry-over accumulation needs addressing before weeks 4–5, rest day verbosity needs prompt tuning, and cross-LLM portability still needs dedicated testing.

---

## 8. Replication Guide

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI or VS Code extension)
- Python 3.12+
- A Strava account (optional)

> **Important:** Claude Code is required for the full system. Without it, MCP servers won't launch and skills won't have access to local data files. The skill prompts still work standalone but without Strava, weather, or persistent data.

### Estimated Replication Time

| Step | Approx. Time |
|------|-------------|
| Clone repo + set up venv + install dependencies | 10–20 min |
| Parse your own program Excel | 2–5 min |
| Configure Strava (optional) | 5–10 min |
| Customize CLAUDE.md for your athlete profile | 10–15 min |
| Test skills + verify MCP tools are running | 10–20 min |
| **Total** | **~1 hour** |

### Step 1: Get the Files

```bash
git clone https://github.com/SandrineLpx/TrainSmart.git
cd TrainSmart
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install fastmcp openpyxl
pip install certifi            # Windows SSL hardening for Strava (optional)
```

### Step 2: Parse Your Program

```bash
python scripts/parse_excel.py "references/Leg Drive.xlsx" 2026-02-02
# Generates data/program.json and data/program_summary.md
```

### Step 3: Configure Strava (Optional)

```bash
# Windows
copy data\strava_config.template.json data\strava_config.json
# Edit strava_config.json with your Client ID and Secret
# (from https://www.strava.com/settings/api)
python scripts/strava_auth.py
```

### Step 4: Open in Claude Code

Open the project folder in Claude Code (or VS Code with the Claude Code extension). The `.mcp.json` file auto-registers both MCP servers.

### Step 5: Run the Skills

```
/weekly-plan    # Plan your training week (run Sunday/Monday)
/checkin        # Pre-session check-in
/log-session    # Log what you did after training
```

### Key Files to Customize

| File | What to Change |
|------|---------------|
| `CLAUDE.md` | Athlete profile, session types, decision thresholds, stop rules |
| `data/preferences.json` | Location coordinates, weather thresholds |
| `data/prs.json` | Your personal records |
| `.claude/skills/*/SKILL.md` | Skill workflows |

---

## Appendix A: Skill File Contents

### `/checkin` — `.claude/skills/checkin/SKILL.md`

```markdown
---
name: checkin
description: Quick pre-workout check-in. Reads your weekly plan, checks how you feel,
  and confirms or adjusts today's session. Use right before training -- takes 10 seconds.
---

# Pre-Workout Check-in

Fast confirmation before training. Reads the weekly plan, asks how you feel, confirms or adjusts.

## Inputs
- Athlete readiness inputs: sleep, leg soreness, energy
- Optional extra context volunteered by athlete
- Current weekly plan (data/current_week_plan.json)
- Supporting context: training log, PRs, Strava (if available), weather (if cardio is suggested)

## Outputs
- Today's recommended session type/intensity (confirm or adjust)
- Exercise-level adjustments with stop rules and time-flex options
- Plan update in data/current_week_plan.json when schedule/session changes

## Workflow

### Step 0: Show context
Read data/current_week_plan.json (contains program_name, total_weeks, week_number). Display one line:
**Program:** [program_name] | **Week [week_number] of [total_weeks]** | **[Today's day], [date]**
Do NOT read program.json here -- the plan already has everything needed.

### Step 1: Ask (3 questions only)
Pre-workout check:
1. Sleep last night: good / ok / bad
2. Leg soreness (0-10):
3. Energy (1-5):
If the athlete volunteers extra info, use it. Don't ask for more.

### Step 2: Gather data (in parallel)
1. Weekly plan: already loaded in Step 0. Find today's session.
2. Training log: Read data/training_log.ndjson. Check completed vs. missed sessions this week + recent cardio (48h).
3. PRs: Read data/prs.json. Used in Step 4 to show target weights per CLAUDE.md "Weight Guidance".
4. Strava (days_back=2): Classify per CLAUDE.md "Strava Activity Types". If unavailable, skip silently.
5. Weather (days=1): Only if today has a cardio suggestion in the plan.

### Step 3: Decide
Apply CLAUDE.md "Session Selection Decision Rules". If readiness is BAD (soreness >= 6 OR bad sleep + energy <= 2): S->mini-S/T, H->mini-T/recovery. T is always OK.
Missed sessions: Flag, ask if skipped or unlogged. If skipped: mark "skipped", carry over 1-2 key exercises, and ask: "Want to keep [N] sessions this week or adjust to [N-1]?"
Hard cardio in last 24-36h: apply protection rule or switch to T/mini.
Not a planned day: offer (1) pull forward next session, (2) just log training, or (3) add a T2 session.

### Step 3b: Time-flex suggestions
Short on time? Drop: accessories -> carry-overs -> lower-priority strength.
Never drop main lift(s). Keep each list to 2-3 items.

### Step 4: Output
Format per templates in references/skill_schemas.md. Always include 2 stop rules from CLAUDE.md + time-flex lines. Show target weights per CLAUDE.md "Weight Guidance" for exercises with a matching PR.

### Step 5: Update plan if changed
If today was not in the schedule or the session differs from the plan: update data/current_week_plan.json. Mark moved sessions as "moved".

## Failure Modes and Fallbacks
- Missing weekly plan: offer /weekly-plan or quick fallback
- Strava unavailable: continue using training log only
- Weather unavailable: skip weather-based gating
- Tool errors on optional data: continue without blocking

## Constraints
- Max 3 questions
- Never recommend S or H when soreness >= 6
- Always include 2 stop rules (CLAUDE.md)
- Use the weekly plan -- don't recalculate from scratch
- If tools fail, continue without them
```

### `/weekly-plan` — `.claude/skills/weekly-plan/SKILL.md`

```markdown
---
name: weekly-plan
description: Plan your training week. Sets how many days you'll train, picks the
  best days based on weather and schedule, and saves a tentative plan.
  Use at the start of each week (Sunday/Monday).
---

# Weekly Planner

Review last week, ask schedule preferences, build day-by-day schedule (WL + cardio), save to data/current_week_plan.json.

## Inputs
- Athlete inputs: available training days, outdoor cardio preference, fatigue/pain
- Competition date from data/preferences.json
- Program/training context: program.json, training_log.ndjson, prs.json
- External context: weather forecast and Strava recent activities

## Outputs
- Weekly schedule response (day-by-day WL/cardio plan + rationale)
- Saved/updated data/current_week_plan.json

## Workflow

### Step 0: Check for competition date
Read data/preferences.json. If competition_date exists, confirm it.

### Step 1: Ask the athlete (all at once)
1. Which days are you training this week?
2. Want to plan outdoor cardio?
3. How are you feeling? Fatigue: low/medium/high, any pain?

### Step 2: Gather data (in parallel)
1. Last week's log: summarize sessions, exercises, cardio, RPE, soreness.
2. Program: read program.json, calculate week number per CLAUDE.md formula.
3. PRs: read prs.json for target weight computation.
4. Weather (days=7): identify outdoor-suitable days per CLAUDE.md.
5. Strava (days_back=7): classify per CLAUDE.md.

### Step 3: Build the schedule
Assign T/S/H/Hybrid per CLAUDE.md. Priority: T > S > H.
If no heavy work in 7+ days, prioritize H over S.
Use condensed to pull exercises from skipped days. Use mini when fatigued.
Place cardio on weather-suitable non-WL days. Never hard run/ski before H or S.
Apply competition taper if within 10 days.

### Step 4: Save the plan
Overwrite data/current_week_plan.json. Include program_name and total_weeks.

### Step 5: Output
Format per template in references/skill_schemas.md.

## Constraints
- Never schedule more WL days than requested
- Always save to current_week_plan.json with program_name + total_weeks
- Maximum 1 protection rule
```

### `/log-session` — `.claude/skills/log-session/SKILL.md`

```markdown
---
name: log-session
description: Log a completed training session. Records what you did, compares to
  the program prescription, and updates your training log. Use after training.
---

# Session Logger

Record a completed session to data/training_log.ndjson. Compare against prescription. Check for new PRs.

## Inputs
- Log date (today or YYYY-MM-DD)
- Session type/intensity and exercises performed (or "as prescribed")
- Readiness fields: RPE, sleep, soreness, optional notes
- Reference files: data/program.json, data/prs.json

## Outputs
- One appended NDJSON log entry in data/training_log.ndjson
- Updated PR values in data/prs.json when a new PR is detected
- Logging confirmation (including PR callouts if applicable)

## Workflow

### Step 0: Detect date
Show Today: YYYY-MM-DD. Default log_date = today.

### Step 1: Ask the athlete (all at once)
1. Log date (today or YYYY-MM-DD)
2. Session type: T / S / H / T2 / mini / cardio / recovery
3. Exercises performed (or "as prescribed")
4. RPE (1-10)
5. Sleep: good/ok/bad
6. Leg soreness (0-10)
7. Notes (optional)

### Step 2: Load program + compare
Read program.json. Calculate week number from log_date. Match performed exercises against prescription.

### Step 3: Build + save
Build single-line JSON per schema in references/skill_schemas.md.
Append via Bash: `echo '<json>' >> data/training_log.ndjson`
Append only -- never read+rewrite the file.

### Step 4: Check PRs
Compare logged weights against prs.json. Update if exceeded.

### Step 5: Output
Format per template in references/skill_schemas.md.

## Constraints
- Append only -- never read+rewrite the log file
- Each entry must be valid JSON on a single line (NDJSON)
```

---

## Appendix B: CLAUDE.md (Full Contents)

```markdown
# Train Smart -- Olympic Weightlifting Optimization System

## Athlete Profile
- Olympic weightlifter, trains ~3 days/week (days vary)
- Uses a flexible T/S/H session system (Technique/Strength/Heavy)
- Supplements with outdoor cardio: bike, run, ski.
- Tracks all activities on Strava (cardio, gym WL sessions, yoga)

## Current Program
- File: data/program.json (parsed from Leg Drive.xlsx)
- Program start date and week calculation formula in data/preferences.json
- To find current week: week = ((today - program_start_date).days // 7) + 1, clamped 1-8

## T/S/H Session System
Session types:
- T (Technique): Snatch pulls, snatch technique, pulls
- S (Strength): Squats, jerks, leg drive
- H (Heavy): Heavy singles, competition lifts
- T2 (Hybrid): Jerk technique + snatch balance or clean + jerk work.

Intensities:
- Light (mini): Only 1-2 main lifts, reduced sets
- Normal: As prescribed in program.json
- Condensed: As prescribed + key exercises pulled from skipped program days

## Non-Negotiable Rules
1. Priority order: Olympic lifts > leg/trunk strength > endurance
2. Cut accessories FIRST, then lower-body volume, ONLY LAST reduce main lift intensity
3. No unnecessary grinding: if technique degrades or fatigue is high, switch to mini

## Stop Rules (apply to ALL sessions)
- If you lose positions or miss 2 attempts in a row -> drop ~5% and finish clean
- If form still degrades after dropping -> switch to mini or stop after priorities

## Session Selection Decision Rules
- If leg soreness >= 6 OR sleep bad + energy <= 2 -> T (or mini-T) or active recovery
- If hard run or hard ski < 24-36h -> avoid heavy S and H -> do T or mini
- If no heavy work in 5-7 days and status OK -> prioritize H
- Otherwise use recommended order: T -> S -> H

## Strava Activity Types
- MTB, Run, Ski, BackcountrySki -> hard cardio, interference (avoid S/H next day)
- Ride -> easy cardio (low interference unless >90 min)
- WeightTraining -> gym WL session. Cross-ref with log
- Yoga -> recovery/mobility, positive readiness signal
- Walk, Hike -> ignore (no impact)

## Weight Guidance
| Reps | % of PR | Use case |
|------|---------|----------|
| 1 (singles) | 85-95% | H-day competition lifts |
| 1+1, 1+2 | 75-85% | Technique complexes |
| 3 | 75-85% | Front squat triples, rack drives |
| 5 | 70-80% | Front squat 5x5, strength work |
| 6+ | 60-70% | RDLs, goblet squats, accessories |

Output format: `Front Squat 5x5 @56-60kg (75-80% of 75kg PR)`
Rules: Round to 0.5kg. Show as range. Omit if no PR.
```

---

## Appendix C: `.mcp.json`

```json
{
  "mcpServers": {
    "weather": {
      "type": "stdio",
      "command": ".venv\\Scripts\\python.exe",
      "args": ["mcp_servers\\weather_mcp.py"]
    },
    "strava": {
      "type": "stdio",
      "command": ".venv\\Scripts\\python.exe",
      "args": ["mcp_servers\\strava_mcp.py"]
    }
  }
}
```

> For macOS/Linux, replace `.venv\\Scripts\\python.exe` with `.venv/bin/python` and use forward slashes in args paths.
