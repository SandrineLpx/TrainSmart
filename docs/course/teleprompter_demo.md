# Demo Teleprompter — End-to-End Training Session

**Format:** Screen recording with voiceover
**Duration:** ~5-6 minutes
**Tools visible:** VS Code + Claude Code terminal

---

## INTRO (45s)

> I built an agentic training assistant for Olympic weightlifting using Claude Code. It has three skills that chain together: weekly plan, check-in, and log session. I'll walk through all three in a single real session — planning my week, checking in before training, and logging what I did.
>
> At the start of a training cycle, I upload my coach's Excel program, and it gets parsed into program.json and program_summary.md — a human-readable snapshot for planning.

**[Briefly show the repo structure in VS Code sidebar]**

> Here's the repo. The skills live in .claude/skills/, the rules are in CLAUDE.md, and state is stored in the data/ folder. The system reads the program, checks weather and Strava data via MCP tools, applies sport-specific decision rules, and writes structured JSON files that persist between sessions.

---

## SKILL 1: /weekly-plan (2 min)

**[Type `/weekly-plan` in terminal]**

> I start each week by running slash weekly-plan. The agent kicks off by confirming my competition date — March 28th — then asks me three things: which days I can train, whether I want outdoor cardio, and how I'm feeling.

**[Show the question UI appearing — pause to let viewer read]**

> I pick three days — Tuesday, Thursday, Friday — say yes to cardio, and report medium fatigue from yesterday's 28-mile bike ride.

**[Select answers]**

> Behind the scenes, it reads five data sources in parallel: my training log, the program file, my personal records, a 7-day weather forecast from an MCP server, and my recent Strava activities through another MCP tool.
>
> It then reviews last week. It found four WL sessions plus a bike ride, and cross-checked Strava against the log — everything matches. But it noticed the Wednesday strength day was skipped, and Saturday's heavy day was kept moderate instead of going heavy. So there's been no true heavy session in over ten days. That becomes a priority.
> It takes about 4 minutes for Claude to read all the data, apply the rules, and build the plan. The rules are in CLAUDE.md. But once it's built, the daily check-in doesn't have to re-apply all the rules — it just reads the plan and updates it as needed.

**[Scroll through the output as it appears]**

> It builds a day-by-day schedule: Tuesday is Technique — yoyo snatches and snatch deadlifts. Thursday is Strength — front squats and rack holds. Friday is Heavy — power snatch and power clean singles, flagged as priority since I haven't gone heavy in over ten days.
>
> For each exercise, it computes a target weight range from my PR file — for example, front squat five-by-five at 52 to 60 kilos, which is 70 to 80 percent of my 75-kilo PR.
>
> It also slots in outdoor cardio on weather-suitable days and adds a protection rule: if my legs are heavy after Thursday's squats, Friday's heavy day drops to a mini session.
>
> Finally, it saves the whole plan to a JSON file that the other skills will read.

---

## SKILL 2: /checkin (1.5 min)

**[Type `/checkin` in terminal]**

> Now I run check-in. It's Monday — not a scheduled training day — so it asks what I want to do: pull Tuesday's session forward, just log whatever I do on my own, or add an extra hybrid session.

**[Show the options appearing]**

> I choose to add a T2 — a hybrid technique session. The system allows this when readiness is decent and there's uncovered priority work. It then asks three quick readiness questions: sleep, soreness, energy.

**[Select: good sleep, soreness 3-5, energy 3]**

> Based on my answers — good sleep, moderate soreness, medium energy — it confirms T2 is appropriate. It checks Strava and sees yesterday's 28-mile bike ride, but since it's a bike and not a hard run or ski, it doesn't block heavier work — just notes the medium fatigue.
>
> It builds the session: BTN power jerks at 58 to 64 kilos, hang snatch plus snatch balance at 41 to 47 kilos, and cossack squats. These cover jerk technique and snatch balance work from the Monday and Wednesday program days I'd otherwise skip this week.
>
> It includes time-flex options — what to cut if I'm short on time, what to add if I have extra — and two stop rules that apply to every session.
>
> Then it updates the weekly plan JSON, bumping me from three to four sessions and marking Monday as planned.

---

## SKILL 3: /log-session (1.5 min)

**[Type `/log-session` in terminal]**

> After training, I run log session. It detects today's date, sees the T2 session in the plan, and asks what I did.

**[Show the question UI]**

> I select "as prescribed" — I did exactly what was planned. RPE 7, ok sleep, soreness 4 out of 10.

**[Select answers]**

> It checks my weights against my personal records file — no PRs today since BTN power jerks and hang snatch plus snatch balance aren't PR-tracked exercises. If I had exceeded a PR on a tracked lift, it would automatically update the PR file and call it out.
>
> It appends a single JSON line to the training log — append-only, never rewriting the file — and marks Monday as completed in the weekly plan.
>
> The confirmation shows everything performed with checkmarks, notes that nothing was skipped, and reminds me what's next: Tuesday's technique session.

---

## WRAP-UP (20s)

> That's the full loop: plan, check in, log. Three skills sharing the same JSON files, with MCP tools pulling in real-world data from Strava and weather. The success criteria I care about are:
>
> One — does it follow the program? It mapped exercises and weights correctly from my coach's prescription.
> Two — does it adapt? It spotted ten days without heavy work, factored in yesterday's long bike ride, adjusted for an unscheduled Monday, and applied readiness rules.
> Three — is it faster than doing it myself? The whole flow took under five minutes, and I didn't have to open a spreadsheet once.
