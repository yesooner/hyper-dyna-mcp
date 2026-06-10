# Execution Workflow

## Default Commands

Use the repository conda Python only:

```powershell
<python> -B -X utf8 -m pytest
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json
```

Start the MCP server with:

```powershell
<python> -m program.server
```

## HyperMesh GUI Listener

When the GUI listener is not connected, generate or use the fixed-port listener command from Claude smoke:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json --with-gui --port 47884 --modeling-smoke --commands-only
```

Paste the printed Tcl into the HyperMesh Tcl Console. The expected fixed-port command shape is:

```tcl
catch {mcp_stop}
if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} else {source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}
```

After sourcing, rerun:

```powershell
<python> -B -X utf8 -m program.claude_smoke --config claude_code_mcp.json --with-gui --port 47884 --modeling-smoke
```

## Implementation Rules

- Add or change modeling behavior only through verified routes in `templates/hm_command_map.json`.
- Keep large mesh requests bounded by route limits before sending Tcl to HyperMesh.
- Return clear errors instead of sending unverified or oversized Tcl loops.
- Preserve the HyperMesh Python API bridge as a separate optional path.
- Keep stdio clean for MCP protocol; diagnostics go to returned JSON, stderr, or log files.
