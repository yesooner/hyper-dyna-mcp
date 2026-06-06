# Hyper-Dyna-MCP

MCP server for LS-DYNA pre-processing automation via HyperMesh GUI.

## Features

- **1935 LS-DYNA keyword templates** — MAT, SECTION, CONTACT, BOUNDARY, LOAD, CONTROL, DATABASE, SET, etc.
- **HyperMesh GUI integration** — Socket communication (port 47882) with IPC fallback
- **K file parser/writer** — Parse, validate, generate LS-DYNA .k files
- **Model operations** — Read/write materials, properties, components, sections
- **Safety** — Tcl script policy enforcement, MCP_SCRIPT markers, command-by-command execution
- **Workflow orchestration** — LS-DYNA, HyperMesh, and mixed pipelines

## Quick Start

```bash
# 1. Start HyperMesh GUI
# 2. In HyperMesh Tcl console:
source F:/hyper-dyna-mcp/hmcustom.tcl
mcp_start

# 3. Start MCP server
E:/anaconda3/anzhuang/envs/hyper-dyna/python.exe -m program.server
```

## MCP Tools (19)

| Tool | Description |
|------|-------------|
| `hm_set_keyword` | Set LS-DYNA keyword (MAT, SECTION, CONTACT, etc.) |
| `hm_keyword_help` | Get keyword help from manual |
| `hm_check_model` | Query current model state |
| `hm_convert_model` | Convert model to LS-DYNA format |
| `hm_read_materials` | Read all materials |
| `hm_read_components` | Read all components |
| `execute_tcl_gui` | Execute Tcl in HyperMesh GUI |
| `execute_hmbatch` | Execute via hmbatch.exe |
| `generate_tcl_script` | Generate Tcl script |
| `check_hypermesh_connection` | Check hmbatch.exe |
| `parse_k_file` | Parse .k file |
| `write_k_file` | Generate .k file |
| `generate_lsdyna_command` | Generate solver command |
| `parse_solver_log` | Parse solver log |
| `execute_lsprepost` | Execute LS-PrePost cfile |
| `generate_cfile` | Generate cfile script |
| `generate_post_processing_cfile` | Generate post-processing cfile |
| `check_environment` | Check Python/conda/packages |
| `load_path_config` | Load YAML config |
| `validate_path` | Check path exists |
| `write_obsidian_log` | Write to Obsidian vault |

## Architecture

```
Agent (Claude Code)
  ↓ MCP protocol
MCP Server (Python)
  ↓ Socket (port 47882) / IPC (file queue)
HyperMesh GUI (Tcl listener)
  ↓ *setvalue / *createentity
LS-DYNA card images
```

## Project Structure

```
hyper-dyna-mcp/
├── program/              # MCP server + tools
│   ├── server.py         # MCP entry point (19 tools)
│   ├── transport_manager.py  # Socket/IPC fallback
│   ├── plugin_loop.py    # IPC command dispatcher
│   └── tools/            # 24 tool modules
├── templates/keyword/    # 1935 Tcl templates
├── ref/                  # LS-DYNA keyword reference (901 keywords)
├── lsdyna-maunal/        # LS-DYNA R13 manuals (3 volumes)
├── path/                 # YAML configs
├── tests/                # 132 tests
├── output/               # Generated models
└── hmcustom.tcl          # HyperMesh auto-load commands
```

## Environment

- Python: 3.13.5 (hyper-dyna conda env)
- HyperMesh: 2021
- LS-PrePost: 4.8
- LS-DYNA: R13.1
