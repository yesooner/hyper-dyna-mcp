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

![Hyper-Dyna-MCP Workflow](docs/images/workflow.svg)

## 快速使用

### 1. 配置 Claude Code / Codex

在 Claude Code 或 Codex 的 MCP 配置文件中添加以下内容，让它知道如何启动本项目的 MCP server：

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

Claude Code / Codex 会通过 stdio（标准输入输出）与 MCP server 通信，不需要手动启动 Web 服务。

### 2. 启动 HyperMesh Listener

两种方式：

**方式 A：GUI 界面启动（推荐）**

首次需要在 HyperMesh Tcl Console 中加载脚本：

```tcl
source "<repo-root>/hmcustom.tcl"
```

加载后会自动创建 MCP 标签页，点击 **Start MCP**（Socket 模式）或 **Start Loop**（IPC 模式）即可。

**方式 B：Tcl Console 手动启动**

在 HyperMesh 中打开 Tcl Console（菜单 View → Tcl Console），执行：

```tcl
set ::mcp_hm_port 47883
source "<repo-root>/runs/hm_gui_listener.tcl"
```

成功时返回 `HYPERMESH_MCP_PONG`。如果端口被占用：

```tcl
catch {mcp_stop}
if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} else {source "<repo-root>/runs/hm_gui_listener_47884.tcl"}
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

| Action | 功能 | curated keywords |
| --- | --- | --- |
| `create_mesh` | 创建结构化 FE 网格 | HEX8、QUAD4 shell |
| `create_element` | 创建直接 FE element | TET4、TRIA3、BAR2/BEAM、DISCRETE、MASS |
| `assign_material` | 分配材料 | `MAT_ELASTIC` |
| `assign_property` / `assign_section` | 分配属性/截面 | `SECTION_SOLID`、`SECTION_SHELL`、`SECTION_BEAM`、`SECTION_DISCRETE` |
| `assign_eos` | 分配 EOS | `EOS_LINEAR_POLYNOMIAL` |
| `apply_constraint` | 施加约束 | `BOUNDARY_SPC`、`BOUNDARY_SPC_SET` |
| `apply_load` | 施加载荷 | `LOAD_NODE`、`LOAD_SEGMENT`、`LOAD_SHELL` 及其 set 变体 |
| `recording_requirements` | 查看录制要求 | 用于 blocked route 的下一步 |
| `validate_recording` | 校验录制证据 | promotion 闭环 |

材料分配支持所有元素类型：`solid_hex`、`solid_tet`、`shell_quad`、`shell_tria`、`line_beam`、`lumped_mass`、`discrete`。未被 curated 的复杂卡片（如 `MAT_3`、`LOAD_BLAST`）仍保持 blocked。

## 功能范围

| 类型 | 当前状态 |
| --- | --- |
| HEX8 structured FE | 已开放，走 verified Tcl route |
| TET4 / TRIA3 direct element | 已开放，只创建直接 FE element，不是自动网格 |
| QUAD4 shell plate | 已开放，结构化 FE shell，不做 surface automesh |
| BAR2/BEAM line | 已开放，创建新直线和 BEAM element |
| DISCRETE / MASS | 已开放，基础 FE element 创建 |
| Geometry surface | 已开放 |
| Geometry solid box | 已开放，走 verified `*solidblock` route |
| 材料/property/section/EOS/约束/LOAD | 已开放，走 `hm_set_keyword` GUI Tcl 模板；复杂卡片仍需验证 |
| `*tetmesh` / surface automesh / line mesh / `mixed_mesh_workflow` | 未开放，需要 command recording |
| K export | 未开放，不能用后端 K writer 代替 GUI 导出 |

FE 网格、几何实体和 K 文件是不同路线。Agent 必须优先走 HyperMesh GUI listener 和 verified route；`program.tools.k_writer`、`program.tools.k_parser`、`program.tools.hm_k_integration` 只能作为离线 fixture/test/review，不能绕过 GUI 建模或伪装成最终 `.k` 导出。

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
