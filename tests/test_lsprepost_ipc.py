"""Tests for LS-PrePost cfile generation (simplified)."""

from program.tools.lsprepost_ipc import generate_cfile_commands, write_cfile


def test_generate_cfile_commands():
    cmds = generate_cfile_commands(d3plot_path="model.d3plot")
    assert "open d3plot model.d3plot" in cmds


def test_generate_cfile_with_keyword():
    cmds = generate_cfile_commands(keyword_path="model.k")
    assert "open key model.k" in cmds


def test_generate_cfile_with_png():
    cmds = generate_cfile_commands(output_png="out.png", width=1920, height=1080)
    assert any("capture" in c for c in cmds)
    assert any("1920" in c for c in cmds)


def test_write_cfile(tmp_path):
    cmds = ["open d3plot test.d3plot", "capture output.png"]
    path = write_cfile(cmds, tmp_path / "test.cfile")
    assert path.exists()
    assert "open d3plot" in path.read_text()
