# Workflow: Discussion Layer

This session handles architecture decisions, approach comparison, and plan refinement.

## Purpose

Before any code is written, decisions go here. The discussion layer compares alternatives, evaluates trade-offs, and produces `workflow_selected.md`.

## Input

- Feature requests or problem statements
- Existing code state
- Manual/documentation references

## Output

- `workflow_selected.md` — the approved plan ready for execution

## Rules

1. Do not write production code in this session
2. All proposals must list at least 2 alternatives with pros/cons
3. Decisions must reference specific manual sections when available
4. Output goes to `workflow_selected.md` for the execution layer to consume
