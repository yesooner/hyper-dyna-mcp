"""LS-PrePost cfile execution.

Supports batch mode (lsprepost cfile=path) with timeout.
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

_RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"


def _ensure_runs_dir() -> Path:
    _RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return _RUNS_DIR


def _resolve_lsprepost(override: str | Path | None = None) -> Path:
    """Resolve lsprepost.exe path from override or YAML config."""
    if override:
        return Path(override)
    config = load_yaml("lsprepost_paths")
    lsprepost_cfg = config.get("lsprepost", {})
    exe = lsprepost_cfg.get("exe") or lsprepost_cfg.get("exe_path", "")
    if not exe:
        raise FileNotFoundError("LS-PrePost path not configured in path/lsprepost_paths.yaml")
    return Path(exe)


def generate_lsprepost_command(
    cfile: str | Path,
    lsprepost_exe: str | Path | None = None,
) -> list[str]:
    """Generate an LS-PrePost command from path config."""
    exe = _resolve_lsprepost(lsprepost_exe)
    return [str(exe), f"cfile={cfile}"]


def run_lsprepost(
    cfile: str | Path,
    dry_run: bool = True,
    timeout: int = 600,
    lsprepost_exe: str | Path | None = None,
) -> dict:
    """Execute an LS-PrePost cfile.

    Args:
        cfile: Path to .cfile command file.
        dry_run: If True, only return the command without executing.
        timeout: Subprocess timeout in seconds.
        lsprepost_exe: Override path to lsprepost executable.

    Returns:
        dict with keys: success, command, stdout, stderr, etc.
    """
    exe = _resolve_lsprepost(lsprepost_exe)
    cmd = [str(exe), f"cfile={cfile}"]

    result = {
        "command": cmd,
        "command_str": " ".join(cmd),
        "dry_run": dry_run,
        "executed": False,
    }

    if dry_run:
        logger.info("dry_run=True — skipping LS-PrePost execution")
        return result

    try:
        completed = subprocess.run(
            cmd,
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
            "message": f"LS-PrePost did not finish within {timeout} seconds.",
            "executed": True,
        })
    except FileNotFoundError as exc:
        result.update({
            "success": False,
            "error": str(exc),
        })

    return result
