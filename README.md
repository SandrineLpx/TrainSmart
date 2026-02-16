# Train Smart — Olympic Weightlifting Optimization System

An agentic AI training assistant built with **Claude Code Skills** and **MCP servers** that plans, adapts, and logs Olympic weightlifting sessions using real-time weather and Strava data.

## How It Works

Train Smart wraps an 8-week periodized weightlifting program with three conversational skills:

| Skill | When | What it does |
|-------|------|--------------|
| `/weekly-plan` | Start of week | Reviews last week, asks which days you can train, builds a schedule respecting weather and recovery |
| `/checkin` | Before each session | Reads the plan, asks sleep/soreness/energy, confirms or adjusts today's session type and intensity |
| `/log-session` | After each session | Records what you did, compares to prescription, detects PRs, updates the training log |

The system uses a **T/S/H session model** (Technique / Strength / Heavy) with decision rules that automatically downgrade sessions when fatigue is high, promote heavy work when overdue, and carry over key exercises from skipped days.
Weekly planning scales from **0-5 training days** (`0=rest`, `1=T`, `2=T+S`, `3=T+S+H`, `4=+T2/hybrid when readiness + logs support it`, `5=full week`), with an override to prioritize heavy work if none has been done in 7+ days.

## Architecture

```
CLAUDE.md                 # Domain rules, decision logic, stop rules
.claude/skills/           # Three skill definitions (checkin, log-session, weekly-plan)
mcp_servers/
  weather_mcp.py          # Open-Meteo forecast for Kirkland, WA (no API key)
  strava_mcp.py           # Strava API v3 — recent activities + OAuth2 refresh
data/
  program.json            # 8-week periodized program (parsed from Excel)
  current_week_plan.json  # Active weekly schedule
  training_log.ndjson     # Append-only session log (NDJSON)
  prs.json                # Personal records tracker
  preferences.json        # Weather thresholds, display settings
scripts/
  parse_excel.py          # Converts coach's Excel spreadsheet to program.json
  strava_auth.py          # One-time OAuth2 setup for Strava
tests/                    # Benchmark scenarios and summary
iterations/               # Development iteration logs + index
```

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI or VS Code extension)
- Python 3.12+
- A Strava account (optional — system works without it)

## Setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd Training_App
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS/Linux
   pip install fastmcp openpyxl
   ```

3. **Configure Strava (optional)**
   ```bash
   # Copy the template and fill in your Strava API credentials
   cp data/strava_config.template.json data/strava_config.json
   # Run the OAuth2 flow
   python scripts/strava_auth.py
   ```

4. **Parse the program (if starting from a new Excel file)**
   ```bash
   python scripts/parse_excel.py "references/Leg Drive.xlsx" 2026-02-02
   ```
   Windows shortcut (optional local helper):
   ```powershell
   .\scripts\parse_program.ps1 -File "references\Leg Drive.xlsx" -StartDate 2026-02-02
   ```

5. **Start Claude Code** — the `.mcp.json` file auto-registers both MCP servers.

## Usage

Open Claude Code in the project directory and use the skills:

```
/weekly-plan          # Plan your training week
/checkin              # Pre-session check-in
/log-session          # Log what you did after training
```

The system reads `CLAUDE.md` for all domain rules (session selection, stop rules, intensity adjustments) so the AI follows the same logic every time.

If `data/current_week_plan.json` is missing, `/checkin` does not auto-run `/weekly-plan`; it offers two options: run `/weekly-plan` now or use a one-off quick fallback for today.

## MCP Servers

| Server | API | Purpose |
|--------|-----|---------|
| `weather_mcp.py` | Open-Meteo (free, no key) | 7-day forecast — gates outdoor cardio suggestions |
| `strava_mcp.py` | Strava API v3 (OAuth2) | Recent activities — detects interference from hard cardio, flags unlogged gym sessions |

## Benchmarks

7 test scenarios with 109 individual tests, all passing. See [tests/benchmark_summary.md](tests/benchmark_summary.md) for full results.

| Category | Scenarios |
|----------|-----------|
| Happy path | Normal checkin + log session |
| Edge cases | Already trained, rest day, rest day override, skipped session detection |
| Ambiguous input | Vague soreness/energy values at decision thresholds |
| Baseline comparison | Raw Claude (25%) vs `/checkin` skill (100%) on same situation |

## Project Structure

```
Training_App/
  CLAUDE.md                          # Single source of truth for domain rules
  .claude/skills/
    checkin/SKILL.md                 # Pre-session check-in skill
    log-session/SKILL.md             # Post-session logging skill
    weekly-plan/SKILL.md             # Weekly planning skill
  .mcp.json                          # MCP server registration
  mcp_servers/
    weather_mcp.py                   # Weather forecast server
    strava_mcp.py                    # Strava activity server
  data/
    program.json                     # Periodized program
    current_week_plan.json           # Active week schedule
    training_log.ndjson              # Session log (append-only)
    prs.json                         # Personal records
    preferences.json                 # User preferences
    strava_config.template.json      # Strava credentials template
  scripts/
    parse_excel.py                   # Excel-to-JSON program parser
    strava_auth.py                   # Strava OAuth2 setup
  tests/
    benchmark_summary.md             # Aggregate results
    scenario_*.md                    # Individual test scenarios
    SCENARIO_TEMPLATE.md             # Template for new scenarios
  iterations/                        # Development logs + artifacts
    README.md                        # Iteration index
    artifacts/                       # Iteration screenshots/assets
  docs/                              # Project documentation
    README.md                        # Docs index
    tutorial.md                      # Full assignment narrative
    instructions.md                  # Short handoff/checklist
  references/                        # Source references/templates
    skill_schemas.md                 # Shared schemas + output templates
    programs/                        # Optional add-on program templates
```

## Orientation for New Contributors

If you are new to this repo, read in this order:

1. `README.md` (this file) for setup and architecture
2. `CLAUDE.md` for training rules and decision logic
3. `docs/README.md` for document navigation
4. `iterations/README.md` for change history navigation

`data/` should hold active runtime state, while `references/` holds source templates/examples.

## License

Academic project — MSIS 549B, AI & Machine Learning.
