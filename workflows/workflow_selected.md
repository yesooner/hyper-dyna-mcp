# Workflow: Selected Plan

Approved plans from the discussion layer land here.

## Current Plan

### Phase 1 — Project Skeleton + dry_run MCP

**Goal:** Private repo with CLAUDE.md, workflow, folder structure, dry_run MCP, K-file tests.

**Decisions:**
- HyperMesh automation: Tcl + hmbatch (first version)
- LS-DYNA: .k keyword file parsing/validation/generation
- LS-PrePost: cfile templates (placeholder)
- All execution tools default `dry_run=True`
- No hardcoded commercial software paths — all via `path/*.yaml`
- Conda environment: `dyna_mcp` with python 3.11

**Implementation order:**
1. Project structure (done)
2. Path YAML configs
3. K-file parser/validator/generator
4. LS-DYNA command generator (dry_run)
5. Obsidian logger
6. MCP server registration
7. Tests
8. Reports

## History

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-26 | Initial project creation | From Dyna-mcp/create.md plan |
