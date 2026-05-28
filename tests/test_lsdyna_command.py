"""Tests for LS-DYNA command generation (dry_run)."""

import pytest
from program.tools.lsdyna_runner import LSDynaCommand, generate_solver_command


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
