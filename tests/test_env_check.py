"""Tests for environment checking."""

import pytest
from program.tools.env_check import check_environment


def test_check_environment_basic():
    report = check_environment()
    assert report.python_version
    assert report.platform


def test_check_environment_missing_package():
    report = check_environment(required=["nonexistent_pkg_12345"])
    assert not report.ok
    assert "nonexistent_pkg_12345" in report.missing_packages
