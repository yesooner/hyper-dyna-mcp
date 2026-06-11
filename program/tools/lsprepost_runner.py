"""LS-PrePost cfile command planning.

Current project scope is HyperMesh GUI-only MCP. This module may prepare
dry-run command metadata for tests and future work, but it must not launch
LS-PrePost.
"""

from __future__ import annotations

from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml

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
    """Prepare an LS-PrePost command, but block real LS-PrePost execution.

    Args:
        cfile: Path to .cfile command file.
        dry_run: Must remain True in the current GUI-only MCP scope.
        timeout: Subprocess timeout in seconds.
        lsprepost_exe: Override path to lsprepost executable.

    Returns:
        dict with keys: success, command, stdout, stderr, etc.
    """
    if not dry_run:
        return {
            "success": False,
            "error_type": "lsprepost_execution_out_of_scope",
            "error": "LS-PrePost execution is outside the current HyperMesh GUI-only MCP scope.",
            "command": [],
            "command_str": "",
            "dry_run": dry_run,
            "executed": False,
        }

    exe = _resolve_lsprepost(lsprepost_exe)
    cmd = [str(exe), f"cfile={cfile}"]

    result = {
        "command": cmd,
        "command_str": " ".join(cmd),
        "dry_run": dry_run,
        "executed": False,
    }

    logger.info("dry_run=True — skipping LS-PrePost execution")
    return result
