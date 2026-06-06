# HyperMesh GUI 直接操作实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 Agent 通过 MCP 直接在 HyperMesh GUI 中读写 LS-DYNA 关键字，不需要转 .k 文件。

**Architecture:** Agent → MCP socket → HyperMesh GUI Tcl → LS-DYNA card image。核心问题是 HyperMesh 需要先加载 LS-DYNA solver template 才能读写 card image。

**Tech Stack:** Python MCP server, HyperMesh Tcl API, TCP socket (port 47881)

---

## 发现的关键问题

1. `*feinputwithdata` 设置 solver template 成功（ERR=0）
2. 但已有材料的 `cardimage` 仍为 `<None>` — 模型是用默认模板创建的
3. `*setvalue mats id=1 cardimage=MAT_ELASTIC` 返回 0 但没有生效
4. `hm_getvalue mats id=1 dataname=RHO` 报 "not a valid data name"
5. `hm_getvalue comps id=1 dataname=name` 返回 `Part 1 for Mat 2 and Elem Type 1` 格式

## 根因分析

模型 `test8_daota_lou.hm` 是用 HyperMesh 默认模板（非 LS-DYNA）创建的。材料/属性没有 LS-DYNA card image。需要：
1. 在模型打开前设置 LS-DYNA solver template
2. 或者在模型打开后转换现有材料/属性到 LS-DYNA 格式

## 实现计划

### Task 1: 建立 LS-DYNA solver template 激活流程

**Files:**
- Modify: `program/tools/hm_gui.py`

- [ ] **Step 1: 实现 `activate_lsdyne_template()` 函数**

```python
def activate_lsdyne_template(timeout: int = 15) -> dict:
    """Activate LS-DYNA solver template in HyperMesh.
    
    Must be called before any LS-DYNA card image operations.
    Uses *feinputwithdata to load LS-DYNA template.
    """
    script = '''
    catch {*feinputwithdata {E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key} {} 0 0} err
    puts "TEMPLATE_RESULT=$err"
    '''
    result = send_tcl_to_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
    }
```

- [ ] **Step 2: 测试激活**

Run: `python -c "from program.tools.hm_gui import activate_lsdyne_template; print(activate_lsdyne_template())"`
Expected: `success: True`

- [ ] **Step 3: Commit**

```bash
git add program/tools/hm_gui.py
git commit -m "feat: 新增 activate_lsdyne_template()"
```

### Task 2: 实现材料/属性转换到 LS-DYNA 格式

**Files:**
- Create: `program/tools/hm_model_converter.py`

- [ ] **Step 1: 创建转换模块**

```python
"""Convert HyperMesh model to LS-DYNA format.

Converts existing materials, properties, and sections to LS-DYNA card images.
"""

from __future__ import annotations
from typing import Any
from program.tools.hm_gui import execute_tcl_gui


def convert_materials_to_lsdyne(timeout: int = 30) -> dict:
    """Convert all materials to LS-DYNA card images.
    
    Maps HyperMesh material types to LS-DYNA MAT_* types.
    """
    script = '''
    set converted 0
    set errors 0
    *createmark mats 1 "all"
    foreach mid [hm_getmark mats 1] {
        # Try to set MAT_ELASTIC as default
        if {[catch {*setvalue mats id=$mid cardimage=MAT_ELASTIC} err] == 0} {
            incr converted
        } else {
            incr errors
        }
    }
    puts "CONVERTED=$converted ERRORS=$errors"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
    }


def convert_properties_to_lsdyne(timeout: int = 30) -> dict:
    """Convert all properties to LS-DYNA section card images."""
    script = '''
    set converted 0
    set errors 0
    *createmark props 1 "all"
    foreach pid [hm_getmark props 1] {
        # Try to set SECTION_SOLID as default
        if {[catch {*setvalue props id=$pid cardimage=SECTION_SOLID} err] == 0} {
            incr converted
        } else {
            incr errors
        }
    }
    puts "CONVERTED=$converted ERRORS=$errors"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
    }


def convert_model_to_lsdyne(timeout: int = 60) -> dict:
    """Convert entire model to LS-DYNA format.
    
    1. Activate LS-DYNA template
    2. Convert materials
    3. Convert properties
    """
    from program.tools.hm_gui import activate_lsdyne_template
    
    # Step 1: Activate template
    template_result = activate_lsdyne_template(timeout=timeout)
    if not template_result.get("success"):
        return {"success": False, "error": "Failed to activate LS-DYNA template"}
    
    # Step 2: Convert materials
    mat_result = convert_materials_to_lsdyne(timeout=timeout)
    
    # Step 3: Convert properties
    prop_result = convert_properties_to_lsdyne(timeout=timeout)
    
    return {
        "success": True,
        "template": template_result,
        "materials": mat_result,
        "properties": prop_result,
    }
```

- [ ] **Step 2: 测试转换**

Run: `python -c "from program.tools.hm_model_converter import convert_model_to_lsdyne; print(convert_model_to_lsdyne())"`
Expected: `success: True`

- [ ] **Step 3: Commit**

```bash
git add program/tools/hm_model_converter.py
git commit -m "feat: 新增 hm_model_converter — 模型转换到 LS-DYNA 格式"
```

### Task 3: 实现模型读取（转换后）

**Files:**
- Modify: `program/tools/hm_gui.py`
- Create: `program/tools/hm_model_reader.py`

- [ ] **Step 1: 创建模型读取模块**

```python
"""Read LS-DYNA model data from HyperMesh GUI.

After model is converted to LS-DYNA format, reads material/property/section data.
"""

from __future__ import annotations
from typing import Any
from program.tools.hm_gui import execute_tcl_gui


def read_material(mid: int, timeout: int = 10) -> dict:
    """Read material properties from HyperMesh.
    
    Args:
        mid: Material ID
        
    Returns:
        dict with material properties (cardimage, RHO, E, PR, etc.)
    """
    script = f'''
    set info {{}}
    catch {{dict set info cardimage [hm_getvalue mats id={mid} dataname=cardimage]}}
    catch {{dict set info RHO [hm_getvalue mats id={mid} dataname=RHO]}}
    catch {{dict set info E [hm_getvalue mats id={mid} dataname=E]}}
    catch {{dict set info PR [hm_getvalue mats id={mid} dataname=PR]}}
    puts "MAT_INFO=[array get info]"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    return _parse_mat_response(result, mid)


def read_property(pid: int, timeout: int = 10) -> dict:
    """Read property/section properties from HyperMesh."""
    script = f'''
    set info {{}}
    catch {{dict set info cardimage [hm_getvalue props id={pid} dataname=cardimage]}}
    catch {{dict set info ELFORM [hm_getvalue props id={pid} dataname=ELFORM]}}
    catch {{dict set info SECID [hm_getvalue props id={pid} dataname=SECID]}}
    puts "PROP_INFO=[array get info]"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    return _parse_prop_response(result, pid)


def read_component(cid: int, timeout: int = 10) -> dict:
    """Read component (part) info from HyperMesh."""
    script = f'''
    set info {{}}
    catch {{dict set info name [hm_getvalue comps id={cid} dataname=name]}}
    catch {{dict set info pid [hm_getvalue comps id={cid} dataname=propertyid]}}
    catch {{dict set info mid [hm_getvalue comps id={cid} dataname=materialid]}}
    puts "COMP_INFO=[array get info]"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    return _parse_comp_response(result, cid)


def read_all_materials(timeout: int = 30) -> list[dict]:
    """Read all materials from HyperMesh."""
    script = '''
    *createmark mats 1 "all"
    set ids [hm_getmark mats 1]
    foreach mid $ids {
        set info {}
        catch {dict set info cardimage [hm_getvalue mats id=$mid dataname=cardimage]}
        catch {dict set info RHO [hm_getvalue mats id=$mid dataname=RHO]}
        catch {dict set info E [hm_getvalue mats id=$mid dataname=E]}
        catch {dict set info PR [hm_getvalue mats id=$mid dataname=PR]}
        puts "MAT_$mid=[array get info]"
    }
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    return _parse_mat_list_response(result)


def _parse_mat_response(result: dict, mid: int) -> dict:
    """Parse material query response."""
    if not result.get("success"):
        return {"success": False, "error": result.get("error")}
    
    info = {"success": True, "mid": mid}
    resp = result.get("response", "")
    for line in resp.split("\n"):
        if "MAT_INFO=" in line:
            data = line.split("MAT_INFO=", 1)[1].strip()
            # Parse Tcl dict
            parts = data.split()
            for i in range(0, len(parts) - 1, 2):
                info[parts[i]] = parts[i + 1]
            break
    return info


def _parse_prop_response(result: dict, pid: int) -> dict:
    """Parse property query response."""
    if not result.get("success"):
        return {"success": False, "error": result.get("error")}
    
    info = {"success": True, "pid": pid}
    resp = result.get("response", "")
    for line in resp.split("\n"):
        if "PROP_INFO=" in line:
            data = line.split("PROP_INFO=", 1)[1].strip()
            parts = data.split()
            for i in range(0, len(parts) - 1, 2):
                info[parts[i]] = parts[i + 1]
            break
    return info


def _parse_comp_response(result: dict, cid: int) -> dict:
    """Parse component query response."""
    if not result.get("success"):
        return {"success": False, "error": result.get("error")}
    
    info = {"success": True, "cid": cid}
    resp = result.get("response", "")
    for line in resp.split("\n"):
        if "COMP_INFO=" in line:
            data = line.split("COMP_INFO=", 1)[1].strip()
            parts = data.split()
            for i in range(0, len(parts) - 1, 2):
                info[parts[i]] = parts[i + 1]
            break
    return info


def _parse_mat_list_response(result: dict) -> list[dict]:
    """Parse material list query response."""
    if not result.get("success"):
        return []
    
    materials = []
    resp = result.get("response", "")
    for line in resp.split("\n"):
        if "MAT_" in line and "=" in line:
            parts = line.split("=", 1)
            mid_str = parts[0].replace("MAT_", "").strip()
            try:
                mid = int(mid_str)
            except ValueError:
                continue
            
            info = {"mid": mid}
            data = parts[1].strip()
            dict_parts = data.split()
            for i in range(0, len(dict_parts) - 1, 2):
                info[dict_parts[i]] = dict_parts[i + 1]
            materials.append(info)
    
    return materials
```

- [ ] **Step 2: 测试读取**

Run: `python -c "from program.tools.hm_model_reader import read_all_materials; print(read_all_materials())"`
Expected: List of material dicts

- [ ] **Step 3: Commit**

```bash
git add program/tools/hm_model_reader.py
git commit -m "feat: 新增 hm_model_reader — 读取 LS-DYNA 模型数据"
```

### Task 4: 实现模型写入（设置关键字）

**Files:**
- Create: `program/tools/hm_model_writer.py`

- [ ] **Step 1: 创建模型写入模块**

```python
"""Write LS-DYNA keyword data to HyperMesh GUI.

Sets material, property, section, contact, boundary, load card images.
"""

from __future__ import annotations
from typing import Any
from program.tools.hm_gui import execute_tcl_gui
from program.tools.hm_template_engine import HmTemplateEngine

_engine = HmTemplateEngine()


def set_material(mid: int, mat_type: str, params: dict[str, Any], timeout: int = 15) -> dict:
    """Set material card image and properties.
    
    Args:
        mid: Material ID
        mat_type: LS-DYNA material type (e.g., "MAT_ELASTIC")
        params: Material parameters (e.g., {"RHO": 7.85e-9, "E": 210000, "PR": 0.3})
    """
    # Step 1: Set card image
    script = f'*setvalue mats id={mid} cardimage={mat_type}'
    r1 = execute_tcl_gui(script, timeout=timeout)
    
    # Step 2: Set properties
    props_script = f"*setvalue mats id={mid} STATUS=2\n"
    for key, value in params.items():
        props_script += f"*setvalue mats id={mid} dataname={key} value={value}\n"
    r2 = execute_tcl_gui(props_script, timeout=timeout)
    
    return {
        "success": r1.get("success", False) and r2.get("success", False),
        "mid": mid,
        "mat_type": mat_type,
        "params": params,
    }


def set_property(pid: int, sec_type: str, params: dict[str, Any], timeout: int = 15) -> dict:
    """Set property/section card image and properties."""
    script = f'*setvalue props id={pid} cardimage=SECTION_{sec_type}'
    r1 = execute_tcl_gui(script, timeout=timeout)
    
    props_script = f"*setvalue props id={pid} STATUS=2\n"
    for key, value in params.items():
        props_script += f"*setvalue props id={pid} dataname={key} value={value}\n"
    r2 = execute_tcl_gui(props_script, timeout=timeout)
    
    return {
        "success": r1.get("success", False) and r2.get("success", False),
        "pid": pid,
        "sec_type": sec_type,
        "params": params,
    }


def set_contact(contact_type: str, params: dict[str, Any], timeout: int = 15) -> dict:
    """Create and set contact definition."""
    script = f'*createentity groups name="CONTACT_{contact_type}" cardimage=CONTACT_{contact_type}\n'
    for key, value in params.items():
        script += f"*setvalue groups id=1 dataname={key} value={value}\n"
    
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "contact_type": contact_type,
        "params": params,
    }


def set_boundary(bc_type: str, params: dict[str, Any], timeout: int = 15) -> dict:
    """Create and set boundary condition."""
    script = f'*createentity groups name="BC_{bc_type}" cardimage=BOUNDARY_{bc_type}\n'
    for key, value in params.items():
        script += f"*setvalue groups id=1 dataname={key} value={value}\n"
    
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "bc_type": bc_type,
        "params": params,
    }


def set_load(load_type: str, params: dict[str, Any], timeout: int = 15) -> dict:
    """Create and set load definition."""
    script = f'*createentity groups name="LOAD_{load_type}" cardimage=LOAD_{load_type}\n'
    for key, value in params.items():
        script += f"*setvalue groups id=1 dataname={key} value={value}\n"
    
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "load_type": load_type,
        "params": params,
    }


def set_control(control_type: str, params: dict[str, Any], timeout: int = 15) -> dict:
    """Set control card."""
    script = f'*createentity cards name="{control_type}" cardimage=CONTROL_{control_type}\n'
    for key, value in params.items():
        script += f"*setvalue cards id=1 dataname={key} value={value}\n"
    
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "control_type": control_type,
        "params": params,
    }
```

- [ ] **Step 2: 测试写入**

Run: `python -c "from program.tools.hm_model_writer import set_material; print(set_material(1, 'MAT_ELASTIC', {'RHO': 7.85e-9, 'E': 210000, 'PR': 0.3}))"`
Expected: `success: True`

- [ ] **Step 3: Commit**

```bash
git add program/tools/hm_model_writer.py
git commit -m "feat: 新增 hm_model_writer — 写入 LS-DYNA 关键字"
```

### Task 5: 集成测试 — 完整流程

**Files:**
- Create: `tests/test_hm_model_operations.py`

- [ ] **Step 1: 编写集成测试**

```python
"""Integration tests for HyperMesh model operations."""

import pytest
from program.tools.hm_gui import query_model_info, activate_lsdyne_template
from program.tools.hm_model_converter import convert_model_to_lsdyne
from program.tools.hm_model_reader import read_all_materials, read_material
from program.tools.hm_model_writer import set_material


def test_query_model_info():
    """Test model info query."""
    info = query_model_info()
    assert info.get("connected") is True
    assert info.get("comps_count", 0) > 0


def test_activate_template():
    """Test LS-DYNA template activation."""
    result = activate_lsdyne_template()
    assert result.get("success") is True


def test_convert_model():
    """Test model conversion to LS-DYNA format."""
    result = convert_model_to_lsdyne()
    assert result.get("success") is True


def test_read_materials():
    """Test reading materials after conversion."""
    materials = read_all_materials()
    assert len(materials) > 0


def test_set_material():
    """Test setting material properties."""
    result = set_material(1, "MAT_ELASTIC", {"RHO": 7.85e-9, "E": 210000, "PR": 0.3})
    assert result.get("success") is True
```

- [ ] **Step 2: 运行测试**

Run: `pytest tests/test_hm_model_operations.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_hm_model_operations.py
git commit -m "test: 新增 HyperMesh 模型操作集成测试"
```

---

## 验收标准

1. Agent 可以通过 MCP 查询当前模型信息（components, materials, properties）
2. Agent 可以激活 LS-DYNA solver template
3. Agent 可以转换现有模型到 LS-DYNA 格式
4. Agent 可以读取材料/属性/截面的 card image 数据
5. Agent 可以设置材料/属性/截面/接触/边界/载荷的 card image
6. 所有操作在 HyperMesh GUI 中实时生效
7. 不需要导出 .k 文件

## 已知限制

1. `hm_getvalue comps id=X dataname=name` 返回格式为 `Part 1 for Mat 2 and Elem Type 1`
2. 需要先激活 LS-DYNA solver template 才能读写 card image
3. 现有模型需要转换才能使用 LS-DYNA card image
