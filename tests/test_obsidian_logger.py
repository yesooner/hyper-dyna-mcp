"""Tests for Obsidian logger."""

import pytest
from program.tools.obsidian_logger import write_execution_log


def test_write_log_returns_entry():
    entry = write_execution_log(
        task="Test task",
        modified_files=["test.py"],
        commands=["pytest"],
        test_results="All passed",
        next_steps="Continue",
    )
    assert "Test task" in entry
    assert "test.py" in entry
    assert "pytest" in entry
