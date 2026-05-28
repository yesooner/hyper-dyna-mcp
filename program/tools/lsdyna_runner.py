"""LS-DYNA solver command generation. All execution defaults to dry_run=True."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml, validate_path


@dataclass
class LSDynaCommand:
    """A generated LS-DYNA solver command."""
    executable: str
    input_file: str
    ncpus: int = 4
    memory: str = "200m"
    args: list[str] | None = None

    def to_command_list(self) -> list[str]:
        cmd = [
            self.executable,
            f"i={self.input_file}",
            f"ncpus={self.ncpus}",
            f"memory={self.memory}",
        ]
        if self.args:
            cmd.extend(self.args)
        return cmd

    def to_command_str(self) -> str:
        return " ".join(self.to_command_list())


def generate_solver_command(
    input_file: str | Path,
    ncpus: int | None = None,
    memory: str | None = None,
    extra_args: list[str] | None = None,
) -> LSDynaCommand:
    """Generate an LS-DYNA solver command from path config.

    Does NOT execute the solver. Always returns the command for review.
    """
    config = load_yaml("lsdyna_paths")
    lsdyna_cfg = config.get("lsdyna", {})

    solver_exe = lsdyna_cfg.get("solver_exe", "")
    if not solver_exe:
        logger.warning("LS-DYNA solver path not configured in lsdyna_paths.yaml")

    if ncpus is None:
        ncpus = lsdyna_cfg.get("ncpus_default", 4)
    if memory is None:
        memory = lsdyna_cfg.get("memory_default", "200m")

    input_path = Path(input_file)
    if not input_path.exists():
        logger.warning(f"Input file does not exist: {input_path}")

    cmd = LSDynaCommand(
        executable=solver_exe,
        input_file=str(input_path.resolve()),
        ncpus=ncpus,
        memory=memory,
        args=extra_args,
    )

    logger.info(f"Generated LS-DYNA command (dry_run): {cmd.to_command_str()}")
    return cmd


def run_lsdyna(
    input_file: str | Path,
    dry_run: bool = True,
    ncpus: int | None = None,
    memory: str | None = None,
    extra_args: list[str] | None = None,
) -> dict:
    """Generate and optionally execute LS-DYNA solver.

    Args:
        input_file: Path to .k input file
        dry_run: If True (default), only generate command without executing
        ncpus: Number of CPU cores
        memory: Memory allocation string
        extra_args: Additional command line arguments

    Returns:
        Dict with command info and execution status
    """
    cmd = generate_solver_command(input_file, ncpus, memory, extra_args)

    result = {
        "command": cmd.to_command_str(),
        "command_list": cmd.to_command_list(),
        "input_file": cmd.input_file,
        "dry_run": dry_run,
        "executed": False,
        "return_code": None,
        "stdout": None,
        "stderr": None,
    }

    if dry_run:
        logger.info("dry_run=True — skipping solver execution")
        return result

    # Real execution (only if explicitly requested)
    import subprocess

    logger.warning(f"Executing LS-DYNA: {cmd.to_command_str()}")
    try:
        proc = subprocess.run(
            cmd.to_command_list(),
            capture_output=True,
            text=True,
            timeout=3600,
        )
        result["executed"] = True
        result["return_code"] = proc.returncode
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
    except subprocess.TimeoutExpired:
        result["stderr"] = "Solver execution timed out (3600s)"
        result["return_code"] = -1
    except FileNotFoundError:
        result["stderr"] = f"Solver executable not found: {cmd.executable}"
        result["return_code"] = -1

    return result
