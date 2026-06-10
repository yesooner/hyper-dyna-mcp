# Selected Workflow

## Current Decision

This repository is maintained as a HyperMesh GUI-only MCP server for the current phase.

The selected route is:

```text
Codex / Claude Code
  -> FastMCP stdio server
  -> HyperMesh Tcl GUI listener
  -> verified Tcl command routes
  -> model-state and visualization validation
```

Do not expose solver execution, LS-PrePost execution, HyperMesh hmbatch execution, or K-file export as current MCP tools.

## Execution Boundaries

- FE cube creation uses the verified `create_structured_hex8_box` route.
- Geometry solid box creation uses the verified `create_geometry_solid_box` route and must validate that `solids_count` increases in the connected GUI session.
- Dyna keyword/manual knowledge is structured-map first. Embeddings and distilled notes are explanation and retrieval aids only; they do not authorize execution.
- HyperMesh Python API tooling remains separate from the Tcl GUI listener path and must stay dry-run by default unless explicitly overridden.
- Claude Code compatibility is verified through repo-local `claude_code_mcp.json` and `program.claude_smoke`.

## Required Evidence Before Claiming Complete

- `program.claude_smoke --config claude_code_mcp.json` succeeds without GUI.
- `program.claude_smoke --config claude_code_mcp.json --with-gui --port <port> --modeling-smoke` succeeds in a real connected HyperMesh GUI.
- Full pytest passes with the repository conda Python.
- MCP tool surface includes required HyperMesh GUI tools and excludes solver/hmbatch/export tools.
- `hm_gui_modeling_smoke` reports FE elements and geometry solids present and displayed.
