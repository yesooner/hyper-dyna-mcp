"""Tests for workflow orchestration modules."""

from pathlib import Path
from program.tools import hm_runner
from program.tools.k_writer import KModel, Material, Part, Section, Node, SolidElement, write_k_file
from program.workflows.lsdyna_workflow import parse_and_validate, generate_and_write, solve, full_pipeline
from program.workflows.hm_workflow import check_connection, probe_model, mesh_surfaces, mesh_solids, save_model
from program.workflows.mixed_workflow import plan_from_k_file, execute_pipeline

_SAMPLES = Path(__file__).resolve().parents[1] / "lib" / "k_samples"
_ROOT = Path(__file__).resolve().parents[1]


def test_agent_workflow_docs_exist_and_match_current_scope():
    selected = _ROOT / "workflows" / "workflow_selected.md"
    execution = _ROOT / "workflows" / "workflow_execution.md"
    validation = _ROOT / "workflows" / "workflow_validation.md"

    for path in (selected, execution, validation):
        assert path.exists()

    text = selected.read_text(encoding="utf-8")
    assert "HyperMesh GUI-only MCP server" in text
    assert "FastMCP stdio server" in text
    assert "solver execution" in text
    validation_text = validation.read_text(encoding="utf-8")
    assert "program.claude_smoke" in validation_text
    assert "claude_smoke.tool_count = 41" in validation_text
    assert "claude_smoke.tool_count = 32" not in validation_text
    assert "modeling_visual_counts.elements > 0" in validation_text
    assert "modeling_visual_counts.solids > 0" not in validation_text.split("Geometry solid counts")[0]
    execution_text = execution.read_text(encoding="utf-8")
    assert "mcp_start_on_port 47884" in execution_text
    assert "hm_modeling_action" in execution_text
    agent_text = (_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    claude_text = (_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "mcp_start_on_port 47884" in agent_text
    assert "HYPERMESH_MCP_PONG" in agent_text
    for doc_text in (agent_text, claude_text):
        assert "hm_python_api_current_model_info" in doc_text
        assert "execute_hm_python_api" in doc_text
        assert "hypermesh_python_api_launch_out_of_scope" in doc_text
        assert "must not start HyperWorks" in doc_text
        assert "launch_hm_gui" in doc_text
        assert "hypermesh_gui_launch_out_of_scope" in doc_text
    for doc_text in (agent_text, claude_text):
        assert "`hm_set_keyword` is MAP-gated" in doc_text
        assert "`dyna_keyword_query.execution_ready` must be true" in doc_text
        assert "dyna_keyword_execution_not_verified" in doc_text
        assert "program.tools.k_parser" in doc_text
        assert "program.tools.hm_k_integration" in doc_text
        assert "offline fixture/validation code only" in doc_text
        assert "generate_integration_script()" in doc_text
        assert "commented" in doc_text
        assert "TET4/TRIA3/BEAM/MASS/DISCRETE" in doc_text
        assert "existing-line mesh" in doc_text
        assert "program.tools.hm_boundary_safe" in doc_text
        assert "constraint_route_not_verified" in doc_text
        assert "blocked_route_name=apply_constraint_spc" in doc_text
        assert "tcl_sent=false" in doc_text
        assert "program.tools.hm_model_writer" in doc_text
        assert "dyna_card_route_not_verified" in doc_text
        assert "set_material" in doc_text
        assert "set_property" in doc_text
        assert "set_contact" in doc_text
        assert "set_load" in doc_text
        assert "program.tools.hm_model_converter" in doc_text
        assert "lsdyna_profile_conversion_not_verified" in doc_text
        assert "activate_lsdyne_template" in doc_text
        assert "lsdyna_template_activation_not_verified" in doc_text
        assert "*templatefileset" in doc_text
        assert "program.tools.cfile_generator" in doc_text
        assert "program.tools.lsprepost_ipc" in doc_text
        assert "commented" in doc_text
        assert "advisory text" in doc_text
        assert "program.workflows.lsdyna_workflow" in doc_text
        assert "program.workflows.mixed_workflow" in doc_text
        assert "offline_review_only=true" in doc_text
        assert "final_k_export_allowed=false" in doc_text
    assert "Execution Entry Guardrails" in agent_text
    assert "send_tcl_to_gui" in agent_text
    assert "plugin_loop.execute_tcl" in agent_text
    assert "file_io_route_not_allowed" in agent_text
    assert "output_hm_path" in agent_text
    assert "hm_auto_save" in agent_text
    assert "allow_file_io=True" in agent_text
    assert "file_io_ipc_not_allowed" in agent_text
    assert "safe_execute_not_verified" in agent_text
    assert "hm_tcl_generator.validate_tcl_script" in agent_text
    assert "generate_save_tcl()" in agent_text
    assert "*feoutputwithdata" in agent_text
    assert "hm_template_validator" in agent_text
    assert "template_execution_not_verified" in agent_text
    assert "Only two internal `enforce_rules=False` paths are expected" in agent_text
    assert "hypermesh_python_api_launch_out_of_scope" in agent_text
    assert "before script writing or command generation" in agent_text
    api_text = (_ROOT / "docs" / "api-reference.md").read_text(encoding="utf-8")
    cc_smoke_text = (_ROOT / "CC_SMOKE_TEST.md").read_text(encoding="utf-8")
    assert "port_owner_summary" in api_text
    assert "port_owner_summary" in cc_smoke_text
    assert "port_occupied_without_pong" in cc_smoke_text
    for smoke_doc_text in (validation_text, cc_smoke_text):
        assert "tool_titles.execute_hm_python_api = Plan HyperMesh Python API Script" in smoke_doc_text
        assert "tool_titles.hm_convert_model = Blocked LS-DYNA Profile Conversion" in smoke_doc_text
        assert "tool_titles.hm_set_keyword = MAP-Gated Keyword Card" in smoke_doc_text
        assert "checked_tools.hm_k_integration_advisory_script_non_executable.ok = true" in smoke_doc_text
        assert "checked_tools.lsprepost_cfile_advisory_non_executable.ok = true" in smoke_doc_text
        assert "checked_tools.lsdyna_runner_dry_run_true_offline_only.offline_review_only = true" in smoke_doc_text
        assert "hm_element_capability_matrix.summary.final_k_export_supported = []" in smoke_doc_text
        assert "hm_element_capability_matrix.summary.hypermesh_gui_k_export_supported = []" in smoke_doc_text
    assert '"error_type": "experimental_route_not_executable"' in api_text
    smoke_section = api_text.split("### `hm_gui_modeling_smoke`", 1)[1]
    assert "visual_counts.elements > 0" in smoke_section
    assert "visual_counts.solids > 0" not in smoke_section
    assert "modeling_runtime_validation_evidence.runtime_validated = true" not in cc_smoke_text
    readme_text = (_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Hyper-Dyna-MCP 是一个面向本机 HyperMesh GUI 的 MCP server" in readme_text
    assert "## 工作流程" in readme_text
    assert "## 快速使用" in readme_text
    assert "## 常用工具" in readme_text
    assert "## 功能范围" in readme_text
    assert "## 录制验证" in readme_text
    assert "## 边界" in readme_text
    assert "FastMCP + stdio" in readme_text
    assert "flowchart TD" in readme_text
    assert "recording_requirements" in readme_text
    assert "validate_recording" in readme_text
    assert "promotion_ready" in readme_text
    assert "HYPERMESH_MCP_PONG" in readme_text
    assert "hm_modeling_action" in readme_text
    assert "hm_element_capability_matrix" in readme_text
    assert "hm_create_fe_cube" in readme_text
    assert "hm_create_surface_plate" in readme_text
    assert "hm_create_shell_plate" in readme_text
    assert "hm_create_beam_line" in readme_text
    assert "默认阻断" in readme_text
    assert "geometry solid box" in readme_text
    assert "`*tetmesh`、surface automesh" in readme_text
    assert "K export" in readme_text
    assert "hm_k_integration" in readme_text
    assert "hm_auto_save" in readme_text
    assert "不能用后端 K writer 代替 GUI 导出" in readme_text
    assert "不能绕过 GUI 建模或伪装成最终 `.k` 导出" in readme_text
    assert "演示内容" not in readme_text
    assert "FE 网格与几何 Solid" not in readme_text
    assert "Execution Entry Guardrails" not in readme_text
    assert "safe_execute_not_verified" not in readme_text
    assert "hm_tcl_generator.validate_tcl_script" not in readme_text
    assert "generate_save_tcl()" not in readme_text
    readme_en_text = (_ROOT / "README.en.md").read_text(encoding="utf-8")
    assert "Hyper-Dyna-MCP is a local MCP server for driving a running HyperMesh GUI session" in readme_en_text
    assert "## Workflow" in readme_en_text
    assert "## Quick Start" in readme_en_text
    assert "## Common Tools" in readme_en_text
    assert "## Capability Scope" in readme_en_text
    assert "## Recording Validation" in readme_en_text
    assert "## Boundaries" in readme_en_text
    assert "FastMCP + stdio" in readme_en_text
    assert "flowchart TD" in readme_en_text
    assert "recording_requirements" in readme_en_text
    assert "validate_recording" in readme_en_text
    assert "promotion_ready" in readme_en_text
    assert "HYPERMESH_MCP_PONG" in readme_en_text
    assert "hm_modeling_action" in readme_en_text
    assert "hm_element_capability_matrix" in readme_en_text
    assert "hm_create_fe_cube" in readme_en_text
    assert "hm_create_surface_plate" in readme_en_text
    assert "hm_create_shell_plate" in readme_en_text
    assert "hm_create_beam_line" in readme_en_text
    assert "Geometry solid" in readme_en_text
    assert "`*tetmesh` / surface automesh" in readme_en_text
    assert "K export" in readme_en_text
    assert "hm_k_integration" in readme_en_text
    assert "hm_auto_save" in readme_en_text
    assert "backend K writer cannot replace GUI export" in readme_en_text
    assert "must not bypass GUI modeling or pretend to be final `.k` export" in readme_en_text
    assert "HyperMesh 2021 Demo Flow" not in readme_en_text
    assert "Current FE Route Boundary" not in readme_en_text
    assert "FE Mesh vs Geometry Solid" not in readme_en_text
    assert "Execution Entry Guardrails" not in readme_en_text
    assert "safe_execute_not_verified" not in readme_en_text
    assert "hm_tcl_generator.validate_tcl_script" not in readme_en_text
    assert "generate_save_tcl()" not in readme_en_text
    executor_doc_text = (_ROOT / "program" / "prompts" / "executor.md").read_text(encoding="utf-8")
    assert "K-file parser/writer/integration" in executor_doc_text
    assert "execute_hm_python_api` is command/script planning only" in executor_doc_text
    assert "hypermesh_python_api_launch_out_of_scope" in executor_doc_text
    assert "must not start HyperWorks" in executor_doc_text
    planner_text = (_ROOT / "program" / "prompts" / "planner.md").read_text(encoding="utf-8")
    executor_text = (_ROOT / "program" / "prompts" / "executor.md").read_text(encoding="utf-8")
    for prompt_text in (planner_text, executor_text):
        assert "TET4/TRIA3/BEAM/MASS/DISCRETE" in prompt_text
        assert "existing-line mesh" in prompt_text
    assert "not existing-line mesh" in executor_text
    validator_text = (_ROOT / "program" / "prompts" / "validator.md").read_text(encoding="utf-8")
    assert "K parser/writer/integration guardrails" in validator_text
    assert "integrate_k_file(dry_run=False)" in validator_text
    assert "generate_integration_script(...)" in validator_text
    assert "commented advisory text only" in validator_text
    assert "LS-PrePost cfile guardrails" in validator_text
    assert "lsprepost_cfile_advisory_non_executable" in validator_text
    assert "offline LS-DYNA workflow guardrails" in validator_text
    assert "final_k_export_allowed=false" in validator_text
    assert "HyperMesh Python API bridge guardrails" in validator_text
    assert "execute_hm_python_api(dry_run=False)" in validator_text
    assert "hypermesh_python_api_launch_out_of_scope" in validator_text
    assert "executed=false" in validator_text
    assert "must not write a script or generate a launch command" in validator_text
    assert "must not start HyperWorks" in validator_text
    assert "validate_tcl_script(generate_save_tcl(...))" in validator_text
    assert "hm_tcl_generator_file_io_blocked" in validator_text
    assert "dry_run=false" in api_text
    assert "error_type=hypermesh_python_api_launch_out_of_scope" in api_text
    assert "Tool title: `Plan HyperMesh Python API Script`" in api_text
    assert "Tool title: `MAP-Gated Keyword Card`" in api_text
    assert "`Blocked LS-DYNA Profile Conversion`" in api_text
    server_text = (_ROOT / "program" / "server.py").read_text(encoding="utf-8")
    assert "Generate a HyperMesh 2024+ Python API script and launch command" in server_text
    assert "Plan HyperMesh Python API Script" in server_text
    assert "Execute HyperMesh Python API" not in server_text
    assert "Blocked LS-DYNA Profile Conversion" in server_text
    assert "Convert Model to LS-DYNA Profile" not in server_text
    assert "Return a blocked compatibility result for unverified profile conversion" in server_text
    assert "Activate the LS-DYNA profile inside HyperMesh and set card images" not in server_text
    assert "MAP-Gated Keyword Card" in server_text
    assert "Set a keyword card only when the structured keyword MAP is execution-ready" in server_text
    assert "Create or update a keyword card inside HyperMesh" not in server_text
    assert "Input for generating a HyperMesh 2024+ Python API script/command" in server_text
    assert "False is accepted for compatibility but returns hypermesh_python_api_launch_out_of_scope" in server_text
    assert "Loading files through execute_tcl_gui is blocked" in server_text
    assert "Saving/export through execute_tcl_gui is blocked" in server_text
    assert "Real external" in server_text
    assert "hypermesh_python_api_launch_out_of_scope" in server_text
    assert "Generate or run a HyperMesh 2024+ Python API script" not in server_text
    assert "Do not launch HyperMesh unless explicitly false" not in server_text
    python_api_text = (_ROOT / "program" / "tools" / "hm_python_api.py").read_text(encoding="utf-8")
    assert "Real external launch is blocked" in python_api_text
    assert "Write and optionally execute a HyperMesh Python API script" not in python_api_text


# --- lsdyna_workflow tests ---


def test_parse_and_validate_valid():
    result = parse_and_validate(_SAMPLES / "minimal_solid.k")
    assert result["valid"] is True
    assert result["n_parts"] >= 1
    assert result["n_materials"] >= 1
    assert len(result["errors"]) == 0


def test_parse_and_validate_errors():
    result = parse_and_validate(_SAMPLES / "missing_material_error.k")
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_generate_and_write(tmp_path):
    model = KModel(
        title="Workflow Test",
        materials=[Material(mid=1, rho=7.85e-9, e=210000.0, pr=0.3)],
        sections=[Section(secid=1)],
        parts=[Part(pid=1, secid=1, mid=1)],
    )
    outpath = tmp_path / "workflow_test.k"
    result = generate_and_write(model, outpath)
    assert outpath.exists()
    assert result["n_materials"] == 1
    assert result["n_parts"] == 1
    assert result["offline_fixture_only"] is True
    assert result["mcp_execution_allowed"] is False
    assert result["final_k_export_allowed"] is False
    assert result["agent_execution_allowed"] is False


def test_solve_dry_run():
    result = solve(_SAMPLES / "minimal_solid.k", dry_run=True)
    assert result["dry_run"] is True
    assert "command" in result
    assert result["execution_allowed"] is False
    assert result["solver_execution_allowed"] is False
    assert result["mcp_execution_allowed"] is False
    assert result["offline_review_only"] is True


def test_full_pipeline():
    result = full_pipeline(_SAMPLES / "minimal_solid.k", dry_run=True)
    assert result["status"] == "offline_plan"
    assert "parse" in result
    assert "solve" in result
    assert result["parse"]["valid"] is True
    assert result["offline_review_only"] is True
    assert result["mcp_execution_allowed"] is False
    assert result["solver_execution_allowed"] is False


def test_full_pipeline_blocks_real_solver_execution():
    result = full_pipeline(_SAMPLES / "minimal_solid.k", dry_run=False)
    assert result["status"] == "blocked"
    assert result["error_type"] == "lsdyna_solver_execution_out_of_scope"
    assert result["solve"]["executed"] is False
    assert result["execution_allowed"] is False
    assert result["mcp_execution_allowed"] is False
    assert result["solver_execution_allowed"] is False


# --- hm_workflow tests ---


def test_check_connection():
    result = check_connection()
    assert "success" in result
    assert "hmbatch_path" in result


def test_probe_model_dry_run(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)
    model_path = tmp_path / "test.hm"
    model_path.write_text("# test model", encoding="utf-8")

    result = probe_model(str(model_path), dry_run=True)
    assert result["phase"] == "probe"
    assert "hmbatch_result" in result
    assert Path(result["hmbatch_result"]["script_path"]).parent == tmp_path


def test_probe_model_blocks_real_hmbatch_execution(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_runner, "_resolve_hmbatch", lambda: tmp_path / "hmbatch.exe")
    model_path = tmp_path / "test.hm"
    model_path.write_text("# test model", encoding="utf-8")

    result = probe_model(str(model_path), dry_run=False)

    assert result["phase"] == "probe"
    assert result["status"] == "blocked"
    assert result["error_type"] == "hmbatch_execution_out_of_scope"
    assert result["execution_allowed"] is False
    assert result["hmbatch_result"]["executed"] is False


def test_save_model_blocks_real_hmbatch_execution(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_runner, "_resolve_hmbatch", lambda: tmp_path / "hmbatch.exe")
    model_path = tmp_path / "test.hm"
    model_path.write_text("# test model", encoding="utf-8")

    result = save_model(str(model_path), str(tmp_path / "out.hm"), dry_run=False)

    assert result["phase"] == "save"
    assert result["status"] == "blocked"
    assert result["error_type"] == "hmbatch_execution_out_of_scope"
    assert result["execution_allowed"] is False
    assert result["hmbatch_result"]["executed"] is False


def test_mesh_surfaces_dry_run(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)
    model_path = tmp_path / "test.hm"
    model_path.write_text("# test model", encoding="utf-8")

    result = mesh_surfaces(str(model_path), element_size=2.0, dry_run=True)
    assert result["phase"] == "mesh"
    assert result["success"] is False
    assert result["error_type"] == "surface_automesh_not_verified"
    assert result["blocked_route_name"] == "surface_automesh"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert "hmbatch_result" not in result


def test_mesh_solids_dry_run_is_blocked(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)
    model_path = tmp_path / "test.hm"
    model_path.write_text("# test model", encoding="utf-8")

    result = mesh_solids(str(model_path), element_size=3.0, dry_run=True)
    assert result["phase"] == "mesh"
    assert result["success"] is False
    assert result["error_type"] == "tetmesh_geometry_solid_not_verified"
    assert result["blocked_route_name"] == "tetmesh_geometry_solid"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert "hmbatch_result" not in result


# --- mixed_workflow tests ---


def test_plan_from_k_file():
    result = plan_from_k_file(str(_SAMPLES / "minimal_solid.k"))
    assert result["n_parts"] >= 1
    assert len(result["suggestions"]) > 0
    assert result["offline_review_only"] is True
    assert result["mcp_execution_allowed"] is False
    assert result["solver_execution_allowed"] is False
    assert all("ready to solve" not in item for item in result["suggestions"])


def test_execute_pipeline_dry_run():
    result = execute_pipeline(
        str(_SAMPLES / "minimal_solid.k"),
        dry_run=True,
        log_to_obsidian=False,
    )
    assert result["status"] == "offline_plan"
    assert "parse" in result
    assert "solve" in result
    assert result["offline_review_only"] is True
    assert result["mcp_execution_allowed"] is False
    assert result["solver_execution_allowed"] is False


def test_execute_pipeline_blocks_real_solver_execution():
    result = execute_pipeline(
        str(_SAMPLES / "minimal_solid.k"),
        dry_run=False,
        log_to_obsidian=False,
    )
    assert result["status"] == "blocked"
    assert result["error_type"] == "lsdyna_solver_execution_out_of_scope"
    assert result["solve"]["executed"] is False
    assert result["execution_allowed"] is False
    assert result["mcp_execution_allowed"] is False
    assert result["solver_execution_allowed"] is False
