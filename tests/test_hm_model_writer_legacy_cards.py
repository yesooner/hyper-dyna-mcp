"""Guardrails for legacy card helpers in hm_model_writer."""

from __future__ import annotations

from program.tools import hm_keyword_skill, hm_model_writer


def _ok_execute(*args, **kwargs):
    return {"success": True, "response": "OK"}


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


def test_legacy_material_property_helpers_execute_gui_templates(monkeypatch):
    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", _ok_execute)
    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", _ok_execute)

    calls = [
        hm_model_writer.set_material(1, "MAT_ELASTIC", {"RHO": 7.85e-6, "E": 210000, "PR": 0.3}),
        hm_model_writer.create_material("steel", "MAT_ELASTIC", {"MID": 2, "RHO": 7.85e-6, "E": 210000, "PR": 0.3}),
        hm_model_writer.set_property(1, "SECTION_SOLID", {"ELFORM": 1}),
        hm_model_writer.create_property("solid_section", "SECTION_SOLID", {"ELFORM": 1}),
        hm_model_writer.assign_material_to_component(1, 1),
        hm_model_writer.assign_property_to_component(1, 1),
    ]

    for result in calls:
        assert result["success"] is True
        assert result["execution_allowed"] is True
        assert result["tcl_sent"] is True


def test_legacy_batch_material_property_helpers_execute_gui_templates(monkeypatch):
    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", _ok_execute)

    material_results = hm_model_writer.set_materials(
        [{"mid": 1, "mat_type": "MAT_ELASTIC", "params": {"RHO": 7.85e-6, "E": 210000, "PR": 0.3}}],
    )
    property_results = hm_model_writer.set_properties(
        [{"pid": 1, "sec_type": "SECTION_SOLID", "params": {"ELFORM": 1}}],
    )

    assert len(material_results) == 1
    assert len(property_results) == 1
    assert material_results[0]["success"] is True
    assert property_results[0]["success"] is True


def test_legacy_contact_control_database_helpers_remain_blocked(monkeypatch):

    expectations = [
        (
            hm_model_writer.set_contact("AUTOMATIC_SURFACE_TO_SURFACE", {"SSID": 1, "MSID": 2}),
            "mixed_material_assignment",
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


def test_legacy_boundary_and_load_helpers_execute_gui_templates(monkeypatch):
    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", _ok_execute)

    boundary = hm_model_writer.set_boundary(
        "SPC",
        {"NODEID": 1, "CID": 0, "DOFX": 1, "DOFY": 1, "DOFZ": 1, "DOFRX": 0, "DOFRY": 0, "DOFRZ": 0},
    )
    load = hm_model_writer.set_load(
        "NODE",
        {"NID": 1, "DOF": 3, "LCID": 1, "SF": 1.0, "CID": 0, "M1": 0.0, "M2": 0.0, "M3": -1.0},
    )

    assert boundary["success"] is True
    assert load["success"] is True
