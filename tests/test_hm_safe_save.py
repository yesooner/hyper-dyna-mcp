"""Tests for the dedicated HyperMesh .hm save helper."""

from __future__ import annotations

from program.tools import hm_safe_save


def test_auto_save_uses_dedicated_file_io_escape_hatch(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    def fake_execute_tcl_gui(script, **kwargs):
        captured["script"] = script
        captured["kwargs"] = kwargs
        save_path.write_text("# fake hm", encoding="utf-8")
        return {"success": True, "response": "OK"}

    save_path = tmp_path / "autosave.hm"
    monkeypatch.setattr(hm_safe_save, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_safe_save.auto_save("unit_test", model_path=str(save_path), timeout=7)

    assert result["success"] is True
    assert result["path"] == str(save_path)
    assert "*writefile" in captured["script"]
    assert captured["kwargs"]["timeout"] == 7
    assert captured["kwargs"]["allow_file_io"] is True


def test_auto_save_reports_missing_file(monkeypatch, tmp_path):
    def fake_execute_tcl_gui(script, **kwargs):
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_safe_save, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_safe_save.auto_save("missing_file", model_path=str(tmp_path / "missing.hm"))

    assert result["success"] is False
    assert result["error"] == "HyperMesh reported success but the .hm file was not created."


def test_safe_execute_is_blocked_compatibility_helper(monkeypatch):
    def fail_execute(*args, **kwargs):
        raise AssertionError("safe_execute must not execute arbitrary Tcl")

    def fail_auto_save(*args, **kwargs):
        raise AssertionError("safe_execute must not auto-save after blocked execution")

    monkeypatch.setattr(hm_safe_save, "execute_tcl_gui", fail_execute)
    monkeypatch.setattr(hm_safe_save, "auto_save", fail_auto_save)

    result = hm_safe_save.safe_execute("legacy", 'puts "unsafe"', model_path="C:/tmp/out.hm")

    assert result["success"] is False
    assert result["error_type"] == "safe_execute_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["auto_save_attempted"] is False
    assert result["required_tool"] == "hm_modeling_action"
    assert result["save_tool"] == "hm_auto_save"


def test_safe_batch_execute_is_blocked_compatibility_helper(monkeypatch):
    def fail_execute(*args, **kwargs):
        raise AssertionError("safe_batch_execute must not execute arbitrary Tcl")

    monkeypatch.setattr(hm_safe_save, "execute_tcl_gui", fail_execute)

    result = hm_safe_save.safe_batch_execute([
        {"description": "one", "script": "puts 1"},
        {"description": "two", "script": "puts 2"},
    ])

    assert result["success"] is False
    assert result["error_type"] == "safe_execute_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["steps_completed"] == 0
    assert result["total_steps"] == 2
    assert len(result["results"]) == 2
    assert all(item["error_type"] == "safe_execute_not_verified" for item in result["results"])
