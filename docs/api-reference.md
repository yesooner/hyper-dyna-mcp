# Hyper-Dyna-MCP API Reference

## MCP Tools

### LS-DYNA Keyword Tools

#### `hm_set_keyword`
Set an LS-DYNA keyword in HyperMesh via Tcl template.

**Input:**
```json
{
  "keyword": "MAT_ELASTIC",
  "params": {"MID": 1, "RHO": 7.85e-9, "E": 210000, "PR": 0.3, "DA": 0, "DB": 0},
  "timeout": 15
}
```

**Output:**
```json
{
  "success": true,
  "keyword": "MAT_ELASTIC",
  "params": {...},
  "response": "OK\n...",
  "error": null
}
```

**Supported keywords:** 1935 templates across 20+ categories (mat, section, contact, boundary, load, control, database, set, element, define, initial, constrained, etc.)

---

#### `hm_keyword_help`
Get help text for an LS-DYNA keyword.

**Input:** `{"keyword": "MAT_ELASTIC"}`
**Output:** `{exists, description, parameters, placeholders, manual_page}`

---

#### `hm_check_model`
Query current model state in HyperMesh GUI.

**Input:** `{}`
**Output:** `{connected, comps_count, nodes_count, elems_count, mats_count, props_count, groups_count, window_title}`

---

#### `hm_convert_model`
Convert HyperMesh model to LS-DYNA format (activate template, set card images).

**Input:** `{}`
**Output:** `{success, template, materials, properties}`

---

#### `hm_read_materials`
Read all materials from HyperMesh GUI.

**Input:** `{}`
**Output:** `[{"mid": 1, "cardimage": "MATL1", "RHO": "7.85e-09", "E": "210000", "PR": "0.3"}, ...]`

---

#### `hm_read_components`
Read all components from HyperMesh GUI.

**Input:** `{}`
**Output:** `[{"cid": 1, "part_id": 1, "mat_id": 2, "elem_type": 1, "raw_name": "Part 1 for Mat 2"}, ...]`

---

### GUI Tools

#### `execute_tcl_gui`
Execute Tcl in HyperMesh GUI via socket (with IPC fallback).

**Input:**
```json
{
  "script": "*createmark nodes 1 \"all\"",
  "model_path": "F:/models/test.hm",
  "output_hm_path": "F:/output/saved.hm",
  "timeout": 120,
  "enforce_rules": true
}
```

**Output:**
```json
{
  "success": true,
  "command_id": "cmd_abc123",
  "transport": "socket",
  "fallback_used": false,
  "retry_count": 0,
  "response": "OK\n...",
  "error_type": null,
  "message": null
}
```

---

#### `start_hypermesh_gui_listener`
Generate and save the HyperMesh GUI listener Tcl script.

**Input:** `{"port": 47882}`
**Output:** Instructions to source the listener.

---

#### `check_hypermesh_connection`
Verify hmbatch.exe is accessible and configured.

**Input:** `{}`
**Output:** `{success, hmbatch_path, altair_home, message}`

---

### K File Tools

#### `parse_k_file`
Parse an LS-DYNA .k file and return structured data with validation.

**Input:** `{"filepath": "F:/models/test.k"}`
**Output:** Summary with keywords, parts, materials, validation errors.

---

#### `write_k_file`
Generate an LS-DYNA .k file from parameters.

**Input:** `{"filepath": "F:/output/test.k", "title": "Test", "material": {...}}`
**Output:** File path and size.

---

### Solver Tools

#### `generate_lsdyna_command`
Generate LS-DYNA solver command (dry_run by default).

**Input:** `{"input_file": "F:/models/test.k", "ncpus": 4, "memory": "200m"}`
**Output:** Command string.

---

#### `parse_solver_log`
Parse LS-DYNA output log for termination status and errors.

**Input:** `{"filepath": "F:/runs/messag"}`
**Output:** Termination status, warnings, errors.

---

### LS-PrePost Tools

#### `execute_lsprepost`
Execute an LS-PrePost cfile (batch mode).

**Input:** `{"cfile": "F:/scripts/test.cfile", "dry_run": true}`
**Output:** Command and execution result.

---

#### `generate_cfile`
Generate an LS-PrePost cfile script from commands.

**Input:** `{"commands": ["open d3plot model.d3plot", "plot deformed all 1"]}`
**Output:** cfile content string.

---

### Utility Tools

| Tool | Input | Output |
|------|-------|--------|
| `check_environment` | `{required_packages: [...]}` | Python version, conda env, packages |
| `load_path_config` | `{name: "hypermesh_paths"}` | YAML config data |
| `validate_path` | `{path: "F:/models"}` | Path exists boolean |
| `write_obsidian_log` | `{task, modified_files, ...}` | Log entry |

---

## Transport Modes

| Mode | Port | Stability | Use Case |
|------|------|-----------|----------|
| Socket GUI | 47882 | Medium | Real-time interaction |
| IPC | File queue | High | Stable fallback |
| hmbatch | subprocess | High | Batch processing |

**Auto-fallback:** Socket fails 3 times → IPC → Socket recovers → back to Socket.
