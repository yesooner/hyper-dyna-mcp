# 07 — K 语言格式规范（基于 LS-DYNA R13 手册）

Generated: 2026-05-28
Source: LS-DYNA Keyword User's Manual Volume I, pages 365-394

## 1. 文件结构

```
*KEYWORD [options]        ← 必须是第一行
$ 注释行
*TITLE
分析标题

*CONTROL_TERMINATION
...

*PART
...

*NODE
...

*ELEMENT_SOLID
...

*END                      ← 可选，标记输入结束
```

**规则：**
- `*KEYWORD` 必须是文件第一行（或在执行行指定 `keyword` 参数）
- 关键字顺序无关（`*END` 除外）
- 多个相同关键字块是允许的
- `*END` 可选，之后的数据不被读取

## 2. 卡片格式

### 2.1 标准格式（Standard Format）

```
8 fields × 10 characters = 80 characters per line
```

| 字段位置 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---------|---|---|---|---|---|---|---|---|
| 字符范围 | 1-10 | 11-20 | 21-30 | 31-40 | 41-50 | 51-60 | 61-70 | 71-80 |

**类型：**
- `I` — 整数（标准 I8，即 8 字符右对齐）
- `F` — 浮点数（标准 F16.8，即 16 字符，8 位小数）
- `A` — 字符串（标准 A8，即 8 字符左对齐）

**示例 — *NODE 卡片：**
```
*NODE
       1       0.0       0.0       0.0       0       0
       2       1.0       0.0       0.0       0       0
       3       1.0       1.0       0.0       0       0
```
字段：NID(I8) X(F16.8) Y(F16.8) Z(F16.8) TC(I8) RC(I8)

### 2.2 自由格式（Free Format）

用逗号分隔值，可在文件中与固定格式混合使用：

```
*NODE
1,0.0,0.0,0.0,0,0
2,1.0,0.0,0.0,0,0
```

**限制：** 逗号分隔时，每个值的字符数不能超过固定格式的字段长度。

### 2.3 长格式（Long Format）

通过以下方式启用：
- 执行行：`long=y`
- *KEYWORD 卡：`*KEYWORD long=y`
- 单个关键字后缀 `+`：`*NODE +`
- *INCLUDE 后缀 `+`：`*INCLUDE +`（包含文件内所有命令使用长格式）

长格式将所有 ≤20 字符的字段扩展到 20 字符，字符串扩展到 A160。

### 2.4 I10 格式

通过以下方式启用：
- 执行行：`i10=y`
- *KEYWORD 卡：`*KEYWORD i10=y`
- 单个关键字后缀 `%`：`*NODE %`

将整数字段从 I8 扩展到 I10。

## 3. 注释

- `$` 在第 1 列 = 注释行（整行被忽略）
- 注释可出现在文件任意位置
- 注释不影响卡片解析

```tcl
$ This is a comment
*NODE
$ Define node 1
       1       0.0       0.0       0.0
```

## 4. 关键字语法

### 4.1 基本格式

```
*KEYWORD_NAME_{OPTION1}_{OPTION2}_...
```

- `*` 必须在第 1 列
- 关键字不区分大小写
- `{OPTION}` 中的 `<>` 表示可选，`{}` 表示必须选一个

### 4.2 常见关键字族

| 关键字族 | 子类型 | 用途 |
|---------|--------|------|
| *ELEMENT | _BEAM, _SHELL, _SOLID, _TSHELL, _DISCRETE, _MASS | 单元定义 |
| *MAT | _001 到 _200+ | 材料模型 |
| *SECTION | _BEAM, _SHELL, _SOLID, _SPH, _TSHELL | 截面属性 |
| *PART | _INERTIA, _REPOSITION, _CONTACT, _PRINT | 部件定义 |
| *CONTACT | _AUTOMATIC_*, _SINGLE_*, _ERODING_* | 接触定义 |
| *BOUNDARY | _SPC, _PRESCRIBED_* | 边界条件 |
| *LOAD | _NODE, _BODY, _SEGMENT, _PRESSURE | 载荷 |
| *CONTROL | _TERMINATION, _TIMESTEP, _HOURGLASS, ... | 全局控制 |
| *DATABASE | _BINARY_D3PLOT, _GLSTAT, _MATSUM, ... | 输出控制 |
| *SET | _NODE, _ELEMENT, _PART, _SEGMENT | 集合 |
| *DEFINE | _CURVE, _COORDINATE_SYSTEM, ... | 定义 |
| *CONSTRAINED | _NODAL_RIGID_BODY, _SPOTWELD, ... | 约束 |

## 5. 关键卡片格式详解

### 5.1 *NODE

```
Card 1 (repeat for each node):
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│   NID    │    X     │    Y     │    Z     │    TC    │    RC    │
│    I     │    F     │    F     │    F     │    I     │    I     │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

- NID: 节点编号（唯一）
- X, Y, Z: 坐标
- TC: 平动约束（0=无, 1=X, 2=Y, 3=Z, 4=XY, 5=YZ, 6=ZX, 7=XYZ）
- RC: 转动约束（同 TC 编码）

### 5.2 *PART

```
Card 1 (required): HEADING — 标题行
Card 2 (required):
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│   PID    │  SECID   │   MID    │  EOSID   │   HGID   │   GRAV   │  ADPOPT  │   TMID   │
│    I     │    I     │    I     │    I     │    I     │    F     │    I     │    I     │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

- PID: 部件 ID（唯一）
- SECID: 引用 *SECTION 定义
- MID: 引用 *MAT 定义
- EOSID: 引用 *EOS（可选，默认 0）
- HGID: 引用 *HOURGLASS（可选，默认 0）

### 5.3 *ELEMENT_SHELL

```
Card 1:
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│   EID    │   PID    │    N1    │    N2    │    N3    │    N4    │
│    I     │    I     │    I     │    I     │    I     │    I     │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

### 5.4 *ELEMENT_SOLID

```
Card 1:
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│   EID    │   PID    │    N1    │    N2    │    N3    │    N4    │    N5    │    N6    │
│    I     │    I     │    I     │    I     │    I     │    I     │    I     │    I     │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
Card 2 (continuation):
┌──────────┬──────────┐
│    N7    │    N8    │
│    I     │    I     │
└──────────┴──────────┘
```

### 5.5 *CONTROL_TERMINATION

```
Card 1:
┌──────────┐
│   ENDTIM │
│    F     │
└──────────┘
```

### 5.6 *DATABASE_BINARY_D3PLOT

```
Card 1:
┌──────────┐
│   DT     │
│    F     │
└──────────┘
```

## 6. 续行卡（Continuation Cards）

当一个关键字需要多于 8 个字段时，使用续行卡：
- 续行卡紧跟在前一张卡片之后
- 下一个 `*` 关键字标记当前块的结束
- 可选卡可以被跳过（使用默认值）

## 7. 对 k_parser.py 的设计影响

### 7.1 解析策略

1. **逐行扫描**：读取每行，判断是注释（`$`）、关键字（`*`）还是数据行
2. **关键字识别**：提取 `*` 后的名称和选项
3. **数据行解析**：根据当前关键字类型确定字段格式
4. **多格式支持**：检测逗号分隔（自由格式）vs 固定宽度

### 7.2 关键字分类

```python
KEYWORD_CATEGORIES = {
    "file": {"*KEYWORD", "*END", "*INCLUDE", "*TITLE", "*PARAMETER"},
    "control": {"*CONTROL_*", "*DATABASE_*"},
    "material": {"*MAT_*", "*EOS_*"},
    "section": {"*SECTION_*"},
    "part": {"*PART", "*PART_*"},
    "node": {"*NODE", "*NODE_*"},
    "element": {"*ELEMENT_*"},
    "set": {"*SET_*"},
    "boundary": {"*BOUNDARY_*"},
    "contact": {"*CONTACT_*"},
    "load": {"*LOAD_*"},
    "define": {"*DEFINE_*"},
    "constrained": {"*CONSTRAINED_*"},
}
```

### 7.3 验证规则

1. `*KEYWORD` 必须是第一个非注释行
2. PART → SECTION → MATERIAL 引用链完整性
3. ELEMENT 的节点引用存在性
4. `*END` 之后无数据
