"""Write LS-DYNA keyword data to HyperMesh GUI.

Provides high-level functions to set materials, properties, contacts,
boundary conditions, loads, control cards, and database cards in the
currently loaded HyperMesh model via the GUI socket listener.

Each function builds a Tcl script using HyperMesh *setvalue / *createentity
commands and sends it through execute_tcl_gui().
"""

from __future__ import annotations

import math
import re
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_gui import execute_tcl_gui
from program.tools.hm_command_map import get_route_limits, get_unsupported_route, require_verified_route
from program.tools.hm_policy import wrap_generated_tcl


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_setvalue_lines(
    entity_type: str,
    entity_id: int | None,
    params: dict[str, Any],
    *,
    name: str | None = None,
    create: bool = False,
) -> list[str]:
    """Build a list of Tcl *setvalue lines for an entity.

    Args:
        entity_type: HyperMesh entity type, e.g. "mats", "props", "sects".
        entity_id: Numeric ID. Ignored when *create* is True (entity is newly created).
        params: Field name -> value mapping.
        name: Optional name for *createentity.
        create: If True, emit a *createentity line first.

    Returns:
        List of Tcl command strings (without trailing newlines).
    """
    lines: list[str] = []

    if create:
        name_part = f" name={name}" if name else ""
        card_part = ""
        # For create, params may contain cardimage as a special key
        if "cardimage" in params:
            card_part = f" cardimage={params.pop('cardimage')}"
        lines.append(f"*createentity {entity_type}{name_part}{card_part}")
        # After create, we need to find the new entity's ID to set remaining fields.
        # We rely on the caller providing the ID via *setvalue on the last-created entity.
        id_ref = f"[hm_latestentityid {entity_type}]" if entity_id is None else str(entity_id)
    else:
        id_ref = str(entity_id)

    for key, value in params.items():
        lines.append(f"*setvalue {entity_type} id={id_ref} dataname={key} value={value}")

    return lines


def _execute_script(lines: list[str], timeout: int = 15, batch_size: int = 50, batch_delay: float = 0.5) -> dict:
    """Execute Tcl lines one by one with batching to avoid HyperMesh crashes.

    HyperMesh can segfault when too many commands are sent rapidly.
    This function:
    - Sends each command individually
    - Pauses between commands (50ms)
    - Pauses longer between batches (batch_delay)
    - Detects connection loss and reports it

    Args:
        lines: Tcl command lines
        timeout: Per-command timeout
        batch_size: Commands per batch before longer pause
        batch_delay: Pause between batches in seconds
    """
    import time
    if not lines:
        return {"success": False, "error": "Empty script"}

    last_result = {"success": True}
    count = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        logger.debug(f"hm_model_writer: {line}")
        result = execute_tcl_gui(line, timeout=timeout)
        count += 1

        if not result.get("success"):
            # Check if this is a connection error (segfault recovery)
            if "connection" in str(result.get("error", "")).lower() or \
               "refused" in str(result.get("error", "")).lower():
                logger.error(f"Connection lost after {count} commands — HyperMesh may have crashed")
                return {"success": False, "error": "HyperMesh connection lost (possible segfault)",
                        "commands_executed": count}
            logger.warning(f"Command failed: {line[:60]} → {result.get('response', '')[:100]}")
            last_result = result

        # Throttle: small delay between commands, longer delay between batches
        if count % batch_size == 0:
            logger.info(f"Batch boundary at {count} commands, pausing {batch_delay}s...")
            time.sleep(batch_delay)
        else:
            time.sleep(0.05)  # 50ms between individual commands

    return last_result


# ---------------------------------------------------------------------------
# Material
# ---------------------------------------------------------------------------

# LS-DYNA field name → HyperMesh dataname mapping
# Different material types use different internal names
_MATERIAL_FIELD_MAP = {
    # Common fields
    "RHO": "density",
    "E": "E",
    "PR": "Nu",
    # MAT_ELASTIC specific
    "DA": "DA",
    "DB": "DB",
    # MAT_PIECEWISE_LINEAR_PLASTICITY specific
    "SIGY": "SIGY",
    "ETAN": "ETAN",
    "FAIL": "FAIL",
    "TDEL": "TDEL",
    # MAT_RIGID specific
    "N": "N",
    "COUPLE": "COUPLE",
    # MAT_JOHNSON_COOK specific
    "G": "G",
    "A": "A",
    "B": "B",
}


def _map_field_name(lsdyna_name: str) -> str:
    """Map LS-DYNA field name to HyperMesh dataname."""
    return _MATERIAL_FIELD_MAP.get(lsdyna_name, lsdyna_name)


def set_material(
    mid: int,
    mat_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Set or update a material card in HyperMesh.

    Args:
        mid: Material ID.
        mat_type: LS-DYNA material cardimage, e.g. "MAT_ELASTIC", "MATL24".
        params: Field values, e.g. {"RHO": 7.85e-9, "E": 210000, "PR": 0.3}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, mid, mat_type, response.
    """
    lines = [
        f"*setvalue mats id={mid} cardimage={mat_type}",
        f"*setvalue mats id={mid} STATUS=2",
    ]
    for key, value in params.items():
        hm_name = _map_field_name(key)
        lines.append(f"*setvalue mats id={mid} dataname={hm_name} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "mid": mid,
        "mat_type": mat_type,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


def create_material(
    name: str,
    mat_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Create a new material card in HyperMesh.

    Args:
        name: Material name.
        mat_type: LS-DYNA material cardimage, e.g. "MAT_ELASTIC".
        params: Field values to set after creation.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, name, mat_type, new_id (parsed from response), response.
    """
    lines = [
        f"*createentity mats name={name} cardimage={mat_type}",
    ]
    # Set STATUS=2 to mark card as populated
    lines.append(f"*setvalue mats name={name} STATUS=2")
    for key, value in params.items():
        lines.append(f"*setvalue mats name={name} dataname={key} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "name": name,
        "mat_type": mat_type,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Property / Section
# ---------------------------------------------------------------------------

def set_property(
    pid: int,
    sec_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Set or update a property (section) card in HyperMesh.

    Args:
        pid: Property ID.
        sec_type: LS-DYNA section cardimage, e.g. "SECTION_SHELL", "SECTION_SOLID".
        params: Field values, e.g. {"ELFORM": 2, "SHRF": 0.833, "NIP": 3}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, pid, sec_type, response.
    """
    # For properties, HyperMesh uses 'props' entity type
    # and 'sects' for section cards attached to props.
    lines = [
        f"*setvalue props id={pid} cardimage={sec_type}",
        f"*setvalue props id={pid} STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue props id={pid} dataname={key} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "pid": pid,
        "sec_type": sec_type,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


def create_property(
    name: str,
    sec_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Create a new property (section) card in HyperMesh.

    Args:
        name: Property name.
        sec_type: LS-DYNA section cardimage.
        params: Field values to set after creation.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, name, sec_type, response.
    """
    lines = [
        f"*createentity props name={name} cardimage={sec_type}",
        f"*setvalue props name={name} STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue props name={name} dataname={key} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "name": name,
        "sec_type": sec_type,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

# Contact type -> HyperMesh cardimage mapping
CONTACT_CARD_MAP: dict[str, str] = {
    "AUTOMATIC_SURFACE_TO_SURFACE": "CONTACT_AUTOMATIC_SURFACE_TO_SURFACE",
    "AUTOMATIC_SINGLE_SURFACE": "CONTACT_AUTOMATIC_SINGLE_SURFACE",
    "TIED_SURFACE_TO_SURFACE": "CONTACT_TIED_SURFACE_TO_SURFACE",
    "NODES_TO_SURFACE": "CONTACT_NODES_TO_SURFACE",
    "ERODING_SURFACE_TO_SURFACE": "CONTACT_ERODING_SURFACE_TO_SURFACE",
    "ERODING_SINGLE_SURFACE": "CONTACT_ERODING_SINGLE_SURFACE",
    "AUTOMATIC_GENERAL": "CONTACT_AUTOMATIC_GENERAL",
}


def set_contact(
    contact_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Create or update a contact definition in HyperMesh.

    In HyperMesh, contacts are represented as 'groups' entity type
    with the appropriate LS-DYNA cardimage.

    Args:
        contact_type: Contact keyword type, e.g. "AUTOMATIC_SURFACE_TO_SURFACE".
        params: Field values, e.g. {"SSID": 1, "MSID": 2, "FS": 0.2, "FD": 0.2}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, contact_type, response.
    """
    cardimage = CONTACT_CARD_MAP.get(contact_type, contact_type)
    # If user passes full keyword name like "CONTACT_AUTOMATIC_SURFACE_TO_SURFACE", use as-is
    if not cardimage.startswith("CONTACT_"):
        cardimage = f"CONTACT_{cardimage}"

    # Contacts are typically created as groups in HyperMesh
    name = params.pop("NAME", cardimage)
    lines = [
        f"*createentity groups name={name} cardimage={cardimage}",
        f"*setvalue groups name={name} STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue groups name={name} dataname={key} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "contact_type": contact_type,
        "cardimage": cardimage,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Boundary Condition
# ---------------------------------------------------------------------------

BOUNDARY_CARD_MAP: dict[str, str] = {
    "SPC": "BOUNDARY_SPC",
    "SPC_SET": "BOUNDARY_SPC_SET",
    "PRESCRIBED_MOTION": "BOUNDARY_PRESCRIBED_MOTION_SET",
    "PRESCRIBED_MOTION_NODE": "BOUNDARY_PRESCRIBED_MOTION_NODE",
}


def set_boundary(
    bc_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Set boundary conditions in HyperMesh.

    Boundary conditions are represented as 'loads' entity type in HyperMesh.

    Args:
        bc_type: Boundary condition type, e.g. "SPC", "SPC_SET",
                 "PRESCRIBED_MOTION".
        params: Field values, e.g. {"NSID": 1, "DOFX": 1, "DOFY": 1, "DOFZ": 1}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, bc_type, response.
    """
    cardimage = BOUNDARY_CARD_MAP.get(bc_type, bc_type)
    if not cardimage.startswith("BOUNDARY_"):
        cardimage = f"BOUNDARY_{cardimage}"

    # Boundary conditions are loadcol entities in HyperMesh
    name = params.pop("NAME", cardimage)
    lines = [
        f"*createentity loadcols name={name} cardimage={cardimage}",
        f"*setvalue loadcols name={name} STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue loadcols name={name} dataname={key} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "bc_type": bc_type,
        "cardimage": cardimage,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

LOAD_CARD_MAP: dict[str, str] = {
    "NODE": "LOAD_NODE",
    "SEGMENT": "LOAD_SEGMENT",
    "SHELL": "LOAD_SHELL",
    "BODY": "LOAD_BODY",
    "PRESCRIBED_MOTION": "LOAD_PRESCRIBED_MOTION_SET",
    "RIGID_BODY": "LOAD_RIGID_BODY",
}


def set_load(
    load_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Set loads in HyperMesh.

    Loads are represented as 'loadcols' entity type in HyperMesh.

    Args:
        load_type: Load type, e.g. "NODE", "SEGMENT", "BODY".
        params: Field values, e.g. {"LCID": 1, "SF": 1.0, "DOF": 2}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, load_type, response.
    """
    cardimage = LOAD_CARD_MAP.get(load_type, load_type)
    if not cardimage.startswith("LOAD_"):
        cardimage = f"LOAD_{cardimage}"

    name = params.pop("NAME", cardimage)
    lines = [
        f"*createentity loadcols name={name} cardimage={cardimage}",
        f"*setvalue loadcols name={name} STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue loadcols name={name} dataname={key} value={value}")

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "load_type": load_type,
        "cardimage": cardimage,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Control Card
# ---------------------------------------------------------------------------

CONTROL_CARD_MAP: dict[str, str] = {
    "TERMINATION": "Termin",
    "TIMESTEP": "Timestep",
    "HOURGLASS": "Hourglass",
    "CONTACT": "Contact",
    "ACCURACY": "Accuracy",
    "ENERGY": "Energy",
    "SHELL": "Shell",
}


def set_control(
    control_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Set control cards in HyperMesh.

    Control cards are global cards. In HyperMesh they are set via
    *setvalue on the 'cards' entity type with the profile-specific cardimage.

    Args:
        control_type: Control card type, e.g. "TERMINATION", "TIMESTEP".
        params: Field values, e.g. {"ENDTIM": 0.01, "DTMIN": 0.001}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, control_type, response.
    """
    cardimage = CONTROL_CARD_MAP.get(control_type, control_type)

    # Control cards are cards entities in HyperMesh with profile-specific cardimage
    lines = [
        f"*createentity cards name=CONTROL_{control_type} cardimage={cardimage}",
        f"*createmark cards 1 \"by name\" \"CONTROL_{control_type}\"",
        "set _ctrl_ids [hm_getmark cards 1]",
        "set _ctrl_id [lindex $_ctrl_ids end]",
        f"*setvalue cards id=$_ctrl_id STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue cards id=$_ctrl_id dataname={key} value={value}")
    lines.append(f'puts "HM_CONTROL_CREATED type={control_type} id=$_ctrl_id"')

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "control_type": control_type,
        "cardimage": cardimage,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Database Card
# ---------------------------------------------------------------------------

DATABASE_CARD_MAP: dict[str, str] = {
    "BINARY_D3PLOT": "DBplot",
    "D3PLOT": "DBplot",
    "GLSTAT": "DBglst",
    "MATSUM": "DBmats",
    "SLEOUT": "DBsleo",
    "ELOUT": "DBelou",
    "RCFORC": "DBrcfo",
    "ABSTAT": "DBabst",
    "JNTFORC": "DBjntf",
    "BINARY_D3THDT": "DBthdt",
    "BINARY_D3DUMP": "DBdump",
}


def set_database(
    db_type: str,
    params: dict[str, Any],
    timeout: int = 15,
) -> dict:
    """Set database output cards in HyperMesh.

    Database cards control LS-DYNA output intervals and formats.
    They are cards entities similar to control cards.

    Args:
        db_type: Database card type, e.g. "D3PLOT", "GLSTAT", "MATSUM".
        params: Field values, e.g. {"DT": 1e-3}.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, db_type, response.
    """
    cardimage = DATABASE_CARD_MAP.get(db_type, db_type)

    # Database cards are cards entities in HyperMesh with profile-specific cardimage
    full_name = db_type if db_type.startswith("DATABASE_") else f"DATABASE_{db_type}"
    lines = [
        f"*createentity cards name={full_name} cardimage={cardimage}",
        f"*createmark cards 1 \"by name\" \"{full_name}\"",
        "set _db_ids [hm_getmark cards 1]",
        "set _db_id [lindex $_db_ids end]",
        f"*setvalue cards id=$_db_id STATUS=2",
    ]
    for key, value in params.items():
        lines.append(f"*setvalue cards id=$_db_id dataname={key} value={value}")
    lines.append(f'puts "HM_DATABASE_CREATED type={db_type} id=$_db_id"')

    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "db_type": db_type,
        "cardimage": cardimage,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Convenience: batch set multiple entities
# ---------------------------------------------------------------------------

def set_materials(
    materials: list[dict[str, Any]],
    timeout: int = 30,
) -> list[dict]:
    """Set multiple materials at once.

    Args:
        materials: List of dicts, each with keys: mid, mat_type, params.
            e.g. [{"mid": 1, "mat_type": "MAT_ELASTIC", "params": {"RHO": 7.85e-9}}]
        timeout: Socket timeout in seconds (shared for the batch).

    Returns:
        List of result dicts.
    """
    results = []
    for mat in materials:
        r = set_material(
            mid=mat["mid"],
            mat_type=mat["mat_type"],
            params=mat.get("params", {}),
            timeout=timeout,
        )
        results.append(r)
    return results


def set_properties(
    properties: list[dict[str, Any]],
    timeout: int = 30,
) -> list[dict]:
    """Set multiple properties at once.

    Args:
        properties: List of dicts, each with keys: pid, sec_type, params.
        timeout: Socket timeout in seconds.

    Returns:
        List of result dicts.
    """
    results = []
    for prop in properties:
        r = set_property(
            pid=prop["pid"],
            sec_type=prop["sec_type"],
            params=prop.get("params", {}),
            timeout=timeout,
        )
        results.append(r)
    return results


# ---------------------------------------------------------------------------
# Component (part) assignment
# ---------------------------------------------------------------------------

def assign_material_to_component(
    comp_id: int,
    mid: int,
    timeout: int = 15,
) -> dict:
    """Assign a material to a component (part) in HyperMesh.

    Args:
        comp_id: Component ID.
        mid: Material ID to assign.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, comp_id, mid.
    """
    lines = [
        f"*setvalue comps id={comp_id} materialid={mid}",
    ]
    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "comp_id": comp_id,
        "mid": mid,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


def assign_property_to_component(
    comp_id: int,
    pid: int,
    timeout: int = 15,
) -> dict:
    """Assign a property to a component (part) in HyperMesh.

    Args:
        comp_id: Component ID.
        pid: Property ID to assign.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, comp_id, pid.
    """
    lines = [
        f"*setvalue comps id={comp_id} propertyid={pid}",
    ]
    result = _execute_script(lines, timeout=timeout)
    return {
        "success": result.get("success", False),
        "comp_id": comp_id,
        "pid": pid,
        "response": result.get("response", ""),
        "error": result.get("error"),
    }


# ---------------------------------------------------------------------------
# Geometry Creation
# ---------------------------------------------------------------------------


def _safe_tcl_name(name: str) -> str:
    """Return a conservative HyperMesh collector/entity name."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    cleaned = re.sub(r"(?i)mcp", "", cleaned)
    cleaned = re.sub(r"[_.-]{2,}", "_", cleaned).strip("_.-")
    return cleaned or "fe_box"


def _parse_last_int(response: str, key: str) -> int | None:
    value: int | None = None
    prefix = f"{key}="
    for line in response.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            try:
                value = int(line[len(prefix):].strip())
            except ValueError:
                pass
    return value


def _parse_last_value(response: str, key: str) -> str | None:
    value: str | None = None
    prefix = f"{key}="
    for line in response.splitlines():
        line = line.strip()
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
    return value


def _build_structured_hex_box_tcl(
    *,
    comp_name: str,
    x_min: float,
    y_min: float,
    z_min: float,
    x_max: float,
    y_max: float,
    z_max: float,
    nx: int,
    ny: int,
    nz: int,
) -> str:
    """Build Tcl that creates a structured HEX8 FE box using verified HM commands."""
    route = require_verified_route("create_structured_hex8_box")
    element_config = int(route.get("element_config", 208))
    nx = max(1, int(nx))
    ny = max(1, int(ny))
    nz = max(1, int(nz))

    def node_index(i: int, j: int, k: int) -> int:
        return k * (ny + 1) * (nx + 1) + j * (nx + 1) + i

    lines = [
        f'catch {{*collectorcreateonly comps "{comp_name}" "" 7}}',
        f'*currentcollector comps "{comp_name}"',
        "set _hdm_nodes {}",
    ]

    for k in range(nz + 1):
        z = z_min + (z_max - z_min) * k / nz
        for j in range(ny + 1):
            y = y_min + (y_max - y_min) * j / ny
            for i in range(nx + 1):
                x = x_min + (x_max - x_min) * i / nx
                lines.extend([
                    f"*createnode {x:.12g} {y:.12g} {z:.12g} 0 0 0",
                    "lappend _hdm_nodes [hm_latestentityid nodes]",
                ])

    lines.extend(["set _hdm_first_elem 0", "set _hdm_last_elem 0", "set _hdm_elem_count 0"])
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                ids = [
                    node_index(i, j, k),
                    node_index(i + 1, j, k),
                    node_index(i + 1, j + 1, k),
                    node_index(i, j + 1, k),
                    node_index(i, j, k + 1),
                    node_index(i + 1, j, k + 1),
                    node_index(i + 1, j + 1, k + 1),
                    node_index(i, j + 1, k + 1),
                ]
                node_refs = " ".join(f"[lindex $_hdm_nodes {idx}]" for idx in ids)
                lines.extend([
                    f"*createlist nodes 1 {node_refs}",
                    f"*createelement {element_config} 1 1 1",
                    "set _hdm_last_elem [hm_latestentityid elements]",
                    'if {$_hdm_first_elem == 0} { set _hdm_first_elem $_hdm_last_elem }',
                    "incr _hdm_elem_count",
                ])

    lines.extend([
        'puts "NODE_COUNT=[llength $_hdm_nodes]"',
        'puts "ELEM_COUNT=$_hdm_elem_count"',
        'puts "ELEM_FIRST=$_hdm_first_elem"',
        'puts "ELEM_LAST=$_hdm_last_elem"',
        _build_visualization_refresh_tcl(),
    ])
    return "\n".join(lines)


def _build_visualization_refresh_tcl() -> str:
    """Build conservative GUI refresh Tcl for old and 2024-era HyperMesh."""
    return "\n".join(
        [
            "# HDM_VISUAL_REFRESH_BEGIN",
            "proc _hdm_visual_try {name script} {",
            "    if {[catch {uplevel 1 $script} _hdm_visual_err]} {",
            "        puts \"VISUAL_STEP_${name}=error\"",
            "        puts \"VISUAL_STEP_${name}_ERROR=$_hdm_visual_err\"",
            "        return 0",
            "    }",
            "    puts \"VISUAL_STEP_${name}=ok\"",
            "    return 1",
            "}",
            "set _hdm_visual_elements_all -1",
            "set _hdm_visual_nodes_all -1",
            "set _hdm_visual_solids_all -1",
            "set _hdm_visual_surfs_all -1",
            "set _hdm_visual_elements_displayed -1",
            "set _hdm_visual_nodes_displayed -1",
            "set _hdm_visual_solids_displayed -1",
            "set _hdm_visual_surfs_displayed -1",
            "set _hdm_visual_elements_all_method unknown",
            "set _hdm_visual_nodes_all_method unknown",
            "set _hdm_visual_solids_all_method unknown",
            "set _hdm_visual_surfs_all_method unknown",
            "set _hdm_visual_elements_displayed_method unknown",
            "set _hdm_visual_nodes_displayed_method unknown",
            "set _hdm_visual_solids_displayed_method unknown",
            "set _hdm_visual_surfs_displayed_method unknown",
            "if {[catch {set _hdm_visual_elements_all [llength [hm_entitylist elements id]]}]} {",
            "    catch {*createmark elements 1 all}",
            "    if {[catch {set _hdm_visual_elements_all [hm_marklength elements 1]}]} {",
            "        set _hdm_visual_elements_all_method failed",
            "    } else {",
            "        set _hdm_visual_elements_all_method marklength",
            "    }",
            "} else {",
            "    set _hdm_visual_elements_all_method entitylist",
            "}",
            "if {[catch {set _hdm_visual_nodes_all [llength [hm_entitylist nodes id]]}]} {",
            "    catch {*createmark nodes 1 all}",
            "    if {[catch {set _hdm_visual_nodes_all [hm_marklength nodes 1]}]} {",
            "        set _hdm_visual_nodes_all_method failed",
            "    } else {",
            "        set _hdm_visual_nodes_all_method marklength",
            "    }",
            "} else {",
            "    set _hdm_visual_nodes_all_method entitylist",
            "}",
            "if {[catch {set _hdm_visual_solids_all [llength [hm_entitylist solids id]]}]} {",
            "    catch {*createmark solids 1 all}",
            "    if {[catch {set _hdm_visual_solids_all [hm_marklength solids 1]}]} {",
            "        set _hdm_visual_solids_all_method failed",
            "    } else {",
            "        set _hdm_visual_solids_all_method marklength",
            "    }",
            "} else {",
            "    set _hdm_visual_solids_all_method entitylist",
            "}",
            "if {[catch {set _hdm_visual_surfs_all [llength [hm_entitylist surfs id]]}]} {",
            "    catch {*createmark surfs 1 all}",
            "    if {[catch {set _hdm_visual_surfs_all [hm_marklength surfs 1]}]} {",
            "        set _hdm_visual_surfs_all_method failed",
            "    } else {",
            "        set _hdm_visual_surfs_all_method marklength",
            "    }",
            "} else {",
            "    set _hdm_visual_surfs_all_method entitylist",
            "}",
            "_hdm_visual_try mark_elements_displayed_before {*createmark elements 1 displayed}",
            "_hdm_visual_try mark_elements_all {*createmark elements 1 all}",
            "_hdm_visual_try mark_nodes_all {*createmark nodes 1 all}",
            "_hdm_visual_try mark_solids_all {*createmark solids 1 all}",
            "_hdm_visual_try mark_surfs_all {*createmark surfs 1 all}",
            "_hdm_visual_try entitydisplay_components {*entitydisplay components all 1}",
            "_hdm_visual_try entitydisplay_comps {*entitydisplay comps all 1}",
            "_hdm_visual_try entitydisplay_solids {*entitydisplay solids all 1}",
            "_hdm_visual_try entitydisplay_surfs {*entitydisplay surfs all 1}",
            "_hdm_visual_try elementchecksettings_display {*elementchecksettings display 1}",
            "_hdm_visual_try displaycollector_comps {*displaycollectorwithfilter comps all 1 0}",
            "_hdm_visual_try displaycollector_solids {*displaycollectorwithfilter solids all 1 0}",
            "catch {*createmark elements 1 displayed}",
            "if {[catch {set _hdm_visual_elements_displayed [hm_marklength elements 1]}]} {",
            "    set _hdm_visual_elements_displayed_method failed",
            "} else {",
            "    set _hdm_visual_elements_displayed_method marklength_displayed",
            "}",
            "catch {*createmark nodes 1 displayed}",
            "if {[catch {set _hdm_visual_nodes_displayed [hm_marklength nodes 1]}]} {",
            "    set _hdm_visual_nodes_displayed_method failed",
            "} else {",
            "    set _hdm_visual_nodes_displayed_method marklength_displayed",
            "}",
            "catch {*createmark solids 1 displayed}",
            "if {[catch {set _hdm_visual_solids_displayed [hm_marklength solids 1]}]} {",
            "    set _hdm_visual_solids_displayed_method failed",
            "} else {",
            "    set _hdm_visual_solids_displayed_method marklength_displayed",
            "}",
            "catch {*createmark surfs 1 displayed}",
            "if {[catch {set _hdm_visual_surfs_displayed [hm_marklength surfs 1]}]} {",
            "    set _hdm_visual_surfs_displayed_method failed",
            "} else {",
            "    set _hdm_visual_surfs_displayed_method marklength_displayed",
            "}",
            "_hdm_visual_try hm_viewfit {hm_viewfit}",
            "_hdm_visual_try hm_viewfit_all {hm_viewfit all}",
            "_hdm_visual_try viewset_all {*viewset all}",
            "_hdm_visual_try hm_redraw {hm_redraw}",
            "_hdm_visual_try update {update}",
            'puts "VISUAL_ELEMENTS_ALL=$_hdm_visual_elements_all"',
            'puts "VISUAL_NODES_ALL=$_hdm_visual_nodes_all"',
            'puts "VISUAL_SOLIDS_ALL=$_hdm_visual_solids_all"',
            'puts "VISUAL_SURFS_ALL=$_hdm_visual_surfs_all"',
            'puts "VISUAL_ELEMENTS_ALL_METHOD=$_hdm_visual_elements_all_method"',
            'puts "VISUAL_NODES_ALL_METHOD=$_hdm_visual_nodes_all_method"',
            'puts "VISUAL_SOLIDS_ALL_METHOD=$_hdm_visual_solids_all_method"',
            'puts "VISUAL_SURFS_ALL_METHOD=$_hdm_visual_surfs_all_method"',
            'puts "VISUAL_ELEMENTS_DISPLAYED=$_hdm_visual_elements_displayed"',
            'puts "VISUAL_NODES_DISPLAYED=$_hdm_visual_nodes_displayed"',
            'puts "VISUAL_SOLIDS_DISPLAYED=$_hdm_visual_solids_displayed"',
            'puts "VISUAL_SURFS_DISPLAYED=$_hdm_visual_surfs_displayed"',
            'puts "VISUAL_ELEMENTS_DISPLAYED_METHOD=$_hdm_visual_elements_displayed_method"',
            'puts "VISUAL_NODES_DISPLAYED_METHOD=$_hdm_visual_nodes_displayed_method"',
            'puts "VISUAL_SOLIDS_DISPLAYED_METHOD=$_hdm_visual_solids_displayed_method"',
            'puts "VISUAL_SURFS_DISPLAYED_METHOD=$_hdm_visual_surfs_displayed_method"',
            'puts "VISUAL_REFRESH=attempted"',
            "# HDM_VISUAL_REFRESH_END",
        ]
    )


def refresh_visualization(timeout: int = 15) -> dict:
    """Ask the current HyperMesh GUI to redraw and fit visible FE/solid entities."""
    script = _build_visualization_refresh_tcl()
    result = execute_tcl_gui(script, timeout=timeout, mode="safe", enforce_rules=False)
    response = result.get("response", "")
    visual = _parse_visualization_response(response)
    return {
        "success": bool(result.get("success")) and "VISUAL_REFRESH=attempted" in response,
        "response": response,
        **visual,
        "error": result.get("error"),
        "note": "Refresh commands are wrapped in Tcl catch for old HyperMesh compatibility.",
    }


def _parse_visualization_response(response: str) -> dict:
    """Parse visual entity counts emitted by the shared refresh Tcl block."""
    visual_counts = {
        "elements": _parse_last_int(response, "VISUAL_ELEMENTS_ALL"),
        "nodes": _parse_last_int(response, "VISUAL_NODES_ALL"),
        "solids": _parse_last_int(response, "VISUAL_SOLIDS_ALL"),
        "surfaces": _parse_last_int(response, "VISUAL_SURFS_ALL"),
    }
    visual_displayed_counts = {
        "elements": _parse_last_int(response, "VISUAL_ELEMENTS_DISPLAYED"),
        "nodes": _parse_last_int(response, "VISUAL_NODES_DISPLAYED"),
        "solids": _parse_last_int(response, "VISUAL_SOLIDS_DISPLAYED"),
        "surfaces": _parse_last_int(response, "VISUAL_SURFS_DISPLAYED"),
    }
    visual_count_methods = {
        "elements": _parse_last_value(response, "VISUAL_ELEMENTS_ALL_METHOD"),
        "nodes": _parse_last_value(response, "VISUAL_NODES_ALL_METHOD"),
        "solids": _parse_last_value(response, "VISUAL_SOLIDS_ALL_METHOD"),
        "surfaces": _parse_last_value(response, "VISUAL_SURFS_ALL_METHOD"),
    }
    visual_display_count_methods = {
        "elements": _parse_last_value(response, "VISUAL_ELEMENTS_DISPLAYED_METHOD"),
        "nodes": _parse_last_value(response, "VISUAL_NODES_DISPLAYED_METHOD"),
        "solids": _parse_last_value(response, "VISUAL_SOLIDS_DISPLAYED_METHOD"),
        "surfaces": _parse_last_value(response, "VISUAL_SURFS_DISPLAYED_METHOD"),
    }
    visual_steps = _parse_visual_steps(response)
    visibility = _summarize_visibility(visual_counts, visual_displayed_counts)
    refresh_summary = _summarize_visual_refresh(response=response, visual_steps=visual_steps)
    return {
        "visual_counts": visual_counts,
        "visual_displayed_counts": visual_displayed_counts,
        "visual_count_methods": visual_count_methods,
        "visual_display_count_methods": visual_display_count_methods,
        "visibility": visibility,
        "visual_steps": visual_steps,
        **refresh_summary,
        "visual_diagnostics": _build_visual_diagnostics(
            visual_counts=visual_counts,
            visual_displayed_counts=visual_displayed_counts,
            visibility=visibility,
            visual_refresh_ok=refresh_summary["visual_refresh_ok"],
            visual_refresh_reason=refresh_summary["visual_refresh_reason"],
            visual_failed_steps=refresh_summary["visual_failed_steps"],
        ),
    }


def _parse_visual_steps(response: str) -> dict[str, dict[str, str | None]]:
    """Parse per-command visualization diagnostics from Tcl output."""
    steps: dict[str, dict[str, str | None]] = {}
    for line in response.splitlines():
        error_match = re.match(r"^VISUAL_STEP_([A-Za-z0-9_]+)_ERROR=(.*)$", line.strip())
        if error_match:
            name, error = error_match.groups()
            steps.setdefault(name, {"status": None, "error": None})["error"] = error
            continue
        match = re.match(r"^VISUAL_STEP_([A-Za-z0-9_]+)=(.*)$", line.strip())
        if match:
            name, status = match.groups()
            steps.setdefault(name, {"status": None, "error": None})["status"] = status
            continue
    return steps


def _summarize_visual_refresh(
    *,
    response: str,
    visual_steps: dict[str, dict[str, str | None]],
) -> dict:
    """Summarize visualization attempts without treating compatibility probes as fatal."""
    attempted = "VISUAL_REFRESH=attempted" in response
    failed_steps = {
        name: step
        for name, step in visual_steps.items()
        if isinstance(step, dict) and step.get("status") == "error"
    }
    if not attempted:
        reason = "refresh_marker_missing"
    elif failed_steps:
        reason = "visual_step_warnings"
    else:
        reason = "all_visual_steps_ok"
    return {
        "visual_refresh_ok": bool(attempted),
        "visual_refresh_reason": reason,
        "visual_failed_steps": failed_steps,
        "visual_failed_step_count": len(failed_steps),
    }


def _summarize_visibility(
    visual_counts: dict[str, int | None],
    visual_displayed_counts: dict[str, int | None],
) -> dict[str, str]:
    """Classify whether created entity classes appear displayed after refresh."""
    summary: dict[str, str] = {}
    for key in ("elements", "nodes", "solids", "surfaces"):
        total = visual_counts.get(key)
        displayed = visual_displayed_counts.get(key)
        if total is None or total < 0:
            summary[key] = "unknown"
        elif total == 0:
            summary[key] = "absent"
        elif displayed is None or displayed < 0:
            summary[key] = "present_display_unknown"
        elif displayed > 0:
            summary[key] = "displayed"
        else:
            summary[key] = "present_hidden"
    return summary


def _build_visual_diagnostics(
    *,
    visual_counts: dict[str, int | None],
    visual_displayed_counts: dict[str, int | None],
    visibility: dict[str, str],
    visual_refresh_ok: bool,
    visual_refresh_reason: str,
    visual_failed_steps: dict[str, dict[str, str | None]],
) -> list[dict[str, object]]:
    """Build agent-readable diagnostics for FE/solid display problems."""
    diagnostics: list[dict[str, object]] = []
    for entity_type in ("elements", "nodes", "solids", "surfaces"):
        state = visibility.get(entity_type, "unknown")
        total = visual_counts.get(entity_type)
        displayed = visual_displayed_counts.get(entity_type)
        if state == "displayed":
            diagnostics.append(
                {
                    "entity_type": entity_type,
                    "state": state,
                    "severity": "ok",
                    "message": f"{entity_type} are present and displayed.",
                    "total": total,
                    "displayed": displayed,
                }
            )
        elif state == "present_hidden":
            diagnostics.append(
                {
                    "entity_type": entity_type,
                    "state": state,
                    "severity": "warning",
                    "message": f"{entity_type} exist but are not displayed after refresh.",
                    "total": total,
                    "displayed": displayed,
                    "suggested_action": (
                        "Check component/entity display state in HyperMesh and rerun hm_visual_refresh."
                    ),
                }
            )
        elif state == "present_display_unknown":
            diagnostics.append(
                {
                    "entity_type": entity_type,
                    "state": state,
                    "severity": "warning",
                    "message": f"{entity_type} exist, but displayed count could not be confirmed.",
                    "total": total,
                    "displayed": displayed,
                    "suggested_action": (
                        "Use the GUI browser/display controls to confirm visibility, then rerun hm_visual_refresh."
                    ),
                }
            )
        elif state == "unknown":
            diagnostics.append(
                {
                    "entity_type": entity_type,
                    "state": state,
                    "severity": "warning",
                    "message": f"{entity_type} count could not be queried from HyperMesh.",
                    "total": total,
                    "displayed": displayed,
                    "suggested_action": (
                        "Inspect visual_steps for Tcl command compatibility on this HyperMesh version."
                    ),
                }
            )

    if not visual_refresh_ok:
        diagnostics.append(
            {
                "entity_type": "visual_refresh",
                "state": visual_refresh_reason,
                "severity": "warning",
                "message": "Visualization refresh did not report the expected marker.",
                "failed_steps": visual_failed_steps,
                "suggested_action": (
                    "Check listener output and rerun hm_visual_refresh from a connected HyperMesh GUI."
                ),
            }
        )
    elif visual_failed_steps:
        diagnostics.append(
            {
                "entity_type": "visual_refresh",
                "state": visual_refresh_reason,
                "severity": "info",
                "message": "One or more optional visualization compatibility probes failed.",
                "failed_steps": visual_failed_steps,
                "suggested_action": (
                    "Use visual_counts, visual_displayed_counts, and visibility as the hard evidence; "
                    "optional display Tcl can vary across HyperMesh versions."
                ),
            }
        )
    return diagnostics


def _smoke_visual_counts_ok(visual_counts: object) -> tuple[bool, str | None]:
    """Require both FE elements and geometry solids after the smoke build."""
    if not isinstance(visual_counts, dict):
        return False, "visual_counts_missing"
    for key in ("elements", "solids"):
        try:
            value = int(visual_counts.get(key) or 0)
        except (TypeError, ValueError):
            return False, f"{key}_count_invalid"
        if value <= 0:
            return False, f"{key}_count_absent"
    return True, None


def _smoke_visual_display_ok(
    visual_counts: object,
    visual_displayed_counts: object,
    visibility: object,
) -> tuple[bool, str | None]:
    """Require both smoke entity classes to be reported as displayed."""
    counts_ok, counts_reason = _smoke_visual_counts_ok(visual_counts)
    if not counts_ok:
        return False, counts_reason
    if not isinstance(visibility, dict):
        return False, "visibility_missing"
    displayed_counts = visual_displayed_counts if isinstance(visual_displayed_counts, dict) else {}
    for key in ("elements", "solids"):
        state = visibility.get(key)
        if state == "displayed":
            continue
        if key in displayed_counts and displayed_counts.get(key) is not None:
            try:
                displayed = int(displayed_counts.get(key) or 0)
            except (TypeError, ValueError):
                return False, f"{key}_display_count_invalid"
            if displayed > 0:
                continue
        return False, f"{key}_not_displayed"
    return True, None


def run_gui_modeling_smoke(
    *,
    size: float = 10.0,
    element_size: float = 10.0,
    timeout: int = 30,
) -> dict:
    """Create one FE cube and one geometry solid box, then refresh the GUI.

    This is intentionally a GUI-only smoke workflow. It does not touch the
    HyperMesh Python API path, solver export, or LS-DYNA execution.
    """
    if size <= 0:
        return {"success": False, "error": "size must be > 0"}
    if element_size <= 0:
        return {"success": False, "error": "element_size must be > 0"}

    stages: dict[str, dict] = {}
    fe_result = create_fe_cube(
        "gui_smoke_fe",
        size,
        element_size,
        comp_name="gui_smoke_fe",
        timeout=timeout,
    )
    stages["fe_cube"] = fe_result
    if not fe_result.get("success"):
        stages["solid_box"] = {"success": False, "stage": "not_run", "reason": "fe_cube_failed"}
        stages["visual_refresh"] = {"success": False, "stage": "not_run", "reason": "fe_cube_failed"}
        return {
            "success": False,
            "stage": "fe_cube",
            "entity_paths": ["fe_mesh", "geometry_solid"],
            "stages": stages,
            "error": fe_result.get("error") or "FE cube smoke stage failed.",
        }

    solid_result = create_solid_box(
        "gui_smoke_solid",
        size * 1.5,
        0.0,
        0.0,
        size * 2.5,
        size,
        size,
        comp_name="gui_smoke_solid",
        timeout=timeout,
    )
    stages["solid_box"] = solid_result
    if not solid_result.get("success"):
        stages["visual_refresh"] = {"success": False, "stage": "not_run", "reason": "solid_box_failed"}
        return {
            "success": False,
            "stage": "solid_box",
            "entity_paths": ["fe_mesh", "geometry_solid"],
            "stages": stages,
            "error": solid_result.get("error") or "Geometry solid smoke stage failed.",
        }

    refresh_result = refresh_visualization(timeout=timeout)
    stages["visual_refresh"] = refresh_result
    refresh_ok = bool(refresh_result.get("success"))
    visual_counts = refresh_result.get("visual_counts")
    visual_displayed_counts = refresh_result.get("visual_displayed_counts")
    visual_count_methods = refresh_result.get("visual_count_methods")
    visual_display_count_methods = refresh_result.get("visual_display_count_methods")
    visibility = refresh_result.get("visibility")
    visual_steps = refresh_result.get("visual_steps")
    visual_refresh_ok = refresh_result.get("visual_refresh_ok")
    visual_refresh_reason = refresh_result.get("visual_refresh_reason")
    visual_failed_steps = refresh_result.get("visual_failed_steps")
    visual_counts_ok, visual_counts_reason = _smoke_visual_counts_ok(visual_counts)
    visual_display_ok, visual_display_reason = _smoke_visual_display_ok(
        visual_counts,
        visual_displayed_counts,
        visibility,
    )
    ok = refresh_ok and visual_counts_ok and visual_display_ok
    runtime_validation_evidence = _build_runtime_validation_evidence(
        success=ok,
        solid_result=solid_result,
        visual_counts=visual_counts,
        visual_displayed_counts=visual_displayed_counts,
        visual_count_methods=visual_count_methods,
        visual_display_count_methods=visual_display_count_methods,
        visibility=visibility,
        visual_counts_ok=visual_counts_ok,
        visual_display_ok=visual_display_ok,
        visual_refresh_ok=bool(visual_refresh_ok),
        visual_refresh_reason=visual_refresh_reason,
        visual_failed_steps=visual_failed_steps,
    )
    if not refresh_ok:
        error = refresh_result.get("error") or "GUI visual refresh smoke stage failed."
    elif not visual_counts_ok:
        error = "GUI visual refresh did not report both FE elements and geometry solids."
    elif not visual_display_ok:
        error = "GUI visual refresh reported FE/solid entities but display state is hidden or unknown."
    else:
        error = None
    return {
        "success": ok,
        "stage": "complete" if ok else "visual_refresh",
        "entity_paths": ["fe_mesh", "geometry_solid"],
        "visual_counts": visual_counts,
        "visual_displayed_counts": visual_displayed_counts,
        "visual_count_methods": visual_count_methods,
        "visual_display_count_methods": visual_display_count_methods,
        "visibility": visibility,
        "visual_steps": visual_steps,
        "visual_refresh_ok": visual_refresh_ok,
        "visual_refresh_reason": visual_refresh_reason,
        "visual_failed_steps": visual_failed_steps,
        "visual_failed_step_count": refresh_result.get("visual_failed_step_count"),
        "visual_counts_ok": visual_counts_ok,
        "visual_counts_reason": visual_counts_reason,
        "visual_display_ok": visual_display_ok,
        "visual_display_reason": visual_display_reason,
        "runtime_validation_evidence": runtime_validation_evidence,
        "stages": stages,
        "error": error,
    }


def _build_runtime_validation_evidence(
    *,
    success: bool,
    solid_result: dict,
    visual_counts: object,
    visual_displayed_counts: object,
    visual_count_methods: object,
    visual_display_count_methods: object,
    visibility: object,
    visual_counts_ok: bool,
    visual_display_ok: bool,
    visual_refresh_ok: bool,
    visual_refresh_reason: object,
    visual_failed_steps: object,
) -> dict:
    """Build evidence needed before promoting source-verified routes to runtime-validated."""
    return {
        "route_name": "create_geometry_solid_box",
        "verification_level_if_passed": "runtime_validated",
        "runtime_validated": bool(success),
        "criteria": {
            "solid_route_success": bool(solid_result.get("success")),
            "solid_created_count_gt_0": bool((solid_result.get("created_count") or 0) > 0),
            "visual_counts_have_elements_and_solids": bool(visual_counts_ok),
            "visual_display_has_elements_and_solids": bool(visual_display_ok),
            "visual_refresh_steps_have_no_errors": bool(visual_refresh_ok),
        },
        "solid": {
            "solid_id": solid_result.get("solid_id"),
            "solids_before": solid_result.get("solids_before"),
            "solids_after": solid_result.get("solids_after"),
            "solid_count_methods": solid_result.get("solid_count_methods"),
            "created_count": solid_result.get("created_count"),
        },
        "visual_counts": visual_counts if isinstance(visual_counts, dict) else None,
        "visual_displayed_counts": (
            visual_displayed_counts if isinstance(visual_displayed_counts, dict) else None
        ),
        "visual_count_methods": visual_count_methods if isinstance(visual_count_methods, dict) else None,
        "visual_display_count_methods": (
            visual_display_count_methods if isinstance(visual_display_count_methods, dict) else None
        ),
        "visibility": visibility if isinstance(visibility, dict) else None,
        "visual_refresh": {
            "ok": bool(visual_refresh_ok),
            "reason": visual_refresh_reason,
            "failed_steps": visual_failed_steps if isinstance(visual_failed_steps, dict) else {},
        },
        "command_map_update_candidate": {
            "path": "templates/hm_command_map.json",
            "route_name": "create_geometry_solid_box",
            "set": {
                "tested_in_session": True,
            },
            "expected_derived": {
                "runtime_validated": True,
                "verification_level": "runtime_validated",
            },
            "requires": [
                "runtime_validation_evidence.runtime_validated=true",
                "connected HyperMesh GUI smoke succeeded",
                "visual_counts.elements > 0",
                "visual_counts.solids > 0",
                "visibility.elements=displayed",
                "visibility.solids=displayed",
            ],
            "note": (
                "Do not apply automatically during smoke; review the connected GUI evidence "
                "before promoting the route."
            ),
        },
        "promotion_note": (
            "Only promote templates/hm_command_map.json create_geometry_solid_box to "
            "tested_in_session=true after this evidence is produced by a connected HyperMesh GUI."
        ),
    }


def create_solid_box(
    name: str,
    x_min: float, y_min: float, z_min: float,
    x_max: float, y_max: float, z_max: float,
    comp_name: str | None = None,
    timeout: int = 30,
) -> dict:
    """Create a geometry solid box through the verified ``*solidblock`` route."""
    route_name = "create_geometry_solid_box"
    unsupported = get_unsupported_route(route_name)
    if unsupported:
        return {
            "success": False,
            "supported": False,
            "route_name": route_name,
            "name": name,
            "component": _safe_tcl_name(comp_name or name),
            "entity_kind": "geometry_solid",
            "error_type": "unsupported_route",
            "error": unsupported.get("reason", "Geometry solid route is not verified."),
            "verification_required": [
                "Record geometry solid box creation in HyperMesh GUI command recording.",
                "Confirm the Tcl works in HyperMesh 2024 and the target older HyperMesh version.",
                "Verify solids_count increases after execution.",
                "Only then move the route from unsupported_routes to routes with status=verified.",
            ],
        }

    require_verified_route(route_name)
    target_comp = _safe_tcl_name(comp_name or name)
    dimension_error = _solid_box_dimension_error(x_min, y_min, z_min, x_max, y_max, z_max)
    if dimension_error:
        return {
            "success": False,
            "supported": True,
            "route_name": route_name,
            "name": name,
            "component": target_comp,
            "entity_kind": "geometry_solid",
            "error_type": "invalid_geometry_dimensions",
            "error": dimension_error,
        }
    script = _build_solid_box_tcl(
        comp_name=target_comp,
        x_min=x_min,
        y_min=y_min,
        z_min=z_min,
        x_max=x_max,
        y_max=y_max,
        z_max=z_max,
    )
    result = execute_tcl_gui(script, timeout=timeout, mode="safe", enforce_rules=False)
    response = result.get("response", "")
    before = _parse_last_int(response, "SOLIDS_BEFORE")
    after = _parse_last_int(response, "SOLIDS_AFTER")
    before_method = _parse_last_value(response, "SOLIDS_BEFORE_METHOD")
    after_method = _parse_last_value(response, "SOLIDS_AFTER_METHOD")
    solid_id = _parse_last_int(response, "SOLID_ID")
    created_count = None
    if before is not None and after is not None:
        created_count = max(0, after - before)
    visual = _parse_visualization_response(response)
    ok = bool(result.get("success")) and bool(created_count and created_count > 0)
    return {
        "success": ok,
        "supported": True,
        "route_name": route_name,
        "name": name,
        "component": target_comp,
        "entity_kind": "geometry_solid",
        "coords": f"({x_min},{y_min},{z_min}) - ({x_max},{y_max},{z_max})",
        "solid_id": solid_id,
        "solids_before": before,
        "solids_after": after,
        "solids_before_count_method": before_method,
        "solids_after_count_method": after_method,
        "solid_count_methods": {
            "before": before_method,
            "after": after_method,
        },
        "created_count": created_count,
        **visual,
        "response": response,
        "error": None if ok else result.get("error") or "Geometry solid creation did not increase solids_count.",
    }


def _solid_box_dimension_error(
    x_min: float,
    y_min: float,
    z_min: float,
    x_max: float,
    y_max: float,
    z_max: float,
) -> str | None:
    dimensions = {
        "dx": x_max - x_min,
        "dy": y_max - y_min,
        "dz": z_max - z_min,
    }
    invalid = [name for name, value in dimensions.items() if value <= 0]
    if invalid:
        return (
            "Geometry solid box dimensions must be positive before sending Tcl "
            f"to HyperMesh; invalid dimensions: {', '.join(invalid)}."
        )
    return None


def _build_solid_box_tcl(
    *,
    comp_name: str,
    x_min: float,
    y_min: float,
    z_min: float,
    x_max: float,
    y_max: float,
    z_max: float,
) -> str:
    """Build Tcl for an axis-aligned geometry solid box using *solidblock."""
    dx = x_max - x_min
    dy = y_max - y_min
    dz = z_max - z_min
    return "\n".join(
        [
            _build_count_entities_tcl("solids", "_hdm_solids_before"),
            f'catch {{*collectorcreateonly comps "{comp_name}" "" 5}}',
            f'*currentcollector comps "{comp_name}"',
            f"*solidblock {x_min:.12g} {y_min:.12g} {z_min:.12g} {dx:.12g} 0 0 0 {dy:.12g} 0 0 0 {dz:.12g}",
            "set _hdm_solid_id 0",
            "catch {set _hdm_solid_id [hm_latestentityid solids]}",
            _build_count_entities_tcl("solids", "_hdm_solids_after"),
            'puts "SOLIDS_BEFORE=$_hdm_solids_before"',
            'puts "SOLIDS_AFTER=$_hdm_solids_after"',
            'puts "SOLIDS_BEFORE_METHOD=$_hdm_solids_before_method"',
            'puts "SOLIDS_AFTER_METHOD=$_hdm_solids_after_method"',
            'puts "SOLID_ID=$_hdm_solid_id"',
            _build_visualization_refresh_tcl(),
        ]
    )


def _build_count_entities_tcl(entity_type: str, var_name: str) -> str:
    """Build old-HyperMesh-compatible Tcl to count entities."""
    return "\n".join(
        [
            f"set {var_name} -1",
            f"set {var_name}_method unknown",
            f"if {{[catch {{set {var_name} [llength [hm_entitylist {entity_type} id]]}}]}} {{",
            f"    catch {{*createmark {entity_type} 1 all}}",
            f"    if {{[catch {{set {var_name} [hm_marklength {entity_type} 1]}}]}} {{",
            f"        set {var_name}_method failed",
            "    } else {",
            f"        set {var_name}_method marklength",
            "    }",
            "} else {",
            f"    set {var_name}_method entitylist",
            "}",
        ]
    )


def _structured_hex_box_limit_error(nx: int, ny: int, nz: int) -> str | None:
    """Return a clear error if the requested structured box is too large."""
    nx = max(1, int(nx))
    ny = max(1, int(ny))
    nz = max(1, int(nz))
    limits = get_route_limits("create_structured_hex8_box")
    element_count = nx * ny * nz
    node_count = (nx + 1) * (ny + 1) * (nz + 1)
    if element_count > limits["max_elements"]:
        return (
            f"Requested structured HEX8 mesh has {element_count} elements, "
            f"which exceeds the verified route limit of {limits['max_elements']}."
        )
    if node_count > limits["max_nodes"]:
        return (
            f"Requested structured HEX8 mesh has {node_count} nodes, "
            f"which exceeds the verified route limit of {limits['max_nodes']}."
        )
    return None


def _execute_structured_hex_box(
    *,
    name: str,
    x_min: float,
    y_min: float,
    z_min: float,
    x_max: float,
    y_max: float,
    z_max: float,
    comp_name: str | None,
    nx: int,
    ny: int,
    nz: int,
    timeout: int,
) -> dict:
    target_comp = _safe_tcl_name(comp_name or name)
    limit_error = _structured_hex_box_limit_error(nx, ny, nz)
    if limit_error:
        return {
            "success": False,
            "name": name,
            "component": target_comp,
            "divisions": [max(1, int(nx)), max(1, int(ny)), max(1, int(nz))],
            "error": limit_error,
            "error_type": "mesh_size_limit",
        }
    script = _build_structured_hex_box_tcl(
        comp_name=target_comp,
        x_min=x_min,
        y_min=y_min,
        z_min=z_min,
        x_max=x_max,
        y_max=y_max,
        z_max=z_max,
        nx=nx,
        ny=ny,
        nz=nz,
    )
    result = execute_tcl_gui(script, timeout=timeout, mode="safe", enforce_rules=False)
    response = result.get("response", "")
    elem_count = _parse_last_int(response, "ELEM_COUNT")
    node_count = _parse_last_int(response, "NODE_COUNT")
    elem_first = _parse_last_int(response, "ELEM_FIRST")
    elem_last = _parse_last_int(response, "ELEM_LAST")
    visual = _parse_visualization_response(response)
    ok = bool(result.get("success")) and bool(elem_count and elem_count > 0)
    return {
        "success": ok,
        "name": name,
        "component": target_comp,
        "node_count": node_count,
        "element_count": elem_count,
        "first_element_id": elem_first,
        "last_element_id": elem_last,
        "divisions": [nx, ny, nz],
        **visual,
        "response": response,
        "error": None if ok else result.get("error") or "Structured HEX8 creation did not report any elements.",
    }


def create_box(
    name: str,
    x_min: float, y_min: float, z_min: float,
    x_max: float, y_max: float, z_max: float,
    comp_name: str | None = None,
    timeout: int = 30,
) -> dict:
    """Create a one-element HEX8 FE box in HyperMesh.

    This uses HyperMesh commands verified in the local Altair scripts:
    ``*createnode`` + ``*createlist`` + ``*createelement 208``.

    Args:
        name: Name for the solid.
        x_min, y_min, z_min: Minimum corner coordinates.
        x_max, y_max, z_max: Maximum corner coordinates.
        comp_name: Component name to create in (optional, uses current if None).
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, name, coordinates.
    """
    result = _execute_structured_hex_box(
        name=name,
        x_min=x_min,
        y_min=y_min,
        z_min=z_min,
        x_max=x_max,
        y_max=y_max,
        z_max=z_max,
        comp_name=comp_name,
        nx=1,
        ny=1,
        nz=1,
        timeout=timeout,
    )
    return {
        "success": result.get("success", False),
        "name": name,
        "component": result.get("component"),
        "coords": f"({x_min},{y_min},{z_min}) - ({x_max},{y_max},{z_max})",
        "node_count": result.get("node_count"),
        "element_count": result.get("element_count"),
        "first_element_id": result.get("first_element_id"),
        "last_element_id": result.get("last_element_id"),
        "response": result.get("response", ""),
        "error": result.get("error"),
        "next_steps": [
            "Call hm_auto_save(step_name='box_created') to save",
            "Use hm_set_keyword to assign materials, sections, contacts, etc.",
        ],
    }


def mesh_box(
    comp_name: str,
    element_size: float,
    timeout: int = 60,
) -> dict:
    """Mesh the current solid with tetrahedral elements.

    Uses *tetmesh command to create tetrahedral mesh from surfaces.

    Args:
        comp_name: Component name (for setting current collector).
        element_size: Target element size.
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, element count.
    """
    lines = [
        f'*currentcollector comps "{comp_name}"',
        '*createmark solids 1 all',
        '*tetmesh 1 1 %s' % element_size,
    ]

    script = wrap_generated_tcl("generate_plain_tetra_tcl", "\n".join(lines))
    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "comp_name": comp_name,
        "element_size": element_size,
        "response": result.get("response", ""),
        "error": result.get("error"),
        "next_steps": [
            "Call hm_auto_save(step_name='mesh_done') to save",
            "Use hm_set_keyword to assign materials, sections, contacts, etc.",
        ],
    }


def create_fe_cube(
    name: str,
    size: float,
    element_size: float,
    *,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
    origin_z: float = 0.0,
    comp_name: str | None = None,
    timeout: int = 90,
) -> dict:
    """Create a structured HEX8 FE cube in the current HyperMesh GUI session.

    This is a convenience workflow for smoke-testing the MCP modeling path.
    It avoids version-sensitive geometry/tetmesh commands and creates nodes
    plus HEX8 elements directly through verified HyperMesh Tcl commands.
    """
    if size <= 0:
        return {"success": False, "error": "size must be > 0"}
    if element_size <= 0:
        return {"success": False, "error": "element_size must be > 0"}

    divisions = max(1, int(math.ceil(size / element_size)))
    box = _execute_structured_hex_box(
        name=name,
        x_min=origin_x,
        y_min=origin_y,
        z_min=origin_z,
        x_max=origin_x + size,
        y_max=origin_y + size,
        z_max=origin_z + size,
        comp_name=comp_name or name,
        nx=divisions,
        ny=divisions,
        nz=divisions,
        timeout=timeout,
    )
    if not box.get("success"):
        return {
            "success": False,
            "stage": "create_box",
            "box": box,
            "next_steps": ["Ensure HyperMesh listener is sourced, then retry hm_create_fe_cube."],
        }

    return {
        "success": True,
        "stage": "complete",
        "name": name,
        "component": box.get("component"),
        "size": size,
        "element_size": element_size,
        "divisions": [divisions, divisions, divisions],
        "node_count": box.get("node_count"),
        "element_count": box.get("element_count"),
        "first_element_id": box.get("first_element_id"),
        "last_element_id": box.get("last_element_id"),
        "origin": [origin_x, origin_y, origin_z],
        "visual_counts": box.get("visual_counts"),
        "visual_displayed_counts": box.get("visual_displayed_counts"),
        "visual_count_methods": box.get("visual_count_methods"),
        "visual_display_count_methods": box.get("visual_display_count_methods"),
        "visibility": box.get("visibility"),
        "visual_steps": box.get("visual_steps"),
        "visual_diagnostics": box.get("visual_diagnostics"),
        "visual_refresh_ok": box.get("visual_refresh_ok"),
        "visual_refresh_reason": box.get("visual_refresh_reason"),
        "visual_failed_steps": box.get("visual_failed_steps"),
        "visual_failed_step_count": box.get("visual_failed_step_count"),
        "box": box,
        "next_steps": [
            "Call hm_check_model to verify entity counts.",
            "Call hm_auto_save(step_name='fe_cube_done') to save the HyperMesh model.",
        ],
    }
