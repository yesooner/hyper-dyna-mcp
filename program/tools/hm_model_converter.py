"""Blocked compatibility helpers for LS-DYNA profile/card conversion.

The current MCP scope is HyperMesh GUI-only plus verified command-map routes.
Bulk LS-DYNA template activation, material card-image conversion, and property
card-image conversion are not verified execution routes. This module keeps the
legacy function names importable, but every conversion-oriented entry returns a
blocked payload and sends no Tcl.
"""

from __future__ import annotations

from typing import Any

from program.tools.hm_gui import DEFAULT_GUI_HOST, DEFAULT_GUI_PORT

_ERROR_TYPE = "lsdyna_profile_conversion_not_verified"


def _blocked_conversion_result(action: str, **requested: Any) -> dict[str, Any]:
    return {
        "success": False,
        "error_type": _ERROR_TYPE,
        "error": (
            "LS-DYNA profile/card conversion is blocked until template activation, "
            "material card assignment, and property card assignment are verified "
            "through command recording and command-map promotion."
        ),
        "action": action,
        "execution_allowed": False,
        "tcl_sent": False,
        "required_tool": "hm_modeling_action",
        "required_routes": [
            "assign_material_to_hex_part",
            "assign_material_to_shell_part",
            "assign_material_to_beam_part",
            "assign_material_to_tet_part",
        ],
        "next_supported_actions": [
            {"tool": "hm_modeling_action", "action": "recording_requirements", "route_name": "assign_material_to_hex_part"},
            {"tool": "hm_modeling_action", "action": "validate_recording", "route_name": "assign_material_to_hex_part"},
        ],
        "policy": "Do not use hm_convert_model or hm_model_converter helpers to bypass dyna_keyword_query, hm_modeling_action, or verified command-map routes.",
        "requested": requested,
    }


def check_connection(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict[str, Any]:
    """Return a blocked compatibility result.

    Use the MCP `check_hypermesh_connection` tool or `diagnose_hypermesh_listener`
    for listener checks. The converter module must not perform socket/Tcl work.
    """
    return _blocked_conversion_result("check_connection", host=host, port=port)


def get_material_ids(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict[str, Any]:
    """Return blocked result; use `hm_read_materials` for read-only material queries."""
    return _blocked_conversion_result("get_material_ids", host=host, port=port)


def get_property_ids(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict[str, Any]:
    """Return blocked result; use `hm_read_components` or verified readers instead."""
    return _blocked_conversion_result("get_property_ids", host=host, port=port)


def find_lsdyna_template(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict[str, Any]:
    """Return blocked result; template activation is not a verified route."""
    return _blocked_conversion_result("find_lsdyna_template", host=host, port=port)


def convert_materials_to_lsdyne(
    card_image: str = "MAT_ELASTIC",
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
    timeout: int = 30,
) -> dict[str, Any]:
    """Return blocked result for legacy material card-image conversion callers."""
    return _blocked_conversion_result(
        "convert_materials_to_lsdyne",
        card_image=card_image,
        host=host,
        port=port,
        timeout=timeout,
    )


def convert_properties_to_lsdyne(
    card_image: str = "SECTION_SOLID",
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
) -> dict[str, Any]:
    """Return blocked result for legacy property card-image conversion callers."""
    return _blocked_conversion_result(
        "convert_properties_to_lsdyne",
        card_image=card_image,
        host=host,
        port=port,
    )


def verify_conversion(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict[str, Any]:
    """Return blocked result; conversion verification is not meaningful before promotion."""
    return _blocked_conversion_result("verify_conversion", host=host, port=port)


def convert_model_to_lsdyne(
    mat_card: str = "MAT_ELASTIC",
    prop_card: str = "SECTION_SOLID",
    verify: bool = True,
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
) -> dict[str, Any]:
    """Return blocked result for the legacy model conversion workflow."""
    return _blocked_conversion_result(
        "convert_model_to_lsdyne",
        mat_card=mat_card,
        prop_card=prop_card,
        verify=verify,
        host=host,
        port=port,
    )
