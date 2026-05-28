"""HyperMesh workflow: Probe → Classify → Mesh → Save/Report.

Adapted from times1234/hypermesh-mcp four-phase workflow.
All execution defaults to dry_run=True.
"""

from __future__ import annotations

from typing import Any

from program.tools.hm_runner import run_hmbatch, check_hypermesh_connection
from program.tools.hm_tcl_generator import (
    generate_surface_automesh_tcl,
    generate_solid_mesh_tcl,
    generate_info_tcl,
    generate_save_tcl,
    validate_tcl_script,
)
from program.tools.hm_policy import check_meshing_rules


def probe_model(model_file: str, dry_run: bool = True) -> dict[str, Any]:
    """Phase 1: Probe — collect model info (nodes, elements, components).

    Args:
        model_file: Path to .hm model file.
        dry_run: If True, only generate the command.

    Returns:
        dict with probe results.
    """
    script = generate_info_tcl()
    result = run_hmbatch(
        tcl_script=script,
        model_file=model_file,
        dry_run=dry_run,
    )
    return {
        "phase": "probe",
        "script": script,
        "hmbatch_result": result,
    }


def mesh_surfaces(
    model_file: str,
    element_size: float = 2.0,
    output_file: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Phase 3: Mesh — surface auto-meshing.

    Args:
        model_file: Path to .hm model file.
        element_size: Target element size.
        output_file: Optional path to save after meshing.
        dry_run: If True, only generate the command.

    Returns:
        dict with mesh results.
    """
    script = generate_surface_automesh_tcl(
        element_size=element_size,
        output_hm_path=output_file,
    )

    # Validate script
    validation = validate_tcl_script(script)
    if not validation["valid"]:
        return {"phase": "mesh", "error": "Script validation failed", **validation}

    result = run_hmbatch(
        tcl_script=script,
        model_file=model_file,
        dry_run=dry_run,
    )
    return {
        "phase": "mesh",
        "element_size": element_size,
        "script": script,
        "hmbatch_result": result,
    }


def mesh_solids(
    model_file: str,
    element_size: float = 3.0,
    output_file: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Phase 3: Mesh — solid tetrahedral meshing.

    Args:
        model_file: Path to .hm model file.
        element_size: Target element size.
        output_file: Optional path to save after meshing.
        dry_run: If True, only generate the command.

    Returns:
        dict with mesh results.
    """
    script = generate_solid_mesh_tcl(
        element_size=element_size,
        output_hm_path=output_file,
    )

    validation = validate_tcl_script(script)
    if not validation["valid"]:
        return {"phase": "mesh", "error": "Script validation failed", **validation}

    result = run_hmbatch(
        tcl_script=script,
        model_file=model_file,
        dry_run=dry_run,
    )
    return {
        "phase": "mesh",
        "mesh_type": "solid_tetra",
        "element_size": element_size,
        "script": script,
        "hmbatch_result": result,
    }


def save_model(
    model_file: str,
    output_path: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Phase 4: Save — save the model.

    Args:
        model_file: Path to .hm model file.
        output_path: Path to save the model.
        dry_run: If True, only generate the command.

    Returns:
        dict with save results.
    """
    script = generate_save_tcl(output_path)
    result = run_hmbatch(
        tcl_script=script,
        model_file=model_file,
        dry_run=dry_run,
    )
    return {
        "phase": "save",
        "output_path": output_path,
        "hmbatch_result": result,
    }


def check_connection() -> dict[str, Any]:
    """Check HyperMesh connection availability."""
    return check_hypermesh_connection()
