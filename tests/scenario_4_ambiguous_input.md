# Scenario 4: Ambiguous / Vague Athlete Input

## Skill Tested
`/checkin`

## Purpose
Tests how the system handles vague, incomplete, or borderline readiness inputs — the kind of answers a real athlete gives when they're unsure how they feel.

## Setup / Preconditions
- Weekly plan exists: Week 2, 4 training days (Tue T done, Wed S, Thu T2, Fri H)
- Today is **Wednesday Feb 11** — planned S session (pulled forward from Thu)
- Tuesday T session completed yesterday (RPE 7, full session including Snatch DLs)
- Strava: Tuesday WeightTraining logged, no cardio
- Athlete gives vague/ambiguous answers instead of clean numbers

## Athlete Input
```
1. Sleep last night: "eh, woke up a couple times but got back to sleep"
2. Leg soreness (0-10): "like a 5? maybe 6? hard to tell, quads are tight from yesterday"
3. Energy (1-5): "I dunno, 3ish I guess"
```

## Actual System Output

> Got it — sleep ok-ish, quads tight at a 5-6, energy around 3. Let me put this together.
>
> Readiness: Borderline. Quads tight from yesterday's snatch DLs (RPE 7, full session). Soreness hovering around 5-6 is right at the threshold. No hard cardio in the last 48h — just the Tuesday lifting.
>
> Strava: Evening WeightTraining on 2/10 matches your logged T session. All clear.
>
> **Today: S (Strength) — adjusted**
>
> Keep the S session but lighten the quad load given the tightness:
>
> **Adjustments:**
> - Front Squat: start light, assess quads during warm-up — if they loosen up, do 5x5 as written; if still tight, cut to 3x5
> - Drop carry-over DB Rows — save them for later in the week when quads aren't the limiter
> - Keep Rack Drives and BTN Pullups (upper body, won't tax quads)
>
> **Why:** Soreness is borderline (5-6), not clearly over the threshold. Yesterday was pulls + snatch DLs so quad tightness is expected. Front squats will tell you quickly if the quads are ready — warm-up sets are your litmus test.
>
> **Stop rules:**
> - If you lose positions or miss 2 attempts in a row → drop ~5% and finish clean
> - If form still degrades after dropping → switch to mini or stop after priorities
>
> **Time-flex:**
> - Short on time? Drop: Lu Raises → BTN Pullups. Keep front squat + rack drives.
> - Extra time? Add: Paused front squat back-offs (3x3 at -10%) → DB Rows carry-over
>
> Shall I confirm S (adjusted) for today, or would you rather flip to a T/mini-T given the quad tightness?

## Tests

### Interpretation Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 1 | Interprets vague sleep | Maps "woke up a couple times" → "ok" (not good, not bad) | Y |
| 2 | Handles borderline soreness | Soreness "5 maybe 6" is on the threshold — system must make a call | Y |
| 3 | Conservative on borderline | Treats borderline 5-6 with caution — adjusts session rather than confirming as-is | Y |
| 4 | Interprets vague energy | Maps "3ish" → 3 (middle range) | Y |
| 5 | Does not ask for clarification | Proceeds with interpretation — does NOT re-ask for exact numbers | Y |

### Decision Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 6 | Session adjustment triggered | Does NOT confirm S as-is — borderline soreness triggers adjustment logic | Y |
| 7 | Appropriate adjustment level | Keeps S type but adjusts volume/load (not full downgrade to mini-S or T) | Y |
| 8 | Explains the adjustment | "Why" section references soreness threshold and quad tightness from yesterday | Y |
| 9 | Preserves priority exercises | Keeps Front Squat (priority) with conditional volume, drops carry-over DB Rows | Y |
| 10 | Stop rules present | 2 stop rules included (especially important when borderline) | Y |
| 11 | Time-flex present | "Short on time?" and "Extra time?" sections with specific exercise names | Y |
| 12 | Quad tightness acknowledged | References tight quads from yesterday's snatch DLs specifically | Y |
| 13 | Warm-up as litmus test | Suggests using warm-up sets to assess before committing to full volume | Y |
| 14 | Offers athlete final say | Asks if athlete wants to confirm adjusted S or switch to T/mini-T | Y |

### Strava + Context Tests

| # | What to verify | Expected | Pass? |
|---|---------------|----------|-------|
| 15 | Strava cross-referenced | Matches WeightTraining activity to logged T session | Y |
| 16 | Yesterday's RPE used | References RPE 7 from Tuesday's logged session as context for today's tightness | Y |

## Decision Logic Verified
- Vague inputs interpreted, not rejected — real athletes don't give clean numbers
- Borderline soreness (5-6) near the ≥6 threshold → adjusted S, not full downgrade
- System chose a **middle path**: not "confirm as-is" (ignoring risk) and not "downgrade to mini" (overreacting). Instead: keep S type, reduce quad load conditionally, offer athlete the final call
- "Quads tight from yesterday" used as contextual signal — connected to snatch DLs at RPE 7
- Warm-up-as-assessment is a real coaching pattern: let the body tell you before committing
- Final question ("confirm or flip to T?") respects athlete autonomy on borderline calls

## What This Scenario Tests That Others Don't
- **Natural language interpretation**: no clean numbers, hedging, uncertainty ("3ish", "maybe 6")
- **Threshold behavior**: soreness 5-6 is exactly at the decision boundary (≥6 = no S/H)
- **Contextual reasoning**: connects quad tightness to yesterday's specific exercises + RPE
- **Graduated response**: system didn't binary-switch (confirm/downgrade) — it found a middle ground
- **Athlete autonomy**: offered a choice instead of dictating when the call is genuinely ambiguous

## Data State After Scenario

### training_log.ndjson
- Unchanged (session not yet completed — athlete hasn't confirmed)

### current_week_plan.json
- Pending athlete confirmation — if S (adjusted) confirmed, intensity may update to reflect reduced volume
