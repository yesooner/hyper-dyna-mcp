"""Tests for the repo-local Claude Code MCP compatibility framework."""

import re
from pathlib import Path

import pytest

from program.claude_smoke import (
    ALLOWED_TOOLS,
    EXPECTED_TOOL_COUNT,
    EXPECTED_RECORDING_REQUIREMENT_ROUTES,
    FORBIDDEN_TOOLS,
    REQUIRED_TOOLS,
    _blocked_execute_tcl_file_io_ok,
    _blocked_external_runner_ok,
    _blocked_generator_file_io_ok,
    _blocked_k_file_integration_ok,
    _blocked_keyword_execution_ok,
    _blocked_model_conversion_ok,
    _blocked_plugin_file_io_ok,
    _blocked_python_api_launch_ok,
    _blocked_gui_launch_ok,
    _blocked_safe_batch_execute_ok,
    _blocked_safe_execute_ok,
    _blocked_template_activation_ok,
    _blocked_template_validator_ok,
    _json_text_payload,
    _dyna_control_status_guardrail_ok,
    _dyna_d3plot_status_guardrail_ok,
    _dyna_field_status_guardrail_ok,
    _dyna_initial_detonation_status_guardrail_ok,
    _dyna_load_blast_status_guardrail_ok,
    _dyna_section_solid_status_guardrail_ok,
    _dyna_timestep_status_guardrail_ok,
    _dyna_unknown_suggestion_guardrail_ok,
    _dependency_blocked_validation_guardrail_ok,
    _element_capability_guardrail_ok,
    _empty_recording_validation_guardrail_ok,
    _forbidden_recording_validation_guardrail_ok,
    _modeling_action_beam_guardrail_ok,
    _modeling_action_material_guardrail_ok,
    _modeling_action_mixed_guardrail_ok,
    _modeling_action_tet_guardrail_ok,
    _modeling_action_unknown_guardrail_ok,
    _recording_requirements_coverage,
    _recording_requirements_guardrail_ok,
    _gui_diagnosis,
    _gui_listener_runtime,
    _gui_listener_version_status,
    _k_integration_advisory_script_ok,
    _lsprepost_cfile_advisory_ok,
    format_next_hypermesh_commands,
    _modeling_visual_displayed_counts,
    _modeling_visual_display_count_methods,
    _modeling_visual_display_ok,
    _modeling_smoke_failure,
    _modeling_runtime_validation_evidence,
    _modeling_visibility,
    _modeling_visual_diagnostics,
    _modeling_visual_refresh,
    _modeling_visual_counts,
    _modeling_visual_count_methods,
    _modeling_visual_counts_ok,
    _modeling_visual_steps,
    _next_hypermesh_commands,
    _offline_solver_metadata_ok,
    _retry_smoke_command,
    _solid_route_runtime_status_ok,
    _tool_titles_guardrail_ok,
    build_stdio_params,
    load_claude_mcp_server,
)


def test_claude_mcp_config_loads_repo_local_server():
    server = load_claude_mcp_server("claude_code_mcp.json", "hyper-dyna-mcp")

    assert server["command"].endswith("python.exe")
    assert server["args"] == ["-m", "program.server"]
    assert server["cwd"] == "F:\\hyper-dyna-mcp"


def test_claude_stdio_params_preserve_utf8_env():
    server = load_claude_mcp_server("claude_code_mcp.json", "hyper-dyna-mcp")
    params = build_stdio_params(server)

    assert params.command.endswith("python.exe")
    assert params.args == ["-m", "program.server"]
    assert params.env["PYTHONUTF8"] == "1"
    assert params.env["PYTHONIOENCODING"] == "utf-8"
    assert params.env["FASTMCP_LOG_LEVEL"] == "ERROR"
    assert params.env["LOGURU_LEVEL"] == "ERROR"


def test_tool_titles_guardrail_blocks_misleading_execution_titles():
    titles = {
        "execute_hm_python_api": "Plan HyperMesh Python API Script",
        "hm_convert_model": "Blocked LS-DYNA Profile Conversion",
        "hm_set_keyword": "MAP-Gated Keyword Card",
    }

    assert _tool_titles_guardrail_ok(titles) is True

    titles["execute_hm_python_api"] = "Execute HyperMesh Python API"

    assert _tool_titles_guardrail_ok(titles) is False


def test_claude_required_surface_keeps_tcl_and_python_api_tools():
    assert EXPECTED_TOOL_COUNT == 41
    assert REQUIRED_TOOLS.issubset(ALLOWED_TOOLS)
    assert FORBIDDEN_TOOLS.isdisjoint(ALLOWED_TOOLS)
    assert "check_hypermesh_connection" in REQUIRED_TOOLS
    assert "diagnose_hypermesh_listener" in REQUIRED_TOOLS
    assert "set_hypermesh_listener_port" in REQUIRED_TOOLS
    assert "hm_visual_refresh" in REQUIRED_TOOLS
    assert "hm_gui_modeling_smoke" in REQUIRED_TOOLS
    assert "hm_create_solid_box" in REQUIRED_TOOLS
    assert "hm_create_surface_plate" in REQUIRED_TOOLS
    assert "hm_create_shell_plate" in REQUIRED_TOOLS
    assert "hm_create_beam_line" in REQUIRED_TOOLS
    assert "hm_create_discrete_spring" in REQUIRED_TOOLS
    assert "hm_create_lumped_mass" in REQUIRED_TOOLS
    assert "hm_create_tria3" in REQUIRED_TOOLS
    assert "hm_create_tet4" in REQUIRED_TOOLS
    assert "hm_element_capability_matrix" in REQUIRED_TOOLS
    assert "hm_modeling_action" in REQUIRED_TOOLS
    assert "dyna_keyword_map_validate" in REQUIRED_TOOLS
    assert "dyna_keyword_query" in REQUIRED_TOOLS
    assert "hm_python_api_status" in REQUIRED_TOOLS
    assert "execute_hm_python_api" in REQUIRED_TOOLS
    assert "hm_python_api_current_model_info" in REQUIRED_TOOLS
    assert "hm_export_k" in FORBIDDEN_TOOLS


def test_server_registered_tools_match_claude_allowed_surface():
    text = Path("program/server.py").read_text(encoding="utf-8")
    registered = set(re.findall(r'@mcp\.tool\(\s*\n\s*name="([^"]+)"', text))

    assert registered == ALLOWED_TOOLS
    assert len(registered) == EXPECTED_TOOL_COUNT


def test_fe_cube_tool_description_preserves_fe_mesh_semantics():
    text = Path("program/server.py").read_text(encoding="utf-8")

    assert "Create a structured HEX8 finite-element cube, not a geometry solid." in text
    assert "Create and tetra-mesh a cube in HyperMesh" not in text


def test_agents_doc_tool_surface_matches_claude_allowed_surface():
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    for tool_name in ALLOWED_TOOLS:
        assert tool_name in text
    for tool_name in FORBIDDEN_TOOLS:
        assert tool_name in text


def test_agent_docs_track_forbidden_tool_surface():
    docs = {
        "AGENTS.md": Path("AGENTS.md").read_text(encoding="utf-8"),
        "CLAUDE.md": Path("CLAUDE.md").read_text(encoding="utf-8"),
        "CC_SMOKE_TEST.md": Path("CC_SMOKE_TEST.md").read_text(encoding="utf-8"),
    }

    for name, text in docs.items():
        for tool_name in FORBIDDEN_TOOLS:
            assert tool_name in text, f"{tool_name} missing from {name}"

    cc_smoke = docs["CC_SMOKE_TEST.md"]
    assert "expected_tool_count=41" in cc_smoke
    assert "unexpected_tools=[]" in cc_smoke
    assert "no forbidden solver/export tools" in cc_smoke


def test_start_listener_tool_returns_port_helper_recovery_commands():
    text = Path("program/server.py").read_text(encoding="utf-8")

    assert "start_or_source_command" in text
    assert "next_hypermesh_commands" in text
    assert "catch {mcp_stop}" in text
    assert "ensure_listener_tcl_for_port(params.port)" in text
    assert "_tcl_start_or_source_command(params.port, path)" in text


def test_box_tools_expose_and_pass_timeout():
    from pydantic import ValidationError
    from program.server import HmCreateBoxInput

    params = HmCreateBoxInput(
        name="solid",
        x_min=0,
        y_min=0,
        z_min=0,
        x_max=1,
        y_max=1,
        z_max=1,
        timeout=45,
    )

    assert params.timeout == 45
    with pytest.raises(ValidationError):
        HmCreateBoxInput(
            name="solid",
            x_min=0,
            y_min=0,
            z_min=0,
            x_max=1,
            y_max=1,
            z_max=1,
            timeout=181,
        )
    for bad_axis in ("x", "y", "z"):
        values = {
            "name": "solid",
            "x_min": 0,
            "y_min": 0,
            "z_min": 0,
            "x_max": 1,
            "y_max": 1,
            "z_max": 1,
        }
        values[f"{bad_axis}_max"] = values[f"{bad_axis}_min"]
        with pytest.raises(ValidationError, match=f"{bad_axis}_min must be less than {bad_axis}_max"):
            HmCreateBoxInput(**values)

    text = Path("program/server.py").read_text(encoding="utf-8")
    assert "create_box,\n        params.name, params.x_min, params.y_min, params.z_min," in text
    assert "create_solid_box,\n        params.name, params.x_min, params.y_min, params.z_min," in text
    assert text.count("params.timeout,") >= 2


def test_agent_prompts_do_not_reference_forbidden_tool_ids():
    prompt_dir = Path("program/prompts")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in prompt_dir.glob("*.md"))

    for tool_name in FORBIDDEN_TOOLS:
        assert tool_name not in combined


def test_agent_prompts_track_smoke_tool_count_and_modeling_guidance():
    prompt_dir = Path("program/prompts")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in prompt_dir.glob("*.md"))

    assert "expected_tool_count=40" not in combined
    assert f"expected_tool_count={EXPECTED_TOOL_COUNT}" in combined
    assert "next_supported_actions" in combined
    assert "hm_modeling_action" in combined
    assert "unknown_element_type" in combined
    assert "known_types" in combined
    assert "recording_requirements_coverage.complete=true" in combined
    assert "valid_requirement_count=17" in combined
    assert "invalid_requirement_count=0" in combined
    assert "recording_steps" in combined
    assert "evidence_schema" in combined
    assert "promotion_checklist" in combined
    assert "positive_integer_id" in combined
    assert "boolean_true" in combined
    assert "integer_count" in combined
    assert "non_empty_list" in combined
    assert "Use `hm_modeling_action` as the first modeling decision tool" in combined
    assert "Do not use `execute_tcl_gui` for agent-planned modeling" in combined
    assert "high-risk fallback" in combined


def test_validator_prompt_requires_unknown_element_guardrail():
    validator = Path("program/prompts/validator.md").read_text(encoding="utf-8")

    assert "unknown_element_type" in validator
    assert "known_types" in validator
    assert "command-recording instructions" in validator


def test_project_docs_describe_next_supported_actions_for_blocked_modeling():
    docs = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in ("README.md", "AGENTS.md", "CLAUDE.md")
    )

    assert "next_supported_actions" in docs
    assert "unknown_element_type" in docs
    assert "known_types" in docs
    assert "create_element" in docs
    assert "create_mesh" in docs
    assert "mixed_mesh_workflow" in docs
    assert "execute_tcl_gui" in docs
    assert "high-risk fallback" in docs
    assert "hm_modeling_action" in docs


def test_execute_tcl_gui_is_documented_as_destructive_fallback():
    server = Path("program/server.py").read_text(encoding="utf-8")

    assert 'name="execute_tcl_gui"' in server
    assert '"destructiveHint": True' in server
    assert "High-risk fallback only" in server
    assert "Use hm_modeling_action first" in server
    assert "Do not use this for agent-planned modeling" in server


def test_direct_modeling_tools_document_modeling_action_first():
    server = Path("program/server.py").read_text(encoding="utf-8")
    direct_tools = [
        "hm_create_box_tool",
        "hm_mesh_box_tool",
        "hm_create_solid_box_tool",
        "hm_create_fe_cube_tool",
        "hm_create_surface_plate_tool",
        "hm_create_shell_plate_tool",
        "hm_create_beam_line_tool",
        "hm_create_discrete_spring_tool",
        "hm_create_lumped_mass_tool",
        "hm_create_tria3_tool",
        "hm_create_tet4_tool",
    ]

    for tool in direct_tools:
        start = server.index(f"async def {tool}")
        end = server.find("\n\n@mcp.tool", start)
        block = server[start : end if end != -1 else len(server)]
        assert "hm_modeling_action" in block, tool


def test_claude_smoke_parses_gui_connection_payload():
    class Result:
        content = [type("Content", (), {"text": '{"connected": false, "success": false}'})()]

    payload = _json_text_payload(Result())

    assert payload == {"connected": False, "success": False}


def test_dyna_field_status_guardrail_requires_unverified_mat3_fields_not_executable():
    payload = {
        "execution_ready": False,
        "advisory_only": {"execution_allowed": False},
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "E": {"executable": False},
            "MID": {"executable": False},
            "PR": {"executable": False},
            "RHO": {"executable": False},
        },
    }

    assert _dyna_field_status_guardrail_ok(payload) is True


def test_dyna_field_status_guardrail_rejects_advisory_execution_allowed():
    payload = {
        "execution_ready": False,
        "advisory_only": {"execution_allowed": True},
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "E": {"executable": False},
            "MID": {"executable": False},
            "PR": {"executable": False},
            "RHO": {"executable": False},
        },
    }

    assert _dyna_field_status_guardrail_ok(payload) is False


def test_dyna_field_status_guardrail_requires_execution_decision():
    payload = {
        "execution_ready": False,
        "field_execution_status": {
            "E": {"executable": False},
            "MID": {"executable": False},
            "PR": {"executable": False},
            "RHO": {"executable": False},
        },
    }

    assert _dyna_field_status_guardrail_ok(payload) is False


def test_dyna_field_status_guardrail_rejects_executable_unverified_field():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "E": {"executable": True},
            "MID": {"executable": False},
            "PR": {"executable": False},
            "RHO": {"executable": False},
        },
    }

    assert _dyna_field_status_guardrail_ok(payload) is False


def test_dyna_control_status_guardrail_requires_control_fields_not_executable():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "DTMIN": {"executable": False},
            "ENDCYC": {"executable": False},
            "ENDENG": {"executable": False},
            "ENDMAS": {"executable": False},
            "ENDTIM": {"executable": False},
        },
    }

    assert _dyna_control_status_guardrail_ok(payload) is True


def test_dyna_control_status_guardrail_rejects_executable_control_field():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "DTMIN": {"executable": False},
            "ENDCYC": {"executable": False},
            "ENDENG": {"executable": False},
            "ENDMAS": {"executable": False},
            "ENDTIM": {"executable": True},
        },
    }

    assert _dyna_control_status_guardrail_ok(payload) is False


def test_dyna_section_solid_guardrail_requires_section_field_not_executable():
    payload = {
        "execution_ready": False,
        "advisory_only": {"execution_allowed": False},
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "SECID": {"executable": False},
        },
    }

    assert _dyna_section_solid_status_guardrail_ok(payload) is True

    payload["field_execution_status"]["SECID"]["executable"] = True

    assert _dyna_section_solid_status_guardrail_ok(payload) is False


def test_dyna_d3plot_status_guardrail_requires_output_fields_not_executable():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "DT": {"executable": False},
            "TSTART": {"executable": False},
            "TTERM": {"executable": False},
            "LCDT": {"executable": False},
        },
    }

    assert _dyna_d3plot_status_guardrail_ok(payload) is True


def test_dyna_d3plot_status_guardrail_rejects_executable_output_field():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "DT": {"executable": True},
            "TSTART": {"executable": False},
            "TTERM": {"executable": False},
            "LCDT": {"executable": False},
        },
    }

    assert _dyna_d3plot_status_guardrail_ok(payload) is False


def test_dyna_timestep_status_guardrail_requires_timestep_fields_not_executable():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "DTINIT": {"executable": False},
            "TSSFAC": {"executable": False},
            "ISDO": {"executable": False},
            "TSLIMT": {"executable": False},
            "DT2MS": {"executable": False},
            "LCTM": {"executable": False},
            "ERODE": {"executable": False},
            "MS1ST": {"executable": False},
        },
    }

    assert _dyna_timestep_status_guardrail_ok(payload) is True


def test_dyna_timestep_status_guardrail_rejects_executable_timestep_field():
    payload = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {
            "DTINIT": {"executable": False},
            "TSSFAC": {"executable": True},
            "ISDO": {"executable": False},
            "TSLIMT": {"executable": False},
            "DT2MS": {"executable": False},
            "LCTM": {"executable": False},
            "ERODE": {"executable": False},
            "MS1ST": {"executable": False},
        },
    }

    assert _dyna_timestep_status_guardrail_ok(payload) is False


def test_dyna_blast_setup_guardrails_require_fields_not_executable():
    initial = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {"SETID": {"executable": False}},
    }
    blast = {
        "execution_ready": False,
        "execution_decision": {
            "state": "blocked",
            "allowed_execution_source": "structured_verified_map",
            "advisory_candidates_are_executable": False,
        },
        "field_execution_status": {"SID": {"executable": False}},
    }

    assert _dyna_initial_detonation_status_guardrail_ok(initial) is True
    assert _dyna_load_blast_status_guardrail_ok(blast) is True

    initial["field_execution_status"]["SETID"]["executable"] = True
    blast["field_execution_status"]["SID"]["executable"] = True

    assert _dyna_initial_detonation_status_guardrail_ok(initial) is False
    assert _dyna_load_blast_status_guardrail_ok(blast) is False


def test_dyna_unknown_suggestion_guardrail_requires_non_executable_suggestions():
    payload = {
        "success": False,
        "known": False,
        "execution_ready": False,
        "execution_blockers": ["no_structured_keyword_route"],
        "execution_decision": {"state": "blocked"},
        "suggestions": [
            {
                "keyword": "*LOAD_BLAST",
                "execution_ready": False,
                "execution_allowed": False,
            }
        ],
    }

    assert _dyna_unknown_suggestion_guardrail_ok(payload, expected_keyword="*LOAD_BLAST") is True

    payload["suggestions"][0]["execution_allowed"] = True

    assert _dyna_unknown_suggestion_guardrail_ok(payload, expected_keyword="*LOAD_BLAST") is False


def test_solid_route_runtime_status_guardrail_requires_explicit_runtime_metadata():
    payload = {
        "route": {
            "status": "experimental",
            "entity_kind": "geometry_solid",
            "execution_stage": "experimental",
            "mcp_execution_allowed": False,
            "agent_execution_allowed": False,
            "promotion_required": ["command recording"],
        }
    }

    assert _solid_route_runtime_status_ok(payload) is True
    payload["route"]["mcp_execution_allowed"] = True
    assert _solid_route_runtime_status_ok(payload) is False
    assert _solid_route_runtime_status_ok({"route": {"status": "verified"}}) is False


def test_element_capability_guardrail_allows_only_verified_gui_creation():
    payload = {
        "success": True,
        "summary": {
            "creation_supported": [
                "discrete",
                "line_beam",
                "lumped_mass",
                "shell_quad",
                "shell_tria",
                "solid_hex",
                "solid_tet",
            ],
            "meshing_supported": ["solid_hex"],
            "material_assignment_supported": [],
            "k_file_generation_agent_execution_allowed": [],
            "k_file_generation_mcp_execution_allowed": [],
            "final_k_export_supported": [],
            "hypermesh_gui_k_export_supported": [],
        },
        "capabilities": {
            "solid_hex": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": True, "route_status": "verified"},
                "material_assignment": {"supported": False, "route_status": "unsupported"},
                "k_file_generation": {
                    "supported": True,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "solid_tet": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": False},
                "material_assignment": {"supported": False},
                "k_file_generation": {
                    "supported": False,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "shell_quad": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": False},
                "material_assignment": {"supported": False},
                "k_file_generation": {
                    "supported": True,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "shell_tria": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": False},
                "material_assignment": {"supported": False},
                "k_file_generation": {
                    "supported": False,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "line_beam": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": False, "route_status": "unsupported"},
                "material_assignment": {"supported": False},
                "k_file_generation": {
                    "supported": True,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "lumped_mass": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": False},
                "material_assignment": {"supported": False},
                "k_file_generation": {
                    "supported": False,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "discrete": {
                "creation": {"supported": True, "route_status": "verified"},
                "meshing": {"supported": False},
                "material_assignment": {"supported": False},
                "k_file_generation": {
                    "supported": False,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
            "mixed": {
                "creation": {"supported": False, "route_status": "unsupported"},
                "meshing": {"supported": False, "route_status": "unsupported"},
                "material_assignment": {"supported": False, "route_status": "unsupported"},
                "k_file_generation": {
                    "supported": False,
                    "role": "offline_fixture_validation_only",
                    "agent_execution_allowed": False,
                    "mcp_execution_allowed": False,
                    "final_k_export_allowed": False,
                    "hypermesh_gui_export_route": False,
                },
            },
        },
    }

    assert _element_capability_guardrail_ok(payload) is True

    payload["capabilities"]["solid_tet"]["meshing"]["supported"] = True

    assert _element_capability_guardrail_ok(payload) is False

    payload["capabilities"]["solid_tet"]["meshing"]["supported"] = False
    payload["capabilities"]["shell_quad"]["k_file_generation"]["agent_execution_allowed"] = True

    assert _element_capability_guardrail_ok(payload) is False

    payload["capabilities"]["shell_quad"]["k_file_generation"]["agent_execution_allowed"] = False
    payload["capabilities"]["shell_quad"]["k_file_generation"]["final_k_export_allowed"] = True

    assert _element_capability_guardrail_ok(payload) is False


def test_modeling_action_guardrails_block_tetmesh_and_mixed_mesh():
    tet_payload = {
        "success": False,
        "action": "create_mesh",
        "element_type": "solid_tet",
        "error_type": "mesh_route_not_verified",
        "blocked_route_name": "tetmesh_geometry_solid",
        "blocked_route_status": "unsupported",
        "execution_allowed": False,
        "tcl_sent": False,
        "required_verification": ["Record the meshing workflow in HyperMesh command recording."],
        "next_supported_actions": [
            {
                "action": "create_element",
                "tool": "hm_create_tet4",
                "route_name": "create_tet_element",
                "required_parameters": ["node1", "node2", "node3", "node4"],
            },
            {"action": "recording_requirements", "route_name": "tetmesh_geometry_solid"},
            {"action": "validate_recording", "route_name": "tetmesh_geometry_solid"},
        ],
    }
    mixed_payload = {
        "success": False,
        "action": "create_mesh",
        "element_type": "mixed",
        "error_type": "unsupported_element_type",
        "execution_allowed": False,
        "tcl_sent": False,
        "required_verification": ["Verify transition rules between HEX/TET/SHELL/BEAM regions."],
        "next_supported_actions": [
            {"action": "capability", "tool": "hm_element_capability_matrix"},
            {"action": "recording_requirements", "route_name": "mixed_mesh_workflow"},
        ],
    }

    assert _modeling_action_tet_guardrail_ok(tet_payload) is True
    assert _modeling_action_mixed_guardrail_ok(mixed_payload) is True

    tet_payload["tcl_sent"] = True
    mixed_payload["execution_allowed"] = True

    assert _modeling_action_tet_guardrail_ok(tet_payload) is False
    assert _modeling_action_mixed_guardrail_ok(mixed_payload) is False

    tet_payload["tcl_sent"] = False
    mixed_payload["execution_allowed"] = False
    tet_payload["next_supported_actions"] = []
    mixed_payload["next_supported_actions"] = []

    assert _modeling_action_tet_guardrail_ok(tet_payload) is False
    assert _modeling_action_mixed_guardrail_ok(mixed_payload) is False


def test_modeling_action_guardrail_blocks_beam_existing_line_mesh():
    payload = {
        "success": False,
        "action": "create_mesh",
        "element_type": "line_beam",
        "error_type": "mesh_route_not_verified",
        "blocked_route_name": "line_mesh_beam",
        "blocked_route_status": "unsupported",
        "execution_allowed": False,
        "tcl_sent": False,
        "next_supported_actions": [
            {
                "action": "create_element",
                "tool": "hm_create_beam_line",
                "route_name": "create_beam_line",
                "scope": "direct generated straight BAR2/BEAM line, not existing-line meshing",
                "required_parameters": ["length", "element_size"],
            },
            {"action": "recording_requirements", "route_name": "line_mesh_beam"},
            {"action": "validate_recording", "route_name": "line_mesh_beam"},
        ],
    }

    assert _modeling_action_beam_guardrail_ok(payload) is True

    payload["blocked_route_name"] = "create_beam_line"

    assert _modeling_action_beam_guardrail_ok(payload) is False


def test_modeling_action_guardrail_rejects_unknown_element_without_recording():
    payload = {
        "success": False,
        "action": "create_mesh",
        "element_type": "pyramid",
        "error_type": "unknown_element_type",
        "execution_allowed": False,
        "tcl_sent": False,
        "known_types": ["discrete", "line_beam", "solid_hex"],
        "required_verification": [
            "Use hm_element_capability_matrix without element_type to list supported canonical element types and aliases.",
            "Do not record or execute Tcl for unknown element families until the capability matrix is extended.",
        ],
        "next_supported_actions": [
            {"action": "capability", "tool": "hm_element_capability_matrix"},
        ],
    }

    assert _modeling_action_unknown_guardrail_ok(payload) is True

    payload["error_type"] = "mesh_route_not_verified"
    assert _modeling_action_unknown_guardrail_ok(payload) is False

    payload["error_type"] = "unknown_element_type"
    payload["required_verification"] = ["Record the meshing workflow in HyperMesh command recording."]
    assert _modeling_action_unknown_guardrail_ok(payload) is False


def test_modeling_action_guardrail_blocks_material_with_recording_route():
    payload = {
        "success": False,
        "action": "assign_material",
        "element_type": "solid_hex",
        "error_type": "assign_material_not_verified",
        "blocked_route_name": "assign_material_to_hex_part",
        "blocked_route_status": "unsupported",
        "execution_allowed": False,
        "tcl_sent": False,
        "next_supported_actions": [
            {"action": "recording_requirements", "route_name": "assign_material_to_hex_part"},
            {"action": "validate_recording", "route_name": "assign_material_to_hex_part"},
        ],
    }

    assert _modeling_action_material_guardrail_ok(payload) is True

    payload["execution_allowed"] = True
    assert _modeling_action_material_guardrail_ok(payload) is False

    payload["execution_allowed"] = False
    payload["blocked_route_name"] = "assign_material_to_shell_part"
    assert _modeling_action_material_guardrail_ok(payload) is False


def _recording_queue_fixture():
    first_routes = [
        "assign_material_to_hex_part",
        "assign_material_to_shell_part",
        "assign_material_to_beam_part",
        "surface_automesh",
        "tetmesh_geometry_solid",
    ]
    remaining = sorted(EXPECTED_RECORDING_REQUIREMENT_ROUTES - set(first_routes))
    return [
        {
            "route_name": route_name,
            "ready_for_recording": route_name != "mixed_mesh_workflow",
            "blocked_by": ["mixed_element_workflow"] if route_name == "mixed_mesh_workflow" else [],
            "execution_allowed": False,
            "mcp_execution_allowed": False,
            "requires_verified_map_promotion": True,
            "tcl_sent": False,
            "evidence_schema": (
                {
                    "component_id": {"kind": "positive_integer_id", "required": "true"},
                    "property_id": {"kind": "positive_integer_id", "required": "true"},
                    "material_id": {"kind": "positive_integer_id", "required": "true"},
                }
                if route_name == "assign_material_to_hex_part"
                else {"datanames_verified": {"kind": "boolean_true", "required": "true"}}
            ),
            "recording_steps": [
                "Start HyperMesh command recording before the manual GUI operation.",
                f"Call hm_modeling_action validate_recording with route_name={route_name}, recording_text, and runtime_evidence.",
            ],
            "promotion_checklist": [
                {
                    "target": f"templates/hm_command_map.json routes.{route_name}.status",
                    "required_value": "verified",
                },
                {
                    "target": f"templates/hm_command_map.json routes.{route_name}.mcp_execution_allowed",
                    "required_value": True,
                },
            ],
        }
        for route_name in [*first_routes, *remaining]
    ]


def _validation_diagnostics_fixture(route_name: str, schema: dict):
    return {
        "expected_evidence_schema": schema,
        "recording_steps": [
            "Start HyperMesh command recording before the manual GUI operation.",
            f"Call hm_modeling_action validate_recording with route_name={route_name}, recording_text, and runtime_evidence.",
        ],
        "promotion_checklist": [
            {
                "target": f"templates/hm_command_map.json routes.{route_name}.status",
                "required_value": "verified",
            },
            {
                "target": f"templates/hm_command_map.json routes.{route_name}.mcp_execution_allowed",
                "required_value": True,
            },
        ],
    }


def test_recording_requirements_guardrail_requires_all_routes_blocked():
    routes = [
        {
            "route_name": route_name,
            "required_markers": ["*setvalue"],
            "forbidden_markers": ["*writefile"],
            "required_evidence": ["datanames_verified"],
            "evidence_schema": {"datanames_verified": {"kind": "boolean_true", "required": "true"}},
            "recording_steps": [
                "Start HyperMesh command recording before the manual GUI operation.",
                f"Call hm_modeling_action validate_recording with route_name={route_name}, recording_text, and runtime_evidence.",
            ],
            "promotion_checklist": [
                {
                    "target": f"templates/hm_command_map.json routes.{route_name}.status",
                    "required_value": "verified",
                },
            ],
            "promotion_target": f"templates/hm_command_map.json unsupported_routes.{route_name} -> routes.{route_name}",
            "execution_allowed": False,
            "mcp_execution_allowed": False,
            "requires_verified_map_promotion": True,
            "tcl_sent": False,
        }
        for route_name in sorted(EXPECTED_RECORDING_REQUIREMENT_ROUTES)
    ]
    payload = {
        "success": True,
        "action": "recording_requirements",
        "count": len(routes),
        "routes": routes,
        "supported_route_names": sorted(EXPECTED_RECORDING_REQUIREMENT_ROUTES),
        "promotion_queue": _recording_queue_fixture(),
        "recommended_next_routes": [
            "assign_material_to_hex_part",
            "assign_material_to_shell_part",
            "assign_material_to_beam_part",
            "surface_automesh",
            "tetmesh_geometry_solid",
        ],
        "coverage": {
            "complete": True,
            "valid_requirement_count": len(routes),
            "invalid_requirement_count": 0,
            "requirement_route_count": len(routes),
            "missing_requirement_routes": [],
            "orphan_requirement_routes": [],
            "invalid_requirement_routes": [],
            "promotion_order_complete": True,
            "missing_promotion_order_routes": [],
            "orphan_promotion_order_routes": [],
        },
    }

    assert _recording_requirements_guardrail_ok(payload) is True

    payload["routes"][0]["execution_allowed"] = True
    assert _recording_requirements_guardrail_ok(payload) is False

    payload["routes"][0]["execution_allowed"] = False
    payload["routes"] = payload["routes"][1:]
    payload["count"] = len(payload["routes"])
    assert _recording_requirements_guardrail_ok(payload) is False

    payload["routes"] = routes
    payload["count"] = len(routes)
    payload["coverage"]["missing_requirement_routes"] = ["new_unsupported_route"]
    payload["coverage"]["complete"] = False
    assert _recording_requirements_guardrail_ok(payload) is False

    payload["coverage"]["missing_requirement_routes"] = []
    payload["coverage"]["invalid_requirement_routes"] = [
        {"route_name": "bad_route", "reasons": ["required_evidence_missing"]}
    ]
    payload["coverage"]["invalid_requirement_count"] = 1
    payload["coverage"]["valid_requirement_count"] = len(routes) - 1
    assert _recording_requirements_guardrail_ok(payload) is False

    payload["coverage"]["invalid_requirement_routes"] = []
    payload["coverage"]["invalid_requirement_count"] = 0
    payload["coverage"]["valid_requirement_count"] = len(routes)
    payload["coverage"]["complete"] = True
    payload["promotion_queue"] = _recording_queue_fixture()
    payload["promotion_queue"][0]["route_name"] = "tetmesh_geometry_solid"
    assert _recording_requirements_guardrail_ok(payload) is False


def test_empty_recording_validation_guardrail_rejects_missing_recording_text():
    payload = {
        "success": True,
        "action": "validate_recording",
        "route_name": "line_mesh_beam",
        "element_type": "line_beam",
        **_validation_diagnostics_fixture(
            "line_mesh_beam",
            {"elements_count_before": {"kind": "integer_count", "required": "true"}},
        ),
        "recording_text_present": False,
        "recording_command_present": False,
        "recording_valid": False,
        "runtime_evidence_valid": True,
        "promotion_ready": False,
        "execution_allowed": False,
        "mcp_execution_allowed": False,
        "requires_verified_map_promotion": True,
        "tcl_sent": False,
    }

    assert _empty_recording_validation_guardrail_ok(payload) is True

    payload["recording_text_present"] = True
    payload["recording_valid"] = True
    payload["promotion_ready"] = True
    assert _empty_recording_validation_guardrail_ok(payload) is False


def test_dependency_blocked_validation_guardrail_requires_dependency_status():
    payload = {
        "success": True,
        "action": "validate_recording",
        "route_name": "assign_material_to_tet_part",
        "element_type": "solid_tet",
        **_validation_diagnostics_fixture(
            "assign_material_to_tet_part",
            {"material_id": {"kind": "positive_integer_id", "required": "true"}},
        ),
        "recording_valid": True,
        "runtime_evidence_valid": True,
        "dependencies_satisfied": False,
        "blocked_dependencies": ["tetmesh_geometry_solid"],
        "dependencies": [
            {"route_name": "tetmesh_geometry_solid", "status": "unsupported", "verified": False}
        ],
        "promotion_ready": False,
        "execution_allowed": False,
        "mcp_execution_allowed": False,
        "requires_verified_map_promotion": True,
        "tcl_sent": False,
    }

    assert _dependency_blocked_validation_guardrail_ok(payload) is True

    payload["dependencies_satisfied"] = True
    payload["promotion_ready"] = True
    assert _dependency_blocked_validation_guardrail_ok(payload) is False


def test_forbidden_recording_validation_guardrail_rejects_exec():
    payload = {
        "success": True,
        "action": "validate_recording",
        "route_name": "line_mesh_beam",
        "element_type": "line_beam",
        **_validation_diagnostics_fixture(
            "line_mesh_beam",
            {"elements_count_before": {"kind": "integer_count", "required": "true"}},
        ),
        "recording_text_present": True,
        "recording_command_present": True,
        "forbidden_markers": ["exec"],
        "recording_valid": False,
        "runtime_evidence_valid": True,
        "promotion_ready": False,
        "execution_allowed": False,
        "mcp_execution_allowed": False,
        "requires_verified_map_promotion": True,
        "tcl_sent": False,
    }

    assert _forbidden_recording_validation_guardrail_ok(payload) is True

    payload["forbidden_markers"] = []
    payload["recording_valid"] = True
    payload["promotion_ready"] = True
    assert _forbidden_recording_validation_guardrail_ok(payload) is False


def test_recording_requirements_coverage_extracts_structured_summary():
    coverage = {
        "unsupported_route_count": 17,
        "requirement_route_count": 17,
        "valid_requirement_count": 17,
        "invalid_requirement_count": 0,
        "missing_requirement_routes": [],
        "orphan_requirement_routes": [],
        "invalid_requirement_routes": [],
        "complete": True,
    }

    assert _recording_requirements_coverage({"coverage": coverage}) == coverage
    assert _recording_requirements_coverage({"coverage": "not-json"}) is None
    assert _recording_requirements_coverage(None) is None


def test_blocked_keyword_execution_guardrail_requires_map_block_response():
    payload = {
        "success": False,
        "error_type": "dyna_keyword_execution_not_verified",
        "execution_ready": False,
        "execution_allowed": False,
        "tcl_sent": False,
        "execution_decision": {"state": "blocked"},
        "execution_blockers": ["datanames_not_verified"],
        "advisory_only": {"execution_allowed": False},
    }

    assert _blocked_keyword_execution_ok(payload) is True

    payload["success"] = True

    assert _blocked_keyword_execution_ok(payload) is False


def test_blocked_model_conversion_guardrail_requires_no_tcl_execution():
    payload = {
        "success": False,
        "error_type": "lsdyna_profile_conversion_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
    }

    assert _blocked_model_conversion_ok(payload) is True

    payload["tcl_sent"] = True

    assert _blocked_model_conversion_ok(payload) is False


def test_blocked_k_file_integration_guardrail_requires_no_tcl_execution():
    payload = {
        "success": False,
        "error_type": "k_file_integration_execution_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
    }

    assert _blocked_k_file_integration_ok(payload) is True

    payload["tcl_sent"] = True

    assert _blocked_k_file_integration_ok(payload) is False


def test_blocked_execute_tcl_file_io_guardrail_requires_no_tcl_execution():
    payload = {
        "success": False,
        "error_type": "file_io_route_not_allowed",
        "execution_allowed": False,
        "tcl_sent": False,
        "required_tool": "hm_auto_save",
    }

    assert _blocked_execute_tcl_file_io_ok(payload) is True

    payload["tcl_sent"] = True

    assert _blocked_execute_tcl_file_io_ok(payload) is False


def test_blocked_plugin_file_io_guardrail_requires_no_payload_escape_hatch():
    payload = {
        "success": False,
        "error_type": "file_io_route_not_allowed",
        "execution_allowed": False,
        "tcl_sent": False,
        "allow_file_io": False,
        "required_tool": "hm_auto_save",
    }

    assert _blocked_plugin_file_io_ok(payload) is True

    payload["allow_file_io"] = True

    assert _blocked_plugin_file_io_ok(payload) is False


def test_blocked_generator_file_io_guardrail_requires_invalid_plan():
    payload = {
        "valid": False,
        "error_type": "file_io_route_not_allowed",
        "execution_allowed": False,
        "tcl_sent": False,
        "required_tool": "hm_auto_save",
    }

    assert _blocked_generator_file_io_ok(payload) is True

    payload["valid"] = True

    assert _blocked_generator_file_io_ok(payload) is False


def test_blocked_safe_execute_guardrail_requires_no_arbitrary_tcl_execution():
    payload = {
        "success": False,
        "error_type": "safe_execute_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
        "auto_save_attempted": False,
        "required_tool": "hm_modeling_action",
        "save_tool": "hm_auto_save",
    }

    assert _blocked_safe_execute_ok(payload) is True

    payload["auto_save_attempted"] = True

    assert _blocked_safe_execute_ok(payload) is False


def test_blocked_safe_batch_execute_guardrail_requires_all_steps_blocked():
    step = {
        "success": False,
        "error_type": "safe_execute_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
        "auto_save_attempted": False,
        "required_tool": "hm_modeling_action",
        "save_tool": "hm_auto_save",
    }
    payload = {
        "success": False,
        "error_type": "safe_execute_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
        "steps_completed": 0,
        "results": [step],
    }

    assert _blocked_safe_batch_execute_ok(payload) is True

    payload["steps_completed"] = 1

    assert _blocked_safe_batch_execute_ok(payload) is False


def test_blocked_template_validator_guardrail_requires_execute_true_to_stay_blocked():
    payload = {
        "status": "blocked",
        "error_type": "template_execution_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
        "requested_execute": True,
        "first_command": "*createentity cards name=TEST",
    }

    assert _blocked_template_validator_ok(payload) is True

    payload["tcl_sent"] = True

    assert _blocked_template_validator_ok(payload) is False


def test_blocked_template_activation_guardrail_requires_no_templatefileset_tcl():
    payload = {
        "success": False,
        "error_type": "lsdyna_template_activation_not_verified",
        "execution_allowed": False,
        "tcl_sent": False,
        "blocked_command": "templatefileset",
        "blocked_route_name": "activate_lsdyna_template",
        "required_tool": "hm_modeling_action",
    }

    assert _blocked_template_activation_ok(payload) is True

    payload["tcl_sent"] = True

    assert _blocked_template_activation_ok(payload) is False


def test_k_integration_advisory_guardrail_requires_commented_tcl():
    script = "\n".join(
        [
            "# HYPERMESH MCP K-INTEGRATION ADVISORY ONLY",
            "# *createnode 0 0 0 0 0 0",
            "# hm_setvalue mats id=1 RHO=7.85e-9",
        ]
    )

    assert _k_integration_advisory_script_ok(script) is True
    assert _k_integration_advisory_script_ok(script + "\n*createnode 1 0 0 0 0 0") is False
    assert _k_integration_advisory_script_ok(script + "\nhm_setvalue mats id=1 E=210000") is False
    assert _k_integration_advisory_script_ok("# missing header\n# *createnode 0 0 0 0 0 0") is False


def test_lsprepost_cfile_advisory_guardrail_requires_commented_commands():
    script = "\n".join(
        [
            "# LS-PREPOST CFILE ADVISORY ONLY",
            "# open d3plot smoke.d3plot",
            "# capture smoke.png",
        ]
    )

    assert _lsprepost_cfile_advisory_ok(script) is True
    assert _lsprepost_cfile_advisory_ok(script + "\nopen d3plot bad.d3plot") is False
    assert _lsprepost_cfile_advisory_ok(script + "\ncapture bad.png") is False
    assert _lsprepost_cfile_advisory_ok("# missing header\n# open d3plot smoke.d3plot") is False


def test_offline_solver_metadata_guardrail_requires_non_executable_flags():
    payload = {
        "executed": False,
        "execution_allowed": False,
        "solver_execution_allowed": False,
        "mcp_execution_allowed": False,
        "offline_review_only": True,
    }

    assert _offline_solver_metadata_ok(payload) is True

    payload["execution_allowed"] = True

    assert _offline_solver_metadata_ok(payload) is False


def test_blocked_python_api_launch_guardrail_requires_no_script_or_command():
    payload = {
        "success": False,
        "error_type": "hypermesh_python_api_launch_out_of_scope",
        "dry_run": False,
        "executed": False,
        "script_path": None,
        "command": [],
    }

    assert _blocked_python_api_launch_ok(payload) is True

    payload["script_path"] = "runs/hm_python_api_should_not_exist.py"

    assert _blocked_python_api_launch_ok(payload) is False


def test_blocked_external_runner_guardrail_requires_empty_command():
    payload = {
        "success": False,
        "error_type": "hmbatch_execution_out_of_scope",
        "dry_run": False,
        "executed": False,
        "command": [],
        "command_str": "",
    }

    assert _blocked_external_runner_ok(
        payload,
        error_type="hmbatch_execution_out_of_scope",
        requires_empty_command=True,
    ) is True

    payload["command"] = ["hmbatch.exe", "-tcl", "bad.tcl"]

    assert _blocked_external_runner_ok(
        payload,
        error_type="hmbatch_execution_out_of_scope",
        requires_empty_command=True,
    ) is False


def test_blocked_gui_launch_guardrail_requires_no_hyperworks_start():
    payload = {
        "success": False,
        "error_type": "hypermesh_gui_launch_out_of_scope",
        "executed": False,
        "dry_run": True,
        "command": ["C:/Altair/hw/bin/win64/hw.exe"],
    }

    assert _blocked_gui_launch_ok(payload) is True

    payload["executed"] = True

    assert _blocked_gui_launch_ok(payload) is False


def test_gui_listener_version_status_requires_expected_version_match():
    assert _gui_listener_version_status(
        {"connected": True, "listener_version": "2024-compat-v3"},
        {"expected_listener_version": "2024-compat-v3"},
    ) == {"ok": True, "current": "2024-compat-v3", "expected": "2024-compat-v3"}

    assert _gui_listener_version_status(
        {"connected": True, "listener_version": "2024-compat-v2"},
        {"expected_listener_version": "2024-compat-v3"},
    ) == {"ok": False, "current": "2024-compat-v2", "expected": "2024-compat-v3"}


def test_gui_listener_runtime_lifts_tcl_metadata():
    runtime = _gui_listener_runtime(
        {
            "connected": True,
            "listener_version": "2024-compat-v3",
            "tcl_version": "8.6",
            "tcl_patchlevel": "8.6.13",
        },
        {"expected_listener_version": "2024-compat-v3"},
    )

    assert runtime == {
        "listener_version": "2024-compat-v3",
        "expected_listener_version": "2024-compat-v3",
        "tcl_version": "8.6",
        "tcl_patchlevel": "8.6.13",
    }


def test_gui_listener_runtime_falls_back_to_diagnostics_ping():
    runtime = _gui_listener_runtime(
        {"connected": False},
        {
            "expected_listener_version": "2024-compat-v3",
            "ping": {
                "listener_version": "2024-compat-v3",
                "tcl_version": "8.5",
                "tcl_patchlevel": "8.5.19",
            },
        },
    )

    assert runtime["listener_version"] == "2024-compat-v3"
    assert runtime["expected_listener_version"] == "2024-compat-v3"
    assert runtime["tcl_version"] == "8.5"
    assert runtime["tcl_patchlevel"] == "8.5.19"


def test_gui_diagnosis_lifts_nested_diagnostics_payload():
    payload = {
        "diagnosis": {
            "reason": "listener_not_running",
            "action": "Source the generated listener Tcl in the HyperMesh Tcl Console.",
        }
    }

    assert _gui_diagnosis(payload) == payload["diagnosis"]
    assert _gui_diagnosis({"diagnosis": "bad"}) is None
    assert _gui_diagnosis(None) is None


def test_modeling_visual_counts_accepts_top_level_counts():
    payload = {"success": True, "visual_counts": {"elements": 1, "nodes": 8, "solids": 1}}

    assert _modeling_visual_counts(payload) == {"elements": 1, "nodes": 8, "solids": 1}
    assert _modeling_visual_counts_ok(payload) is True
    assert _modeling_visual_display_ok(payload) is False


def test_modeling_visual_gates_prefer_tool_reported_booleans():
    payload = {
        "success": True,
        "visual_counts_ok": False,
        "visual_display_ok": False,
        "visual_counts": {"elements": 1, "nodes": 8, "solids": 1},
        "visual_displayed_counts": {"elements": 1, "nodes": 8, "solids": 1},
        "visibility": {"elements": "displayed", "solids": "displayed"},
    }

    assert _modeling_visual_counts_ok(payload) is False
    assert _modeling_visual_display_ok(payload) is False


def test_modeling_visual_counts_accepts_nested_refresh_counts_with_hidden_solid():
    payload = {
        "success": True,
        "stages": {
            "visual_refresh": {
                "visual_counts": {"elements": 2, "nodes": 12, "solids": 1, "surfaces": 6},
                "visual_displayed_counts": {"elements": 2, "nodes": 12, "solids": 0, "surfaces": 0},
                "visual_count_methods": {"elements": "entitylist", "solids": "marklength"},
                "visual_display_count_methods": {
                    "elements": "marklength_displayed",
                    "solids": "marklength_displayed",
                },
                "visibility": {"elements": "displayed", "solids": "present_hidden"},
                "visual_steps": {"hm_redraw": {"status": "ok", "error": None}},
            }
        },
    }

    assert _modeling_visual_counts(payload)["surfaces"] == 6
    assert _modeling_visual_displayed_counts(payload)["solids"] == 0
    assert _modeling_visual_count_methods(payload)["solids"] == "marklength"
    assert _modeling_visual_display_count_methods(payload)["solids"] == "marklength_displayed"
    assert _modeling_visibility(payload)["solids"] == "present_hidden"
    assert _modeling_visual_steps(payload)["hm_redraw"] == {"status": "ok", "error": None}
    assert _modeling_visual_counts_ok(payload) is True
    assert _modeling_visual_display_ok(payload) is True


def test_modeling_visual_steps_accepts_top_level_steps():
    payload = {
        "success": True,
        "visual_steps": {"hm_viewfit": {"status": "error", "error": "bad command"}},
        "visual_refresh_ok": False,
        "visual_refresh_reason": "visual_step_errors",
        "visual_failed_steps": {"hm_viewfit": {"status": "error", "error": "bad command"}},
        "visual_failed_step_count": 1,
    }

    assert _modeling_visual_steps(payload) == {
        "hm_viewfit": {"status": "error", "error": "bad command"}
    }
    assert _modeling_visual_refresh(payload) == {
        "ok": False,
        "reason": "visual_step_errors",
        "failed_steps": {"hm_viewfit": {"status": "error", "error": "bad command"}},
        "failed_step_count": 1,
    }


def test_modeling_visual_count_methods_accept_top_level_methods():
    payload = {
        "success": True,
        "visual_count_methods": {"elements": "entitylist", "solids": "marklength"},
        "visual_display_count_methods": {
            "elements": "marklength_displayed",
            "solids": "marklength_displayed",
        },
    }

    assert _modeling_visual_count_methods(payload) == {
        "elements": "entitylist",
        "solids": "marklength",
    }
    assert _modeling_visual_display_count_methods(payload) == {
        "elements": "marklength_displayed",
        "solids": "marklength_displayed",
    }
    assert _modeling_visual_count_methods({"visual_count_methods": "bad"}) is None


def test_modeling_visual_diagnostics_accepts_top_level_and_nested_refresh():
    top_level = {
        "success": True,
        "visual_diagnostics": [
            {"entity_type": "solids", "state": "present_hidden", "severity": "warning"},
        ],
    }
    nested = {
        "success": True,
        "stages": {
            "visual_refresh": {
                "visual_diagnostics": [
                    {"entity_type": "visual_refresh", "state": "visual_step_errors"},
                    "bad",
                ],
            }
        },
    }

    assert _modeling_visual_diagnostics(top_level) == [
        {"entity_type": "solids", "state": "present_hidden", "severity": "warning"}
    ]
    assert _modeling_visual_diagnostics(nested) == [
        {"entity_type": "visual_refresh", "state": "visual_step_errors"}
    ]
    assert _modeling_visual_diagnostics({"visual_diagnostics": "bad"}) is None


def test_modeling_visual_refresh_accepts_nested_refresh_summary():
    payload = {
        "success": True,
        "stages": {
            "visual_refresh": {
                "visual_refresh_ok": False,
                "visual_refresh_reason": "visual_step_errors",
                "visual_failed_steps": {"hm_redraw": {"status": "error", "error": "bad"}},
                "visual_failed_step_count": 1,
            }
        },
    }

    assert _modeling_visual_refresh(payload) == {
        "ok": False,
        "reason": "visual_step_errors",
        "failed_steps": {"hm_redraw": {"status": "error", "error": "bad"}},
        "failed_step_count": 1,
    }


def test_modeling_runtime_validation_evidence_accepts_top_level_evidence():
    payload = {
        "success": True,
        "runtime_validation_evidence": {
            "route_name": "create_geometry_solid_box",
            "runtime_validated": True,
        },
    }

    assert _modeling_runtime_validation_evidence(payload) == payload["runtime_validation_evidence"]
    assert _modeling_runtime_validation_evidence({"runtime_validation_evidence": "bad"}) is None


def test_modeling_visual_counts_requires_positive_element_count_only():
    assert _modeling_visual_counts_ok({"success": True, "visual_counts": {"elements": 0, "solids": 1}}) is False
    assert _modeling_visual_counts_ok({"success": True, "visual_counts": {"elements": 1, "solids": 0}}) is True
    assert _modeling_visual_counts_ok({"success": True, "visual_counts": {"elements": 1}}) is True
    assert _modeling_visual_counts_ok({"success": True}) is False


def test_modeling_visual_display_accepts_displayed_elements_without_solid_requirement():
    payload = {
        "success": True,
        "visual_counts": {"elements": 1, "solids": 0},
        "visual_displayed_counts": {"elements": 1, "solids": 0},
        "visibility": {"elements": "displayed", "solids": "present_hidden"},
    }

    assert _modeling_visual_display_ok(payload) is True


def test_modeling_visual_display_rejects_missing_display_evidence():
    payload = {
        "success": True,
        "visual_counts": {"elements": 1},
    }

    assert _modeling_visual_display_ok(payload) is False


def test_modeling_visual_display_accepts_positive_display_counts_without_visibility():
    payload = {
        "success": True,
        "visual_counts": {"elements": 1, "solids": 0},
        "visual_displayed_counts": {"elements": 1, "solids": 0},
    }

    assert _modeling_visual_display_ok(payload) is True


def test_modeling_smoke_failure_reports_gui_not_connected():
    failure = _modeling_smoke_failure(
        gui_connected=False,
        payload=None,
        visual_counts=None,
        visual_counts_ok=None,
        visual_displayed_counts=None,
        visibility=None,
        visual_display_ok=None,
    )

    assert failure["reason"] == "gui_not_connected"


def test_modeling_smoke_failure_reports_tool_failure():
    failure = _modeling_smoke_failure(
        gui_connected=True,
        payload={"success": False, "stage": "solid_box", "error": "no solid"},
        visual_counts=None,
        visual_counts_ok=False,
        visual_displayed_counts=None,
        visibility=None,
        visual_display_ok=False,
    )

    assert failure == {"reason": "tool_failed", "stage": "solid_box", "error": "no solid"}


def test_modeling_smoke_failure_reports_listener_version_mismatch():
    failure = _modeling_smoke_failure(
        gui_connected=True,
        listener_version_ok=False,
        listener_version_status={"current": "2024-compat-v2", "expected": "2024-compat-v3", "ok": False},
        payload=None,
        visual_counts=None,
        visual_counts_ok=False,
        visual_displayed_counts=None,
        visibility=None,
        visual_display_ok=False,
    )

    assert failure["reason"] == "listener_version_mismatch"
    assert failure["listener_version"]["current"] == "2024-compat-v2"


def test_modeling_smoke_failure_reports_visual_count_problem():
    failure = _modeling_smoke_failure(
        gui_connected=True,
        payload={"success": True, "visual_counts": {"elements": 0, "solids": 1}},
        visual_counts={"elements": 0, "solids": 1},
        visual_counts_ok=False,
        visual_displayed_counts=None,
        visibility=None,
        visual_display_ok=False,
    )

    assert failure["reason"] == "visual_counts_insufficient"
    assert failure["required"] == {"elements": "> 0"}


def test_modeling_smoke_failure_reports_hidden_display_problem():
    failure = _modeling_smoke_failure(
        gui_connected=True,
        payload={"success": True},
        visual_counts={"elements": 1, "solids": 0},
        visual_counts_ok=True,
        visual_displayed_counts={"elements": 0, "solids": 0},
        visibility={"elements": "present_hidden", "solids": "present_hidden"},
        visual_display_ok=False,
    )

    assert failure["reason"] == "visual_display_hidden"
    assert failure["visibility"]["elements"] == "present_hidden"
    assert failure["required"] == {"elements": "displayed"}


def test_modeling_smoke_failure_returns_none_for_valid_payload():
    assert _modeling_smoke_failure(
        gui_connected=True,
        payload={"success": True, "visual_counts": {"elements": 1, "solids": 0}},
        visual_counts={"elements": 1, "solids": 0},
        visual_counts_ok=True,
        visual_displayed_counts={"elements": 1, "solids": 0},
        visibility={"elements": "displayed", "solids": "present_hidden"},
        visual_display_ok=True,
    ) is None


def test_next_hypermesh_commands_prefers_port_helper_and_dedupes():
    commands = _next_hypermesh_commands(
        set_port_payload={
            "hypermesh_command": (
                'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
                'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
            )
        },
        diagnostics_payload={
            "source_command": 'source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"',
            "start_or_source_command": (
                'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
                'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
            ),
            "alternate_port_command": 'source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47885.tcl"',
            "recovery_steps": [
                "In HyperMesh Tcl Console, run: mcp_stop",
                (
                    "In HyperMesh Tcl Console, run: "
                    'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
                    'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
                ),
            ],
        },
        port=47884,
        include=True,
    )

    assert commands == [
        "catch {mcp_stop}",
        (
            'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
            'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
        ),
    ]


def test_next_hypermesh_commands_can_include_alternate_when_no_fixed_port():
    commands = _next_hypermesh_commands(
        set_port_payload=None,
        diagnostics_payload={
            "source_command": 'source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47883.tcl"',
            "start_or_source_command": (
                'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47883} '
                'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47883.tcl"}'
            ),
            "alternate_port_command": 'source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"',
            "alternate_start_or_source_command": (
                'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
                'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
            ),
            "recovery_steps": ["In HyperMesh Tcl Console, run: mcp_stop"],
        },
        port=None,
        include=True,
    )

    assert commands == [
        "catch {mcp_stop}",
        (
            'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47883} '
            'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47883.tcl"}'
        ),
        (
            'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
            'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
        ),
    ]


def test_next_hypermesh_commands_wraps_legacy_source_for_fixed_port():
    commands = _next_hypermesh_commands(
        set_port_payload=None,
        diagnostics_payload={"source_command": 'source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"'},
        port=47884,
        include=True,
    )

    assert commands == [
        (
            'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
            'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
        )
    ]


def test_next_hypermesh_commands_empty_when_not_needed():
    assert _next_hypermesh_commands(
        set_port_payload={"hypermesh_command": "source test.tcl"},
        diagnostics_payload={"source_command": "source test.tcl"},
        port=47884,
        include=False,
    ) == []


def test_retry_smoke_command_includes_fixed_port_and_modeling_flag():
    command = _retry_smoke_command(
        config_path="claude_code_mcp.json",
        server_name="hyper-dyna-mcp",
        with_gui=True,
        modeling_smoke=True,
        port=47884,
        include=True,
    )

    assert command == (
        r"E:\anaconda3\anzhuang\envs\hyper-dyna\python.exe "
        "-B -X utf8 -m program.claude_smoke --config claude_code_mcp.json "
        "--with-gui --port 47884 --modeling-smoke"
    )


def test_retry_smoke_command_empty_when_not_needed():
    assert _retry_smoke_command(
        config_path="claude_code_mcp.json",
        server_name="hyper-dyna-mcp",
        with_gui=True,
        modeling_smoke=True,
        port=47884,
        include=False,
    ) is None


def test_format_next_hypermesh_commands_outputs_tcl_lines():
    result = {
        "next_hypermesh_commands": [
            "catch {mcp_stop}",
            (
                'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
                'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
            ),
        ]
    }

    assert format_next_hypermesh_commands(result) == (
        "catch {mcp_stop}\n"
        'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
        'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
    )


def test_format_next_hypermesh_commands_returns_empty_without_commands():
    assert format_next_hypermesh_commands({"next_hypermesh_commands": []}) == ""
    assert format_next_hypermesh_commands({"success": True}) == ""
