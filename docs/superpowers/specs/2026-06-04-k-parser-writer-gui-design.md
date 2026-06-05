# Dyna-mcp Phase 6 Design — K Parser/Writer 增强 + HyperMesh GUI 验证

**Date:** 2026-06-04
**Status:** Approved

---

## 1. 目标

1. K parser 全字段级解析（~80 个字段）
2. K writer 全覆盖生成（CONTACT + LOAD + BOUNDARY + DEFINE_CURVE + SET）
3. HyperMesh GUI 实际 socket 验证
4. 统一目录结构，分类存储全流程文件

---

## 2. 目录结构

```
F:/Dyna-mcp/
├── models/                    # 输入模型文件 (.k, .key, .hm)
├── scripts/                   # 生成的 Tcl/cfile 脚本
├── output/                    # 输出文件
│   ├── screenshots/           # 验证截图 (.png)
│   └── *.k                    # 生成的 K 文件
├── runs/                      # 运行目录
│   ├── case_NNN/              # 求解器输入输出
│   └── lsprepost_commands/    # LS-PrePost IPC
├── logs/                      # 日志
│   └── run/                   # 运行日志
├── reports/                   # 验证报告
├── lib/                       # 模板和样本
│   ├── k_samples/
│   ├── hypermesh_samples/
│   ├── tcl_templates/
│   └── cfile_templates/
├── path/                      # YAML 配置
├── program/                   # MCP 代码
│   ├── tools/
│   └── workflows/
└── tests/                     # 测试
```

---

## 3. K Parser 增强 — 全字段级解析

### 3.1 字段映射表定义

为每个关键字族定义字段映射表：

```python
# program/tools/keyword_fields.py

CONTACT_S2S_FIELDS = [
    ("SSID", int), ("MSID", int), ("SSTYP", int), ("MSTYP", int),
    ("SBOXID", int), ("MBOXID", int), ("SPR", int), ("MPR", int),
    ("FS", float), ("FD", float), ("DC", float), ("VC", float),
    ("VDC", float), ("PENCHK", int), ("BT", float), ("DT", float),
]

CONTACT_S2S_OPT_FIELDS = [
    ("SLSFAC", float), ("RWPNAL", float), ("ISLCHK", int),
    ("SHLTHK", int), ("SNLOG", int), ("ISLDT", int),
    ("IRTH", int), ("IGAP", int), ("PENOPT", int),
]

BOUNDARY_SPC_FIELDS = [
    ("NSID", int), ("CID", int), ("DOFX", int), ("DOFY", int),
    ("DOFZ", int), ("DOFRX", int), ("DOFRY", int), ("DOFRZ", int),
]

DEFINE_CURVE_HEADER = [
    ("LCID", int), ("SIDR", int), ("SFA", float), ("SFO", float),
    ("OFFA", float), ("OFFO", float), ("DTIME", float),
]

DEFINE_CURVE_POINT = [
    ("A", float), ("O", float),
]

LOAD_SEGMENT_FIELDS = [
    ("LCID", int), ("SF", float), ("AT", float), ("N1", float),
    ("N2", float), ("N3", float), ("N4", float),
]

SET_NODE_LIST_HEADER = [("SID", int)]
SET_NODE_LIST_DATA = [("NID", int)]

SET_SEGMENT_HEADER = [("SID", int)]
SET_SEGMENT_DATA = [("N1", int), ("N2", int), ("N3", int), ("N4", int), ("PID", int)]

SET_PART_LIST_HEADER = [("SID", int)]
SET_PART_LIST_DATA = [("PID", int)]

NODE_FIELDS = [("NID", int), ("X", float), ("Y", float), ("Z", float), ("TC", int), ("RC", int)]

ELEMENT_SHELL_FIELDS = [("EID", int), ("PID", int), ("N1", int), ("N2", int), ("N3", int), ("N4", int)]

ELEMENT_SOLID_FIELDS = [("EID", int), ("PID", int), ("N1", int), ("N2", int), ("N3", int), ("N4", int), ("N5", int), ("N6", int), ("N7", int), ("N8", int)]

PART_HEADER = [("HEADING", str)]
PART_DATA = [("PID", int), ("SECID", int), ("MID", int), ("EOSID", int), ("HGID", int)]

MAT_ELASTIC_FIELDS = [("MID", int), ("RHO", float), ("E", float), ("PR", float), ("DA", float), ("DB", float)]

MAT_RIGID_FIELDS = [("MID", int), ("RHO", float), ("E", float), ("PR", float)]

SECTION_SOLID_FIELDS = [("SECID", int), ("ELFORM", int), ("AET", int)]

SECTION_SHELL_FIELDS = [("SECID", int), ("ELFORM", int), ("SHRF", float), ("NIP", int)]
```

### 3.2 KKeyword 增强

```python
@dataclass
class KKeyword:
    name: str
    category: str = "other"
    comments: list[str] = field(default_factory=list)
    data_lines: list[str] = field(default_factory=list)
    options: list[str] = field(default_factory=list)
    parsed_fields: dict = field(default_factory=dict)  # 新增
```

### 3.3 解析逻辑

```python
def _parse_keyword_fields(keyword: KKeyword) -> dict:
    """根据关键字名自动解析字段"""
    fields = KEYWORD_FIELDS_MAP.get(keyword.name)
    if not fields:
        return {}
    result = {}
    for line in keyword.data_lines:
        values = _parse_data_line(line)
        for i, (fname, ftype) in enumerate(fields):
            if i < len(values):
                try:
                    result[fname] = ftype(values[i])
                except (ValueError, TypeError):
                    pass
    return result
```

---

## 4. K Writer 增强 — 全覆盖生成

### 4.1 新增数据类

```python
@dataclass
class Contact:
    ssid: int
    msid: int
    sstyp: int = 0
    mstyp: int = 0
    fs: float = 0.3
    fd: float = 0.3
    dc: float = 0.0
    vc: float = 0.0
    contact_type: str = "AUTOMATIC_SURFACE_TO_SURFACE"

@dataclass
class BoundarySPC:
    nsid: int
    cid: int = 0
    dofx: int = 1
    dofy: int = 1
    dofz: int = 1
    dofrx: int = 0
    dofry: int = 0
    dofrz: int = 0

@dataclass
class LoadSegment:
    lcid: int
    sf: float = 1.0

@dataclass
class DefineCurve:
    lcid: int
    sfa: float = 1.0
    sfo: float = 1.0
    points: list[tuple[float, float]] = field(default_factory=list)

@dataclass
class SetNodeList:
    sid: int
    nodes: list[int] = field(default_factory=list)

@dataclass
class SetSegment:
    sid: int
    segments: list[list[int]] = field(default_factory=list)

@dataclass
class SetPartList:
    sid: int
    parts: list[int] = field(default_factory=list)
```

### 4.2 KModel 增强

```python
@dataclass
class KModel:
    # ... existing fields ...
    contacts: list[Contact] = field(default_factory=list)
    boundaries: list[BoundarySPC] = field(default_factory=list)
    loads: list[LoadSegment] = field(default_factory=list)
    curves: list[DefineCurve] = field(default_factory=list)
    set_node_lists: list[SetNodeList] = field(default_factory=list)
    set_segments: list[SetSegment] = field(default_factory=list)
    set_part_lists: list[SetPartList] = field(default_factory=list)
```

### 4.3 生成函数

```python
def _gen_contacts(model: KModel) -> list[str]: ...
def _gen_boundaries(model: KModel) -> list[str]: ...
def _gen_loads(model: KModel) -> list[str]: ...
def _gen_curves(model: KModel) -> list[str]: ...
def _gen_sets(model: KModel) -> list[str]: ...
```

---

## 5. HyperMesh GUI 验证

### 5.1 验证流程

```
1. 检查 hmbatch.exe 存在
2. 启动 HyperMesh GUI (mmain.exe)
3. 等待 GUI 加载 (15s)
4. source listener Tcl (socket 47881)
5. 发送 *readfile model.k
6. 发送 *createmark 查询 Part/Material/Element
7. 发送 *writefile 保存
8. 截图验证
9. 关闭连接
```

### 5.2 验证脚本

```python
def verify_model_in_gui(model_path: str, screenshot_path: str) -> dict:
    """在 HyperMesh GUI 中验证模型"""
    # 1. Generate listener
    save_listener_tcl()
    
    # 2. Launch GUI
    proc = subprocess.Popen([hm_exe])
    
    # 3. Wait for GUI
    time.sleep(15)
    
    # 4. Source listener (manual step - provide instructions)
    
    # 5. Send commands
    result = execute_tcl_gui(f'*readfile "{model_path}"')
    
    # 6. Query model
    result = execute_tcl_gui('*createmark parts 1 "all"\nputs [hm_getmark parts 1]')
    
    # 7. Save
    result = execute_tcl_gui(f'*writefile "{screenshot_path}" 1')
    
    return result
```

---

## 6. ID 冲突检测 + 空集合检测

### 6.1 新增验证函数

```python
def validate_id_conflicts(kfile: KFile) -> list[str]:
    """检测 ID 冲突"""
    errors = []
    # Material IDs
    mat_ids = kfile.get_material_ids()
    # Section IDs
    sec_ids = kfile.get_section_ids()
    # Part IDs
    part_ids = {pid for pid in kfile.get_part_material_refs().keys()}
    # Node IDs
    node_ids = {n for n in kfile.get_nodes()}
    
    # Check for conflicts
    if len(mat_ids) != len(set(mat_ids)):
        errors.append("Duplicate material IDs")
    return errors

def validate_empty_sets(kfile: KFile) -> list[str]:
    """检测空集合"""
    errors = []
    for set_type in ['SET_NODE_LIST', 'SET_SEGMENT', 'SET_PART_LIST']:
        sets = kfile.get_keywords(set_type)
        for s in sets:
            if len(s.data_lines) <= 1:  # Only header
                errors.append(f"Empty {set_type} in {s.name}")
    return errors
```

---

## 7. 统一 logs 目录

```
logs/
├── run/                    # 运行日志
│   ├── dyna_mcp_run.log    # 主运行日志
│   ├── dyna_mcp_error.log  # 错误日志
│   └── dyna_mcp_validation.log  # 验证日志
└── handoff/                # 交接文档
```

---

## 8. 实现顺序

1. **Phase 6.1**: 创建 keyword_fields.py（字段映射表）
2. **Phase 6.2**: 增强 K parser（parsed_fields）
3. **Phase 6.3**: 增强 K writer（新数据类 + 生成函数）
4. **Phase 6.4**: ID 冲突检测 + 空集合检测
5. **Phase 6.5**: HyperMesh GUI 验证
6. **Phase 6.6**: 统一 logs 目录
7. **Phase 6.7**: 测试 + 验证

---

## 9. 验收标准

1. K parser 能解析 model_original.k 中所有关键字的字段
2. K writer 能生成包含 CONTACT/LOAD/BOUNDARY/DEFINE_CURVE/SET 的 K 文件
3. 生成的 K 文件能在 HyperMesh GUI 中打开
4. ID 冲突检测能发现重复 ID
5. 空集合检测能发现空 SET
6. 所有测试通过
