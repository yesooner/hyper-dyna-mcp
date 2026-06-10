"""Tests for verified HyperMesh Tcl command map."""

import pytest

from program.tools.hm_command_map import (
    command_map_stats,
    get_route_limits,
    get_verified_route,
    load_command_map,
    list_verified_routes,
    require_verified_route,
    validate_command_map,
)
from program.tools.dyna_keyword_map import dyna_keyword_policy_summary, embedding_execution_allowed
from program.tools.hm_model_writer import _build_structured_hex_box_tcl, create_fe_cube
from program.tools.hm_template_engine import HmTemplateEngine


def test_keyword_index_search_is_available():
    engine = HmTemplateEngine()
    results = engine.search_keywords("MAT")

    assert results
    assert any("keyword" in item for item in results)


def test_verified_hex8_route_is_available():
    route = get_verified_route("create_structured_hex8_box")

    assert route is not None
    assert route["status"] == "verified"
    assert route["element_config"] == 208
    assert route["limits"]["max_elements"] > 0
    assert "*createnode" in route["commands"]
    assert "*createlist nodes" in route["commands"]
    assert "*createelement 208" in route["commands"]
    assert route["runtime_validated"] is True
    assert route["verification_level"] == "runtime_validated"


def test_command_map_stats_and_listing():
    stats = command_map_stats()
    routes = list_verified_routes()

    assert stats["verified_routes"] >= 1
    assert stats["runtime_validated_routes"] >= 1
    assert stats["runtime_validated_routes"] <= stats["verified_routes"]
    assert stats["unsupported_routes"] >= 1
    assert stats["map_valid"] is True
    assert stats["map_errors"] == []
    assert any("runtime validation still pending" in warning for warning in stats["map_warnings"])
    assert any(route["name"] == "create_structured_hex8_box" for route in routes)
    assert any(route["name"] == "create_geometry_solid_box" for route in routes)


def test_verified_solid_box_route_is_available():
    route = get_verified_route("create_geometry_solid_box")

    assert route is not None
    assert route["status"] == "verified"
    assert route["entity_kind"] == "geometry_solid"
    assert "*solidblock" in route["commands"]
    assert "hm_entitylist solids id" in route["commands"]
    assert "hm_marklength solids" in route["commands"]
    assert route["runtime_validated"] is False
    assert route["verification_level"] == "source_verified_runtime_pending"
    assert route["tested_in_session"] is False


def test_command_map_template_validates_successfully():
    result = validate_command_map()

    assert result["success"] is True
    assert result["errors"] == []
    assert result["routes_checked"] >= 2


def test_command_map_validator_requires_fe_limits():
    data = load_command_map()
    bad_data = {
        **data,
        "routes": {
            **data["routes"],
            "create_structured_hex8_box": {
                **data["routes"]["create_structured_hex8_box"],
                "limits": {"max_elements": 5000},
            },
        },
    }

    result = validate_command_map(bad_data)

    assert result["success"] is False
    assert any("limits.max_nodes" in error for error in result["errors"])


def test_command_map_validator_rejects_geometry_command_in_fe_route():
    data = load_command_map()
    bad_route = {
        **data["routes"]["create_structured_hex8_box"],
        "commands": [
            *data["routes"]["create_structured_hex8_box"]["commands"],
            "*solidblock",
        ],
    }
    bad_data = {**data, "routes": {**data["routes"], "create_structured_hex8_box": bad_route}}

    result = validate_command_map(bad_data)

    assert result["success"] is False
    assert any("FE route must not contain *solidblock" in error for error in result["errors"])


def test_command_map_validator_requires_solid_runtime_validation():
    data = load_command_map()
    bad_route = {
        **data["routes"]["create_geometry_solid_box"],
        "runtime_validation": [],
    }
    bad_data = {**data, "routes": {**data["routes"], "create_geometry_solid_box": bad_route}}

    result = validate_command_map(bad_data)

    assert result["success"] is False
    assert any("runtime_validation" in error for error in result["errors"])


def test_unsupported_tetmesh_solid_route_is_rejected():
    with pytest.raises(ValueError, match="unsupported"):
        require_verified_route("tetmesh_geometry_solid")


def test_structured_hex_tcl_uses_verified_route_commands():
    script = _build_structured_hex_box_tcl(
        comp_name="soil_cube",
        x_min=0.0,
        y_min=0.0,
        z_min=0.0,
        x_max=1.0,
        y_max=1.0,
        z_max=1.0,
        nx=1,
        ny=1,
        nz=1,
    )

    assert "*createnode" in script
    assert "*createlist nodes 1" in script
    assert "*createelement 208 1 1 1" in script
    assert "*solidblock" not in script
    assert "*tetmesh" not in script


def test_dyna_manual_embedding_is_not_execution_source():
    summary = dyna_keyword_policy_summary()

    assert embedding_execution_allowed() is False
    assert summary["embedding_execution_allowed"] is False
    assert "keyword" in summary["lookup_flow"]
    assert "manual_notes" in summary["sources"]


def test_route_limits_are_exposed():
    limits = get_route_limits("create_structured_hex8_box")

    assert limits["max_elements"] == 5000
    assert limits["max_nodes"] == 8000


def test_oversized_fe_cube_is_rejected_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": ""}

    monkeypatch.setattr("program.tools.hm_model_writer.execute_tcl_gui", fake_execute_tcl_gui)

    result = create_fe_cube("too_big", size=100.0, element_size=1.0)

    assert result["success"] is False
    assert result["stage"] == "create_box"
    assert result["box"]["error_type"] == "mesh_size_limit"
    assert called is False
