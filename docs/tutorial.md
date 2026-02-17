# Train Smart: An Agentic AI System for Olympic Weightlifting Training Optimization

**MSIS 549B — AI and GenAI for Business Applications**
University of Washington, Foster School of Business

**GitHub:** [Github Link to TrainSmart Repo](https://github.com/SandrineLpx/TrainSmart/tree/main)
**Demo Video:** [OneDrive Link](https://1drv.ms/v/c/e60b04fc350039b3/IQBZNlMg4L10QaU5-3A9qM1hASBl6b01-DtnKTZfpvnmB-U?e=5mKFIz)

### Submission Placeholders (Fill Before Final Export)


- [ ] Verify benchmark totals and appendix links are final
- [ ] Export this tutorial to PDF and confirm formatting

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [System Design](#2-system-design)
3. [Building Process](#3-building-process)
4. [Prompt Iterations](#4-prompt-iterations)
5. [Real Usage and Iteration](#5-real-usage-and-iteration)
6. [Benchmark Methodology and Findings](#6-benchmark-methodology-and-findings)
7. [Reflection](#7-reflection)
8. [Replication Guide](#8-replication-guide)

---

## 1. Problem Statement

### The Pain Point

I'm an Olympic weightlifter on a coach-prescribed 5-day program ("Leg Drive" - an 8-week periodized cycle), but in practice I usually don't complete all 5 days. Between school and frequent outdoor activities, I'm mostly following a 3-days-per-week training schedule right now. That mismatch creates a daily decision problem:

- **Which session do I run today?** The program prescribes Mon-Fri, but I usually train Tue/Thu/Fri (or whatever days fit that week).
- **What intensity?** If I'm sore from yesterday's ski or last night's sleep was bad, should I go lighter?
- **What exercises carry over?** If I skip Thursday's squat day, does the Front Squat just disappear, or should it move to Friday?
- **When is outdoor cardio safe?** A hard run before heavy day wrecks performance, but a bike ride (road) is fine. MTB might be different. 

Today, I handle this with a spreadsheet and gut feel. It takes 5-10 minutes of mental math before each session, and I often second-guess myself mid-warm-up. Worse, I lose track of skipped exercises — they just fall through the cracks.

### Why an Agentic Workflow

A single LLM prompt can't solve this because the decision requires:

1. **Structured data access** — reading the current week's program, the training log, and the weekly plan
2. **Real-time external data** — today's weather (for cardio suggestions) and Strava activities (to detect hard cardio interference)
3. **Persistent state** — the weekly plan must survive between sessions, and the training log must accumulate over weeks
4. **Domain-specific rules** — stop rules, session selection thresholds, and priority ordering that the athlete has refined over years

An agentic system with multiple skills and MCP tools can orchestrate all of these in a 10-second pre-workout check-in.

### Tech Stack

- **Claude Code** (CLI / VS Code extension) with Claude Opus model
- **3 Claude Code Skills** (markdown skill files in `.claude/skills/`)
- **2 MCP Servers** (Python, using FastMCP): weather forecast + Strava activities
- **CLAUDE.md** as the single source of truth for domain rules
- **Python 3.12+** for MCP servers and utility scripts
- **Data files:** JSON + NDJSON for program, plan, log, preferences, and personal records

---

## 2. System Design

### Architecture Overview

The system has three layers:

```
┌──────────────────────────────────────────────────┐
│                   CLAUDE.md                       │
│  Domain rules, decision logic, stop rules,       │
│  session types, Strava classification, PRs        │
└──────────────────────┬───────────────────────────┘
                       │ always loaded as context
┌──────────────────────▼───────────────────────────┐
│              3 Skills (SKILL.md)                  │
│  /weekly-plan  →  /checkin  →  /log-session       │
│    (plan week)    (confirm)    (record session)   │
└────┬───────────────┬──────────────────┬──────────┘
     │               │                  │
┌────▼────┐   ┌──────▼──────┐   ┌──────▼──────┐
│ Weather │   │   Strava    │   │  Data Files │
│  MCP    │   │    MCP      │   │  (JSON/NDJSON)│
│(Open-Meteo)│   │ (API v3)    │   │  program,plan│
│ No API key│   │  OAuth2     │   │  log,PRs     │
└─────────┘   └─────────────┘   └─────────────┘
```

> **Figure 1:** Architecture diagram showing the three-layer system. <!-- TODO: Replace ASCII diagram with a proper figure (e.g., draw.io or Mermaid export) if submitting as PDF -->

### CLAUDE.md — The Domain Brain

`CLAUDE.md` (~120 lines) contains all domain knowledge that skills reference but don't duplicate:

- **Athlete profile:** 3 days/week, Kirkland WA, Strava-tracked
- **T/S/H session system:** Technique / Strength / Heavy, each with light/normal/condensed intensities
- **Session selection rules:** threshold-based (soreness >= 6 → no S/H, bad sleep + energy <= 2 → T only, etc.)
- **Stop rules:** 2 universal rules that appear in every session output
- **Priority order:** Olympic lifts > strength > endurance > accessories
- **Strava classification:** Run/Ski = interference, Ride = low impact, Yoga = recovery
- **Weather thresholds:** rain < 40%, temp > 4C, wind < 25 mph

Skills say `"Apply per CLAUDE.md 'Session Selection Decision Rules'"` instead of repeating the rules. This means updating a threshold in one place changes behavior across all three skills.

### The Three Skills

| Skill | When | Input | Output | Files Read | Files Written |
|-------|------|-------|--------|-----------|--------------|
| `/weekly-plan` | Start of week | Training days, fatigue, cardio preference | Day-by-day schedule with exercises, cardio, weather + advisory log-completeness prompt | program.json, training_log.ndjson, Weather MCP, Strava MCP | current_week_plan.json |
| `/checkin` | Before each session | Sleep, soreness (0-10), energy (1-5) | Session confirmation/adjustment with stop rules | current_week_plan.json, training_log.ndjson, Strava MCP, Weather MCP | current_week_plan.json (if changed) |
| `/log-session` | After each session | Session type, exercises, RPE | Log confirmation, skipped exercises, PRs | program.json, prs.json | training_log.ndjson (append), prs.json (if PR) |

### Skill Workflow

The three skills form a pipeline that runs weekly:

```
Sunday/Monday:  /weekly-plan  ──►  Saves plan to current_week_plan.json
                                        │
Before each     /checkin      ◄─────────┘  Reads plan, asks 3 questions,
session:                                    confirms or adjusts session
                                        │
After each      /log-session  ◄─────────┘  Records what happened,
session:                                    compares to prescription
```

### T/S/H Session System

The program prescribes 5 days (Mon-Fri), but the athlete trains 3. Sessions are abstracted into types that can be moved to any day:

| Type | Focus | Maps to Program Day | Priority |
|------|-------|-------------------|----------|
| **T** (Technique) | Snatch pulls, snatch work | Tuesday | 1st (always safe) |
| **S** (Strength) | Squats, jerks, leg drive | Monday + Thursday | 2nd |
| **H** (Heavy) | Competition lifts, heavy singles | Friday | 3rd |
| **T2** (Hybrid) | Clean/jerk technique + uncovered priority work | Added as 4th session when freshness/readiness and weekly logs support it | 4th |

Day-count mapping used by `/weekly-plan`:
- **0 days:** Rest/recovery week (no WL sessions)
- **1 day:** T
- **2 days:** T + S
- **3 days:** T + S + H
- **4 days:** T + S + H + T2 (if readiness/logs support it)
- **5 days:** Full program week

Override rule: if no heavy work in 7+ days, prioritize H over S when selecting limited sessions.

Each type can run at three intensities:
- **Light (mini):** 1-2 main lifts only, reduced sets — for fatigue or deload
- **Normal:** As prescribed
- **Condensed:** As prescribed + key exercises from skipped days — for fewer training days with full coverage

### MCP Servers

| Server | API | Auth | Purpose |
|--------|-----|------|---------|
| `weather_mcp.py` | Open-Meteo | None (free) | 7-day forecast. Gates outdoor cardio suggestions based on rain/temp/wind thresholds. 12-hour cache. |
| `strava_mcp.py` | Strava API v3 | OAuth2 | Recent activities. Detects interference from hard cardio (run/ski within 24-36h). Flags unlogged gym sessions. 6-hour cache with automatic token refresh. |

Both servers use only Python standard library + `fastmcp`. No heavy dependencies. They launch via `.mcp.json` and are available to all skills automatically.

### Shared Reference File

All three skills reference `references/skill_schemas.md` for JSON schemas, output templates, and examples. This file was extracted in Iteration 7 to avoid duplicating schema definitions across skills. It contains:

- **`current_week_plan.json` schema** — the exact JSON structure written by `/weekly-plan` and read by `/checkin`
- **`training_log.ndjson` entry schemas** — WL session and cardio log entry formats
- **Condensed session example** — shows how exercises from skipped days merge into a condensed session
- **Output templates** — for `/checkin` (confirming, adjusting, no-plan fallback), `/weekly-plan`, and `/log-session`

Skills reference it with lines like `"Format per templates in references/skill_schemas.md"` rather than embedding templates inline.

### Data Files

| File | Format | Purpose |
|------|--------|---------|
| `data/program.json` | JSON | 8-week periodized program (parsed from coach's Excel) |
| `data/current_week_plan.json` | JSON | Active weekly schedule (written by /weekly-plan, read by /checkin) |
| `data/training_log.ndjson` | NDJSON | Append-only session log (one JSON object per line) |
| `data/prs.json` | JSON | Personal records for 11 tracked lifts |
| `data/preferences.json` | JSON | Location coordinates, weather thresholds |
| `data/strava_config.json` | JSON | OAuth tokens (gitignored) |

---

## 3. Building Process

### Tools and LLMs Used

The entire system was built using **Claude Code** (VS Code extension) with the **Claude Opus** model. Claude Code was used for:

- Generating skill files from natural language descriptions
- Writing both MCP servers (weather + Strava)
- Writing the Excel parser script
- Iterating on prompts based on test results
- Running benchmark scenarios

**Python** was used for MCP servers (`fastmcp` library) and utility scripts (`openpyxl` for Excel parsing). No other frameworks or libraries.

### Build Timeline

The system was built across 12 iterations over 2 days:

| Iteration | What Changed | Key Decision |
|-----------|-------------|--------------|
| 1 | Initial build: 3 skills, 2 MCP servers, data layer, CLAUDE.md | Split /checkin and /weekly-plan into separate skills (was one monolithic skill) |
| 2 | Session label update to T/S/H + intensity levels (light/normal/condensed) | Self-documenting labels > abstract labels |
| 3 | Strava SSL certificate fix | `certifi` SSL context was applied to token refresh but not activity fetch |
| 4 | Simplified weekly planning questions (5 → 4) | "Which days?" replaces "how many?" + "which days off?" |
| 5 | Checkin context line + numbered no-plan fallback | Show program/week/date before asking anything |
| 6 | Prompt deduplication (-38% across all skills) | Skills reference CLAUDE.md sections instead of repeating them |
| 7 | Extract schemas to reference file (-49% cumulative) | JSON schemas + output templates → `references/skill_schemas.md` |
| 8 | MCP response caching | Weather: 12h TTL. Strava: 6h TTL + config cache |
| 9 | NDJSON training log | O(1) append instead of O(n) read+rewrite |
| 10 | Direct MCP server launch | Remove `cmd /c` wrapper from `.mcp.json` |
| 11 | Excel parser optimization | `read_only=True` + `values_only=True` for openpyxl |
| 12 | Cache artifact cleanup + encoding audit | Removed tracked .pyc, verified clean UTF-8 |

### Time Spent by Step

Approximate time by major step (for replication planning):

| Step | Approx. Time | Notes |
|------|--------------|-------|
| Initial architecture + data model | 2-3 hours | Defined 3-skill split and file/state model |
| MCP/tool integration | 2-4 hours | Weather + Strava setup, auth, Windows launch issues |
| Prompt iteration + refinement | 4-6 hours | 12 iterations across behavior and UX |
| Benchmark design + execution | 3-4 hours | Scenario writing, scoring, reruns after fixes |
| Tutorial + appendices | 3-5 hours | Write-up, benchmark tables, replication guide |


### Example Prompts Given to Claude Code

This project involved hundreds of prompts across multiple Claude Code sessions — most were not tracked, since the build was iterative and conversational (fixing a bug, tweaking a threshold, asking "why did it do that?"). The prompts below are reconstructed from iteration logs and git history for the most impactful changes. They are not exact quotes, but realistic in tone and intent.

**Initial build (Iteration 1):**
> "I'm an olympic weightlifter, I follow a 5-day program from my coach but I only train 3 days a week. I need a checkin skill that tells me what to train today based on how I feel, a weekly planner, and a way to log sessions after. I also have weather and strava data via MCP. Build the skills and CLAUDE.md."

**Mid-iteration 1 — skill split:**
> "checkin is too slow, it asks too many questions and re-fetches everything every time. split it — do the heavy planning once a week and just confirm before each session."

**T/S/H rename (Iteration 2):**
> "rename A/B/C to something meaningful. T for technique, S for strength, H for heavy. also add intensity levels — light, normal, and condensed for when I train fewer days but still want to cover everything."

**SSL fix (Iteration 3):**
> "strava MCP is failing with SSL CERTIFICATE_VERIFY_FAILED. weather works fine. fix it."

**Dedup (Iteration 6):**
> "the skill files are way too long. they all repeat the strava classification, stop rules, session types etc. CLAUDE.md is always loaded anyway — just reference it instead of copy-pasting."

**Schema extraction (Iteration 7):**
> "move the JSON schemas and output templates out of the skill files into a shared reference file. skills should just say 'format per skill_schemas.md'."

**NDJSON switch (Iteration 9):**
> "the training log is a JSON array, which means every write has to read the whole file first. switch to NDJSON so log-session can just append a line."

**Log-session BOM fix (Iteration 13):**
> "log-session isn't showing up as a skill. checkin and weekly-plan work. what's wrong?"

### Frustrations and Bottlenecks

1. **Windows SSL certificates:** The Strava MCP server failed with `SSL: CERTIFICATE_VERIFY_FAILED` on Windows because Python's venv doesn't access the Windows certificate store. Fix: use `certifi` CA bundle. The bug was that `SSL_CONTEXT` was passed to token refresh but not to activity fetch — a one-line inconsistency that took time to diagnose.

2. **MCP server launch on Windows:** Claude Code initially couldn't launch Python MCP servers directly. We had to wrap them in `cmd /c`, which added latency and complexity. Later (Iteration 10) we found that direct launch works and removed the wrapper.

3. **Prompt bloat:** After the initial build, each skill file was 120-210 lines because it repeated domain rules from CLAUDE.md (session types, Strava classification, stop rules, etc.). Two iterations of deduplication reduced total prompt size by ~69% (517 → ~162 lines). Subsequent feature additions grew them back to 259 lines — still a 50% net reduction.

4. **Training log format:** The initial JSON array format (`{"entries":[...]}`) required reading the entire file on every write. With 3 sessions/week, this becomes O(n) per append. Switching to NDJSON (one JSON object per line) made writes O(1) — a simple `echo >> file` append.

---

## 4. Prompt Iterations

The assignment requires documenting at least one prompt iteration. Here are the three most impactful ones, each showing before/after and the reasoning.

### Iteration A: Skill Architecture — One Skill vs. Three

**Before (v1):**
A single `/checkin` skill that did everything: asked 5+ questions, gathered all data, ran full session selection logic, and produced a recommendation. Every session felt like a planning session.

**After (v2):**
Split into `/weekly-plan` (once per week, ~4 questions, heavy data gathering) and `/checkin` (before each session, 3 questions, reads cached plan). Added `/log-session` as a third skill for post-session recording.

**Why:** The athlete wants convenience. Planning happens once; daily confirmation should be near-instant. This maps to real behavior — you decide your week on Sunday, then just show up and train. The split also reduced redundant API calls (weather and Strava fetched once per week instead of every session).

**Result:** Check-in time dropped from 60+ seconds to ~10 seconds. The weekly plan persists in `current_week_plan.json`, so `/checkin` doesn't need to recalculate.

### Iteration B: Session Label Update to T/S/H + Intensity Levels

**Before:**
```
Session types used abstract labels tied to program days.
One intensity level: as prescribed.
```

**After:**
```
Session types: T (Technique), S (Strength), H (Heavy).
Three intensities: light (mini), normal (as prescribed), condensed
(as prescribed + key exercises from skipped days).
```

**Why:** The previous labels were abstract and required memorization. T/S/H is self-documenting. Intensity levels give real flexibility: train 3 days with condensed coverage or 3 days with normal volume. This matches real-world decisions athletes make weekly.

**Result:** Session type labels instantly communicate intent. The condensed option means fewer training days doesn't mean missing critical exercises.

### Iteration C: Prompt Deduplication (Iterations 6-7)

**Before (each skill repeated domain rules):**
```markdown
# In checkin/SKILL.md — 185 lines
Classify Strava activities:
- Run, NordicSki → hard cardio (interference)
- Ride → easy cardio
- WeightTraining → gym session
- Yoga → recovery
- Walk, Hike → ignore

Stop rules:
1. If you lose positions or miss 2 attempts → drop 5%
2. If form still degrades → switch to mini
...
```

**After (skills reference CLAUDE.md):**
```markdown
# In checkin/SKILL.md
Classify per CLAUDE.md "Strava Activity Types".
...
Stop rules: [2 stop rules from CLAUDE.md]
```

**Why:** Since CLAUDE.md is always loaded as context alongside any skill, duplicating its content inflates prompt tokens without adding information. The initial dedup (Iterations 6-7) cut total skill lines from 517 to ~162. Subsequent iterations (8-12) added new features (caching logic, Strava skip rules, competition taper, PR weight guidance), growing the files to their current sizes:

| Skill | Before (v1) | After dedup (v7) | Current (v12) | Net reduction |
|-------|-------------|-------------------|----------------|---------------|
| checkin | 185 lines | ~65 lines | 97 lines | -48% |
| weekly-plan | 212 lines | ~58 lines | 94 lines | -56% |
| log-session | 120 lines | ~39 lines | 68 lines | -43% |
| **Total** | **517 lines** | **~162 lines** | **259 lines** | **-50%** |

**Result:** Even after feature growth, skills are still half their original size. The dedup created headroom — new features could be added without returning to bloated prompts. Single source of truth (one edit propagates everywhere), and skills remain pure workflow logic.

### Prompt Quality Critique

**Strengths:**
- Skills are concise step-by-step workflows (5 steps each), not monolithic paragraphs
- Decision rules are threshold-based and unambiguous (soreness >= 6, energy <= 2)
- Output format is constrained (max 3 adjustments, exactly 2 stop rules, structured time-flex)
- Fallback paths are explicit (no plan → numbered options, Strava unavailable → skip silently)

**Weaknesses:**
- The system can be verbose on rest days — a 2-line "rest day, bike if weather holds" would suffice but it often produces a full weather summary and protection rule paragraph
- Stop rules are hardcoded as exactly 2 — there's no mechanism for session-specific stop rules (e.g., a clean-specific rule vs. a squat-specific rule)
- The "condensed session" logic relies on the LLM to correctly merge exercises from different program days, which could break for unusual program structures

---

## 5. Real Usage and Iteration

The system was tested with real training data across 2 weeks of the Leg Drive program. Below are two real usage examples showing the full input/output cycle.

### Example 1: Normal Check-in (Scenario 1)

**Context:** Week 2, Tuesday. First session of the week. Plan calls for T (Technique).

**Athlete input:**
```
1. Sleep last night: ok
2. Leg soreness (0-10): 2
3. Energy (1-5): 3
```

**System output:**
> **Program:** Leg Drive | **Week 2 of 8** | **Tuesday, 2026-02-10**
>
> **Today: T (Technique) — confirmed**
>
> Snatch Pull + Snatch 6x(1+1) — no straps. High pull at light weight, speed pull at working weight.
> Snatch Deadlift 6x3
> Single Leg Squat 3x10 each
> Lu Raises 3x12
>
> **Why:** Readiness is good (sleep ok, soreness 2, energy 3). T session as planned — first session of the week, no interference.
>
> **Stop rules:**
> - If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean
> - If form still degrades after dropping → switch to mini or stop after priorities
>
> **Time-flex:**
> - Short on time? Drop: Lu Raises. Keep snatch complex + snatch DL.
> - Extra time? Add: Snatch balance 3x1, Ab Wheel 3x10

<!-- TODO: Add screenshot of actual /checkin output in Claude Code terminal (Figure 2) -->

**What worked:** Confirmed the session in 10 seconds. Exercises are exact (from program.json), stop rules are always present, time-flex gives options without overloading.

**What changed after this run:** Nothing — the happy path worked as designed.

### Example 2: Rest Day Override + 4th Session (Scenario 3.2)

**Context:** Week 2, Wednesday. Not a planned lifting day — plan says Bike Z2.

**Athlete input (3 phases):**
```
Phase 1: Sleep: good, Soreness: 4, Energy: 4
Phase 2: "I will train this morning instead"
Phase 3: "I will do 4 sessions this week"
```

**System output (3 phases):**

Phase 1 — Rest day response:
> **Program:** Leg Drive | **Week 2 of 8** | **Wednesday, 2026-02-11**
>
> Today is a rest/cardio day — Bike Z2 suggested (30-45 min). Weather looks good.
> **Up next:** Thursday S (Front Squat 5x5, Rack Drives, DB Row carry-over).

Phase 2 — Override accepted:
> **Today: S (Strength) — pulled forward from Thursday**
>
> Goblet Squat 3x10, Front Squat 5x5, Rack Drives 4x3, BTN Pullups 3x10, Lu Raises 3x12 + DB Row 3x15 carry-over.
>
> **Why:** Readiness is good. Pulling S to Wed gives better spacing — Wed S → Fri H instead of back-to-back Thu S → Fri H.

Phase 3 — 4th session added:
> Updated layout: **Tue T (done) → Wed S → Thu T2 → Fri H**
>
> Thursday now picks up Wed program day: Hang power clean + 2 jerks 6x(1+1+1), Jerk Recovery 6x(1+1), Cossack squats 3x10.

> See the [demo video](https://1drv.ms/v/c/e60b04fc350039b3/IQBZNlMg4L10QaU5-3A9qM1hASBl6b01-DtnKTZfpvnmB-U?e=5mKFIz) for a live walkthrough of this scenario (rest day override with 4th session addition), including the `/weekly-plan` happy path that precedes it.

**What worked:** The system adapted gracefully to an unplanned change. It pulled the next logical session (S from Thursday), provided a spacing rationale, and when the athlete wanted a 4th session, it sourced exercises from an uncovered program day and placed them correctly. The weekly plan was updated to reflect all changes.

**What changed after this run:** Added Step 5 to `/checkin` — "Update plan if changed." The original skill confirmed sessions but didn't write changes back to the plan file, so the next `/checkin` would still see the old 3-day plan.

### Iteration Triggered by Real Usage

The most impactful change from real usage was discovering that `/checkin` didn't ask about adjusting weekly volume when a session was skipped. In Scenario 6, the AI correctly detected a missed Wednesday session (via Strava + log cross-reference) and carried over Front Squat to Thursday, but it never asked: "Want to keep 4 sessions this week or adjust to 3?"

This was the only hard test failure across all 113 tests. The fix was a one-line addition to `/checkin` Step 3:

**Before:**
> If skipped: mark it `"skipped"` in the plan, carry over 1-2 key exercises (cut accessories).

**After:**
> If skipped: mark it `"skipped"` in the plan, carry over 1-2 key exercises (cut accessories), and ask: "Want to keep [N] sessions this week or adjust to [N-1]?"

---

## 6. Benchmark Methodology and Findings

### Design

The benchmark evaluates `/checkin` (the most complex skill) across 8 scored scenarios designed to cover the decision space.

| # | Scenario | Type | Tests |
|---|----------|------|-------|
| 1 | Normal checkin + log session | Happy path | 17 |
| 2 | Already trained today | Edge case | 8 |
| 3.1 | Rest / cardio day | Edge case | 11 |
| 3.2 | Rest day override + 4th session | Edge case | 32 |
| 4 | Ambiguous / vague input | Ambiguous | 16 |
| 5 | Baseline comparison | Baseline | 11 |
| 6 | Skipped session detection | Edge case | 14 |
| 7 | Trained yesterday + plan/log mismatch | Edge case | 4 |

### Scoring Rubric

Each test is scored on a 0/1/2 scale:

| Score | Meaning |
|-------|---------|
| 0 | Fail — wrong output, missing section, or incorrect behavior |
| 1 | Partial — correct intent but missing detail, wrong format, or incomplete |
| 2 | Pass — fully correct output matching expected behavior |

### Evaluation Method

Human scoring by the athlete (domain expert). Each test has a specific expected output and pass/fail criterion. Prompts and CLAUDE.md were frozen at Iteration 12 versions throughout testing.
All scored benchmark runs were executed in Claude Code (Opus). I also tested `/checkin` with Codex after adding `AGENTS.md`; guidance adherence improved, but behavior still did not fully match the expected workflow/format, so those Codex runs were not included in benchmark scoring.

### Aggregate Results (Scored Scenarios Only)

| # | Scenario | Tests | Score |
|---|----------|-------|-------|
| 1 | Normal checkin + log session | 17 | 34/34 |
| 2 | Already trained today | 8 | 16/16 |
| 3.1 | Rest / cardio day | 11 | 22/22 |
| 3.2 | Rest day override + 4th session | 32 | 64/64 |
| 4 | Ambiguous / vague input | 16 | 32/32 |
| 5 | Baseline comparison | 11 | 22/22 vs 5.5/22 |
| 6 | Skipped session detection | 14 | 28/28 |
| 7 | Trained yesterday + plan/log mismatch | 4 | 8/8 |
| **Total (scored)** | | **113** | **226/226** |

All 113 scored tests pass after fixing the one failure in Scenario 6.

### Concrete Example 1: Ambiguous Input (Scenario 4)

This scenario tests how the system handles vague athlete inputs at decision thresholds.

**Setup:** Week 2, Wednesday. Planned S session. Yesterday was a full T session (RPE 7 with Snatch Deadlifts).

**Athlete input (deliberately vague):**
```
1. Sleep: "eh, woke up a couple times but got back to sleep"
2. Soreness: "like a 5? maybe 6? hard to tell, quads are tight from yesterday"
3. Energy: "I dunno, 3ish I guess"
```

**System output:**
> Got it — sleep ok-ish, quads tight at a 5-6, energy around 3.
>
> Readiness: Borderline. Quads tight from yesterday's snatch DLs (RPE 7, full session). Soreness hovering around 5-6 is right at the threshold.
>
> **Today: S (Strength) — adjusted**
>
> Keep the S session but lighten the quad load:
> - Front Squat: start light, assess quads during warm-up — if they loosen up, do 5x5; if still tight, cut to 3x5
> - Drop carry-over DB Rows — save them for later
> - Keep Rack Drives and BTN Pullups (upper body, won't tax quads)
>
> Shall I confirm S (adjusted), or would you rather flip to T/mini-T given the quad tightness?

**Key findings:**
- The system interpreted vague inputs without re-asking for exact numbers (5 → "ok", "5 maybe 6" → borderline, "3ish" → 3)
- At the soreness threshold (5-6, where >= 6 = no S/H), it chose a graduated response: adjust the session rather than binary confirm/downgrade
- It connected "quads tight" to yesterday's specific exercises (snatch DLs at RPE 7) — contextual reasoning across sessions
- It offered the athlete a final choice — emergent behavior not explicitly prescribed in the skill

### Concrete Example 2: Baseline Comparison (Scenario 5)

This compares raw Claude (no skills, no data access, no MCP tools) to the `/checkin` skill on the identical situation.

**Same input for both:** Week 2 Tuesday, sleep ok, soreness 2, energy 3.

**Raw Claude** was given only the prompt: *"I'm an Olympic weightlifter following the Leg Drive program. It's Week 2 of 8, Tuesday. I slept OK, soreness is 2/10, energy 3/5. What should I train today?"*

| Dimension | Raw Claude | /checkin |
|-----------|:---------:|:-------:|
| Correct exercises | 2 | 2 |
| Sets/reps/notes | 1 | 2 |
| Session type (T/S/H) | 0 | 2 |
| Readiness assessment | 1.5 | 2 |
| Stop rules | 1 | 2 |
| Strava interference | 0 | 2 |
| Weather for cardio | 0 | 2 |
| Carry-overs | 0 | 2 |
| Time-flex suggestions | 0 | 2 |
| Next session preview | 0 | 2 |
| Plan consistency | 0 | 2 |
| **Total** | **5.5/22 (25%)** | **22/22 (100%)** |

Raw Claude scored higher than predicted (25% vs. an expected ~9%) because it could read the Excel spreadsheet and extract correct exercises. However, it still lacks 8 of 11 evaluated dimensions — all the agentic layers: session typing, Strava cross-reference, weather gating, carry-overs, time-flex, and plan management.

**Key insight:** The system's value isn't in being "smarter" than raw Claude. It's in having the right information at the right time and applying consistent rules. A human coach with a clipboard could do the same thing, but this system does it in 10 seconds.

### Failure Analysis

**Hard failure (1):** Scenario 6, test #14. The AI detected a skipped session and carried over exercises but didn't ask about adjusting weekly volume. **Root cause:** checkin Step 3 had carry-over logic but no volume renegotiation prompt. **Fix:** Added "Want to keep [N] sessions or adjust to [N-1]?" to Step 3. After the fix, all 14 tests pass.

**Soft issues observed (4):**
1. Verbosity on rest days — full weather summary when a 2-line response would suffice
2. Borderline soreness — system doesn't explicitly state which number it used, just says "5-6"
3. Carry-over accumulation — if the same exercise is missed across multiple weeks, the carry-over list grows without bound
4. No Strava fallback messaging — when Strava is unavailable, it silently skips (no transparency)

**Untested failure modes (3):**
- Strava token expiry mid-session (OAuth refresh token is long-lived but not permanent)
- Program week overflow (what happens after week 8? The formula clamps to 1-8 but /weekly-plan would try to plan week 9)
- Concurrent plan edits (if /weekly-plan and /checkin run simultaneously, last writer wins)

### Reproducibility

All scored scenarios include:
- Exact preconditions (plan state, log entries, Strava data)
- Exact athlete inputs (sleep, soreness, energy)
- Expected outputs per test case
- Data state after scenario

To reproduce: reset data files to the precondition state described in each scenario, run the skill, and verify against the test matrix. All scenario files are in `tests/`.

---

## 7. Reflection

### Why This Workflow

Training decision-making is a genuine daily pain point. I spend 5-10 minutes before each session reconciling a 5-day program with a 3-day schedule, checking weather for cardio, and mentally reviewing what I missed last week. This system reduces that to a 10-second check-in.

### What Worked Well

1. **CLAUDE.md as single source of truth.** Domain rules live in one file. Skills reference sections by name instead of duplicating content. When I changed the soreness threshold, I edited one line and all three skills picked it up.

2. **Two-phase workflow (plan + checkin).** Planning once per week and confirming daily matches how athletes actually think. The weekly plan serves as a cache — `/checkin` doesn't need to recalculate everything from scratch.

3. **MCP tools for real-time data.** Weather and Strava provide signals that static prompts can't access. The interference detection (hard ski → avoid heavy S/H next day) caught a real scenario in testing.

4. **Prompt deduplication.** Reducing skills by 50% net (517 → 259 lines, with a low of ~162 before feature additions) while preserving behavior was the highest-leverage improvement. Faster responses, single source of truth, easier iteration.

### What Did Not Work Well

1. **Verbosity.** The system sometimes produces 300+ word outputs for simple confirmations. Rest days don't need a full weather table and protection rule paragraph. This is a prompt tuning issue — the output templates constrain format but not length.

2. **No auto-scheduling.** Claude Code skills can't run autonomously on a schedule. The system only works when the athlete manually invokes `/checkin`. If I forget, there's no nudge. A staleness check was added to `/checkin` (if no plan exists, offer to run `/weekly-plan`), but it's not truly proactive.

3. **Carry-over debt.** If the same exercise is skipped for 3 weeks, the carry-over list accumulates without aging out. This wasn't triggered in testing (only 2 weeks of data) but would be a problem over a full 8-week cycle.

### How Prompts Evolved

The biggest evolution was from monolithic → modular:
- **v1:** One skill that asked 5 questions, read 4 files, called 2 APIs, and ran all logic
- **v2:** Three skills with clear separation of concerns
- **v3:** Skills reference CLAUDE.md instead of duplicating content

Each iteration was triggered by real usage friction: too many questions, too slow, redundant data, bloated prompts.

### What the Benchmark Revealed

The baseline comparison was the most telling result. Raw Claude scored 25% (5.5/22) — better than expected on exercises (it could read the spreadsheet) but zero on 8 of 11 dimensions. The agentic layers (MCP tools, decision rules, state management, output formatting) are where the value lives.

The one hard failure (Scenario 6, test #14) demonstrated that benchmarking works as intended: it found a real gap, triggered a real fix, and the fix was verified by re-running the test.

### Would I Keep Using This System?

**Yes.** I've been using it for the last 2 weeks of real training and it has already saved decision time. The check-in is genuinely fast (10 seconds), the exercise carry-over prevents things from falling through cracks, and the Strava integration catches interference I might overlook.

**Caveats:** I would need to address the carry-over accumulation issue before week 4-5 of the program, and the verbosity on rest days needs prompt tuning. The system also assumes a single program — if I run a squat specialization cycle alongside the base program, the merge logic isn't implemented yet (planned as a future iteration). Cross-LLM portability is also a current limitation: after adding `AGENTS.md`, Codex behavior improved but still did not fully match the Claude-tuned skill behavior, so multi-LLM reliability still needs dedicated testing.

---

## 8. Replication Guide

To rebuild this system from scratch:

### Prerequisites
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI or VS Code extension)
- Python 3.12+
- A Strava account (optional)

### Step 1: Clone and set up
```bash
git clone <repo-url>
cd <repo-folder>                # e.g., TrainSmart
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install fastmcp openpyxl
# Optional (Windows SSL hardening for Strava):
# pip install certifi
```

### Step 2: Parse your program
If starting from a new Excel spreadsheet:
```bash
python scripts/parse_excel.py "references/Leg Drive.xlsx" 2026-02-02
```
Windows shortcut (optional local helper):
```powershell
.\scripts\parse_program.ps1 -File "references\Leg Drive.xlsx" -StartDate 2026-02-02
```
This generates `data/program.json` and `data/program_summary.md`.

### Step 3: Configure Strava (optional)
```bash
copy data\strava_config.template.json data\strava_config.json   # Windows
# cp data/strava_config.template.json data/strava_config.json    # macOS/Linux
# Edit strava_config.json with your Client ID and Client Secret
# (Get these from https://www.strava.com/settings/api)
python scripts/strava_auth.py
```

### Step 4: Start Claude Code
Open the project folder in Claude Code (or VS Code with the Claude Code extension). The `.mcp.json` file auto-registers both MCP servers.

### Step 5: Run the skills
```
/weekly-plan          # Plan your training week
/checkin              # Pre-session check-in
/log-session          # Log what you did
```

### Key Files to Customize
- **CLAUDE.md** — Change athlete profile, session types, decision thresholds, stop rules
- **data/preferences.json** — Change location coordinates and weather thresholds
- **data/prs.json** — Set your personal records
- **.claude/skills/\*/SKILL.md** — Modify skill workflows

---

## Appendix A: Skill File Contents (Exact)

The full contents of each skill file are reproduced below. These are the actual prompts loaded by Claude Code when a skill is invoked.

### `/checkin` — `.claude/skills/checkin/SKILL.md` (97 lines)

```markdown
---
name: checkin
description: Quick pre-workout check-in. Reads your weekly plan, checks how you feel,
  and confirms or adjusts today's session. Use right before training — takes 10 seconds.
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
**Program:** [program_name] | **Week [week_number] of [total_weeks]** | **[Today's day], [date]**
Do NOT read `program.json` here — the plan already has everything needed.

### Step 1: Ask (3 questions only)

Pre-workout check:
1. Sleep last night: good / ok / bad
2. Leg soreness (0-10):
3. Energy (1-5):
If the athlete volunteers extra info, use it. Don't ask for more.

### Step 2: Gather data (in parallel)

1. **Weekly plan** → already loaded in Step 0. Find today's session. If no plan exists → offer:
   (1) run `/weekly-plan` or (2) quick fallback (read `program.json` + apply decision rules).
2. **Training log** → Read `data/training_log.ndjson`. Check completed vs. missed sessions this
   week + recent cardio (48h).
3. **PRs** → Read `data/prs.json`. Used in Step 4 to show target weights per CLAUDE.md
   "Weight Guidance".
4. **Strava** (days_back=2) → Classify per CLAUDE.md "Strava Activity Types". If unavailable or
   returns `"status": "not_configured"`, skip silently and rely on training log for recent activity
   data. **Skip if the weekly plan was created today** (`created_date` == today) — Strava data was
   already fetched by `/weekly-plan` and recent activity is reflected in the plan's notes.
5. **Weather** (days=1) → Only if today has a cardio suggestion in the plan. **Skip if the weekly
   plan was created today** — weather was already checked by `/weekly-plan`.

### Step 3: Decide

Apply CLAUDE.md "Session Selection Decision Rules". If readiness is BAD (soreness >= 6 OR bad
sleep + energy <= 2): S→mini-S/T, H→mini-T/recovery, Condensed→drop extras. T is always OK.

**Missed sessions:** If a planned session has no matching log entry and no Strava activity for
that date, flag it. Ask if it was skipped or just unlogged. If skipped: mark it `"skipped"` in
the plan, carry over 1-2 key exercises (cut accessories), and ask: "Want to keep [N] sessions
this week or adjust to [N-1]?"
**Hard cardio in last 24-36h:** apply protection rule from plan, or switch to T/mini.
**Not a planned day:** Ask the athlete what they want to do:
1. **Pull forward next session** — carry over the next planned session to today.
2. **Just log training** — skip session planning, keep the weekly plan as-is.
3. **Add a hybrid (T2) session** — add an extra session for the week. Build a T2 per CLAUDE.md
   rules. If readiness is bad, suggest option 1 or 2 instead.

### Step 3b: Time-flex suggestions

**Short on time?** Drop: accessories → carry-overs → lower-priority strength. Never drop main lift(s).
**Extra time?** Add: carry-overs → skipped-day accessories → back-off sets.
Keep each list to 2-3 items with exercise names.

### Step 4: Output

Format per templates in `references/skill_schemas.md` (confirming / adjusting / no-plan). Always
include 2 stop rules from CLAUDE.md + time-flex lines. Show target weights per CLAUDE.md "Weight
Guidance" for exercises with a matching PR.

### Step 5: Update plan if changed

If today was **not in the schedule** or the recommended session **differs from the plan**: read
`data/current_week_plan.json`, update the `schedule` array, and write it back. If a session was
pulled forward, mark that day's status as `"moved"`. Skip this step if the session matches exactly.

## Failure Modes and Fallbacks

- Missing weekly plan file: offer `(1) /weekly-plan` or `(2) quick fallback for today`
- Strava unavailable/not configured: continue using training log only
- Weather unavailable: skip weather-based cardio gating and continue
- Tool/read errors on optional data: continue with available inputs; do not block the check-in

## Constraints

- Max 3 questions
- Never recommend S or H when soreness >= 6
- Always include 2 stop rules (CLAUDE.md)
- Use the weekly plan — don't recalculate from scratch
- If tools fail, continue without them
```

### `/weekly-plan` — `.claude/skills/weekly-plan/SKILL.md` (94 lines)

```markdown
---
name: weekly-plan
description: Plan your training week. Sets how many days you'll train, picks the best days based
  on weather and schedule, and saves a tentative plan. Use at the start of each week (Sunday/Monday).
---

# Weekly Planner

Review last week, ask schedule preferences, build day-by-day schedule (WL + cardio), save to
`data/current_week_plan.json`.

## Inputs

- Athlete inputs: available training days, outdoor cardio preference, fatigue/pain
- Competition date confirmation/update from `data/preferences.json`
- Program/training context: `data/program.json`, `data/training_log.ndjson`, `data/prs.json`
- External context: weather forecast and Strava recent activities (if available)

## Outputs

- Weekly schedule response (day-by-day WL/cardio plan + rationale)
- Saved/updated `data/current_week_plan.json` including `program_name` and `total_weeks`

## Workflow

### Step 0: Check for competition date

Before asking anything, read `data/preferences.json` and check for a `competition_date` field.
- **If a competition date exists:** Show it to the athlete and ask to confirm it's still correct.
  Also ask if there are any other competitions or events before that date.
- **If no competition date exists:** Ask if there's a competition within the next 4 weeks. If yes,
  save the date to `data/preferences.json` as `competition_date` (ISO format).

### Step 1: Ask the athlete (all at once)

Quick weekly planning:
1. Which days are you training this week? (e.g., "Tue, Thu, Sat" or "none")
2. Want to plan outdoor cardio? (yes/no — I'll check weather)
3. How are you feeling? Fatigue: low/medium/high, any pain?
Note: Competition question is handled in Step 0 — do NOT ask again here.

### Step 2: Gather data (in parallel)

1. **Last week's log** → Read `data/training_log.ndjson`. Summarize: sessions done, exercises
   completed vs. skipped, cardio, RPE avg, soreness trend.
2. **Program** → Read `data/program.json`. Calculate week number per CLAUDE.md formula. Look up
   prescribed exercises for all 5 days.
3. **PRs** → Read `data/prs.json`. Used in Step 3 to compute target weights per CLAUDE.md
   "Weight Guidance".
4. **Weather** (days=7) → Identify outdoor-suitable days per CLAUDE.md "Weather Preferences".
5. **Strava** (days_back=7) → Classify per CLAUDE.md "Strava Activity Types".

After loading data, do a quick log-completeness check (no hard block):
- **If Strava is available:** Cross-check last week's Strava activities against
  `training_log.ndjson`. If likely training sessions are missing from the log, ask whether to log
  missing sessions.
- **If Strava is unavailable/not configured:** Ask: "Are last week's training days accurately
  logged, or do you want to add anything before I plan this week?"
- In both cases, athlete chooses whether to add info now or continue planning. Never block.

### Step 3: Build the schedule

Assign T/S/H/Hybrid per CLAUDE.md "T/S/H Session System". Priority when fewer than 5 days:
T → S → H. (0=rest, 1=T, 2=T+S, 3=T+S+H, 4=+Hybrid, 5=full week). If no heavy work in 7+ days,
prioritize H over S.
**Intensity:** default normal. Use condensed to pull 1-2 priority exercises from skipped days.
Use light/mini when fatigued. See condensed example in `references/skill_schemas.md`.
**Weights:** For each exercise with a matching PR in `prs.json`, compute target weight range per
CLAUDE.md "Weight Guidance" and show it inline.
**Spacing:** >= 1 rest day between sessions when possible. Note carry-overs from last week.
**Cardio:** place on weather-suitable non-WL days. Hard run/ski never before H or heavy S.
**Competition taper:** D-10→D-5: reduce volume 20-40%. D-4→D-2: light technique. D-1: mini-T/mobility.
**Fatigue:** High/pain >5 → all mini. Medium → standard. Low → full.

### Step 4: Save the plan

Read then overwrite `data/current_week_plan.json`. Include `program_name` and `total_weeks` from
program.json so `/checkin` can skip reading the program file. Schema in `references/skill_schemas.md`.

### Step 5: Output

Format per template in `references/skill_schemas.md`. Display temperatures as C (F) per CLAUDE.md.

## Failure Modes and Fallbacks

- Weather unavailable: plan with log/program data only and skip weather ranking
- Strava unavailable/not configured: ask about recent cardio or rely on training log
- Missing/limited recent logs: continue planning from program + athlete inputs
- Conflicting availability constraints: prioritize requested WL day count

## Constraints

- Never schedule more WL days than requested
- Always save to `data/current_week_plan.json` with `program_name` + `total_weeks`
- Maximum 1 protection rule
- Schedule is a suggestion — athlete can move sessions
- If weather/Strava unavailable, skip or use log data only
- Log-completeness checks are advisory only (user choice, no hard-block)
```

### `/log-session` — `.claude/skills/log-session/SKILL.md` (68 lines)

```markdown
---
name: log-session
description: Log a completed training session. Records what you did, compares to the program
  prescription, and updates your training log. Use after training.
---

# Session Logger

Record a completed session to `data/training_log.ndjson`. Compare against prescription. Check
for new PRs.

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

Read `data/program.json`. Calculate week number from `log_date` per CLAUDE.md formula (not always
from today). Match performed exercises against prescription. "as prescribed" -> all completed.
Unmatched extras -> bonus entries. Cardio -> no comparison.

### Step 3: Build + save

Build entry as a single-line JSON object per schema in `references/skill_schemas.md`. Append it
to `data/training_log.ndjson` using Bash: `echo '<json>' >> data/training_log.ndjson`.
**Append only - never read+rewrite the file.**

### Step 4: Check PRs

Read `data/prs.json`. Compare logged weights against PR-tracked exercises (CLAUDE.md "Personal
Records"). If exceeded -> update `prs.json`.

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
```

## Appendix B: Benchmark Test Case Table

Full test results across 8 scored scenarios (113 tests).

| Scenario | # | Test | Pass |
|----------|---|------|:----:|
| **1. Normal checkin** | 1 | Context line displayed | Y |
| | 2 | Correct session confirmed (T) | Y |
| | 3 | Even-week Tuesday exercises | Y |
| | 4 | Exercise notes from program | Y |
| | 5 | Time-flex suggestions present | Y |
| | 6 | Stop rules (exactly 2) | Y |
| | 7 | No unnecessary adjustment | Y |
| | 8 | Strava — no interference | Y |
| | 9 | Log: asks only missing info | Y |
| | 10 | Log: exercises correct | Y |
| | 11 | Log: all marked completed | Y |
| | 12 | Log: no skipped exercises | Y |
| | 13 | Log: entry appended (NDJSON) | Y |
| | 14 | Log: plan status → completed | Y |
| | 15 | Log: next session previewed | Y |
| | 16 | Log: cardio suggestion | Y |
| | 17 | Log: output format correct | Y |
| **2. Already trained** | 1 | Detects today's session done | Y |
| | 2 | Does not re-recommend | Y |
| | 3 | Shows next session preview | Y |
| | 4 | No readiness questions | Y |
| | 5 | Strava cross-referenced | Y |
| | 6 | Log entry matched | Y |
| | 7 | Graceful messaging | Y |
| | 8 | No plan modification | Y |
| **3.1 Rest day** | 1 | Context line | Y |
| | 2 | Rest day identified | Y |
| | 3 | Readiness questions asked | Y |
| | 4 | Cardio suggestion (Bike Z2) | Y |
| | 5 | Weather checked | Y |
| | 6 | Next lifting session previewed | Y |
| | 7 | No lifting recommendation | Y |
| | 8 | Weather data in output | Y |
| | 9 | Cross-day awareness | Y |
| | 10 | Stop rules suppressed | Y |
| | 11 | Time-flex suppressed | Y |
| **3.2 Rest day override** | 1-6 | Initial rest day response | Y |
| | 7-14 | Override accepted + S session | Y |
| | 15-21 | 4th session addition | Y |
| | 22-32 | Plan file correctly updated | Y |
| **4. Ambiguous input** | 1-5 | Vague input interpretation | Y |
| | 6-14 | Decision at threshold | Y |
| | 15-16 | Strava + context cross-ref | Y |
| **5. Baseline** | 1-11 | 11 dimensions scored (see Section 6) | — |
| **6. Skipped session** | 1-2 | Context + readiness | Y |
| | 3-5 | Missed session detection | Y |
| | 6-10 | Session + carry-over | Y |
| | 11-13 | Output format | Y |
| | 14 | Volume adjustment question | Y |
| **7. Trained yesterday + plan/log mismatch** | 1-3 | Session selection + stop rules | Y |
| | 4 | Output format (adjusting template) | Y |

**Total: 113 tests, 226/226 score (100%)**

## Appendix C: CLAUDE.md (Full Contents)

See the [CLAUDE.md file in the GitHub repository](https://github.com/SandrineLpx/TrainSmart/blob/main/CLAUDE.md) for the complete ~120-line domain rules file.
