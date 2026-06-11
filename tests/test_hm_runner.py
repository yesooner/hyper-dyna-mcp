"""Tests for HyperMesh hmbatch runner."""

from pathlib import Path

from program.tools import hm_runner
from program.tools.hm_runner import (
    generate_hmbatch_command,
    run_hmbatch,
    check_hypermesh_connection,
)


def test_generate_hmbatch_command():
    cmd = generate_hmbatch_command(tcl_script="test.tcl")
    assert "-tcl" in cmd
    assert "test.tcl" in cmd
    assert any("hmbatch" in c.lower() for c in cmd)


def test_generate_hmbatch_command_with_model():
    cmd = generate_hmbatch_command(tcl_script="test.tcl", model_file="model.hm")
    assert "-m" in cmd
    assert "model.hm" in cmd


def test_run_hmbatch_dry_run(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)

    result = run_hmbatch(tcl_script="test.tcl", dry_run=True)
    assert result["dry_run"] is True
    assert result["executed"] is False
    assert "command" in result
    assert Path(result["script_path"]).parent == tmp_path


def test_run_hmbatch_blocks_real_execution(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_runner, "_resolve_hmbatch", lambda: tmp_path / "hmbatch.exe")

    result = run_hmbatch(tcl_script="test.tcl", dry_run=False)

    assert result["success"] is False
    assert result["error_type"] == "hmbatch_execution_out_of_scope"
    assert result["executed"] is False
    assert result["command"] == []
    assert result["script_path"] is None


def test_run_hmbatch_blocks_before_writing_or_path_resolution(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)

    def fail_write(*args, **kwargs):
        raise AssertionError("dry_run=False must block before writing a Tcl script")

    def fail_resolve(*args, **kwargs):
        raise AssertionError("dry_run=False must block before resolving hmbatch")

    monkeypatch.setattr(hm_runner, "_write_run_script", fail_write)
    monkeypatch.setattr(hm_runner, "_resolve_hmbatch", fail_resolve)

    result = run_hmbatch(tcl_script='puts "hello"', dry_run=False)

    assert result["success"] is False
    assert result["error_type"] == "hmbatch_execution_out_of_scope"
    assert result["executed"] is False
    assert result["command"] == []
    assert result["script_path"] is None


def test_run_hmbatch_inline_script(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)

    script = 'puts "hello"'
    result = run_hmbatch(tcl_script=script, dry_run=True)
    assert result["dry_run"] is True
    assert "script_path" in result
    # Script should have been written to runs/
    sp = Path(result["script_path"])
    assert sp.exists()
    assert sp.parent == tmp_path
    assert "hello" in sp.read_text()


def test_run_hmbatch_model_not_found(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_runner, "_RUNS_DIR", tmp_path)

    result = run_hmbatch(tcl_script="test.tcl", model_file="/nonexistent/model.hm", dry_run=True)
    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_check_hypermesh_connection():
    result = check_hypermesh_connection()
    assert "success" in result
    assert "hmbatch_path" in result
    # May or may not exist on this machine
    assert isinstance(result["success"], bool)
