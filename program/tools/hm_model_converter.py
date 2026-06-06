"""Convert HyperMesh model to LS-DYNA format via GUI.

Iterates all materials and properties in the current HyperMesh model
and sets their card images to LS-DYNA types (MAT_ELASTIC, SECTION_SOLID).

Requires:
  - HyperMesh GUI running with listener on port 47882
  - LS-DYNA solver template already activated (call activate_lsdyne_template first)
"""

from __future__ import annotations

import time
from program.tools.hm_gui import (
    DEFAULT_GUI_HOST,
    DEFAULT_GUI_PORT,
    activate_lsdyne_template,
    execute_tcl_gui,
    send_tcl_to_gui,
)


def check_connection(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Check if HyperMesh GUI listener is connected.

    Returns:
        dict with connected (bool), host, port
    """
    result = send_tcl_to_gui('puts "PING"', host=host, port=port, timeout=5)
    return {
        "connected": result.get("success", False),
        "host": host,
        "port": port,
    }


def get_material_ids(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Get all material IDs from the current model.

    Returns:
        dict with success, material_ids (list of int), count
    """
    script = '''
    *createmark mats 1 "all"
    set ids [hm_getmark mats 1]
    puts "IDS=$ids"
    puts "COUNT=[llength $ids]"
    '''
    result = execute_tcl_gui(script, host=host, port=port, timeout=30)
    if not result.get("success"):
        return {"success": False, "error": result.get("error", result.get("response", ""))}

    resp = result.get("response", "")
    ids = []
    count = 0
    for line in resp.split("\n"):
        line = line.strip()
        if line.startswith("IDS="):
            raw = line[4:].strip("{}")
            ids = [int(x) for x in raw.split() if x.strip().isdigit()]
        elif line.startswith("COUNT="):
            try:
                count = int(line[6:])
            except ValueError:
                pass

    return {"success": True, "material_ids": ids, "count": count}


def get_property_ids(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Get all property IDs from the current model.

    Returns:
        dict with success, property_ids (list of int), count
    """
    script = '''
    *createmark props 1 "all"
    set ids [hm_getmark props 1]
    puts "IDS=$ids"
    puts "COUNT=[llength $ids]"
    '''
    result = execute_tcl_gui(script, host=host, port=port, timeout=30)
    if not result.get("success"):
        return {"success": False, "error": result.get("error", result.get("response", ""))}

    resp = result.get("response", "")
    ids = []
    count = 0
    for line in resp.split("\n"):
        line = line.strip()
        if line.startswith("IDS="):
            raw = line[4:].strip("{}")
            ids = [int(x) for x in raw.split() if x.strip().isdigit()]
        elif line.startswith("COUNT="):
            try:
                count = int(line[6:])
            except ValueError:
                pass

    return {"success": True, "property_ids": ids, "count": count}


def find_lsdyna_template(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> str | None:
    """Try to find the LS-DYNA template file path.

    Returns:
        Template path if found, None otherwise
    """
    # Common LS-DYNA template paths in HyperMesh 2021
    template_paths = [
        "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna/lsyna.key",
        "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/ls-dyna.key",
        "E:/HM2021/2021/hwdesktop/hm/templates/feoutput/lsdyna.key",
    ]

    script = '''
    set found ""
    foreach path {''' + " ".join(f'"{p}"' for p in template_paths) + '''} {
        if {[file exists $path]} {
            set found $path
            break
        }
    }
    puts "TEMPLATE=$found"
    '''
    result = execute_tcl_gui(script, host=host, port=port, timeout=15)
    if not result.get("success"):
        return None

    resp = result.get("response", "")
    for line in resp.split("\n"):
        line = line.strip()
        if line.startswith("TEMPLATE="):
            path = line[9:].strip()
            if path and path != "":
                return path
    return None


def convert_materials_to_lsdyne(
    card_image: str = "MAT_ELASTIC",
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
    timeout: int = 30,
) -> dict:
    """Set card image for all materials in the model.

    Args:
        card_image: LS-DYNA material card image name (default MAT_ELASTIC).

    Returns:
        dict with success, converted count, errors
    """
    mat_result = get_material_ids(host=host, port=port)
    if not mat_result.get("success"):
        return {"success": False, "error": mat_result.get("error", "Failed to get material IDs")}

    mat_ids = mat_result.get("material_ids", [])
    if not mat_ids:
        return {"success": True, "converted": 0, "message": "No materials found"}

    # Build a single script that converts all materials
    # Use *setvalue with proper error handling
    lines = []
    lines.append("set __conv_ok 0")
    lines.append("set __conv_fail 0")
    lines.append("set __conv_errors {}")

    for mid in mat_ids:
        lines.append(f"set __r [catch {{*setvalue mats id={mid} cardimage={card_image}}} __e]")
        lines.append(f"if {{$__r == 0}} {{")
        lines.append(f"    incr __conv_ok")
        lines.append(f"}} else {{")
        lines.append(f"    incr __conv_fail")
        lines.append(f"    lappend __conv_errors \"id={mid}:$__e\"")
        lines.append(f"}}")

    lines.append('puts "OK=$__conv_ok"')
    lines.append('puts "FAIL=$__conv_fail"')
    lines.append('if {[llength $__conv_errors] > 0} { puts "ERRORS=$__conv_errors" }')

    script = "\n".join(lines)
    result = execute_tcl_gui(script, host=host, port=port, timeout=60)

    if not result.get("success"):
        return {"success": False, "error": result.get("error", result.get("response", ""))}

    resp = result.get("response", "")
    ok_count = 0
    fail_count = 0
    errors = []
    for line in resp.split("\n"):
        line = line.strip()
        if line.startswith("OK="):
            try:
                ok_count = int(line[3:])
            except ValueError:
                pass
        elif line.startswith("FAIL="):
            try:
                fail_count = int(line[5:])
            except ValueError:
                pass
        elif line.startswith("ERRORS="):
            errors.append(line[7:])

    return {
        "success": fail_count == 0,
        "converted": ok_count,
        "failed": fail_count,
        "total": len(mat_ids),
        "errors": errors,
    }


def convert_properties_to_lsdyne(
    card_image: str = "SECTION_SOLID",
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
) -> dict:
    """Set card image for all properties in the model.

    Args:
        card_image: LS-DYNA property card image name (default SECTION_SOLID).

    Returns:
        dict with success, converted count, errors
    """
    prop_result = get_property_ids(host=host, port=port)
    if not prop_result.get("success"):
        return {"success": False, "error": prop_result.get("error", "Failed to get property IDs")}

    prop_ids = prop_result.get("property_ids", [])
    if not prop_ids:
        return {"success": True, "converted": 0, "message": "No properties found"}

    # Build a single script that converts all properties
    lines = []
    lines.append("set __conv_ok 0")
    lines.append("set __conv_fail 0")
    lines.append("set __conv_errors {}")

    for pid in prop_ids:
        lines.append(f"set __r [catch {{*setvalue props id={pid} cardimage={card_image}}} __e]")
        lines.append(f"if {{$__r == 0}} {{")
        lines.append(f"    incr __conv_ok")
        lines.append(f"}} else {{")
        lines.append(f"    incr __conv_fail")
        lines.append(f"    lappend __conv_errors \"id={pid}:$__e\"")
        lines.append(f"}}")

    lines.append('puts "OK=$__conv_ok"')
    lines.append('puts "FAIL=$__conv_fail"')
    lines.append('if {[llength $__conv_errors] > 0} { puts "ERRORS=$__conv_errors" }')

    script = "\n".join(lines)
    result = execute_tcl_gui(script, host=host, port=port, timeout=60)

    if not result.get("success"):
        return {"success": False, "error": result.get("error", result.get("response", ""))}

    resp = result.get("response", "")
    ok_count = 0
    fail_count = 0
    errors = []
    for line in resp.split("\n"):
        line = line.strip()
        if line.startswith("OK="):
            try:
                ok_count = int(line[3:])
            except ValueError:
                pass
        elif line.startswith("FAIL="):
            try:
                fail_count = int(line[5:])
            except ValueError:
                pass
        elif line.startswith("ERRORS="):
            errors.append(line[7:])

    return {
        "success": fail_count == 0,
        "converted": ok_count,
        "failed": fail_count,
        "total": len(prop_ids),
        "errors": errors,
    }


def verify_conversion(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Verify that card images are set correctly after conversion.

    Queries all materials and properties to check their cardimage field.

    Returns:
        dict with success, materials_verified, properties_verified
    """
    script = '''
    # Check materials
    *createmark mats 1 "all"
    set mat_ids [hm_getmark mats 1]
    set mat_ok 0
    set mat_fail 0
    set mat_details {}
    foreach mid $mat_ids {
        set r [catch {set ci [hm_getvalue mats id=$mid dataname=cardimage]} e]
        if {$r == 0} {
            if {$ci ne "" && $ci ne "<None>"} {
                incr mat_ok
            } else {
                incr mat_fail
                lappend mat_details "id=$mid:cardimage=$ci"
            }
        } else {
            incr mat_fail
            lappend mat_details "id=$mid:error=$e"
        }
    }
    puts "MAT_OK=$mat_ok"
    puts "MAT_FAIL=$mat_fail"
    if {[llength $mat_details] > 0} { puts "MAT_DETAILS=$mat_details" }

    # Check properties
    *createmark props 1 "all"
    set prop_ids [hm_getmark props 1]
    set prop_ok 0
    set prop_fail 0
    set prop_details {}
    foreach pid $prop_ids {
        set r [catch {set ci [hm_getvalue props id=$pid dataname=cardimage]} e]
        if {$r == 0} {
            if {$ci ne "" && $ci ne "<None>"} {
                incr prop_ok
            } else {
                incr prop_fail
                lappend prop_details "id=$pid:cardimage=$ci"
            }
        } else {
            incr prop_fail
            lappend prop_details "id=$pid:error=$e"
        }
    }
    puts "PROP_OK=$prop_ok"
    puts "PROP_FAIL=$prop_fail"
    if {[llength $prop_details] > 0} { puts "PROP_DETAILS=$prop_details" }
    '''
    result = execute_tcl_gui(script, host=host, port=port, timeout=60)
    if not result.get("success"):
        return {"success": False, "error": result.get("error", result.get("response", ""))}

    resp = result.get("response", "")
    info = {}
    for line in resp.split("\n"):
        line = line.strip()
        for prefix in ("MAT_OK=", "MAT_FAIL=", "PROP_OK=", "PROP_FAIL="):
            if line.startswith(prefix):
                try:
                    info[prefix.rstrip("=").lower()] = int(line[len(prefix):])
                except ValueError:
                    pass

    return {
        "success": True,
        "materials_ok": info.get("mat_ok", 0),
        "materials_fail": info.get("mat_fail", 0),
        "properties_ok": info.get("prop_ok", 0),
        "properties_fail": info.get("prop_fail", 0),
    }


def convert_model_to_lsdyne(
    mat_card: str = "MAT_ELASTIC",
    prop_card: str = "SECTION_SOLID",
    verify: bool = True,
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
) -> dict:
    """Full conversion pipeline: activate LS-DYNA template, convert materials and properties.

    Args:
        mat_card: Material card image type (default MAT_ELASTIC).
        prop_card: Property card image type (default SECTION_SOLID).
        verify: If True, verify card images after conversion.

    Returns:
        dict with success, template, materials, properties, verification
    """
    # Step 0: Check connection
    if not check_connection(host=host, port=port):
        return {
            "success": False,
            "error": "HyperMesh GUI listener not connected. Please source the listener script in HyperMesh.",
        }

    # Step 1: Activate LS-DYNA template
    tpl = activate_lsdyne_template(host=host, port=port)
    if not tpl.get("success"):
        return {
            "success": False,
            "error": "Failed to activate LS-DYNA template",
            "template": tpl,
        }

    # Step 2: Convert materials
    mat = convert_materials_to_lsdyne(card_image=mat_card, host=host, port=port)

    # Step 3: Convert properties
    prop = convert_properties_to_lsdyne(card_image=prop_card, host=host, port=port)

    # Step 4: Verify
    verif = {}
    if verify:
        verif = verify_conversion(host=host, port=port)

    overall = mat.get("success", False) and prop.get("success", False)
    return {
        "success": overall,
        "template": tpl,
        "materials": mat,
        "properties": prop,
        "verification": verif,
    }
