"""Tests for path tools."""

import pytest
from program.tools.path_tools import load_yaml, validate_path


def test_load_local_paths():
    data = load_yaml("local_paths")
    assert "project" in data
    assert data["project"]["conda_env"] == "dyna_mcp"


def test_load_obsidian_paths():
    data = load_yaml("obsidian_paths")
    assert "obsidian" in data
    assert "execution_log" in data["obsidian"]


def test_load_nonexistent_config():
    with pytest.raises(FileNotFoundError):
        load_yaml("nonexistent_config_xyz")


def test_validate_path_existing():
    # This file exists (the test itself)
    assert validate_path(__file__)


def test_validate_path_missing():
    assert not validate_path("/nonexistent/path/xyz.txt")
