"""HyperMesh Tcl script generation.

Adapted from times1234/hypermesh-mcp Tcl generation patterns.
All generated scripts are wrapped with MCP_SCRIPT_BEGIN/END markers.
"""

from __future__ import annotations

from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_policy import (
    wrap_generated_tcl,
    check_meshing_rules,
)

# Template directory (fallback mode)
_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "lib" / "tcl_templates"


# --- Tcl helpers (from hypermesh-mcp) ---


def tcl_escape_name(name: str) -> str:
    """Escape a string for safe use as a Tcl literal."""
    s = name.replace("\\", "\\\\")
    s = s.replace("{", "\\{").replace("}", "\\}")
    s = s.replace("[", "\\[").replace("]", "\\]")
    s = s.replace("$", "\\$").replace('"', '\\"')
    return s


def quote_tcl_path(path: str | Path) -> str:
    """Normalize a file path for Tcl (forward slashes, escape quotes)."""
    return str(path).replace("\\", "/").replace('"', '\\"')


# --- Template-based generation (fallback) ---


def generate_tcl(template_name: str, variables: dict[str, str]) -> str:
    """Generate a Tcl script by filling a template file.

    Templates are in lib/tcl_templates/{name}.tcl with {{key}} placeholders.
    Returns the filled script (without MCP markers — caller should wrap).
    """
    template_path = _TEMPLATES_DIR / f"{template_name}.tcl"
    if not template_path.exists():
        raise FileNotFoundError(f"Tcl template not found: {template_path}")

    content = template_path.read_text(encoding="utf-8")
    for key, value in variables.items():
        content = content.replace("{{" + key + "}}", value)

    logger.info(f"Generated Tcl from template: {template_name}")
    return content


# --- String-list generation (from hypermesh-mcp pattern) ---


def generate_surface_automesh_tcl(
    element_size: float,
    output_hm_path: str | None = None,
) -> str:
    """Generate Tcl for surface auto-meshing.

    Args:
        element_size: Target element size.
        output_hm_path: Optional path to save .hm file after meshing.
    """
    lines = [
        "# HyperMesh MCP surface automesh",
        'catch {*beginhistorystate "MCP surface automesh"}',
        '*createmark surfaces 1 "all"',
        f"set elem_size {float(element_size)}",
        "*interactiveremeshsurf 1 $elem_size 2 2 2 1 1",
        "*automesh 0 2 2",
        "*storemeshtodatabase 1",
        "*ameshclearsurface",
        'catch {*endhistorystate "MCP surface automesh"}',
    ]
    if output_hm_path:
        lines.append(f'*writefile "{quote_tcl_path(output_hm_path)}" 1')

    return wrap_generated_tcl("generate_surface_automesh_tcl", "\n".join(lines))


def generate_solid_mesh_tcl(
    element_size: float,
    output_hm_path: str | None = None,
) -> str:
    """Generate Tcl for solid tetrahedral meshing.

    Args:
        element_size: Target element size for tetra mesh.
        output_hm_path: Optional path to save .hm file after meshing.
    """
    lines = [
        "# HyperMesh MCP solid tetra mesh",
        'catch {*beginhistorystate "MCP solid tetra mesh"}',
        '*createmark solids 1 "all"',
        f"set elem_size {float(element_size)}",
        "*meshsolidsonly $elem_size 1",
        'catch {*endhistorystate "MCP solid tetra mesh"}',
    ]
    if output_hm_path:
        lines.append(f'*writefile "{quote_tcl_path(output_hm_path)}" 1')

    return wrap_generated_tcl("generate_plain_tetra_tcl", "\n".join(lines))


def generate_info_tcl() -> str:
    """Generate Tcl to collect model info (nodes, elements, components)."""
    lines = [
        "# HyperMesh MCP model info query",
        '*createmark nodes 1 "all"',
        "set node_count [hm_getmark nodes 1]",
        'puts "MCP_INFO nodes=$node_count"',
        '*createmark elements 1 "all"',
        "set elem_count [hm_getmark elements 1]",
        'puts "MCP_INFO elements=$elem_count"',
        "set comp_count [hm_gettotalcomponents]",
        'puts "MCP_INFO components=$comp_count"',
    ]
    return "\n".join(lines)


def generate_save_tcl(output_path: str) -> str:
    """Generate Tcl to save the current model."""
    return f'*writefile "{quote_tcl_path(output_path)}" 1'


# --- Validation ---


def validate_tcl_script(script: str) -> dict:
    """Validate a Tcl script against meshing safety rules.

    Returns:
        dict with 'valid' key and optional 'error' details.
    """
    violation = check_meshing_rules(script)
    if violation:
        return {"valid": False, **violation}
    return {"valid": True}
