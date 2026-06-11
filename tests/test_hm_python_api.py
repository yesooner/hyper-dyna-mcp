"""Tests for HyperMesh 2024+ Python API script channel."""

from pathlib import Path

from program.tools import hm_python_api
from program.tools.hm_python_api import (
    build_model_info_script,
    check_python_api_environment,
    check_python_api_policy,
    generate_python_api_command,
    query_current_gui_model_info_via_python,
    run_python_api_script,
)


def test_python_api_environment_uses_2025_config():
    result = check_python_api_environment()

    assert result["enabled"] is True
    assert result["version"] == "2025"
    assert result["is_2024_plus"] is True
    assert result["hw_exe"].endswith("hw.exe")
    assert result["script_arg"] == "-python"


def test_build_model_info_script_uses_hm_api():
    script = build_model_info_script("F:/models/test.hm")

    assert "import hm" in script
    assert "import hm.entities as ent" in script
    assert "hm.Session()" in script
    assert "hm.Model(session.get_all_models()[0])" in script
    assert "model.readfile" in script
    assert "HDM_PYTHON_API_RESULT=" in script
    assert "HDM_TRUSTED_RESULT_FILE=" in script


def test_generate_python_api_command():
    command = generate_python_api_command(
        "runs/test.py",
        hw_exe="E:/HM2025/program/hwdesktop/hw/bin/win64/hw.exe",
    )

    assert command[0].endswith("hw.exe")
    assert "-client" in command
    assert "HyperMesh" in command
    assert "-python" in command
    assert "runs/test.py" in command


def test_run_python_api_script_dry_run_writes_script(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_python_api, "_RUNS_DIR", tmp_path)

    script = build_model_info_script()
    result = run_python_api_script(script, dry_run=True)

    assert result["success"] is True
    assert result["dry_run"] is True
    assert result["executed"] is False
    assert "command" in result
    script_path = Path(result["script_path"])
    assert script_path.exists()
    assert script_path.parent == tmp_path
    assert "import hm" in script_path.read_text(encoding="utf-8")


def test_run_python_api_script_blocks_real_external_launch(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_python_api, "_RUNS_DIR", tmp_path)

    script = build_model_info_script()
    result = run_python_api_script(script, dry_run=False)

    assert result["success"] is False
    assert result["dry_run"] is False
    assert result["executed"] is False
    assert result["error_type"] == "hypermesh_python_api_launch_out_of_scope"
    assert result["script_path"] is None
    assert result["command"] == []


def test_run_python_api_script_blocks_before_writing_or_command_generation(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_python_api, "_RUNS_DIR", tmp_path)

    def fail_write(*args, **kwargs):
        raise AssertionError("dry_run=False must block before writing a Python API script")

    def fail_command(*args, **kwargs):
        raise AssertionError("dry_run=False must block before generating a launch command")

    monkeypatch.setattr(hm_python_api, "write_python_api_script", fail_write)
    monkeypatch.setattr(hm_python_api, "generate_python_api_command", fail_command)

    script = build_model_info_script()
    result = run_python_api_script(script, dry_run=False)

    assert result["success"] is False
    assert result["dry_run"] is False
    assert result["executed"] is False
    assert result["error_type"] == "hypermesh_python_api_launch_out_of_scope"
    assert result["script_path"] is None
    assert result["command"] == []


def test_python_api_policy_blocks_unsafe_patterns():
    error = check_python_api_policy("import hm\nimport subprocess\n")

    assert error is not None
    assert "Blocked unsafe" in error


def test_python_api_safe_mode_requires_hm_import():
    error = check_python_api_policy("print('hello')", mode="safe")

    assert error is not None
    assert "import hm" in error


def test_python_api_raw_mode_still_blocks_dangerous_patterns():
    result = run_python_api_script("import os\nos.remove('x')", dry_run=True, mode="raw")

    assert result["success"] is False
    assert result["error_type"] == "policy_error"


def test_current_gui_python_api_query_keeps_meshing_policy_enabled(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, **kwargs):
        captured["script"] = script
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "PY_MODELS=1\n"
                "PY_COMPONENTS=2\n"
                "PY_NODES=3\n"
                "PY_ELEMENTS=4\n"
            ),
        }

    import program.tools.hm_gui as hm_gui

    monkeypatch.setattr(hm_gui, "execute_tcl_gui", fake_execute_tcl_gui)

    result = query_current_gui_model_info_via_python(timeout=19)

    assert result["success"] is True
    assert captured["kwargs"]["timeout"] == 19
    assert captured["kwargs"]["mode"] == "raw"
    assert "enforce_rules" not in captured["kwargs"]
    assert "::hw::HwxPyExec" in captured["script"]
