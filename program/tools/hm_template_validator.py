"""Validate Tcl templates against a live HyperMesh GUI.

Reads each template from templates/keyword/, renders with dummy parameters,
sends the first HyperMesh command (*createentity) to the GUI listener,
and records success/failure.

Usage:
    from program.tools.hm_template_validator import validate_category, validate_all

    # Validate one category
    results = validate_category("control", timeout=5)

    # Validate everything
    report = validate_all(timeout=5)
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_gui import execute_tcl_gui

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "keyword"


def _extract_first_command(template_content: str) -> str | None:
    """Extract the first HyperMesh command line from a template.

    Returns the first line starting with '*' (after filling dummy params),
    or None if no such line exists.
    """
    for line in template_content.splitlines():
        line = line.strip()
        if line.startswith("*"):
            return line
    return None


def _fill_dummy_params(template_content: str) -> str:
    """Replace all {{PARAM}} placeholders with dummy numeric values."""
    # Find all placeholder names
    placeholders = re.findall(r"\{\{(\w+)\}\}", template_content)
    filled = template_content
    for i, name in enumerate(placeholders):
        placeholder = "{{" + name + "}}"
        # Use sequential dummy IDs starting from 900000 to avoid collisions
        filled = filled.replace(placeholder, str(900000 + i))
    return filled


def validate_template(keyword: str, timeout: int = 5) -> dict[str, Any]:
    """Validate a single template against HyperMesh GUI.

    Steps:
        1. Load the .tcl template file
        2. Fill all placeholders with dummy values
        3. Extract the first command (*createentity or similar)
        4. Send it to HyperMesh GUI via execute_tcl_gui
        5. Return result dict

    Args:
        keyword: Template keyword name (e.g., "CONTROL_TERMINATION")
                 or category/name path (e.g., "control/CONTROL_TERMINATION")
        timeout: Socket timeout in seconds.

    Returns:
        dict with keys: keyword, status ("ok"/"fail"/"skip"/"missing"),
        first_command, response, error, elapsed_ms
    """
    result: dict[str, Any] = {
        "keyword": keyword,
        "status": "unknown",
        "first_command": None,
        "response": None,
        "error": None,
        "elapsed_ms": 0,
    }

    # Resolve template path
    template_path = _resolve_template_path(keyword)
    if template_path is None or not template_path.exists():
        result["status"] = "missing"
        result["error"] = f"Template file not found: {keyword}"
        return result

    # Read and fill
    try:
        content = template_path.read_text(encoding="utf-8")
    except Exception as e:
        result["status"] = "fail"
        result["error"] = f"Read error: {e}"
        return result

    filled = _fill_dummy_params(content)
    first_cmd = _extract_first_command(filled)

    if first_cmd is None:
        result["status"] = "skip"
        result["error"] = "No HyperMesh command found in template"
        return result

    result["first_command"] = first_cmd

    # Send to GUI
    t0 = time.perf_counter()
    try:
        gui_result = execute_tcl_gui(first_cmd, timeout=timeout, enforce_rules=False)
        elapsed = (time.perf_counter() - t0) * 1000
        result["elapsed_ms"] = round(elapsed, 1)
        result["response"] = gui_result.get("response", "")

        if gui_result.get("success"):
            result["status"] = "ok"
        else:
            result["status"] = "fail"
            result["error"] = gui_result.get("error") or gui_result.get("response", "")
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        result["elapsed_ms"] = round(elapsed, 1)
        result["status"] = "fail"
        result["error"] = str(e)

    return result


def _resolve_template_path(keyword: str) -> Path | None:
    """Resolve keyword to template file path.

    Accepts:
        - "CONTROL_TERMINATION" -> searches in category dirs
        - "control/CONTROL_TERMINATION" -> direct path
    """
    # Direct category/name format
    if "/" in keyword:
        path = TEMPLATES_DIR / f"{keyword}.tcl"
        if path.exists():
            return path
        # Try just the name part
        keyword = keyword.split("/", 1)[1]

    keyword_upper = keyword.upper()

    # Category prefix mapping (same as hm_template_engine.py)
    category_prefixes = {
        "MAT": "mat",
        "SECTION": "section",
        "PART": "part",
        "CONTACT": "contact",
        "BOUNDARY": "boundary",
        "LOAD": "load",
        "CONTROL": "control",
        "DATABASE": "database",
        "SET": "set",
        "DEFINE": "define",
        "CONSTRAINED": "constrained",
        "INITIAL": "initial",
        "EOS": "eos",
        "RIGIDWALL": "rigidwall",
        "HOURGLASS": "hourglass",
        "AIRBAG": "airbag",
        "ALE": "ale",
        "DAMPING": "damping",
        "ELEMENT": "element",
        "INTERFACE": "interface",
        "NODE": "node",
        "OTHER": "other",
        "SENSOR": "sensor",
    }

    for prefix, subdir in category_prefixes.items():
        if keyword_upper.startswith(prefix):
            path = TEMPLATES_DIR / subdir / f"{keyword_upper}.tcl"
            if path.exists():
                return path

    # Fallback: search all directories
    for subdir in TEMPLATES_DIR.iterdir():
        if subdir.is_dir():
            path = subdir / f"{keyword_upper}.tcl"
            if path.exists():
                return path

    return None


def validate_category(category: str, timeout: int = 5) -> list[dict[str, Any]]:
    """Validate all templates in a category directory.

    Args:
        category: Subdirectory name under templates/keyword/ (e.g., "control")
        timeout: Socket timeout per template in seconds.

    Returns:
        List of validation result dicts.
    """
    cat_dir = TEMPLATES_DIR / category.lower()
    if not cat_dir.exists() or not cat_dir.is_dir():
        return [{"category": category, "status": "missing", "error": f"Category directory not found: {category}"}]

    templates = sorted(cat_dir.glob("*.tcl"))
    results = []
    for tpl_path in templates:
        keyword = f"{category.lower()}/{tpl_path.stem}"
        result = validate_template(keyword, timeout=timeout)
        results.append(result)

    return results


def validate_all(
    batch_size: int = 50,
    timeout: int = 5,
) -> dict[str, Any]:
    """Validate all templates across all categories.

    Args:
        batch_size: Number of templates to validate before logging progress.
        timeout: Socket timeout per template in seconds.

    Returns:
        dict with keys:
            - total: int
            - ok: list of keyword names
            - fail: list of {keyword, error, ...}
            - skip: list of keyword names
            - missing: list of keyword names
            - categories: dict of category -> {ok, fail, skip, missing, total}
            - elapsed_sec: float
    """
    report: dict[str, Any] = {
        "total": 0,
        "ok": [],
        "fail": [],
        "skip": [],
        "missing": [],
        "categories": {},
        "elapsed_sec": 0,
    }

    t_start = time.perf_counter()

    # Discover categories
    categories = sorted(
        d.name for d in TEMPLATES_DIR.iterdir() if d.is_dir()
    )

    count = 0
    for cat in categories:
        cat_dir = TEMPLATES_DIR / cat
        templates = sorted(cat_dir.glob("*.tcl"))
        cat_stats = {"ok": 0, "fail": 0, "skip": 0, "missing": 0, "total": len(templates)}

        for tpl_path in templates:
            keyword = f"{cat}/{tpl_path.stem}"
            result = validate_template(keyword, timeout=timeout)
            status = result["status"]

            if status == "ok":
                report["ok"].append(keyword)
                cat_stats["ok"] += 1
            elif status == "fail":
                report["fail"].append({
                    "keyword": keyword,
                    "error": result.get("error", ""),
                    "first_command": result.get("first_command", ""),
                })
                cat_stats["fail"] += 1
            elif status == "skip":
                report["skip"].append(keyword)
                cat_stats["skip"] += 1
            elif status == "missing":
                report["missing"].append(keyword)
                cat_stats["missing"] += 1

            count += 1
            report["total"] = count

            if count % batch_size == 0:
                elapsed = time.perf_counter() - t_start
                logger.info(
                    f"Progress: {count} templates validated, "
                    f"elapsed={elapsed:.1f}s, "
                    f"ok={len(report['ok'])}, fail={len(report['fail'])}"
                )

        report["categories"][cat] = cat_stats

    report["elapsed_sec"] = round(time.perf_counter() - t_start, 2)
    return report
