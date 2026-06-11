"""Recording evidence requirements for promoting blocked HyperMesh routes.

This module is intentionally independent from the MCP server. It lets tests,
smoke checks, and future agent docs query the same promotion policy without
adding more MCP tools or sending Tcl to HyperMesh.
"""

from __future__ import annotations

from typing import Any, Optional

from program.tools.hm_command_map import known_element_types, load_command_map


RECORDING_ROUTE_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "tetmesh_geometry_solid": {
        "element_type": "solid_tet",
        "required_markers": ["*tetmesh"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": ["elements_count_before", "elements_count_after", "solids_count_before", "solids_count_after", "display_verified"],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.tetmesh_geometry_solid -> routes.tetmesh_geometry_solid",
    },
    "surface_automesh": {
        "element_type": "shell_quad",
        "required_markers": ["*automesh"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": ["elements_count_before", "elements_count_after", "surfaces_count_before", "surfaces_count_after", "display_verified"],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.surface_automesh -> routes.surface_automesh",
    },
    "line_mesh_beam": {
        "element_type": "line_beam",
        "required_markers": [],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "line_selection_verified",
            "mesh_command_verified",
            "elements_count_before",
            "elements_count_after",
            "beam_config_verified",
            "orientation_verified",
            "display_verified",
        ],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.line_mesh_beam -> routes.line_mesh_beam",
    },
    "mesh_lumped_mass": {
        "element_type": "lumped_mass",
        "required_markers": ["*masselement"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "target_node_or_set_verified",
            "elements_count_before",
            "elements_count_after",
            "mass_value_verified",
            "mass_config_verified",
            "display_verified",
        ],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.mesh_lumped_mass -> routes.mesh_lumped_mass",
    },
    "mesh_discrete_element": {
        "element_type": "discrete",
        "required_markers": ["*spring"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "node_pair_or_set_verified",
            "elements_count_before",
            "elements_count_after",
            "discrete_config_verified",
            "property_binding_verified",
            "display_verified",
        ],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.mesh_discrete_element -> routes.mesh_discrete_element",
    },
    "mixed_element_workflow": {
        "element_type": "mixed",
        "required_markers": [],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "regions",
            "element_family_routes_verified",
            "elements_count_before",
            "elements_count_after",
            "component_ownership_verified",
            "interface_rules_verified",
            "display_verified",
        ],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.mixed_element_workflow -> routes.mixed_element_workflow",
    },
    "mixed_mesh_workflow": {
        "element_type": "mixed",
        "required_markers": [],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "regions",
            "elements_count_before",
            "elements_count_after",
            "component_ownership_verified",
            "transition_rules_verified",
            "display_verified",
        ],
        "count_pairs": [("elements_count_before", "elements_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.mixed_mesh_workflow -> routes.mixed_mesh_workflow",
    },
    "mixed_material_assignment": {
        "element_type": "mixed",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "solid_material_binding_verified",
            "shell_material_binding_verified",
            "beam_material_binding_verified",
            "mass_or_discrete_property_policy_verified",
            "component_bindings_verified",
            "property_material_bindings_verified",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.mixed_material_assignment -> routes.mixed_material_assignment",
    },
    "assign_material_to_hex_part": {
        "element_type": "solid_hex",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "cardimage_verified",
            "datanames_verified",
            "component_binding_verified",
            "property_material_binding_verified",
            "component_id",
            "property_id",
            "material_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_material_to_hex_part -> routes.assign_material_to_hex_part",
    },
    "assign_material_to_tet_part": {
        "element_type": "solid_tet",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "cardimage_verified",
            "datanames_verified",
            "component_binding_verified",
            "property_material_binding_verified",
            "component_id",
            "property_id",
            "material_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_material_to_tet_part -> routes.assign_material_to_tet_part",
    },
    "assign_material_to_shell_part": {
        "element_type": "shell_quad",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "cardimage_verified",
            "datanames_verified",
            "component_binding_verified",
            "property_material_binding_verified",
            "thickness_verified",
            "component_id",
            "property_id",
            "material_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_material_to_shell_part -> routes.assign_material_to_shell_part",
    },
    "assign_material_to_beam_part": {
        "element_type": "line_beam",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "cardimage_verified",
            "datanames_verified",
            "component_binding_verified",
            "property_material_binding_verified",
            "beam_section_verified",
            "orientation_verified",
            "component_id",
            "property_id",
            "material_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_material_to_beam_part -> routes.assign_material_to_beam_part",
    },
    "assign_material_to_lumped_mass": {
        "element_type": "lumped_mass",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "mass_card_policy_verified",
            "datanames_verified",
            "component_binding_verified",
            "property_or_mass_binding_verified",
            "component_id",
            "mass_or_property_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_material_to_lumped_mass -> routes.assign_material_to_lumped_mass",
    },
    "assign_material_to_discrete_element": {
        "element_type": "discrete",
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "discrete_card_policy_verified",
            "datanames_verified",
            "component_binding_verified",
            "property_or_section_binding_verified",
            "component_id",
            "property_or_section_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_material_to_discrete_element -> routes.assign_material_to_discrete_element",
    },
    "assign_eos_to_material": {
        "element_type": None,
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "eos_cardimage_verified",
            "eos_datanames_verified",
            "material_cardimage_verified",
            "material_eos_binding_verified",
            "material_id",
            "eos_id",
        ],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.assign_eos_to_material -> routes.assign_eos_to_material",
    },
    "apply_constraint_spc": {
        "element_type": None,
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "constraints_count_before",
            "constraints_count_after",
            "collector_verified",
            "target_set_verified",
            "datanames_verified",
            "values_verified",
        ],
        "count_pairs": [("constraints_count_before", "constraints_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.apply_constraint_spc -> routes.apply_constraint_spc",
    },
    "apply_load_nodal_or_pressure": {
        "element_type": None,
        "required_markers": ["*setvalue"],
        "forbidden_markers": ["*writefile"],
        "required_evidence": [
            "loads_count_before",
            "loads_count_after",
            "collector_verified",
            "target_verified",
            "datanames_verified",
            "values_verified",
        ],
        "count_pairs": [("loads_count_before", "loads_count_after")],
        "promotion_target": "templates/hm_command_map.json unsupported_routes.apply_load_nodal_or_pressure -> routes.apply_load_nodal_or_pressure",
    },
}


RECORDING_ROUTE_PROMOTION_ORDER = [
    "assign_material_to_hex_part",
    "assign_material_to_shell_part",
    "assign_material_to_beam_part",
    "surface_automesh",
    "tetmesh_geometry_solid",
    "assign_material_to_tet_part",
    "line_mesh_beam",
    "apply_constraint_spc",
    "apply_load_nodal_or_pressure",
    "mesh_lumped_mass",
    "mesh_discrete_element",
    "assign_material_to_lumped_mass",
    "assign_material_to_discrete_element",
    "assign_eos_to_material",
    "mixed_material_assignment",
    "mixed_element_workflow",
    "mixed_mesh_workflow",
]


RECORDING_ROUTE_DEPENDENCIES: dict[str, list[str]] = {
    "assign_material_to_tet_part": ["tetmesh_geometry_solid"],
    "assign_material_to_lumped_mass": ["mesh_lumped_mass"],
    "assign_material_to_discrete_element": ["mesh_discrete_element"],
    "mixed_material_assignment": [
        "assign_material_to_hex_part",
        "assign_material_to_shell_part",
        "assign_material_to_beam_part",
        "assign_material_to_lumped_mass",
        "assign_material_to_discrete_element",
    ],
    "mixed_element_workflow": [
        "tetmesh_geometry_solid",
        "surface_automesh",
        "line_mesh_beam",
        "mesh_lumped_mass",
        "mesh_discrete_element",
    ],
    "mixed_mesh_workflow": [
        "tetmesh_geometry_solid",
        "surface_automesh",
        "line_mesh_beam",
        "mixed_element_workflow",
    ],
}


GLOBAL_FORBIDDEN_RECORDING_COMMANDS = {
    "*feoutput",
    "*feoutputwithdata",
    "*writefile",
    "exec",
    "open",
    "source",
}


GLOBAL_FORBIDDEN_RECORDING_PREFIXES = (
    "file copy",
    "file delete",
    "file mkdir",
    "file rename",
)


def recording_blocked(
    *,
    action: str,
    element_type: Optional[str],
    error_type: str,
    reason: str,
    required_verification: list[str],
) -> dict[str, Any]:
    return {
        "success": False,
        "action": action,
        "element_type": element_type,
        "error_type": error_type,
        "error": reason,
        "execution_allowed": False,
        "tcl_sent": False,
        "required_verification": required_verification,
        "policy": "Only verified HyperMesh command-map routes may execute Tcl.",
    }


def _recording_command_present(recording_text: str) -> bool:
    """Return true when the text looks like HyperMesh command-recording Tcl."""
    for line in recording_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("*") or stripped.startswith("hm_"):
            return True
    return False


def _global_forbidden_recording_markers(recording_text: str) -> list[str]:
    """Return global forbidden Tcl command markers found in recording text."""
    found: list[str] = []
    for line in recording_text.splitlines():
        stripped = line.strip().lower()
        if not stripped:
            continue
        command = stripped.split()[0]
        if command in GLOBAL_FORBIDDEN_RECORDING_COMMANDS:
            found.append(command)
            continue
        for prefix in GLOBAL_FORBIDDEN_RECORDING_PREFIXES:
            if stripped.startswith(prefix):
                found.append(prefix)
                break
    return found


def _route_dependency_status(route_name: str, command_map: Optional[dict[str, Any]] = None) -> tuple[bool, list[str], list[dict[str, Any]]]:
    data = command_map if command_map is not None else load_command_map()
    routes = data.get("routes") or {}
    unsupported_routes = data.get("unsupported_routes") or {}
    dependencies = RECORDING_ROUTE_DEPENDENCIES.get(route_name, [])
    blocked_dependencies: list[str] = []
    dependency_status: list[dict[str, Any]] = []
    for dependency in dependencies:
        if dependency in routes:
            status = routes[dependency].get("status", "unknown")
            verified = status == "verified"
        elif dependency in unsupported_routes:
            status = "unsupported"
            verified = False
        else:
            status = "missing"
            verified = False
        if not verified:
            blocked_dependencies.append(dependency)
        dependency_status.append(
            {
                "route_name": dependency,
                "status": status,
                "verified": verified,
            }
        )
    return not blocked_dependencies, blocked_dependencies, dependency_status


def _positive_id_evidence_names(required_evidence: list[str]) -> set[str]:
    """Return evidence keys that must be real HyperMesh entity ids."""
    explicit_id_names = {
        "component_id",
        "property_id",
        "material_id",
        "eos_id",
        "mass_or_property_id",
        "property_or_section_id",
    }
    return {
        name
        for name in required_evidence
        if name in explicit_id_names or (name.endswith("_id") and not name.endswith("_verified"))
    }


def _invalid_evidence_values(required_evidence: list[str], runtime_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []
    schema = _evidence_schema(required_evidence)
    for name in sorted(schema):
        if name not in runtime_evidence:
            continue
        value = runtime_evidence.get(name)
        kind = schema[name]["kind"]
        if kind == "positive_integer_id":
            try:
                if isinstance(value, bool):
                    raise ValueError
                parsed = int(value)
                if parsed <= 0:
                    raise ValueError
            except Exception:
                invalid.append(
                    {
                        "name": name,
                        "value": value,
                        "reason": "must be a positive HyperMesh entity id",
                    }
                )
        elif kind == "integer_count":
            try:
                if isinstance(value, bool):
                    raise ValueError
                parsed = int(value)
                if parsed < 0:
                    raise ValueError
            except Exception:
                invalid.append(
                    {
                        "name": name,
                        "value": value,
                        "reason": "must be a non-negative integer count",
                    }
                )
        elif kind == "non_empty_list":
            if not isinstance(value, list) or not value:
                invalid.append(
                    {
                        "name": name,
                        "value": value,
                        "reason": "must be a non-empty list",
                    }
                )
        elif kind == "required_value":
            if value is None or value == "":
                invalid.append(
                    {
                        "name": name,
                        "value": value,
                        "reason": "must be a non-empty value",
                    }
                )
    return invalid


def _evidence_kind(name: str, required_evidence: list[str]) -> str:
    if name in _positive_id_evidence_names(required_evidence):
        return "positive_integer_id"
    if name.endswith("_verified"):
        return "boolean_true"
    if name.endswith("_before") or name.endswith("_after"):
        return "integer_count"
    if name in {"regions"}:
        return "non_empty_list"
    return "required_value"


def _evidence_schema(required_evidence: list[str]) -> dict[str, dict[str, str]]:
    return {
        name: {
            "kind": _evidence_kind(name, required_evidence),
            "required": "true",
        }
        for name in required_evidence
    }


def _recording_steps(route_name: str, requirement: dict[str, Any]) -> list[str]:
    required_markers = list(requirement.get("required_markers", []))
    required_evidence = list(requirement.get("required_evidence", []))
    steps = [
        "Start HyperMesh command recording before the manual GUI operation.",
        "Perform only the target route operation in the current HyperMesh profile.",
    ]
    if required_markers:
        steps.append(f"Confirm the recording text contains these Tcl markers: {', '.join(required_markers)}.")
    else:
        steps.append("Confirm the recording text contains at least one HyperMesh Tcl command line beginning with * or hm_.")
    if requirement.get("count_pairs"):
        pairs = ", ".join(f"{before}->{after}" for before, after in requirement.get("count_pairs", []))
        steps.append(f"Capture before/after entity counts and verify increases for: {pairs}.")
    if "display_verified" in required_evidence:
        steps.append("Refresh/fit the GUI and confirm the created or modified entities are visible.")
    if _positive_id_evidence_names(required_evidence):
        steps.append("Record positive HyperMesh entity ids for component/property/material/EOS/mass/section bindings.")
    steps.append(f"Call hm_modeling_action validate_recording with route_name={route_name}, recording_text, and runtime_evidence.")
    steps.append("Promote the route only when promotion_ready=true; do not execute this route through MCP before promotion.")
    return steps


def _promotion_checklist(route_name: str, requirement: dict[str, Any]) -> list[dict[str, Any]]:
    """Return map fields that must be reviewed before a route becomes executable."""
    return [
        {
            "target": f"templates/hm_command_map.json routes.{route_name}.status",
            "required_value": "verified",
            "reason": "Only verified routes may execute Tcl.",
        },
        {
            "target": f"templates/hm_command_map.json routes.{route_name}.mcp_execution_allowed",
            "required_value": True,
            "reason": "Execution must remain blocked until this flag is intentionally set after validation.",
        },
        {
            "target": f"templates/hm_command_map.json routes.{route_name}.tested_in_session",
            "required_value": True,
            "reason": "Route must be proven in the connected HyperMesh GUI/profile before agent use.",
        },
        {
            "target": f"templates/hm_command_map.json routes.{route_name}.runtime_validation",
            "required_value": "recording_text, runtime_evidence, count/display checks, and dependency status",
            "reason": "Future agents need the exact evidence that justified promotion.",
        },
        {
            "target": f"templates/hm_command_map.json routes.{route_name}.commands",
            "required_value": list(requirement.get("required_markers", [])),
            "reason": "The verified map must preserve the command markers found in HyperMesh command recording.",
        },
        {
            "target": f"templates/hm_command_map.json routes.{route_name}.limits",
            "required_value": "explicit route-specific bounds",
            "reason": "New executable routes need bounded input sizes before MCP dispatch.",
        },
        {
            "target": f"templates/hm_command_map.json unsupported_routes.{route_name}",
            "required_value": "removed after route is added to routes",
            "reason": "A route must not be both executable and documented as unsupported.",
        },
        {
            "target": "tests",
            "required_value": "route execution/guardrail tests updated",
            "reason": "Promotion must add tests proving execution is gated and validated.",
        },
    ]


def _promotion_checklist_reasons(route_name: str, requirement: dict[str, Any]) -> list[str]:
    checklist = _promotion_checklist(route_name, requirement)
    if not isinstance(checklist, list) or not checklist:
        return ["promotion_checklist_missing"]
    required_targets = {
        f"templates/hm_command_map.json routes.{route_name}.status",
        f"templates/hm_command_map.json routes.{route_name}.mcp_execution_allowed",
        f"templates/hm_command_map.json routes.{route_name}.tested_in_session",
        f"templates/hm_command_map.json routes.{route_name}.runtime_validation",
        f"templates/hm_command_map.json routes.{route_name}.commands",
        f"templates/hm_command_map.json routes.{route_name}.limits",
        f"templates/hm_command_map.json unsupported_routes.{route_name}",
        "tests",
    }
    reasons: list[str] = []
    targets = set()
    for item in checklist:
        if not isinstance(item, dict):
            reasons.append("promotion_checklist_item_not_dict")
            continue
        target = item.get("target")
        if not isinstance(target, str) or not target:
            reasons.append("promotion_checklist_target_missing")
        else:
            targets.add(target)
        if "required_value" not in item:
            reasons.append("promotion_checklist_required_value_missing")
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason:
            reasons.append("promotion_checklist_reason_missing")
    missing_targets = required_targets - targets
    if missing_targets:
        reasons.append("promotion_checklist_target_coverage_missing")
    return list(dict.fromkeys(reasons))


def validate_recorded_route(element_key: Optional[str], parameters: dict[str, Any]) -> dict[str, Any]:
    route_name = str(parameters.get("route_name", "")).strip()
    recording_text = str(parameters.get("recording_text", ""))
    runtime_evidence = parameters.get("runtime_evidence", {})
    if not isinstance(runtime_evidence, dict):
        runtime_evidence = {}

    requirement = RECORDING_ROUTE_REQUIREMENTS.get(route_name)
    if requirement is None:
        return recording_blocked(
            action="validate_recording",
            element_type=element_key,
            error_type="recording_route_not_supported",
            reason="This route_name is not supported by the MCP recording validation guard.",
            required_verification=[
                "Choose a supported route_name from recording_requirements, then attach the HyperMesh command recording Tcl and runtime evidence.",
            ],
        )
    expected_element_type = requirement["element_type"]
    if expected_element_type is not None and element_key is not None and element_key != expected_element_type:
        return recording_blocked(
            action="validate_recording",
            element_type=element_key,
            error_type="recording_element_type_mismatch",
            reason=f"{route_name} recordings must use element_type={expected_element_type}.",
            required_verification=[f"Retry with element_type={expected_element_type}."],
        )

    recording_text_present = bool(recording_text.strip())
    recording_command_present = _recording_command_present(recording_text)
    lowered = recording_text.lower()
    missing_markers = [marker for marker in requirement["required_markers"] if marker.lower() not in lowered]
    route_forbidden_markers = [marker for marker in requirement["forbidden_markers"] if marker.lower() in lowered]
    forbidden_markers = list(dict.fromkeys([*route_forbidden_markers, *_global_forbidden_recording_markers(recording_text)]))
    expected_evidence_schema = _evidence_schema(requirement["required_evidence"])
    recording_steps = _recording_steps(route_name, requirement)
    promotion_checklist = _promotion_checklist(route_name, requirement)
    missing_evidence = [name for name in requirement["required_evidence"] if name not in runtime_evidence]
    false_evidence = [
        name
        for name in requirement["required_evidence"]
        if name.endswith("_verified") and runtime_evidence.get(name) is not True
    ]
    invalid_evidence_values = _invalid_evidence_values(requirement["required_evidence"], runtime_evidence)

    evidence_ok = not missing_evidence and not false_evidence and not invalid_evidence_values
    count_failures: list[dict[str, Any]] = []
    for before_key, after_key in requirement.get("count_pairs", []):
        if before_key not in runtime_evidence or after_key not in runtime_evidence:
            continue
        try:
            pair_ok = int(runtime_evidence[after_key]) > int(runtime_evidence[before_key])
        except Exception:
            pair_ok = False
        if not pair_ok:
            count_failures.append({"before": before_key, "after": after_key})
    count_ok = not count_failures
    display_ok = runtime_evidence.get("display_verified") is True if "display_verified" in requirement["required_evidence"] else True
    recording_valid = recording_text_present and recording_command_present and not missing_markers and not forbidden_markers
    dependencies_satisfied, blocked_dependencies, dependency_status = _route_dependency_status(route_name)
    promotion_ready = recording_valid and evidence_ok and count_ok and display_ok and dependencies_satisfied

    return {
        "success": True,
        "action": "validate_recording",
        "route_name": route_name,
        "element_type": expected_element_type,
        "route_category": requirement.get("route_category", "recorded_route"),
        "execution_allowed": False,
        "mcp_execution_allowed": False,
        "requires_verified_map_promotion": True,
        "tcl_sent": False,
        "recording_text_present": recording_text_present,
        "recording_command_present": recording_command_present,
        "recording_valid": recording_valid,
        "runtime_evidence_valid": evidence_ok and count_ok and display_ok,
        "dependencies_satisfied": dependencies_satisfied,
        "blocked_dependencies": blocked_dependencies,
        "dependencies": dependency_status,
        "promotion_ready": promotion_ready,
        "missing_markers": missing_markers,
        "forbidden_markers": forbidden_markers,
        "missing_evidence": missing_evidence,
        "false_evidence": false_evidence,
        "invalid_evidence_values": invalid_evidence_values,
        "expected_evidence_schema": expected_evidence_schema,
        "recording_steps": recording_steps,
        "promotion_checklist": promotion_checklist,
        "count_increase_verified": count_ok,
        "count_failures": count_failures,
        "display_verified": display_ok,
        "promotion_target": requirement["promotion_target"],
        "next_steps": (
            [
                "Move the route from unsupported_routes into routes with status=verified.",
                "Add tested_in_session=true, runtime_validation, limits, and mcp_execution_allowed=true.",
                "Add/adjust MCP execution tests before allowing create_mesh to send Tcl.",
            ]
            if promotion_ready
            else [
                "Complete missing recording markers and runtime evidence.",
                "Verify blocked dependency routes first if blocked_dependencies is non-empty.",
                "Do not execute this route through MCP until promotion_ready=true and the verified map is updated.",
            ]
        ),
    }


def requirement_public_payload(route_name: str, requirement: dict[str, Any]) -> dict[str, Any]:
    required_evidence = list(requirement.get("required_evidence", []))
    return {
        "route_name": route_name,
        "element_type": requirement.get("element_type"),
        "required_markers": list(requirement.get("required_markers", [])),
        "forbidden_markers": list(requirement.get("forbidden_markers", [])),
        "required_evidence": required_evidence,
        "evidence_schema": _evidence_schema(required_evidence),
        "recording_steps": _recording_steps(route_name, requirement),
        "promotion_checklist": _promotion_checklist(route_name, requirement),
        "count_pairs": [list(pair) for pair in requirement.get("count_pairs", [])],
        "promotion_target": requirement.get("promotion_target"),
        "execution_allowed": False,
        "mcp_execution_allowed": False,
        "requires_verified_map_promotion": True,
        "tcl_sent": False,
    }


def recording_promotion_queue(command_map: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    """Return the recommended order for validating unsupported route promotions."""
    data = command_map if command_map is not None else load_command_map()
    unsupported_routes = data.get("unsupported_routes") or {}
    routes = data.get("routes") or {}
    route_names = set(unsupported_routes)
    ordered_names = [name for name in RECORDING_ROUTE_PROMOTION_ORDER if name in route_names]
    ordered_names.extend(sorted(route_names - set(ordered_names)))

    queue: list[dict[str, Any]] = []
    for index, route_name in enumerate(ordered_names, start=1):
        requirement = RECORDING_ROUTE_REQUIREMENTS.get(route_name, {})
        unsupported = unsupported_routes.get(route_name, {})
        dependencies_satisfied, blocked_dependencies, dependency_status = _route_dependency_status(route_name, data)
        required_evidence = list(requirement.get("required_evidence", []))
        queue.append(
            {
                "priority": index,
                "route_name": route_name,
                "element_type": requirement.get("element_type"),
                "entity_kind": unsupported.get("entity_kind"),
                "status": unsupported.get("status", "unsupported"),
                "blocked_by": blocked_dependencies,
                "dependencies": dependency_status,
                "ready_for_recording": dependencies_satisfied,
                "execution_allowed": False,
                "mcp_execution_allowed": False,
                "requires_verified_map_promotion": True,
                "tcl_sent": False,
                "required_markers": list(requirement.get("required_markers", [])),
                "required_evidence": required_evidence,
                "evidence_schema": _evidence_schema(required_evidence),
                "recording_steps": _recording_steps(route_name, requirement),
                "promotion_checklist": _promotion_checklist(route_name, requirement),
                "next_supported_actions": [
                    {
                        "action": "recording_requirements",
                        "route_name": route_name,
                    },
                    {
                        "action": "validate_recording",
                        "route_name": route_name,
                    },
                ],
            }
        )
    return queue


def recording_requirements_coverage(command_map: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Report whether every documented unsupported route has promotion requirements."""
    data = command_map if command_map is not None else load_command_map()
    unsupported_routes = documented_unsupported_route_names(data)
    requirement_routes = set(RECORDING_ROUTE_REQUIREMENTS.keys())
    missing_requirement_routes = sorted(unsupported_routes - requirement_routes)
    orphan_requirement_routes = sorted(requirement_routes - unsupported_routes)
    invalid_requirement_routes: list[dict[str, Any]] = []
    known_types = set(known_element_types())
    for route_name, requirement in sorted(RECORDING_ROUTE_REQUIREMENTS.items()):
        reasons = []
        element_type = requirement.get("element_type")
        if element_type is not None and element_type not in known_types:
            reasons.append("element_type_unknown")
        required_evidence = requirement.get("required_evidence")
        promotion_target = str(requirement.get("promotion_target", ""))
        if not isinstance(required_evidence, list) or not required_evidence:
            reasons.append("required_evidence_missing")
            evidence_names = set()
        else:
            evidence_names = {name for name in required_evidence if isinstance(name, str)}
            if any(not isinstance(name, str) for name in required_evidence):
                reasons.append("required_evidence_item_not_string")
        if route_name not in promotion_target:
            reasons.append("promotion_target_route_mismatch")
        forbidden_markers = requirement.get("forbidden_markers", [])
        if not isinstance(forbidden_markers, list):
            reasons.append("forbidden_markers_not_list")
        elif any(not isinstance(marker, str) for marker in forbidden_markers):
            reasons.append("forbidden_markers_item_not_string")
        required_markers = requirement.get("required_markers", [])
        if not isinstance(required_markers, list):
            reasons.append("required_markers_not_list")
        elif any(not isinstance(marker, str) for marker in required_markers):
            reasons.append("required_markers_item_not_string")
        count_pairs = requirement.get("count_pairs", [])
        if not isinstance(count_pairs, list):
            reasons.append("count_pairs_not_list")
        else:
            for pair in count_pairs:
                if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                    reasons.append("count_pair_invalid")
                    continue
                before_key, after_key = pair
                if before_key not in evidence_names or after_key not in evidence_names:
                    reasons.append("count_pair_evidence_missing")
        reasons.extend(_promotion_checklist_reasons(route_name, requirement))
        if reasons:
            invalid_requirement_routes.append({"route_name": route_name, "reasons": sorted(set(reasons))})
    promotion_order_routes = set(RECORDING_ROUTE_PROMOTION_ORDER)
    missing_promotion_order_routes = sorted(unsupported_routes - promotion_order_routes)
    orphan_promotion_order_routes = sorted(promotion_order_routes - unsupported_routes)
    return {
        "unsupported_route_count": len(unsupported_routes),
        "requirement_route_count": len(requirement_routes),
        "valid_requirement_count": len(requirement_routes) - len(invalid_requirement_routes),
        "invalid_requirement_count": len(invalid_requirement_routes),
        "missing_requirement_routes": missing_requirement_routes,
        "orphan_requirement_routes": orphan_requirement_routes,
        "invalid_requirement_routes": invalid_requirement_routes,
        "missing_promotion_order_routes": missing_promotion_order_routes,
        "orphan_promotion_order_routes": orphan_promotion_order_routes,
        "promotion_order_complete": not missing_promotion_order_routes and not orphan_promotion_order_routes,
        "complete": (
            not missing_requirement_routes
            and not orphan_requirement_routes
            and not invalid_requirement_routes
            and not missing_promotion_order_routes
            and not orphan_promotion_order_routes
        ),
    }


def documented_unsupported_route_names(command_map: Optional[dict[str, Any]] = None) -> set[str]:
    """Return unsupported route names documented in the command map."""
    data = command_map if command_map is not None else load_command_map()
    return set((data.get("unsupported_routes") or {}).keys())


def recording_requirements(element_key: Optional[str], parameters: dict[str, Any]) -> dict[str, Any]:
    coverage = recording_requirements_coverage()
    promotion_queue = recording_promotion_queue()
    filtered_promotion_queue = [
        item for item in promotion_queue if element_key is None or item.get("element_type") in (None, element_key)
    ]
    route_name = str(parameters.get("route_name", "")).strip()
    if route_name:
        requirement = RECORDING_ROUTE_REQUIREMENTS.get(route_name)
        if requirement is None:
            return recording_blocked(
                action="recording_requirements",
                element_type=element_key,
                error_type="recording_route_not_supported",
                reason="This route_name is not supported by the MCP recording requirements guard.",
                required_verification=[
                    "Call recording_requirements without route_name to list supported promotion routes.",
                ],
            )
        return {
            "success": True,
            "action": "recording_requirements",
            "route": requirement_public_payload(route_name, requirement),
            "supported_route_names": sorted(RECORDING_ROUTE_REQUIREMENTS),
            "promotion_queue": [
                item for item in filtered_promotion_queue if item["route_name"] == route_name
            ],
            "coverage": coverage,
        }

    routes = []
    for name, requirement in sorted(RECORDING_ROUTE_REQUIREMENTS.items()):
        expected = requirement.get("element_type")
        if element_key is not None and expected not in (None, element_key):
            continue
        routes.append(requirement_public_payload(name, requirement))
    return {
        "success": True,
        "action": "recording_requirements",
        "element_type": element_key,
        "count": len(routes),
        "routes": routes,
        "supported_route_names": sorted(RECORDING_ROUTE_REQUIREMENTS),
        "promotion_queue": filtered_promotion_queue,
        "recommended_next_routes": [
            item["route_name"] for item in filtered_promotion_queue if item["ready_for_recording"]
        ][:5],
        "coverage": coverage,
        "policy": "These are promotion requirements only. No Tcl is sent and execution remains blocked until validate_recording returns promotion_ready=true and the route is promoted to verified map.",
    }
