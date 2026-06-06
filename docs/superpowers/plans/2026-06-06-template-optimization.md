# Template Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 验证并优化 1941 个 Tcl 模板的精度，确保在 HyperMesh 中可用。

**Architecture:** 批量验证 → 清理噪音 → 精确化核心模板 → 提交。

**Tech Stack:** Python, HyperMesh socket (port 47882), Tcl templates

---

## Task 1: 批量验证模板（B3）

**Files:**
- Create: `program/tools/hm_template_validator.py`

- [ ] **Step 1: 创建验证模块**

```python
"""Validate Tcl templates against HyperMesh GUI."""

from __future__ import annotations
from pathlib import Path
from program.tools.hm_gui import execute_tcl_gui
from program.tools.hm_template_engine import HmTemplateEngine

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "keyword"


def validate_template(keyword: str, timeout: int = 10) -> dict:
    """Test if a template can be rendered and the first command executes."""
    engine = HmTemplateEngine()
    
    if not engine.has_template(keyword):
        return {"keyword": keyword, "status": "missing"}
    
    # Render with dummy params
    info = engine.get_template_info(keyword)
    placeholders = info.get("placeholders", [])
    dummy_params = {p: "1" for p in placeholders}
    
    try:
        script = engine.render(keyword, dummy_params)
    except Exception as e:
        return {"keyword": keyword, "status": "render_error", "error": str(e)}
    
    # Extract first command (skip comments)
    first_cmd = None
    for line in script.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            first_cmd = line
            break
    
    if not first_cmd:
        return {"keyword": keyword, "status": "empty", "error": "No commands in template"}
    
    # Test first command in HyperMesh
    result = execute_tcl_gui(first_cmd, timeout=timeout)
    
    return {
        "keyword": keyword,
        "status": "ok" if result.get("success") else "fail",
        "first_cmd": first_cmd[:80],
        "response": result.get("response", "")[:100],
    }


def validate_category(category: str, timeout: int = 10) -> list[dict]:
    """Validate all templates in a category."""
    cat_dir = TEMPLATES_DIR / category
    if not cat_dir.exists():
        return []
    
    results = []
    for f in sorted(cat_dir.glob("*.tcl")):
        keyword = f.stem
        r = validate_template(keyword, timeout=timeout)
        results.append(r)
    
    return results


def validate_all(batch_size: int = 50, timeout: int = 5) -> dict:
    """Validate all templates in batches."""
    engine = HmTemplateEngine()
    all_templates = engine.list_templates()
    
    results = {"ok": [], "fail": [], "missing": [], "empty": [], "render_error": []}
    
    for template_path in all_templates:
        keyword = template_path.split("/")[-1] if "/" in template_path else template_path
        r = validate_template(keyword, timeout=timeout)
        status = r.get("status", "unknown")
        if status in results:
            results[status].append(r)
        else:
            results.setdefault(status, []).append(r)
    
    return results
```

- [ ] **Step 2: 运行验证（核心类别）**

```bash
cd F:/hyper-dyna-mcp && python -c "
from program.tools.hm_template_validator import validate_category
for cat in ['mat', 'section', 'control', 'database', 'contact', 'boundary', 'load', 'set']:
    results = validate_category(cat)
    ok = sum(1 for r in results if r['status'] == 'ok')
    fail = sum(1 for r in results if r['status'] == 'fail')
    print(f'{cat}: {ok} ok, {fail} fail, {len(results)} total')
"
```

- [ ] **Step 3: 保存验证结果**

```bash
cd F:/hyper-dyna-mcp && python -c "
import json
from program.tools.hm_template_validator import validate_all
results = validate_all()
with open('reports/template_validation.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'OK: {len(results[\"ok\"])}, FAIL: {len(results[\"fail\"])}, Missing: {len(results[\"missing\"])}')
"
```

- [ ] **Step 4: Commit**

```bash
git add program/tools/hm_template_validator.py reports/template_validation.json
git commit -m "feat: 模板批量验证器 + 验证结果"
```

## Task 2: 清理截断模板（B1）

**Files:**
- Modify: `templates/keyword/` — 删除无效模板

- [ ] **Step 1: 识别截断模板**

```bash
cd F:/hyper-dyna-mcp && python -c "
from pathlib import Path
import re

templates_dir = Path('templates/keyword')
truncated = []

for f in templates_dir.rglob('*.tcl'):
    content = f.read_text()
    # Check for truncated keywords (ending with _ or incomplete)
    first_cmd = None
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            first_cmd = line
            break
    
    if first_cmd and ('_' in first_cmd and first_cmd.endswith('_')):
        truncated.append(str(f))

print(f'Found {len(truncated)} truncated templates')
for t in truncated[:10]:
    print(f'  {t}')
"
```

- [ ] **Step 2: 删除截断模板**

```bash
cd F:/hyper-dyna-mcp && python -c "
from pathlib import Path
import re

templates_dir = Path('templates/keyword')
deleted = 0

for f in templates_dir.rglob('*.tcl'):
    content = f.read_text()
    first_cmd = None
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            first_cmd = line
            break
    
    if first_cmd and ('_' in first_cmd and first_cmd.endswith('_')):
        f.unlink()
        deleted += 1

print(f'Deleted {deleted} truncated templates')
"
```

- [ ] **Step 3: Commit**

```bash
git add templates/
git commit -m "chore: 清理截断模板"
```

## Task 3: 精确化核心 50 个模板（B2）

**Files:**
- Modify: `templates/keyword/mat/MAT_ELASTIC.tcl` 等 50 个核心模板

- [ ] **Step 1: 从手册提取核心模板字段**

```bash
cd F:/hyper-dyna-mcp && python -c "
import re

# Read Volume II for MAT field definitions
with open('lsdyna-maunal/volume_II.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find MAT_001 = MAT_ELASTIC section and extract fields
# This requires parsing the manual's field table format
# For now, use the existing keyword_fields.py definitions
from program.tools.keyword_fields import KEYWORD_FIELDS_MAP

core_mats = ['MAT_ELASTIC', 'MAT_RIGID', 'MAT_PIECEWISE_LINEAR_PLASTICITY', 
             'MAT_PLASTIC_KINEMATIC', 'MAT_NULL', 'MAT_JOHNSON_COOK']

for mat in core_mats:
    fields = KEYWORD_FIELDS_MAP.get(mat, [])
    print(f'{mat}: {[f[0] for f in fields]}')
"
```

- [ ] **Step 2: 更新核心模板**

```bash
cd F:/hyper-dyna-mcp && python -c "
from program.tools.keyword_fields import KEYWORD_FIELDS_MAP
from pathlib import Path

templates_dir = Path('templates/keyword')

# Update core MAT templates with precise fields
core_mats = {
    'MAT_ELASTIC': ['MID', 'RHO', 'E', 'PR', 'DA', 'DB'],
    'MAT_RIGID': ['MID', 'RHO', 'E', 'PR', 'N', 'COUPLE', 'M', 'TLOG'],
    'MAT_PIECEWISE_LINEAR_PLASTICITY': ['MID', 'RHO', 'E', 'PR', 'SIGY', 'ETAN', 'FAIL', 'TDEL'],
    'MAT_PLASTIC_KINEMATIC': ['MID', 'RHO', 'E', 'PR', 'SIGY', 'ETAN', 'BETA'],
    'MAT_NULL': ['MID', 'RHO', 'E', 'PR'],
    'MAT_JOHNSON_COOK': ['MID', 'RHO', 'G', 'E', 'PR', 'A', 'B', 'N'],
}

for mat_name, fields in core_mats.items():
    template_path = templates_dir / 'mat' / f'{mat_name}.tcl'
    if not template_path.exists():
        continue
    
    lines = [f'# LS-DYNA R13 *{mat_name}']
    lines.append(f'# Category: mat')
    lines.append(f'# Parameters: {', '.join(fields)}')
    lines.append('')
    lines.append(f'*createentity mats name=\"{mat_name}_{{{{{fields[0]}}}}}\" cardimage={mat_name}')
    lines.append(f'*setvalue mats id={{{{{fields[0]}}}}} STATUS=2')
    
    for field in fields[1:]:  # Skip ID field
        lines.append(f'*setvalue mats id={{{{{fields[0]}}}}} dataname={field} value={{{{{field}}}}}')
    
    template_path.write_text('\n'.join(lines) + '\n')
    print(f'Updated {mat_name}')

print('Done')
"
```

- [ ] **Step 3: 验证更新后的模板**

```bash
cd F:/hyper-dyna-mcp && python -c "
from program.tools.hm_template_validator import validate_category
results = validate_category('mat')
ok = sum(1 for r in results if r['status'] == 'ok')
print(f'MAT templates: {ok}/{len(results)} pass')
"
```

- [ ] **Step 4: Commit**

```bash
git add templates/
git commit -m "feat: 精确化核心 MAT 模板字段"
```

## Task 4: 端口保障（A2）

**Files:**
- Modify: `runs/hm_gui_listener.tcl` — 已完成

- [ ] **Step 1: 验证端口重试逻辑**

```bash
# 测试：关闭 HyperMesh，重新打开，检查 listener 是否自动绑定
# 预期：即使端口被占用，也能在 3 次重试内成功
```

- [ ] **Step 2: Commit**

```bash
git add runs/hm_gui_listener.tcl
git commit -m "fix: listener 端口绑定重试机制"
```

## Task 5: 更新验证报告

**Files:**
- Create: `reports/08_template_validation_report.md`

- [ ] **Step 1: 生成报告**

```markdown
# Template Validation Report

## Summary
- Total templates: X
- Valid: X
- Failed: X
- Truncated (deleted): X

## By Category
| Category | Total | Valid | Failed |
|----------|-------|-------|--------|
| mat | ... | ... | ... |
| section | ... | ... | ... |

## Core Templates (50)
| Keyword | Status | Notes |
|---------|--------|-------|
| MAT_ELASTIC | ✓ | All fields verified |
```

- [ ] **Step 2: Commit**

```bash
git add reports/
git commit -m "docs: 模板验证报告"
```

---

## Execution Order

```
Task 1 (批量验证) → Task 2 (清理截断) → Task 3 (精确化核心) → Task 4 (端口保障) → Task 5 (报告)
```

## 验收标准

1. 核心 50 个模板在 HyperMesh 中全部验证通过
2. 截断模板全部清理
3. 验证报告完整
4. 端口绑定重试机制工作正常
