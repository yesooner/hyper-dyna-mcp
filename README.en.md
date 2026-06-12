# Hyper-Dyna-MCP

<p align="center">
  <a href="./README.md"><img alt="中文" src="https://img.shields.io/badge/Language-中文-blue"></a>
  <a href="./README.en.md"><img alt="English" src="https://img.shields.io/badge/语言-English-lightgrey"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-AGPL--3.0-orange"></a>
</p>

Hyper-Dyna-MCP is a local MCP server for driving a running HyperMesh GUI session. It integrates with Claude Code / Codex through `FastMCP + stdio` and sends verified Tcl routes to the HyperMesh GUI listener.

The current scope is HyperMesh GUI automation only. LS-DYNA solver execution, LS-PrePost, hmbatch, backend K writing, and K-file export are not active MCP execution capabilities.

## Current Status

- Version: `2.0.0`
- MCP transport: `FastMCP + stdio`
- Runtime target: local HyperMesh GUI listener
- Default port: `47883`
- Available FE creation: HEX8, TET4, QUAD4 shell, TRIA3, BAR2/BEAM, DISCRETE spring, MASS element
- Available geometry creation: surface plate, geometry solid box (verified `*solidblock` route)
- Available modeling actions: `assign_material`, `assign_property`, `assign_section`, `assign_eos`, `apply_constraint`, `apply_load`
- Blocked by default: `*tetmesh`, surface automesh, line mesh, mixed mesh, K export; complex cards (e.g. `MAT_3`, `LOAD_BLAST`) still require validation

## Workflow

![Hyper-Dyna-MCP Workflow](docs/images/workflow.svg)

## Quick Start

### 1. Configure Claude Code / Codex

Add the following to your Claude Code or Codex MCP config file, so it knows how to start this MCP server:

```json
{
  "mcpServers": {
    "hyper-dyna-mcp": {
      "command": "<python>",
      "args": ["-m", "program.server"],
      "cwd": "<repo-root>",
      "env": {
        "PYTHONPATH": "<repo-root>"
      }
    }
  }
}
```

Claude Code / Codex communicates with the MCP server via stdio (standard input/output). No manual web server startup needed.

### 2. Start The HyperMesh Listener

Two ways to start:

**Method A: GUI interface (recommended)**

First load the script in HyperMesh Tcl Console:

```tcl
source "<repo-root>/hmcustom.tcl"
```

This auto-creates an MCP tab. Click **Start MCP** (socket mode) or **Start Loop** (IPC mode).

**Method B: Tcl Console manual start**

Open the Tcl Console in HyperMesh (menu View → Tcl Console) and run:

```tcl
set ::mcp_hm_port 47883
source "<repo-root>/runs/hm_gui_listener.tcl"
```

Success returns `HYPERMESH_MCP_PONG`. If the port is occupied:

```tcl
catch {mcp_stop}
if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} else {source "<repo-root>/runs/hm_gui_listener_47884.tcl"}
```

## Common Tools

Prefer these tools:

```text
hm_modeling_action
hm_element_capability_matrix
hm_command_map
hm_gui_modeling_smoke
hm_visual_refresh
hm_auto_save
check_hypermesh_connection
diagnose_hypermesh_listener
set_hypermesh_listener_port
```

Direct creation tools:

```text
hm_create_fe_cube
hm_create_surface_plate
hm_create_shell_plate
hm_create_tet4
hm_create_tria3
hm_create_beam_line
hm_create_discrete_spring
hm_create_lumped_mass
hm_create_solid_box
```

LS-DYNA keyword tools are for verified template execution, planning, and validation:

```text
dyna_keyword_policy
dyna_keyword_map_validate
dyna_keyword_query
hm_set_keyword
```

## Modeling Actions

`hm_modeling_action` is the preferred agent modeling entry point. It supports the following actions:

| Action | Function | Curated Keywords |
| --- | --- | --- |
| `create_mesh` | Create structured FE mesh | HEX8, QUAD4 shell |
| `create_element` | Create direct FE element | TET4, TRIA3, BAR2/BEAM, DISCRETE, MASS |
| `assign_material` | Assign material | `MAT_ELASTIC` |
| `assign_property` / `assign_section` | Assign property/section | `SECTION_SOLID`, `SECTION_SHELL`, `SECTION_BEAM`, `SECTION_DISCRETE` |
| `assign_eos` | Assign EOS | `EOS_LINEAR_POLYNOMIAL` |
| `apply_constraint` | Apply constraint | `BOUNDARY_SPC`, `BOUNDARY_SPC_SET` |
| `apply_load` | Apply load | `LOAD_NODE`, `LOAD_SEGMENT`, `LOAD_SHELL` and set variants |
| `recording_requirements` | Inspect recording requirements | For blocked routes next step |
| `validate_recording` | Validate recording evidence | Promotion loop |

Material assignment supports all element types: `solid_hex`, `solid_tet`, `shell_quad`, `shell_tria`, `line_beam`, `lumped_mass`, `discrete`. Complex cards that are not curated (e.g. `MAT_3`, `LOAD_BLAST`) remain blocked.

## Capability Scope

| Type | Current Status |
| --- | --- |
| HEX8 structured FE | Open, verified Tcl route |
| TET4 / TRIA3 direct element | Open, direct FE element only, not automesh |
| QUAD4 shell plate | Open, structured FE shell, no surface automesh |
| BAR2/BEAM line | Open, creates a new line and BEAM elements |
| DISCRETE / MASS | Open, basic FE element creation |
| Geometry surface | Open |
| Geometry solid | Open, verified `*solidblock` route |
| Material/property/section/EOS/constraints/LOAD | Open, `hm_set_keyword` GUI Tcl templates; complex cards still require validation |
| `*tetmesh` / surface automesh / line mesh / `mixed_mesh_workflow` | Not open, requires command recording |
| K export | Not open; backend K writer cannot replace GUI export |

FE mesh, geometry entities, and K files are separate routes. Agents must prefer the HyperMesh GUI listener and verified routes. `program.tools.k_writer`, `program.tools.k_parser`, and `program.tools.hm_k_integration` are offline fixture/test/review helpers only and must not bypass GUI modeling or pretend to be final `.k` export.

## Key Files

```text
program/server.py                 MCP server entry
program/tools/hm_gui.py           GUI listener client and diagnostics
program/tools/hm_model_writer.py  FE modeling helpers
program/tools/hm_command_map.py   verified HyperMesh Tcl route map
program/tools/dyna_keyword_map.py structured LS-DYNA keyword policy
program/claude_smoke.py           MCP smoke test
runs/hm_gui_listener.tcl          HyperMesh Tcl listener
templates/hm_command_map.json     HyperMesh route definitions
templates/dyna_keyword_map.json   LS-DYNA keyword route definitions
```

## Boundaries

- Do not guess unverified HyperMesh Tcl commands.
- Do not execute LS-DYNA, LS-PrePost, or hmbatch from the current MCP surface.
- Do not use Dyna manual text or embeddings as execution authority.
- Do not use K writer/parser/integration to bypass HyperMesh GUI.
- Do not commit `.claude/`, `.codex/`, local MCP JSON, commercial software paths, tokens, proxies, or local path YAML.

## License

This project is licensed under the GNU Affero General Public License v3.0. See [LICENSE](LICENSE).
