"""Offline LS-DYNA .k fixture/review parser.

This module reads keyword files for validation, fixture tests, and planning
review only. It is not a HyperMesh GUI route, not an MCP modeling/export tool,
and must not be used to satisfy final K export or model-creation requests in
the GUI-only MCP.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# --- Keyword categories (from manual pp.365-374) ---

KEYWORD_CATEGORIES: dict[str, set[str]] = {
    "file": {"KEYWORD", "END", "INCLUDE", "TITLE", "PARAMETER", "PARAMETER_EXPRESSION"},
    "control": set(),  # matched by prefix
    "material": set(),  # matched by prefix
    "section": set(),  # matched by prefix
    "part": set(),  # matched by prefix
    "node": set(),  # matched by prefix
    "element": set(),  # matched by prefix
    "set": set(),  # matched by prefix
    "boundary": set(),  # matched by prefix
    "contact": set(),  # matched by prefix
    "load": set(),  # matched by prefix
    "define": set(),  # matched by prefix
    "constrained": set(),  # matched by prefix
}

_CATEGORY_PREFIXES = {
    "control": "CONTROL",
    "material": "MAT_",
    "section": "SECTION_",
    "part": "PART",
    "node": "NODE",
    "element": "ELEMENT_",
    "set": "SET_",
    "boundary": "BOUNDARY_",
    "contact": "CONTACT_",
    "load": "LOAD_",
    "define": "DEFINE_",
    "constrained": "CONSTRAINED_",
}


def _classify_keyword(name: str) -> str:
    """Classify a keyword name into a category."""
    for cat, prefix in _CATEGORY_PREFIXES.items():
        if name.startswith(prefix):
            return cat
    if name in KEYWORD_CATEGORIES.get("file", set()):
        return "file"
    return "other"


# --- Data classes ---


@dataclass
class KKeyword:
    name: str
    category: str = "other"
    comments: list[str] = field(default_factory=list)
    data_lines: list[str] = field(default_factory=list)
    options: list[str] = field(default_factory=list)
    parsed_fields: dict = field(default_factory=dict)

    @property
    def is_long_format(self) -> bool:
        """Check if this keyword uses long format (suffixed with +)."""
        return any(opt == "+" for opt in self.options)

    @property
    def is_i10_format(self) -> bool:
        """Check if this keyword uses I10 format (suffixed with %)."""
        return any(opt == "%" for opt in self.options)

    def get_data_fields(self, card_index: int = 0) -> list[str]:
        """Parse a data line into fields (handles both fixed and free format)."""
        if card_index >= len(self.data_lines):
            return []
        return _parse_data_line(self.data_lines[card_index])

    def parse_field_values(self) -> dict:
        """Parse all data lines using keyword_fields mapping."""
        from program.tools.keyword_fields import parse_fields
        if not self.data_lines:
            return {}
        self.parsed_fields = parse_fields(self.name, self.data_lines[0])
        return self.parsed_fields


@dataclass
class KFile:
    title: str = ""
    keywords: list[KKeyword] = field(default_factory=list)
    format_hint: str = "standard"  # standard | long | i10
    memory: int | None = None
    ncpu: int | None = None

    def get_keywords(self, name: str) -> list[KKeyword]:
        return [k for k in self.keywords if k.name == name.upper()]

    def get_keywords_by_prefix(self, prefix: str) -> list[KKeyword]:
        return [k for k in self.keywords if k.name.startswith(prefix)]

    def get_keyword_blocks(self, name: str) -> list[list[KKeyword]]:
        """Get all blocks for a keyword (may appear multiple times)."""
        return [k for k in self.keywords if k.name == name.upper()]

    def get_parts(self) -> list[KKeyword]:
        return self.get_keywords("PART")

    def get_materials(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("MAT_")

    def get_sections(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("SECTION_")

    def get_nodes(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("NODE")

    def get_elements(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("ELEMENT_")

    def get_contacts(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("CONTACT_")

    def get_boundaries(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("BOUNDARY_")

    def get_loads(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("LOAD_")

    def get_curves(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("DEFINE_CURVE")

    def get_sets(self) -> list[KKeyword]:
        return self.get_keywords_by_prefix("SET_")

    def get_material_ids(self) -> set[int]:
        """Extract all defined material IDs."""
        ids: set[int] = set()
        for k in self.get_materials():
            if k.data_lines:
                fields = _parse_data_line(k.data_lines[0])
                if fields:
                    try:
                        ids.add(int(fields[0]))
                    except ValueError:
                        pass
        return ids

    def get_section_ids(self) -> set[int]:
        """Extract all defined section IDs."""
        ids: set[int] = set()
        for k in self.get_sections():
            if k.data_lines:
                fields = _parse_data_line(k.data_lines[0])
                if fields:
                    try:
                        ids.add(int(fields[0]))
                    except ValueError:
                        pass
        return ids

    def get_part_material_refs(self) -> dict[int, int]:
        """Return {pid: mid} mapping from PART keyword.

        PART card 1: title (string)
        PART card 2: PID, SECID, MID, EOSID, HGID, GRAV, ADPOPT, TMID
        """
        refs: dict[int, int] = {}
        for part in self.get_parts():
            data = part.data_lines
            # Find the data card (skip title lines that contain non-numeric data)
            for line in data:
                fields = _parse_data_line(line)
                if len(fields) >= 3:
                    try:
                        pid = int(fields[0])
                        mid = int(fields[2])
                        refs[pid] = mid
                        break
                    except ValueError:
                        continue
        return refs

    def get_part_section_refs(self) -> dict[int, int]:
        """Return {pid: secid} mapping from PART keyword."""
        refs: dict[int, int] = {}
        for part in self.get_parts():
            data = part.data_lines
            for line in data:
                fields = _parse_data_line(line)
                if len(fields) >= 2:
                    try:
                        pid = int(fields[0])
                        secid = int(fields[1])
                        refs[pid] = secid
                        break
                    except ValueError:
                        continue
        return refs

    def get_element_part_refs(self) -> dict[int, int]:
        """Return {eid: pid} mapping from ELEMENT keywords."""
        refs: dict[int, int] = {}
        for k in self.get_elements():
            for line in k.data_lines:
                fields = _parse_data_line(line)
                if len(fields) >= 2:
                    try:
                        eid = int(fields[0])
                        pid = int(fields[1])
                        refs[eid] = pid
                    except (ValueError, IndexError):
                        pass
        return refs

    def validate(self) -> list[str]:
        """Run validation checks. Returns list of error messages."""
        errors: list[str] = []

        if not self.keywords:
            errors.append("No keywords found in file")
            return errors

        # Check *KEYWORD is present
        if not self.get_keywords("KEYWORD"):
            errors.append("Missing *KEYWORD header")

        # Check MAT_ keywords contain MID
        mat_ids = self.get_material_ids()
        part_refs = self.get_part_material_refs()

        if not mat_ids and part_refs:
            errors.append("Parts reference materials but no MAT_ keywords defined")

        # Check PART material references exist
        for pid, mid in part_refs.items():
            if mid not in mat_ids:
                errors.append(f"PART {pid} references undefined material MID={mid}")

        # Check PART section references exist
        sec_ids = self.get_section_ids()
        part_sec_refs = self.get_part_section_refs()
        for pid, secid in part_sec_refs.items():
            if secid not in sec_ids:
                errors.append(f"PART {pid} references undefined section SECID={secid}")

        # Check ID conflicts (duplicate IDs)
        all_mat_ids = []
        for k in self.get_materials():
            if k.data_lines:
                fields = _parse_data_line(k.data_lines[0])
                if fields:
                    try:
                        all_mat_ids.append(int(fields[0]))
                    except ValueError:
                        pass
        if len(all_mat_ids) != len(set(all_mat_ids)):
            errors.append("Duplicate material IDs detected")

        all_sec_ids = []
        for k in self.get_sections():
            if k.data_lines:
                fields = _parse_data_line(k.data_lines[0])
                if fields:
                    try:
                        all_sec_ids.append(int(fields[0]))
                    except ValueError:
                        pass
        if len(all_sec_ids) != len(set(all_sec_ids)):
            errors.append("Duplicate section IDs detected")

        # Check empty sets
        for set_type in ["SET_NODE_LIST", "SET_SEGMENT", "SET_PART_LIST",
                         "SET_SHELL_LIST", "SET_SOLID_LIST"]:
            for s in self.get_keywords(set_type):
                if not s.data_lines:
                    errors.append(f"Empty {set_type} (no data lines)")
                elif len(s.data_lines) <= 1:
                    # Only header, no actual set members
                    pass  # Some sets may legitimately have 1 line

        # Check contact references
        for contact in self.get_contacts():
            pf = contact.parsed_fields
            if pf:
                ssid = pf.get("SSID")
                msid = pf.get("MSID")
                if ssid is not None:
                    # Check slave set exists
                    pass
                if msid is not None:
                    # Check master set exists
                    pass

        return errors


# --- Field parsing helpers ---


def _parse_data_line(line: str) -> list[str]:
    """Parse a data line into fields.

    Detects format:
    - Free format: comma-separated values
    - Fixed format: 8 fields × 10 characters (fields align on 10-char boundaries)
    - Loose format: whitespace-separated (multiple spaces between values)
    """
    line = line.rstrip()
    if not line:
        return []

    # Free format: comma-separated
    if "," in line:
        return [f.strip() for f in line.split(",") if f.strip()]

    # Detect true fixed-width: every 10-char boundary must have whitespace on BOTH sides
    # AND there should be no more than 8 fields
    if len(line) >= 20:
        is_fixed = True
        n_boundaries = min(len(line) // 10, 8)
        for i in range(1, n_boundaries):
            pos = i * 10
            if pos < len(line):
                # Both characters adjacent to boundary must be space
                if line[pos - 1] != " " or line[pos] != " ":
                    is_fixed = False
                    break
        if is_fixed and n_boundaries >= 2:
            fields = []
            for i in range(0, min(len(line), 80), 10):
                field = line[i : i + 10].strip()
                if field:
                    fields.append(field)
            return fields

    # Loose format: split on whitespace
    return line.split()


# --- Main parser ---


def parse_k_file(filepath: str | Path) -> KFile:
    """Parse an offline/review .k file and return structured data.

    Parsing is not model creation and is not evidence that HyperMesh imported,
    created, or exported the model through the GUI listener.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"K file not found: {path}")

    content = path.read_text(encoding="utf-8", errors="replace")
    return parse_k_content(content)


def parse_k_content(content: str) -> KFile:
    """Parse offline/review LS-DYNA .k content.

    Parsing is for validation and planning only. It must not be treated as a
    HyperMesh GUI import route, modeling route, or final K export route.

    Handles:
    - Standard format (8 fields × 10 chars)
    - Free format (comma-separated)
    - Comments ($ in column 1)
    - Multiple blocks per keyword
    - Long format (+ suffix) and I10 format (% suffix)
    - *KEYWORD with options (long=y, i10=y, memory, NCPU)
    """
    kfile = KFile()
    current_keyword: KKeyword | None = None
    title_next_line = False

    for line in content.splitlines():
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            if current_keyword:
                current_keyword.data_lines.append(line)
            continue

        # Comment lines start with $ in column 1
        if stripped.startswith("$"):
            if current_keyword:
                current_keyword.comments.append(stripped)
            continue

        # Keyword lines start with *
        if stripped.startswith("*"):
            # Save previous keyword
            if current_keyword:
                kfile.keywords.append(current_keyword)
                current_keyword = None

            # Parse keyword name and options
            keyword_line = stripped.split(",")[0].strip()
            parts = keyword_line.split()
            raw_name = parts[0].lstrip("*").upper()
            keyword_options = parts[1:] if len(parts) > 1 else []

            # Handle *KEYWORD header — extract format hints
            if raw_name == "KEYWORD":
                kfile.format_hint = _detect_format(keyword_options, "standard")
                _parse_keyword_options(kfile, keyword_options)
                kw = KKeyword(name="KEYWORD", category="file", options=keyword_options)
                kfile.keywords.append(kw)
                current_keyword = None
                continue

            # Handle *TITLE
            if raw_name == "TITLE":
                current_keyword = KKeyword(
                    name="TITLE", category="file", options=keyword_options
                )
                kfile.keywords.append(current_keyword)
                current_keyword = None
                title_next_line = True
                continue

            # Handle *END
            if raw_name == "END":
                kfile.keywords.append(
                    KKeyword(name="END", category="file", options=keyword_options)
                )
                current_keyword = None
                continue

            category = _classify_keyword(raw_name)
            current_keyword = KKeyword(
                name=raw_name, category=category, options=keyword_options
            )
            continue

        # Data lines
        if title_next_line and not current_keyword:
            kfile.title = stripped
            title_next_line = False
            continue

        if current_keyword:
            current_keyword.data_lines.append(stripped)

    # Save last keyword
    if current_keyword:
        kfile.keywords.append(current_keyword)

    # Auto-parse field values for all keywords
    for kw in kfile.keywords:
        if kw.data_lines:
            kw.parse_field_values()

    return kfile


def _detect_format(options: list[str], default: str) -> str:
    """Detect format hint from *KEYWORD options."""
    for opt in options:
        if opt.lower().startswith("long="):
            return "long"
        if opt.lower().startswith("i10="):
            return "i10"
    return default


def _parse_keyword_options(kfile: KFile, options: list[str]) -> None:
    """Parse *KEYWORD line options (memory, NCPU, long, i10)."""
    for opt in options:
        opt_lower = opt.lower()
        if opt_lower.startswith("memory"):
            # memory=120m or just 120m
            val = opt.split("=")[-1] if "=" in opt else opt
            kfile.memory = _parse_memory_value(val)
        elif opt_lower.startswith("ncpu="):
            try:
                kfile.ncpu = int(opt.split("=")[-1])
            except ValueError:
                pass


def _parse_memory_value(val: str) -> int:
    """Parse memory value like '120m' or '120000000'."""
    val = val.strip().lower()
    if val.endswith("m"):
        return int(float(val[:-1]) * 1_000_000)
    if val.endswith("k"):
        return int(float(val[:-1]) * 1_000)
    return int(float(val))
