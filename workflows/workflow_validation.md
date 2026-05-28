# Workflow: Validation Layer

The validation layer checks correctness after execution.

## Validation Checklist

1. **Path checks:** All YAML paths resolve to existing files/directories
2. **Environment checks:** Conda environment, Python version, required packages
3. **Code checks:** pytest passes, no import errors
4. **K-file checks:** Sample .k files parse correctly, validation catches known errors
5. **Dry-run checks:** Solver commands are generated but not executed
6. **Log checks:** Obsidian logs are written correctly

## Output

- `reports/validation_report.md`
- Obsidian validation log entry

## Rules

1. Run `pytest` — all tests must pass
2. Verify no tool accidentally calls a real solver
3. Verify YAML paths load correctly
4. Report any TODOs that remain open
