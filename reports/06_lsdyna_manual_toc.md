# 06 — LS-DYNA R13 手册目录结构

Generated: 2026-05-28
Source: Zotero `手册` collection — 三卷 LS-DYNA R13 Keyword User's Manual

## Volume I — Keyword User's Manual (3826 pages, 1081 TOC entries)

| Section | Pages | Relevance |
|---------|-------|-----------|
| CHRONOLOGICAL HISTORY | 37-355 | 版本历史，低优先级 |
| MATERIAL MODELS | 356 | 材料模型概述 |
| CONTACT-IMPACT INTERFACES | 361 | 接口概述 |
| **GETTING STARTED** | **365-394** | **K 语言格式规范（核心）** |
| ├─ DESCRIPTION OF KEYWORD INPUT | 365-374 | 输入格式概述 |
| ├─ SUMMARY OF COMMONLY USED OPTIONS | 374 | 常用关键字表 |
| ├─ EXECUTION SYNTAX | 376 | 执行命令行语法 |
| ├─ SENSE SWITCH CONTROLS | 379 | 感知开关 |
| ├─ MPP Procedure | 381 | 并行处理 |
| ├─ FILES | 382 | 文件说明 |
| ├─ RESTART ANALYSIS | 384 | 重启分析 |
| ├─ LS-PrePost | 387 | 后处理 |
| └─ **GENERAL CARD FORMAT** | **391-394** | **卡片格式规范（核心）** |
| *AIRBAG | 395-502 | 气囊定义 |
| *ALE | 503-640 | ALE 方法 |
| *BOUNDARY | 641-790 | 边界条件 |
| *CASE | ~791 | 多工况 |
| *CONSTRAINED | ~800 | 约束 |
| *CONTACT | ~900 | 接触定义 |
| *CONTROL | ~1000 | 全局控制参数 |
| *DAMPING | ~1100 | 阻尼 |
| *DATABASE | ~1150 | 数据库输出控制 |
| *DEFINE | ~1200 | 定义曲线/坐标系等 |
| *ELEMENT | 2381-2518 | 单元定义 |
| ├─ *ELEMENT_BEAM | 2383 | 梁单元 |
| ├─ *ELEMENT_SHELL | ~2440 | 壳单元 |
| ├─ *ELEMENT_SOLID | ~2480 | 实体单元 |
| └─ *ELEMENT_TSHELL | ~2510 | 厚壳单元 |
| *END | 2519 | 输入结束标记 |
| *INCLUDE | 2683-2700 | 文件包含 |
| *INITIAL | ~2710 | 初始条件 |
| *INTEGRATION | ~2730 | 积分规则 |
| *KEYWORD | 3003-3005 | 关键字标记（首卡） |
| *LOAD | ~3010 | 载荷定义 |
| *MAT | ~3020 | 材料定义（详见 Vol.II） |
| *NODE | 3183-3186 | 节点定义 |
| *PARAMETER | ~3200 | 参数定义 |
| *PART | 3207-3210 | 部件定义 |
| *SECTION | 3297-3300+ | 截面定义 |
| *SET | ~3400 | 集合定义 |
| *TERMINATION | ~3500 | 终止条件 |
| *TITLE | ~3510 | 标题 |

## Volume II — Material Models (1993 pages, 345 TOC entries)

| Section | Pages | Relevance |
|---------|-------|-----------|
| *EOS | 13-66 | 状态方程（22种） |
| *MAT | 67-1993 | 材料模型（200+种） |
| ├─ MATERIAL MODEL REFERENCE TABLES | 76-87 | 材料模型对照表 |
| ├─ Alphabetized Materials List | 88-99 | 按字母排序列表 |
| ├─ *MAT_ADD_* | 100-196 | 附加材料特性 |
| ├─ *MAT_001 *MAT_ELASTIC | 197 | 弹性材料 |
| ├─ *MAT_003 *MAT_PLASTIC_KINEMATIC | 215 | 运动硬化塑性 |
| ├─ *MAT_015 *MAT_JOHNSON_COOK | 253 | Johnson-Cook |
| ├─ *MAT_020 *MAT_RIGID | 279 | 刚性材料 |
| ├─ *MAT_024 *MAT_PIECEWISE_LINEAR_PLASTICITY | 308 | 分段线性塑性（常用） |
| └─ ... 更多材料模型 | ... | ... |

## Volume III — Special Topics (571 pages, 285 TOC entries)

| Section | Pages | Relevance |
|---------|-------|-----------|
| *BATTERY | 15-30 | 电池模型 |
| *CESE | 31-108 | CESE 方法 |
| *CHEMISTRY | 109-132 | 化学反应 |
| *DUALCESE | 133-300+ | 双 CESE 方法 |
| ... 更多专题 | ... | ... |

## Dyna-mcp 解析器需要覆盖的关键字

基于 Phase 1 范围，优先解析以下关键字：

| 优先级 | 关键字类别 | 示例 | Volume |
|--------|-----------|------|--------|
| P0 | 文件结构 | *KEYWORD, *END, *INCLUDE, *TITLE | I |
| P0 | 控制卡片 | *CONTROL_TERMINATION, *DATABASE_BINARY_D3PLOT | I |
| P0 | 材料 | *MAT_ELASTIC, *MAT_PIECEWISE_LINEAR_PLASTICITY | II |
| P0 | 截面 | *SECTION_SOLID, *SECTION_SHELL, *SECTION_BEAM | I |
| P0 | 部件 | *PART | I |
| P0 | 节点 | *NODE | I |
| P0 | 单元 | *ELEMENT_SOLID, *ELEMENT_SHELL, *ELEMENT_BEAM | I |
| P1 | 集合 | *SET_NODE, *SET_ELEMENT, *SET_PART | I |
| P1 | 边界 | *BOUNDARY_SPC, *BOUNDARY_PRESCRIBED | I |
| P1 | 接触 | *CONTACT_AUTOMATIC_*, *CONTACT_SINGLE_* | I |
| P1 | 载荷 | *LOAD_NODE, *LOAD_BODY, *LOAD_SEGMENT | I |
| P2 | 状态方程 | *EOS_* | II |
| P2 | 定义 | *DEFINE_CURVE, *DEFINE_COORDINATE | I |
| P2 | 参数 | *PARAMETER, *PARAMETER_EXPRESSION | I |
