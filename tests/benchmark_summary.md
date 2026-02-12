# Benchmark Summary — Train Smart System

## Methodology

- **Evaluation method:** Human scoring (athlete as domain expert) + automated checks (data file validation)
- **Prompts frozen:** All SKILL.md files at Iteration 12 versions throughout testing
- **Environment:** Claude Code with Opus model, Windows 11, both MCP servers running

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 0 | Fail — wrong output, missing section, or incorrect behavior |
| 1 | Partial — correct intent but missing detail, wrong format, or incomplete |
| 2 | Pass — fully correct output matching expected behavior |

## Aggregate Results

| # | Scenario | Type | Skill | Tests | Pass | Partial | Fail | Score |
|---|----------|------|-------|-------|------|---------|------|-------|
| 1 | Normal checkin + log session | Happy path | /checkin + /log-session | 17 | 17 | 0 | 0 | 34/34 |
| 2 | Already trained today | Edge case | /checkin | 8 | 8 | 0 | 0 | 16/16 |
| 3.1 | Rest / cardio day | Edge case | /checkin | 11 | 11 | 0 | 0 | 22/22 |
| 3.2 | Rest day override + 4th session | Edge case | /checkin | 32 | 32 | 0 | 0 | 64/64 |
| 4 | Ambiguous / vague input | Ambiguous | /checkin | 16 | 16 | 0 | 0 | 32/32 |
| 5 | Baseline comparison | Baseline | /checkin vs raw Claude | 11 | — | — | — | 22/22 vs 5.5/22 |
| 6 | Skipped session detection | Edge case | /checkin | 14 | 14 | 0 | 0 | 28/28 |
| **Total** | | | | **109** | **98** | **0** | **0** | **218/218** |

(Scenario 5 scored separately — see baseline comparison detail below.)
Note: Scenario 6 test #14 initially failed, triggering a fix to `/checkin` Step 3 (volume adjustment question). After the fix, all 14 tests pass.

## Scenario Coverage

| Category | Rubric requirement | Covered by |
|----------|--------------------|------------|
| 2+ test cases | Yes (7 scenarios) | All |
| Clear metrics | 0/1/2 scoring per test | All |
| Edge cases | At least 1 | Scenarios 2, 3.1, 3.2 |
| Ambiguous case | At least 1 | Scenario 4 |
| Baseline comparison | At least 1 | Scenario 5 |
| Failure analysis | Required | See below |

## Baseline Comparison Summary (Scenario 5)

| Dimension | Raw Claude (0-2) | /checkin (0-2) |
|-----------|-----------------|----------------|
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

Raw Claude scored higher than predicted (25% vs 9%) because it could read the Excel spreadsheet and extract correct exercises. However, it still lacks the agentic layers: session typing, Strava cross-reference, weather gating, carry-overs, time-flex, and plan management.

## Failure Analysis

### No hard failures observed

98 of 98 scored tests pass across 7 scenarios (after fixing the one failure in Scenario 6). The initial failure — missing volume adjustment question on skipped sessions — was the only hard failure found. It triggered a real improvement to `/checkin` Step 3. The remaining test cases were designed after 12 iterations, so they validate current behavior rather than stress-testing unknown inputs.

### Soft issues observed during testing

1. **Verbosity on rest days (Scenario 3.1):** Output was longer than necessary for a rest day — included a full weather summary and protection rule paragraph when a 2-line "rest day, bike Z2 if weather holds" would suffice. Not a failure, but a UX improvement opportunity.

2. **Borderline soreness — graduated response (Scenario 4):** When the athlete said "like a 5? maybe 6?", the system chose a middle path: keep S but adjust quad load (Front Squat conditional 5x5→3x5, drop carry-over DB Rows). This is better than a binary confirm/downgrade, but it didn't explicitly state which soreness number it used — just "borderline (5-6)." More transparent output would say "Interpreting as 5-6, keeping S with reduced quad volume." Also notably, it offered the athlete a final choice ("confirm or flip to T?"), which is good coaching but wasn't prescribed in the skill — emergent behavior.

3. **Carry-over accumulation:** If the athlete keeps missing the same exercise across multiple weeks, the carry-over list grows without bound. The system doesn't age-out or deprioritize old carry-overs. Not triggered in testing (only 2 weeks of data), but would surface over a full 8-week program.

4. **No Strava fallback messaging:** When Strava MCP is unavailable, the skill silently skips it (by design). But the athlete has no way to know whether Strava was checked or not. A one-line note ("Strava: unavailable, skipped") would add transparency.

### Potential failure modes not yet tested

- **Strava token expiry mid-session:** OAuth refresh could fail if the refresh token itself expires (Strava tokens expire after 6 hours; refresh tokens are long-lived but not permanent)
- **Program week overflow:** What happens after week 8? The week calculation clamps to 1-8, but `/weekly-plan` would still try to build a schedule from a non-existent week 9
- **Concurrent plan edits:** If the athlete runs `/weekly-plan` and `/checkin` simultaneously, both could write to `current_week_plan.json` — last writer wins

## Reproducibility

All test scenarios include:
- Exact preconditions (plan state, log entries, Strava data)
- Exact athlete inputs (sleep, soreness, energy)
- Expected outputs per test case
- Data state after scenario

To reproduce: reset data files to the precondition state described in each scenario, run the skill, and verify against the test matrix.
