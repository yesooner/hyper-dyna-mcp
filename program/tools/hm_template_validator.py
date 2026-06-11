"""Review Tcl templates without bypassing verified MAP gates.

Reads each template from templates/keyword/, renders with dummy parameters,
and extracts the first HyperMesh command for offline inspection. Live execution
is disabled by default because keyword templates are not execution authority;
routes must be promoted through dyna_keyword_query / hm_set_keyword policy.

Usage:
    from program.tools.hm_template_validator import validate_category, validate_all

    # Validate one category
    results = validate_category("control", timeout=5)

    # Review everything without sending Tcl
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


def validate_template(keyword: str, timeout: int = 5, execute: bool = False) -> dict[str, Any]:
    """Review a single template without executing Tcl.

    Steps:
        1. Load the .tcl template file
        2. Fill all placeholders with dummy values
        3. Extract the first command (*createentity or similar)
        4. Stop before GUI execution and return blocked/offline status
        5. Return result dict

    Args:
        keyword: Template keyword name (e.g., "CONTROL_TERMINATION")
                 or category/name path (e.g., "control/CONTROL_TERMINATION")
        timeout: Compatibility timeout in seconds.
        execute: Compatibility flag accepted by legacy callers. It does not
            enable Tcl execution in the current HyperMesh GUI-only MCP scope.

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
        "execution_allowed": False,
        "tcl_sent": False,
        "policy": "template_review_only_execution_blocked",
        "requested_execute": bool(execute),
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

    result["status"] = "blocked"
    result["error_type"] = "template_execution_not_verified"
    result["error"] = (
        "Template validation is offline-only. The execute flag is accepted for "
        "legacy compatibility but cannot enable Tcl execution. Use "
        "dyna_keyword_query and hm_set_keyword policy gates; do not execute "
        "keyword templates as a shortcut around verified dataname/cardimage routes."
    )
    result["execution_allowed"] = False
    result["tcl_sent"] = False

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


def validate_category(category: str, timeout: int = 5, execute: bool = False) -> list[dict[str, Any]]:
    """Review all templates in a category directory.

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
        result = validate_template(keyword, timeout=timeout, execute=execute)
        results.append(result)

    return results


def validate_all(
    batch_size: int = 50,
    timeout: int = 5,
    execute: bool = False,
) -> dict[str, Any]:
    """Review all templates across all categories.

    Args:
        batch_size: Number of templates to validate before logging progress.
        timeout: Socket timeout per template in seconds.

    Returns:
        dict with keys:
            - total: int
            - ok: list of keyword names
            - fail: list of {keyword, error, ...}
            - blocked: list of keyword names reviewed without execution
            - skip: list of keyword names
            - missing: list of keyword names
            - categories: dict of category -> {ok, fail, skip, missing, total}
            - elapsed_sec: float
    """
    report: dict[str, Any] = {
        "total": 0,
        "ok": [],
        "fail": [],
        "blocked": [],
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
        cat_stats = {"ok": 0, "fail": 0, "blocked": 0, "skip": 0, "missing": 0, "total": len(templates)}

        for tpl_path in templates:
            keyword = f"{cat}/{tpl_path.stem}"
            result = validate_template(keyword, timeout=timeout, execute=execute)
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
            elif status == "blocked":
                report["blocked"].append(keyword)
                cat_stats["blocked"] += 1
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
                    f"ok={len(report['ok'])}, blocked={len(report['blocked'])}, "
                    f"fail={len(report['fail'])}"
                )

        report["categories"][cat] = cat_stats

    report["elapsed_sec"] = round(time.perf_counter() - t_start, 2)
    return report
