"""K file keyword integration for HyperMesh.

Maps LS-DYNA K file keywords to HyperMesh Tcl commands.
Creates HyperMesh objects that correspond to K file keywords.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.k_parser import parse_k_file, KFile, KKeyword
from program.tools.hm_gui import execute_tcl_gui


@dataclass
class IntegrationResult:
    success: bool
    objects_created: int = 0
    errors: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


# --- K keyword to HyperMesh Tcl mapping ---


def _generate_mat_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *MAT keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    mid = pf.get("MID")
    if mid is None:
        return lines

    mat_type = kw.name.replace("MAT_", "")
    name = f"MAT_{mat_type}_{mid}"

    lines.append(f'*createentity mats name="{name}"')
    lines.append(f'hm_setvalue mats id={mid} STATUS=2 MAT_TYPE={mat_type}')

    if pf.get("RHO") is not None:
        lines.append(f'hm_setvalue mats id={mid} RHO={pf["RHO"]}')
    if pf.get("E") is not None:
        lines.append(f'hm_setvalue mats id={mid} E={pf["E"]}')
    if pf.get("PR") is not None:
        lines.append(f'hm_setvalue mats id={mid} PR={pf["PR"]}')

    return lines


def _generate_section_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *SECTION keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    secid = pf.get("SECID")
    if secid is None:
        return lines

    sec_type = kw.name.replace("SECTION_", "")
    name = f"SECTION_{sec_type}_{secid}"

    lines.append(f'*createentity props name="{name}"')
    lines.append(f'hm_setvalue props id={secid} STATUS=2 SECTION_TYPE={sec_type}')

    if pf.get("ELFORM") is not None:
        lines.append(f'hm_setvalue props id={secid} ELFORM={pf["ELFORM"]}')
    if pf.get("SHRF") is not None:
        lines.append(f'hm_setvalue props id={secid} SHRF={pf["SHRF"]}')
    if pf.get("NIP") is not None:
        lines.append(f'hm_setvalue props id={secid} NIP={pf["NIP"]}')

    return lines


def _generate_part_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *PART keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    pid = pf.get("PID")
    if pid is None:
        return lines

    title = kw.data_lines[0] if kw.data_lines else f"Part_{pid}"
    lines.append(f'*createentity comps name="{title}"')

    secid = pf.get("SECID")
    mid = pf.get("MID")

    if secid is not None:
        lines.append(f'hm_setvalue comps id={pid} STATUS=2 PROPERTYID={secid}')
    if mid is not None:
        lines.append(f'hm_setvalue comps id={pid} STATUS=2 MATERIALID={mid}')

    return lines


def _generate_node_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *NODE keyword."""
    lines = []
    for data_line in kw.data_lines:
        pf = kw.parse_field_values() if not kw.parsed_fields else kw.parsed_fields
        # Parse each line individually
        from program.tools.k_parser import _parse_data_line
        values = _parse_data_line(data_line)
        if len(values) >= 4:
            try:
                nid = int(values[0])
                x = float(values[1])
                y = float(values[2])
                z = float(values[3])
                lines.append(f'*createnode {x} {y} {z} 0 0 0')
            except (ValueError, IndexError):
                pass
    return lines


def _generate_element_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *ELEMENT keyword."""
    lines = []
    for data_line in kw.data_lines:
        from program.tools.k_parser import _parse_data_line
        values = _parse_data_line(data_line)
        if len(values) >= 6:
            try:
                eid = int(values[0])
                pid = int(values[1])
                n1 = int(values[2])
                n2 = int(values[3])
                n3 = int(values[4])
                n4 = int(values[5])

                if "SHELL" in kw.name:
                    lines.append(f'*createmark nodes 1 {n1} {n2} {n3} {n4}')
                    lines.append(f'*element 1 0 {n1} {n2} {n3} {n4}')
                elif "SOLID" in kw.name and len(values) >= 10:
                    n5 = int(values[6])
                    n6 = int(values[7])
                    n7 = int(values[8])
                    n8 = int(values[9])
                    lines.append(f'*createmark nodes 1 {n1} {n2} {n3} {n4} {n5} {n6} {n7} {n8}')
                    lines.append(f'*element 1 0 {n1} {n2} {n3} {n4} {n5} {n6} {n7} {n8}')
            except (ValueError, IndexError):
                pass
    return lines


def _generate_contact_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *CONTACT keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    ssid = pf.get("SSID")
    msid = pf.get("MSID")
    if ssid is None or msid is None:
        return lines

    contact_type = kw.name.replace("CONTACT_", "")
    name = f"CONTACT_{contact_type}_{ssid}_{msid}"

    lines.append(f'*createentity groups name="{name}"')
    lines.append(f'hm_setvalue groups id={ssid} STATUS=2 GROUP_TYPE=CONTACT')
    lines.append(f'hm_setvalue groups id={ssid} CARD_IMAGE={kw.name}')

    if pf.get("FS") is not None:
        lines.append(f'hm_setvalue groups id={ssid} FS={pf["FS"]}')
    if pf.get("FD") is not None:
        lines.append(f'hm_setvalue groups id={ssid} FD={pf["FD"]}')

    return lines


def _generate_boundary_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *BOUNDARY keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    nsid = pf.get("NSID")
    if nsid is None:
        return lines

    bc_type = kw.name.replace("BOUNDARY_", "")
    name = f"BC_{bc_type}_{nsid}"

    lines.append(f'*createentity groups name="{name}"')
    lines.append(f'hm_setvalue groups id={nsid} STATUS=2 GROUP_TYPE=BOUNDARY')
    lines.append(f'hm_setvalue groups id={nsid} CARD_IMAGE={kw.name}')

    for dof in ["DOFX", "DOFY", "DOFZ", "DOFRX", "DOFRY", "DOFRZ"]:
        if pf.get(dof) is not None:
            lines.append(f'hm_setvalue groups id={nsid} {dof}={pf[dof]}')

    return lines


def _generate_load_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *LOAD keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    lcid = pf.get("LCID")
    if lcid is None:
        return lines

    load_type = kw.name.replace("LOAD_", "")
    name = f"LOAD_{load_type}_{lcid}"

    lines.append(f'*createentity groups name="{name}"')
    lines.append(f'hm_setvalue groups id={lcid} STATUS=2 GROUP_TYPE=LOAD')
    lines.append(f'hm_setvalue groups id={lcid} CARD_IMAGE={kw.name}')

    if pf.get("SF") is not None:
        lines.append(f'hm_setvalue groups id={lcid} SF={pf["SF"]}')

    return lines


def _generate_set_tcl(kw: KKeyword) -> list[str]:
    """Generate Tcl commands for *SET keyword."""
    lines = []
    pf = kw.parsed_fields
    if not pf:
        return lines

    sid = pf.get("SID")
    if sid is None:
        return lines

    set_type = kw.name.replace("SET_", "")
    name = f"SET_{set_type}_{sid}"

    lines.append(f'*createentity groups name="{name}"')
    lines.append(f'hm_setvalue groups id={sid} STATUS=2 GROUP_TYPE=SET')
    lines.append(f'hm_setvalue groups id={sid} CARD_IMAGE={kw.name}')

    return lines


# --- Main integration function ---


def integrate_k_file(
    k_file_path: str | Path,
    timeout: int = 30,
    dry_run: bool = True,
) -> IntegrationResult:
    """Integrate a K file into HyperMesh.

    Args:
        k_file_path: Path to .k file
        timeout: Timeout for each Tcl command
        dry_run: If True, only generate commands without executing

    Returns:
        IntegrationResult with success status and details
    """
    result = IntegrationResult(success=True)

    # Parse K file
    try:
        kfile = parse_k_file(k_file_path)
    except Exception as e:
        result.success = False
        result.errors.append(f"Failed to parse K file: {e}")
        return result

    # Validate
    errors = kfile.validate()
    if errors:
        result.warnings.extend(errors)

    # Generate Tcl commands for each keyword
    all_commands: list[str] = []

    # Order: MATERIAL → SECTION → PART → NODE → ELEMENT → SET → BOUNDARY → LOAD → CONTACT
    keyword_order = [
        ("MAT_", _generate_mat_tcl),
        ("SECTION_", _generate_section_tcl),
        ("PART", _generate_part_tcl),
        ("NODE", _generate_node_tcl),
        ("ELEMENT_", _generate_element_tcl),
        ("SET_", _generate_set_tcl),
        ("BOUNDARY_", _generate_boundary_tcl),
        ("LOAD_", _generate_load_tcl),
        ("CONTACT_", _generate_contact_tcl),
    ]

    for prefix, generator in keyword_order:
        for kw in kfile.keywords:
            if kw.name.startswith(prefix) or kw.name == prefix.rstrip("_"):
                commands = generator(kw)
                if commands:
                    all_commands.extend(commands)
                    result.objects_created += 1

    # Execute commands
    if not dry_run:
        for cmd in all_commands:
            r = execute_tcl_gui(cmd, timeout=timeout)
            if not r.get("success"):
                result.errors.append(f"Failed: {cmd[:50]}... → {r.get('error', '')[:100]}")
                # Don't set success=False for non-critical commands
                if "createmark" not in cmd and "element" not in cmd:
                    result.success = False

    return result


def generate_integration_script(k_file_path: str | Path) -> str:
    """Generate a complete Tcl script for K file integration.

    Returns the script as a string (for manual execution or batch mode).
    """
    kfile = parse_k_file(k_file_path)
    all_commands: list[str] = []

    keyword_order = [
        ("MAT_", _generate_mat_tcl),
        ("SECTION_", _generate_section_tcl),
        ("PART", _generate_part_tcl),
        ("NODE", _generate_node_tcl),
        ("ELEMENT_", _generate_element_tcl),
        ("SET_", _generate_set_tcl),
        ("BOUNDARY_", _generate_boundary_tcl),
        ("LOAD_", _generate_load_tcl),
        ("CONTACT_", _generate_contact_tcl),
    ]

    for prefix, generator in keyword_order:
        for kw in kfile.keywords:
            if kw.name.startswith(prefix) or kw.name == prefix.rstrip("_"):
                commands = generator(kw)
                if commands:
                    all_commands.extend(commands)

    return "\n".join(all_commands)
