"""Tests for LS-DYNA command generation (dry_run)."""

from program.tools import lsdyna_runner
from program.tools.lsdyna_runner import LSDynaCommand, generate_solver_command, run_lsdyna


def test_command_format():
    cmd = LSDynaCommand(
        executable="ls-dyna",
        input_file="test.k",
        ncpus=4,
        memory="200m",
    )
    parts = cmd.to_command_list()
    assert parts[0] == "ls-dyna"
    assert "i=test.k" in parts
    assert "ncpus=4" in parts


def test_command_str():
    cmd = LSDynaCommand(executable="ls-dyna", input_file="test.k")
    s = cmd.to_command_str()
    assert "ls-dyna" in s
    assert "i=test.k" in s


def test_run_lsdyna_blocks_real_execution(tmp_path):
    k_file = tmp_path / "model.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    result = run_lsdyna(k_file, dry_run=False)

    assert result["success"] is False
    assert result["error_type"] == "lsdyna_solver_execution_out_of_scope"
    assert result["executed"] is False
    assert result["execution_allowed"] is False
    assert result["solver_execution_allowed"] is False
    assert result["mcp_execution_allowed"] is False
    assert result["offline_review_only"] is True


def test_run_lsdyna_dry_run_is_offline_review_only(tmp_path):
    k_file = tmp_path / "model.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    result = run_lsdyna(k_file, dry_run=True)

    assert result["success"] is True
    assert result["executed"] is False
    assert result["execution_allowed"] is False
    assert result["solver_execution_allowed"] is False
    assert result["mcp_execution_allowed"] is False
    assert result["offline_review_only"] is True


def test_run_lsdyna_blocks_before_command_generation(monkeypatch, tmp_path):
    k_file = tmp_path / "model.k"
    k_file.write_text("*KEYWORD\n*END\n", encoding="utf-8")

    def fail_generate(*args, **kwargs):
        raise AssertionError("dry_run=False must block before command generation")

    monkeypatch.setattr(lsdyna_runner, "generate_solver_command", fail_generate)

    result = lsdyna_runner.run_lsdyna(k_file, dry_run=False)

    assert result["success"] is False
    assert result["error_type"] == "lsdyna_solver_execution_out_of_scope"
    assert result["executed"] is False
    assert result["command"] == ""
    assert result["command_list"] == []
    assert result["execution_allowed"] is False
