"""Load and validate YAML path configurations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PATH_DIR = _PROJECT_ROOT / "path"


def load_yaml(name: str) -> dict[str, Any]:
    """Load a YAML config from the path/ directory."""
    p = _PATH_DIR / f"{name}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Path config not found: {p}")
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    logger.debug(f"Loaded path config: {name}")
    return data


def load_all_paths() -> dict[str, Any]:
    """Load all path configs into a single dict."""
    configs = {}
    for yaml_file in sorted(_PATH_DIR.glob("*.yaml")):
        configs[yaml_file.stem] = load_yaml(yaml_file.stem)
    return configs


def validate_path(path_str: str) -> bool:
    """Check if a filesystem path exists."""
    return Path(path_str).exists()
