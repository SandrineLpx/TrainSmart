"""
Initialize local runtime state files from templates.

Usage:
  python scripts/init_local_state.py
  python scripts/init_local_state.py --with-strava
  python scripts/init_local_state.py --force
  python scripts/init_local_state.py --location "Kirkland, WA 98034" --latitude 47.6769 --longitude -122.206
  python scripts/init_local_state.py --program-start-date 2026-02-02 --training-days-per-week 3
  python scripts/init_local_state.py --pr "Snatch=57" --pr "Clean & Jerk=73"
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize local PR file from template and apply optional local overrides."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing local files with template values before applying overrides.",
    )
    parser.add_argument(
        "--with-strava",
        action="store_true",
        help="Also create data/strava_config.json from template if missing.",
    )

    parser.add_argument("--location", default=None, help="Set preferences.location")
    parser.add_argument(
        "--latitude",
        type=float,
        default=None,
        help="Set preferences.latitude",
    )
    parser.add_argument(
        "--longitude",
        type=float,
        default=None,
        help="Set preferences.longitude",
    )
    parser.add_argument(
        "--program-start-date",
        default=None,
        help="Set preferences.program_start_date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--training-days-per-week",
        type=int,
        default=None,
        help="Set preferences.training_days_per_week (0-5)",
    )
    parser.add_argument(
        "--competition-date",
        default=None,
        help="Set preferences.competition_date in YYYY-MM-DD format (or 'none')",
    )

    parser.add_argument(
        "--pr",
        action="append",
        default=[],
        help="Set a PR value in the form 'Exercise=WeightKg'. Repeat for multiple.",
    )
    return parser.parse_args()


def _copy_template(
    template_name: str,
    target_name: str,
    force: bool,
) -> str:
    template_path = DATA_DIR / template_name
    target_path = DATA_DIR / target_name

    if not template_path.exists():
        raise FileNotFoundError(f"Missing template file: {template_path}")

    existed = target_path.exists()
    if existed and not force:
        return "existing"

    target_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    return "reset" if existed else "created"


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _validate_iso_date(value: str, field_name: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}: '{value}' (expected YYYY-MM-DD)") from exc
    return value


def _apply_preferences_overrides(args: argparse.Namespace) -> bool:
    has_pref_args = any(
        value is not None
        for value in [
            args.location,
            args.latitude,
            args.longitude,
            args.program_start_date,
            args.training_days_per_week,
            args.competition_date,
        ]
    )
    if not has_pref_args:
        return False

    prefs_path = DATA_DIR / "preferences.json"
    if not prefs_path.exists():
        raise FileNotFoundError(
            "Missing data/preferences.json. This file is tracked for reproducibility."
        )
    prefs = _load_json(prefs_path)
    changed = False

    if args.location is not None:
        prefs["location"] = args.location
        changed = True
    if args.latitude is not None:
        prefs["latitude"] = args.latitude
        changed = True
    if args.longitude is not None:
        prefs["longitude"] = args.longitude
        changed = True
    if args.program_start_date is not None:
        prefs["program_start_date"] = _validate_iso_date(
            args.program_start_date, "program_start_date"
        )
        changed = True
    if args.training_days_per_week is not None:
        if args.training_days_per_week < 0 or args.training_days_per_week > 5:
            raise ValueError("training_days_per_week must be between 0 and 5")
        prefs["training_days_per_week"] = args.training_days_per_week
        changed = True
    if args.competition_date is not None:
        if args.competition_date.lower() == "none":
            prefs["competition_date"] = None
        else:
            prefs["competition_date"] = _validate_iso_date(
                args.competition_date, "competition_date"
            )
        changed = True

    if changed:
        _save_json(prefs_path, prefs)
    return changed


def _parse_pr_args(pr_args: list[str]) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for item in pr_args:
        if "=" not in item:
            raise ValueError(f"Invalid --pr value '{item}'. Use Exercise=WeightKg")
        exercise, weight_str = item.split("=", 1)
        exercise = exercise.strip()
        if not exercise:
            raise ValueError(f"Invalid --pr value '{item}'. Exercise name is empty.")
        try:
            weight_kg = float(weight_str.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid PR weight in '{item}'.") from exc
        if weight_kg < 0:
            raise ValueError(f"Invalid PR weight in '{item}'. Must be >= 0.")
        parsed[exercise.casefold()] = weight_kg
    return parsed


def _apply_pr_overrides(pr_args: list[str]) -> bool:
    if not pr_args:
        return False

    prs_path = DATA_DIR / "prs.json"
    prs_data = _load_json(prs_path)
    updates = _parse_pr_args(pr_args)
    records = prs_data.get("records", [])
    if not isinstance(records, list):
        raise ValueError("Invalid data/prs.json format. Expected a 'records' list.")

    by_exercise: dict[str, dict[str, Any]] = {}
    for record in records:
        name = str(record.get("exercise", "")).strip()
        if name:
            by_exercise[name.casefold()] = record

    missing = [name for name in updates if name not in by_exercise]
    if missing:
        available = ", ".join(sorted(record["exercise"] for record in records if "exercise" in record))
        missing_names = ", ".join(missing)
        raise ValueError(
            f"Unknown PR exercise(s): {missing_names}. Available: {available}"
        )

    for exercise_key, value in updates.items():
        record = by_exercise[exercise_key]
        rounded = round(value * 2) / 2
        record["weight_kg"] = int(rounded) if float(rounded).is_integer() else rounded
        if record.get("notes") in (None, "", "set_your_pr"):
            record["notes"] = "seeded"

    _save_json(prs_path, prs_data)
    return True


def main() -> int:
    args = _parse_args()

    status: dict[str, str] = {}
    status["prs.json"] = _copy_template("prs.template.json", "prs.json", args.force)
    if args.with_strava:
        status["strava_config.json"] = _copy_template(
            "strava_config.template.json", "strava_config.json", args.force
        )

    prefs_changed = _apply_preferences_overrides(args)
    prs_changed = _apply_pr_overrides(args.pr)

    print("Local state initialization complete.")
    for filename, file_status in status.items():
        print(f"- {filename}: {file_status}")
    if prefs_changed:
        print("- preferences.json: updated from CLI overrides")
    if prs_changed:
        print("- prs.json: updated from CLI --pr values")

    print("\nNext:")
    print("1. Review data/preferences.json and data/prs.json.")
    print("2. Run /weekly-plan to generate the current week schedule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
