# Hyper-Dyna-MCP

<p align="center">
  <a href="./README.md"><img alt="中文" src="https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E4%B8%AD%E6%96%87-blue"></a>
  <a href="./README.en.md"><img alt="English" src="https://img.shields.io/badge/Language-English-lightgrey"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-AGPL--3.0-orange"></a>
</p>

Hyper-Dyna-MCP 是一个面向本机 HyperMesh GUI 的 MCP server。它通过 `FastMCP + stdio` 接入 Claude Code / Codex，再由 Python 编排层把经过验证的 Tcl 路线发送到正在运行的 HyperMesh GUI listener。

当前版本聚焦 HyperMesh GUI 自动化。LS-DYNA 求解器执行、LS-PrePost 执行和 K 文件导出不属于当前 MCP 工具面。

## ✅ 当前状态

- 版本：`1.0.0`
- MCP 传输：`FastMCP + stdio`
- 运行目标：本机 HyperMesh GUI listener
- 工具数量：33 个 HyperMesh 相关 MCP tools
- FE 路线：已验证的结构化 HEX8 网格路线，使用 `*createnode`、`*createlist nodes`、`*createelement 208`
- Solid 路线：`*solidblock` 已有本机脚本证据，仍需要目标 HyperMesh GUI session 的 runtime validation
- Dyna keyword：结构化 MAP 优先，manual notes / embedding 只用于解释和检索，不作为执行依据

## 🎬 HyperMesh 2021 演示流程

以下流程基于 HyperMesh 2021 演示。README 中已删除单独 `source hmcustom.tcl` 的步骤，只保留 MCP server 启动和 HyperMesh listener/smoke 两步。

### Step 1: 注册 MCP Server

推荐方式是让 Claude Code / Codex 通过 stdio MCP 配置自动启动 `program.server`。不要把 stdio MCP server 当成普通后台 HTTP 服务手动常驻运行。

本机 MCP 注册示例：

```json
{
  "mcpServers": {
    "hyper-dyna-mcp": {
      "command": "C:/path/to/conda/envs/hyper-dyna/python.exe",
      "args": ["-B", "-X", "utf8", "-m", "program.server"],
      "cwd": "C:/path/to/hyper-dyna-mcp"
    }
  }
}
```

本机 MCP 注册文件不要提交到 Git。仓库已忽略 `.claude/`、`.codex/`、`claude_code_mcp*.json` 和本机路径配置。

仅调试 server 入口时可手动运行：

```powershell
C:/path/to/conda/envs/hyper-dyna/python.exe -B -X utf8 -m program.server
```

### Step 2: 连接 HyperMesh 并运行 Smoke

在 MCP client 中先调用 `start_hypermesh_gui_listener`，生成当前机器可用的 Tcl listener 文件。然后在 HyperMesh Tcl Console 中 source 工具返回的 listener 路径，例如：

```tcl
source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
```

预期 listener metadata 包含：

```text
HYPERMESH_MCP_PONG
LISTENER_VERSION=2024-compat-v3
```

然后运行连接 HyperMesh GUI 的 smoke test：

```powershell
C:/path/to/conda/envs/hyper-dyna/python.exe -B -X utf8 -m program.claude_smoke --config C:/path/to/local-mcp-config.json --with-gui --port 47884 --modeling-smoke
```

如果旧 listener 或端口占用影响演示，可使用端口专用 listener：

```tcl
source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"
```

## 🧭 架构流程

```mermaid
flowchart LR
    U["用户 / Agent"] --> C["Claude Code / Codex"]
    C --> M["FastMCP stdio<br/>program.server"]
    M --> T["MCP Tools<br/>hm_create_fe_cube / hm_create_solid_box / dyna_keyword_query"]
    T --> V["Verified Maps<br/>hm_command_map.json<br/>dyna_keyword_map.json"]
    T --> S["Socket Client<br/>program.tools.hm_gui"]
    S --> L["HyperMesh Tcl Listener<br/>runs/hm_gui_listener*.tcl"]
    L --> H["HyperMesh GUI"]
    H --> R["Model State<br/>FE elements / geometry solids / visibility"]
    R --> M

    V -. "只允许 verified route 执行" .-> T
    T -. "FE mesh route" .-> FE["*createnode<br/>*createlist nodes<br/>*createelement 208"]
    T -. "Geometry solid route" .-> SO["*solidblock<br/>runtime validation required"]
```

## 🛠️ 主要工具

常用 MCP tools：

```text
ping
check_environment
start_hypermesh_gui_listener
check_hypermesh_connection
diagnose_hypermesh_listener
set_hypermesh_listener_port
get_model_info
execute_tcl_gui
hm_auto_save
hm_check_model
hm_read_materials
hm_read_components
hm_set_keyword
hm_create_fe_cube
hm_create_solid_box
hm_create_surface_plate
hm_create_shell_plate
hm_create_beam_line
hm_create_discrete_spring
hm_create_lumped_mass
hm_visual_refresh
hm_gui_modeling_smoke
hm_command_map
hm_element_capability_matrix
dyna_keyword_policy
dyna_keyword_map_validate
dyna_keyword_query
hm_python_api_status
execute_hm_python_api
hm_python_api_current_model_info
```

## 🧱 FE 网格与几何 Solid

`hm_create_fe_cube` 创建的是有限元网格实体，不是 HyperMesh CAD solid。它使用已验证的 FE 路线：

```text
*createnode
*createlist nodes
*createelement 208
```

当前可执行网格能力只到这里：规则 HEX8 FE cube。`hm_mesh_box` 不会再发送未验证的 `*tetmesh`；它会返回 `unsupported_route=tetmesh_geometry_solid`，直到该路线通过 HyperMesh command recording 和真实 GUI runtime validation。

`hm_element_capability_matrix` 用于检查单元族能力边界：当前 `solid_hex` 的 FE 单元创建可执行，`shell_quad` 的结构化 QUAD4 FE plate 直接创建也可执行，`line_beam` 的结构化 BAR2/BEAM line 直接创建也可执行，`discrete` 的两节点 DISCRETE spring 创建可执行，`lumped_mass` 的单节点 MASS 创建可执行；`shell_quad` 另有 geometry surface 创建路线 `hm_create_surface_plate`。但 surface automesh、`SECTION_SHELL` 厚度/属性 datanames、beam section 宽高/orientation datanames、`TET`、`TRIA3`、离散/质量 property datanames、网格划分和材料赋值路线仍是 blocked/unsupported，必须先补 HyperMesh command recording 证据。

`hm_create_surface_plate` 使用已在 HyperMesh 2021 GUI listener 中验证的 `*createdoublearray + *surfacecreatenurbs` 路线创建矩形 geometry surface。它只证明 HyperMesh 几何面实体可创建，不代表 LS-DYNA `*ELEMENT_SHELL`、shell property/material 绑定或 K 文件导出已可执行。

`hm_create_shell_plate` 使用已在 HyperMesh 2021 GUI listener 中验证的 `*createnode + *createlist nodes + *createelement 104` 路线创建结构化 QUAD4 shell FE plate。它不运行 surface automesh，也不设置 `SECTION_SHELL` 厚度/属性或材料绑定。

`hm_create_beam_line` 使用已在 HyperMesh 2021 GUI listener 中验证的 `*linecreatestraight + *createnode + *createlist nodes + *createelement 60` 路线创建结构化 BAR2/BEAM line。不要使用 `*createelement 2` 创建 beam，因为测试证明它生成 `Plotel`。该工具会在同一 Tcl 脚本末尾自动执行可视化刷新；beam section 宽高、orientation 和材料/属性 datanames 仍需后续录制验证。

`hm_create_discrete_spring` 使用已在 HyperMesh 2021 GUI listener 中验证的 `*spring node_a node_b 1 "" 0` 路线创建 `TYPE=DISCRETE, CONFIG=21` 的两节点离散弹簧单元。`hm_create_lumped_mass` 使用 `*createmark nodes 1 node; *masselement 1 mass "" 0` 创建 `TYPE=MASS, CONFIG=1` 的集中质量单元。两者都只创建 FE 元素；`SECTION_DISCRETE` 刚度/阻尼和 `ELEMENT_MASS` property/card datanames 仍未验证，不能作为材料/属性赋值路线使用。

K 文件侧能力与 GUI 创建能力分开判断。当前 `program.tools.k_writer.build_shell_plate_model` 已能生成 QUAD4 shell plate 的 LS-DYNA K 文件，包含：

```text
*NODE
*ELEMENT_SHELL
*ELEMENT_SHELL_THICKNESS
*SECTION_SHELL
*MAT_ELASTIC
*PART
```

这只证明离线 fixture/验证用的 K 文件生成能力，不代表 HyperMesh GUI 里已经可以通过 MCP 创建 shell 单元。Agent 不得用 `k_writer`、`write_k_file` 或后端 K keyword 拼写来绕过 HyperMesh GUI/Tcl listener；建模和可视化必须优先走 Tcl Console/listener 与 verified route。若用户要求最终 `.k` 导出，当前 GUI-only MCP 应返回“不支持/待验证 HyperMesh GUI 导出路线”，不能静默改成后端写 K 文件。

`hm_create_solid_box` 是独立的 geometry solid 路线，基于 `*solidblock`。它必须在目标 HyperMesh GUI session 中证明：

- `solids_count` 增加
- GUI 中 solid 可见
- listener 返回成功结果

不要把 FE 路线替换成 solid 路线。两者创建的实体类型不同，验证门槛也不同。

## 📚 Dyna Keyword 策略

Dyna keyword 支持采用结构化 MAP：

```text
keyword -> cardimage -> dataname -> fields -> examples -> manual_refs
```

manual notes 和 embedding 只用于解释、检索和审查。只有当 HyperMesh cardimage 与 dataname 通过 command recording 或可信本地字典验证后，对应 keyword route 才能进入可执行状态。

关键文件：

```text
templates/dyna_keyword_map.json
templates/dyna_manual_notes.jsonl
templates/hm_command_map.json
templates/hm_dictionary.json
templates/keyword_index.json
```

## ✅ 验证

本地开发可运行：

```powershell
C:/path/to/conda/envs/hyper-dyna/python.exe -B -X utf8 -m pytest
```

MCP smoke：

```powershell
C:/path/to/conda/envs/hyper-dyna/python.exe -B -X utf8 -m program.claude_smoke --config C:/path/to/local-mcp-config.json
```

## 📁 关键路径

```text
program/server.py                 MCP server entry
program/tools/hm_gui.py           GUI listener client and diagnostics
program/tools/hm_model_writer.py  FE and solid modeling tools
program/tools/hm_command_map.py   verified HyperMesh Tcl route map
program/tools/dyna_keyword_map.py structured Dyna keyword policy
program/claude_smoke.py           Claude/Codex MCP smoke test
hmcustom.tcl                      optional HyperMesh Tcl helper
templates/hm_command_map.json     HyperMesh route definitions
templates/dyna_keyword_map.json   Dyna keyword route definitions
```

本机路径应放在被忽略的 `path/*.yaml` 或私有 MCP config 中。不要提交商业软件路径、用户 vault 路径、token、proxy 或 agent session state。

## ⚖️ 许可证

本项目使用 GNU Affero General Public License v3.0，见 [LICENSE](LICENSE)。

## 🔐 边界

- 不猜测未验证的 HyperMesh Tcl 命令
- 不从当前 MCP 工具面执行 LS-DYNA 或 LS-PrePost
- 不把 Dyna manual 文本或 embedding 作为执行依据
- 不提交 `.claude/`、`.codex/`、本机 MCP JSON 或机器专属 path YAML
