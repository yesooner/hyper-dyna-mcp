# Workflow: Execution Layer

The execution layer (Claude Code / Codex) reads this file and follows the plan from `workflow_selected.md`.

## Pre-flight Checklist

Before executing any task, read these files in order:

1. `CLAUDE.md`
2. `workflows/workflow_selected.md`
3. `path/local_paths.yaml`
4. `path/obsidian_paths.yaml`

## Task Execution Rules

1. Follow `workflow_selected.md` — do not deviate without going through the discussion layer
2. All paths come from `path/*.yaml` — never hardcode
3. All tools default `dry_run=True` unless explicitly overridden
4. After completing a task, update `reports/` with results
5. After completing a task, write to Obsidian execution log
6. Do not delete existing files
7. Uncertain HyperMesh commands go to TODO — do not fabricate

## Output

- Modified/created source files
- `reports/` with execution results
- Obsidian log entries via `program/tools/obsidian_logger.py`
