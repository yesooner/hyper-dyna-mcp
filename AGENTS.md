# AGENTS.md

This file provides repository-local guidance for Codex when working in this repository.

## Project Overview

This repository is currently a HyperMesh GUI-only MCP server. The MCP server controls a running HyperMesh GUI through a Tcl socket listener and a file IPC fallback.

Current scope:

- Start and check the HyperMesh GUI listener.
- Execute validated Tcl in HyperMesh GUI.
- Query current model state.
- Create FE nodes/elements for smoke-test models.
- Save `.hm` files and verify they exist.
- Keep keyword helper tools available for HyperMesh card/template work.

Out of current scope:

- LS-DYNA solver execution.
- LS-PrePost execution.
- HyperMesh hmbatch execution.
- K-file export as an MCP tool.
- Solver-deck automation as a required workflow.

## Hard Rules

- Use the project conda interpreter for Python, pytest, MCP server, and helper commands.
- Do not use bare `python`, `pip`, or `pytest`.
- Do not fabricate unverified HyperMesh Tcl commands. If uncertain, mark TODO or test against HyperMesh first.
- Do not delete existing files. Edit in place or create new versions.
- Do not expose secrets, private env files, proxy values, or credentials.
- Keep runtime paths in `path/*.yaml` or environment variables.
- Default listener port is `47883`. When a previous listener or stale socket
  occupies that port, use the fixed smoke-test recovery port `47884` and the
  `mcp_start_on_port` flow documented below.

## Build And Run

Run MCP server:

```powershell
<python> -m program.server
```

Run tests:

```powershell
<python> -m pytest
```

Prefer UTF-8 mode for commands that may print Chinese:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
<python> -B -X utf8 -m pytest
```

## HyperMesh Listener

In HyperMesh Tcl Console:

```tcl
set ::mcp_hm_port 47883
source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
```

Expected:

```text
Dyna-mcp GUI listener ready on 127.0.0.1:47883
```

If the default port is occupied or does not return `HYPERMESH_MCP_PONG`, use
the fixed recovery command printed by Claude smoke:

```tcl
catch {mcp_stop}
if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} else {source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}
```

A listener is usable only after `check_hypermesh_connection` or `mcp_status`
receives `HYPERMESH_MCP_PONG` with the expected listener version.

## Architecture

```text
program/server.py                 MCP server entry
program/tools/hm_gui.py           GUI socket client, listener generation, Tcl validation
program/tools/hm_python_api.py    optional HyperMesh Python API bridge
program/tools/hm_model_writer.py  FE node/element creation
program/tools/hm_command_map.py   verified HyperMesh Tcl command route map
program/tools/dyna_keyword_map.py structured Dyna keyword/manual policy
program/tools/hm_safe_save.py     HyperMesh model save with file existence check
program/plugin_loop.py            IPC command loop
program/transport_manager.py      socket/IPC fallback state
runs/hm_gui_listener.tcl          generated HyperMesh listener
hmcustom.tcl                      HyperMesh helper script/menu
path/hypermesh_paths.yaml         HyperMesh config
```

## Current MCP Tool Surface

Expected exposed tools:

```text
ping
check_environment
load_path_config
validate_path
start_hypermesh_gui_listener
check_hypermesh_connection
diagnose_hypermesh_listener
set_hypermesh_listener_port
get_model_info
execute_tcl_gui
hm_python_api_status
execute_hm_python_api
hm_python_api_current_model_info
hm_auto_save
hm_check_model
hm_read_materials
hm_read_components
hm_convert_model
hm_set_keyword
hm_keyword_help
hm_create_box
hm_mesh_box
hm_create_fe_cube
hm_create_solid_box
hm_visual_refresh
hm_gui_modeling_smoke
hm_search_keywords
hm_keyword_map
hm_command_map
dyna_keyword_policy
dyna_keyword_map_validate
dyna_keyword_query
```

Tools that must not be exposed in current scope:

```text
hm_export_k
parse_k_file
write_k_file
generate_lsdyna_command
parse_solver_log
execute_lsprepost
execute_hmbatch
```

## Modeling Notes

`hm_create_fe_cube` creates FE nodes and HEX8 elements. It does not create CAD/geometry solids.

Verified HyperMesh Tcl route:

```text
*createnode
*createlist nodes
*createelement 208
```

To see created cubes in the GUI, enable element display and fit/zoom extents.

`hm_create_solid_box` creates geometry solid boxes through the source-verified
`*solidblock` route. It must validate success by checking that `solids_count`
increases in the connected HyperMesh GUI session.

`hm_gui_modeling_smoke` is the preferred connected-GUI end-to-end check after
the listener responds. It creates one FE cube, one geometry solid box, and then
requests a GUI visualization refresh. Inspect `visual_counts`,
`visual_displayed_counts`, `visibility`, and `visual_steps` to distinguish
hidden display state from failed entity creation or failed display/view Tcl
commands.

Created HyperMesh component names should not contain `MCP` or `mcp`; model writer strips those markers.

High-level modeling helpers must use `templates/hm_command_map.json` for verified HyperMesh Tcl routes. Do not grep the Altair install tree during normal tool execution, and do not introduce unverified route commands into modeling helpers.

Dyna manual distillation and embeddings are retrieval aids only. Execution must resolve through structured keyword/cardimage/dataname maps and verified HyperMesh command routes. `dyna_keyword_map_validate` must stay clean before any Dyna keyword MAP is used for execution planning.

`hm_set_keyword` is MAP-gated. A local Tcl template or dictionary hit is not enough to execute a Dyna keyword; `dyna_keyword_query.execution_ready` must be true first. Current unverified routes such as `SECTION_SOLID` must return `error_type=dyna_keyword_execution_not_verified` instead of sending Tcl to HyperMesh.

## Handoff Convention

When the user asks for handoff, summarize in Chinese and save the summary under `logs/handoff/` using a timestamped Markdown file.



