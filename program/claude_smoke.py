"""Claude Code compatible MCP stdio smoke test.

This module reads a Claude Code style ``mcpServers`` JSON file, starts the
configured MCP server over stdio, and verifies the repo-local tool surface.
It does not connect to HyperMesh unless ``--with-gui`` is passed.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


ALLOWED_TOOLS = {
    "ping",
    "check_environment",
    "load_path_config",
    "validate_path",
    "start_hypermesh_gui_listener",
    "check_hypermesh_connection",
    "diagnose_hypermesh_listener",
    "set_hypermesh_listener_port",
    "get_model_info",
    "execute_tcl_gui",
    "hm_python_api_status",
    "execute_hm_python_api",
    "hm_python_api_current_model_info",
    "hm_auto_save",
    "hm_check_model",
    "hm_read_materials",
    "hm_read_components",
    "hm_convert_model",
    "hm_set_keyword",
    "hm_keyword_help",
    "hm_create_box",
    "hm_mesh_box",
    "hm_create_solid_box",
    "hm_create_surface_plate",
    "hm_create_shell_plate",
    "hm_create_beam_line",
    "hm_create_discrete_spring",
    "hm_create_lumped_mass",
    "hm_create_fe_cube",
    "hm_visual_refresh",
    "hm_gui_modeling_smoke",
    "hm_search_keywords",
    "hm_keyword_map",
    "hm_command_map",
    "hm_element_capability_matrix",
    "dyna_keyword_policy",
    "dyna_keyword_query",
    "dyna_keyword_map_validate",
}

REQUIRED_TOOLS = {
    "check_hypermesh_connection",
    "diagnose_hypermesh_listener",
    "set_hypermesh_listener_port",
    "dyna_keyword_policy",
    "dyna_keyword_map_validate",
    "dyna_keyword_query",
    "hm_auto_save",
    "hm_command_map",
    "hm_element_capability_matrix",
    "hm_create_fe_cube",
    "hm_gui_modeling_smoke",
    "hm_create_solid_box",
    "hm_create_surface_plate",
    "hm_create_shell_plate",
    "hm_create_beam_line",
    "hm_create_discrete_spring",
    "hm_create_lumped_mass",
    "hm_visual_refresh",
    "hm_python_api_status",
    "execute_hm_python_api",
    "hm_python_api_current_model_info",
}

FORBIDDEN_TOOLS = {
    "execute_hmbatch",
    "execute_lsprepost",
    "generate_lsdyna_command",
    "hm_export_k",
    "parse_k_file",
    "parse_solver_log",
    "write_k_file",
}

EXPECTED_TOOL_COUNT = len(ALLOWED_TOOLS)


def load_claude_mcp_server(config_path: str | Path, server_name: str) -> dict[str, Any]:
    """Load one Claude Code MCP server entry from a repo-local JSON config."""
    path = Path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        raise ValueError("Config must contain an object field named mcpServers.")
    server = servers.get(server_name)
    if not isinstance(server, dict):
        raise ValueError(f"MCP server not found in config: {server_name}")
    for key in ("command", "args", "cwd"):
        if key not in server:
            raise ValueError(f"MCP server {server_name!r} is missing required key: {key}")
    if not isinstance(server["args"], list):
        raise ValueError(f"MCP server {server_name!r} args must be a list.")
    return server


def build_stdio_params(server: dict[str, Any]) -> StdioServerParameters:
    """Build MCP stdio parameters without changing global Claude Code config."""
    env = os.environ.copy()
    env.update(server.get("env", {}) or {})
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.setdefault("FASTMCP_LOG_LEVEL", "ERROR")
    env.setdefault("LOGURU_LEVEL", "ERROR")
    return StdioServerParameters(
        command=str(server["command"]),
        args=[str(arg) for arg in server["args"]],
        cwd=str(server["cwd"]),
        env=env,
    )


async def run_smoke(
    config_path: str | Path = "claude_code_mcp.json",
    server_name: str = "hyper-dyna-mcp",
    *,
    with_gui: bool = False,
    port: int | None = None,
    modeling_smoke: bool = False,
) -> dict[str, Any]:
    """Run a Claude Code MCP smoke check and return a JSON-serializable result."""
    server = load_claude_mcp_server(config_path, server_name)
    params = build_stdio_params(server)

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tool_names = sorted(tool.name for tool in tools_result.tools)

            dyna_policy = await session.call_tool("dyna_keyword_policy", {})
            dyna_map_validate = await session.call_tool("dyna_keyword_map_validate", {})
            dyna_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "MAT_3"}},
            )
            dyna_control_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "CONTROL_TERMINATION"}},
            )
            dyna_section_solid_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "SECTION_SOLID"}},
            )
            dyna_d3plot_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "DATABASE_BINARY_D3PLOT"}},
            )
            dyna_timestep_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "CONTROL_TIMESTEP"}},
            )
            dyna_initial_detonation_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "INITIAL_DETONATION"}},
            )
            dyna_load_blast_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "LOAD_BLAST"}},
            )
            dyna_unknown_suggestion_query = await session.call_tool(
                "dyna_keyword_query",
                {"params": {"keyword": "LOAD_BLAS"}},
            )
            blocked_section_set_keyword = await session.call_tool(
                "hm_set_keyword",
                {"params": {"keyword": "SECTION_SOLID", "params": {"SECID": 1, "ELFORM": 1}}},
            )
            dyna_query_payload = _json_text_payload(dyna_query)
            dyna_control_query_payload = _json_text_payload(dyna_control_query)
            dyna_section_solid_query_payload = _json_text_payload(dyna_section_solid_query)
            dyna_d3plot_query_payload = _json_text_payload(dyna_d3plot_query)
            dyna_timestep_query_payload = _json_text_payload(dyna_timestep_query)
            dyna_initial_detonation_query_payload = _json_text_payload(dyna_initial_detonation_query)
            dyna_load_blast_query_payload = _json_text_payload(dyna_load_blast_query)
            dyna_unknown_suggestion_query_payload = _json_text_payload(dyna_unknown_suggestion_query)
            blocked_section_set_keyword_payload = _json_text_payload(blocked_section_set_keyword)
            dyna_field_status_ok = _dyna_field_status_guardrail_ok(dyna_query_payload)
            dyna_control_status_ok = _dyna_control_status_guardrail_ok(dyna_control_query_payload)
            dyna_section_solid_status_ok = _dyna_section_solid_status_guardrail_ok(
                dyna_section_solid_query_payload
            )
            dyna_d3plot_status_ok = _dyna_d3plot_status_guardrail_ok(dyna_d3plot_query_payload)
            dyna_timestep_status_ok = _dyna_timestep_status_guardrail_ok(dyna_timestep_query_payload)
            dyna_initial_detonation_status_ok = _dyna_initial_detonation_status_guardrail_ok(
                dyna_initial_detonation_query_payload
            )
            dyna_load_blast_status_ok = _dyna_load_blast_status_guardrail_ok(dyna_load_blast_query_payload)
            dyna_unknown_suggestion_ok = _dyna_unknown_suggestion_guardrail_ok(
                dyna_unknown_suggestion_query_payload,
                expected_keyword="*LOAD_BLAST",
            )
            blocked_section_set_keyword_ok = _blocked_keyword_execution_ok(blocked_section_set_keyword_payload)
            command_map = await session.call_tool(
                "hm_command_map",
                {"params": {"route_name": "create_structured_hex8_box"}},
            )
            solid_command_map = await session.call_tool(
                "hm_command_map",
                {"params": {"route_name": "create_geometry_solid_box"}},
            )
            element_capability_matrix_result = await session.call_tool(
                "hm_element_capability_matrix",
                {"params": {}},
            )
            solid_command_map_payload = _json_text_payload(solid_command_map)
            element_capability_matrix_payload = _json_text_payload(element_capability_matrix_result)
            solid_route_runtime_status_ok = _solid_route_runtime_status_ok(solid_command_map_payload)
            set_port_result = None
            if port is not None:
                set_port_result = await session.call_tool(
                    "set_hypermesh_listener_port",
                    {"params": {"port": int(port)}},
                )
            set_port_payload = _json_text_payload(set_port_result)

            gui_result = None
            gui_diagnostics = None
            modeling_smoke_result = None
            modeling_smoke_payload = None
            gui_payload = None
            gui_diagnostics_payload = None
            if with_gui:
                gui_result = await session.call_tool("check_hypermesh_connection", {})
                gui_payload = _json_text_payload(gui_result)
                gui_diagnostics = await session.call_tool(
                    "diagnose_hypermesh_listener",
                    {"params": {"include_alternate": port is None}},
                )
                gui_diagnostics_payload = _json_text_payload(gui_diagnostics)
                gui_version_status = _gui_listener_version_status(gui_payload, gui_diagnostics_payload)
                if (
                    modeling_smoke
                    and gui_payload
                    and gui_payload.get("connected") is True
                    and gui_version_status.get("ok") is True
                ):
                    modeling_smoke_result = await session.call_tool(
                        "hm_gui_modeling_smoke",
                        {"params": {"size": 10.0, "element_size": 10.0, "timeout": 30}},
                    )
                    modeling_smoke_payload = _json_text_payload(modeling_smoke_result)

    missing = sorted(REQUIRED_TOOLS.difference(tool_names))
    forbidden = sorted(FORBIDDEN_TOOLS.intersection(tool_names))
    unexpected = sorted(set(tool_names).difference(ALLOWED_TOOLS))
    guardrail_failures: list[str] = []
    if unexpected:
        guardrail_failures.append(
            "Unexpected MCP tools are exposed outside the HyperMesh GUI-only allowed surface: "
            + ", ".join(unexpected)
        )
    if len(tool_names) != EXPECTED_TOOL_COUNT:
        guardrail_failures.append(
            f"MCP tool count drifted: expected {EXPECTED_TOOL_COUNT}, got {len(tool_names)}."
        )
    if not dyna_field_status_ok:
        guardrail_failures.append("dyna_keyword_query field_execution_status marks unverified MAT_3 fields executable.")
    if not dyna_control_status_ok:
        guardrail_failures.append(
            "dyna_keyword_query field_execution_status marks unverified CONTROL_TERMINATION fields executable."
        )
    if not dyna_section_solid_status_ok:
        guardrail_failures.append(
            "dyna_keyword_query field_execution_status marks unverified SECTION_SOLID fields executable."
        )
    if not dyna_d3plot_status_ok:
        guardrail_failures.append(
            "dyna_keyword_query field_execution_status marks unverified DATABASE_BINARY_D3PLOT fields executable."
        )
    if not dyna_timestep_status_ok:
        guardrail_failures.append("dyna_keyword_query field_execution_status marks unverified CONTROL_TIMESTEP fields executable.")
    if not dyna_initial_detonation_status_ok:
        guardrail_failures.append(
            "dyna_keyword_query field_execution_status marks unverified INITIAL_DETONATION fields executable."
        )
    if not dyna_load_blast_status_ok:
        guardrail_failures.append("dyna_keyword_query field_execution_status marks unverified LOAD_BLAST fields executable.")
    if not dyna_unknown_suggestion_ok:
        guardrail_failures.append("dyna_keyword_query suggestions must stay non-executable for unknown/near-match keywords.")
    if not blocked_section_set_keyword_ok:
        guardrail_failures.append("hm_set_keyword must block unverified SECTION_SOLID execution before Tcl is sent.")
    if not solid_route_runtime_status_ok:
        guardrail_failures.append("hm_command_map create_geometry_solid_box must expose runtime validation status.")
    if not _element_capability_guardrail_ok(element_capability_matrix_payload):
        guardrail_failures.append(
            "hm_element_capability_matrix must report only verified FE creation routes, keep surface automesh/material assignment blocked, and keep K writer execution disabled."
        )
    gui_connected = True
    gui_version_status = None
    gui_listener_version_ok = True
    if with_gui:
        gui_connected = bool(gui_payload and gui_payload.get("connected") is True)
        gui_version_status = _gui_listener_version_status(gui_payload, gui_diagnostics_payload)
        gui_listener_version_ok = bool(gui_version_status.get("ok"))
    gui_diagnosis = _gui_diagnosis(gui_diagnostics_payload) if with_gui else None
    gui_listener_runtime = _gui_listener_runtime(gui_payload, gui_diagnostics_payload) if with_gui else None
    modeling_smoke_ok = True
    modeling_visual_counts = None
    modeling_visual_displayed_counts = None
    modeling_visual_count_methods = None
    modeling_visual_display_count_methods = None
    modeling_visibility = None
    modeling_visual_steps = None
    modeling_visual_diagnostics = None
    modeling_visual_refresh = None
    modeling_runtime_validation_evidence = None
    modeling_visual_counts_ok = None
    modeling_visual_display_ok = None
    modeling_smoke_failure = None
    if modeling_smoke:
        modeling_visual_counts = _modeling_visual_counts(modeling_smoke_payload)
        modeling_visual_displayed_counts = _modeling_visual_displayed_counts(modeling_smoke_payload)
        modeling_visual_count_methods = _modeling_visual_count_methods(modeling_smoke_payload)
        modeling_visual_display_count_methods = _modeling_visual_display_count_methods(modeling_smoke_payload)
        modeling_visibility = _modeling_visibility(modeling_smoke_payload)
        modeling_visual_steps = _modeling_visual_steps(modeling_smoke_payload)
        modeling_visual_diagnostics = _modeling_visual_diagnostics(modeling_smoke_payload)
        modeling_visual_refresh = _modeling_visual_refresh(modeling_smoke_payload)
        modeling_runtime_validation_evidence = _modeling_runtime_validation_evidence(modeling_smoke_payload)
        modeling_visual_counts_ok = _modeling_visual_counts_ok(modeling_smoke_payload)
        modeling_visual_display_ok = _modeling_visual_display_ok(modeling_smoke_payload)
        modeling_smoke_ok = bool(
            modeling_smoke_payload
            and modeling_smoke_payload.get("success") is True
            and modeling_visual_counts_ok
            and modeling_visual_display_ok
        )
        modeling_smoke_failure = _modeling_smoke_failure(
            gui_connected=gui_connected,
            listener_version_ok=gui_listener_version_ok,
            listener_version_status=gui_version_status,
            payload=modeling_smoke_payload,
            visual_counts=modeling_visual_counts,
            visual_counts_ok=modeling_visual_counts_ok,
            visual_displayed_counts=modeling_visual_displayed_counts,
            visibility=modeling_visibility,
            visual_display_ok=modeling_visual_display_ok,
        )
    next_hypermesh_commands = _next_hypermesh_commands(
        set_port_payload=set_port_payload,
        diagnostics_payload=gui_diagnostics_payload,
        port=port,
        include=bool(with_gui and not (gui_connected and gui_listener_version_ok)),
    )
    retry_smoke_command = _retry_smoke_command(
        config_path=config_path,
        server_name=server_name,
        with_gui=with_gui,
        modeling_smoke=modeling_smoke,
        port=port,
        include=bool(with_gui and not (gui_connected and gui_listener_version_ok)),
    )
    success = (
        not missing
        and not forbidden
        and not guardrail_failures
        and gui_connected
        and gui_listener_version_ok
        and modeling_smoke_ok
    )

    return {
        "success": success,
        "server_name": server_name,
        "tool_count": len(tool_names),
        "expected_tool_count": EXPECTED_TOOL_COUNT,
        "missing_required_tools": missing,
        "forbidden_tools": forbidden,
        "unexpected_tools": unexpected,
        "guardrail_failures": guardrail_failures,
        "has_python_api_tools": {
            "hm_python_api_status": "hm_python_api_status" in tool_names,
            "execute_hm_python_api": "execute_hm_python_api" in tool_names,
            "hm_python_api_current_model_info": "hm_python_api_current_model_info" in tool_names,
        },
        "gui_connected": gui_connected if with_gui else None,
        "gui_listener_version_ok": gui_listener_version_ok if with_gui else None,
        "gui_listener_version": gui_version_status if with_gui else None,
        "gui_listener_runtime": gui_listener_runtime,
        "gui_diagnosis": gui_diagnosis,
        "gui_connection": gui_payload if with_gui else None,
        "gui_diagnostics": gui_diagnostics_payload if with_gui else None,
        "set_port_result": set_port_payload if port is not None else None,
        "modeling_smoke_ok": modeling_smoke_ok if modeling_smoke else None,
        "modeling_smoke_failure": modeling_smoke_failure if modeling_smoke else None,
        "modeling_visual_counts_ok": modeling_visual_counts_ok if modeling_smoke else None,
        "modeling_visual_display_ok": modeling_visual_display_ok if modeling_smoke else None,
        "modeling_visual_counts": modeling_visual_counts if modeling_smoke else None,
        "modeling_visual_displayed_counts": modeling_visual_displayed_counts if modeling_smoke else None,
        "modeling_visual_count_methods": modeling_visual_count_methods if modeling_smoke else None,
        "modeling_visual_display_count_methods": (
            modeling_visual_display_count_methods if modeling_smoke else None
        ),
        "modeling_visibility": modeling_visibility if modeling_smoke else None,
        "modeling_visual_steps": modeling_visual_steps if modeling_smoke else None,
        "modeling_visual_diagnostics": modeling_visual_diagnostics if modeling_smoke else None,
        "modeling_visual_refresh": modeling_visual_refresh if modeling_smoke else None,
        "modeling_runtime_validation_evidence": (
            modeling_runtime_validation_evidence if modeling_smoke else None
        ),
        "next_hypermesh_commands": next_hypermesh_commands,
        "retry_smoke_command": retry_smoke_command,
        "checked_tools": {
            "dyna_keyword_policy": _first_text(dyna_policy),
            "dyna_keyword_map_validate": _first_text(dyna_map_validate),
            "dyna_keyword_query": _first_text(dyna_query),
            "dyna_control_keyword_query": _first_text(dyna_control_query),
            "dyna_section_solid_keyword_query": _first_text(dyna_section_solid_query),
            "dyna_d3plot_keyword_query": _first_text(dyna_d3plot_query),
            "dyna_timestep_keyword_query": _first_text(dyna_timestep_query),
            "dyna_initial_detonation_keyword_query": _first_text(dyna_initial_detonation_query),
            "dyna_load_blast_keyword_query": _first_text(dyna_load_blast_query),
            "dyna_unknown_suggestion_query": _first_text(dyna_unknown_suggestion_query),
            "hm_set_keyword_section_solid_blocked": _first_text(blocked_section_set_keyword),
            "hm_command_map": _first_text(command_map),
            "hm_solid_command_map": _first_text(solid_command_map),
            "hm_element_capability_matrix": _first_text(element_capability_matrix_result),
            "set_hypermesh_listener_port": _first_text(set_port_result) if set_port_result else None,
            "check_hypermesh_connection": _first_text(gui_result) if gui_result else None,
            "diagnose_hypermesh_listener": _first_text(gui_diagnostics) if gui_diagnostics else None,
            "hm_gui_modeling_smoke": _first_text(modeling_smoke_result) if modeling_smoke_result else None,
        },
        "with_gui": with_gui,
        "modeling_smoke": modeling_smoke,
        "port": port,
    }


def _first_text(result: Any) -> str | None:
    if result is None:
        return None
    content = getattr(result, "content", None)
    if not content:
        return None
    return getattr(content[0], "text", str(content[0]))


def _json_text_payload(result: Any) -> dict[str, Any] | None:
    text = _first_text(result)
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _dyna_field_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(payload, required_fields=("E", "MID", "PR", "RHO"))


def _dyna_control_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(
        payload,
        required_fields=("DTMIN", "ENDCYC", "ENDENG", "ENDMAS", "ENDTIM"),
    )


def _dyna_section_solid_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(payload, required_fields=("SECID",))


def _dyna_d3plot_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(
        payload,
        required_fields=("DT", "TSTART", "TTERM", "LCDT"),
    )


def _dyna_timestep_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(
        payload,
        required_fields=("DTINIT", "TSSFAC", "ISDO", "TSLIMT", "DT2MS", "LCTM", "ERODE", "MS1ST"),
    )


def _dyna_initial_detonation_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(payload, required_fields=("SETID",))


def _dyna_load_blast_status_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    return _dyna_query_guardrail_ok(payload, required_fields=("SID",))


def _dyna_unknown_suggestion_guardrail_ok(
    payload: dict[str, Any] | None,
    *,
    expected_keyword: str,
) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("known") is not False or payload.get("success") is not False:
        return False
    if payload.get("execution_ready") is not False:
        return False
    decision = payload.get("execution_decision")
    if not isinstance(decision, dict) or decision.get("state") != "blocked":
        return False
    if "no_structured_keyword_route" not in payload.get("execution_blockers", []):
        return False
    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list) or not suggestions:
        return False
    for suggestion in suggestions:
        if not isinstance(suggestion, dict):
            return False
        if suggestion.get("execution_allowed") is not False:
            return False
    return any(
        isinstance(suggestion, dict)
        and suggestion.get("keyword") == expected_keyword
        and suggestion.get("execution_ready") is False
        for suggestion in suggestions
    )


def _solid_route_runtime_status_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    route = payload.get("route")
    if not isinstance(route, dict):
        return False
    return (
        route.get("status") == "verified"
        and route.get("entity_kind") == "geometry_solid"
        and isinstance(route.get("runtime_validated"), bool)
        and route.get("verification_level") in {"runtime_validated", "source_verified_runtime_pending"}
    )


def _element_capability_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict) or payload.get("success") is not True:
        return False
    summary = payload.get("summary")
    capabilities = payload.get("capabilities")
    if not isinstance(summary, dict) or not isinstance(capabilities, dict):
        return False
    if summary.get("creation_supported") != ["discrete", "line_beam", "lumped_mass", "shell_quad", "solid_hex"]:
        return False
    if summary.get("meshing_supported") != ["solid_hex"]:
        return False
    if summary.get("material_assignment_supported") != []:
        return False
    if summary.get("k_file_generation_agent_execution_allowed") not in (None, []):
        return False
    if summary.get("k_file_generation_mcp_execution_allowed") not in (None, []):
        return False
    required = {"solid_hex", "solid_tet", "shell_quad", "shell_tria", "line_beam", "lumped_mass", "discrete"}
    if not required.issubset(capabilities):
        return False
    if capabilities["solid_hex"]["creation"].get("route_status") != "verified":
        return False
    shell_quad = capabilities.get("shell_quad")
    if not isinstance(shell_quad, dict):
        return False
    line_beam = capabilities.get("line_beam")
    if not isinstance(line_beam, dict):
        return False
    if shell_quad.get("creation", {}).get("supported") is not True:
        return False
    if shell_quad.get("creation", {}).get("route_status") != "verified":
        return False
    if line_beam.get("creation", {}).get("supported") is not True:
        return False
    if line_beam.get("creation", {}).get("route_status") != "verified":
        return False
    lumped_mass = capabilities.get("lumped_mass")
    if not isinstance(lumped_mass, dict):
        return False
    discrete = capabilities.get("discrete")
    if not isinstance(discrete, dict):
        return False
    if lumped_mass.get("creation", {}).get("supported") is not True:
        return False
    if lumped_mass.get("creation", {}).get("route_status") != "verified":
        return False
    if discrete.get("creation", {}).get("supported") is not True:
        return False
    if discrete.get("creation", {}).get("route_status") != "verified":
        return False
    for name in required - {"solid_hex", "shell_quad", "line_beam", "lumped_mass", "discrete"}:
        item = capabilities.get(name)
        if not isinstance(item, dict):
            return False
        for area in ("creation", "meshing", "material_assignment"):
            area_payload = item.get(area)
            if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
                return False
    for area in ("meshing", "material_assignment"):
        area_payload = shell_quad.get(area)
        if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
            return False
    for area in ("meshing", "material_assignment"):
        area_payload = line_beam.get(area)
        if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
            return False
    for item in (lumped_mass, discrete):
        for area in ("meshing", "material_assignment"):
            area_payload = item.get(area)
            if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
                return False
    for name in required:
        item = capabilities.get(name)
        if not isinstance(item, dict):
            return False
        k_file_generation = item.get("k_file_generation")
        if isinstance(k_file_generation, dict):
            if k_file_generation.get("agent_execution_allowed") is not False:
                return False
            if k_file_generation.get("mcp_execution_allowed") is not False:
                return False
            if k_file_generation.get("role") != "offline_fixture_validation_only":
                return False
    return capabilities["solid_hex"]["material_assignment"].get("supported") is False


def _blocked_keyword_execution_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "dyna_keyword_execution_not_verified"
        and payload.get("execution_ready") is False
        and isinstance(payload.get("execution_decision"), dict)
        and payload["execution_decision"].get("state") == "blocked"
        and isinstance(payload.get("execution_blockers"), list)
        and isinstance(payload.get("advisory_only"), dict)
        and payload["advisory_only"].get("execution_allowed") is False
    )


def _dyna_query_guardrail_ok(
    payload: dict[str, Any] | None,
    *,
    required_fields: tuple[str, ...],
) -> bool:
    if not isinstance(payload, dict):
        return False
    field_status = payload.get("field_execution_status")
    if not isinstance(field_status, dict):
        return False
    decision = payload.get("execution_decision")
    if not isinstance(decision, dict):
        return False
    if decision.get("state") != "blocked":
        return False
    if decision.get("allowed_execution_source") != "structured_verified_map":
        return False
    if decision.get("advisory_candidates_are_executable") is not False:
        return False
    advisory = payload.get("advisory_only")
    if isinstance(advisory, dict) and advisory.get("execution_allowed") is not False:
        return False
    for field in required_fields:
        item = field_status.get(field)
        if not isinstance(item, dict):
            return False
        if item.get("executable") is True:
            return False
    return payload.get("execution_ready") is False


def _gui_listener_version_status(
    gui_payload: dict[str, Any] | None,
    diagnostics_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compare connected listener version with the generated listener version."""
    current = None
    expected = None
    if isinstance(gui_payload, dict):
        current = gui_payload.get("listener_version")
    if isinstance(diagnostics_payload, dict):
        expected = diagnostics_payload.get("expected_listener_version")
        ping = diagnostics_payload.get("ping")
        if current in (None, "") and isinstance(ping, dict):
            current = ping.get("listener_version")
    return {
        "ok": bool(current and expected and str(current) == str(expected)),
        "current": current,
        "expected": expected,
    }


def _gui_diagnosis(diagnostics_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(diagnostics_payload, dict):
        return None
    diagnosis = diagnostics_payload.get("diagnosis")
    return diagnosis if isinstance(diagnosis, dict) else None


def _gui_listener_runtime(
    gui_payload: dict[str, Any] | None,
    diagnostics_payload: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Lift listener/Tcl runtime metadata to the smoke top level."""
    if not isinstance(gui_payload, dict) and not isinstance(diagnostics_payload, dict):
        return None
    ping = diagnostics_payload.get("ping") if isinstance(diagnostics_payload, dict) else None
    ping = ping if isinstance(ping, dict) else {}
    return {
        "listener_version": _first_present(gui_payload, ping, key="listener_version"),
        "expected_listener_version": (
            diagnostics_payload.get("expected_listener_version")
            if isinstance(diagnostics_payload, dict) else None
        ),
        "tcl_version": _first_present(gui_payload, ping, key="tcl_version"),
        "tcl_patchlevel": _first_present(gui_payload, ping, key="tcl_patchlevel"),
    }


def _first_present(*payloads: dict[str, Any] | None, key: str) -> Any:
    for payload in payloads:
        if isinstance(payload, dict) and payload.get(key) not in (None, ""):
            return payload.get(key)
    return None


def _modeling_visual_counts(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    counts = payload.get("visual_counts")
    if isinstance(counts, dict):
        return counts
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visual_counts"), dict):
            return refresh["visual_counts"]
    return None


def _modeling_visual_displayed_counts(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    counts = payload.get("visual_displayed_counts")
    if isinstance(counts, dict):
        return counts
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visual_displayed_counts"), dict):
            return refresh["visual_displayed_counts"]
    return None


def _modeling_visual_count_methods(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    methods = payload.get("visual_count_methods")
    if isinstance(methods, dict):
        return methods
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visual_count_methods"), dict):
            return refresh["visual_count_methods"]
    return None


def _modeling_visual_display_count_methods(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    methods = payload.get("visual_display_count_methods")
    if isinstance(methods, dict):
        return methods
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visual_display_count_methods"), dict):
            return refresh["visual_display_count_methods"]
    return None


def _modeling_visibility(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    visibility = payload.get("visibility")
    if isinstance(visibility, dict):
        return visibility
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visibility"), dict):
            return refresh["visibility"]
    return None


def _modeling_visual_steps(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    steps = payload.get("visual_steps")
    if isinstance(steps, dict):
        return steps
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visual_steps"), dict):
            return refresh["visual_steps"]
    return None


def _modeling_visual_diagnostics(payload: dict[str, Any] | None) -> list[dict[str, Any]] | None:
    if not isinstance(payload, dict):
        return None
    diagnostics = payload.get("visual_diagnostics")
    if isinstance(diagnostics, list):
        return [item for item in diagnostics if isinstance(item, dict)]
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict) and isinstance(refresh.get("visual_diagnostics"), list):
            return [item for item in refresh["visual_diagnostics"] if isinstance(item, dict)]
    return None


def _modeling_visual_refresh(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    if "visual_refresh_ok" in payload or "visual_refresh_reason" in payload:
        return {
            "ok": payload.get("visual_refresh_ok"),
            "reason": payload.get("visual_refresh_reason"),
            "failed_steps": payload.get("visual_failed_steps")
            if isinstance(payload.get("visual_failed_steps"), dict)
            else {},
            "failed_step_count": payload.get("visual_failed_step_count"),
        }
    stages = payload.get("stages")
    if isinstance(stages, dict):
        refresh = stages.get("visual_refresh")
        if isinstance(refresh, dict):
            return {
                "ok": refresh.get("visual_refresh_ok"),
                "reason": refresh.get("visual_refresh_reason"),
                "failed_steps": refresh.get("visual_failed_steps")
                if isinstance(refresh.get("visual_failed_steps"), dict)
                else {},
                "failed_step_count": refresh.get("visual_failed_step_count"),
            }
    return None


def _modeling_runtime_validation_evidence(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    evidence = payload.get("runtime_validation_evidence")
    return evidence if isinstance(evidence, dict) else None


def _modeling_visual_counts_ok(payload: dict[str, Any] | None) -> bool:
    explicit = _payload_bool(payload, "visual_counts_ok")
    if explicit is not None:
        return explicit
    counts = _modeling_visual_counts(payload)
    if not counts:
        return False
    try:
        return int(counts.get("elements") or 0) > 0 and int(counts.get("solids") or 0) > 0
    except (TypeError, ValueError):
        return False


def _modeling_visual_display_ok(payload: dict[str, Any] | None) -> bool:
    explicit = _payload_bool(payload, "visual_display_ok")
    if explicit is not None:
        return explicit
    counts = _modeling_visual_counts(payload)
    displayed = _modeling_visual_displayed_counts(payload)
    visibility = _modeling_visibility(payload)
    if not counts:
        return False
    for key in ("elements", "solids"):
        try:
            total = int(counts.get(key) or 0)
        except (TypeError, ValueError):
            return False
        if total <= 0:
            return False
        state = str((visibility or {}).get(key) or "")
        if state == "displayed":
            continue
        if state == "present_hidden":
            return False
        if displayed and displayed.get(key) is not None:
            try:
                if int(displayed.get(key) or 0) <= 0:
                    return False
                continue
            except (TypeError, ValueError):
                return False
        return False
    return True


def _payload_bool(payload: dict[str, Any] | None, key: str) -> bool | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get(key)
    return value if isinstance(value, bool) else None


def _modeling_smoke_failure(
    *,
    gui_connected: bool,
    payload: dict[str, Any] | None,
    visual_counts: dict[str, Any] | None,
    visual_counts_ok: bool | None,
    visual_displayed_counts: dict[str, Any] | None = None,
    visibility: dict[str, Any] | None = None,
    visual_display_ok: bool | None = None,
    listener_version_ok: bool = True,
    listener_version_status: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not gui_connected:
        return {
            "reason": "gui_not_connected",
            "message": "HyperMesh GUI listener is not connected, so modeling smoke was not run.",
        }
    if not listener_version_ok:
        return {
            "reason": "listener_version_mismatch",
            "message": "HyperMesh GUI listener version does not match the generated listener expected by this smoke test.",
            "listener_version": listener_version_status,
        }
    if payload is None:
        return {
            "reason": "tool_not_run",
            "message": "hm_gui_modeling_smoke did not return a JSON payload.",
        }
    if payload.get("success") is not True:
        return {
            "reason": "tool_failed",
            "stage": payload.get("stage"),
            "error": payload.get("error"),
        }
    if visual_counts is None:
        return {
            "reason": "visual_counts_missing",
            "message": "hm_gui_modeling_smoke succeeded but did not return visual_counts.",
        }
    if visual_counts_ok is not True:
        return {
            "reason": "visual_counts_insufficient",
            "visual_counts": visual_counts,
            "required": {"elements": "> 0", "solids": "> 0"},
        }
    if visual_display_ok is not True:
        return {
            "reason": "visual_display_hidden",
            "visual_counts": visual_counts,
            "visual_displayed_counts": visual_displayed_counts,
            "visibility": visibility,
            "required": {"elements": "displayed", "solids": "displayed"},
        }
    return None


def _next_hypermesh_commands(
    *,
    set_port_payload: dict[str, Any] | None,
    diagnostics_payload: dict[str, Any] | None,
    port: int | None,
    include: bool,
) -> list[str]:
    if not include:
        return []
    commands: list[str] = []
    if isinstance(diagnostics_payload, dict):
        for step in diagnostics_payload.get("recovery_steps", []) or []:
            if isinstance(step, str) and "run:" in step:
                command = step.rsplit("run:", 1)[1].strip()
                if command == "mcp_stop":
                    commands.append("catch {mcp_stop}")
    if port is not None:
        command = None
        if isinstance(set_port_payload, dict) and set_port_payload.get("hypermesh_command"):
            command = str(set_port_payload["hypermesh_command"])
        elif isinstance(diagnostics_payload, dict) and diagnostics_payload.get("start_or_source_command"):
            command = str(diagnostics_payload["start_or_source_command"])
        elif isinstance(diagnostics_payload, dict) and diagnostics_payload.get("source_command"):
            command = _wrap_source_with_port_helper(int(port), str(diagnostics_payload["source_command"]))
        if command:
            commands.append(command)
        else:
            commands.append(f"mcp_start_on_port {int(port)}")
        return _dedupe_strings(commands)
    if isinstance(set_port_payload, dict) and set_port_payload.get("hypermesh_command"):
        commands.append(str(set_port_payload["hypermesh_command"]))
    if isinstance(diagnostics_payload, dict):
        primary = diagnostics_payload.get("start_or_source_command") or diagnostics_payload.get("source_command")
        alternate = (
            diagnostics_payload.get("alternate_start_or_source_command")
            or diagnostics_payload.get("alternate_port_command")
        )
        for value in (primary, alternate):
            if value:
                commands.append(str(value))
        for step in diagnostics_payload.get("recovery_steps", []) or []:
            if isinstance(step, str) and "run:" in step:
                command = step.rsplit("run:", 1)[1].strip()
                if command != "mcp_stop":
                    commands.append(command)
    return _dedupe_strings(commands)


def _wrap_source_with_port_helper(port: int, source_command: str) -> str:
    """Prefer hmcustom.tcl's verified starter unless the command is already wrapped."""
    if "mcp_start_on_port" in source_command:
        return source_command
    return (
        f"if {{[llength [info commands mcp_start_on_port]]}} "
        f"{{mcp_start_on_port {int(port)}}} else {{{source_command}}}"
    )


def _retry_smoke_command(
    *,
    config_path: str | Path,
    server_name: str,
    with_gui: bool,
    modeling_smoke: bool,
    port: int | None,
    include: bool,
) -> str | None:
    if not include:
        return None
    command = [
        sys.executable,
        "-B",
        "-X",
        "utf8",
        "-m",
        "program.claude_smoke",
        "--config",
        str(config_path),
    ]
    if server_name != "hyper-dyna-mcp":
        command.extend(["--server-name", server_name])
    if with_gui:
        command.append("--with-gui")
    if port is not None:
        command.extend(["--port", str(int(port))])
    if modeling_smoke:
        command.append("--modeling-smoke")
    return " ".join(command)


def format_next_hypermesh_commands(result: dict[str, Any]) -> str:
    """Format the retry commands for direct use in HyperMesh Tcl Console."""
    commands = result.get("next_hypermesh_commands")
    if not isinstance(commands, list) or not commands:
        return ""
    return "\n".join(str(command).strip() for command in commands if str(command).strip())


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        clean = item.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        deduped.append(clean)
    return deduped


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Claude Code MCP stdio smoke test.")
    parser.add_argument("--config", default="claude_code_mcp.json")
    parser.add_argument("--server-name", default="hyper-dyna-mcp")
    parser.add_argument("--with-gui", action="store_true")
    parser.add_argument("--port", type=int, default=None, help="Set MCP listener port before GUI checks.")
    parser.add_argument("--modeling-smoke", action="store_true", help="After GUI connection, create FE and solid smoke entities.")
    parser.add_argument(
        "--commands-only",
        action="store_true",
        help="Print only HyperMesh Tcl Console retry commands when available.",
    )
    args = parser.parse_args()

    result = asyncio.run(
        run_smoke(
            args.config,
            args.server_name,
            with_gui=bool(args.with_gui),
            port=args.port,
            modeling_smoke=bool(args.modeling_smoke),
        )
    )
    if args.commands_only:
        commands_text = format_next_hypermesh_commands(result)
        if commands_text:
            print(commands_text)
            if not result.get("success"):
                raise SystemExit(1)
            return
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("success"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
