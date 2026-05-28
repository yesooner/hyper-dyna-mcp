"""Mixed workflow: NL request → Plan → HM preprocess → .k extract → Solve → Post → Log.

This module orchestrates the full CAE pipeline combining HyperMesh, LS-DYNA, and LS-PrePost.
"""

from __future__ import annotations

from typing import Any

from program.tools.k_parser import parse_k_file
from program.tools.k_writer import KModel
from program.tools.lsdyna_runner import run_lsdyna
from program.tools.obsidian_logger import write_execution_log


def plan_from_k_file(filepath: str) -> dict[str, Any]:
    """Analyze a .k file and suggest next steps.

    Returns:
        dict with analysis and recommended actions.
    """
    kfile = parse_k_file(filepath)
    errors = kfile.validate()

    suggestions: list[str] = []

    if errors:
        suggestions.append("Fix validation errors before solving")

    if not kfile.get_materials():
        suggestions.append("No materials defined — add *MAT_* cards")

    if not kfile.get_parts():
        suggestions.append("No parts defined — add *PART cards")

    if not kfile.get_nodes():
        suggestions.append("No nodes defined — add *NODE cards")

    if not kfile.get_elements():
        suggestions.append("No elements defined — add *ELEMENT_* cards")

    if kfile.get_materials() and kfile.get_parts() and kfile.get_nodes() and kfile.get_elements():
        suggestions.append("Model looks complete — ready to solve")

    return {
        "filepath": filepath,
        "title": kfile.title,
        "n_parts": len(kfile.get_parts()),
        "n_materials": len(kfile.get_materials()),
        "n_nodes": len(kfile.get_nodes()),
        "n_elements": len(kfile.get_elements()),
        "errors": errors,
        "suggestions": suggestions,
    }


def execute_pipeline(
    k_file: str,
    dry_run: bool = True,
    log_to_obsidian: bool = False,
) -> dict[str, Any]:
    """Execute the full mixed workflow.

    Steps:
    1. Parse and validate .k file
    2. Generate solver command
    3. Optionally execute solver
    4. Log results to Obsidian

    Args:
        k_file: Path to .k input file.
        dry_run: If True, only generate commands.
        log_to_obsidian: If True, write execution log.

    Returns:
        dict with pipeline results.
    """
    results: dict[str, Any] = {"steps": []}

    # Step 1: Parse
    parse_result = plan_from_k_file(k_file)
    results["parse"] = parse_result
    results["steps"].append("parse")

    if parse_result["errors"]:
        results["status"] = "validation_failed"
        return results

    # Step 2: Solve
    solve_result = run_lsdyna(input_file=k_file, dry_run=dry_run)
    results["solve"] = solve_result
    results["steps"].append("solve")

    # Step 3: Log
    if log_to_obsidian:
        log_entry = write_execution_log(
            task=f"Mixed pipeline: {parse_result['title'] or k_file}",
            modified_files=[k_file],
            commands=[solve_result.get("command_str", "")],
            test_results=f"Parts={parse_result['n_parts']}, Materials={parse_result['n_materials']}",
            next_steps="Review solver output" if not dry_run else "Run with dry_run=False to execute",
        )
        results["obsidian_log"] = log_entry
        results["steps"].append("log")

    results["status"] = "dry_run" if dry_run else "completed"
    return results
