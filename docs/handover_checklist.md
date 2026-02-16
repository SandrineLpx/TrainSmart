# Handover Checklist (Quick Setup)

## What Is Included

### Skills (`.claude/skills/*/SKILL.md`)
- `/weekly-plan`: weekly schedule builder (WL + optional cardio)
- `/checkin`: pre-session readiness check and session adjustment
- `/log-session`: post-session logging + PR update handling

### MCP servers (`mcp_servers/`)
- `weather_mcp.py`: Open-Meteo forecast (no API key)
- `strava_mcp.py`: Strava API integration (optional, requires OAuth)

### Core data/config files
- `data/program.json`: parsed 8-week program
- `data/program_summary.md`: human-readable program summary
- `data/current_week_plan.json`: active weekly plan
- `data/training_log.ndjson`: append-only log
- `data/prs.json`: PR tracking
- `data/preferences.json`: weather thresholds + program dates
- `CLAUDE.md`: domain rules and decision logic
- `.mcp.json`: MCP registration for Claude Code

## 5-Minute Quick Setup (New User)

1. Create and activate virtual env
   - `python -m venv .venv`
   - Windows: `.\.venv\Scripts\activate`
2. Install dependencies
   - `pip install fastmcp openpyxl`
3. Optional Strava setup (optional)
   - Copy template: `copy data\strava_config.template.json data\strava_config.json`
   - Create Strava API app: `https://www.strava.com/settings/api`
   - Run OAuth: `python scripts/strava_auth.py`
4. If using a new coach spreadsheet, parse it
   - `python scripts/parse_excel.py "references/Leg Drive.xlsx" 2026-02-02`
5. Open Claude Code in project root and run:
   - `/weekly-plan`
   - `/checkin`
   - `/log-session`

## Quick Validation (Smoke Test)

1. `/weekly-plan` saves/updates `data/current_week_plan.json`
2. `/checkin` reads plan and returns session type + stop rules
3. `/log-session` appends one JSON line to `data/training_log.ndjson`
4. If Strava is not configured, skills still run with fallback behavior

## Current Benchmark Status

- Scenarios: `8` (`tests/scenario_*.md`)
- Total tests: `113`
- Score: `226/226`
- Summary: `tests/benchmark_summary.md`
- Appendix: `tests/benchmark_appendix.md`

## HW2 Submission Readiness

1. Artifact ready: skills + MCP servers + data files present
2. Tutorial includes problem/design/iterations/real usage/benchmark/reflection/replication
3. Baseline comparison included
4. Edge case + ambiguous case included
5. Demo video link placeholder added
6. Repo link + final video link inserted
7. Final PDF exported
