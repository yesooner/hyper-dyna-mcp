# Hyper-Dyna-MCP

<p align="center">
  <a href="./README.md"><img alt="中文" src="https://img.shields.io/badge/语言-中文-blue"></a>
  <a href="./README.en.md"><img alt="English" src="https://img.shields.io/badge/Language-English-lightgrey"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-AGPL--3.0-orange"></a>
</p>

Hyper-Dyna-MCP 是一个面向本机 HyperMesh GUI 的 MCP server。它通过 `FastMCP + stdio` 接入 Claude Code / Codex，并把经过验证的 Tcl 路线发送到正在运行的 HyperMesh GUI listener。

当前范围只包含 HyperMesh GUI 自动化。LS-DYNA 求解器、LS-PrePost、hmbatch、后端写 K 文件和 K 文件导出都不是当前 MCP 执行能力。

## 当前状态

- 版本：`2.0.0`
- MCP 传输：`FastMCP + stdio`
- 运行目标：本机 HyperMesh GUI listener
- 默认端口：`47883`
- 可用 FE 创建：HEX8、TET4、QUAD4 shell、TRIA3、BAR2/BEAM、DISCRETE spring、MASS element
- 可用几何创建：surface plate、geometry solid box（verified `*solidblock` route）
- 可用建模 action：`assign_material`、`assign_property`、`assign_section`、`assign_eos`、`apply_constraint`、`apply_load`
- 默认阻断：`*tetmesh`、surface automesh、line mesh、mixed mesh、K export；复杂卡片（如 `MAT_3`、`LOAD_BLAST`）仍需验证

## 工作流程

```mermaid
flowchart TD
    A["Claude Code / Codex"] --> B["FastMCP stdio<br/>program.server"]
    B --> C["首选入口<br/>hm_modeling_action"]
    C --> D["能力查询<br/>hm_element_capability_matrix"]
    D --> E{"路线是否 verified?"}
    E -- "是" --> F["发送 Tcl<br/>HyperMesh GUI listener"]
    F --> G["HyperMesh GUI<br/>创建/显示/保存 .hm"]
    E -- "否" --> H["阻断执行<br/>recording_requirements"]
    H --> I["HyperMesh command recording"]
    I --> J["validate_recording"]
    J --> K{"promotion_ready?"}
    K -- "是" --> L["加入 verified map"]
    K -- "否" --> H
```

## 快速使用

### 1. 注册 MCP

让 Claude Code / Codex 通过 stdio 启动：

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

本项目不是 FastAPI/HTTP 服务，不需要手动常驻 Web server。

### 2. 启动 HyperMesh Listener

在 HyperMesh Tcl Console 中执行：

```tcl
set ::mcp_hm_port 47883
source "<repo-root>/runs/hm_gui_listener.tcl"
```

成功时应能收到：

```text
HYPERMESH_MCP_PONG
```

如果端口被占用，使用固定恢复端口 `47884`：

```tcl
catch {mcp_stop}
if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} else {source "<repo-root>/runs/hm_gui_listener_47884.tcl"}
```

### 3. 验证

连接 HyperMesh 的 smoke：

```powershell
<python> -B -X utf8 -m program.claude_smoke --config <mcp-config.json> --with-gui --port 47883 --modeling-smoke
```

只做本地 no-GUI 检查：

```powershell
<python> -B -X utf8 -m program.claude_smoke --config <mcp-config.json>
```

## 常用工具

优先使用：

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

直接创建工具：

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

LS-DYNA keyword 查询只用于规划和校验：

```text
dyna_keyword_policy
dyna_keyword_map_validate
dyna_keyword_query
hm_set_keyword
```

## 建模 Action

`hm_modeling_action` 是 agent 建模的首选入口，支持以下 action：

| Action | 功能 | 说明 |
| --- | --- | --- |
| `create_mesh` | 创建结构化 FE 网格 | verified route：HEX8、QUAD4 shell |
| `create_element` | 创建直接 FE element | TET4、TRIA3、BAR2/BEAM、DISCRETE、MASS |
| `assign_material` | 分配材料 | curated keywords：`MAT_ELASTIC` 等 |
| `assign_property` | 分配属性 | curated keywords：`SECTION_SOLID`、`SECTION_SHELL`、`SECTION_BEAM`、`SECTION_DISCRETE` |
| `assign_section` | 分配截面 | 同 assign_property |
| `assign_eos` | 分配 EOS | curated keywords：`EOS_LINEAR_POLYNOMIAL` 等 |
| `apply_constraint` | 施加约束 | curated keywords：`BOUNDARY_SPC`、`BOUNDARY_SPC_SET` |
| `apply_load` | 施加载荷 | curated keywords：`LOAD_NODE`、`LOAD_SEGMENT`、`LOAD_SHELL` 及其 set 变体 |
| `recording_requirements` | 查看录制要求 | 用于 blocked route 的下一步 |
| `validate_recording` | 校验录制证据 | promotion 闭环 |

材料分配能力矩阵支持所有元素类型：`solid_hex`、`solid_tet`、`shell_quad`、`shell_tria`、`line_beam`、`lumped_mass`、`discrete`。

## Curated Keyword 列表

当前通过 `hm_set_keyword` 可执行的 LS-DYNA keyword：

**材料**
- `MAT_ELASTIC`

**截面/属性**
- `SECTION_SOLID`
- `SECTION_SHELL`
- `SECTION_BEAM`
- `SECTION_DISCRETE`

**EOS**
- `EOS_LINEAR_POLYNOMIAL`

**约束**
- `BOUNDARY_SPC`
- `BOUNDARY_SPC_SET`

**载荷**
- `LOAD_NODE`、`LOAD_NODE_SET`
- `LOAD_SEGMENT`、`LOAD_SEGMENT_SET`
- `LOAD_SHELL`、`LOAD_SHELL_SET`

未被 curated 的复杂卡片仍保持 blocked，例如 `MAT_3`、`LOAD_BLAST`。

## 功能范围

| 类型 | 当前状态 |
| --- | --- |
| HEX8 structured FE | 可用，走 verified Tcl route |
| TET4 / TRIA3 direct element | 可用，只创建直接 FE element，不是自动网格 |
| QUAD4 shell plate | 可用，结构化 FE shell，不做 surface automesh |
| BAR2/BEAM line | 可用，创建新直线和 BEAM element |
| DISCRETE / MASS | 可用，基础 FE element 创建 |
| Geometry surface | 可用 |
| Geometry solid box | 可用，走 verified `*solidblock` route |
| 材料/property/section/EOS/约束/LOAD | 可用，走 `hm_set_keyword` GUI Tcl 模板；复杂卡片仍需验证 |
| `*tetmesh` / surface automesh / line mesh / `mixed_mesh_workflow` | 未开放，需要 command recording |
| K export | 未开放，不能用后端 K writer 代替 GUI 导出 |

FE 网格、几何实体和 K 文件是不同路线。Agent 必须优先走 HyperMesh GUI listener 和 verified route；`program.tools.k_writer`、`program.tools.k_parser`、`program.tools.hm_k_integration` 只能作为离线 fixture/test/review，不能绕过 GUI 建模或伪装成最终 `.k` 导出。

## 录制验证

未开放路线不能靠猜 Tcl 实现。流程是：

1. 用 `hm_modeling_action(action="recording_requirements")` 查看需要的证据。
2. 在 HyperMesh 中用 command recording 录制真实 Tcl。
3. 用 `hm_modeling_action(action="validate_recording")` 校验 recording 和 runtime evidence。
4. 只有 `promotion_ready=true` 后，才能把路线加入 verified map。

## 本地验证

```powershell
<python> -B -X utf8 -m pytest
<python> -B -X utf8 -m program.claude_smoke --config <mcp-config.json>
```

## 关键文件

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

## 边界

- 不猜测未验证的 HyperMesh Tcl 命令。
- 不通过当前 MCP 执行 LS-DYNA、LS-PrePost 或 hmbatch。
- 不把 Dyna manual 文本或 embedding 当作执行依据。
- 不用 K writer/parser/integration 绕过 HyperMesh GUI。
- 不提交 `.claude/`、`.codex/`、本机 MCP JSON、商业软件路径、token、proxy 或本机 path YAML。

## 许可证

本项目使用 GNU Affero General Public License v3.0，见 [LICENSE](LICENSE)。
