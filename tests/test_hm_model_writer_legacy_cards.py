"""Guardrails for legacy card helpers in hm_model_writer."""

from __future__ import annotations

from program.tools import hm_model_writer


def _fail_execute(*args, **kwargs):
    raise AssertionError("legacy card helper must not execute Tcl")


def _assert_blocked(result: dict, route_name: str) -> None:
    assert result["success"] is False
    assert result["error_type"] == "dyna_card_route_not_verified"
    assert result["blocked_route_name"] == route_name
    assert result["blocked_route_status"] == "unsupported"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_modeling_action"
    assert result["next_supported_actions"][0]["action"] == "recording_requirements"
    assert result["next_supported_actions"][1]["action"] == "validate_recording"


def test_legacy_material_property_helpers_are_blocked(monkeypatch):
    monkeypatch.setattr(hm_model_writer, "_execute_script", _fail_execute)

    calls = [
        hm_model_writer.set_material(1, "MAT_ELASTIC", {"E": 210000}),
        hm_model_writer.create_material("steel", "MAT_ELASTIC", {"E": 210000}),
        hm_model_writer.set_property(1, "SECTION_SOLID", {"ELFORM": 1}),
        hm_model_writer.create_property("solid_section", "SECTION_SOLID", {"ELFORM": 1}),
        hm_model_writer.assign_material_to_component(1, 1),
        hm_model_writer.assign_property_to_component(1, 1),
    ]

    for result in calls:
        _assert_blocked(result, "assign_material_to_hex_part")


def test_legacy_batch_material_property_helpers_are_blocked(monkeypatch):
    monkeypatch.setattr(hm_model_writer, "_execute_script", _fail_execute)

    material_results = hm_model_writer.set_materials(
        [{"mid": 1, "mat_type": "MAT_ELASTIC", "params": {"E": 210000}}],
    )
    property_results = hm_model_writer.set_properties(
        [{"pid": 1, "sec_type": "SECTION_SOLID", "params": {"ELFORM": 1}}],
    )

    assert len(material_results) == 1
    assert len(property_results) == 1
    _assert_blocked(material_results[0], "assign_material_to_hex_part")
    _assert_blocked(property_results[0], "assign_material_to_hex_part")


def test_legacy_contact_boundary_load_control_database_helpers_are_blocked(monkeypatch):
    monkeypatch.setattr(hm_model_writer, "_execute_script", _fail_execute)

    expectations = [
        (
            hm_model_writer.set_contact("AUTOMATIC_SURFACE_TO_SURFACE", {"SSID": 1, "MSID": 2}),
            "mixed_material_assignment",
        ),
        (
            hm_model_writer.set_boundary("SPC", {"NSID": 1, "DOFX": 1}),
            "apply_constraint_spc",
        ),
        (
            hm_model_writer.set_load("NODE", {"LCID": 1, "SF": 1.0}),
            "apply_load_nodal_or_pressure",
        ),
        (
            hm_model_writer.set_control("TERMINATION", {"ENDTIM": 1.0}),
            "mixed_material_assignment",
        ),
        (
            hm_model_writer.set_database("D3PLOT", {"DT": 0.1}),
            "mixed_material_assignment",
        ),
    ]

    for result, route_name in expectations:
        _assert_blocked(result, route_name)
