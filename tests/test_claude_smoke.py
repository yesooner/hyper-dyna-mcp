"""Tests for the repo-local Claude Code MCP compatibility framework."""

import re
from pathlib import Path

import pytest

from program.claude_smoke import (
    ALLOWED_TOOLS,
    EXPECTED_TOOL_COUNT,
    FORBIDDEN_TOOLS,
    REQUIRED_TOOLS,
    _blocked_keyword_execution_ok,
    _json_text_payload,
    _dyna_control_status_guardrail_ok,
    _dyna_d3plot_status_guardrail_ok,
    _dyna_field_status_guardrail_ok,
    _dyna_initial_detonation_status_guardrail_ok,
    _dyna_load_blast_status_guardrail_ok,
    _dyna_section_solid_status_guardrail_ok,
    _dyna_timestep_status_guardrail_ok,
    _dyna_unknown_suggestion_guardrail_ok,
    _gui_diagnosis,
    _gui_listener_runtime,
    _gui_listener_version_status,
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
    _retry_smoke_command,
    _solid_route_runtime_status_ok,
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


def test_claude_required_surface_keeps_tcl_and_python_api_tools():
    assert EXPECTED_TOOL_COUNT == 32
    assert REQUIRED_TOOLS.issubset(ALLOWED_TOOLS)
    assert FORBIDDEN_TOOLS.isdisjoint(ALLOWED_TOOLS)
    assert "check_hypermesh_connection" in REQUIRED_TOOLS
    assert "diagnose_hypermesh_listener" in REQUIRED_TOOLS
    assert "set_hypermesh_listener_port" in REQUIRED_TOOLS
    assert "hm_visual_refresh" in REQUIRED_TOOLS
    assert "hm_gui_modeling_smoke" in REQUIRED_TOOLS
    assert "hm_create_solid_box" in REQUIRED_TOOLS
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


def test_claude_smoke_parses_gui_connection_payload():
    class Result:
        content = [type("Content", (), {"text": '{"connected": false, "success": true}'})()]

    payload = _json_text_payload(Result())

    assert payload == {"connected": False, "success": True}


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
            "status": "verified",
            "entity_kind": "geometry_solid",
            "runtime_validated": False,
            "verification_level": "source_verified_runtime_pending",
        }
    }

    assert _solid_route_runtime_status_ok(payload) is True
    assert _solid_route_runtime_status_ok({"route": {"status": "verified"}}) is False


def test_blocked_keyword_execution_guardrail_requires_map_block_response():
    payload = {
        "success": False,
        "error_type": "dyna_keyword_execution_not_verified",
        "execution_ready": False,
        "execution_decision": {"state": "blocked"},
        "execution_blockers": ["datanames_not_verified"],
        "advisory_only": {"execution_allowed": False},
    }

    assert _blocked_keyword_execution_ok(payload) is True

    payload["success"] = True

    assert _blocked_keyword_execution_ok(payload) is False


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


def test_modeling_visual_counts_accepts_nested_refresh_counts():
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
    assert _modeling_visual_display_ok(payload) is False


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


def test_modeling_visual_counts_rejects_missing_solid_or_element_count():
    assert _modeling_visual_counts_ok({"success": True, "visual_counts": {"elements": 0, "solids": 1}}) is False
    assert _modeling_visual_counts_ok({"success": True, "visual_counts": {"elements": 1, "solids": 0}}) is False
    assert _modeling_visual_counts_ok({"success": True}) is False


def test_modeling_visual_display_accepts_displayed_elements_and_solids():
    payload = {
        "success": True,
        "visual_counts": {"elements": 1, "solids": 1},
        "visual_displayed_counts": {"elements": 1, "solids": 1},
        "visibility": {"elements": "displayed", "solids": "displayed"},
    }

    assert _modeling_visual_display_ok(payload) is True


def test_modeling_visual_display_rejects_missing_display_evidence():
    payload = {
        "success": True,
        "visual_counts": {"elements": 1, "solids": 1},
    }

    assert _modeling_visual_display_ok(payload) is False


def test_modeling_visual_display_accepts_positive_display_counts_without_visibility():
    payload = {
        "success": True,
        "visual_counts": {"elements": 1, "solids": 1},
        "visual_displayed_counts": {"elements": 1, "solids": 1},
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
        payload={"success": True, "visual_counts": {"elements": 1, "solids": 0}},
        visual_counts={"elements": 1, "solids": 0},
        visual_counts_ok=False,
        visual_displayed_counts=None,
        visibility=None,
        visual_display_ok=False,
    )

    assert failure["reason"] == "visual_counts_insufficient"
    assert failure["required"] == {"elements": "> 0", "solids": "> 0"}


def test_modeling_smoke_failure_reports_hidden_display_problem():
    failure = _modeling_smoke_failure(
        gui_connected=True,
        payload={"success": True},
        visual_counts={"elements": 1, "solids": 1},
        visual_counts_ok=True,
        visual_displayed_counts={"elements": 1, "solids": 0},
        visibility={"elements": "displayed", "solids": "present_hidden"},
        visual_display_ok=False,
    )

    assert failure["reason"] == "visual_display_hidden"
    assert failure["visibility"]["solids"] == "present_hidden"
    assert failure["required"] == {"elements": "displayed", "solids": "displayed"}


def test_modeling_smoke_failure_returns_none_for_valid_payload():
    assert _modeling_smoke_failure(
        gui_connected=True,
        payload={"success": True, "visual_counts": {"elements": 1, "solids": 1}},
        visual_counts={"elements": 1, "solids": 1},
        visual_counts_ok=True,
        visual_displayed_counts={"elements": 1, "solids": 1},
        visibility={"elements": "displayed", "solids": "displayed"},
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
