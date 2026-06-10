# CLAUDE.md

This file provides Claude Code guidance for working in this repository.

## Current Scope

This repository is a HyperMesh GUI-only MCP server. Claude Code should use the
repo-local MCP config `claude_code_mcp.json` to start `program.server` over
stdio, then control an already running HyperMesh GUI through the Tcl socket
listener.

In scope:

- Start and check the HyperMesh Tcl GUI listener.
- Execute validated Tcl through the listener.
- Query current model counts.
- Create verified FE HEX8 smoke-test meshes.
- Keep the HyperMesh 2024+ Python API bridge available as a separate optional
  framework.

Out of scope:

- LS-DYNA solver execution.
- LS-PrePost execution.
- HyperMesh hmbatch execution as an MCP tool.
- K-file export as a required MCP workflow.

## Required Python

Use the project conda interpreter for all commands in this repository:

```powershell
<python>
```

Do not use bare `python`, `pip`, or `pytest`.

## Claude Code MCP Config

Repo-local config:

```text
<repo>\claude_code_mcp.json
```

Expected server entry:

```json
{
  "mcpServers": {
    "hyper-dyna-mcp": {
      "command": "C:/path/to/conda/envs/hyper-dyna/python.exe",
      "args": ["-m", "program.server"],
      "cwd": "C:\\path\\to\\hyper-dyna-mcp",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\hyper-dyna-mcp"
      }
    }
  }
}
```

This file is a repo-local template/smoke config. Do not modify global Claude
Code settings unless the user explicitly asks.

## Smoke Test

Run a Claude-compatible stdio smoke test without requiring HyperMesh GUI:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json
```

If the HyperMesh Tcl listener is already sourced, include GUI connection check:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json --with-gui
```

After confirming the listener is connected, run the optional modeling smoke:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json --with-gui --modeling-smoke
```

This check only passes when `hm_gui_modeling_smoke.success=true` and the returned
`visual_counts` report both `elements > 0` and `solids > 0`.
If `hm_gui_modeling_smoke` returns `visual_counts_ok` or `visual_display_ok`,
Claude smoke uses those tool-reported gates before falling back to inference
from `visual_counts`, `visual_displayed_counts`, and `visibility`.
The output also includes `visual_displayed_counts` and `visibility`; use those
fields when entities exist but the HyperMesh GUI does not visibly show them.
When visibility data is available, Claude smoke requires FE elements and solids
to be displayed, not merely present.
On failure, inspect `modeling_smoke_failure.reason`; common values are
`gui_not_connected`, `tool_failed`, `visual_counts_missing`, and
`visual_counts_insufficient`, `visual_display_hidden`.
When GUI connection fails, `next_hypermesh_commands` lists the Tcl Console
commands to try next. The same smoke output also exposes parsed
`gui_connection`, `gui_diagnostics`, and `set_port_result` fields so Claude
does not need to parse the raw `checked_tools` strings.
Prefer top-level `gui_diagnosis.reason` and `.action` for recovery decisions
instead of parsing raw tool strings. It mirrors `gui_diagnostics.diagnosis`:
`listener_not_running` means source the generated listener,
`port_occupied_without_pong` means stop the stale listener or switch ports,
`listener_version_mismatch` means source the regenerated listener, and
`listener_ready` means proceed to modeling smoke.

## HyperMesh Tcl Listener

In the HyperMesh Tcl Console:

```tcl
set ::mcp_hm_port 47883
source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
```

Expected output:

```text
Dyna-mcp GUI listener ready on 127.0.0.1:47883
```

The generated listener is compatible with older HyperMesh Tcl runtimes around
2024. It avoids hard dependencies on newer Tcl `dict exists` behavior and uses
fallback channel enumeration.
`hmcustom.tcl` follows the same compatibility pattern for channel enumeration
and socket `fconfigure` calls.

If the default port is stuck, `hmcustom.tcl` provides:

```tcl
mcp_start_on_port 47884
```

It uses `runs/hm_gui_listener_47884.tcl` when that file exists.
`mcp_status` reports listener active only after receiving
`HYPERMESH_MCP_PONG`; a plain TCP connection without PONG is treated as an
occupied/non-responsive port.
`mcp_start_on_port` also verifies PONG after sourcing, so a successful source
message alone is not enough evidence that the MCP endpoint is ready.
Generated GUI listeners use nonblocking request reads so Tcl-side ping clients
do not have to half-close the socket before the listener can respond.
The expected generated listener version is `2024-compat-v3`; Claude smoke
reports this under `gui_diagnostics.expected_listener_version`.
Claude smoke also reports `gui_listener_version_ok`; it must be true before
modeling smoke is allowed to run.
`mcp_loop` clears stale `ipc/stop.flag` before starting, so a previous
`mcp_stop` does not immediately stop a new IPC loop.

## Architecture Boundaries

```text
program/server.py              FastMCP stdio server
program/tools/hm_gui.py        Tcl socket listener generation and socket client
program/tools/hm_model_writer.py verified FE mesh creation
program/tools/hm_command_map.py verified Tcl route map loader
program/tools/hm_python_api.py  separate HyperMesh 2024+ Python API framework
program/claude_smoke.py         Claude-compatible MCP stdio smoke test
runs/hm_gui_listener.tcl        generated Tcl listener
```

Do not merge the Tcl listener framework into the Python API framework. They are
separate channels:

- Tcl listener: controls the current visible GUI session through socket Tcl.
- Python API: launches or queries HyperMesh Python API scripts when explicitly
  requested.

## Current Tool Surface

Claude Code should expect these key tools:

```text
check_hypermesh_connection
diagnose_hypermesh_listener
set_hypermesh_listener_port
dyna_keyword_policy
dyna_keyword_map_validate
dyna_keyword_query
execute_hm_python_api
execute_tcl_gui
get_model_info
hm_auto_save
hm_command_map
hm_create_fe_cube
hm_gui_modeling_smoke
hm_create_solid_box
hm_python_api_current_model_info
hm_python_api_status
hm_visual_refresh
```

Tools that must not be exposed in the current HyperMesh GUI-only scope:

```text
execute_hmbatch
execute_lsprepost
generate_lsdyna_command
hm_export_k
parse_k_file
parse_solver_log
write_k_file
```

## Hard Rules

- Do not fabricate unverified HyperMesh Tcl commands.
- `hm_create_fe_cube` creates FE nodes/elements, not geometry solids.
- Geometry solid creation uses the source-verified `*solidblock` route and must
  confirm that solids_count increases in the target GUI session.
- Dyna manual embeddings are retrieval aids only; execution must use structured
  maps and verified command routes.
- `hm_set_keyword` is MAP-gated. A local Tcl template or dictionary hit is not
  enough to execute a Dyna keyword; `dyna_keyword_query.execution_ready` must be true
  before `hm_set_keyword` sends Tcl. Current unverified routes such as
  `SECTION_SOLID` must return `error_type=dyna_keyword_execution_not_verified`.
- Do not delete existing files; archive or edit in place.


