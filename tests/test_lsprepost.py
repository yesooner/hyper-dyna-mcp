"""Tests for LS-PrePost runner and cfile generator."""

import pytest
from pathlib import Path
from program.tools.lsprepost_runner import (
    generate_lsprepost_command,
    run_lsprepost,
)
from program.tools.cfile_generator import (
    generate_cfile,
    generate_open_d3plot,
    generate_undeformed,
    generate_deformed,
    generate_stress_contour,
    generate_energy_plot,
    generate_export_png,
    generate_post_processing,
)


# --- lsprepost_runner tests ---


def test_generate_lsprepost_command():
    cmd = generate_lsprepost_command(cfile="test.cfile")
    assert "cfile=test.cfile" in cmd
    assert any("lsprepost" in c.lower() for c in cmd)


def test_run_lsprepost_dry_run():
    result = run_lsprepost(cfile="test.cfile", dry_run=True)
    assert result["dry_run"] is True
    assert result["executed"] is False


# --- cfile_generator tests ---


def test_generate_cfile_basic():
    content = generate_cfile(["open d3plot test.d3plot", "plot undeform all 1"])
    assert "open d3plot" in content
    assert "plot undeform" in content
    assert content.endswith("\n")


def test_generate_cfile_to_file(tmp_path):
    out = tmp_path / "test.cfile"
    content = generate_cfile(["test command"], output_path=str(out))
    assert out.exists()
    assert "test command" in out.read_text()


def test_open_d3plot():
    cmds = generate_open_d3plot("model.d3plot")
    assert len(cmds) == 1
    assert "open d3plot model.d3plot" in cmds[0]


def test_undeformed():
    cmds = generate_undeformed()
    assert any("undeform" in c for c in cmds)


def test_deformed():
    cmds = generate_deformed(scale=2.0)
    assert any("2.0" in c for c in cmds)


def test_stress_contour():
    cmds = generate_stress_contour("von_mises")
    assert len(cmds) >= 2


def test_energy_plot():
    cmds = generate_energy_plot()
    assert len(cmds) >= 1


def test_export_png():
    cmds = generate_export_png("output.png", width=1920, height=1080)
    assert any("1920" in c for c in cmds)
    assert any("output.png" in c for c in cmds)


def test_post_processing():
    content = generate_post_processing(
        d3plot_path="model.d3plot",
        output_dir="results",
    )
    assert "open d3plot" in content
    assert "results/" in content
    assert "stress" in content.lower() or "fringe" in content.lower()
