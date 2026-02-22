---
name: onboard
description: Initialize local onboarding data for a new user. Creates local PR/Strava files from templates and optionally customizes tracked preferences/PRs.
---

# New User Onboarding

Initialize local state files so a new user can start planning and logging sessions.

## Inputs

- Optional user preferences: location, coordinates, start date, training days, competition date
- Optional PR values for tracked exercises

## Outputs

- Local data files created from templates:
  - `data/prs.json`
  - Optional: `data/strava_config.json`
- Optional updates applied to tracked `data/preferences.json`
- Confirmation summary formatted per `references/skill_schemas.md`

## Workflow

### Step 1: Ask setup choices

Ask all at once:

1. Initialize local data files now? (yes/no)
2. Also create Strava config template now? (yes/no)
3. Do you want to set key values now? (yes/no)

If answer to (1) is no, stop.

### Step 2: Initialize files via script

Run:

```bash
python scripts/init_local_state.py
```

If Strava setup is requested, run:

```bash
python scripts/init_local_state.py --with-strava
```

The script is idempotent. It creates missing template-based files and leaves existing files unchanged unless `--force` is used.

### Step 3: Optional personalization

If the user wants key values set now, ask for:

- `location`
- `latitude`, `longitude`
- `program_start_date` (`YYYY-MM-DD`)
- `training_days_per_week` (0-5)
- `competition_date` (`YYYY-MM-DD` or `none`)
- Optional PR updates as `Exercise=WeightKg` pairs

Apply updates with one command (include only provided flags):

```bash
python scripts/init_local_state.py --location "<...>" --latitude <...> --longitude <...> --program-start-date <...> --training-days-per-week <...> --competition-date <...> --pr "Snatch=57" --pr "Clean & Jerk=73"
```

### Step 4: Output

Format response per `/onboard` template in `references/skill_schemas.md`.

## Failure Modes and Fallbacks

- Missing template files: report which template is missing and stop.
- Missing `data/preferences.json`: report it and stop if preference override flags are provided.
- Invalid date/PR format: show the specific invalid input and request correction.
- Existing files already present: keep them unless user explicitly requests reset with `--force`.

## Constraints

- Do not delete user local files.
- Do not overwrite existing local files unless user asks for `--force`.
- Keep file paths under `data/` exactly as defined in CLAUDE.md.
