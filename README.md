# Dyna-mcp

MCP server for CAE workflow automation: HyperMesh pre-processing, LS-DYNA .k file generation/validation, LS-DYNA solver dry-run, LS-PrePost post-processing, and Obsidian logging.

## First Phase (current)

- Path management via YAML config
- Environment checking (conda, commercial software paths)
- LS-DYNA .k file parsing, validation, and generation
- LS-DYNA solver command generation (dry_run only)
- Obsidian execution log backflow
- All execution tools default to `dry_run=True`

## Environment Setup

```powershell
conda create -n dyna_mcp python=3.11 -y
conda activate dyna_mcp
pip install -e ".[dev]"
```

## Project Structure

```
Dyna-mcp/
├── CLAUDE.md          # Execution rules for AI sessions
├── workflows/         # Workflow layer definitions
├── program/           # MCP server and tools
│   ├── server.py
│   ├── tools/         # Individual tool modules
│   └── prompts/       # Planner/executor/validator prompts
├── lib/               # Samples, templates, manuals
├── path/              # YAML path configurations
├── tests/             # pytest test suite
├── reports/           # Generated reports
└── runs/              # Solver run directories
```
