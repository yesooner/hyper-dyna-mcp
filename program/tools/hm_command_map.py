"""Verified HyperMesh Tcl command route map.

This module keeps modeling tools from guessing HyperMesh Tcl commands.
Only routes marked as verified in templates/hm_command_map.json should be
used by high-level model creation helpers.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_MAP_PATH = Path(__file__).resolve().parents[2] / "templates" / "hm_command_map.json"
_ALLOWED_ROUTE_STATUSES = {"verified"}

_ELEMENT_CAPABILITY_ALIASES = {
    "solid": "solid_hex",
    "solid element": "solid_hex",
    "hex": "solid_hex",
    "hex8": "solid_hex",
    "brick": "solid_hex",
    "solid_hex": "solid_hex",
    "tet": "solid_tet",
    "tetra": "solid_tet",
    "tet4": "solid_tet",
    "solid_tet": "solid_tet",
    "shell": "shell_quad",
    "shell element": "shell_quad",
    "quad": "shell_quad",
    "quad4": "shell_quad",
    "shell_quad": "shell_quad",
    "tria": "shell_tria",
    "tri": "shell_tria",
    "tria3": "shell_tria",
    "shell_tria": "shell_tria",
    "line": "line_beam",
    "beam": "line_beam",
    "beam element": "line_beam",
    "bar2": "line_beam",
    "line_beam": "line_beam",
    "lumped": "lumped_mass",
    "mass": "lumped_mass",
    "lumped element": "lumped_mass",
    "lumped_mass": "lumped_mass",
    "discrete": "discrete",
    "discrete element": "discrete",
    "district": "discrete",
    "spring": "discrete",
    "mixed": "mixed",
    "hybrid": "mixed",
    "mixed mesh": "mixed",
}

_ELEMENT_CAPABILITY_MATRIX = {
    "solid_hex": {
        "labels": ["solid element", "HEX", "HEX8"],
        "element_family": "solid",
        "creation": {
            "supported": True,
            "tool": "hm_create_fe_cube",
            "route_name": "create_structured_hex8_box",
            "entity_kind": "fe_mesh",
            "notes": "Creates structured HEX8 FE nodes/elements directly. This is not CAD geometry solid creation.",
        },
        "meshing": {
            "supported": True,
            "tool": "hm_create_fe_cube",
            "route_name": "create_structured_hex8_box",
            "method": "structured direct FE generation",
            "limits_source": "templates/hm_command_map.json routes.create_structured_hex8_box.limits",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_hex_part",
            "reason": "Part/property/material datanames for LS-DYNA solid sections are not execution-verified.",
        },
        "k_file_generation": {
            "supported": True,
            "module": "program.tools.k_writer",
            "keywords": ["*NODE", "*ELEMENT_SOLID", "*SECTION_SOLID", "*MAT_ELASTIC", "*PART"],
            "notes": "Offline fixture/validation only. Agents must not use this to bypass HyperMesh GUI Tcl execution.",
        },
    },
    "solid_tet": {
        "labels": ["TET", "TET4", "tetra solid"],
        "element_family": "solid",
        "creation": {
            "supported": True,
            "tool": "hm_create_tet4",
            "route_name": "create_tet_element",
            "entity_kind": "fe_tet_element",
            "notes": "Creates one direct TET4 element with *createelement 204. This is not geometry *tetmesh.",
        },
        "meshing": {
            "supported": False,
            "route_name": "tetmesh_geometry_solid",
            "reason": "Geometry-solid tetmesh is unsupported until HyperMesh command recording verifies *tetmesh workflow.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_tet_part",
            "reason": "Requires verified part/property/material route after TET creation/meshing route exists.",
        },
        "k_file_generation": {
            "supported": False,
            "reason": "Dedicated TET4 writer semantics are not separated from generic ELEMENT_SOLID yet.",
        },
    },
    "shell_quad": {
        "labels": ["shell element", "quad", "QUAD4"],
        "element_family": "shell",
        "creation": {
            "supported": True,
            "tool": "hm_create_shell_plate",
            "route_name": "create_structured_quad4_shell_plate",
            "entity_kind": "fe_shell_mesh",
            "notes": "Creates structured QUAD4 shell FE nodes/elements directly. This is not geometry surface creation or surface automesh.",
        },
        "geometry_surface_creation": {
            "supported": True,
            "tool": "hm_create_surface_plate",
            "route_name": "create_geometry_surface_rect_nurbs",
            "entity_kind": "geometry_surface",
            "notes": "Creates a rectangular HyperMesh geometry surface only; this is not QUAD4 shell FE element creation.",
        },
        "meshing": {
            "supported": False,
            "route_name": "surface_automesh",
            "reason": "Surface automesh is not verified for the GUI-only MCP execution path.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_shell_part",
            "reason": "Shell section/property thickness and material datanames require command recording.",
        },
        "k_file_generation": {
            "supported": True,
            "module": "program.tools.k_writer.build_shell_plate_model",
            "keywords": [
                "*NODE",
                "*ELEMENT_SHELL",
                "*ELEMENT_SHELL_THICKNESS",
                "*SECTION_SHELL",
                "*MAT_ELASTIC",
                "*PART",
            ],
            "notes": "Offline fixture/validation only. This does not authorize shell creation or K export as an MCP workflow.",
        },
    },
    "shell_tria": {
        "labels": ["tria", "TRIA3", "tri shell"],
        "element_family": "shell",
        "creation": {
            "supported": True,
            "tool": "hm_create_tria3",
            "route_name": "create_shell_tria3",
            "entity_kind": "fe_shell_element",
            "notes": "Creates one direct TRIA3 element with *createelement 103. This is not surface automesh.",
        },
        "meshing": {
            "supported": False,
            "route_name": "surface_automesh",
            "reason": "Triangular surface meshing controls are not verified for the GUI-only MCP execution path.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_shell_part",
            "reason": "Shell section/property thickness and material datanames require command recording.",
        },
        "k_file_generation": {
            "supported": False,
            "reason": "TRIA3-specific K writer route is not separated from QUAD4 shell generation yet.",
        },
    },
    "line_beam": {
        "labels": ["line", "beam element"],
        "element_family": "beam",
        "creation": {
            "supported": True,
            "tool": "hm_create_beam_line",
            "route_name": "create_beam_line",
            "entity_kind": "fe_beam_mesh",
            "notes": "Creates structured BAR2/BEAM elements with *createelement 60. Does not verify beam section datanames or orientation cards.",
        },
        "meshing": {
            "supported": False,
            "route_name": "line_mesh_beam",
            "reason": "Meshing an already-existing selected line is unsupported until HyperMesh command recording verifies the line mesh workflow. Use creation.create_beam_line only for generating a new straight visual line plus BAR2/BEAM elements.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_beam_part",
            "reason": "Beam section/property and orientation datanames require command recording.",
        },
        "k_file_generation": {
            "supported": True,
            "module": "program.tools.k_writer",
            "keywords": ["*NODE", "*ELEMENT_BEAM", "*SECTION_BEAM", "*MAT_ELASTIC", "*PART"],
            "notes": "Offline fixture/validation only. GUI beam creation and export remain blocked until Tcl routes are verified.",
        },
    },
    "lumped_mass": {
        "labels": ["lumped", "mass", "lumped mass"],
        "element_family": "mass",
        "creation": {
            "supported": True,
            "tool": "hm_create_lumped_mass",
            "route_name": "create_lumped_mass",
            "entity_kind": "fe_mass_element",
            "notes": "Creates a one-node MASS element with *masselement. Property/card datanames remain unverified.",
        },
        "meshing": {
            "supported": False,
            "route_name": "mesh_lumped_mass",
            "reason": "Lumped masses are assigned to nodes/sets rather than meshed as geometry; node/set route is unverified.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_lumped_mass",
            "reason": "Lumped mass generally needs mass/property definition, not ordinary material assignment; route is unverified.",
        },
        "k_file_generation": {
            "supported": False,
            "reason": "Lumped mass K keyword writer is not implemented as a structured route.",
        },
    },
    "discrete": {
        "labels": ["discrete element"],
        "element_family": "discrete",
        "creation": {
            "supported": True,
            "tool": "hm_create_discrete_spring",
            "route_name": "create_discrete_element",
            "entity_kind": "fe_discrete_element",
            "notes": "Creates a two-node DISCRETE spring element with *spring. Stiffness/damping datanames remain unverified.",
        },
        "meshing": {
            "supported": False,
            "route_name": "mesh_discrete_element",
            "reason": "Discrete elements connect existing nodes/sets rather than being generated by a mesh operation; route is unverified.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "assign_material_to_discrete_element",
            "reason": "Discrete behavior normally comes from property/section cards; verified datanames are missing.",
        },
        "k_file_generation": {
            "supported": False,
            "reason": "Discrete element K keyword writer is not implemented as a structured route.",
        },
    },
    "mixed": {
        "labels": ["mixed mesh", "hybrid mesh", "solid + shell + beam"],
        "element_family": "mixed",
        "creation": {
            "supported": False,
            "route_name": "mixed_element_workflow",
            "reason": "Mixed workflows are not a single verified MCP route.",
        },
        "meshing": {
            "supported": False,
            "route_name": "mixed_mesh_workflow",
            "reason": "Mixed HEX/TET/SHELL/BEAM meshing requires a recorded workflow with transition/interface rules.",
        },
        "material_assignment": {
            "supported": False,
            "route_name": "mixed_material_assignment",
            "reason": "Mixed model material/property/section assignment requires per-family verified datanames and binding rules.",
        },
        "k_file_generation": {
            "supported": False,
            "reason": "Mixed-model K generation is not an MCP execution route and must not bypass HyperMesh GUI verification.",
        },
    },
}


@lru_cache(maxsize=1)
def load_command_map() -> dict[str, Any]:
    """Load the verified HyperMesh command map."""
    if not _MAP_PATH.exists():
        return {"version": 0, "routes": {}, "unsupported_routes": {}}
    return json.loads(_MAP_PATH.read_text(encoding="utf-8"))


def get_verified_route(route_name: str) -> dict[str, Any] | None:
    """Return a verified route by name, or None if absent/not verified."""
    route = load_command_map().get("routes", {}).get(route_name)
    if not route or route.get("status") != "verified":
        return None
    return _route_with_validation_metadata(route)


def get_unsupported_route(route_name: str) -> dict[str, Any] | None:
    """Return an unsupported route record, if documented."""
    route = load_command_map().get("unsupported_routes", {}).get(route_name)
    if not route:
        return None
    return route


def get_experimental_route(route_name: str) -> dict[str, Any] | None:
    """Return an experimental route record, if documented."""
    route = load_command_map().get("experimental_routes", {}).get(route_name)
    if not route:
        return None
    return route


def require_verified_route(route_name: str) -> dict[str, Any]:
    """Return a verified route or raise a clear unsupported-route error."""
    route = get_verified_route(route_name)
    if route is not None:
        return route

    unsupported = load_command_map().get("unsupported_routes", {}).get(route_name)
    if unsupported:
        reason = unsupported.get("reason", "Route is not verified.")
        raise ValueError(f"HyperMesh Tcl route is unsupported: {route_name}. {reason}")
    experimental = load_command_map().get("experimental_routes", {}).get(route_name)
    if experimental:
        reason = experimental.get("execution_block_reason", "Route is experimental.")
        raise ValueError(f"HyperMesh Tcl route is experimental: {route_name}. {reason}")
    raise ValueError(f"HyperMesh Tcl route is not verified: {route_name}")


def route_allows_mcp_execution(route: dict[str, Any]) -> bool:
    """Return whether a verified route is allowed for MCP tool execution."""
    if route.get("mcp_execution_allowed") is False:
        return False
    if route.get("agent_execution_allowed") is False:
        return False
    if route.get("execution_stage") == "experimental":
        return False
    return True


def require_executable_route(route_name: str) -> dict[str, Any]:
    """Return a verified route that is explicitly allowed for MCP execution."""
    experimental = get_experimental_route(route_name)
    if experimental:
        reason = experimental.get("execution_block_reason") or (
            "Route is experimental and must be promoted before MCP execution."
        )
        raise ValueError(f"HyperMesh Tcl route is not executable by MCP: {route_name}. {reason}")

    route = require_verified_route(route_name)
    if route_allows_mcp_execution(route):
        return route
    reason = route.get("execution_block_reason") or route.get("reason") or (
        "Route is verified as source evidence but is not allowed for MCP execution."
    )
    raise ValueError(f"HyperMesh Tcl route is not executable by MCP: {route_name}. {reason}")


def list_verified_routes() -> list[dict[str, Any]]:
    """List verified command routes."""
    routes = load_command_map().get("routes", {})
    return [
        {"name": name, **_route_with_validation_metadata(route)}
        for name, route in sorted(routes.items())
        if route.get("status") == "verified"
    ]


def command_map_stats() -> dict[str, Any]:
    """Return basic command map statistics."""
    data = load_command_map()
    routes = data.get("routes", {})
    unsupported = data.get("unsupported_routes", {})
    experimental = data.get("experimental_routes", {})
    validation = validate_command_map(data)
    return {
        "verified_routes": sum(1 for route in routes.values() if route.get("status") == "verified"),
        "runtime_validated_routes": sum(
            1
            for route in routes.values()
            if route.get("status") == "verified" and route.get("tested_in_session") is True
        ),
        "unsupported_routes": len(unsupported),
        "experimental_routes": len(experimental),
        "map_valid": validation["success"],
        "map_errors": validation["errors"],
        "map_warnings": validation["warnings"],
    }


def canonical_element_type(element_type: str | None) -> str | None:
    """Return the canonical element capability key for a user-facing label."""
    if not element_type:
        return None
    normalized = element_type.strip().lower()
    return _ELEMENT_CAPABILITY_ALIASES.get(normalized, normalized)


def known_element_types() -> list[str]:
    """Return canonical element types supported by the capability matrix."""
    return sorted(_ELEMENT_CAPABILITY_MATRIX)


def element_capability_matrix(element_type: str | None = None) -> dict[str, Any]:
    """Return executable capability status for requested FE element families."""
    data = load_command_map()
    routes = data.get("routes", {})
    unsupported = data.get("unsupported_routes", {})

    def enrich(name: str, item: dict[str, Any]) -> dict[str, Any]:
        enriched = {"name": name, **item}
        for area in ("creation", "geometry_surface_creation", "meshing", "material_assignment"):
            route_name = enriched.get(area, {}).get("route_name")
            if not route_name:
                continue
            if route_name in routes:
                route = routes[route_name]
                enriched[area]["route_status"] = route.get("status")
                enriched[area]["runtime_validated"] = route.get("tested_in_session") is True
                enriched[area]["verification_level"] = (
                    "runtime_validated" if route.get("tested_in_session") is True else "source_verified_runtime_pending"
                )
                enriched[area]["mcp_execution_allowed"] = route_allows_mcp_execution(route)
                if not enriched[area]["mcp_execution_allowed"]:
                    enriched[area]["execution_block_reason"] = route.get(
                        "execution_block_reason",
                        "Route is not allowed for default MCP/agent execution.",
                    )
            elif route_name in unsupported:
                enriched[area]["route_status"] = "unsupported"
                enriched[area]["required_verification"] = unsupported[route_name].get("required_verification", [])
            else:
                enriched[area]["route_status"] = "missing"
                enriched[area]["required_verification"] = [
                    "Add route evidence to templates/hm_command_map.json.",
                    "Verify Tcl in a connected HyperMesh GUI session before execution.",
                ]
            if area == "material_assignment" and route_name in routes and route_allows_mcp_execution(routes[route_name]):
                enriched[area]["supported"] = True
                enriched[area]["tool"] = "hm_set_keyword"
                enriched[area]["method"] = "GUI Tcl keyword template / component binding"
        k_file_generation = enriched.get("k_file_generation")
        if isinstance(k_file_generation, dict):
            k_file_generation.setdefault("role", "offline_fixture_validation_only")
            k_file_generation.setdefault("fixture_available", bool(k_file_generation.get("supported") is True))
            k_file_generation.setdefault("execution_scope", "offline_ls_dyna_keyword_fixture_only")
            k_file_generation.setdefault("agent_execution_allowed", False)
            k_file_generation.setdefault("mcp_execution_allowed", False)
            k_file_generation.setdefault("final_k_export_allowed", False)
            k_file_generation.setdefault("hypermesh_gui_export_route", False)
            k_file_generation.setdefault("preferred_modeling_path", "HyperMesh GUI Tcl listener / Tcl Console")
            k_file_generation.setdefault(
                "guardrail",
                "Do not use backend K writing to satisfy modeling or final K export requests in the GUI-only MCP.",
            )
        return enriched

    if element_type:
        key = canonical_element_type(element_type)
        item = _ELEMENT_CAPABILITY_MATRIX.get(key)
        if item is None:
            return {
                "success": False,
                "element_type": element_type,
                "known": False,
                "known_types": sorted(_ELEMENT_CAPABILITY_MATRIX),
                "aliases": sorted(_ELEMENT_CAPABILITY_ALIASES),
            }
        return {
            "success": True,
            "element_type": element_type,
            "canonical_type": key,
            "capability": enrich(key, item),
        }

    capabilities = {name: enrich(name, item) for name, item in _ELEMENT_CAPABILITY_MATRIX.items()}
    return {
        "success": True,
        "policy": "Only runtime-verified routes may execute Tcl. Missing/unsupported routes are planning-only.",
        "summary": {
            "types_checked": len(capabilities),
            "creation_supported": sorted(
                name for name, item in capabilities.items() if item["creation"].get("supported") is True
            ),
            "meshing_supported": sorted(
                name for name, item in capabilities.items() if item["meshing"].get("supported") is True
            ),
            "material_assignment_supported": sorted(
                name for name, item in capabilities.items() if item["material_assignment"].get("supported") is True
            ),
            "geometry_surface_creation_supported": sorted(
                name
                for name, item in capabilities.items()
                if item.get("geometry_surface_creation", {}).get("supported") is True
            ),
            "k_file_generation_supported": sorted(
                name for name, item in capabilities.items() if item.get("k_file_generation", {}).get("supported") is True
            ),
            "offline_k_file_generation_supported": sorted(
                name for name, item in capabilities.items() if item.get("k_file_generation", {}).get("supported") is True
            ),
            "k_file_generation_agent_execution_allowed": sorted(
                name
                for name, item in capabilities.items()
                if item.get("k_file_generation", {}).get("agent_execution_allowed") is True
            ),
            "k_file_generation_mcp_execution_allowed": sorted(
                name
                for name, item in capabilities.items()
                if item.get("k_file_generation", {}).get("mcp_execution_allowed") is True
            ),
            "final_k_export_supported": sorted(
                name
                for name, item in capabilities.items()
                if item.get("k_file_generation", {}).get("final_k_export_allowed") is True
            ),
            "hypermesh_gui_k_export_supported": sorted(
                name
                for name, item in capabilities.items()
                if item.get("k_file_generation", {}).get("hypermesh_gui_export_route") is True
            ),
        },
        "capabilities": capabilities,
    }


def get_route_limits(route_name: str) -> dict[str, int]:
    """Return integer route limits for a verified route."""
    route = require_verified_route(route_name)
    limits = route.get("limits", {})
    return {
        "max_elements": int(limits.get("max_elements", 5000)),
        "max_nodes": int(limits.get("max_nodes", 8000)),
    }


def validate_command_map(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate route-map invariants that protect executable modeling tools."""
    command_map = data if data is not None else load_command_map()
    routes = command_map.get("routes", {})
    unsupported = command_map.get("unsupported_routes", {})
    experimental = command_map.get("experimental_routes", {})
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(routes, dict):
        return {
            "success": False,
            "errors": ["routes must be an object."],
            "warnings": warnings,
            "routes_checked": 0,
        }

    for route_name, route in routes.items():
        if not isinstance(route, dict):
            errors.append(f"{route_name}: route must be an object.")
            continue

        status = route.get("status")
        if status not in _ALLOWED_ROUTE_STATUSES:
            errors.append(f"{route_name}: status must be one of {sorted(_ALLOWED_ROUTE_STATUSES)}.")

        commands = route.get("commands")
        if not isinstance(commands, list) or not commands or not all(isinstance(item, str) for item in commands):
            errors.append(f"{route_name}: commands must be a non-empty string list.")
            commands = []

        command_text = "\n".join(commands)
        entity_kind = route.get("entity_kind")
        if entity_kind == "fe_mesh":
            _validate_fe_mesh_route(route_name, route, command_text, errors)
        elif entity_kind == "geometry_solid":
            _validate_geometry_solid_route(route_name, route, command_text, errors, warnings)
        elif entity_kind == "geometry_surface":
            _validate_geometry_surface_route(route_name, route, command_text, errors, warnings)
        elif entity_kind == "keyword_card":
            _validate_keyword_card_route(route_name, route, command_text, errors)
        else:
            errors.append(f"{route_name}: entity_kind must be fe_mesh, geometry_solid, geometry_surface, or keyword_card.")

    if not isinstance(unsupported, dict):
        errors.append("unsupported_routes must be an object.")
    else:
        for route_name, route in unsupported.items():
            if not isinstance(route, dict) or route.get("status") != "unsupported":
                errors.append(f"{route_name}: unsupported route must have status=unsupported.")

    if not isinstance(experimental, dict):
        errors.append("experimental_routes must be an object.")
    else:
        for route_name, route in experimental.items():
            if not isinstance(route, dict) or route.get("status") != "experimental":
                errors.append(f"{route_name}: experimental route must have status=experimental.")
                continue
            _validate_experimental_route(route_name, route, errors)

    return {
        "success": not errors,
        "errors": errors,
        "warnings": warnings,
        "routes_checked": len(routes),
    }


def _validate_fe_mesh_route(route_name: str, route: dict[str, Any], command_text: str, errors: list[str]) -> None:
    limits = route.get("limits")
    if not isinstance(limits, dict):
        errors.append(f"{route_name}: fe_mesh route must define limits.")
        return

    for limit_name in ("max_elements", "max_nodes"):
        value = limits.get(limit_name)
        if not isinstance(value, int) or value <= 0:
            errors.append(f"{route_name}: limits.{limit_name} must be a positive integer.")

        if route_name == "create_structured_hex8_box":
            if route.get("element_config") != 208:
                errors.append(f"{route_name}: element_config must remain 208 for HEX8 elements.")
            for required in ("*createnode", "*createlist nodes", "*createelement 208"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
        if route_name == "create_structured_quad4_shell_plate":
            if route.get("element_config") != 104:
                errors.append(f"{route_name}: element_config must remain 104 for QUAD4 shell elements.")
            for required in ("*createnode", "*createlist nodes", "*createelement 104"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
        if route_name == "create_beam_line":
            if route.get("element_config") != 60:
                errors.append(f"{route_name}: element_config must remain 60 for BAR2/BEAM elements.")
            for required in ("*createnode", "*createlist nodes", "*createelement 60"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
            if "*createelement 2" in command_text:
                errors.append(f"{route_name}: must not use *createelement 2 because it creates Plotel.")
        if route_name == "create_discrete_element":
            if route.get("element_config") != 21:
                errors.append(f"{route_name}: element_config must remain 21 for DISCRETE elements.")
            for required in ("*createnode", "*spring"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
        if route_name == "create_lumped_mass":
            if route.get("element_config") != 1:
                errors.append(f"{route_name}: element_config must remain 1 for MASS elements.")
            for required in ("*createnode", "*createmark nodes", "*masselement"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
        if route_name == "create_tet_element":
            if route.get("element_config") != 204:
                errors.append(f"{route_name}: element_config must remain 204 for TET4 elements.")
            for required in ("*createnode", "*createlist nodes", "*createelement 204"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
        if route_name == "create_shell_tria3":
            if route.get("element_config") != 103:
                errors.append(f"{route_name}: element_config must remain 103 for TRIA3 elements.")
            for required in ("*createnode", "*createlist nodes", "*createelement 103"):
                if required not in command_text:
                    errors.append(f"{route_name}: missing required command marker {required}.")
        for forbidden in ("*solidblock", "*tetmesh", "*surfacecreatenurbs"):
            if forbidden in command_text:
                errors.append(f"{route_name}: FE route must not contain {forbidden}.")


def _validate_geometry_solid_route(
    route_name: str,
    route: dict[str, Any],
    command_text: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    if "*solidblock" not in command_text:
        errors.append(f"{route_name}: geometry_solid route must contain *solidblock.")
    if "*createelement" in command_text or "*createnode" in command_text:
        errors.append(f"{route_name}: geometry_solid route must not create FE mesh entities.")

    runtime_validation = route.get("runtime_validation")
    if not isinstance(runtime_validation, list) or not runtime_validation:
        errors.append(f"{route_name}: geometry_solid route must document runtime_validation checks.")

    if route.get("tested_in_session") is not True:
        warnings.append(f"{route_name}: source verified, runtime validation still pending in target HyperMesh.")
        if route.get("mcp_execution_allowed") is not False:
            errors.append(f"{route_name}: source-verified geometry_solid route must set mcp_execution_allowed=false.")
        if route.get("agent_execution_allowed") is not False:
            errors.append(f"{route_name}: source-verified geometry_solid route must set agent_execution_allowed=false.")
        if route.get("execution_stage") != "experimental":
            errors.append(f"{route_name}: source-verified geometry_solid route must set execution_stage=experimental.")


def _validate_experimental_route(route_name: str, route: dict[str, Any], errors: list[str]) -> None:
    if route.get("execution_stage") != "experimental":
        errors.append(f"{route_name}: experimental route must set execution_stage=experimental.")
    if route.get("mcp_execution_allowed") is not False:
        errors.append(f"{route_name}: experimental route must set mcp_execution_allowed=false.")
    if route.get("agent_execution_allowed") is not False:
        errors.append(f"{route_name}: experimental route must set agent_execution_allowed=false.")
    if not route.get("execution_block_reason"):
        errors.append(f"{route_name}: experimental route must document execution_block_reason.")
    promotion_required = route.get("promotion_required")
    if not isinstance(promotion_required, list) or not promotion_required:
        errors.append(f"{route_name}: experimental route must document promotion_required steps.")


def _validate_geometry_surface_route(
    route_name: str,
    route: dict[str, Any],
    command_text: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    for required in ("*createdoublearray", "*surfacecreatenurbs"):
        if required not in command_text:
            errors.append(f"{route_name}: geometry_surface route must contain {required}.")
    for forbidden in ("*createelement", "*createnode", "*solidblock", "*tetmesh"):
        if forbidden in command_text:
            errors.append(f"{route_name}: geometry_surface route must not contain {forbidden}.")

    runtime_validation = route.get("runtime_validation")
    if not isinstance(runtime_validation, list) or not runtime_validation:
        errors.append(f"{route_name}: geometry_surface route must document runtime_validation checks.")

    if route.get("tested_in_session") is not True:
        warnings.append(f"{route_name}: source verified, runtime validation still pending in target HyperMesh.")


def _validate_keyword_card_route(route_name: str, route: dict[str, Any], command_text: str, errors: list[str]) -> None:
    if not route.get("keyword_families"):
        errors.append(f"{route_name}: keyword_card route must define keyword_families.")
    runtime_validation = route.get("runtime_validation")
    if not isinstance(runtime_validation, list) or not runtime_validation:
        errors.append(f"{route_name}: keyword_card route must document runtime_validation checks.")
    if "*writefile" in command_text or "*feoutput" in command_text:
        errors.append(f"{route_name}: keyword_card route must not include file export commands.")


def _route_with_validation_metadata(route: dict[str, Any]) -> dict[str, Any]:
    """Return a route copy with explicit source/runtime validation semantics."""
    enriched = dict(route)
    runtime_validated = route.get("tested_in_session") is True
    enriched["runtime_validated"] = runtime_validated
    enriched["verification_level"] = "runtime_validated" if runtime_validated else "source_verified_runtime_pending"
    return enriched
