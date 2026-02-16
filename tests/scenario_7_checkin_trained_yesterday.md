# Scenario 7: Check-in After Training Yesterday, Plan Differs From Log

## Skill Tested
`/checkin`

## Type
Edge case

## Purpose
Validate that `/checkin` recommends a mini-T when soreness is high, even if the plan shows a heavy day and the athlete trained yesterday with a session that differed from the plan, and that the system uses the actual system date.

## Setup / Preconditions
- Program: Leg Drive, Week 2 of 8 (even-week pattern)
- Today: **Friday 2026-02-13** — verified via system date (`Get-Date`)
- Plan state: exists, 5 training days (Tue T, Wed S, Thu T2, Fri T mini, Sat H moved)
- Completed sessions this week: Tue 2026-02-10 (T) completed, Thu 2026-02-12 (custom session logged)
- Training log: appended Thu 2026-02-12 session that differs from the plan
- Strava (last 48h): none available in this interface (MCP not accessible)
- Weather: not used

## Athlete Input
```
1. Sleep last night: good
2. Leg soreness (0-10): 7
3. Energy (1-5): 3
I trained yesterday. I am going to train today.
```

## Actual System Output
> **Today:** mini-T (was: no session scheduled)  
> **Why:** Soreness 7/10 ⇒ technique/mini only.  
>   
> **Session:**  
> - Hang power clean + 2 jerks — 4 x (1+1+1)  
> - Jerk recovery / bottoms-up squat — 4 x (1+1)  
> - Cossack squats — 2 x 10  
>   
> **Adjustments:**  
> - Reduced volume and intensity due to soreness.  
> - No heavy or strength work today.  
>   
> **Short on time?** Drop: cossacks, then one set from each main lift.  |  **Extra time?** Add: 1–2 sets of Hang power clean + 2 jerks, then light accessories.  
>   
> **Stop rules:** If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean. If form still degrades after dropping → switch to mini or stop after priorities.  

## Notes
- The system initially assumed Saturday based on stale context, then corrected to Friday after checking `Get-Date`.

## Tests

### Session Selection Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | High soreness rule applied | Recommends mini-T (not S or H) when soreness is 7/10 | Y |
| 2 | Heavy day avoided | Output explicitly avoids heavy/strength work | Y |
| 3 | Stop rules included | Exactly two stop rules from CLAUDE.md | Y |

### Output Format Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Output follows `/checkin` adjusting template | Includes Today, Why, Session, Adjustments, time-flex, Stop rules | Y |

## Decision Logic Verified
- Session Selection Decision Rules: leg soreness 7 ≥ 6 → mini-T only
- Priority order applied: technique preserved, heavy/strength avoided
- Training occurred yesterday → avoid heavy today (aligned with soreness rule)

## What This Scenario Tests That Others Don't
- **Plan vs. log mismatch**: Check-in recommendation remains valid when the logged session differs from the weekly plan.
- **Back-to-back training**: Soreness threshold blocks heavy work even when a heavy day is planned.

## Data State After Scenario

### training_log.ndjson
- Changed — appended entry for Thu 2026-02-12 with the custom session (back squat 3x3 @ 75 kg, EMOM complexes, RDL 3x8 @ 50 kg).

### current_week_plan.json
- Changed — Fri 2026-02-13 updated to mini-T with soreness note; Sat 2026-02-14 added as H (moved from Friday).

---
<!--
CHECKLIST before marking scenario complete:
- [ ] Purpose is one clear sentence
- [ ] Preconditions are specific enough to reproduce (dates, data state, Strava)
- [ ] Athlete input is exact (quoted, not paraphrased)
- [ ] Actual system output is pasted (blockquote)
- [ ] Every test row has: number, what to verify, expected behavior, Y/N result
- [ ] Decision logic references CLAUDE.md rules by name
- [ ] "What this tests that others don't" has at least 1 bullet
- [ ] Data state shows before→after for all affected files
- [ ] Screenshot attached if available (![alt](filename.png))
-->
