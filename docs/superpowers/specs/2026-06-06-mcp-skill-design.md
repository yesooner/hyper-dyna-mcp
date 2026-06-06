# HyperMesh MCP Skill 设计文档

**Date:** 2026-06-06
**Status:** Pending User Review

---

## 1. 目标

构建面向 Claude Code / Codex 的 MCP Skill，使 AI 代理能够通过 Tcl 命令控制 HyperMesh，完成 LS-DYNA 前处理全流程。

---

## 2. 核心流程

```
人工导入模型 → Agent 设置求解器模板 → Agent 几何/网格
→ Agent 设置全部关键字 → Agent 模型检查 → 人工导出 .k
```

| 步骤 | 执行者 | 说明 |
|------|--------|------|
| 导入模型 | 人工 | 打开 HyperMesh，导入 .hm / CAD |
| 设置求解器模板 | Agent | 切换 LS-DYNA solver interface |
| 几何/网格 | Agent | 网格划分、质量检查 |
| Section 定义 | Agent | *SECTION_SOLID/SHELL/BEAM |
| Material/EOS | Agent | *MAT_* + *EOS_* |
| Part 赋值 | Agent | 绑定 PID→SECID→MID |
| Set 定义 | Agent | *SET_NODE/PART/SEGMENT |
| Contact | Agent | *CONTACT_* |
| Boundary/Load | Agent | *BOUNDARY_* + *LOAD_* + *DEFINE_CURVE |
| Control Cards | Agent | *CONTROL_* |
| Database 输出 | Agent | *DATABASE_* |
| 模型检查 | Agent | 验证完整性 |
| 导出 .k | 人工 | HyperMesh Export Solver Deck |

---

## 3. 架构

```
hyper-dyna-mcp/
├── ref/
│   └── lsdyna_keyword_reference.md    ← 901 个关键字索引
├── program/
│   ├── tools/
│   │   ├── keyword_fields.py          ← 字段映射（已有）
│   │   ├── hm_gui.py                  ← socket 通信（已有）
│   │   ├── hm_tcl_generator.py        ← Tcl 生成（已有）
│   │   ├── hm_template_engine.py      ← 新：模板引擎
│   │   └── hm_keyword_templates.py    ← 新：901 个 Tcl 模板
│   └── skills/
│       └── hm_lsdyne_skill.py         ← 新：MCP Skill 入口
├── templates/
│   └── keyword/                       ← 新：Tcl 模板文件
│       ├── mat/
│       ├── section/
│       ├── contact/
│       ├── boundary/
│       ├── load/
│       ├── control/
│       ├── database/
│       ├── set/
│       └── ...
```

---

## 4. Tcl 模板设计

### 4.1 模板格式

每个关键字对应一个 Tcl 模板文件，格式：

```tcl
# templates/keyword/mat/MAT_ELASTIC.tcl
# LS-DYNA R13 *MAT_ELASTIC
# Parameters: MID, RHO, E, PR

*createentity mats name="MAT_ELASTIC_{{MID}}" cardimage=MAT_ELASTIC
*setvalue mats id={{MID}} dataname=RHO value={{RHO}}
*setvalue mats id={{MID}} dataname=E value={{E}}
*setvalue mats id={{MID}} dataname=PR value={{PR}}
```

### 4.2 模板引擎

```python
class HmTemplateEngine:
    def render(self, keyword: str, params: dict) -> str:
        """Load template, fill parameters, return Tcl script."""
        template = self.load_template(keyword)
        for key, value in params.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

    def render_sequence(self, steps: list[dict]) -> str:
        """Render multiple keyword templates in order."""
        scripts = []
        for step in steps:
            scripts.append(self.render(step["keyword"], step["params"]))
        return "\n".join(scripts)
```

### 4.3 模板来源

从手册 `lsdyna-maunal/volume_I/II/III.md` 提取每个关键字的：
1. 字段名和类型
2. 默认值
3. 必填/可选
4. 参考页码

映射到 HyperMesh Tcl 命令：
- `*createentity` — 创建实体
- `*setvalue` — 设置属性
- `hm_getvalue` — 查询属性
- `*createmark` — 选择实体

---

## 5. MCP Skill 定义

### 5.1 工具列表

| Tool | 功能 |
|------|------|
| `hm_set_keyword` | 设置单个关键字（查表生成 Tcl） |
| `hm_batch_keywords` | 批量设置多个关键字 |
| `hm_check_model` | 检查模型完整性 |
| `hm_query_keyword` | 查询当前关键字设置 |
| `hm_keyword_help` | 查看关键字说明（从手册） |

### 5.2 `hm_set_keyword` 示例

```
Input:
  keyword: MAT_ELASTIC
  params: {MID: 1, RHO: 7.85e-9, E: 210000, PR: 0.3}

Process:
  1. 查 ref/lsdyna_keyword_reference.md 确认关键字存在
  2. 加载 templates/keyword/mat/MAT_ELASTIC.tcl
  3. 填入参数
  4. 通过 socket 发送到 HyperMesh

Output:
  {success: true, keyword: "MAT_ELASTIC", mid: 1}
```

### 5.3 `hm_keyword_help` 示例

```
Input:
  keyword: CONTACT_AUTOMATIC_SURFACE_TO_SURFACE

Output:
  从手册提取：
  - 关键字用途
  - 字段说明（SSID, MSID, FS, FD 等）
  - 推荐用法
  - 参考页码
```

---

## 6. 901 个关键字的分层策略

### 第一层：核心关键字（约 50 个）— 优先实现

```
MAT: ELASTIC, RIGID, PLASTIC_KINEMATIC, PIECEWISE_LINEAR_PLASTICITY,
     NULL, JOHNSON_COOK, HIGH_EXPLOSIVE_BURN, CONCRETE_DAMAGE_REL3
SECTION: SOLID, SHELL, BEAM, TSHELL
PART: PART
NODE: NODE
ELEMENT: SOLID, SHELL, BEAM
CONTACT: AUTOMATIC_SURFACE_TO_SURFACE, AUTOMATIC_SINGLE_SURFACE,
         TIED_SURFACE_TO_SURFACE, ERODING_SINGLE_SURFACE
BOUNDARY: SPC_SET, SPC_NODE, PRESCRIBED_MOTION_SET
LOAD: NODE_SET, SEGMENT_SET, BODY, RIGID_BODY
SET: NODE_LIST, PART_LIST, SEGMENT
CONTROL: TERMINATION, TIMESTEP, CONTACT, HOURGLASS, ENERGY
DATABASE: BINARY_D3PLOT, GLSTAT, MATSUM, RCFORC
DEFINE: CURVE
```

### 第二层：扩展关键字（约 200 个）— 第二批

```
MAT: 其余常用材料模型
EOS: LINEAR_POLYNOMIAL, GRUNEISEN, TABULATED
BOUNDARY: 其余边界类型
LOAD: 其余载荷类型
CONTACT: 其余接触类型
CONSTRAINED: NODAL_RIGID_BODY, SPOTWELD, EXTRA_NODES
INITIAL: VELOCITY, STRESS
RIGIDWALL: PLANAR, GEOMETRIC
```

### 第三层：长尾关键字（约 650 个）— 按需扩展

```
AIRBAG, ALE, CESE, CHEMISTRY, DUALCESE, IGA 等专业领域关键字
```

---

## 7. 模板数据提取流程

```
lsdyna-maunal/volume_I.md
  → 提取关键字定义（字段名、类型、默认值）
  → 映射到 HyperMesh Tcl 命令
  → 生成 templates/keyword/*.tcl
  → 验证：在 HyperMesh 中执行，检查 card image
```

每个模板需要：
1. 从手册提取字段定义
2. 在 HyperMesh 中手动验证 Tcl 命令格式
3. 编写模板
4. 编写测试

---

## 8. 验证方案

每个模板验证流程：

```
1. 生成 Tcl 脚本
2. 通过 MCP socket 发送到 HyperMesh
3. 查询设置结果（hm_getvalue）
4. 人工在 HyperMesh 中检查 card image
5. 导出 .k 文件，检查关键字是否正确
```

---

## 9. 实现顺序

```
Phase 7.1: 搭建模板引擎 + 目录结构
Phase 7.2: 提取核心 50 个关键字模板（从手册）
Phase 7.3: 实现 MCP Skill（hm_set_keyword 等）
Phase 7.4: 在 HyperMesh 中验证核心模板
Phase 7.5: 扩展到 200 个关键字
Phase 7.6: 扩展到 901 个关键字
```

---

## 10. 验收标准

1. AI 可通过 `hm_set_keyword` 设置任意已实现的关键字
2. 设置结果在 HyperMesh card image 中正确显示
3. 人工导出的 .k 文件中关键字正确
4. `hm_keyword_help` 能返回任意关键字的手册说明
5. 全部 901 个关键字有模板覆盖
