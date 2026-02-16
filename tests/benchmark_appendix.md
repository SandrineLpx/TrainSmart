# Benchmark Appendix — Scenarios, Outputs, Scores

This appendix links each scenario file (with full inputs and actual system output blocks) and summarizes scoring.  
Outputs are included inside each `tests/scenario_*.md` file as required.

## Scenario Index

| # | Scenario File | Type | Skill | Tests | Score | Notes |
|---|---------------|------|-------|-------|-------|-------|
| 1 | `tests/scenario_1_checkin_normal.md` | Happy path | /checkin + /log-session | 17 | 34/34 | Included in `tests/benchmark_summary.md` |
| 2 | `tests/scenario_2_checkin_already_done.md` | Edge case | /checkin | 8 | 16/16 | Included in `tests/benchmark_summary.md` |
| 3.1 | `tests/scenario_3.1_checkin_rest_day.md` | Edge case | /checkin | 11 | 22/22 | Included in `tests/benchmark_summary.md` |
| 3.2 | `tests/scenario_3.2_checkin_rest_day_override.md` | Edge case | /checkin | 32 | 64/64 | Included in `tests/benchmark_summary.md` |
| 4 | `tests/scenario_4_ambiguous_input.md` | Ambiguous | /checkin | 16 | 32/32 | Included in `tests/benchmark_summary.md` |
| 5 | `tests/scenario_5_baseline_comparison.md` | Baseline | /checkin vs raw Claude | 11 | 22/22 vs 5.5/22 | Included in `tests/benchmark_summary.md` |
| 6 | `tests/scenario_6_skipped_session.md` | Edge case | /checkin | 14 | 28/28 | Included in `tests/benchmark_summary.md` |
| 7 | `tests/scenario_7_checkin_trained_yesterday.md` | Edge case | /checkin | TBD | TBD | Not yet added to `tests/benchmark_summary.md` |

## Notes

- `tests/benchmark_summary.md` covers Scenarios 1–6 only.
- Scenario 7 was added after the benchmark summary and needs scoring to be added there if you want aggregate totals updated.
