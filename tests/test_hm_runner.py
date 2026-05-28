"""Tests for HyperMesh hmbatch runner."""

import pytest
from pathlib import Path
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


def test_run_hmbatch_dry_run():
    result = run_hmbatch(tcl_script="test.tcl", dry_run=True)
    assert result["dry_run"] is True
    assert result["executed"] is False
    assert "command" in result


def test_run_hmbatch_inline_script():
    script = 'puts "hello"'
    result = run_hmbatch(tcl_script=script, dry_run=True)
    assert result["dry_run"] is True
    assert "script_path" in result
    # Script should have been written to runs/
    sp = Path(result["script_path"])
    assert sp.exists()
    assert "hello" in sp.read_text()


def test_run_hmbatch_model_not_found():
    result = run_hmbatch(tcl_script="test.tcl", model_file="/nonexistent/model.hm", dry_run=True)
    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_check_hypermesh_connection():
    result = check_hypermesh_connection()
    assert "success" in result
    assert "hmbatch_path" in result
    # May or may not exist on this machine
    assert isinstance(result["success"], bool)
