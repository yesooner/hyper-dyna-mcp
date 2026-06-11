"""HyperMesh Tcl script safety policy layer.

Generated Tcl can be useful as offline recording/review evidence, but current
MCP execution must still go through verified command-map routes. Unsupported
meshing workflows such as surface automesh and geometry tetmesh are blocked
even when they come from an old MCP generator wrapper.
"""

from __future__ import annotations

from typing import Any


# --- Boundary markers (from hypermesh-mcp) ---

MCP_SCRIPT_BEGIN = "# MCP_SCRIPT_BEGIN"
MCP_SCRIPT_END = "# MCP_SCRIPT_END"

# Trusted generator names — only these can produce scripts with forbidden commands
TRUSTED_MESHING_GENERATORS: set[str] = {
    "generate_surface_automesh_tcl",
    "generate_plain_tetra_tcl",
    "generate_batched_plain_tetra_tcl",
    "generate_gear_tooth_preview_tcl",
    "generate_guarded_drag_hex_tcl",
    "generate_batched_drag_hex_tcl",
    "generate_cutsection_spin_hex_tcl",
}

TRUSTED_NON_MESHING_GENERATORS: set[str] = {
    "generate_phase2_finalize_tcl",
    "generate_finalize_components_tcl",
    "generate_delete_gear_tooth_preview_tcl",
}

TRUSTED_GENERATORS: set[str] = TRUSTED_MESHING_GENERATORS | TRUSTED_NON_MESHING_GENERATORS

# Legacy generators kept for fixture/review compatibility only. They must not
# be treated as permission to execute unverified mesh workflows.
EXECUTION_BLOCKED_GENERATORS: dict[str, str] = {
    "generate_surface_automesh_tcl": "surface_automesh",
    "generate_plain_tetra_tcl": "tetmesh_geometry_solid",
    "generate_batched_plain_tetra_tcl": "tetmesh_geometry_solid",
}

# Commands that are only allowed inside generated-script boundaries
FORBIDDEN_MESHING_COMMANDS: list[str] = [
    "*meshdragelements",
    "*meshspinelements",
    "*set_meshedgeparams",
    "*interactiveremeshedge",
    "*defaultmeshsurf_growth",
    "*interactiveremeshsurf",
    "*automesh",
    "*meshsolidsonly",
    "*tetmesh",
]

FORBIDDEN_COMMAND_ROUTES: dict[str, str] = {
    "*interactiveremeshsurf": "surface_automesh",
    "*automesh": "surface_automesh",
    "*meshsolidsonly": "tetmesh_geometry_solid",
    "*tetmesh": "tetmesh_geometry_solid",
}


# --- Helper functions ---


def _generated_by(script: str) -> str | None:
    """Extract generator name from # MCP_GENERATED_BY= header."""
    for line in script.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# MCP_GENERATED_BY="):
            return stripped.split("=", 1)[1].strip()
    return None


def wrap_generated_tcl(generator_name: str, body: str) -> str:
    """Wrap generated Tcl with boundary markers for policy enforcement."""
    return "\n".join([
        f"# MCP_GENERATED_BY={generator_name}",
        MCP_SCRIPT_BEGIN,
        body,
        MCP_SCRIPT_END,
    ])


def unwrap_generated_tcl(script: str) -> str:
    """Return body inside generated-script markers."""
    text = str(script)
    if MCP_SCRIPT_BEGIN in text and MCP_SCRIPT_END in text:
        return text.split(MCP_SCRIPT_BEGIN, 1)[1].split(MCP_SCRIPT_END, 1)[0].strip()
    return text


# --- Policy enforcement ---


def check_meshing_rules(script: str) -> dict[str, Any] | None:
    """Check if a Tcl script violates meshing safety rules.

    Returns None if the script is allowed, or a dict with violation details.

    Rules:
    - Generated scripts (with MCP_GENERATED_BY header) must have both
      MCP_SCRIPT_BEGIN and MCP_SCRIPT_END markers.
    - Generated scripts must come from a trusted generator.
    - Forbidden meshing commands are only allowed inside generated boundaries.
    - No forbidden commands may appear after the final MCP_SCRIPT_END.
    - Non-generated scripts must not contain any forbidden meshing commands.
    """
    generator_name = _generated_by(script)

    # Strip comments for clean scanning
    clean_lines = []
    for line in script.split("\n"):
        pos = line.find("#")
        if pos >= 0:
            line = line[:pos]
        clean_lines.append(line)
    lowered_clean = "\n".join(clean_lines).lower()

    has_begin = MCP_SCRIPT_BEGIN.lower() in script.lower()
    has_end = MCP_SCRIPT_END.lower() in script.lower()

    # Generated script path
    if generator_name is not None:
        if generator_name not in TRUSTED_GENERATORS:
            return {
                "success": False,
                "policy_violation": True,
                "message": f"Generated Tcl from unknown MCP generator: {generator_name}.",
            }
        if not has_begin or not has_end:
            return {
                "success": False,
                "policy_violation": True,
                "message": "Generated Tcl missing MCP_SCRIPT_BEGIN or MCP_SCRIPT_END markers.",
            }
        # Check after final END
        _, _, after_end = script.lower().rpartition(MCP_SCRIPT_END.lower())
        if any(token in after_end for token in FORBIDDEN_MESHING_COMMANDS):
            return {
                "success": False,
                "policy_violation": True,
                "message": "Forbidden meshing Tcl detected after MCP_SCRIPT_END.",
            }
        blocked_route = EXECUTION_BLOCKED_GENERATORS.get(generator_name)
        if blocked_route and any(token in lowered_clean for token in FORBIDDEN_MESHING_COMMANDS):
            return {
                "success": False,
                "policy_violation": True,
                "error_type": "mesh_route_not_verified",
                "blocked_route_name": blocked_route,
                "generator_name": generator_name,
                "execution_allowed": False,
                "tcl_sent": False,
                "message": (
                    f"Generated Tcl from {generator_name} is offline evidence only. "
                    f"Route {blocked_route} must be promoted through verified MAP "
                    "before execution."
                ),
            }
        return None

    # Non-generated script — forbid all raw meshing commands
    for token in FORBIDDEN_MESHING_COMMANDS:
        if token in lowered_clean:
            route_name = FORBIDDEN_COMMAND_ROUTES.get(token)
            return {
                "success": False,
                "policy_violation": True,
                "error_type": "mesh_route_not_verified",
                "blocked_command": token.lstrip("*"),
                "blocked_route_name": route_name,
                "execution_allowed": False,
                "tcl_sent": False,
                "message": (
                    "Raw meshing Tcl blocked. "
                    + (
                        f"Route {route_name} must be promoted through verified MAP before execution."
                        if route_name else
                        "Use recording_requirements/validate_recording before route promotion."
                    )
                ),
            }

    return None
