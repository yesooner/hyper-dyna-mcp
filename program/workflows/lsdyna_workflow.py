"""Offline LS-DYNA fixture workflow.

Current MCP scope is HyperMesh GUI-only. This module may parse/generate
fixture data and dry-run command metadata for tests, but it must not report
solver execution as completed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from program.tools.k_parser import parse_k_file, KFile
from program.tools.k_writer import KModel, write_k_file, generate_k_content
from program.tools.lsdyna_runner import run_lsdyna


def parse_and_validate(filepath: str | Path) -> dict[str, Any]:
    """Parse a .k file and run validation checks.

    Returns:
        dict with parsed KFile summary and validation errors.
    """
    kfile = parse_k_file(filepath)
    errors = kfile.validate()

    return {
        "filepath": str(filepath),
        "title": kfile.title,
        "n_keywords": len(kfile.keywords),
        "n_parts": len(kfile.get_parts()),
        "n_materials": len(kfile.get_materials()),
        "n_sections": len(kfile.get_sections()),
        "n_nodes": len(kfile.get_nodes()),
        "n_elements": len(kfile.get_elements()),
        "material_ids": sorted(kfile.get_material_ids()),
        "part_material_refs": kfile.get_part_material_refs(),
        "errors": errors,
        "valid": len(errors) == 0,
    }


def generate_and_write(
    model: KModel,
    output_path: str | Path,
) -> dict[str, Any]:
    """Generate a fixture .k file from KModel and write to disk.

    This is repository fixture/review behavior only. It does not authorize
    backend K writing as MCP modeling or final export.

    Returns:
        dict with generation summary.
    """
    content = write_k_file(model, output_path)
    return {
        "output_path": str(output_path),
        "n_bytes": len(content),
        "n_materials": len(model.materials),
        "n_parts": len(model.parts),
        "n_nodes": len(model.nodes),
        "n_elements": (
            len(model.solid_elements)
            + len(model.shell_elements)
            + len(model.beam_elements)
        ),
        "success": True,
        "offline_fixture_only": True,
        "mcp_execution_allowed": False,
        "final_k_export_allowed": False,
        "agent_execution_allowed": False,
    }


def solve(
    input_file: str | Path,
    dry_run: bool = True,
    ncpus: int | None = None,
    memory: str | None = None,
) -> dict[str, Any]:
    """Generate solver command metadata.

    Returns:
        dict with solver command metadata or blocked execution status.
    """
    result = run_lsdyna(
        input_file=str(input_file),
        dry_run=dry_run,
        ncpus=ncpus,
        memory=memory,
    )
    return result


def full_pipeline(
    input_file: str | Path,
    output_file: str | Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Run the offline LS-DYNA fixture pipeline: parse → validate → plan solve.

    Args:
        input_file: Path to existing .k file to parse and solve.
        output_file: Optional path to write a modified .k file.
        dry_run: If True, only generate commands without executing. If False,
            solver execution remains blocked by project scope.

    Returns:
        dict with pipeline results.
    """
    results: dict[str, Any] = {}

    # Step 1: Parse and validate
    parse_result = parse_and_validate(input_file)
    results["parse"] = parse_result

    if not parse_result["valid"]:
        results["status"] = "validation_failed"
        results["errors"] = parse_result["errors"]
        return results

    # Step 2: Solve
    solve_result = solve(input_file, dry_run=dry_run)
    results["solve"] = solve_result
    if solve_result.get("error_type") == "lsdyna_solver_execution_out_of_scope":
        results["status"] = "blocked"
        results["error_type"] = solve_result["error_type"]
        results["execution_allowed"] = False
        results["solver_execution_allowed"] = False
        results["mcp_execution_allowed"] = False
        results["offline_review_only"] = True
    else:
        results["status"] = "offline_plan"
        results["offline_review_only"] = True
        results["mcp_execution_allowed"] = False
        results["solver_execution_allowed"] = False

    return results
