from program.server import HmModelingActionInput, run_modeling_action
from program.tools.hm_command_map import element_capability_matrix, load_command_map
from program.tools.hm_recording_requirements import (
    documented_unsupported_route_names,
    recording_promotion_queue,
    recording_requirements_coverage,
)


def test_modeling_action_dry_run_hex_mesh_uses_verified_route():
    result = run_modeling_action(
        HmModelingActionInput(
            action="create_mesh",
            element_type="HEX8",
            parameters={"size": 100.0, "element_size": 10.0},
            dry_run=True,
        )
    )

    assert result["success"] is True
    assert result["tool"] == "hm_create_fe_cube"
    assert result["route_name"] == "create_structured_hex8_box"
    assert result["execution_allowed"] is True
    assert result["tcl_sent"] is False


def test_modeling_action_dry_run_verified_mesh_routes_match_capability_matrix():
    expected = {
        "HEX8": {
            "element_type": "solid_hex",
            "tool": "hm_create_fe_cube",
            "route_name": "create_structured_hex8_box",
            "required_parameters": ["size", "element_size"],
        },
        "QUAD4": {
            "element_type": "shell_quad",
            "tool": "hm_create_shell_plate",
            "route_name": "create_structured_quad4_shell_plate",
            "required_parameters": ["width", "height", "element_size"],
        },
    }

    for element_type, values in expected.items():
        result = run_modeling_action(
            HmModelingActionInput(
                action="create_mesh",
                element_type=element_type,
                dry_run=True,
            )
        )
        capability = element_capability_matrix(element_type)["capability"]["creation"]

        assert result["success"] is True
        assert result["action"] == "create_mesh"
        assert result["element_type"] == values["element_type"]
        assert result["tool"] == values["tool"] == capability["tool"]
        assert result["route_name"] == values["route_name"] == capability["route_name"]
        assert result["required_parameters"] == values["required_parameters"]
        assert result["execution_allowed"] is True
        assert result["tcl_sent"] is False
        assert capability["supported"] is True
        assert capability["route_status"] == "verified"


def test_modeling_action_dry_run_verified_create_element_routes_match_capability_matrix():
    expected = {
        "TET4": {
            "element_type": "solid_tet",
            "tool": "hm_create_tet4",
            "route_name": "create_tet_element",
            "required_parameters": ["node1", "node2", "node3", "node4"],
        },
        "TRIA3": {
            "element_type": "shell_tria",
            "tool": "hm_create_tria3",
            "route_name": "create_shell_tria3",
            "required_parameters": ["node1", "node2", "node3"],
        },
        "mass": {
            "element_type": "lumped_mass",
            "tool": "hm_create_lumped_mass",
            "route_name": "create_lumped_mass",
            "required_parameters": ["mass"],
        },
        "discrete": {
            "element_type": "discrete",
            "tool": "hm_create_discrete_spring",
            "route_name": "create_discrete_element",
            "required_parameters": ["node_a", "node_b"],
        },
        "beam": {
            "element_type": "line_beam",
            "tool": "hm_create_beam_line",
            "route_name": "create_beam_line",
            "required_parameters": ["length", "element_size"],
        },
    }

    for element_type, values in expected.items():
        result = run_modeling_action(
            HmModelingActionInput(
                action="create_element",
                element_type=element_type,
                dry_run=True,
            )
        )
        capability = element_capability_matrix(element_type)["capability"]["creation"]

        assert result["success"] is True
        assert result["action"] == "create_element"
        assert result["element_type"] == values["element_type"]
        assert result["tool"] == values["tool"] == capability["tool"]
        assert result["route_name"] == values["route_name"] == capability["route_name"]
        assert result["required_parameters"] == values["required_parameters"]
        assert result["execution_allowed"] is True
        assert result["tcl_sent"] is False
        assert capability["supported"] is True
        assert capability["route_status"] == "verified"


def test_modeling_action_create_element_rejects_structured_mesh_families():
    for element_type in ("HEX8", "QUAD4"):
        result = run_modeling_action(
            HmModelingActionInput(
                action="create_element",
                element_type=element_type,
                dry_run=True,
            )
        )

        assert result["success"] is False
        assert result["error_type"] == "action_not_supported_for_element_type"
        assert result["execution_allowed"] is False
        assert result["tcl_sent"] is False
        assert result["required_verification"] == [
            "Check hm_element_capability_matrix for the current supported route.",
            "Add a verified command-map route before exposing execution.",
        ]


def test_modeling_action_blocks_tet_automatic_mesh():
    result = run_modeling_action(
        HmModelingActionInput(
            action="create_mesh",
            element_type="TET4",
            parameters={"element_size": 10.0},
        )
    )

    assert result["success"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["element_type"] == "solid_tet"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["blocked_route_name"] == "tetmesh_geometry_solid"
    assert result["blocked_route_status"] == "unsupported"
    assert result["next_supported_actions"][0] == {
        "action": "create_element",
        "tool": "hm_create_tet4",
        "route_name": "create_tet_element",
        "scope": "direct single TET4 FE element, not geometry tetmesh",
        "required_parameters": ["node1", "node2", "node3", "node4"],
    }
    assert result["next_supported_actions"][1]["action"] == "recording_requirements"
    assert result["next_supported_actions"][1]["route_name"] == "tetmesh_geometry_solid"
    assert result["next_supported_actions"][2]["action"] == "validate_recording"
    assert result["next_supported_actions"][2]["route_name"] == "tetmesh_geometry_solid"


def test_modeling_action_suggests_direct_elements_when_automesh_is_blocked():
    expected = {
        "TRIA3": ("hm_create_tria3", "create_shell_tria3", "surface_automesh"),
        "beam": ("hm_create_beam_line", "create_beam_line", "line_mesh_beam"),
        "mass": ("hm_create_lumped_mass", "create_lumped_mass", "mesh_lumped_mass"),
        "discrete": ("hm_create_discrete_spring", "create_discrete_element", "mesh_discrete_element"),
    }

    for element_type, (tool, route_name, blocked_route_name) in expected.items():
        result = run_modeling_action(
            HmModelingActionInput(
                action="create_mesh",
                element_type=element_type,
                parameters={"element_size": 10.0},
            )
        )

        assert result["success"] is False
        assert result["error_type"] == "mesh_route_not_verified"
        assert result["execution_allowed"] is False
        assert result["tcl_sent"] is False
        assert result["next_supported_actions"][0]["action"] == "create_element"
        assert result["next_supported_actions"][0]["tool"] == tool
        assert result["next_supported_actions"][0]["route_name"] == route_name
        assert result["blocked_route_name"] == blocked_route_name
        assert result["blocked_route_status"] == "unsupported"
        assert result["next_supported_actions"][1]["action"] == "recording_requirements"
        assert result["next_supported_actions"][1]["route_name"] == blocked_route_name
        assert result["next_supported_actions"][2]["action"] == "validate_recording"
        assert result["next_supported_actions"][2]["route_name"] == blocked_route_name


def test_automesh_alternatives_match_capability_matrix_creation_routes():
    for element_type in ("TET4", "TRIA3", "beam", "mass", "discrete"):
        blocked = run_modeling_action(
            HmModelingActionInput(
                action="create_mesh",
                element_type=element_type,
                parameters={"element_size": 10.0},
            )
        )
        capability = element_capability_matrix(element_type)

        alternative = blocked["next_supported_actions"][0]
        creation = capability["capability"]["creation"]
        blocked_recording = blocked["next_supported_actions"][1]
        meshing = capability["capability"]["meshing"]
        assert alternative["action"] == "create_element"
        assert alternative["tool"] == creation["tool"]
        assert alternative["route_name"] == creation["route_name"]
        assert creation["supported"] is True
        assert creation["route_status"] == "verified"
        assert blocked["blocked_route_name"] == meshing["route_name"]
        assert blocked_recording["action"] == "recording_requirements"
        assert blocked_recording["route_name"] == meshing["route_name"]


def test_modeling_action_blocks_mixed_mesh():
    result = run_modeling_action(
        HmModelingActionInput(
            action="create_mesh",
            element_type="mixed",
            parameters={"element_size": 10.0},
        )
    )

    assert result["success"] is False
    assert result["error_type"] == "unsupported_element_type"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["next_supported_actions"][0]["action"] == "capability"
    assert result["next_supported_actions"][1]["route_name"] == "mixed_mesh_workflow"


def test_modeling_action_rejects_unknown_element_type_before_route_planning():
    result = run_modeling_action(
        HmModelingActionInput(
            action="create_mesh",
            element_type="pyramid",
            parameters={"element_size": 10.0},
        )
    )

    assert result["success"] is False
    assert result["error_type"] == "unknown_element_type"
    assert result["element_type"] == "pyramid"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert "solid_hex" in result["known_types"]
    assert result["next_supported_actions"][0]["action"] == "capability"
    assert "command recording" not in " ".join(result["required_verification"]).lower()


def test_modeling_action_capability_reports_mixed_as_explicitly_blocked():
    result = run_modeling_action(
        HmModelingActionInput(
            action="capability",
            element_type="mixed",
        )
    )

    assert result["success"] is True
    assert result["canonical_type"] == "mixed"
    assert result["capability"]["meshing"]["supported"] is False
    assert result["capability"]["meshing"]["route_status"] == "unsupported"


def test_modeling_action_plans_material_eos_load_constraint_execution():
    expected_keywords = {
        "assign_material": "MAT_ELASTIC",
        "assign_eos": "EOS_LINEAR_POLYNOMIAL",
        "apply_constraint": "BOUNDARY_SPC",
        "apply_load": "LOAD_NODE",
    }
    for action, keyword in expected_keywords.items():
        result = run_modeling_action(
            HmModelingActionInput(
                action=action,
                element_type="solid_hex",
                parameters={"MID": 1, "RHO": 7.85e-6, "E": 210000.0, "PR": 0.3}
                if action == "assign_material"
                else {"EOSID": 1}
                if action == "assign_eos"
                else {"NODEID": 1, "CID": 0, "DOFX": 1, "DOFY": 1, "DOFZ": 1, "DOFRX": 0, "DOFRY": 0, "DOFRZ": 0}
                if action == "apply_constraint"
                else {"NID": 1, "DOF": 3, "LCID": 1, "SF": 1.0, "CID": 0, "M1": 0.0, "M2": 0.0, "M3": -100.0},
                dry_run=True,
            )
        )

        assert result["success"] is True
        assert result["tool"] == "hm_set_keyword"
        assert result["route_name"] == keyword
        assert result["keyword"] == keyword
        assert result["execution_allowed"] is True
        assert result["tcl_sent"] is False


def test_modeling_action_material_keyword_route_is_shared_across_element_families():
    for element_type in ("HEX8", "TET4", "QUAD4", "TRIA3", "beam", "mass", "discrete"):
        result = run_modeling_action(
            HmModelingActionInput(
                action="assign_material",
                element_type=element_type,
                parameters={"MID": 1, "RHO": 7.85e-6, "E": 210000.0, "PR": 0.3},
                dry_run=True,
            )
        )

        assert result["success"] is True
        assert result["tool"] == "hm_set_keyword"
        assert result["route_name"] == "MAT_ELASTIC"
        assert result["execution_allowed"] is True
        assert result["tcl_sent"] is False


def test_modeling_action_reports_recording_requirements_for_one_route():
    result = run_modeling_action(
        HmModelingActionInput(
            action="recording_requirements",
            element_type="HEX8",
            parameters={"route_name": "assign_material_to_hex_part"},
        )
    )

    route = result["route"]
    assert result["success"] is True
    assert result["action"] == "recording_requirements"
    assert result["coverage"]["complete"] is True
    assert route["route_name"] == "assign_material_to_hex_part"
    assert route["element_type"] == "solid_hex"
    assert "*setvalue" in route["required_markers"]
    assert "datanames_verified" in route["required_evidence"]
    assert route["execution_allowed"] is False
    assert route["tcl_sent"] is False
    assert result["promotion_queue"] == []


def test_modeling_action_filters_recording_requirements_by_element_type():
    result = run_modeling_action(
        HmModelingActionInput(
            action="recording_requirements",
            element_type="HEX8",
        )
    )

    route_names = {route["route_name"] for route in result["routes"]}
    assert result["success"] is True
    assert "assign_material_to_hex_part" in route_names
    assert "assign_eos_to_material" in route_names
    assert "apply_constraint_spc" in route_names
    assert "assign_material_to_shell_part" not in route_names
    assert result["recommended_next_routes"] == []


def test_modeling_action_rejects_unknown_recording_requirement_route():
    result = run_modeling_action(
        HmModelingActionInput(
            action="recording_requirements",
            parameters={"route_name": "unknown_route"},
        )
    )

    assert result["success"] is False
    assert result["error_type"] == "recording_route_not_supported"
    assert result["execution_allowed"] is False


def test_all_documented_unsupported_routes_have_recording_requirements():
    unsupported_routes = set(load_command_map()["unsupported_routes"])
    coverage = recording_requirements_coverage()

    assert documented_unsupported_route_names() == unsupported_routes
    assert coverage["complete"] is True
    assert coverage["valid_requirement_count"] == coverage["requirement_route_count"]
    assert coverage["invalid_requirement_count"] == 0
    assert coverage["missing_requirement_routes"] == []
    assert coverage["orphan_requirement_routes"] == []
    assert coverage["invalid_requirement_routes"] == []
    assert coverage["promotion_order_complete"] is True
    assert coverage["missing_promotion_order_routes"] == []
    assert coverage["orphan_promotion_order_routes"] == []

    for route_name in sorted(unsupported_routes):
        result = run_modeling_action(
            HmModelingActionInput(
                action="recording_requirements",
                parameters={"route_name": route_name},
            )
        )

        assert result["success"] is True, route_name
        assert result["route"]["route_name"] == route_name
        assert result["route"]["execution_allowed"] is False
        assert result["route"]["mcp_execution_allowed"] is False
        assert result["route"]["requires_verified_map_promotion"] is True
        assert result["route"]["tcl_sent"] is False
        assert result["route"]["evidence_schema"], route_name
        assert set(result["route"]["evidence_schema"]) == set(result["route"]["required_evidence"])
        assert result["route"]["recording_steps"][0].startswith("Start HyperMesh command recording")
        assert result["route"]["recording_steps"][-1].startswith("Promote the route only when")
        assert result["route"]["promotion_checklist"], route_name
        assert any(
            item["target"] == f"templates/hm_command_map.json routes.{route_name}.status"
            for item in result["route"]["promotion_checklist"]
        )


def test_recording_requirements_exposes_material_evidence_schema_and_steps():
    result = run_modeling_action(
        HmModelingActionInput(
            action="recording_requirements",
            element_type="HEX8",
            parameters={"route_name": "assign_material_to_hex_part"},
        )
    )

    schema = result["route"]["evidence_schema"]
    steps = result["route"]["recording_steps"]
    checklist = {item["target"]: item for item in result["route"]["promotion_checklist"]}

    assert schema["component_id"]["kind"] == "positive_integer_id"
    assert schema["property_id"]["kind"] == "positive_integer_id"
    assert schema["material_id"]["kind"] == "positive_integer_id"
    assert schema["cardimage_verified"]["kind"] == "boolean_true"
    assert schema["datanames_verified"]["kind"] == "boolean_true"
    assert any("positive HyperMesh entity ids" in step for step in steps)
    assert any("route_name=assign_material_to_hex_part" in step for step in steps)
    assert checklist["templates/hm_command_map.json routes.assign_material_to_hex_part.mcp_execution_allowed"]["required_value"] is True


def test_recording_promotion_queue_prioritizes_independent_recordings():
    queue = recording_promotion_queue()

    assert [item["route_name"] for item in queue[:2]] == [
        "surface_automesh",
        "tetmesh_geometry_solid",
    ]
    assert len(queue) == len(load_command_map()["unsupported_routes"])
    assert all(item["status"] == "unsupported" for item in queue)
    assert all(item["next_supported_actions"][0]["action"] == "recording_requirements" for item in queue)
    assert all(item["execution_allowed"] is False for item in queue)
    assert all(item["mcp_execution_allowed"] is False for item in queue)
    assert all(item["requires_verified_map_promotion"] is True for item in queue)
    assert all(item["tcl_sent"] is False for item in queue)
    assert all(item["evidence_schema"] for item in queue)
    assert all(item["recording_steps"] for item in queue)
    assert all(item["promotion_checklist"] for item in queue)


def test_recording_promotion_queue_marks_mixed_routes_dependency_blocked():
    queue = {item["route_name"]: item for item in recording_promotion_queue()}

    assert queue["mixed_mesh_workflow"]["ready_for_recording"] is False
    assert "mixed_element_workflow" in queue["mixed_mesh_workflow"]["blocked_by"]
    assert "assign_material_to_hex_part" not in queue
    assert "assign_material_to_tet_part" not in queue


def test_recording_promotion_queue_marks_dependency_ready_when_verified():
    command_map = {
        "routes": {
            "tetmesh_geometry_solid": {"status": "verified"},
        },
        "unsupported_routes": {
            "assign_material_to_tet_part": {"status": "unsupported", "entity_kind": "material_assignment"},
        },
    }

    queue = recording_promotion_queue(command_map)

    assert len(queue) == 1
    item = queue[0]
    assert item["priority"] == 1
    assert item["route_name"] == "assign_material_to_tet_part"
    assert item["element_type"] == "solid_tet"
    assert item["entity_kind"] == "material_assignment"
    assert item["status"] == "unsupported"
    assert item["blocked_by"] == []
    assert item["dependencies"] == [
        {"route_name": "tetmesh_geometry_solid", "status": "verified", "verified": True}
    ]
    assert item["ready_for_recording"] is True
    assert item["required_markers"] == ["*setvalue"]
    assert item["required_evidence"] == [
        "cardimage_verified",
        "datanames_verified",
        "component_binding_verified",
        "property_material_binding_verified",
        "component_id",
        "property_id",
        "material_id",
    ]
    assert item["evidence_schema"]["material_id"]["kind"] == "positive_integer_id"
    assert any("route_name=assign_material_to_tet_part" in step for step in item["recording_steps"])
    assert any(
        checklist_item["target"] == "templates/hm_command_map.json routes.assign_material_to_tet_part.status"
        for checklist_item in item["promotion_checklist"]
    )
    assert item["next_supported_actions"] == [
        {"action": "recording_requirements", "route_name": "assign_material_to_tet_part"},
        {"action": "validate_recording", "route_name": "assign_material_to_tet_part"},
    ]


def test_recording_requirements_coverage_reports_missing_and_orphan_routes():
    command_map = {
        "unsupported_routes": {
            "documented_without_requirement": {},
            "tetmesh_geometry_solid": {},
        }
    }

    coverage = recording_requirements_coverage(command_map)

    assert coverage["complete"] is False
    assert coverage["missing_requirement_routes"] == ["documented_without_requirement"]
    assert "assign_material_to_hex_part" in coverage["orphan_requirement_routes"]
    assert coverage["missing_promotion_order_routes"] == ["documented_without_requirement"]


def test_recording_requirements_coverage_reports_invalid_requirements(monkeypatch):
    from program.tools import hm_recording_requirements

    monkeypatch.setitem(
        hm_recording_requirements.RECORDING_ROUTE_REQUIREMENTS,
        "tetmesh_geometry_solid",
        {
            "element_type": "solid_tet",
            "required_markers": "*tetmesh",
            "forbidden_markers": "*writefile",
            "required_evidence": [],
            "promotion_target": "templates/hm_command_map.json unsupported_routes.other -> routes.other",
        },
    )

    coverage = recording_requirements_coverage({"unsupported_routes": {"tetmesh_geometry_solid": {}}})

    assert coverage["complete"] is False
    assert coverage["invalid_requirement_count"] == 1
    invalid = coverage["invalid_requirement_routes"][0]
    assert invalid["route_name"] == "tetmesh_geometry_solid"
    assert "required_evidence_missing" in invalid["reasons"]
    assert "promotion_target_route_mismatch" in invalid["reasons"]
    assert "required_markers_not_list" in invalid["reasons"]
    assert "forbidden_markers_not_list" in invalid["reasons"]


def test_recording_requirements_coverage_validates_count_pairs(monkeypatch):
    from program.tools import hm_recording_requirements

    monkeypatch.setitem(
        hm_recording_requirements.RECORDING_ROUTE_REQUIREMENTS,
        "tetmesh_geometry_solid",
        {
            "element_type": "solid_tet",
            "required_markers": ["*tetmesh"],
            "forbidden_markers": ["*writefile"],
            "required_evidence": ["elements_count_before"],
            "count_pairs": [("elements_count_before", "elements_count_after"), ("bad",)],
            "promotion_target": "templates/hm_command_map.json unsupported_routes.tetmesh_geometry_solid -> routes.tetmesh_geometry_solid",
        },
    )

    coverage = recording_requirements_coverage({"unsupported_routes": {"tetmesh_geometry_solid": {}}})

    assert coverage["complete"] is False
    assert coverage["invalid_requirement_count"] == 1
    invalid = coverage["invalid_requirement_routes"][0]
    assert invalid["route_name"] == "tetmesh_geometry_solid"
    assert "count_pair_invalid" in invalid["reasons"]
    assert "count_pair_evidence_missing" in invalid["reasons"]


def test_recording_requirements_coverage_validates_element_type(monkeypatch):
    from program.tools import hm_recording_requirements

    monkeypatch.setitem(
        hm_recording_requirements.RECORDING_ROUTE_REQUIREMENTS,
        "tetmesh_geometry_solid",
        {
            "element_type": "solid_teet",
            "required_markers": ["*tetmesh"],
            "forbidden_markers": ["*writefile"],
            "required_evidence": ["elements_count_before", "elements_count_after"],
            "count_pairs": [("elements_count_before", "elements_count_after")],
            "promotion_target": "templates/hm_command_map.json unsupported_routes.tetmesh_geometry_solid -> routes.tetmesh_geometry_solid",
        },
    )

    coverage = recording_requirements_coverage({"unsupported_routes": {"tetmesh_geometry_solid": {}}})

    assert coverage["complete"] is False
    invalid = coverage["invalid_requirement_routes"][0]
    assert invalid["route_name"] == "tetmesh_geometry_solid"
    assert "element_type_unknown" in invalid["reasons"]


def test_recording_requirements_coverage_validates_string_list_items(monkeypatch):
    from program.tools import hm_recording_requirements

    monkeypatch.setitem(
        hm_recording_requirements.RECORDING_ROUTE_REQUIREMENTS,
        "tetmesh_geometry_solid",
        {
            "element_type": "solid_tet",
            "required_markers": ["*tetmesh", 42],
            "forbidden_markers": ["*writefile", {"bad": "marker"}],
            "required_evidence": ["elements_count_before", "elements_count_after", {"bad": "evidence"}, ["bad"]],
            "count_pairs": [("elements_count_before", "elements_count_after")],
            "promotion_target": "templates/hm_command_map.json unsupported_routes.tetmesh_geometry_solid -> routes.tetmesh_geometry_solid",
        },
    )

    coverage = recording_requirements_coverage({"unsupported_routes": {"tetmesh_geometry_solid": {}}})

    assert coverage["complete"] is False
    invalid = coverage["invalid_requirement_routes"][0]
    assert invalid["route_name"] == "tetmesh_geometry_solid"
    assert "required_markers_item_not_string" in invalid["reasons"]
    assert "forbidden_markers_item_not_string" in invalid["reasons"]
    assert "required_evidence_item_not_string" in invalid["reasons"]


def test_recording_requirements_coverage_validates_promotion_checklist(monkeypatch):
    from program.tools import hm_recording_requirements

    def broken_checklist(route_name, requirement):
        return [
            {
                "target": f"templates/hm_command_map.json routes.{route_name}.status",
                "required_value": "verified",
            },
            {"target": "", "required_value": True, "reason": "missing target should fail"},
            "not-a-checklist-item",
        ]

    monkeypatch.setattr(hm_recording_requirements, "_promotion_checklist", broken_checklist)

    coverage = recording_requirements_coverage({"unsupported_routes": {"tetmesh_geometry_solid": {}}})

    assert coverage["complete"] is False
    assert coverage["invalid_requirement_count"] >= 1
    invalid_by_route = {item["route_name"]: item for item in coverage["invalid_requirement_routes"]}
    invalid = invalid_by_route["tetmesh_geometry_solid"]
    assert "promotion_checklist_item_not_dict" in invalid["reasons"]
    assert "promotion_checklist_target_missing" in invalid["reasons"]
    assert "promotion_checklist_reason_missing" in invalid["reasons"]
    assert "promotion_checklist_target_coverage_missing" in invalid["reasons"]


def test_modeling_action_validates_tetmesh_recording_before_promotion():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="TET4",
            parameters={
                "route_name": "tetmesh_geometry_solid",
                "recording_text": "*createmark solids 1 1\n*tetmesh solids 1 10",
                "runtime_evidence": {
                    "elements_count_before": 0,
                    "elements_count_after": 25,
                    "solids_count_before": 1,
                    "solids_count_after": 1,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["execution_allowed"] is False
    assert result["mcp_execution_allowed"] is False
    assert result["requires_verified_map_promotion"] is True
    assert result["tcl_sent"] is False
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is True
    assert result["promotion_ready"] is True
    assert result["promotion_target"].endswith("routes.tetmesh_geometry_solid")
    checklist = {item["target"]: item for item in result["promotion_checklist"]}
    assert checklist["templates/hm_command_map.json routes.tetmesh_geometry_solid.status"]["required_value"] == "verified"
    assert checklist["templates/hm_command_map.json routes.tetmesh_geometry_solid.mcp_execution_allowed"]["required_value"] is True
    assert checklist["templates/hm_command_map.json unsupported_routes.tetmesh_geometry_solid"]["required_value"] == "removed after route is added to routes"
    assert checklist["tests"]["required_value"] == "route execution/guardrail tests updated"


def test_modeling_action_rejects_surface_recording_without_runtime_evidence():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="shell_quad",
            parameters={
                "route_name": "surface_automesh",
                "recording_text": "*createmark surfaces 1 1\n*automesh 0 2 2",
                "runtime_evidence": {"display_verified": True},
            },
        )
    )

    assert result["success"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is False
    assert result["promotion_ready"] is False
    assert "elements_count_before" in result["missing_evidence"]
    assert result["expected_evidence_schema"]["elements_count_before"]["kind"] == "integer_count"
    assert any("route_name=surface_automesh" in step for step in result["recording_steps"])
    assert any(
        item["target"] == "templates/hm_command_map.json routes.surface_automesh.status"
        and item["required_value"] == "verified"
        for item in result["promotion_checklist"]
    )
    assert result["tcl_sent"] is False


def test_modeling_action_rejects_recording_that_writes_k_or_hm_files():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="TET4",
            parameters={
                "route_name": "tetmesh_geometry_solid",
                "recording_text": "*tetmesh solids 1 10\n*writefile \"bad.k\" 1",
                "runtime_evidence": {
                    "elements_count_before": 0,
                    "elements_count_after": 25,
                    "solids_count_before": 1,
                    "solids_count_after": 1,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["recording_valid"] is False
    assert result["promotion_ready"] is False
    assert "*writefile" in result["forbidden_markers"]


def test_modeling_action_rejects_recording_with_global_forbidden_tcl_commands():
    cases = {
        "exec lsdyna i=model.k": "exec",
        "*feoutputwithdata \"bad.k\" 0 0 0 0 0": "*feoutputwithdata",
        "file delete bad.hm": "file delete",
        "source \"F:/other_script.tcl\"": "source",
        "open \"bad.k\" w": "open",
    }

    for recording_text, forbidden_marker in cases.items():
        result = run_modeling_action(
            HmModelingActionInput(
                action="validate_recording",
                element_type="beam",
                parameters={
                    "route_name": "line_mesh_beam",
                    "recording_text": f"hm_createmark lines 1 10\n{recording_text}",
                    "runtime_evidence": {
                        "line_selection_verified": True,
                        "mesh_command_verified": True,
                        "elements_count_before": 0,
                        "elements_count_after": 4,
                        "beam_config_verified": True,
                        "orientation_verified": True,
                        "display_verified": True,
                    },
                },
            )
        )

        assert result["success"] is True
        assert result["recording_command_present"] is True
        assert result["runtime_evidence_valid"] is True
        assert result["recording_valid"] is False
        assert result["promotion_ready"] is False
        assert forbidden_marker in result["forbidden_markers"]


def test_modeling_action_rejects_empty_recording_text_even_without_required_markers():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="beam",
            parameters={
                "route_name": "line_mesh_beam",
                "recording_text": "  ",
                "runtime_evidence": {
                    "line_selection_verified": True,
                    "mesh_command_verified": True,
                    "elements_count_before": 0,
                    "elements_count_after": 4,
                    "beam_config_verified": True,
                    "orientation_verified": True,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_text_present"] is False
    assert result["recording_command_present"] is False
    assert result["recording_valid"] is False
    assert result["runtime_evidence_valid"] is True
    assert result["promotion_ready"] is False
    assert result["missing_markers"] == []
    assert result["tcl_sent"] is False


def test_modeling_action_rejects_non_command_recording_text_even_with_evidence():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="beam",
            parameters={
                "route_name": "line_mesh_beam",
                "recording_text": "I clicked the line mesh panel and it worked.",
                "runtime_evidence": {
                    "line_selection_verified": True,
                    "mesh_command_verified": True,
                    "elements_count_before": 0,
                    "elements_count_after": 4,
                    "beam_config_verified": True,
                    "orientation_verified": True,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_text_present"] is True
    assert result["recording_command_present"] is False
    assert result["recording_valid"] is False
    assert result["runtime_evidence_valid"] is True
    assert result["promotion_ready"] is False


def test_modeling_action_accepts_hm_command_recording_without_route_specific_markers():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="beam",
            parameters={
                "route_name": "line_mesh_beam",
                "recording_text": "hm_createmark lines 1 10\n*createmark elems 1 all",
                "runtime_evidence": {
                    "line_selection_verified": True,
                    "mesh_command_verified": True,
                    "elements_count_before": 0,
                    "elements_count_after": 4,
                    "beam_config_verified": True,
                    "orientation_verified": True,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_text_present"] is True
    assert result["recording_command_present"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is True
    assert result["promotion_ready"] is True


def test_modeling_action_validates_material_binding_recording_before_promotion():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="HEX8",
            parameters={
                "route_name": "assign_material_to_hex_part",
                "recording_text": "*createentity mats name=TEST\n*setvalue mats id=1 STATUS=1\n*setvalue comps id=1 propertyid=1",
                "runtime_evidence": {
                    "cardimage_verified": True,
                    "datanames_verified": True,
                    "component_binding_verified": True,
                    "property_material_binding_verified": True,
                    "component_id": 1,
                    "property_id": 1,
                    "material_id": 1,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["route_name"] == "assign_material_to_hex_part"
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is True
    assert result["promotion_ready"] is True
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    checklist = {item["target"]: item for item in result["promotion_checklist"]}
    assert checklist["templates/hm_command_map.json routes.assign_material_to_hex_part.mcp_execution_allowed"]["required_value"] is True
    assert checklist["templates/hm_command_map.json routes.assign_material_to_hex_part.commands"]["required_value"] == ["*setvalue"]


def test_modeling_action_rejects_material_recording_with_invalid_entity_ids():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="HEX8",
            parameters={
                "route_name": "assign_material_to_hex_part",
                "recording_text": "*createentity mats name=TEST\n*setvalue mats id=1 STATUS=1\n*setvalue comps id=1 propertyid=1",
                "runtime_evidence": {
                    "cardimage_verified": True,
                    "datanames_verified": True,
                    "component_binding_verified": True,
                    "property_material_binding_verified": True,
                    "component_id": 0,
                    "property_id": "",
                    "material_id": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is False
    assert result["promotion_ready"] is False
    assert result["missing_evidence"] == []
    assert result["false_evidence"] == []
    assert result["invalid_evidence_values"] == [
        {
            "name": "component_id",
            "value": 0,
            "reason": "must be a positive HyperMesh entity id",
        },
        {
            "name": "material_id",
            "value": True,
            "reason": "must be a positive HyperMesh entity id",
        },
        {
            "name": "property_id",
            "value": "",
            "reason": "must be a positive HyperMesh entity id",
        },
    ]


def test_modeling_action_rejects_recording_with_invalid_integer_count_evidence():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="TET4",
            parameters={
                "route_name": "tetmesh_geometry_solid",
                "recording_text": "*createmark solids 1 1\n*tetmesh solids 1 10",
                "runtime_evidence": {
                    "elements_count_before": 0,
                    "elements_count_after": 25,
                    "solids_count_before": "not-a-count",
                    "solids_count_after": -1,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is False
    assert result["promotion_ready"] is False
    assert result["invalid_evidence_values"] == [
        {
            "name": "solids_count_after",
            "value": -1,
            "reason": "must be a non-negative integer count",
        },
        {
            "name": "solids_count_before",
            "value": "not-a-count",
            "reason": "must be a non-negative integer count",
        },
    ]
    assert result["expected_evidence_schema"]["solids_count_before"]["kind"] == "integer_count"
    assert any("route_name=tetmesh_geometry_solid" in step for step in result["recording_steps"])


def test_modeling_action_rejects_mixed_recording_with_empty_regions():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="mixed",
            parameters={
                "route_name": "mixed_element_workflow",
                "recording_text": "hm_createmark elems 1 all",
                "runtime_evidence": {
                    "regions": [],
                    "element_family_routes_verified": True,
                    "elements_count_before": 0,
                    "elements_count_after": 10,
                    "component_ownership_verified": True,
                    "interface_rules_verified": True,
                    "display_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is False
    assert result["promotion_ready"] is False
    assert result["invalid_evidence_values"] == [
        {
            "name": "regions",
            "value": [],
            "reason": "must be a non-empty list",
        }
    ]
    assert result["expected_evidence_schema"]["regions"]["kind"] == "non_empty_list"
    assert any("route_name=mixed_element_workflow" in step for step in result["recording_steps"])


def test_modeling_action_rejects_mass_and_discrete_policy_recordings_with_invalid_binding_ids():
    cases = [
        (
            "mass",
            "assign_material_to_lumped_mass",
            {
                "mass_card_policy_verified": True,
                "datanames_verified": True,
                "component_binding_verified": True,
                "property_or_mass_binding_verified": True,
                "component_id": 1,
                "mass_or_property_id": 0,
            },
            "mass_or_property_id",
        ),
        (
            "discrete",
            "assign_material_to_discrete_element",
            {
                "discrete_card_policy_verified": True,
                "datanames_verified": True,
                "component_binding_verified": True,
                "property_or_section_binding_verified": True,
                "component_id": 1,
                "property_or_section_id": None,
            },
            "property_or_section_id",
        ),
    ]

    for element_type, route_name, runtime_evidence, invalid_name in cases:
        result = run_modeling_action(
            HmModelingActionInput(
                action="validate_recording",
                element_type=element_type,
                parameters={
                    "route_name": route_name,
                    "recording_text": "*setvalue comps id=1 propertyid=1",
                    "runtime_evidence": runtime_evidence,
                },
            )
        )

        assert result["success"] is True
        assert result["recording_valid"] is True
        assert result["runtime_evidence_valid"] is False
        assert result["promotion_ready"] is False
        assert result["invalid_evidence_values"][0]["name"] == invalid_name
        assert result["invalid_evidence_values"][0]["reason"] == "must be a positive HyperMesh entity id"


def test_modeling_action_blocks_promotion_when_route_dependencies_are_unverified():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            element_type="TET4",
            parameters={
                "route_name": "assign_material_to_tet_part",
                "recording_text": "*createentity mats name=TEST\n*setvalue comps id=1 propertyid=1",
                "runtime_evidence": {
                    "cardimage_verified": True,
                    "datanames_verified": True,
                    "component_binding_verified": True,
                    "property_material_binding_verified": True,
                    "component_id": 1,
                    "property_id": 1,
                    "material_id": 1,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is True
    assert result["dependencies_satisfied"] is False
    assert result["blocked_dependencies"] == ["tetmesh_geometry_solid"]
    assert result["dependencies"] == [
        {"route_name": "tetmesh_geometry_solid", "status": "unsupported", "verified": False}
    ]
    assert result["promotion_ready"] is False
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False


def test_modeling_action_rejects_eos_recording_without_verified_datanames():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            parameters={
                "route_name": "assign_eos_to_material",
                "recording_text": "*setvalue mats id=1 eosid=1",
                "runtime_evidence": {
                    "eos_cardimage_verified": True,
                    "eos_datanames_verified": False,
                    "material_cardimage_verified": True,
                    "material_eos_binding_verified": True,
                    "material_id": 1,
                    "eos_id": 1,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["recording_valid"] is True
    assert result["runtime_evidence_valid"] is False
    assert result["promotion_ready"] is False
    assert "eos_datanames_verified" in result["false_evidence"]
    assert result["expected_evidence_schema"]["eos_datanames_verified"]["kind"] == "boolean_true"
    assert any("route_name=assign_eos_to_material" in step for step in result["recording_steps"])


def test_modeling_action_rejects_load_recording_without_count_increase():
    result = run_modeling_action(
        HmModelingActionInput(
            action="validate_recording",
            parameters={
                "route_name": "apply_load_nodal_or_pressure",
                "recording_text": "*setvalue loads id=1 magnitude=100",
                "runtime_evidence": {
                    "loads_count_before": 2,
                    "loads_count_after": 2,
                    "collector_verified": True,
                    "target_verified": True,
                    "datanames_verified": True,
                    "values_verified": True,
                },
            },
        )
    )

    assert result["success"] is True
    assert result["runtime_evidence_valid"] is False
    assert result["promotion_ready"] is False
    assert result["count_failures"] == [{"before": "loads_count_before", "after": "loads_count_after"}]
