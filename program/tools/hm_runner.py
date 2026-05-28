"""HyperMesh hmbatch execution.

Adapted from times1234/hypermesh-mcp _run_hmbatch pattern.
Supports batch mode (hmbatch.exe -tcl) with environment setup and timeout.
dry_run=True by default — does not launch real software.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml

# --- Constants ---

_RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"


# --- Helpers ---


def _ensure_runs_dir() -> Path:
    _RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return _RUNS_DIR


def _resolve_hmbatch(override: str | Path | None = None) -> Path:
    """Resolve hmbatch.exe path from override or YAML config."""
    if override:
        return Path(override)
    config = load_yaml("hypermesh_paths")
    exe = config.get("hypermesh", {}).get("hmbatch_exe", "")
    if not exe:
        raise FileNotFoundError("HyperMesh hmbatch path not configured in path/hypermesh_paths.yaml")
    return Path(exe)


def _altair_home_from_exe(exe: Path) -> Path:
    """Infer ALTAIR_HOME from hmbatch.exe location."""
    # Typical: E:/HM2021/2021/hwdesktop/hw/bin/win64/hmbatch.exe
    # ALTAIR_HOME = E:/HM2021/2021/hwdesktop
    return exe.parent.parent.parent.parent


def _hmbatch_environment(exe: Path) -> dict[str, str]:
    """Build environment variables for hmbatch subprocess."""
    env = os.environ.copy()
    altair_home = _altair_home_from_exe(exe)
    env["ALTAIR_HOME"] = str(altair_home)
    env.setdefault("HW_ROOTDIR", str(altair_home))

    bin_paths = [
        altair_home / "hm" / "bin" / "win64",
        altair_home / "hw" / "bin" / "win64",
    ]
    existing_bins = [str(p) for p in bin_paths if p.exists()]
    if existing_bins:
        env["PATH"] = ";".join(existing_bins + [env.get("PATH", "")])

    tcl_library = altair_home / "hw" / "tcl" / "tcl8.5.9" / "win64" / "lib" / "tcl8.5"
    if tcl_library.exists():
        env["TCL_LIBRARY"] = str(tcl_library)
    return env


def _write_run_script(script: str) -> Path:
    """Write Tcl script to runs/ directory with timestamp."""
    run_dir = _ensure_runs_dir()
    ts = time.strftime("%Y%m%d_%H%M%S")
    script_path = run_dir / f"hypermesh_mcp_{ts}_{os.getpid()}.tcl"
    script_path.write_text(script, encoding="utf-8")
    return script_path


# --- Public API ---


def generate_hmbatch_command(
    tcl_script: str | Path,
    model_file: str | Path | None = None,
) -> list[str]:
    """Generate an hmbatch command from path config.

    Does NOT execute. Returns the command list for review.
    """
    config = load_yaml("hypermesh_paths")
    hm_cfg = config.get("hypermesh", {})
    hmbatch = hm_cfg.get("hmbatch_exe", "")
    if not hmbatch:
        logger.warning("HyperMesh hmbatch path not configured")

    cmd = [hmbatch, "-noexit", "-tcl", str(tcl_script)]
    if model_file:
        cmd.extend(["-m", str(model_file)])
    return cmd


def run_hmbatch(
    tcl_script: str | Path,
    model_file: str | Path | None = None,
    dry_run: bool = True,
    timeout: int = 300,
) -> dict:
    """Execute a Tcl script via hmbatch.exe.

    Args:
        tcl_script: Path to .tcl file or inline Tcl script content.
        model_file: Optional .hm model file.
        dry_run: If True, only return the command without executing.
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: success, command, script_path, stdout, stderr, etc.
    """
    # If tcl_script is inline content, write to file first
    if "\n" in str(tcl_script) or not Path(str(tcl_script)).exists():
        script_path = _write_run_script(str(tcl_script))
    else:
        script_path = Path(tcl_script)

    exe = _resolve_hmbatch()
    command = [str(exe), "-noexit", "-tcl", str(script_path)]

    if model_file:
        model = Path(model_file)
        if not model.exists():
            return {"success": False, "error": f"Model file not found: {model}"}
        command.append(str(model))

    result = {
        "command": command,
        "command_str": " ".join(command),
        "script_path": str(script_path),
        "dry_run": dry_run,
        "executed": False,
    }

    if dry_run:
        logger.info("dry_run=True — skipping hmbatch execution")
        return result

    env = _hmbatch_environment(exe)
    try:
        completed = subprocess.run(
            command,
            cwd=str(script_path.parent),
            env=env,
            capture_output=True,
            text=True,
            timeout=max(1, timeout),
        )
        result.update({
            "success": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "executed": True,
        })
    except subprocess.TimeoutExpired as exc:
        result.update({
            "success": False,
            "timeout": True,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "message": f"hmbatch did not finish within {timeout} seconds.",
            "executed": True,
        })
    except FileNotFoundError as exc:
        result.update({
            "success": False,
            "error": str(exc),
        })

    return result


def check_hypermesh_connection() -> dict:
    """Check if hmbatch.exe is accessible and configured."""
    try:
        exe = _resolve_hmbatch()
        exists = exe.exists()
        return {
            "success": exists,
            "hmbatch_path": str(exe),
            "altair_home": str(_altair_home_from_exe(exe)),
            "message": "hmbatch.exe found" if exists else f"hmbatch.exe not found at {exe}",
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}
