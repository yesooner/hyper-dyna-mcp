"""HyperMesh GUI launcher with auto-loaded MCP listener.

Launches HyperWorks with the listener script pre-loaded.
No manual Tcl console interaction needed.
"""

from __future__ import annotations

import subprocess
import time
import socket
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
) -> dict:
    """Launch HyperWorks GUI with MCP listener auto-loaded.

    Args:
        model_path: Optional .hm model file to open.
        wait_for_listener: Wait for listener to be ready.
        timeout: Max wait time in seconds.

    Returns:
        dict with process info and connection status.
    """
    # Get paths
    config = load_yaml("hypermesh_paths")
    hm_cfg = config.get("hypermesh", {})
    install_dir = hm_cfg.get("install_dir", "")

    hw_exe = Path(install_dir) / "hw" / "bin" / "win64" / "hw.exe"
    if not hw_exe.exists():
        return {"success": False, "error": f"hw.exe not found: {hw_exe}"}

    # Build command
    listener = str(_LISTENER_PATH).replace("\\", "/")
    cmd = [str(hw_exe), "-tcl", f'source "{listener}"']

    # Set environment
    import os
    env = os.environ.copy()
    env["ALTAIR_HOME"] = str(install_dir)
    env.setdefault("HW_ROOTDIR", str(install_dir))

    # Launch
    try:
        proc = subprocess.Popen(
            cmd,
            env=env,
            cwd=str(install_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        return {"success": False, "error": f"Failed to launch: {e}"}

    result = {
        "success": True,
        "pid": proc.pid,
        "command": cmd,
        "listener": str(_LISTENER_PATH),
    }

    # Wait for listener
    if wait_for_listener:
        start = time.time()
        while time.time() - start < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((DEFAULT_GUI_HOST, DEFAULT_GUI_PORT))
                sock.close()
                result["listener_ready"] = True
                result["wait_time"] = round(time.time() - start, 1)
                logger.info(f"Listener ready on {DEFAULT_GUI_HOST}:{DEFAULT_GUI_PORT}")
                return result
            except (ConnectionRefusedError, OSError):
                time.sleep(1)

        result["listener_ready"] = False
        result["warning"] = f"Listener not ready after {timeout}s"

    return result


def check_listener(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Check if the MCP listener is active."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((host, port))
        sock.close()
        return {"success": True, "host": host, "port": port, "status": "listening"}
    except (ConnectionRefusedError, OSError) as e:
        return {"success": False, "host": host, "port": port, "error": str(e)}
