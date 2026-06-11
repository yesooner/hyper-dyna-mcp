"""Tests for HyperMesh GUI launch planning guardrails."""

from program.tools import hm_launcher


def test_launch_hm_gui_defaults_to_dry_run(monkeypatch, tmp_path):
    install_dir = tmp_path / "Altair"
    hw_exe = install_dir / "hw" / "bin" / "win64" / "hw.exe"
    hw_exe.parent.mkdir(parents=True)
    hw_exe.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        hm_launcher,
        "load_yaml",
        lambda name: {"hypermesh": {"install_dir": str(install_dir)}},
    )

    result = hm_launcher.launch_hm_gui(wait_for_listener=True)

    assert result["success"] is True
    assert result["executed"] is False
    assert result["dry_run"] is True
    assert result["command"][0].endswith("hw.exe")
    assert result["wait_for_listener_requested"] is True


def test_launch_hm_gui_execute_is_blocked(monkeypatch, tmp_path):
    def fail_load_yaml(name):
        raise AssertionError("execute=True must block before resolving install paths")

    monkeypatch.setattr(hm_launcher, "load_yaml", fail_load_yaml)

    result = hm_launcher.launch_hm_gui(execute=True)

    assert result["success"] is False
    assert result["executed"] is False
    assert result["dry_run"] is True
    assert result["error_type"] == "hypermesh_gui_launch_out_of_scope"


def test_check_listener_requires_pong(monkeypatch):
    def fake_diagnose_listener_port(host, port, timeout, include_alternate):
        return {
            "success": False,
            "diagnosis": {"reason": "port_occupied_without_pong"},
            "ping": {"connected": True, "listener_pong": False},
        }

    import program.tools.hm_gui as hm_gui

    monkeypatch.setattr(hm_gui, "diagnose_listener_port", fake_diagnose_listener_port)

    result = hm_launcher.check_listener(port=47883)

    assert result["success"] is False
    assert result["status"] == "port_occupied_without_pong"
    assert result["ping"]["listener_pong"] is False
