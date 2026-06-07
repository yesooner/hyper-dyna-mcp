"""Write execution logs to Obsidian vault."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml, validate_path


def _get_obsidian_paths() -> dict:
    return load_yaml("obsidian_paths")


def write_execution_log(
    task: str,
    modified_files: list[str] | None = None,
    commands: list[str] | None = None,
    test_results: str | None = None,
    next_steps: str | None = None,
    log_type: str = "execution",
) -> str:
    """Write a log entry to the Obsidian vault.

    Args:
        task: Description of the task performed
        modified_files: List of files modified
        commands: List of commands executed
        test_results: Test result summary
        next_steps: Next planned steps
        log_type: One of "execution", "workflow", "validation"

    Returns:
        The formatted log entry string
    """
    config = _get_obsidian_paths()
    obs_cfg = config.get("obsidian", {})

    log_key = f"{log_type}_log"
    log_path = obs_cfg.get(log_key, "")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry_lines = [
        f"\n---\n",
        f"## [{now}] {task}\n",
    ]

    if modified_files:
        entry_lines.append("### Modified Files\n")
        for f in modified_files:
            entry_lines.append(f"- `{f}`")
        entry_lines.append("")

    if commands:
        entry_lines.append("### Commands\n")
        for c in commands:
            entry_lines.append(f"```powershell\n{c}\n```")
        entry_lines.append("")

    if test_results:
        entry_lines.append("### Test Results\n")
        entry_lines.append(test_results)
        entry_lines.append("")

    if next_steps:
        entry_lines.append("### Next Steps\n")
        entry_lines.append(next_steps)
        entry_lines.append("")

    entry = "\n".join(entry_lines)

    if log_path and validate_path(str(Path(log_path).parent)):
        p = Path(log_path)
        with open(p, "a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(f"Wrote Obsidian log to: {log_path}")
    else:
        logger.warning(f"Obsidian log path not available: {log_path}")

    return entry
