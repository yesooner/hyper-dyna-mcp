# 00 — GitHub Survey: Existing CAE MCP Projects

Generated: 2026-05-27

## Summary

Found **6 relevant repos** across LS-DYNA, HyperMesh, and ANSYS domains. Key finding:
**Python 在现有项目中已经成功作为 Tcl/APDL/.k 之间的编排层**，而非替代原生语言。

## Repository Inventory

### 1. times1234/hypermesh-mcp ⭐⭐⭐ 最相关
- **Stars:** 3 | **Language:** Python | **Updated:** 2026-05-25
- **Description:** HyperMesh MCP server，通过 Tcl 脚本自动化网格划分流程
- **架构：** Python 生成 Tcl → hmbatch.exe 执行 或 GUI listener 模式
- **关键文件：**
  - `hypermesh_mcp_server.py` (337KB) — 主服务器，注册 20+ MCP tools
  - `run_full_meshing_workflow.py` (107KB) — 独立工作流运行器
  - `launch_meshing_workflow_panel.tcl` (33KB) — GUI listener Tcl
  - `MCP_WORKFLOW_LOGIC.md` (29KB) — 工作流逻辑文档
  - `OFFLINE_WORKFLOW_SOP.md` (26KB) — 离线 SOP
- **HM版本：** Altair 2020
- **关键技术点：**
  - 双模式执行：batch (hmbatch.exe) vs GUI (listener + socket 127.0.0.1:47881)
  - Tcl 脚本用 `MCP_SCRIPT_BEGIN` / `MCP_SCRIPT_END` 标记保护
  - 信任生成器机制：只执行带标记的网格化命令
  - 批处理 + 检查点：长运行任务分批执行，每批保存 .hm 文件
  - 质量策略：先修拓扑 → 修 2D → 才进 tetra → 删而非留坏单元
  - 齿轮识别：纯几何判定，不依赖命名
- **可复用模块：** Tcl 生成模式、hmbatch 执行器、GUI listener、质量检查逻辑

### 2. knewnothing-git/ansys-mcp-server ⭐⭐
- **Stars:** 22 | **Language:** Python | **Updated:** 2026-05-25
- **Description:** 综合性 ANSYS MCP server，可对接多种 ANSYS 产品
- **架构：** 单文件 `ansys_mcp_server.py` (12.6KB)
- **可复用模块：** ANSYS 产品检测、多产品适配模式

### 3. hongwenwang36-eng/ANSYS-Workbench-mcp ⭐⭐
- **Stars:** 11 | **Language:** Python | **Updated:** 2026-05-26
- **Description:** 基于 MCP 的 ANSYS Workbench 本地桥接工具
- **架构：** Python MCP server ↔ 文件队列 IPC ↔ Workbench journal (.wbjn)
- **IPC 机制：**
  - MCP server 写 JSON 命令文件到 `commands/` 目录
  - Workbench bridge journal 轮询命令目录，执行后写结果到 `results/`
  - `status.json` 做心跳
- **支持模式：** 常驻桥接 (RunWB2.exe -B -R) + 直接批处理
- **可复用模块：** 文件队列 IPC 模式、journal 脚本桥接

### 4. ddm-j/lsdyna-mcp-server
- **Stars:** 0 | **Language:** JavaScript | **Updated:** 2026-01-14
- **Description:** RAG MCP Server for LS-DYNA Docs（仅文档 RAG，无求解器自动化）
- **复用价值：** 低 — 只是文档查询，不含 .k 文件解析或求解器调用

### 5. times1234/hypermesh-mcp-server
- **Stars:** 1 | **Language:** Python | **Updated:** 2026-05-20
- **Description:** 同一作者的另一个版本

### 6. damandeep-hyprbots/hypermesh-mcp
- **Stars:** 0 | **Language:** Python | **Updated:** 2026-01-13
- **Description:** 基本为空，无实际内容

## 关键发现：Python 在 CAE MCP 中的角色

现有成功项目的一致模式是 **Python 只做编排，不做核心 CAE 计算**：

```
LLM/Agent  →  MCP Server (Python)  →  原生语言脚本  →  CAE 软件执行
                                      Tcl          →  HyperMesh (hmbatch)
                                      .wbjn        →  ANSYS Workbench
                                      .k           →  LS-DYNA (求解器)
                                      cfile        →  LS-PrePost
```

| 软件 | 原生自动化语言 | Python 角色 | 成熟方案 |
|------|--------------|------------|---------|
| HyperMesh | Tcl (hmbatch) | 生成 Tcl、管理执行 | times1234/hypermesh-mcp ✓ |
| ANSYS Workbench | .wbjn journal + APDL | 文件队列 IPC | hongwenwang36-eng ✓ |
| LS-DYNA | .k keyword | 解析/生成/调用求解器 | **无成熟方案** |
| LS-PrePost | cfile | 生成 cfile、调用执行 | **无成熟方案** |

## 建议下一步

1. **HyperMesh MCP：** fork `times1234/hypermesh-mcp`，适配 HM 2021 路径 ✓ 已 fork
2. **LS-DYNA .k：** 继续自建 `k_parser.py` / `k_writer.py`（无现有方案可复用）
3. **LS-PrePost：** 参考 ANSYS-Workbench-mcp 的文件队列 IPC 模式
4. **整体架构：** 遵循现有项目的 Python 编排模式，不要试图用 Python 替代 K/Tcl
