# Claude Code Smoke Test

This repository includes `claude_code_mcp.json` for Claude Code MCP registration.

## Current Config

```json
{
  "command": "C:/path/to/conda/envs/hyper-dyna/python.exe",
  "args": ["-m", "program.server"],
  "cwd": "F:\\hyper-dyna-mcp"
}
```

The config was audited with the MCP stdio client and exposes the current HyperMesh-only tool surface, including:

```text
hm_command_map
dyna_keyword_policy
dyna_keyword_map_validate
dyna_keyword_query
hm_create_fe_cube
hm_create_solid_box
hm_visual_refresh
hm_gui_modeling_smoke
check_hypermesh_connection
diagnose_hypermesh_listener
set_hypermesh_listener_port
hm_auto_save
```

## HyperMesh Prerequisite

Default listener startup in HyperMesh Tcl Console:

```tcl
set ::mcp_hm_port 47883
source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
```

Expected:

```text
Dyna-mcp GUI listener ready on 127.0.0.1:47883
```

If the default port is occupied, stale, or does not return
`HYPERMESH_MCP_PONG`, prefer the fixed recovery port used by the repo-local
Claude smoke:

```tcl
catch {mcp_stop}
if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} else {source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}
```

Use `mcp_status` to distinguish a real MCP listener from a merely occupied TCP
port. Active means the listener returned `HYPERMESH_MCP_PONG`.
`mcp_start_on_port` also verifies PONG after sourcing and reports failure if the
listener file sourced but the MCP endpoint did not respond.

## Tool Smoke Test

1. List tools and confirm the repo-local allowed surface has `expected_tool_count=32`, `unexpected_tools=[]`, and no forbidden solver/export tools such as `hm_export_k`, `execute_hmbatch`, `generate_lsdyna_command`, or `parse_k_file`.
2. Confirm `hm_command_map`, `dyna_keyword_policy`, `dyna_keyword_map_validate`, `dyna_keyword_query`, `hm_create_fe_cube`, `hm_create_solid_box`, `hm_visual_refresh`, `hm_gui_modeling_smoke`, `hm_python_api_status`, `execute_hm_python_api`, and `hm_python_api_current_model_info` are available.
3. Call `dyna_keyword_policy` and confirm `embedding_execution_allowed=false`.
4. Call `dyna_keyword_map_validate` and confirm `success=true`, `embedding_execution_allowed=false`, and `errors=[]`.
5. Call `dyna_keyword_query` with `keyword=MAT_3` and confirm it returns `cardimage=MATL3`, `candidate_confidence=cardimage_direct_datanames_unverified`, `execution_ready=false`, `execution_decision.state=blocked`, `execution_decision.advisory_candidates_are_executable=false`, `advisory_only.execution_allowed=false`, and `field_execution_status.E.executable=false`.
6. Call `dyna_keyword_query` with `keyword=SECTION_SOLID` and confirm `execution_ready=false`, `execution_decision.state=blocked`, and `field_execution_status.SECID.executable=false`.
7. Call `dyna_keyword_query` with a near miss such as `LOAD_BLAS` and confirm `known=false`, `execution_ready=false`, and every returned suggestion has `execution_allowed=false`.
8. Call `hm_set_keyword` only for routes where `dyna_keyword_query.execution_ready=true`. For current unverified routes such as `SECTION_SOLID`, expect `error_type=dyna_keyword_execution_not_verified`.
9. Call `hm_command_map` with `route_name=create_structured_hex8_box`.
10. Call `check_hypermesh_connection`.
11. Call `get_model_info`.
12. Call `hm_create_fe_cube` with a small test cube and inspect its `visual_counts`, `visual_displayed_counts`, `visual_count_methods`, `visual_display_count_methods`, and `visibility`.
13. Call `hm_visual_refresh` and inspect `visual_counts`, `visual_displayed_counts`, `visual_count_methods`, `visual_display_count_methods`, `visibility`, `visual_steps`, `visual_refresh_ok`, `visual_refresh_reason`, and `visual_failed_steps`.
14. Call `hm_create_solid_box` with a small test box and confirm `created_count > 0`, `solid_count_methods`, plus `visibility.solids=displayed` in a connected GUI session.
15. Optionally call `hm_gui_modeling_smoke` to run FE, solid, and visualization stages in one tool call.
15. Call `hm_auto_save` and confirm the returned `.hm` file exists.

The repo-local `program.claude_smoke --with-gui --modeling-smoke` command uses
the same gate: `visual_counts.elements > 0` and `visual_counts.solids > 0` are
required for success. When `visual_displayed_counts` or `visibility` are
available, FE elements and solids must also be displayed; hidden entities fail
with `visual_display_hidden`. If `hm_gui_modeling_smoke` returns
`visual_counts_ok` or `visual_display_ok`, Claude smoke uses those tool-reported
gate fields before falling back to count/display inference.
Claude smoke also lifts `modeling_visual_refresh` to the top level. Use it to
inspect non-blocking display/view command failures when FE and solid entity
counts are otherwise present. In HyperMesh 2024 or older sessions,
`visual_refresh_reason=visual_step_warnings` means one optional display probe
failed, while the hard gate still comes from entity counts and displayed counts.
Claude smoke also lifts `modeling_visual_count_methods` and
`modeling_visual_display_count_methods` to the top level. Use these fields to
distinguish direct `hm_entitylist` counts from old-version `hm_marklength`
fallback counts when checking HyperMesh 2024 or older sessions.
On a successful connected smoke, inspect
`modeling_runtime_validation_evidence`. It is the structured evidence that can
justify changing `create_geometry_solid_box` from
`source_verified_runtime_pending` to runtime validated in the command map.
The nested `command_map_update_candidate` field names the route and map file;
apply it only after reviewing the connected GUI evidence. The actual map edit
should set `tested_in_session=true`, while `runtime_validated` and
`verification_level` remain derived by the command-map loader.

If it fails, inspect `modeling_smoke_failure.reason`:

```text
gui_not_connected
tool_not_run
tool_failed
listener_version_mismatch
visual_counts_missing
visual_counts_insufficient
visual_display_hidden
```

When the listener is not connected, the smoke JSON also includes
`gui_connection`, `gui_diagnostics`, and `next_hypermesh_commands`; execute
those commands in the HyperMesh Tcl Console before retrying. The same JSON
includes `retry_smoke_command`, which is the PowerShell command to run after
the Tcl Console commands have been executed.
Use top-level `gui_diagnosis.reason` and `.action` for stable recovery
classification; it mirrors `gui_diagnostics.diagnosis`. Expected reasons include `listener_not_running`,
`port_occupied_without_pong`, `listener_version_mismatch`, and
`listener_ready`.
If `gui_diagnosis.reason=port_occupied_without_pong`, inspect
`gui_diagnostics.port_owner_summary` and report the process/PID occupying the
listener port before switching ports or retrying.
When the listener is connected, `gui_listener_version_ok` must be true and
`gui_listener_version.current` must match `gui_listener_version.expected`.
The connected smoke JSON also exposes `gui_listener_runtime`, including
`listener_version`, `expected_listener_version`, `tcl_version`, and
`tcl_patchlevel`, so older HyperMesh Tcl runtime differences are visible in
Claude/Codex logs.

To print only those Tcl Console commands:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json --with-gui --port 47884 --modeling-smoke --commands-only
```

When `--port` is supplied, this command prints only the fixed-port recovery
steps and does not generate an alternate-port listener file. Fixed-port output
uses `mcp_start_on_port <port>` and does not append a second direct `source`
command, because `mcp_start_on_port` already sources and verifies the listener.
If `hmcustom.tcl` has not been loaded and `mcp_start_on_port` is unavailable,
the same Tcl line falls back to directly sourcing the fixed-port listener.
It intentionally does not print the PowerShell retry command, because the output
is meant to be pasted directly into the HyperMesh Tcl Console.

## Expected Results

```text
dyna_keyword_policy.embedding_execution_allowed = false
dyna_keyword_map_validate.success = true
dyna_keyword_map_validate.errors = []
dyna_keyword_query.execution_policy = structured_map_only
dyna_keyword_query.cardimage = MATL3
dyna_keyword_query.execution_ready = false
dyna_keyword_query.execution_decision.state = blocked
dyna_keyword_query.execution_decision.advisory_candidates_are_executable = false
dyna_keyword_query.advisory_only.execution_allowed = false
dyna_keyword_query.field_execution_status.E.executable = false
dyna_unknown_suggestion_query.known = false
dyna_unknown_suggestion_query.suggestions[*].execution_allowed = false
dyna_section_solid_keyword_query.execution_ready = false
dyna_section_solid_keyword_query.field_execution_status.SECID.executable = false
hm_set_keyword(SECTION_SOLID).error_type = dyna_keyword_execution_not_verified
checked_tools.hm_set_keyword_section_solid_blocked contains the blocked response
hm_command_map.route.status = verified
check_hypermesh_connection.connected = true
gui_listener_runtime.tcl_version is not empty
gui_listener_runtime.tcl_patchlevel is not empty
hm_create_fe_cube.success = true
hm_create_solid_box.created_count > 0
hm_gui_modeling_smoke.success = true
hm_gui_modeling_smoke.visual_counts.elements > 0
hm_gui_modeling_smoke.visual_counts.solids > 0
hm_gui_modeling_smoke.visual_count_methods.solids in {entitylist, marklength}
hm_gui_modeling_smoke.visual_display_count_methods.solids = marklength_displayed
hm_gui_modeling_smoke.visibility.elements = displayed
hm_gui_modeling_smoke.visibility.solids = displayed
modeling_runtime_validation_evidence.runtime_validated = true
hm_auto_save.success = true
```




