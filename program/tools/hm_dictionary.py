"""HyperMesh LS-DYNA dictionary validator.

Validates cardimage and dataname against the official HyperMesh LS-DYNA profile
extracted from dyna971_R93.key. Used to prevent agent from guessing invalid
cardimage/dataname values.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DICT_PATH = Path(__file__).resolve().parents[2] / "templates" / "hm_dictionary.json"

_dictionary: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _dictionary
    if _dictionary is None:
        if _DICT_PATH.exists():
            _dictionary = json.loads(_DICT_PATH.read_text(encoding="utf-8"))
        else:
            _dictionary = {"cardmenuitem": {}, "mats": {}, "props": {}, "lsd_fields": {}, "all_cardimages": []}
    return _dictionary


def is_valid_cardimage(cardimage: str) -> bool:
    """Check if a cardimage is valid in the HyperMesh LS-DYNA profile."""
    d = _load()
    return cardimage in d.get("all_cardimages", [])


def get_cardimage_for_keyword(keyword: str) -> str | None:
    """Get the correct HyperMesh cardimage for an LS-DYNA keyword.

    Args:
        keyword: LS-DYNA keyword (e.g., "MAT_ELASTIC", "CONTROL_TERMINATION")

    Returns:
        HyperMesh cardimage (e.g., "MATL1", "Termin") or None if not found.
    """
    d = _load()
    return d.get("cardmenuitem", {}).get(keyword.upper().lstrip("*"))


def get_material_category(cardimage: str) -> str | None:
    """Get material category for a cardimage."""
    d = _load()
    return d.get("mats", {}).get(cardimage)


def get_property_category(cardimage: str) -> str | None:
    """Get property category for a cardimage."""
    d = _load()
    return d.get("props", {}).get(cardimage)


def get_lsd_fields(cardimage: str) -> dict[str, str]:
    """Get LSD_* dataname mappings for a cardimage.

    Returns:
        Dict mapping field name to LSD_* dataname (e.g., {"ENDTIM": "LSD_ENDTIM"}).
    """
    d = _load()
    return d.get("lsd_fields", {}).get(cardimage, {})


def validate_cardimage_in_script(script: str) -> str | None:
    """Check if a Tcl script uses an invalid cardimage.

    Scans for cardimage=xxx patterns and validates against the dictionary.

    Returns:
        Error message with correction hint, or None if valid.
    """
    import re

    d = _load()
    all_cardimages = set(d.get("all_cardimages", []))

    # Find all cardimage=xxx patterns
    for m in re.finditer(r'cardimage=(\w+)', script):
        cardimage = m.group(1)
        if cardimage not in all_cardimages:
            # Try to find the correct cardimage
            hint = ""
            keyword = cardimage.upper()
            correct = d.get("cardmenuitem", {}).get(keyword)
            if correct:
                hint = f" '{keyword}' should use cardimage='{correct}'"
            return (
                f"Invalid cardimage: '{cardimage}'. "
                f"Not found in HyperMesh LS-DYNA profile.{hint}"
            )

    return None


def validate_dataname_in_script(script: str) -> str | None:
    """Check if a Tcl script uses invalid dataname for known cardimages.

    Scans for *setvalue patterns and validates dataname against LSD_* fields.

    Returns:
        Error message with correction hint, or None if valid.
    """
    import re

    d = _load()
    lsd_fields = d.get("lsd_fields", {})

    # Find *setvalue entity id=X dataname=FIELD value=V
    for m in re.finditer(r'\*setvalue\s+\w+\s+id=\S+\s+dataname=(\w+)', script):
        dataname = m.group(1)
        # Skip if it's a known LSD_ field for any card
        is_known = False
        for card_fields in lsd_fields.values():
            if dataname in card_fields.values() or dataname in card_fields:
                is_known = True
                break
        # Also skip common HyperMesh datanames
        common = {"Rho", "E", "Nu", "Yield", "Etan", "thickness", "propertyid", "materialid", "STATUS"}
        if dataname in common:
            is_known = True
        if not is_known:
            return f"Unknown dataname: '{dataname}'. May not be valid for this cardimage."

    return None


def dictionary_stats() -> dict[str, int]:
    """Return dictionary statistics."""
    d = _load()
    return {
        "cardmenuitem": len(d.get("cardmenuitem", {})),
        "mats": len(d.get("mats", {})),
        "props": len(d.get("props", {})),
        "lsd_fields": len(d.get("lsd_fields", {})),
        "all_cardimages": len(d.get("all_cardimages", [])),
    }
