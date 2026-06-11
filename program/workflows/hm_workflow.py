"""Legacy HyperMesh workflow helpers.

Current MCP scope is HyperMesh GUI-only with verified Tcl routes. Legacy
hmbatch-style helpers may be kept for offline probes/dry-run metadata, but
unverified automesh workflows must remain blocked until command recording and
verified-map promotion.
"""

from __future__ import annotations

from typing import Any

from program.tools.hm_runner import run_hmbatch, check_hypermesh_connection
from program.tools.hm_tcl_generator import (
    generate_info_tcl,
    generate_save_tcl,
)


def _wrap_hmbatch_workflow_result(
    *,
    phase: str,
    hmbatch_result: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "phase": phase,
        "hmbatch_result": hmbatch_result,
    }
    if extra:
        payload.update(extra)
    if hmbatch_result.get("error_type") == "hmbatch_execution_out_of_scope":
        payload.update(
            {
                "status": "blocked",
                "success": False,
                "error_type": hmbatch_result["error_type"],
                "execution_allowed": False,
                "tcl_sent": False,
            }
        )
    else:
        payload["status"] = "dry_run" if hmbatch_result.get("dry_run") is True else "unknown"
    return payload


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
    return _wrap_hmbatch_workflow_result(
        phase="probe",
        hmbatch_result=result,
        extra={"script": script},
    )


def mesh_surfaces(
    model_file: str,
    element_size: float = 2.0,
    output_file: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Block legacy surface auto-meshing workflow.

    Args:
        model_file: Path to .hm model file.
        element_size: Target element size.
        output_file: Optional path to save after meshing.
        dry_run: Ignored. Surface automesh remains blocked in this workflow.

    Returns:
        dict with mesh results.
    """
    return {
        "phase": "mesh",
        "success": False,
        "error_type": "surface_automesh_not_verified",
        "error": "Surface automesh is not executable until command recording and verified-map promotion are complete.",
        "blocked_route_name": "surface_automesh",
        "blocked_route_status": "unsupported",
        "execution_allowed": False,
        "tcl_sent": False,
        "element_size": element_size,
        "model_file": model_file,
        "output_file": output_file,
        "next_supported_actions": [
            {"action": "recording_requirements", "route_name": "surface_automesh"},
            {"action": "validate_recording", "route_name": "surface_automesh"},
        ],
    }


def mesh_solids(
    model_file: str,
    element_size: float = 3.0,
    output_file: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Block legacy solid tetrahedral auto-meshing workflow.

    Args:
        model_file: Path to .hm model file.
        element_size: Target element size.
        output_file: Optional path to save after meshing.
        dry_run: Ignored. Tetmesh remains blocked in this workflow.

    Returns:
        dict with mesh results.
    """
    return {
        "phase": "mesh",
        "success": False,
        "error_type": "tetmesh_geometry_solid_not_verified",
        "error": "Geometry solid tetmesh is not executable until command recording and verified-map promotion are complete.",
        "blocked_route_name": "tetmesh_geometry_solid",
        "blocked_route_status": "unsupported",
        "execution_allowed": False,
        "tcl_sent": False,
        "mesh_type": "solid_tetra",
        "element_size": element_size,
        "model_file": model_file,
        "output_file": output_file,
        "next_supported_actions": [
            {"action": "recording_requirements", "route_name": "tetmesh_geometry_solid"},
            {"action": "validate_recording", "route_name": "tetmesh_geometry_solid"},
        ],
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
    return _wrap_hmbatch_workflow_result(
        phase="save",
        hmbatch_result=result,
        extra={"output_path": output_path},
    )


def check_connection() -> dict[str, Any]:
    """Check HyperMesh connection availability."""
    return check_hypermesh_connection()
