"""Read LS-DYNA model data from HyperMesh GUI.

After model is converted to LS-DYNA format, reads material/property/section data.
"""

from __future__ import annotations

from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_gui import execute_tcl_gui


def read_material(mid: int, timeout: int = 10) -> dict[str, Any]:
    """Read material properties from HyperMesh.

    Uses HyperMesh internal datanames:
    - density (not RHO)
    - cardimage (MATL1, MATL96, etc.)
    - E, Nu (standard)
    - SIGY, ETAN (plasticity materials)

    For MATL96 (MAT_024), some fields may return 0 because
    HyperMesh uses different internal names. raw_fields contains
    all queried values for debugging.
    """
    fields = ["cardimage", "density", "Rho", "E", "Nu", "SIGY", "ETAN"]
    info: dict[str, Any] = {"success": True, "mid": mid}
    raw_fields: dict[str, str] = {}

    for fname in fields:
        script = f'puts [hm_getvalue mats id={mid} dataname={fname}]'
        result = execute_tcl_gui(script, timeout=timeout)
        if result.get("success"):
            resp = result.get("response", "")
            for line in resp.split("\n"):
                line = line.strip()
                if line and line != "OK" and line != "ERROR":
                    info[fname] = line
                    raw_fields[fname] = line
                    break

    info["raw_fields"] = raw_fields
    return info


def read_property(pid: int, timeout: int = 10) -> dict[str, Any]:
    """Read property/section properties from HyperMesh."""
    script = f'''
    set info {{}}
    catch {{dict set info cardimage [hm_getvalue props id={pid} dataname=cardimage]}}
    catch {{dict set info ELFORM [hm_getvalue props id={pid} dataname=ELFORM]}}
    catch {{dict set info SECID [hm_getvalue props id={pid} dataname=SECID]}}
    puts "PROP_INFO=[array get info]"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    if not result.get("success"):
        return {"success": False, "pid": pid, "error": result.get("error")}

    info = {"success": True, "pid": pid}
    for line in result.get("response", "").split("\n"):
        if "PROP_INFO=" in line:
            data = line.split("PROP_INFO=", 1)[1].strip()
            parts = data.split()
            for i in range(0, len(parts) - 1, 2):
                info[parts[i]] = parts[i + 1]
            break
    return info


def read_component(cid: int, timeout: int = 10) -> dict[str, Any]:
    """Read component (part) info from HyperMesh."""
    script = f'''
    set info {{}}
    catch {{dict set info name [hm_getvalue comps id={cid} dataname=name]}}
    catch {{dict set info pid [hm_getvalue comps id={cid} dataname=propertyid]}}
    catch {{dict set info mid [hm_getvalue comps id={cid} dataname=materialid]}}
    puts "COMP_INFO=[array get info]"
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    if not result.get("success"):
        return {"success": False, "cid": cid, "error": result.get("error")}

    info = {"success": True, "cid": cid}
    for line in result.get("response", "").split("\n"):
        if "COMP_INFO=" in line:
            data = line.split("COMP_INFO=", 1)[1].strip()
            parts = data.split()
            for i in range(0, len(parts) - 1, 2):
                info[parts[i]] = parts[i + 1]
            break
    return info


def read_all_materials(timeout: int = 30) -> list[dict[str, Any]]:
    """Read all materials from HyperMesh.

    Uses HyperMesh internal datanames: density, Rho, E, Nu, SIGY, ETAN, cardimage.
    """
    script = '''
    *createmark mats 1 "all"
    set ids [hm_getmark mats 1]
    foreach mid $ids {
        set info [list mid $mid]
        catch {lappend info cardimage [hm_getvalue mats id=$mid dataname=cardimage]}
        catch {lappend info density [hm_getvalue mats id=$mid dataname=density]}
        catch {lappend info Rho [hm_getvalue mats id=$mid dataname=Rho]}
        catch {lappend info E [hm_getvalue mats id=$mid dataname=E]}
        catch {lappend info Nu [hm_getvalue mats id=$mid dataname=Nu]}
        catch {lappend info SIGY [hm_getvalue mats id=$mid dataname=SIGY]}
        catch {lappend info ETAN [hm_getvalue mats id=$mid dataname=ETAN]}
        puts "MAT_$mid=$info"
    }
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    if not result.get("success"):
        return []

    materials = []
    for line in result.get("response", "").split("\n"):
        if "MAT_" in line and "=" in line:
            parts = line.split("=", 1)
            mid_str = parts[0].replace("MAT_", "").strip()
            try:
                mid = int(mid_str)
            except ValueError:
                continue

            info: dict[str, Any] = {"mid": mid}
            data = parts[1].strip().strip("{}")
            tokens = data.split()
            i = 0
            while i < len(tokens) - 1:
                key = tokens[i]
                val = tokens[i + 1]
                info[key] = val
                i += 2
            materials.append(info)

    return materials


def _parse_comp_name(raw_name: str) -> dict[str, Any]:
    """Parse HyperMesh auto-generated component name.

    Format: 'Part N for Mat M and Elem Type T'
    Returns dict with part_id, mat_id, elem_type, or raw name.
    """
    import re
    pattern = r"Part\s+(\d+)\s+for\s+Mat\s+(\d+)\s+and\s+Elem\s+Type\s+(\d+)"
    m = re.search(pattern, raw_name)
    if m:
        return {
            "part_id": int(m.group(1)),
            "mat_id": int(m.group(2)),
            "elem_type": int(m.group(3)),
            "raw_name": raw_name.strip(),
        }
    return {"raw_name": raw_name.strip()}


def read_all_components(timeout: int = 30) -> list[dict[str, Any]]:
    """Read all components from HyperMesh."""
    script = '''
    *createmark comps 1 "all"
    set ids [hm_getmark comps 1]
    foreach cid $ids {
        set info [list cid $cid]
        catch {lappend info name [hm_getvalue comps id=$cid dataname=name]}
        catch {lappend info pid [hm_getvalue comps id=$cid dataname=propertyid]}
        catch {lappend info mid [hm_getvalue comps id=$cid dataname=materialid]}
        puts "COMP_$cid=$info"
    }
    '''
    result = execute_tcl_gui(script, timeout=timeout)
    if not result.get("success"):
        return []

    components = []
    for line in result.get("response", "").split("\n"):
        if "COMP_" in line and "=" in line:
            parts = line.split("=", 1)
            cid_str = parts[0].replace("COMP_", "").strip()
            try:
                cid = int(cid_str)
            except ValueError:
                continue

            info: dict[str, Any] = {"cid": cid}
            data = parts[1].strip()
            # Parse key-value pairs, handling {braced values}
            import re
            kv_pattern = r"(\w+)\s+(\{[^}]+\}|\S+)"
            for m in re.finditer(kv_pattern, data):
                key = m.group(1)
                val = m.group(2).strip("{}")
                info[key] = val

            # Parse component name (clean Tcl braces)
            raw_name = info.get("name", "").strip("{}")
            name_info = _parse_comp_name(raw_name)
            info.update(name_info)

            components.append(info)

    return components
