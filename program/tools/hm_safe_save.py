"""HyperMesh auto-save hook — save model after each major operation.

Prevents data loss from segfaults by saving after each successful step.
"""

from __future__ import annotations

import time
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_gui import execute_tcl_gui
from program.tools.hm_tcl_generator import quote_tcl_path

_SAVES_DIR = Path(__file__).resolve().parents[2] / "output" / "saves"


def auto_save(
    step_name: str,
    model_path: str | None = None,
    timeout: int = 30,
) -> dict:
    """Save current HyperMesh model after a successful step.

    Args:
        step_name: Description of completed step (e.g., "materials_set")
        model_path: Path to save .hm file. Auto-generated if None.
        timeout: Socket timeout

    Returns:
        dict with success and saved path.
    """
    _SAVES_DIR.mkdir(parents=True, exist_ok=True)

    if model_path is None:
        ts = time.strftime("%Y%m%d_%H%M%S")
        model_path = str(_SAVES_DIR / f"autosave_{step_name}_{ts}.hm")

    save_path = Path(model_path)
    script = f'*writefile "{quote_tcl_path(save_path)}" 1'
    result = execute_tcl_gui(script, timeout=timeout)

    if result.get("success") and save_path.exists():
        logger.info(f"Auto-saved after '{step_name}': {model_path}")
        return {"success": True, "step": step_name, "path": str(save_path), "size": save_path.stat().st_size}
    if result.get("success"):
        logger.warning(f"Auto-save reported success but file was not created: {model_path}")
        return {
            "success": False,
            "step": step_name,
            "path": str(save_path),
            "error": "HyperMesh reported success but the .hm file was not created.",
            "response": result.get("response", ""),
        }
    else:
        logger.warning(f"Auto-save failed after '{step_name}'")
        return {"success": False, "step": step_name, "error": result.get("error")}


def safe_execute(
    description: str,
    script: str,
    model_path: str | None = None,
    timeout: int = 30,
    save_after: bool = True,
) -> dict:
    """Execute a Tcl script with auto-save on success.

    Args:
        description: Human-readable step description
        script: Tcl script to execute
        model_path: Path to save after execution
        timeout: Socket timeout
        save_after: Whether to auto-save after success

    Returns:
        dict with execution result and save status.
    """
    result = execute_tcl_gui(script, timeout=timeout)

    if result.get("success") and save_after:
        save_result = auto_save(description, model_path, timeout=timeout)
        result["auto_save"] = save_result

    return result


def safe_batch_execute(
    steps: list[dict],
    model_path: str | None = None,
    timeout: int = 30,
) -> dict:
    """Execute multiple steps with auto-save after each.

    Args:
        steps: List of {"description": "...", "script": "..."}
        model_path: Base path for saves
        timeout: Per-step timeout

    Returns:
        dict with results for each step.
    """
    results = []
    for i, step in enumerate(steps):
        desc = step.get("description", f"step_{i+1}")
        script = step.get("script", "")

        logger.info(f"Executing step {i+1}/{len(steps)}: {desc}")
        r = safe_execute(desc, script, model_path, timeout, save_after=True)
        results.append(r)

        if not r.get("success"):
            logger.error(f"Step {desc} failed, stopping batch")
            break

    return {
        "success": all(r.get("success") for r in results),
        "steps_completed": sum(1 for r in results if r.get("success")),
        "total_steps": len(steps),
        "results": results,
    }
