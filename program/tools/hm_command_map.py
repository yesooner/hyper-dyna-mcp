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


def require_verified_route(route_name: str) -> dict[str, Any]:
    """Return a verified route or raise a clear unsupported-route error."""
    route = get_verified_route(route_name)
    if route is not None:
        return route

    unsupported = load_command_map().get("unsupported_routes", {}).get(route_name)
    if unsupported:
        reason = unsupported.get("reason", "Route is not verified.")
        raise ValueError(f"HyperMesh Tcl route is unsupported: {route_name}. {reason}")
    raise ValueError(f"HyperMesh Tcl route is not verified: {route_name}")


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
    validation = validate_command_map(data)
    return {
        "verified_routes": sum(1 for route in routes.values() if route.get("status") == "verified"),
        "runtime_validated_routes": sum(
            1
            for route in routes.values()
            if route.get("status") == "verified" and route.get("tested_in_session") is True
        ),
        "unsupported_routes": len(unsupported),
        "map_valid": validation["success"],
        "map_errors": validation["errors"],
        "map_warnings": validation["warnings"],
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
        else:
            errors.append(f"{route_name}: entity_kind must be fe_mesh or geometry_solid.")

    if not isinstance(unsupported, dict):
        errors.append("unsupported_routes must be an object.")
    else:
        for route_name, route in unsupported.items():
            if not isinstance(route, dict) or route.get("status") != "unsupported":
                errors.append(f"{route_name}: unsupported route must have status=unsupported.")

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
        for forbidden in ("*solidblock", "*tetmesh"):
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


def _route_with_validation_metadata(route: dict[str, Any]) -> dict[str, Any]:
    """Return a route copy with explicit source/runtime validation semantics."""
    enriched = dict(route)
    runtime_validated = route.get("tested_in_session") is True
    enriched["runtime_validated"] = runtime_validated
    enriched["verification_level"] = "runtime_validated" if runtime_validated else "source_verified_runtime_pending"
    return enriched
