"""Parse LS-DYNA output logs (messag, d3hsp). Placeholder for Phase 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LSDynaLog:
    filepath: str = ""
    termination_status: str = ""
    cpu_time: str = ""
    energy_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def parse_messag(filepath: str | Path) -> LSDynaLog:
    """Parse an LS-DYNA messag file.

    TODO: Full implementation in Phase 2.
    """
    path = Path(filepath)
    log = LSDynaLog(filepath=str(path))

    if not path.exists():
        log.errors.append(f"File not found: {path}")
        return log

    content = path.read_text(encoding="utf-8", errors="replace")

    for line in content.splitlines():
        if "Normal termination" in line:
            log.termination_status = "normal"
        elif "Error termination" in line:
            log.termination_status = "error"
        elif "warning" in line.lower():
            log.warnings.append(line.strip())

    return log
