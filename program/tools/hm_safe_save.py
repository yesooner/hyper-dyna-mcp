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
    result = execute_tcl_gui(script, timeout=timeout, allow_file_io=True)

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
    """Blocked compatibility helper for arbitrary Tcl execution plus save.

    Arbitrary Tcl execution must go through verified modeling tools or explicit
    user-provided ``execute_tcl_gui`` fallback. This helper is kept importable
    for legacy callers but must not send Tcl.
    """
    return {
        "success": False,
        "description": description,
        "error_type": "safe_execute_not_verified",
        "error": (
            "safe_execute is a legacy arbitrary Tcl helper and is blocked. "
            "Use verified modeling tools for execution and hm_auto_save for .hm saves."
        ),
        "execution_allowed": False,
        "tcl_sent": False,
        "auto_save_attempted": False,
        "required_tool": "hm_modeling_action",
        "save_tool": "hm_auto_save",
        "requested": {
            "script_length": len(script or ""),
            "model_path": model_path,
            "timeout": timeout,
            "save_after": save_after,
        },
    }


def safe_batch_execute(
    steps: list[dict],
    model_path: str | None = None,
    timeout: int = 30,
) -> dict:
    """Blocked compatibility helper for arbitrary batch Tcl execution.

    Kept importable for legacy callers, but it must not dispatch Tcl.
    """
    results = [
        safe_execute(
            step.get("description", f"step_{i+1}"),
            step.get("script", ""),
            model_path=model_path,
            timeout=timeout,
            save_after=True,
        )
        for i, step in enumerate(steps)
    ]
    return {
        "success": False,
        "error_type": "safe_execute_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
        "steps_completed": 0,
        "total_steps": len(steps),
        "results": results,
    }
