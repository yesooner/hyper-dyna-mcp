"""Tests for verified HyperMesh Tcl command map."""

import pytest

from program.tools.hm_command_map import (
    canonical_element_type,
    command_map_stats,
    element_capability_matrix,
    known_element_types,
    get_experimental_route,
    get_route_limits,
    get_verified_route,
    load_command_map,
    list_verified_routes,
    require_executable_route,
    require_verified_route,
    validate_command_map,
)
from program.tools.dyna_keyword_map import dyna_keyword_policy_summary, embedding_execution_allowed
from program.tools.hm_model_writer import (
    _build_direct_element_tcl,
    _build_discrete_spring_tcl,
    _build_lumped_mass_tcl,
    _build_structured_beam_line_tcl,
    _build_structured_hex_box_tcl,
    _build_structured_quad4_shell_plate_tcl,
    create_fe_cube,
)
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
    assert stats["experimental_routes"] == 0
    assert stats["map_valid"] is True
    assert stats["map_errors"] == []
    assert any(route["name"] == "create_structured_hex8_box" for route in routes)
    assert any(route["name"] == "create_structured_quad4_shell_plate" for route in routes)
    assert any(route["name"] == "create_beam_line" for route in routes)
    assert any(route["name"] == "create_discrete_element" for route in routes)
    assert any(route["name"] == "create_lumped_mass" for route in routes)
    assert any(route["name"] == "create_geometry_solid_box" for route in routes)
    assert any(route["name"] == "create_geometry_surface_rect_nurbs" for route in routes)


def test_geometry_solid_route_is_verified_and_executable():
    route = get_verified_route("create_geometry_solid_box")
    experimental = get_experimental_route("create_geometry_solid_box")

    assert experimental is None
    assert route is not None
    assert route["status"] == "verified"
    assert route["entity_kind"] == "geometry_solid"
    assert "*solidblock" in route["commands"]
    assert "hm_entitylist solids id" in route["commands"]
    assert "hm_marklength solids" in route["commands"]
    assert route["tested_in_session"] is True
    assert route["runtime_validated"] is True
    assert route["mcp_execution_allowed"] is True
    assert route["agent_execution_allowed"] is True
    assert require_executable_route("create_geometry_solid_box")["status"] == "verified"


def test_verified_quad4_shell_plate_route_is_available():
    route = get_verified_route("create_structured_quad4_shell_plate")

    assert route is not None
    assert route["status"] == "verified"
    assert route["entity_kind"] == "fe_mesh"
    assert route["element_config"] == 104
    assert route["limits"]["max_elements"] > 0
    assert "*createnode" in route["commands"]
    assert "*createlist nodes" in route["commands"]
    assert "*createelement 104" in route["commands"]
    assert route["runtime_validated"] is True
    assert route["verification_level"] == "runtime_validated"
    assert route["tested_in_session"] is True


def test_verified_beam_line_route_is_available():
    route = get_verified_route("create_beam_line")

    assert route is not None
    assert route["status"] == "verified"
    assert route["entity_kind"] == "fe_mesh"
    assert route["element_config"] == 60
    assert "*linecreatestraight" in route["commands"]
    assert "*createnode" in route["commands"]
    assert "*createlist nodes" in route["commands"]
    assert "*createelement 60" in route["commands"]
    assert "hm_getvalue elements id typename" in route["commands"]
    assert route["runtime_validated"] is True
    assert route["verification_level"] == "runtime_validated"


def test_verified_discrete_and_mass_routes_are_available():
    discrete = get_verified_route("create_discrete_element")
    lumped = get_verified_route("create_lumped_mass")

    assert discrete is not None
    assert discrete["status"] == "verified"
    assert discrete["entity_kind"] == "fe_mesh"
    assert discrete["element_config"] == 21
    assert "*spring" in discrete["commands"]
    assert discrete["runtime_validated"] is True
    assert discrete["verification_level"] == "runtime_validated"

    assert lumped is not None
    assert lumped["status"] == "verified"
    assert lumped["entity_kind"] == "fe_mesh"
    assert lumped["element_config"] == 1
    assert "*createmark nodes" in lumped["commands"]
    assert "*masselement" in lumped["commands"]
    assert lumped["runtime_validated"] is True
    assert lumped["verification_level"] == "runtime_validated"


def test_verified_surface_plate_route_is_available():
    route = get_verified_route("create_geometry_surface_rect_nurbs")

    assert route is not None
    assert route["status"] == "verified"
    assert route["entity_kind"] == "geometry_surface"
    assert "*createdoublearray" in route["commands"]
    assert "*surfacecreatenurbs" in route["commands"]
    assert "hm_entitylist surfaces id" in route["commands"]
    assert route["runtime_validated"] is True
    assert route["verification_level"] == "runtime_validated"
    assert route["tested_in_session"] is True


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
        "status": "verified",
        "runtime_validation": [],
    }
    bad_data = {**data, "routes": {**data["routes"], "create_geometry_solid_box": bad_route}}

    result = validate_command_map(bad_data)

    assert result["success"] is False
    assert any("runtime_validation" in error for error in result["errors"])


def test_command_map_validator_blocks_runtime_pending_geometry_solid_execution():
    data = load_command_map()
    bad_route = {
        **data["routes"]["create_geometry_solid_box"],
        "tested_in_session": False,
        "mcp_execution_allowed": True,
    }
    bad_data = {**data, "routes": {**data["routes"], "create_geometry_solid_box": bad_route}}

    result = validate_command_map(bad_data)

    assert result["success"] is False
    assert any("mcp_execution_allowed=false" in error for error in result["errors"])


def test_unsupported_tetmesh_solid_route_is_rejected():
    with pytest.raises(ValueError, match="unsupported"):
        require_verified_route("tetmesh_geometry_solid")


def test_verified_geometry_solid_route_is_executable():
    assert require_executable_route("create_geometry_solid_box")["status"] == "verified"


def test_element_capability_matrix_answers_requested_element_families():
    result = element_capability_matrix()

    assert result["success"] is True
    assert result["summary"]["types_checked"] == 8
    assert result["summary"]["creation_supported"] == [
        "discrete",
        "line_beam",
        "lumped_mass",
        "shell_quad",
        "shell_tria",
        "solid_hex",
        "solid_tet",
    ]
    assert result["summary"]["geometry_surface_creation_supported"] == ["shell_quad"]
    assert result["summary"]["meshing_supported"] == ["solid_hex"]
    assert result["summary"]["material_assignment_supported"] == [
        "discrete",
        "line_beam",
        "lumped_mass",
        "shell_quad",
        "shell_tria",
        "solid_hex",
        "solid_tet",
    ]
    assert result["summary"]["k_file_generation_supported"] == ["line_beam", "shell_quad", "solid_hex"]
    assert result["summary"]["offline_k_file_generation_supported"] == ["line_beam", "shell_quad", "solid_hex"]
    assert result["summary"]["k_file_generation_agent_execution_allowed"] == []
    assert result["summary"]["k_file_generation_mcp_execution_allowed"] == []
    assert result["summary"]["final_k_export_supported"] == []
    assert result["summary"]["hypermesh_gui_k_export_supported"] == []

    caps = result["capabilities"]
    assert caps["solid_hex"]["creation"]["supported"] is True
    assert caps["solid_hex"]["creation"]["tool"] == "hm_create_fe_cube"
    assert caps["solid_hex"]["meshing"]["route_name"] == "create_structured_hex8_box"
    assert caps["solid_hex"]["material_assignment"]["supported"] is True
    assert caps["solid_tet"]["creation"]["supported"] is True
    assert caps["solid_tet"]["creation"]["tool"] == "hm_create_tet4"
    assert caps["solid_tet"]["creation"]["route_status"] == "verified"
    assert caps["solid_tet"]["creation"]["runtime_validated"] is False
    assert caps["solid_tet"]["meshing"]["route_status"] == "unsupported"
    assert caps["shell_quad"]["creation"]["supported"] is True
    assert caps["shell_quad"]["creation"]["tool"] == "hm_create_shell_plate"
    assert caps["shell_quad"]["creation"]["route_name"] == "create_structured_quad4_shell_plate"
    assert caps["shell_quad"]["creation"]["route_status"] == "verified"
    assert caps["shell_quad"]["creation"]["runtime_validated"] is True
    assert caps["shell_quad"]["meshing"]["route_status"] == "unsupported"
    assert caps["shell_quad"]["geometry_surface_creation"]["supported"] is True
    assert caps["shell_quad"]["geometry_surface_creation"]["tool"] == "hm_create_surface_plate"
    assert caps["shell_quad"]["geometry_surface_creation"]["route_status"] == "verified"
    assert caps["shell_quad"]["geometry_surface_creation"]["runtime_validated"] is True
    assert caps["shell_quad"]["k_file_generation"]["supported"] is True
    assert caps["shell_quad"]["k_file_generation"]["fixture_available"] is True
    assert caps["shell_quad"]["k_file_generation"]["role"] == "offline_fixture_validation_only"
    assert caps["shell_quad"]["k_file_generation"]["agent_execution_allowed"] is False
    assert caps["shell_quad"]["k_file_generation"]["mcp_execution_allowed"] is False
    assert caps["shell_quad"]["k_file_generation"]["final_k_export_allowed"] is False
    assert caps["shell_quad"]["k_file_generation"]["hypermesh_gui_export_route"] is False
    assert caps["shell_quad"]["k_file_generation"]["preferred_modeling_path"] == "HyperMesh GUI Tcl listener / Tcl Console"
    assert "*ELEMENT_SHELL_THICKNESS" in caps["shell_quad"]["k_file_generation"]["keywords"]
    assert caps["shell_tria"]["creation"]["supported"] is True
    assert caps["shell_tria"]["creation"]["tool"] == "hm_create_tria3"
    assert caps["shell_tria"]["creation"]["route_status"] == "verified"
    assert caps["shell_tria"]["creation"]["runtime_validated"] is False
    assert caps["shell_tria"]["meshing"]["route_status"] == "unsupported"
    assert caps["line_beam"]["creation"]["supported"] is True
    assert caps["line_beam"]["creation"]["tool"] == "hm_create_beam_line"
    assert caps["line_beam"]["creation"]["route_name"] == "create_beam_line"
    assert caps["line_beam"]["creation"]["route_status"] == "verified"
    assert caps["line_beam"]["creation"]["runtime_validated"] is True
    assert caps["line_beam"]["meshing"]["supported"] is False
    assert caps["line_beam"]["meshing"]["route_name"] == "line_mesh_beam"
    assert caps["line_beam"]["meshing"]["route_status"] == "unsupported"
    assert "existing" in caps["line_beam"]["meshing"]["reason"]
    assert caps["lumped_mass"]["creation"]["supported"] is True
    assert caps["lumped_mass"]["creation"]["tool"] == "hm_create_lumped_mass"
    assert caps["lumped_mass"]["creation"]["route_status"] == "verified"
    assert caps["lumped_mass"]["creation"]["runtime_validated"] is True
    assert caps["lumped_mass"]["meshing"]["route_status"] == "unsupported"
    assert caps["lumped_mass"]["material_assignment"]["route_status"] == "verified"
    assert caps["discrete"]["creation"]["supported"] is True
    assert caps["discrete"]["creation"]["tool"] == "hm_create_discrete_spring"
    assert caps["discrete"]["creation"]["route_status"] == "verified"
    assert caps["discrete"]["creation"]["runtime_validated"] is True
    assert caps["discrete"]["meshing"]["route_status"] == "unsupported"
    assert caps["discrete"]["material_assignment"]["route_status"] == "verified"
    assert caps["mixed"]["creation"]["supported"] is False
    assert caps["mixed"]["creation"]["route_status"] == "unsupported"
    assert caps["mixed"]["meshing"]["supported"] is False
    assert caps["mixed"]["meshing"]["route_name"] == "mixed_mesh_workflow"
    assert caps["mixed"]["meshing"]["route_status"] == "unsupported"
    assert "transition" in " ".join(caps["mixed"]["meshing"]["required_verification"]).lower()
    assert caps["mixed"]["material_assignment"]["route_status"] == "unsupported"


def test_element_capability_matrix_accepts_aliases_and_rejects_unknown():
    hex_result = element_capability_matrix("HEX")
    tet_result = element_capability_matrix("solid element")
    bar_result = element_capability_matrix("bar2")
    spring_result = element_capability_matrix("spring")
    typo_result = element_capability_matrix("district")
    mixed_result = element_capability_matrix("mixed")
    unknown = element_capability_matrix("pyramid")

    assert hex_result["success"] is True
    assert hex_result["canonical_type"] == "solid_hex"
    assert tet_result["success"] is True
    assert tet_result["canonical_type"] == "solid_hex"
    assert bar_result["success"] is True
    assert bar_result["canonical_type"] == "line_beam"
    assert spring_result["success"] is True
    assert spring_result["canonical_type"] == "discrete"
    assert typo_result["success"] is True
    assert typo_result["canonical_type"] == "discrete"
    assert mixed_result["success"] is True
    assert mixed_result["canonical_type"] == "mixed"
    assert mixed_result["capability"]["meshing"]["route_status"] == "unsupported"
    assert unknown["success"] is False
    assert unknown["known"] is False


def test_canonical_element_type_is_single_alias_source_for_modeling():
    assert canonical_element_type(None) is None
    assert canonical_element_type("HEX8") == "solid_hex"
    assert canonical_element_type("solid element") == "solid_hex"
    assert canonical_element_type("bar2") == "line_beam"
    assert canonical_element_type("spring") == "discrete"
    assert canonical_element_type("district") == "discrete"
    assert canonical_element_type("pyramid") == "pyramid"
    assert "solid_hex" in known_element_types()
    assert "pyramid" not in known_element_types()


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


def test_structured_quad4_shell_plate_tcl_uses_verified_route_commands():
    script = _build_structured_quad4_shell_plate_tcl(
        comp_name="shell_plate",
        width=200.0,
        height=100.0,
        origin_x=0.0,
        origin_y=0.0,
        origin_z=0.0,
        nx=10,
        ny=5,
    )

    assert '*collectorcreateonly comps "shell_plate" "" 7' in script
    assert "*createnode 0 0 0 0 0 0" in script
    assert "*createnode 200 100 0 0 0 0" in script
    assert "*createlist nodes 1" in script
    assert "*createelement 104 1 1 1" in script
    assert 'puts "SHELL_NODE_COUNT=[llength $_hdm_shell_nodes]"' in script
    assert 'puts "SHELL_ELEM_COUNT=$_hdm_shell_elem_count"' in script
    assert "*surfacecreatenurbs" not in script
    assert "*solidblock" not in script
    assert "*tetmesh" not in script


def test_structured_beam_line_tcl_uses_verified_route_commands():
    script = _build_structured_beam_line_tcl(
        comp_name="beam_line",
        length=500.0,
        origin_x=0.0,
        origin_y=0.0,
        origin_z=0.0,
        direction_x=1.0,
        direction_y=0.0,
        direction_z=0.0,
        divisions=10,
    )

    assert '*collectorcreateonly comps "beam_line" "" 7' in script
    assert "*linecreatestraight 0 0 0 500 0 0" in script
    assert "*createnode 0 0 0 0 0 0" in script
    assert "*createnode 500 0 0 0 0 0" in script
    assert "*createlist nodes 1" in script
    assert "*createelement 60 1 1 1" in script
    assert "*createelement 2" not in script
    assert 'puts "BEAM_LAST_TYPE=$_hdm_beam_last_type"' in script
    assert 'puts "BEAM_LAST_CONFIG=$_hdm_beam_last_config"' in script
    assert "*surfacecreatenurbs" not in script
    assert "*solidblock" not in script
    assert "*tetmesh" not in script


def test_discrete_spring_tcl_uses_verified_route_commands():
    script = _build_discrete_spring_tcl(
        comp_name="discrete_test",
        node_a=(0.0, 0.0, 0.0),
        node_b=(100.0, 0.0, 0.0),
    )

    assert '*collectorcreateonly comps "discrete_test" "" 7' in script
    assert "*createnode 0 0 0 0 0 0" in script
    assert "*createnode 100 0 0 0 0 0" in script
    assert '*spring $_hdm_discrete_node_a $_hdm_discrete_node_b 1 "" 0' in script
    assert 'puts "DISCRETE_LAST_TYPE=$_hdm_discrete_type"' in script
    assert 'puts "DISCRETE_LAST_CONFIG=$_hdm_discrete_config"' in script
    assert "SECTION_DISCRETE" not in script
    assert "stiffness" not in script
    assert "damping" not in script
    assert "*surfacecreatenurbs" not in script
    assert "*solidblock" not in script
    assert "*tetmesh" not in script


def test_lumped_mass_tcl_uses_verified_route_commands():
    script = _build_lumped_mass_tcl(
        comp_name="mass_test",
        mass=10.0,
        x=0.0,
        y=0.0,
        z=0.0,
    )

    assert '*collectorcreateonly comps "mass_test" "" 7' in script
    assert "*createnode 0 0 0 0 0 0" in script
    assert "*createmark nodes 1 $_hdm_mass_node" in script
    assert '*masselement 1 10 "" 0' in script
    assert 'puts "MASS_LAST_TYPE=$_hdm_mass_type"' in script
    assert 'puts "MASS_LAST_CONFIG=$_hdm_mass_config"' in script
    assert "ELEMENT_MASS" not in script
    assert "*surfacecreatenurbs" not in script
    assert "*solidblock" not in script
    assert "*tetmesh" not in script


def test_direct_tria3_and_tet4_tcl_use_verified_config_routes():
    tria = _build_direct_element_tcl(
        comp_name="tria3_test",
        route_name="create_shell_tria3",
        element_config=103,
        label="TRIA3",
        nodes=[(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (0.0, 100.0, 0.0)],
    )
    tet = _build_direct_element_tcl(
        comp_name="tet4_test",
        route_name="create_tet_element",
        element_config=204,
        label="TET4",
        nodes=[(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (0.0, 100.0, 0.0), (0.0, 0.0, 100.0)],
    )

    assert '*collectorcreateonly comps "tria3_test" "" 7' in tria
    assert "*createlist nodes 1 $_hdm_tria3_nodes" in tria
    assert "*createelement 103 1 1 1" in tria
    assert 'puts "TRIA3_LAST_CONFIG=$_hdm_tria3_config"' in tria
    assert "*automesh" not in tria
    assert "*tetmesh" not in tria

    assert '*collectorcreateonly comps "tet4_test" "" 7' in tet
    assert "*createlist nodes 1 $_hdm_tet4_nodes" in tet
    assert "*createelement 204 1 1 1" in tet
    assert 'puts "TET4_LAST_CONFIG=$_hdm_tet4_config"' in tet
    assert "*solidblock" not in tet
    assert "*tetmesh" not in tet


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
