# Validation Workflow

## Non-GUI Validation

Run:

```powershell
<python> -B -X utf8 -m pytest
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json
```

Expected:

```text
pytest: all tests pass
claude_smoke.success = true
claude_smoke.tool_count = 32
missing_required_tools = []
forbidden_tools = []
guardrail_failures = []
```

## Connected GUI Validation

Run after the listener is sourced inside HyperMesh:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json --with-gui --port 47884 --modeling-smoke
```

Expected:

```text
gui_connected = true
gui_listener_version_ok = true
modeling_smoke_ok = true
modeling_visual_counts_ok = true
modeling_visual_display_ok = true
modeling_visual_counts.elements > 0
modeling_visual_counts.solids > 0
modeling_visibility.elements = displayed
modeling_visibility.solids = displayed
```

If the connected-GUI check fails, inspect:

```text
gui_connection
gui_diagnosis
gui_diagnostics
modeling_smoke_failure
modeling_visual_steps
modeling_runtime_validation_evidence
next_hypermesh_commands
retry_smoke_command
```
