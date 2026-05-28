"""Check runtime environment: Python version, conda env, installed packages."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class EnvReport:
    python_version: str = ""
    platform: str = ""
    conda_env: str = ""
    conda_available: bool = False
    required_packages: dict[str, str] = field(default_factory=dict)
    missing_packages: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing_packages) == 0

    def to_dict(self) -> dict:
        return {
            "python_version": self.python_version,
            "platform": self.platform,
            "conda_env": self.conda_env,
            "conda_available": self.conda_available,
            "required_packages": self.required_packages,
            "missing_packages": self.missing_packages,
            "warnings": self.warnings,
            "ok": self.ok,
        }


def check_environment(required: list[str] | None = None) -> EnvReport:
    """Run environment checks and return a report."""
    report = EnvReport()
    report.python_version = platform.python_version()
    report.platform = sys.platform

    # Conda check
    report.conda_available = shutil.which("conda") is not None
    report.conda_env = sys.prefix

    # Package checks
    if required is None:
        required = ["mcp", "pydantic", "yaml", "loguru"]

    for pkg in required:
        try:
            mod = __import__(pkg)
            version = getattr(mod, "__version__", "unknown")
            report.required_packages[pkg] = version
        except ImportError:
            report.missing_packages.append(pkg)

    return report
