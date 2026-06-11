# Hyper-Dyna-MCP API Reference

Current API scope: HyperMesh GUI listener tools only.

## Connection Tools

### `ping`

Returns MCP server health.

### `start_hypermesh_gui_listener`

Generates `runs/hm_gui_listener.tcl`.

Input:

```json
{"params": {"port": 47883}}
```

Expected output includes:

```json
{
  "listener_tcl": "runs/hm_gui_listener.tcl",
  "host": "127.0.0.1",
  "port": 47883,
  "listener_version": "2024-compat-v3",
  "source_command": "source \"<repo-root>/runs/hm_gui_listener.tcl\"",
  "start_or_source_command": "if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47883} else {source \"<repo-root>/runs/hm_gui_listener.tcl\"}",
  "next_hypermesh_commands": [
    "catch {mcp_stop}",
    "if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47883} else {source \"<repo-root>/runs/hm_gui_listener.tcl\"}"
  ]
}
```

Use `start_or_source_command` instead of a bare `source` when `hmcustom.tcl`
may already be loaded, because `mcp_start_on_port` verifies listener PONG after
sourcing.

### `check_hypermesh_connection`

Sends a listener ping to HyperMesh.

Expected output includes:

```json
{
  "connected": true,
  "host": "127.0.0.1",
  "port": 47883,
  "listener_version": "2024-compat-v3",
  "tcl_version": "8.6",
  "tcl_patchlevel": "8.6.13",
  "response": "OK\nHYPERMESH_MCP_PONG\n"
}
```

`tcl_version` and `tcl_patchlevel` are reported by the Tcl runtime inside the
connected HyperMesh process. Use them when diagnosing behavior differences
between HyperMesh 2024 and older bundled Tcl builds.

## Model Query Tools

### `get_model_info`

Returns current model counts from HyperMesh GUI:

```json
{
  "connected": true,
  "comps_count": 5,
  "nodes_count": 122,
  "elems_count": 25,
  "mats_count": 4,
  "props_count": 2,
  "groups_count": 0
}
```

### `hm_check_model`

Checks model state through HyperMesh Tcl.

### `hm_read_materials`

Reads materials with pagination.

### `hm_read_components`

Reads components with pagination.

## Execution Tools

### `execute_tcl_gui`

Executes Tcl in the running HyperMesh GUI listener.

Input:

```json
{
  "params": {
    "script": "*createmark nodes 1 \"all\"",
    "timeout": 120,
    "mode": "safe"
  }
}
```

Modes:

```text
safe  whitelist and dictionary validation
raw   skips whitelist/dictionary checks, but still blocks destructive commands
```

Unknown Tcl commands and listener-side errors return `success=false`.

### `hm_python_api_status`

Checks whether the optional HyperMesh Python API bridge is available.

### `execute_hm_python_api`

Tool title: `Plan HyperMesh Python API Script`.

Generates a constrained HyperMesh Python API script and launch command for review with `dry_run=true`. Real external launch is outside the current GUI-only MCP scope: `dry_run=false` must return `success=false`, `executed=false`, and `error_type=hypermesh_python_api_launch_out_of_scope`.

## FE Creation Tools

### `hm_create_box`

Creates a one-element HEX8 FE box. This creates FE nodes/elements, not geometry solids.
The input accepts `timeout` so older HyperMesh GUI sessions can be given more
time to respond. Degenerate dimensions are rejected at the MCP schema layer:
`x_min < x_max`, `y_min < y_max`, and `z_min < z_max` are required.

```json
{
  "params": {
    "name": "fe_box",
    "x_min": 0,
    "y_min": 0,
    "z_min": 0,
    "x_max": 10,
    "y_max": 10,
    "z_max": 10,
    "comp_name": "fe_box",
    "timeout": 45
  }
}
```

### `hm_create_fe_cube`

Creates a structured HEX8 FE cube.

Input:

```json
{
  "params": {
    "name": "soil_cube",
    "size": 10.0,
    "element_size": 5.0,
    "origin_x": 0.0,
    "origin_y": 0.0,
    "origin_z": 0.0,
    "comp_name": "soil_cube",
    "timeout": 60
  }
}
```

Output includes:

```json
{
  "success": true,
  "stage": "complete",
  "component": "soil_cube",
  "node_count": 27,
  "element_count": 8,
  "first_element_id": 18,
  "last_element_id": 25,
  "visual_counts": {
    "elements": 8,
    "nodes": 27,
    "solids": 0,
    "surfaces": 0
  },
  "visual_displayed_counts": {
    "elements": 8,
    "nodes": 27,
    "solids": 0,
    "surfaces": 0
  },
  "visual_count_methods": {
    "elements": "entitylist",
    "nodes": "entitylist",
    "solids": "entitylist",
    "surfaces": "entitylist"
  },
  "visual_display_count_methods": {
    "elements": "marklength_displayed",
    "nodes": "marklength_displayed",
    "solids": "marklength_displayed",
    "surfaces": "marklength_displayed"
  },
  "visibility": {
    "elements": "displayed",
    "solids": "absent"
  }
}
```

Component names created in HyperMesh strip `MCP/mcp` markers.

### `hm_create_solid_box`

Geometry solid creation is a separate route from FE mesh creation. The tool
uses the verified `create_geometry_solid_box` / `*solidblock` route and creates
HyperMesh geometry solids only, not HEX/TET FE mesh entities.

The input uses the same coordinate fields as `hm_create_box` and also accepts
`timeout` for slow connected GUI sessions.

```json
{
  "success": true,
  "supported": true,
  "route_name": "create_geometry_solid_box",
  "solid_id": 4,
  "created_count": 1
}
```

Runtime evidence for this route should prove that `solids_count` increases and
that the created solid is visible in the connected GUI. Those checks are part
of connected GUI smoke.

### `hm_visual_refresh`

Attempts to redraw and fit visible FE/solid entities in the current HyperMesh
GUI. The underlying Tcl commands are wrapped in `catch` for older HyperMesh
compatibility.

Output includes `visual_counts`, `visual_displayed_counts`,
`visual_count_methods`, `visual_display_count_methods`, `visibility`,
`visual_steps`, and a non-blocking `visual_refresh_ok` summary when the
connected listener can query entity lists. `visual_steps` records per-command
display/viewfit/redraw Tcl diagnostics so older HyperMesh display failures can
be isolated:

```json
{
  "success": true,
  "visual_counts": {
    "elements": 8,
    "nodes": 27,
    "solids": 1,
    "surfaces": 6
  },
  "visual_displayed_counts": {
    "elements": 8,
    "nodes": 27,
    "solids": 1,
    "surfaces": 6
  },
  "visual_count_methods": {
    "elements": "entitylist",
    "nodes": "entitylist",
    "solids": "marklength",
    "surfaces": "marklength"
  },
  "visual_display_count_methods": {
    "elements": "marklength_displayed",
    "nodes": "marklength_displayed",
    "solids": "marklength_displayed",
    "surfaces": "marklength_displayed"
  },
  "visibility": {
    "elements": "displayed",
    "nodes": "displayed",
    "solids": "displayed",
    "surfaces": "displayed"
  },
  "visual_steps": {
    "hm_viewfit": {"status": "ok", "error": null},
    "hm_redraw": {"status": "ok", "error": null}
  },
  "visual_refresh_ok": true,
  "visual_refresh_reason": "all_visual_steps_ok",
  "visual_failed_steps": {},
  "visual_failed_step_count": 0
}
```

`visual_refresh_ok=false` means the refresh marker was not reported by the
listener. Optional display/viewfit/redraw Tcl commands may still fail on older
HyperMesh builds; those failures are retained in `visual_failed_steps` with
`visual_refresh_reason=visual_step_warnings`, but they are not the hard creation
gate when `visual_counts`, `visual_displayed_counts`, and `visibility` prove
the FE entities exist and are displayed.
Method values such as `entitylist`, `marklength`, `marklength_displayed`, and
`failed` explain whether the count came from direct entity-list queries or
old-version mark fallback Tcl.

### `hm_gui_modeling_smoke`

Runs a connected-GUI FE/visualization smoke workflow: create one small FE cube,
record the current geometry-solid route state, then request a visualization
refresh. The experimental-blocked geometry solid stage is recorded in
`stages.solid_box` but does not make the ordinary FE smoke fail.
Successful output also lifts the refresh `visual_counts`,
`visual_displayed_counts`, `visual_count_methods`,
`visual_display_count_methods`, `visibility`, `visual_steps`, and
`visual_refresh_ok/reason` to the top level so Claude/Codex can distinguish
"entities were created but hidden" from "no entities were created" and inspect
which optional display command failed.
The tool itself treats the modeling smoke as failed unless
`visual_counts.elements > 0`, and exposes `visual_counts_ok` plus
`visual_display_ok` for the count/display gates. The repo-local Claude smoke
command enforces the same gate and prefers those tool-reported gate fields when
present. When display diagnostics are available, FE elements must be displayed;
otherwise the failure reason is `visual_display_hidden`.
Its JSON output includes `modeling_smoke_failure.reason` when that gate fails.
`runtime_validation_evidence` remains false for geometry solid promotion unless
the solid route actually succeeds with `created_count > 0`, `solids_count`
increasing, visible solids, and displayed solids. Ordinary FE/visual smoke
success does not promote `create_geometry_solid_box`.
When the GUI listener is not connected, it also returns
parsed `gui_connection`, `gui_diagnostics`, and `next_hypermesh_commands` with
Tcl Console commands such as `mcp_start_on_port 47884`. If Claude smoke is run
with a fixed `--port`, the recovery commands stay on that port and do not
generate an alternate listener file. Fixed-port recovery uses
`mcp_start_on_port <port>` and does not append a second direct `source` command,
because `mcp_start_on_port` already sources and verifies the listener. If
`hmcustom.tcl` has not been loaded and `mcp_start_on_port` is unavailable, the
same Tcl line falls back to directly sourcing the fixed-port listener. The JSON also includes
`retry_smoke_command`, a PowerShell command to run after the Tcl Console
recovery commands.
`diagnose_hypermesh_listener` also exposes `start_or_source_command` and
`alternate_start_or_source_command` for the same recovery flow; keep
`source_command` only as a compatibility fallback.
Connected GUI smoke also reports `gui_listener_version_ok` and
`gui_listener_version`; the current listener version must match
`gui_diagnostics.expected_listener_version` before modeling smoke runs.
`gui_diagnosis` lifts `gui_diagnostics.diagnosis` to the top level for agents
that should not parse nested diagnostics. Its `reason` and `action` fields
provide stable recovery classification, such as `listener_not_running`,
`port_occupied_without_pong`, `listener_version_mismatch`, and
`listener_ready`.
When a local TCP endpoint accepts the port but does not return
`HYPERMESH_MCP_PONG`, `diagnose_hypermesh_listener` also returns
`port_owner_summary`, a compact list such as
`hwx.exe pid=123 state=LISTENING local=127.0.0.1:47884`. Use it to report the
process/PID occupying the listener port without requiring agents to parse raw
`netstat` rows.
Claude smoke lifts this tool field to top-level
`modeling_runtime_validation_evidence` when `--modeling-smoke` is used.

Input:

```json
{
  "params": {
    "size": 10.0,
    "element_size": 10.0,
    "timeout": 30
  }
}
```

### `hm_command_map`

Lists or inspects verified HyperMesh Tcl modeling command routes.

Input:

```json
{"params": {"route_name": "create_structured_hex8_box"}}
```

Output includes:

```json
{
  "success": true,
  "route_name": "create_structured_hex8_box",
  "route": {
    "status": "verified",
    "runtime_validated": true,
    "verification_level": "runtime_validated",
    "element_config": 208,
    "commands": ["*createnode", "*createlist nodes", "*createelement 208"]
  }
}
```

High-level modeling tools should only use command routes marked `verified`.
`verification_level` distinguishes local source evidence from connected-GUI
runtime validation. Geometry-solid `*solidblock` may report
`source_verified_runtime_pending` until `hm_gui_modeling_smoke` proves that
`solids_count` increases and the solid is displayed in the current HyperMesh
session.

## Save Tools

### `hm_auto_save`

Saves the current HyperMesh model and verifies the file exists.

Input:

```json
{
  "params": {
    "step_name": "listener_smoke",
    "model_path": "runs/listener_smoke.hm",
    "timeout": 60
  }
}
```

Output:

```json
{
  "success": true,
  "path": "runs/listener_smoke.hm",
  "size": 22717
}
```

## Config Tools

### `check_environment`

Checks Python/conda/package environment.

### `load_path_config`

Loads a YAML config from `path/`.

### `validate_path`

Checks whether a path exists.

### `dyna_keyword_policy`

Returns the structured Dyna keyword/manual/embedding execution policy.

Expected output includes:

```json
{
  "success": true,
  "embedding_execution_allowed": false,
  "lookup_flow": ["keyword", "cardimage", "entity_type", "datanames", "fields", "examples", "manual_refs"]
}
```

### `dyna_keyword_query`

Looks up one LS-DYNA keyword in the structured local maps. This is a read-only
retrieval helper and does not authorize execution from manual notes or
embedding results.

Input:

```json
{"params": {"keyword": "MAT_3"}}
```

Expected output includes:

```json
{
  "success": true,
  "keyword": "*MAT_3",
  "canonical_keyword": "*MAT_3",
  "matched_alias": false,
  "known": true,
  "cardimage": "MATL3",
  "candidate_confidence": "cardimage_direct_datanames_unverified",
  "field_execution_status": {
    "E": {
      "dataname": null,
      "route_status": "requires_hm_recording",
      "executable": false,
      "reason": "requires_hm_recording"
    }
  },
  "execution_decision": {
    "state": "blocked",
    "allowed_execution_source": "structured_verified_map",
    "blocked_reasons": [
      "datanames_not_verified",
      "fields_require_hm_recording"
    ],
    "advisory_candidates_are_executable": false
  },
  "execution_blockers": [
    "datanames_not_verified",
    "fields_require_hm_recording"
  ],
  "advisory_only": {
    "dataname_candidates": true,
    "dataname_candidate_fields": ["E", "MID", "PR"],
    "examples": true,
    "manual_refs": true,
    "manual_notes": true,
    "execution_allowed": false
  },
  "execution_ready": false,
  "suggestions": [],
  "execution_policy": "structured_map_only",
  "execution_allowed_from_embedding": false
}
```

Direct cardimage routes do not imply executable datanames. For example,
`*MAT_3` maps directly to `MATL3`, but its fields stay non-executable until the
HyperMesh datanames are verified through command recording or a trusted local
dictionary source. Dictionary dataname candidates are advisory only; they do
not make `execution_ready=true` unless the route itself is marked as verified
and every declared field has a verified dataname. `advisory_only` is a compact
reminder that dictionary candidates, examples, manual refs, and manual notes are
not execution authority. Claude/Codex integrations should use
`execution_decision.state`, `execution_blockers`, and
`advisory_only.execution_allowed=false` as go/no-go fields before any Tcl or
K-language action.

For unknown or misspelled keywords, `dyna_keyword_query` may return
`suggestions` from structured routes, aliases, and `keyword_index`. Suggestions
are retrieval-only and must not be executed directly:

```json
{
  "success": false,
  "keyword": "*LOAD_BLAS",
  "canonical_keyword": "*LOAD_BLAS",
  "known": false,
  "execution_ready": false,
  "execution_blockers": ["no_structured_keyword_route"],
  "suggestions": [
    {
      "keyword": "*LOAD_BLAST",
      "source": "dyna_keyword_map.keyword_routes",
      "cardimage": "LOAD_BLAST",
      "execution_ready": false,
      "execution_allowed": false
    }
  ]
}
```

If a suggestion looks correct, call `dyna_keyword_query` again with the
suggested canonical keyword and still require `execution_ready=true` before any
keyword-setting tool is allowed to send Tcl.

`dyna_keyword_map_validate` also rejects inconsistent MAP edits where a field
status ends with `verified` but the field has no `dataname`. If a dataname is
present while the field status is still unverified, validation returns a warning
and the route remains non-executable.

### `hm_set_keyword`

Tool title: `MAP-Gated Keyword Card`.

Attempts to set one LS-DYNA keyword card in the connected HyperMesh GUI. This
tool is gated by `dyna_keyword_query`: a local Tcl template or verified-looking
template mapping is not enough to execute. The keyword route must return
`execution_ready=true`, which requires structured verified cardimage and
datanames for every required field.

When the route is not verified, the tool returns:

```json
{
  "success": false,
  "error_type": "dyna_keyword_execution_not_verified",
  "execution_ready": false,
  "execution_decision": {
    "state": "blocked"
  },
  "execution_blockers": [
    "datanames_not_verified",
    "fields_require_hm_recording"
  ],
  "advisory_only": {
    "execution_allowed": false
  }
}
```

Use this blocked response as the expected state for keywords such as
`SECTION_SOLID` until their HyperMesh cardimage and datanames are verified by
command recording or another trusted local source and promoted in
`templates/dyna_keyword_map.json`.

### `dyna_keyword_map_validate`

Validates the structured LS-DYNA keyword MAP guardrails before any execution
workflow uses it. This is read-only and is intended for CC/Codex smoke checks.

Expected output includes:

```json
{
  "success": true,
  "errors": [],
  "routes_checked": 7,
  "embedding_execution_allowed": false
}
```

Current structured routes include `*MAT_3`, `*SECTION_SOLID`,
`*CONTROL_TERMINATION`, `*CONTROL_TIMESTEP`, `*DATABASE_BINARY_D3PLOT`,
`*INITIAL_DETONATION`, and `*LOAD_BLAST`. `*CONTROL_TERMINATION`,
`*CONTROL_TIMESTEP`, `*INITIAL_DETONATION`, and `*LOAD_BLAST` are intentionally
retrieval/planning-only until their HyperMesh card fields are recorded and
verified in the target profile. Fields such as `ENDTIM`, timestep/mass-scaling
controls, detonation setup, and blast load set IDs must remain non-executable
in smoke checks. The local dictionary may surface advisory cardimage or
dataname candidates such as `Termin`, `TimeStep`, or `LSD_DT2MS`; these
candidates help plan the next recording step but still do not make any field
executable.

## Keyword Helpers

The following tools remain available for HyperMesh card/template work, but they do not imply solver execution:

```text
hm_set_keyword
hm_keyword_help
hm_search_keywords
hm_keyword_map
hm_convert_model
```

`hm_convert_model` has the tool title `Blocked LS-DYNA Profile Conversion` and
returns a blocked compatibility result until LS-DYNA profile activation,
cardimage conversion, material/property binding, and related datanames have
verified HyperMesh GUI routes.

## Not In Current API Scope

The current MCP server should not expose non-HyperMesh GUI listener workflows.
