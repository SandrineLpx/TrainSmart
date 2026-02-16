# Codex Repo Instructions (Train Smart)

Before editing:
1) Read `README.md` and `CLAUDE.md`.
2) For skill changes, read only the relevant `.claude/skills/<skill>/SKILL.md`.
3) Treat `CLAUDE.md` as canonical policy/rules; avoid duplicating thresholds in skill files.
4) Keep output/template changes in `references/skill_schemas.md`.

Validation:
- rg "RULE-" CLAUDE.md .claude/skills references/skill_schemas.md
- git diff --check

Repo focus:
- Skills orchestrate workflow.
- `CLAUDE.md` defines domain decisions.
- Data files under `data/` are runtime state.
