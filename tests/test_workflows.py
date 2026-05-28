"""Tests for workflow orchestration modules."""

from pathlib import Path
from program.tools.k_writer import KModel, Material, Part, Section, Node, SolidElement, write_k_file
from program.workflows.lsdyna_workflow import parse_and_validate, generate_and_write, solve, full_pipeline
from program.workflows.hm_workflow import check_connection, probe_model, mesh_surfaces
from program.workflows.mixed_workflow import plan_from_k_file, execute_pipeline

_SAMPLES = Path(__file__).resolve().parents[1] / "lib" / "k_samples"


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


def test_solve_dry_run():
    result = solve(_SAMPLES / "minimal_solid.k", dry_run=True)
    assert result["dry_run"] is True
    assert "command" in result


def test_full_pipeline():
    result = full_pipeline(_SAMPLES / "minimal_solid.k", dry_run=True)
    assert result["status"] == "dry_run"
    assert "parse" in result
    assert "solve" in result
    assert result["parse"]["valid"] is True


# --- hm_workflow tests ---


def test_check_connection():
    result = check_connection()
    assert "success" in result
    assert "hmbatch_path" in result


def test_probe_model_dry_run():
    result = probe_model("test.hm", dry_run=True)
    assert result["phase"] == "probe"
    assert "hmbatch_result" in result


def test_mesh_surfaces_dry_run():
    result = mesh_surfaces("test.hm", element_size=2.0, dry_run=True)
    assert result["phase"] == "mesh"
    assert "hmbatch_result" in result


# --- mixed_workflow tests ---


def test_plan_from_k_file():
    result = plan_from_k_file(str(_SAMPLES / "minimal_solid.k"))
    assert result["n_parts"] >= 1
    assert len(result["suggestions"]) > 0


def test_execute_pipeline_dry_run():
    result = execute_pipeline(
        str(_SAMPLES / "minimal_solid.k"),
        dry_run=True,
        log_to_obsidian=False,
    )
    assert result["status"] == "dry_run"
    assert "parse" in result
    assert "solve" in result
