# Skill Reference — JSON Schemas, Examples & Output Templates

Reference file for skill SKILL.md files. Not loaded automatically — skills read this only when they need a schema or example.

---

## current_week_plan.json schema

Written by `/weekly-plan`, read by `/checkin`.

```json
{
  "program_name": "Leg Drive",
  "total_weeks": 8,
  "week_number": 2,
  "created_date": "2026-02-09",
  "training_days_planned": 3,
  "schedule": [
    {
      "day": "Tuesday", "date": "2026-02-11",
      "type": "T", "intensity": "normal",
      "focus": "Snatch Pull + Snatch, Snatch DL",
      "key_exercises": ["Snatch Pull + Snatch 6x1+1", "Snatch Deadlift 6x3"],
      "carry_over": [], "status": "planned"
    },
    {
      "day": "Thursday", "date": "2026-02-13",
      "type": "S", "intensity": "condensed",
      "focus": "BTN Thrusters, Pause BS + Snatch Pull from Tue",
      "key_exercises": ["BTN Thrusters 6x3", "Pause Back Squats 6x2", "Snatch Pull + Snatch 6x1+1 (from Tue)"],
      "carry_over": ["DB Row (missed last week)"], "status": "planned"
    },
    {
      "day": "Saturday", "date": "2026-02-15",
      "type": "H", "intensity": "normal",
      "focus": "Heavy singles — Snatch + Clean & Jerk",
      "key_exercises": ["Snatch 3 heavy singles", "Clean & Jerk 3 heavy reps"],
      "carry_over": [], "status": "planned"
    }
  ],
  "cardio_suggestions": [
    { "day": "Wednesday", "date": "2026-02-12", "activity": "Bike Z2", "duration": "30-45 min", "weather": "11°C (52°F), 5% rain, 6mph wind" }
  ],
  "protection_rule": "If hard run Wed, switch Sat H to mini-H",
  "notes": "Even-week pattern. Volume: 6 sets on main lifts."
}
```

---

## training_log.ndjson entry schemas

File: `data/training_log.ndjson` — NDJSON format (one JSON object per line).
- **Write:** append a single line via Bash `echo '<json>' >> data/training_log.ndjson`
- **Read:** Read tool returns all lines; parse each line as independent JSON

**WL session (one line):**
```json
{"date":"YYYY-MM-DD","week_number":1,"day_of_week":"Monday","session_type":"S","intensity":"normal","exercises_performed":[{"exercise":"Clean & Jerk + Jerk","sets_done":6,"weight_kg":55,"completed":true},{"exercise":"DB Row","sets_done":0,"completed":false}],"rpe":7,"sleep":"good","leg_soreness":3,"notes":""}
```

**Cardio (one line):**
```json
{"date":"YYYY-MM-DD","week_number":1,"day_of_week":"Wednesday","session_type":"cardio","activity":"bike","duration_minutes":45,"intensity":"Z2","rpe":4,"sleep":"ok","leg_soreness":2,"notes":""}
```

---

## Condensed session example

3 days (Mon, Wed, Fri) in Week 2 (even):
- **Mon (S-condensed):** BTN Thrusters 6x3, Pause BS 6x2 + *Snatch Pull 6x1+1 from Tue* + *Front Squat 5x5 from Thu*
- **Wed (T2-normal):** Hang Clean + Jerks 6x1+1+1, Jerk Recovery 6x1+1, Cossack Squats
- **Fri (H-normal):** Snatch 3 heavy singles, C&J 3 heavy reps, Side Bends

Mon covers strength + technique + squats, Wed covers jerk work, Fri covers heavy day. Nothing critical missed.

---

## Output templates

### /checkin — confirming
```
**Today:** [type] (as planned)

**Session:**
- [Exercise 1] — [sets] x [reps]
- [Exercise 2] — [sets] x [reps]
[+ carry-over if any]

**Short on time?** Drop: [list]
**Extra time?** Add: [list]

**Stop rules:** [2 stop rules from CLAUDE.md]
```

### /checkin — adjusting
```
**Today:** [adjusted type] (was: [original])
**Why:** [1 line]

**Session:** [exercises with sets × reps]
**Adjustments:** [max 2 bullets]

**Short on time?** Drop: [list]  |  **Extra time?** Add: [list]

**Stop rules:** [2 stop rules from CLAUDE.md]
```

### /checkin — no plan fallback
```
**Today:** [type] (no weekly plan — using program defaults)
**Session:** [exercises with sets × reps]
**Short on time?** Drop: [list]  |  **Extra time?** Add: [list]
**Stop rules:** [2 stop rules from CLAUDE.md]
**Tip:** Run `/weekly-plan` next time — makes daily check-ins instant.
```

### /weekly-plan
```
## Last Week Review
**Done:** [sessions] | **Missed:** [carry-overs or "Clean week!"]
**Cardio:** [summary] | **RPE avg:** [N] | **Soreness trend:** [trend]

---

## This Week's Plan (Week [N])
**Training days:** [N] | **Pattern:** [odd/even] | **Fatigue adjustment:** [none/reduced/light]

| Day | Session | Intensity | Focus | Notes |
|-----|---------|-----------|-------|-------|

**Outdoor cardio:**
| Day | Activity | Weather |
|-----|----------|---------|

**Protection rule:** [rule]

---

## 7-Day Weather
| Day | High | Low | Rain% | Wind | Outdoor? |
|-----|------|-----|-------|------|----------|

**Plan saved.** Use `/checkin` before each session.
```

Display temperatures as °C (°F) per CLAUDE.md.

### /log-session
```
**Today:** [today_date] | **Logged for:** [date] (Week [N], [day]) — Session [type]

**Performed:**
- [Exercise 1] — [sets] × [reps] ✓
- ...

**Skipped:** [prescribed but not done, or "None"]
**PRs:** [new PRs, e.g., "Snatch 59kg (was 57kg)" — omit if none]
**Stats:** RPE: [N] | Sleep: [quality] | Soreness: [N]/10
```

### /onboard
```
**Local setup status**
- preferences.json: [available | missing]
- prs.json: [created | existing | reset]
- strava_config.json: [created | existing | reset | skipped]

**Personalization**
- Preferences updated: [yes/no]
- PRs updated: [yes/no]

**Next**
1. Review `data/preferences.json` and `data/prs.json`
2. Run `/weekly-plan`
```
