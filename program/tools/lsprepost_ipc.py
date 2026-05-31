"""LS-PrePost batch execution via cfile.

LS-PrePost 4.8 does NOT support Tcl scripting via cfiles.
cfiles only support LS-PrePost native commands (open, capture, etc.).
Use lsprepost_runner.py for subprocess execution.
"""

from __future__ import annotations

from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml


def generate_cfile_commands(
    d3plot_path: str | None = None,
    keyword_path: str | None = None,
    output_png: str | None = None,
    width: int = 1920,
    height: int = 1080,
) -> list[str]:
    """Generate LS-PrePost native cfile commands.

    Note: These are LS-PrePost commands, NOT Tcl.
    """
    commands = []
    if d3plot_path:
        commands.append(f"open d3plot {d3plot_path}")
    if keyword_path:
        commands.append(f"open key {keyword_path}")
    if output_png:
        commands.append(f"screen width {width}")
        commands.append(f"screen height {height}")
        commands.append(f"capture {output_png}")
    return commands


def write_cfile(
    commands: list[str],
    output_path: str | Path,
) -> Path:
    """Write cfile commands to a file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(commands) + "\n"
    path.write_text(content, encoding="utf-8")
    logger.info(f"Wrote cfile: {path}")
    return path
