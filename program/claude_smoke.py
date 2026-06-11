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
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from program.tools.hm_recording_requirements import documented_unsupported_route_names
from program.plugin_loop import execute_tcl as plugin_loop_execute_tcl
from program.tools.hm_gui import activate_lsdyne_template
from program.tools.hm_gui import execute_tcl_gui
from program.tools.hm_k_integration import generate_integration_script, integrate_k_file
from program.tools.hm_launcher import launch_hm_gui
from program.tools.hm_runner import run_hmbatch
from program.tools.lsdyna_runner import run_lsdyna
from program.tools.lsprepost_runner import run_lsprepost
from program.tools.hm_safe_save import safe_batch_execute as hm_safe_batch_execute
from program.tools.hm_safe_save import safe_execute as hm_safe_execute
from program.tools.hm_template_validator import validate_template
from program.tools.hm_tcl_generator import generate_save_tcl, validate_tcl_script
from program.tools.cfile_generator import generate_cfile


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
    "hm_create_tria3",
    "hm_create_tet4",
    "hm_create_fe_cube",
    "hm_visual_refresh",
    "hm_gui_modeling_smoke",
    "hm_search_keywords",
    "hm_keyword_map",
    "hm_command_map",
    "hm_element_capability_matrix",
    "hm_modeling_action",
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
    "hm_modeling_action",
    "hm_create_fe_cube",
    "hm_gui_modeling_smoke",
    "hm_create_solid_box",
    "hm_create_surface_plate",
    "hm_create_shell_plate",
    "hm_create_beam_line",
    "hm_create_discrete_spring",
    "hm_create_lumped_mass",
    "hm_create_tria3",
    "hm_create_tet4",
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

EXPECTED_RECORDING_REQUIREMENT_ROUTES = documented_unsupported_route_names()

REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_K_SAMPLE = REPO_ROOT / "lib" / "k_samples" / "minimal_solid.k"


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


def _tool_annotation_title(tool: Any) -> str | None:
    annotations = getattr(tool, "annotations", None)
    if annotations is None:
        return None
    if isinstance(annotations, dict):
        title = annotations.get("title")
    else:
        title = getattr(annotations, "title", None)
    return title if isinstance(title, str) else None


def _tool_titles_guardrail_ok(tool_titles: dict[str, str | None]) -> bool:
    expected = {
        "execute_hm_python_api": "Plan HyperMesh Python API Script",
        "hm_convert_model": "Blocked LS-DYNA Profile Conversion",
        "hm_set_keyword": "MAP-Gated Keyword Card",
    }
    forbidden = {
        "execute_hm_python_api": {"Execute HyperMesh Python API"},
        "hm_convert_model": {"Convert Model to LS-DYNA Profile"},
        "hm_set_keyword": {"Set Keyword Card"},
    }
    for tool_name, expected_title in expected.items():
        title = tool_titles.get(tool_name)
        if title != expected_title:
            return False
        if title in forbidden.get(tool_name, set()):
            return False
    return True


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
            tool_titles = {
                tool.name: _tool_annotation_title(tool)
                for tool in tools_result.tools
            }

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
            blocked_model_conversion = await session.call_tool("hm_convert_model", {})
            dyna_query_payload = _json_text_payload(dyna_query)
            dyna_control_query_payload = _json_text_payload(dyna_control_query)
            dyna_section_solid_query_payload = _json_text_payload(dyna_section_solid_query)
            dyna_d3plot_query_payload = _json_text_payload(dyna_d3plot_query)
            dyna_timestep_query_payload = _json_text_payload(dyna_timestep_query)
            dyna_initial_detonation_query_payload = _json_text_payload(dyna_initial_detonation_query)
            dyna_load_blast_query_payload = _json_text_payload(dyna_load_blast_query)
            dyna_unknown_suggestion_query_payload = _json_text_payload(dyna_unknown_suggestion_query)
            blocked_section_set_keyword_payload = _json_text_payload(blocked_section_set_keyword)
            blocked_model_conversion_payload = _json_text_payload(blocked_model_conversion)
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
            blocked_model_conversion_ok = _blocked_model_conversion_ok(blocked_model_conversion_payload)
            blocked_execute_tcl_file_io_payload = execute_tcl_gui(
                '*writefile "smoke_file_io_should_not_execute.hm" 1',
                mode="raw",
            )
            blocked_plugin_file_io_payload = plugin_loop_execute_tcl(
                {
                    "script": '*writefile "smoke_ipc_file_io_should_not_execute.hm" 1',
                    "mode": "raw",
                    "timeout": 1,
                    "allow_file_io": True,
                }
            )
            blocked_generator_file_io_payload = validate_tcl_script(
                generate_save_tcl("smoke_generator_file_io_should_not_execute.hm")
            )
            blocked_safe_execute_payload = hm_safe_execute("smoke arbitrary Tcl", 'puts "unsafe"')
            blocked_safe_batch_execute_payload = hm_safe_batch_execute(
                [{"description": "smoke batch arbitrary Tcl", "script": 'puts "unsafe"'}]
            )
            blocked_template_validator_payload = validate_template(
                "airbag/AIRBAG_ADIABATIC_GAS_MODEL",
                execute=True,
            )
            blocked_template_activation_payload = activate_lsdyne_template(port=0, timeout=1)
            blocked_gui_launch_payload = launch_hm_gui(execute=True)
            blocked_python_api_launch = await session.call_tool(
                "execute_hm_python_api",
                {"params": {"script": "import hm\nprint('smoke')", "dry_run": False}},
            )
            blocked_python_api_launch_payload = _json_text_payload(blocked_python_api_launch)
            blocked_hmbatch_runner_payload = run_hmbatch('puts "smoke"', dry_run=False)
            lsdyna_runner_dry_run_payload = run_lsdyna(SMOKE_K_SAMPLE, dry_run=True)
            blocked_lsdyna_runner_payload = run_lsdyna("smoke_should_not_run.k", dry_run=False)
            blocked_lsprepost_runner_payload = run_lsprepost("smoke_should_not_run.cfile", dry_run=False)
            lsprepost_cfile_advisory_script = generate_cfile(
                ["open d3plot smoke.d3plot", "capture smoke.png"]
            )
            lsprepost_cfile_advisory_ok = _lsprepost_cfile_advisory_ok(
                lsprepost_cfile_advisory_script
            )
            blocked_execute_tcl_file_io_ok = _blocked_execute_tcl_file_io_ok(
                blocked_execute_tcl_file_io_payload
            )
            blocked_plugin_file_io_ok = _blocked_plugin_file_io_ok(blocked_plugin_file_io_payload)
            blocked_generator_file_io_ok = _blocked_generator_file_io_ok(
                blocked_generator_file_io_payload
            )
            blocked_safe_execute_ok = _blocked_safe_execute_ok(blocked_safe_execute_payload)
            blocked_safe_batch_execute_ok = _blocked_safe_batch_execute_ok(
                blocked_safe_batch_execute_payload
            )
            blocked_template_validator_ok = _blocked_template_validator_ok(
                blocked_template_validator_payload
            )
            blocked_template_activation_ok = _blocked_template_activation_ok(
                blocked_template_activation_payload
            )
            blocked_gui_launch_ok = _blocked_gui_launch_ok(blocked_gui_launch_payload)
            blocked_python_api_launch_ok = _blocked_python_api_launch_ok(
                blocked_python_api_launch_payload
            )
            blocked_hmbatch_runner_ok = _blocked_external_runner_ok(
                blocked_hmbatch_runner_payload,
                error_type="hmbatch_execution_out_of_scope",
                requires_empty_command=True,
            )
            blocked_lsdyna_runner_ok = _blocked_external_runner_ok(
                blocked_lsdyna_runner_payload,
                error_type="lsdyna_solver_execution_out_of_scope",
                requires_empty_command=True,
            )
            lsdyna_runner_dry_run_offline_ok = _offline_solver_metadata_ok(
                lsdyna_runner_dry_run_payload
            )
            blocked_lsprepost_runner_ok = _blocked_external_runner_ok(
                blocked_lsprepost_runner_payload,
                error_type="lsprepost_execution_out_of_scope",
                requires_empty_command=True,
            )
            try:
                blocked_k_integration_payload = asdict(
                    integrate_k_file(SMOKE_K_SAMPLE, dry_run=False)
                )
            except Exception as exc:
                blocked_k_integration_payload = {
                    "success": False,
                    "error_type": "k_file_integration_smoke_error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "execution_allowed": None,
                    "tcl_sent": None,
                }
            blocked_k_integration_ok = _blocked_k_file_integration_ok(blocked_k_integration_payload)
            try:
                k_integration_advisory_script = generate_integration_script(SMOKE_K_SAMPLE)
            except Exception as exc:
                k_integration_advisory_script = f"ERROR: {type(exc).__name__}: {exc}"
            k_integration_advisory_ok = _k_integration_advisory_script_ok(
                k_integration_advisory_script
            )
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
            tet_modeling_action = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "create_mesh",
                    "element_type": "TET4",
                    "parameters": {"element_size": 10.0},
                }},
            )
            beam_modeling_action = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "create_mesh",
                    "element_type": "beam",
                    "parameters": {"element_size": 10.0},
                }},
            )
            mixed_modeling_action = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "create_mesh",
                    "element_type": "mixed",
                    "parameters": {"element_size": 10.0},
                }},
            )
            unknown_modeling_action = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "create_mesh",
                    "element_type": "pyramid",
                    "parameters": {"element_size": 10.0},
                }},
            )
            material_modeling_action = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "assign_material",
                    "element_type": "HEX8",
                    "parameters": {"component": "SMOKE_HEX", "material": "SMOKE_STEEL"},
                }},
            )
            recording_requirements = await session.call_tool(
                "hm_modeling_action",
                {"params": {"action": "recording_requirements"}},
            )
            empty_recording_validation = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "validate_recording",
                    "element_type": "beam",
                    "parameters": {
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
                }},
            )
            dependency_blocked_validation = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "validate_recording",
                    "element_type": "TET4",
                    "parameters": {
                        "route_name": "assign_material_to_tet_part",
                        "recording_text": "*createentity mats name=SMOKE_TET\n*setvalue comps id=1 propertyid=1",
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
                }},
            )
            forbidden_recording_validation = await session.call_tool(
                "hm_modeling_action",
                {"params": {
                    "action": "validate_recording",
                    "element_type": "beam",
                    "parameters": {
                        "route_name": "line_mesh_beam",
                        "recording_text": "hm_createmark lines 1 10\nexec lsdyna i=bad.k",
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
                }},
            )
            solid_command_map_payload = _json_text_payload(solid_command_map)
            element_capability_matrix_payload = _json_text_payload(element_capability_matrix_result)
            tet_modeling_action_payload = _json_text_payload(tet_modeling_action)
            beam_modeling_action_payload = _json_text_payload(beam_modeling_action)
            mixed_modeling_action_payload = _json_text_payload(mixed_modeling_action)
            unknown_modeling_action_payload = _json_text_payload(unknown_modeling_action)
            material_modeling_action_payload = _json_text_payload(material_modeling_action)
            recording_requirements_payload = _json_text_payload(recording_requirements)
            empty_recording_validation_payload = _json_text_payload(empty_recording_validation)
            dependency_blocked_validation_payload = _json_text_payload(dependency_blocked_validation)
            forbidden_recording_validation_payload = _json_text_payload(forbidden_recording_validation)
            solid_route_runtime_status_ok = _solid_route_runtime_status_ok(solid_command_map_payload)
            tet_modeling_action_guardrail_ok = _modeling_action_tet_guardrail_ok(tet_modeling_action_payload)
            beam_modeling_action_guardrail_ok = _modeling_action_beam_guardrail_ok(beam_modeling_action_payload)
            mixed_modeling_action_guardrail_ok = _modeling_action_mixed_guardrail_ok(mixed_modeling_action_payload)
            unknown_modeling_action_guardrail_ok = _modeling_action_unknown_guardrail_ok(
                unknown_modeling_action_payload
            )
            material_modeling_action_guardrail_ok = _modeling_action_material_guardrail_ok(
                material_modeling_action_payload
            )
            recording_requirements_guardrail_ok = _recording_requirements_guardrail_ok(
                recording_requirements_payload
            )
            empty_recording_validation_guardrail_ok = _empty_recording_validation_guardrail_ok(
                empty_recording_validation_payload
            )
            dependency_blocked_validation_guardrail_ok = _dependency_blocked_validation_guardrail_ok(
                dependency_blocked_validation_payload
            )
            forbidden_recording_validation_guardrail_ok = _forbidden_recording_validation_guardrail_ok(
                forbidden_recording_validation_payload
            )
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
    if not _tool_titles_guardrail_ok(tool_titles):
        guardrail_failures.append(
            "MCP tool titles must not imply blocked execution for Python API, profile conversion, or keyword cards."
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
    if not blocked_model_conversion_ok:
        guardrail_failures.append("hm_convert_model must stay blocked until LS-DYNA profile/card routes are verified.")
    if not blocked_k_integration_ok:
        guardrail_failures.append(
            "hm_k_integration.integrate_k_file(dry_run=False) must stay blocked and must not send K-derived Tcl."
        )
    if not k_integration_advisory_ok:
        guardrail_failures.append(
            "hm_k_integration.generate_integration_script must return commented advisory text, not executable K-derived Tcl."
        )
    if not blocked_execute_tcl_file_io_ok:
        guardrail_failures.append("execute_tcl_gui must block file I/O before Tcl is sent.")
    if not blocked_plugin_file_io_ok:
        guardrail_failures.append("plugin_loop.execute_tcl must ignore allow_file_io payloads and block file I/O.")
    if not blocked_generator_file_io_ok:
        guardrail_failures.append("hm_tcl_generator.validate_tcl_script must block legacy file I/O scripts.")
    if not blocked_safe_execute_ok:
        guardrail_failures.append("hm_safe_save.safe_execute must stay blocked and must not execute arbitrary Tcl.")
    if not blocked_safe_batch_execute_ok:
        guardrail_failures.append("hm_safe_save.safe_batch_execute must stay blocked and must not execute arbitrary Tcl.")
    if not blocked_template_validator_ok:
        guardrail_failures.append("hm_template_validator execute=True must stay blocked and must not send Tcl.")
    if not blocked_template_activation_ok:
        guardrail_failures.append("activate_lsdyne_template must stay blocked and must not send *templatefileset Tcl.")
    if not blocked_gui_launch_ok:
        guardrail_failures.append("launch_hm_gui execute=True must stay blocked and must not start HyperWorks.")
    if not blocked_python_api_launch_ok:
        guardrail_failures.append(
            "execute_hm_python_api dry_run=false must stay blocked before script writing or launch command generation."
        )
    if not blocked_hmbatch_runner_ok:
        guardrail_failures.append("run_hmbatch dry_run=false must stay blocked before script writing or hmbatch command generation.")
    if not blocked_lsdyna_runner_ok:
        guardrail_failures.append("run_lsdyna dry_run=false must stay blocked before solver command generation.")
    if not lsdyna_runner_dry_run_offline_ok:
        guardrail_failures.append(
            "run_lsdyna dry_run=true must stay offline-review-only and must not imply MCP solver execution."
        )
    if not blocked_lsprepost_runner_ok:
        guardrail_failures.append("run_lsprepost dry_run=false must stay blocked before LS-PrePost command generation.")
    if not lsprepost_cfile_advisory_ok:
        guardrail_failures.append(
            "LS-PrePost cfile helpers must return commented advisory text, not executable cfile commands."
        )
    if not solid_route_runtime_status_ok:
        guardrail_failures.append("hm_command_map create_geometry_solid_box must expose experimental blocked status.")
    if not _element_capability_guardrail_ok(element_capability_matrix_payload):
        guardrail_failures.append(
            "hm_element_capability_matrix must report only verified FE creation routes, keep surface automesh/material assignment blocked, and keep K writer execution disabled."
        )
    if not tet_modeling_action_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action must block TET4 create_mesh as mesh_route_not_verified without sending Tcl."
        )
    if not beam_modeling_action_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action must block BEAM create_mesh as line_mesh_beam while offering direct create_element."
        )
    if not mixed_modeling_action_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action must block mixed create_mesh as unsupported_element_type without sending Tcl."
        )
    if not unknown_modeling_action_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action must reject unknown element types before recording or route planning."
        )
    if not material_modeling_action_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action must block material assignment with a concrete unsupported route and recording next steps."
        )
    if not recording_requirements_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action recording_requirements must expose every documented unsupported route without allowing Tcl execution."
        )
    if not empty_recording_validation_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action validate_recording must reject empty command recording text even when runtime evidence is complete."
        )
    if not dependency_blocked_validation_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action validate_recording must block promotion when prerequisite routes are still unsupported."
        )
    if not forbidden_recording_validation_guardrail_ok:
        guardrail_failures.append(
            "hm_modeling_action validate_recording must reject global forbidden Tcl commands such as exec/open/source/export."
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
    recording_requirements_coverage = _recording_requirements_coverage(
        recording_requirements_payload
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
        "tool_titles": tool_titles,
        "recording_requirements_coverage": recording_requirements_coverage,
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
            "hm_convert_model_blocked": _first_text(blocked_model_conversion),
            "hm_k_integration_blocked": blocked_k_integration_payload,
            "hm_k_integration_advisory_script_non_executable": {
                "ok": k_integration_advisory_ok,
                "preview": k_integration_advisory_script.splitlines()[:8],
            },
            "execute_tcl_gui_file_io_blocked": blocked_execute_tcl_file_io_payload,
            "plugin_loop_file_io_blocked": blocked_plugin_file_io_payload,
            "hm_tcl_generator_file_io_blocked": blocked_generator_file_io_payload,
            "hm_safe_execute_blocked": blocked_safe_execute_payload,
            "hm_safe_batch_execute_blocked": blocked_safe_batch_execute_payload,
            "hm_template_validator_execute_true_blocked": blocked_template_validator_payload,
            "activate_lsdyne_template_blocked": blocked_template_activation_payload,
            "launch_hm_gui_execute_true_blocked": blocked_gui_launch_payload,
            "execute_hm_python_api_dry_run_false_blocked": _first_text(blocked_python_api_launch),
            "hm_runner_hmbatch_dry_run_false_blocked": blocked_hmbatch_runner_payload,
            "lsdyna_runner_dry_run_true_offline_only": lsdyna_runner_dry_run_payload,
            "lsdyna_runner_dry_run_false_blocked": blocked_lsdyna_runner_payload,
            "lsprepost_runner_dry_run_false_blocked": blocked_lsprepost_runner_payload,
            "lsprepost_cfile_advisory_non_executable": {
                "ok": lsprepost_cfile_advisory_ok,
                "preview": lsprepost_cfile_advisory_script.splitlines()[:8],
            },
            "hm_command_map": _first_text(command_map),
            "hm_solid_command_map": _first_text(solid_command_map),
            "hm_element_capability_matrix": _first_text(element_capability_matrix_result),
            "hm_modeling_action_tet_create_mesh": _first_text(tet_modeling_action),
            "hm_modeling_action_beam_create_mesh": _first_text(beam_modeling_action),
            "hm_modeling_action_mixed_create_mesh": _first_text(mixed_modeling_action),
            "hm_modeling_action_unknown_create_mesh": _first_text(unknown_modeling_action),
            "hm_modeling_action_material_assignment": _first_text(material_modeling_action),
            "hm_modeling_action_recording_requirements": _first_text(recording_requirements),
            "hm_modeling_action_empty_recording_validation": _first_text(empty_recording_validation),
            "hm_modeling_action_dependency_blocked_validation": _first_text(dependency_blocked_validation),
            "hm_modeling_action_forbidden_recording_validation": _first_text(forbidden_recording_validation),
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
        route.get("status") == "experimental"
        and route.get("entity_kind") == "geometry_solid"
        and route.get("execution_stage") == "experimental"
        and route.get("mcp_execution_allowed") is False
        and route.get("agent_execution_allowed") is False
        and bool(route.get("promotion_required"))
    )


def _modeling_action_tet_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    next_supported_actions = payload.get("next_supported_actions")
    has_direct_tet_alternative = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "create_element"
            and action.get("tool") == "hm_create_tet4"
            and action.get("route_name") == "create_tet_element"
            and action.get("required_parameters") == ["node1", "node2", "node3", "node4"]
            for action in next_supported_actions
        )
    )
    has_tetmesh_recording_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "recording_requirements"
            and action.get("route_name") == "tetmesh_geometry_solid"
            for action in next_supported_actions
        )
    )
    has_tetmesh_validation_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "validate_recording"
            and action.get("route_name") == "tetmesh_geometry_solid"
            for action in next_supported_actions
        )
    )
    return (
        payload.get("success") is False
        and payload.get("action") == "create_mesh"
        and payload.get("element_type") == "solid_tet"
        and payload.get("error_type") == "mesh_route_not_verified"
        and payload.get("blocked_route_name") == "tetmesh_geometry_solid"
        and payload.get("blocked_route_status") == "unsupported"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and has_direct_tet_alternative
        and has_tetmesh_recording_step
        and has_tetmesh_validation_step
        and "command recording" in " ".join(payload.get("required_verification", [])).lower()
    )


def _modeling_action_beam_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    next_supported_actions = payload.get("next_supported_actions")
    has_direct_beam_alternative = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "create_element"
            and action.get("tool") == "hm_create_beam_line"
            and action.get("route_name") == "create_beam_line"
            and action.get("required_parameters") == ["length", "element_size"]
            and "not existing-line meshing" in str(action.get("scope", ""))
            for action in next_supported_actions
        )
    )
    has_line_mesh_recording_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "recording_requirements"
            and action.get("route_name") == "line_mesh_beam"
            for action in next_supported_actions
        )
    )
    has_line_mesh_validation_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "validate_recording"
            and action.get("route_name") == "line_mesh_beam"
            for action in next_supported_actions
        )
    )
    return (
        payload.get("success") is False
        and payload.get("action") == "create_mesh"
        and payload.get("element_type") == "line_beam"
        and payload.get("error_type") == "mesh_route_not_verified"
        and payload.get("blocked_route_name") == "line_mesh_beam"
        and payload.get("blocked_route_status") == "unsupported"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and has_direct_beam_alternative
        and has_line_mesh_recording_step
        and has_line_mesh_validation_step
    )


def _modeling_action_mixed_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    verification = " ".join(payload.get("required_verification", [])).lower()
    next_supported_actions = payload.get("next_supported_actions")
    has_capability_next_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "capability"
            and action.get("tool") == "hm_element_capability_matrix"
            for action in next_supported_actions
        )
    )
    has_recording_next_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "recording_requirements"
            and action.get("route_name") == "mixed_mesh_workflow"
            for action in next_supported_actions
        )
    )
    return (
        payload.get("success") is False
        and payload.get("action") == "create_mesh"
        and payload.get("element_type") == "mixed"
        and payload.get("error_type") == "unsupported_element_type"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and has_capability_next_step
        and has_recording_next_step
        and "hex/tet/shell/beam" in verification
    )


def _modeling_action_unknown_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    verification = " ".join(payload.get("required_verification", [])).lower()
    next_supported_actions = payload.get("next_supported_actions")
    has_capability_next_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "capability"
            and action.get("tool") == "hm_element_capability_matrix"
            for action in next_supported_actions
        )
    )
    known_types = payload.get("known_types")
    return (
        payload.get("success") is False
        and payload.get("action") == "create_mesh"
        and payload.get("element_type") == "pyramid"
        and payload.get("error_type") == "unknown_element_type"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and isinstance(known_types, list)
        and "solid_hex" in known_types
        and has_capability_next_step
        and "command recording" not in verification
    )


def _modeling_action_material_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    next_supported_actions = payload.get("next_supported_actions")
    has_recording_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "recording_requirements"
            and action.get("route_name") == "assign_material_to_hex_part"
            for action in next_supported_actions
        )
    )
    has_validation_step = (
        isinstance(next_supported_actions, list)
        and any(
            isinstance(action, dict)
            and action.get("action") == "validate_recording"
            and action.get("route_name") == "assign_material_to_hex_part"
            for action in next_supported_actions
        )
    )
    return (
        payload.get("success") is False
        and payload.get("action") == "assign_material"
        and payload.get("element_type") == "solid_hex"
        and payload.get("error_type") == "assign_material_not_verified"
        and payload.get("blocked_route_name") == "assign_material_to_hex_part"
        and payload.get("blocked_route_status") == "unsupported"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and has_recording_step
        and has_validation_step
    )


def _recording_requirements_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("success") is not True or payload.get("action") != "recording_requirements":
        return False
    routes = payload.get("routes")
    coverage = payload.get("coverage")
    promotion_queue = payload.get("promotion_queue")
    recommended_next_routes = payload.get("recommended_next_routes")
    supported_names = set(payload.get("supported_route_names", []))
    if not isinstance(routes, list) or not isinstance(coverage, dict):
        return False
    if not isinstance(promotion_queue, list) or not promotion_queue:
        return False
    if not isinstance(recommended_next_routes, list) or not recommended_next_routes:
        return False
    if coverage.get("complete") is not True:
        return False
    if coverage.get("missing_requirement_routes") not in ([], None):
        return False
    if coverage.get("orphan_requirement_routes") not in ([], None):
        return False
    if coverage.get("invalid_requirement_routes") not in ([], None):
        return False
    if coverage.get("invalid_requirement_count") not in (0, None):
        return False
    if coverage.get("valid_requirement_count") != coverage.get("requirement_route_count"):
        return False
    if coverage.get("promotion_order_complete") is not True:
        return False
    if coverage.get("missing_promotion_order_routes") not in ([], None):
        return False
    if coverage.get("orphan_promotion_order_routes") not in ([], None):
        return False
    route_names = set()
    for route in routes:
        if not isinstance(route, dict):
            return False
        name = route.get("route_name")
        route_names.add(name)
        if route.get("execution_allowed") is not False or route.get("tcl_sent") is not False:
            return False
        if route.get("mcp_execution_allowed") is not False:
            return False
        if route.get("requires_verified_map_promotion") is not True:
            return False
        if not route.get("promotion_target"):
            return False
        if not isinstance(route.get("required_evidence"), list) or not route.get("required_evidence"):
            return False
        evidence_schema = route.get("evidence_schema")
        recording_steps = route.get("recording_steps")
        promotion_checklist = route.get("promotion_checklist")
        if not isinstance(evidence_schema, dict) or set(evidence_schema) != set(route.get("required_evidence", [])):
            return False
        if not isinstance(recording_steps, list) or not recording_steps:
            return False
        if not isinstance(promotion_checklist, list) or not any(
            isinstance(item, dict)
            and item.get("target") == f"templates/hm_command_map.json routes.{name}.status"
            and item.get("required_value") == "verified"
            for item in promotion_checklist
        ):
            return False
    queue_names = [item.get("route_name") for item in promotion_queue if isinstance(item, dict)]
    if not EXPECTED_RECORDING_REQUIREMENT_ROUTES.issubset(set(queue_names)):
        return False
    if queue_names[:5] != [
        "assign_material_to_hex_part",
        "assign_material_to_shell_part",
        "assign_material_to_beam_part",
        "surface_automesh",
        "tetmesh_geometry_solid",
    ]:
        return False
    queue_by_name = {
        item.get("route_name"): item
        for item in promotion_queue
        if isinstance(item, dict)
    }
    for item in promotion_queue:
        if not isinstance(item, dict):
            return False
        if item.get("execution_allowed") is not False or item.get("tcl_sent") is not False:
            return False
        if item.get("mcp_execution_allowed") is not False:
            return False
        if item.get("requires_verified_map_promotion") is not True:
            return False
    hex_material = queue_by_name.get("assign_material_to_hex_part", {})
    hex_material_schema = hex_material.get("evidence_schema", {})
    hex_material_checklist = hex_material.get("promotion_checklist", [])
    if hex_material_schema.get("component_id", {}).get("kind") != "positive_integer_id":
        return False
    if hex_material_schema.get("property_id", {}).get("kind") != "positive_integer_id":
        return False
    if hex_material_schema.get("material_id", {}).get("kind") != "positive_integer_id":
        return False
    if not isinstance(hex_material_checklist, list) or not any(
        isinstance(item, dict)
        and item.get("target") == "templates/hm_command_map.json routes.assign_material_to_hex_part.mcp_execution_allowed"
        and item.get("required_value") is True
        for item in hex_material_checklist
    ):
        return False
    if not isinstance(hex_material.get("recording_steps"), list) or not hex_material.get("recording_steps"):
        return False
    if queue_by_name.get("assign_material_to_hex_part", {}).get("ready_for_recording") is not True:
        return False
    if queue_by_name.get("mixed_mesh_workflow", {}).get("ready_for_recording") is not False:
        return False
    if "mixed_element_workflow" not in queue_by_name.get("mixed_mesh_workflow", {}).get("blocked_by", []):
        return False
    if recommended_next_routes[:3] != [
        "assign_material_to_hex_part",
        "assign_material_to_shell_part",
        "assign_material_to_beam_part",
    ]:
        return False
    return (
        EXPECTED_RECORDING_REQUIREMENT_ROUTES.issubset(route_names)
        and EXPECTED_RECORDING_REQUIREMENT_ROUTES.issubset(supported_names)
        and payload.get("count") == len(routes)
    )


def _empty_recording_validation_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    schema = payload.get("expected_evidence_schema")
    steps = payload.get("recording_steps")
    checklist = payload.get("promotion_checklist")
    return (
        payload.get("success") is True
        and payload.get("action") == "validate_recording"
        and payload.get("route_name") == "line_mesh_beam"
        and payload.get("element_type") == "line_beam"
        and payload.get("recording_text_present") is False
        and payload.get("recording_command_present") is False
        and payload.get("recording_valid") is False
        and payload.get("runtime_evidence_valid") is True
        and payload.get("promotion_ready") is False
        and payload.get("mcp_execution_allowed") is False
        and payload.get("requires_verified_map_promotion") is True
        and isinstance(schema, dict)
        and schema.get("elements_count_before", {}).get("kind") == "integer_count"
        and isinstance(steps, list)
        and any("route_name=line_mesh_beam" in step for step in steps)
        and isinstance(checklist, list)
        and any(
            isinstance(item, dict)
            and item.get("target") == "templates/hm_command_map.json routes.line_mesh_beam.status"
            and item.get("required_value") == "verified"
            for item in checklist
        )
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
    )


def _dependency_blocked_validation_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    dependencies = payload.get("dependencies")
    schema = payload.get("expected_evidence_schema")
    steps = payload.get("recording_steps")
    checklist = payload.get("promotion_checklist")
    return (
        payload.get("success") is True
        and payload.get("action") == "validate_recording"
        and payload.get("route_name") == "assign_material_to_tet_part"
        and payload.get("element_type") == "solid_tet"
        and payload.get("recording_valid") is True
        and payload.get("runtime_evidence_valid") is True
        and payload.get("dependencies_satisfied") is False
        and payload.get("blocked_dependencies") == ["tetmesh_geometry_solid"]
        and isinstance(dependencies, list)
        and dependencies == [
            {"route_name": "tetmesh_geometry_solid", "status": "unsupported", "verified": False}
        ]
        and payload.get("promotion_ready") is False
        and payload.get("mcp_execution_allowed") is False
        and payload.get("requires_verified_map_promotion") is True
        and isinstance(schema, dict)
        and schema.get("material_id", {}).get("kind") == "positive_integer_id"
        and isinstance(steps, list)
        and any("route_name=assign_material_to_tet_part" in step for step in steps)
        and isinstance(checklist, list)
        and any(
            isinstance(item, dict)
            and item.get("target") == "templates/hm_command_map.json routes.assign_material_to_tet_part.mcp_execution_allowed"
            and item.get("required_value") is True
            for item in checklist
        )
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
    )


def _forbidden_recording_validation_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    forbidden_markers = payload.get("forbidden_markers")
    schema = payload.get("expected_evidence_schema")
    steps = payload.get("recording_steps")
    checklist = payload.get("promotion_checklist")
    return (
        payload.get("success") is True
        and payload.get("action") == "validate_recording"
        and payload.get("route_name") == "line_mesh_beam"
        and payload.get("element_type") == "line_beam"
        and payload.get("recording_text_present") is True
        and payload.get("recording_command_present") is True
        and isinstance(forbidden_markers, list)
        and "exec" in forbidden_markers
        and payload.get("recording_valid") is False
        and payload.get("runtime_evidence_valid") is True
        and payload.get("promotion_ready") is False
        and payload.get("mcp_execution_allowed") is False
        and payload.get("requires_verified_map_promotion") is True
        and isinstance(schema, dict)
        and schema.get("elements_count_before", {}).get("kind") == "integer_count"
        and isinstance(steps, list)
        and any("route_name=line_mesh_beam" in step for step in steps)
        and isinstance(checklist, list)
        and any(
            isinstance(item, dict)
            and item.get("target") == "templates/hm_command_map.json routes.line_mesh_beam.status"
            and item.get("required_value") == "verified"
            for item in checklist
        )
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
    )


def _recording_requirements_coverage(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    coverage = payload.get("coverage")
    return coverage if isinstance(coverage, dict) else None


def _element_capability_guardrail_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict) or payload.get("success") is not True:
        return False
    summary = payload.get("summary")
    capabilities = payload.get("capabilities")
    if not isinstance(summary, dict) or not isinstance(capabilities, dict):
        return False
    if summary.get("creation_supported") != [
        "discrete",
        "line_beam",
        "lumped_mass",
        "shell_quad",
        "shell_tria",
        "solid_hex",
        "solid_tet",
    ]:
        return False
    if summary.get("meshing_supported") != ["solid_hex"]:
        return False
    if summary.get("material_assignment_supported") != []:
        return False
    if summary.get("k_file_generation_agent_execution_allowed") not in (None, []):
        return False
    if summary.get("k_file_generation_mcp_execution_allowed") not in (None, []):
        return False
    if summary.get("final_k_export_supported") not in (None, []):
        return False
    if summary.get("hypermesh_gui_k_export_supported") not in (None, []):
        return False
    required = {"solid_hex", "solid_tet", "shell_quad", "shell_tria", "line_beam", "lumped_mass", "discrete", "mixed"}
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
    solid_tet = capabilities.get("solid_tet")
    if not isinstance(solid_tet, dict):
        return False
    shell_tria = capabilities.get("shell_tria")
    if not isinstance(shell_tria, dict):
        return False
    if shell_quad.get("creation", {}).get("supported") is not True:
        return False
    if shell_quad.get("creation", {}).get("route_status") != "verified":
        return False
    if line_beam.get("creation", {}).get("supported") is not True:
        return False
    if line_beam.get("creation", {}).get("route_status") != "verified":
        return False
    if solid_tet.get("creation", {}).get("supported") is not True:
        return False
    if solid_tet.get("creation", {}).get("route_status") != "verified":
        return False
    if shell_tria.get("creation", {}).get("supported") is not True:
        return False
    if shell_tria.get("creation", {}).get("route_status") != "verified":
        return False
    lumped_mass = capabilities.get("lumped_mass")
    if not isinstance(lumped_mass, dict):
        return False
    discrete = capabilities.get("discrete")
    if not isinstance(discrete, dict):
        return False
    mixed = capabilities.get("mixed")
    if not isinstance(mixed, dict):
        return False
    if lumped_mass.get("creation", {}).get("supported") is not True:
        return False
    if lumped_mass.get("creation", {}).get("route_status") != "verified":
        return False
    if discrete.get("creation", {}).get("supported") is not True:
        return False
    if discrete.get("creation", {}).get("route_status") != "verified":
        return False
    for name in required - {"solid_hex", "solid_tet", "shell_quad", "shell_tria", "line_beam", "lumped_mass", "discrete"}:
        item = capabilities.get(name)
        if not isinstance(item, dict):
            return False
        for area in ("creation", "meshing", "material_assignment"):
            area_payload = item.get(area)
            if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
                return False
    for item in (solid_tet, shell_tria):
        for area in ("meshing", "material_assignment"):
            area_payload = item.get(area)
            if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
                return False
    for area in ("meshing", "material_assignment"):
        area_payload = shell_quad.get(area)
        if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
            return False
    line_beam_meshing = line_beam.get("meshing")
    if not isinstance(line_beam_meshing, dict) or line_beam_meshing.get("supported") is not False:
        return False
    if line_beam_meshing.get("route_status") != "unsupported":
        return False
    line_beam_material = line_beam.get("material_assignment")
    if not isinstance(line_beam_material, dict) or line_beam_material.get("supported") is not False:
        return False
    for item in (lumped_mass, discrete):
        for area in ("meshing", "material_assignment"):
            area_payload = item.get(area)
            if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
                return False
    for area in ("creation", "meshing", "material_assignment"):
        area_payload = mixed.get(area)
        if not isinstance(area_payload, dict) or area_payload.get("supported") is not False:
            return False
        if area_payload.get("route_status") != "unsupported":
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
            if k_file_generation.get("final_k_export_allowed") is not False:
                return False
            if k_file_generation.get("hypermesh_gui_export_route") is not False:
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
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and isinstance(payload.get("execution_decision"), dict)
        and payload["execution_decision"].get("state") == "blocked"
        and isinstance(payload.get("execution_blockers"), list)
        and isinstance(payload.get("advisory_only"), dict)
        and payload["advisory_only"].get("execution_allowed") is False
    )


def _blocked_model_conversion_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "lsdyna_profile_conversion_not_verified"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
    )


def _blocked_k_file_integration_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "k_file_integration_execution_not_verified"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
    )


def _k_integration_advisory_script_ok(script: str | None) -> bool:
    if not isinstance(script, str) or "ADVISORY ONLY" not in script:
        return False
    for line in script.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("*") or stripped.startswith("hm_"):
            return False
    return True


def _lsprepost_cfile_advisory_ok(script: str | None) -> bool:
    if not isinstance(script, str) or "LS-PREPOST CFILE ADVISORY ONLY" not in script:
        return False
    executable_prefixes = (
        "open ",
        "capture",
        "screen ",
        "set screen",
        "plot ",
        "result ",
        "fringe ",
        "view ",
        "xyp",
    )
    for line in script.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.lower().startswith(executable_prefixes):
            return False
    return True


def _offline_solver_metadata_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("executed") is False
        and payload.get("execution_allowed") is False
        and payload.get("solver_execution_allowed") is False
        and payload.get("mcp_execution_allowed") is False
        and payload.get("offline_review_only") is True
    )


def _blocked_execute_tcl_file_io_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "file_io_route_not_allowed"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("required_tool") == "hm_auto_save"
    )


def _blocked_plugin_file_io_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "file_io_route_not_allowed"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("allow_file_io") is False
        and payload.get("required_tool") == "hm_auto_save"
    )


def _blocked_generator_file_io_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("valid") is False
        and payload.get("error_type") == "file_io_route_not_allowed"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("required_tool") == "hm_auto_save"
    )


def _blocked_safe_execute_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "safe_execute_not_verified"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("auto_save_attempted") is False
        and payload.get("required_tool") == "hm_modeling_action"
        and payload.get("save_tool") == "hm_auto_save"
    )


def _blocked_safe_batch_execute_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "safe_execute_not_verified"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("steps_completed") == 0
        and all(_blocked_safe_execute_ok(item) for item in results)
    )


def _blocked_template_validator_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("status") == "blocked"
        and payload.get("error_type") == "template_execution_not_verified"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("requested_execute") is True
        and isinstance(payload.get("first_command"), str)
        and payload.get("first_command", "").startswith("*")
    )


def _blocked_template_activation_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "lsdyna_template_activation_not_verified"
        and payload.get("execution_allowed") is False
        and payload.get("tcl_sent") is False
        and payload.get("blocked_command") == "templatefileset"
        and payload.get("blocked_route_name") == "activate_lsdyna_template"
        and payload.get("required_tool") == "hm_modeling_action"
    )


def _blocked_gui_launch_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "hypermesh_gui_launch_out_of_scope"
        and payload.get("executed") is False
        and payload.get("dry_run") is True
        and isinstance(payload.get("command"), list)
    )


def _blocked_python_api_launch_ok(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return (
        payload.get("success") is False
        and payload.get("error_type") == "hypermesh_python_api_launch_out_of_scope"
        and payload.get("dry_run") is False
        and payload.get("executed") is False
        and payload.get("script_path") is None
        and payload.get("command") == []
    )


def _blocked_external_runner_ok(
    payload: dict[str, Any] | None,
    *,
    error_type: str,
    requires_empty_command: bool = False,
) -> bool:
    if not isinstance(payload, dict):
        return False
    if (
        payload.get("success") is not False
        or payload.get("error_type") != error_type
        or payload.get("dry_run") is not False
        or payload.get("executed") is not False
    ):
        return False
    if requires_empty_command:
        command = payload.get("command")
        command_list = payload.get("command_list")
        if command not in ("", []):
            return False
        if command_list not in (None, []):
            return False
        if payload.get("command_str") not in (None, ""):
            return False
    return True


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
        return int(counts.get("elements") or 0) > 0
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
    try:
        total = int(counts.get("elements") or 0)
    except (TypeError, ValueError):
        return False
    if total <= 0:
        return False
    state = str((visibility or {}).get("elements") or "")
    if state == "displayed":
        return True
    if state == "present_hidden":
        return False
    if displayed and displayed.get("elements") is not None:
        try:
            return int(displayed.get("elements") or 0) > 0
        except (TypeError, ValueError):
            return False
    return False


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
            "required": {"elements": "> 0"},
        }
    if visual_display_ok is not True:
        return {
            "reason": "visual_display_hidden",
            "visual_counts": visual_counts,
            "visual_displayed_counts": visual_displayed_counts,
            "visibility": visibility,
            "required": {"elements": "displayed"},
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
    parser.add_argument(
        "--modeling-smoke",
        action="store_true",
        help="After GUI connection, run FE creation and visualization smoke. Geometry solid remains a separate promotion route.",
    )
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
