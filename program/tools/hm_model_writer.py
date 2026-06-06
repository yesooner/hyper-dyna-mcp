"""Write LS-DYNA keyword data to HyperMesh GUI.

Provides high-level functions to set materials, properties, contacts,
boundary conditions, loads, control cards, and database cards in the
currently loaded HyperMesh model via the GUI socket listener.

Each function builds a Tcl script using HyperMesh *setvalue / *createentity
commands and sends it through execute_tcl_gui().
"""

from __future__ import annotations

from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_gui import execute_tcl_gui


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


def _execute_script(lines: list[str], timeout: int = 15) -> dict:
    """Join Tcl lines and execute via GUI socket."""
    script = "\n".join(lines)
    if not script.strip():
        return {"success": False, "error": "Empty script"}
    logger.debug(f"hm_model_writer script:\n{script}")
    result = execute_tcl_gui(script, timeout=timeout)
    return result


# ---------------------------------------------------------------------------
# Material
# ---------------------------------------------------------------------------

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
        lines.append(f"*setvalue mats id={mid} dataname={key} value={value}")

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
