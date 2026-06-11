"""HyperMesh GUI launch planning helpers.

Current MCP scope is GUI-only and expects the user to start HyperMesh manually,
then source the generated listener in the Tcl Console. This module may prepare
launch commands for review, but it must not start HyperWorks as an agent
execution path.
"""

from __future__ import annotations

from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml

DEFAULT_GUI_HOST = "127.0.0.1"
DEFAULT_GUI_PORT = 47883
_LISTENER_PATH = Path(__file__).resolve().parents[2] / "runs" / "mcp.tcl"


def launch_hm_gui(
    model_path: str | Path | None = None,
    wait_for_listener: bool = True,
    timeout: int = 30,
    execute: bool = False,
) -> dict:
    """Prepare a HyperWorks GUI launch command without executing it by default.

    Args:
        model_path: Optional .hm model file to open.
        wait_for_listener: Deprecated. Listener readiness requires PONG checks
            after the user sources the listener in HyperMesh.
        timeout: Max wait time in seconds.
        execute: Reserved for future explicit UI launch support. Real execution
            is blocked in the current GUI-only MCP scope.

    Returns:
        dict with process info and connection status.
    """
    if execute:
        return {
            "success": False,
            "executed": False,
            "dry_run": True,
            "error_type": "hypermesh_gui_launch_out_of_scope",
            "error": (
                "Automatic HyperMesh GUI launch is outside the current MCP execution scope. "
                "Open HyperMesh manually and source the generated listener Tcl."
            ),
            "command": [],
            "listener": str(_LISTENER_PATH),
            "model_path": str(model_path) if model_path else None,
            "wait_for_listener_requested": bool(wait_for_listener),
            "timeout": timeout,
        }

    # Get paths
    config = load_yaml("hypermesh_paths")
    hm_cfg = config.get("hypermesh", {})
    install_dir = hm_cfg.get("install_dir", "")

    hw_exe = Path(install_dir) / "hw" / "bin" / "win64" / "hw.exe"
    if not hw_exe.exists():
        return {"success": False, "error": f"hw.exe not found: {hw_exe}", "executed": False}

    # Build command
    listener = str(_LISTENER_PATH).replace("\\", "/")
    cmd = [str(hw_exe), "-tcl", f'source "{listener}"']

    result = {
        "success": not execute,
        "executed": False,
        "dry_run": True,
        "error_type": None if not execute else "hypermesh_gui_launch_out_of_scope",
        "error": None if not execute else (
            "Automatic HyperMesh GUI launch is outside the current MCP execution scope. "
            "Open HyperMesh manually and source the generated listener Tcl."
        ),
        "command": cmd,
        "listener": str(_LISTENER_PATH),
        "model_path": str(model_path) if model_path else None,
        "wait_for_listener_requested": bool(wait_for_listener),
        "timeout": timeout,
    }
    return result


def check_listener(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Check whether the HyperMesh listener returns the expected PONG."""
    from program.tools.hm_gui import diagnose_listener_port

    result = diagnose_listener_port(host=host, port=port, timeout=3, include_alternate=False)
    return {
        "success": result.get("success", False),
        "host": host,
        "port": port,
        "status": (result.get("diagnosis") or {}).get("reason"),
        "diagnosis": result.get("diagnosis"),
        "ping": result.get("ping"),
    }
