"""HyperMesh Tcl template engine for LS-DYNA keywords.

Loads Tcl templates from templates/keyword/, fills parameters,
sends to HyperMesh via socket.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_lsdyna_mapping import (
    get_verified_mapping,
    has_verified_mapping,
    render_verified_keyword,
)

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "keyword"
_INDEX_PATH = TEMPLATES_DIR.parent / "keyword_index.json"

# Pre-built keyword index: keyword → {category, entity_type, placeholders, description}
_KEYWORD_INDEX: dict[str, dict] = {}
if _INDEX_PATH.exists():
    import json
    _KEYWORD_INDEX = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))

# --- Keyword category → subdirectory mapping ---
CATEGORY_DIR = {
    "MAT": "mat",
    "SECTION": "section",
    "PART": "part",
    "CONTACT": "contact",
    "BOUNDARY": "boundary",
    "LOAD": "load",
    "CONTROL": "control",
    "DATABASE": "database",
    "SET": "set",
    "DEFINE": "define",
    "CONSTRAINED": "constrained",
    "INITIAL": "initial",
    "EOS": "eos",
    "RIGIDWALL": "rigidwall",
    "HOURGLASS": "hourglass",
}


def _keyword_to_path(keyword: str) -> Path:
    """Map keyword name to template file path."""
    keyword = keyword.upper().lstrip("*")

    # Find category
    for prefix, subdir in CATEGORY_DIR.items():
        if keyword.startswith(prefix):
            return TEMPLATES_DIR / subdir / f"{keyword}.tcl"

    # Fallback: try root
    return TEMPLATES_DIR / f"{keyword}.tcl"


class HmTemplateEngine:
    """Template engine for HyperMesh Tcl scripts."""

    def __init__(self, templates_dir: Path | str | None = None):
        self.templates_dir = Path(templates_dir) if templates_dir else TEMPLATES_DIR

    def list_templates(self, category: str | None = None) -> list[str]:
        """List available templates."""
        templates = []
        if category:
            cat_dir = self.templates_dir / category.lower()
            if cat_dir.exists():
                for f in cat_dir.glob("*.tcl"):
                    templates.append(f.stem)
        else:
            for cat_dir in self.templates_dir.iterdir():
                if cat_dir.is_dir():
                    for f in cat_dir.glob("*.tcl"):
                        templates.append(f"{cat_dir.name}/{f.stem}")
        return sorted(templates)

    def load_template(self, keyword: str) -> str:
        """Load a Tcl template by keyword name."""
        path = _keyword_to_path(keyword)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {keyword} ({path})")
        return path.read_text(encoding="utf-8")

    def render(self, keyword: str, params: dict[str, Any]) -> str:
        """Load template, fill parameters, return Tcl script.

        Args:
            keyword: LS-DYNA keyword name (e.g., "MAT_ELASTIC")
            params: Parameter values (e.g., {"MID": 1, "RHO": 7.85e-9})

        Returns:
            Tcl script string with parameters filled.
        """
        if has_verified_mapping(keyword):
            return render_verified_keyword(keyword, params)

        template = self.load_template(keyword)

        # Fill {{PARAM}} placeholders
        for key, value in params.items():
            placeholder = "{{" + key + "}}"
            template = template.replace(placeholder, str(value))

        # Check for unfilled placeholders
        unfilled = re.findall(r"\{\{(\w+)\}\}", template)
        if unfilled:
            logger.warning(f"Unfilled placeholders in {keyword}: {unfilled}")

        return template

    def render_sequence(self, steps: list[dict[str, Any]]) -> str:
        """Render multiple keyword templates in sequence.

        Args:
            steps: List of {"keyword": "MAT_ELASTIC", "params": {...}}

        Returns:
            Combined Tcl script.
        """
        scripts = []
        for step in steps:
            keyword = step["keyword"]
            params = step.get("params", {})
            try:
                scripts.append(self.render(keyword, params))
            except FileNotFoundError as e:
                logger.error(f"Template not found: {keyword}")
                scripts.append(f"# ERROR: Template not found: {keyword}")
        return "\n\n".join(scripts)

    def has_template(self, keyword: str) -> bool:
        """Check if a template exists for the keyword."""
        if has_verified_mapping(keyword):
            return True
        return _keyword_to_path(keyword).exists()

    def get_template_info(self, keyword: str) -> dict[str, Any]:
        """Get template metadata (placeholder names, file path)."""
        mapping = get_verified_mapping(keyword)
        if mapping is not None:
            return {
                "exists": True,
                "keyword": mapping.keyword,
                "source": "verified_hypermesh_mapping",
                "entity_type": mapping.entity_type,
                "cardimage": mapping.cardimage,
                "id_param": mapping.id_param,
                "fields": mapping.fields,
                "optional_fields": mapping.optional_fields or {},
                "unsupported_fields": list(mapping.unsupported_fields),
                "placeholders": mapping.placeholders,
                "description": f"Verified HyperMesh mapping to {mapping.cardimage}",
                "parameters": ", ".join(mapping.placeholders),
            }

        path = _keyword_to_path(keyword)
        if not path.exists():
            return {"exists": False, "keyword": keyword}

        content = path.read_text(encoding="utf-8")
        placeholders = list(set(re.findall(r"\{\{(\w+)\}\}", content)))

        # Extract comment header
        header_lines = []
        for line in content.split("\n"):
            if line.strip().startswith("#"):
                header_lines.append(line.strip().lstrip("# ").strip())
            else:
                break

        return {
            "exists": True,
            "keyword": keyword,
            "path": str(path),
            "placeholders": sorted(placeholders),
            "description": header_lines[1] if len(header_lines) > 1 else "",
            "parameters": header_lines[2] if len(header_lines) > 2 else "",
        }

    # --- Index-based lookup (fast, no file I/O) ---

    def search_keywords(self, query: str, category: str | None = None) -> list[dict]:
        """Search keyword index by substring match.

        Args:
            query: Search string (matched against keyword name and description)
            category: Optional category filter (e.g., "mat", "contact")

        Returns:
            List of matching keyword entries.
        """
        q = query.upper()
        results = []
        for kw, info in _KEYWORD_INDEX.items():
            if category and info.get("category", "") != category.lower():
                continue
            if q in kw or q in info.get("description", "").upper():
                results.append({"keyword": kw, **info})
        return results

    def get_keyword_map(self, category: str) -> list[dict]:
        """Get all keywords in a category from the index.

        Args:
            category: Category name (e.g., "mat", "contact", "boundary")

        Returns:
            List of keyword entries in that category.
        """
        return [
            {"keyword": kw, **info}
            for kw, info in _KEYWORD_INDEX.items()
            if info.get("category", "") == category.lower()
        ]

    def get_keyword_params(self, keyword: str) -> dict | None:
        """Get required parameters for a keyword from the index.

        Args:
            keyword: LS-DYNA keyword name

        Returns:
            Dict with category, entity_type, placeholders, description or None.
        """
        kw = keyword.upper().lstrip("*")
        return _KEYWORD_INDEX.get(kw)
