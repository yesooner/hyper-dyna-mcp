"""Tests for HyperMesh GUI listener mode."""

from pathlib import Path

from program import transport_manager
from program import plugin_loop
from program.tools import hm_model_writer
from program.tools import hm_gui
from program.tools.hm_gui import (
    generate_listener_tcl,
    save_listener_tcl,
    diagnose_listener_port,
    configure_gui_port,
    current_gui_port,
    send_tcl_to_gui,
    execute_tcl_gui,
    DEFAULT_GUI_PORT,
    ensure_listener_tcl_for_port,
    _check_forbidden,
    _check_whitelist,
    _tcl_start_or_source_command,
    parse_listener_ping_response,
)
from program.tools.hm_policy import wrap_generated_tcl
from program.tools.hm_model_writer import _parse_visualization_response, _summarize_visibility


def test_generate_listener_tcl():
    script = generate_listener_tcl()
    assert "socket -server" in script
    assert str(DEFAULT_GUI_PORT) in script
    assert "127.0.0.1" in script
    assert "mcp_hm_accept" in script


def test_generate_listener_tcl_custom_port():
    script = generate_listener_tcl(port=50000)
    assert "50000" in script


def test_generate_listener_tcl_closes_server_channel():
    script = generate_listener_tcl()
    assert "proc ::mcp_hm_close_port" in script
    assert "chan names" in script
    assert "-sockname" in script
    assert "close $::mcp_hm_server" in script
    assert "close ::mcp_hm_server" not in script
    assert "Cannot start HyperMesh MCP listener" in script


def test_generate_listener_tcl_forces_configured_port():
    script = generate_listener_tcl(port=50000)
    assert "set ::mcp_hm_port 50000" in script
    assert 'if {![info exists ::mcp_hm_port]}' not in script


def test_generate_listener_tcl_has_ping_and_fatal_response():
    script = generate_listener_tcl()
    assert "__HDM_PING__" in script
    assert "HYPERMESH_MCP_PONG" in script
    assert "LISTENER_VERSION=" in script
    assert "TCL_VERSION=[info tclversion]" in script
    assert "TCL_PATCHLEVEL=[info patchlevel]" in script
    assert "Listener fatal error" in script
    assert "-buffering none" in script


def test_generate_listener_tcl_uses_nonblocking_request_read_for_tcl_ping():
    script = generate_listener_tcl()

    assert "proc ::mcp_hm_read_request" in script
    assert "catch {fconfigure $chan -blocking 0}" in script
    assert "set script [::mcp_hm_read_request $chan]" in script
    assert "set script [read $chan]" not in script
    assert "quiet_deadline" in script


def test_generate_listener_tcl_is_hm2024_compat():
    script = generate_listener_tcl()
    assert "2024-compat-v3" in script


def test_activate_lsdyne_template_blocks_profile_activation(monkeypatch):
    def fail_send(*args, **kwargs):
        raise AssertionError("LS-DYNA template activation must not send Tcl")

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fail_send)

    result = hm_gui.activate_lsdyne_template(port=50000, timeout=3)

    assert result["success"] is False
    assert result["error_type"] == "lsdyna_template_activation_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["blocked_command"] == "templatefileset"
    assert result["blocked_route_name"] == "activate_lsdyna_template"


def test_parse_listener_ping_response():
    info = parse_listener_ping_response(
        "OK\n"
        "HYPERMESH_MCP_PONG\n"
        "LISTENER_VERSION=2024-compat-v3\n"
        "TCL_VERSION=8.6\n"
        "TCL_PATCHLEVEL=8.6.13\n"
    )
    assert info["pong"] == "true"
    assert info["listener_version"] == "2024-compat-v3"
    assert info["tcl_version"] == "8.6"
    assert info["tcl_patchlevel"] == "8.6.13"


def test_save_listener_tcl():
    path = save_listener_tcl()
    assert path.exists()
    assert path.name == "hm_gui_listener.tcl"
    content = path.read_text(encoding="utf-8")
    assert "socket -server" in content


def test_save_listener_tcl_custom_filename_and_port(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)

    path = save_listener_tcl(port=50001, filename="hm_gui_listener_50001.tcl")
    assert path.exists()
    assert path.name == "hm_gui_listener_50001.tcl"
    assert path.parent == tmp_path
    content = path.read_text(encoding="utf-8")
    assert "set ::mcp_hm_port 50001" in content


def test_ensure_listener_tcl_for_port_uses_port_specific_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_gui, "_configured_gui_port_from_file", lambda: 47883)

    default_path = ensure_listener_tcl_for_port(47883)
    alternate_path = ensure_listener_tcl_for_port(47884)

    assert default_path.name == "hm_gui_listener.tcl"
    assert alternate_path.name == "hm_gui_listener_47884.tcl"
    assert "set ::mcp_hm_port 47883" in default_path.read_text(encoding="utf-8")
    assert "set ::mcp_hm_port 47884" in alternate_path.read_text(encoding="utf-8")


def test_tcl_start_or_source_command_prefers_verified_port_helper():
    command = _tcl_start_or_source_command(47884, "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl")

    assert command == (
        'if {[llength [info commands mcp_start_on_port]]} {mcp_start_on_port 47884} '
        'else {source "F:/hyper-dyna-mcp/runs/hm_gui_listener_47884.tcl"}'
    )


def test_diagnose_listener_port_suggests_alternate_listener(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_gui, "_raw_listener_ping", lambda *args, **kwargs: {
        "connected": True,
        "listener_pong": False,
        "listener_version": None,
        "response": "",
        "error": "socket_timeout: timed out",
    })
    monkeypatch.setattr(
        hm_gui,
        "_netstat_port_owners",
        lambda port: [
            {
                "pid": "123",
                "process_name": "hwx.exe",
                "state": "LISTENING",
                "local_address": f"127.0.0.1:{port}",
            }
        ],
    )
    monkeypatch.setattr(hm_gui, "find_free_listener_port", lambda **kwargs: 50002)

    result = diagnose_listener_port(port=50000, timeout=1)

    assert result["success"] is False
    assert result["suggested_free_port"] == 50002
    assert result["alternate_listener_included"] is True
    assert "hm_gui_listener_50000.tcl" in result["source_command"]
    assert "hm_gui_listener_50002.tcl" in result["alternate_port_command"]
    assert "mcp_start_on_port 50000" in result["start_or_source_command"]
    assert "hm_gui_listener_50000.tcl" in result["start_or_source_command"]
    assert "mcp_start_on_port 50002" in result["alternate_start_or_source_command"]
    assert "hm_gui_listener_50002.tcl" in result["alternate_start_or_source_command"]
    assert "mcp_start_on_port 50000" in result["recovery_steps"][1]
    assert "mcp_start_on_port 50002" in result["recovery_steps"][2]
    assert "\\" not in result["source_command"]
    assert "\\" not in result["alternate_port_command"]
    assert result["port_owners"][0]["process_name"] == "hwx.exe"
    assert result["port_owner_summary"] == ["hwx.exe pid=123 state=LISTENING local=127.0.0.1:50000"]
    assert result["diagnosis"]["reason"] == "port_occupied_without_pong"
    assert "different free port" in result["diagnosis"]["action"]
    assert "Port owner: hwx.exe" in result["diagnosis"]["detail"]


def test_listener_diagnosis_uses_pid_when_process_name_missing():
    diagnosis = hm_gui._listener_diagnosis(
        {
            "connected": True,
            "listener_pong": False,
            "listener_version": None,
            "error": "socket_timeout: timed out",
        },
        [{"pid": "456", "process_name": None}],
    )

    assert diagnosis["reason"] == "port_occupied_without_pong"
    assert "Port owner: 456" in diagnosis["detail"]


def test_diagnose_listener_port_can_skip_alternate_listener(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_gui, "_raw_listener_ping", lambda *args, **kwargs: {
        "connected": False,
        "listener_pong": False,
        "response": "",
        "error": "connection_refused",
    })
    monkeypatch.setattr(hm_gui, "_netstat_port_owners", lambda port: [])
    monkeypatch.setattr(hm_gui, "find_free_listener_port", lambda **kwargs: 50002)

    result = diagnose_listener_port(port=50000, timeout=1, include_alternate=False)

    assert result["suggested_free_port"] is None
    assert result["alternate_port_command"] is None
    assert result["alternate_start_or_source_command"] is None
    assert result["alternate_listener_included"] is False
    assert (tmp_path / "hm_gui_listener_50000.tcl").exists()
    assert not (tmp_path / "hm_gui_listener_50002.tcl").exists()
    assert result["diagnosis"]["reason"] == "listener_not_running"
    assert "Source the generated listener" in result["diagnosis"]["action"]


def test_configure_gui_port_returns_verified_start_command(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)

    result = configure_gui_port(50003)

    assert result["success"] is True
    assert result["port"] == 50003
    assert "hm_gui_listener_50003.tcl" in result["source_command"]
    assert "mcp_start_on_port 50003" in result["start_or_source_command"]
    assert result["hypermesh_command"] == result["start_or_source_command"]
    assert result["next_hypermesh_commands"] == [
        "catch {mcp_stop}",
        result["start_or_source_command"],
    ]


def test_listener_diagnosis_ready_and_version_mismatch():
    ready = hm_gui._listener_diagnosis(
        {
            "connected": True,
            "listener_pong": True,
            "listener_version": hm_gui.LISTENER_VERSION,
            "error": None,
        },
        [],
    )
    mismatch = hm_gui._listener_diagnosis(
        {
            "connected": True,
            "listener_pong": True,
            "listener_version": "2024-compat-v2",
            "error": None,
        },
        [],
    )

    assert ready["reason"] == "listener_ready"
    assert mismatch["reason"] == "listener_version_mismatch"
    assert hm_gui.LISTENER_VERSION in mismatch["detail"]


def test_configure_gui_port_updates_current_process(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)
    old_env = hm_gui.os.environ.get("HDM_GUI_PORT")
    try:
        result = configure_gui_port(50003)

        assert result["success"] is True
        assert current_gui_port() == 50003
        path = Path(result["listener_tcl"])
        assert path.exists()
        assert path.name == "hm_gui_listener_50003.tcl"
        assert "set ::mcp_hm_port 50003" in path.read_text(encoding="utf-8")
        assert result["source_command"].endswith('hm_gui_listener_50003.tcl"')
        assert "mcp_start_on_port 50003" in result["hypermesh_command"]
        assert "\\" not in result["hypermesh_command"]
    finally:
        if old_env is None:
            hm_gui.os.environ.pop("HDM_GUI_PORT", None)
        else:
            hm_gui.os.environ["HDM_GUI_PORT"] = old_env


def test_connection_refused_points_to_current_port_listener(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_gui, "_configured_gui_port_from_file", lambda: 47883)
    monkeypatch.setattr(
        hm_gui.socket,
        "create_connection",
        lambda *args, **kwargs: (_ for _ in ()).throw(ConnectionRefusedError()),
    )

    result = send_tcl_to_gui('puts "hello"', port=50004, timeout=1)

    assert result["success"] is False
    assert result["error_type"] == "connection_refused"
    assert "hm_gui_listener_50004.tcl" in result["error"]
    assert "hm_gui_listener_50004.tcl" in result["source_command"]
    assert "mcp_start_on_port 50004" in result["start_or_source_command"]
    assert result["next_hypermesh_commands"] == [
        "catch {mcp_stop}",
        result["start_or_source_command"],
    ]
    assert "\\" not in result["source_command"]
    assert "\\" not in result["start_or_source_command"]
    assert (tmp_path / "hm_gui_listener_50004.tcl").exists()


def test_socket_timeout_points_to_current_port_listener(monkeypatch, tmp_path):
    monkeypatch.setattr(hm_gui, "_RUNS_DIR", tmp_path)
    monkeypatch.setattr(hm_gui, "_configured_gui_port_from_file", lambda: 47883)
    monkeypatch.setattr(
        hm_gui.socket,
        "create_connection",
        lambda *args, **kwargs: (_ for _ in ()).throw(hm_gui.socket.timeout()),
    )

    result = send_tcl_to_gui('puts "hello"', port=50005, timeout=1)

    assert result["success"] is False
    assert result["error_type"] == "socket_timeout"
    assert "hm_gui_listener_50005.tcl" in result["error"]
    assert "hm_gui_listener_50005.tcl" in result["source_command"]
    assert "mcp_start_on_port 50005" in result["start_or_source_command"]
    assert result["next_hypermesh_commands"] == [
        "catch {mcp_stop}",
        result["start_or_source_command"],
    ]
    assert "\\" not in result["start_or_source_command"]
    assert (tmp_path / "hm_gui_listener_50005.tcl").exists()


def test_send_tcl_to_gui_refused():
    """Connection refused when no listener is running."""
    result = send_tcl_to_gui('puts "hello"', port=57982, timeout=2)
    assert result["success"] is False
    assert result.get("error_type") in {"connection_refused", "socket_timeout", "socket_error"}


def test_execute_tcl_gui_empty():
    result = execute_tcl_gui("")
    assert result["success"] is False
    assert "empty" in result["error"].lower()


def test_execute_tcl_gui_refused():
    """Connection refused when no listener is running."""
    result = execute_tcl_gui('puts "hello"', port=57982, timeout=2)
    assert result["success"] is False


def test_execute_tcl_gui_blocks_generated_unverified_mesh_before_socket(monkeypatch):
    def fail_send(*args, **kwargs):
        raise AssertionError("unverified mesh Tcl must be blocked before socket send")

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fail_send)
    script = wrap_generated_tcl(
        "generate_surface_automesh_tcl",
        '*createmark surfaces 1 "all"\n*automesh 0 2 2',
    )

    result = execute_tcl_gui(script, mode="raw")

    assert result["success"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "surface_automesh"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert "surface_automesh" in result["message"]


def test_execute_tcl_gui_blocks_file_io_path_args_before_socket(monkeypatch):
    def fail_send(*args, **kwargs):
        raise AssertionError("file I/O path args must be blocked before socket send")

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fail_send)

    result = execute_tcl_gui('puts "hello"', model_path="C:/tmp/in.hm", output_hm_path="C:/tmp/out.hm")

    assert result["success"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_auto_save"


def test_execute_tcl_gui_blocks_file_io_commands_before_socket(monkeypatch):
    def fail_send(*args, **kwargs):
        raise AssertionError("file I/O Tcl must be blocked before socket send")

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fail_send)

    result = execute_tcl_gui('*writefile "C:/tmp/out.hm" 1', mode="raw")

    assert result["success"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_auto_save"


def test_solidblock_is_allowed_for_verified_box_creation():
    assert _check_forbidden("*solidblock 1 0 0 0 1 1 1") is None
    assert _check_whitelist("*solidblock 1 0 0 0 1 1 1") is None


def test_guessed_solid_command_is_preblocked():
    error = _check_forbidden("*solidrc 1 0 0 0 1")
    assert error is not None
    assert "blocked command" in error.lower()


def test_safe_whitelist_allows_tcl_control_flow():
    script = """
    set found ""
    foreach candidate {"a" "b"} {
        if {[file exists $candidate]} {
            set found $candidate
            break
        } else {
            continue
        }
    }
    if {$found eq ""} {
        error "not found"
    }
    return $found
    """
    assert _check_whitelist(script) is None


def test_safe_whitelist_allows_model_read_write_commands():
    script = '*readfile "model.hm"\nputs "ok"\n*writefile "out.hm" 1'
    assert _check_whitelist(script) is None


def test_safe_whitelist_allows_verified_hex_element_commands():
    script = """
    *createlist nodes 1 1 2 3 4 5 6 7 8
    *createelement 208 1 1 1
    """
    assert _check_whitelist(script) is None


def test_safe_whitelist_allows_verified_surface_nurbs_commands():
    script = """
    *createdoublearray 16 0 1 0 1 0 0 0 200 0 0 0 100 0 200 100 0
    *surfacecreatenurbs 1 1 2 2 2 2 0 1 16
    """
    assert _check_whitelist(script) is None


def test_send_tcl_to_gui_blocks_file_io_commands_before_socket(monkeypatch):
    def fail_socket(*args, **kwargs):
        raise AssertionError("file I/O Tcl must be blocked before opening a socket")

    monkeypatch.setattr(hm_gui.socket, "socket", fail_socket)

    result = send_tcl_to_gui('*writefile "C:/tmp/out.hm" 1', port=57982, timeout=1, mode="raw")

    assert result["success"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_auto_save"


def test_execute_tcl_gui_preserves_raw_mode_for_socket(monkeypatch):
    captured = {}

    def fake_send(script, host="127.0.0.1", port=47883, timeout=120, mode="safe", allow_file_io=False):
        captured["script"] = script
        captured["mode"] = mode
        captured["allow_file_io"] = allow_file_io
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fake_send)
    monkeypatch.setattr(hm_gui, "start_heartbeat", lambda: None)
    transport_manager.reset_state()

    result = hm_gui.execute_tcl_gui("customhmcommand debug", mode="raw")

    assert result["success"] is True
    assert captured["mode"] == "raw"
    assert captured["allow_file_io"] is False
    assert "customhmcommand debug" in captured["script"]


def test_plugin_loop_passes_mode_to_socket(monkeypatch):
    captured = {}

    def fake_send(script, timeout=120, mode="safe", allow_file_io=False):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["mode"] = mode
        captured["allow_file_io"] = allow_file_io
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fake_send)

    result = plugin_loop.execute_tcl({"script": "customhmcommand debug", "timeout": 7, "mode": "raw"})

    assert result["success"] is True
    assert captured == {
        "script": "customhmcommand debug",
        "timeout": 7,
        "mode": "raw",
        "allow_file_io": False,
    }


def test_plugin_loop_execute_tcl_blocks_file_io_by_default():
    result = plugin_loop.execute_tcl({
        "script": '*writefile "C:/tmp/out.hm" 1',
        "timeout": 1,
        "mode": "raw",
    })

    assert result["success"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_auto_save"
    assert result["allow_file_io"] is False


def test_plugin_loop_execute_tcl_ignores_allow_file_io_payload():
    result = plugin_loop.execute_tcl({
        "script": '*writefile "C:/tmp/out.hm" 1',
        "timeout": 1,
        "mode": "raw",
        "allow_file_io": True,
    })

    assert result["success"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["allow_file_io"] is False


def test_execute_tcl_gui_file_io_does_not_fallback_to_ipc(monkeypatch):
    def fake_send(*args, **kwargs):
        return {"success": False, "error": "connection refused", "response": ""}

    def fail_submit(*args, **kwargs):
        raise AssertionError("file I/O must not be submitted through IPC fallback")

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fake_send)
    monkeypatch.setattr(hm_gui, "start_heartbeat", lambda: None)
    monkeypatch.setattr(plugin_loop, "submit_command", fail_submit)
    transport_manager.reset_state()

    result = hm_gui.execute_tcl_gui(
        '*writefile "C:/tmp/out.hm" 1',
        mode="raw",
        allow_file_io=True,
        port=47883,
        timeout=1,
    )

    assert result["success"] is False
    assert result["error_type"] == "file_io_ipc_not_allowed"
    assert result["fallback_used"] is False


def test_execute_tcl_gui_direct_ipc_path_does_not_pass_file_io_flag(monkeypatch):
    captured = {}

    def fake_submit(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return "cmd_test"

    def fake_wait(command_id, timeout):
        captured["command_id"] = command_id
        captured["wait_timeout"] = timeout
        return {"ok": True, "payload": {"response": "OK"}}

    monkeypatch.setattr(hm_gui, "start_heartbeat", lambda: None)
    monkeypatch.setattr(plugin_loop, "submit_command", fake_submit)
    monkeypatch.setattr(plugin_loop, "wait_result", fake_wait)
    transport_manager.reset_state()
    state = transport_manager.get_state()
    state.socket_active = False
    state.ipc_active = True

    result = hm_gui.execute_tcl_gui("hm_getmark elems 1", mode="raw", timeout=1)

    assert result["success"] is True
    assert result["transport"] == "ipc"
    assert captured["command"] == "execute_tcl"
    assert captured["kwargs"]["mode"] == "raw"
    assert "allow_file_io" not in captured["kwargs"]


def test_plugin_loop_export_keyword_is_blocked(monkeypatch):
    def fail_send(*args, **kwargs):
        raise AssertionError("export_keyword must not send Tcl")

    monkeypatch.setattr(hm_gui, "send_tcl_to_gui", fail_send)

    result = plugin_loop.export_keyword({"output": "bad.k"})

    assert result["success"] is False
    assert result["error_type"] == "k_export_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["output"] == "bad.k"


def test_raw_mode_still_blocks_dangerous_commands():
    result = send_tcl_to_gui("exec debug-tool", port=57982, timeout=1, mode="raw")
    assert result["success"] is False
    assert result["error_type"] == "blocked_command"
    assert "dangerous" in result["error"].lower()


def test_safe_mode_blocks_unknown_dataname_before_socket():
    script = "*setvalue mats id=1 dataname=BOGUS_FIELD value=1"
    result = send_tcl_to_gui(script, port=57982, timeout=1, mode="safe")

    assert result["success"] is False
    assert result["error_type"] == "invalid_dataname"
    assert result["retry_allowed"] is False


def test_raw_mode_skips_dataname_dictionary_validation():
    script = "*setvalue mats id=1 dataname=BOGUS_FIELD value=1"
    result = send_tcl_to_gui(script, port=57982, timeout=1, mode="raw")

    assert result["success"] is False
    assert result.get("error_type") != "invalid_dataname"


def test_send_tcl_to_gui_raw_mode_still_blocks_unverified_meshing_before_socket():
    result = send_tcl_to_gui('*createmark solids 1 "all"\n*tetmesh 1 1 1', port=57982, timeout=1, mode="raw")

    assert result["success"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "tetmesh_geometry_solid"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_modeling_action"


def test_plugin_loop_execute_tcl_preserves_policy_violation_fields():
    result = plugin_loop.execute_tcl({
        "script": '*createmark surfaces 1 "all"\n*automesh 0 2 2',
        "timeout": 1,
        "mode": "raw",
    })

    assert result["success"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "surface_automesh"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False


def test_mesh_box_blocks_unverified_tetmesh_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(script, timeout=60, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.mesh_box("soil", 2.5, timeout=45)

    assert result["success"] is False
    assert result["supported"] is False
    assert result["error_type"] == "unsupported_route"
    assert result["route_name"] == "tetmesh_geometry_solid"
    assert result["available_mesh_routes"] == ["create_structured_hex8_box"]
    assert "command recording" in " ".join(result["required_verification"]).lower()
    assert called is False


def test_verified_modeling_script_gateway_blocks_unverified_mesh_before_socket(monkeypatch):
    def fail_execute(*args, **kwargs):
        raise AssertionError("unverified mesh Tcl must not reach execute_tcl_gui")

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fail_execute)

    result = hm_model_writer._execute_verified_modeling_script(
        '*createmark solids 1 "all"\n*tetmesh 1 1 1',
        timeout=10,
        route_name="create_structured_hex8_box",
    )

    assert result["success"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "tetmesh_geometry_solid"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False


def test_create_fe_cube_builds_structured_hex_mesh(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=60, **kwargs):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "OK\n"
                "NODE_COUNT=1331\n"
                "ELEM_COUNT=1000\n"
                "ELEM_FIRST=1\n"
                "ELEM_LAST=1000\n"
                "VISUAL_ELEMENTS_ALL=1000\n"
                "VISUAL_NODES_ALL=1331\n"
                "VISUAL_SOLIDS_ALL=0\n"
                "VISUAL_SURFS_ALL=0\n"
                "VISUAL_ELEMENTS_ALL_METHOD=entitylist\n"
                "VISUAL_NODES_ALL_METHOD=entitylist\n"
                "VISUAL_SOLIDS_ALL_METHOD=marklength\n"
                "VISUAL_SURFS_ALL_METHOD=marklength\n"
                "VISUAL_ELEMENTS_DISPLAYED=1000\n"
                "VISUAL_NODES_DISPLAYED=1331\n"
                "VISUAL_SOLIDS_DISPLAYED=0\n"
                "VISUAL_SURFS_DISPLAYED=0\n"
                "VISUAL_ELEMENTS_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_NODES_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_SOLIDS_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_SURFS_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_REFRESH=attempted\n"
            ),
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_fe_cube("soil", 500.0, 50.0, comp_name="soil_comp", timeout=33)

    assert result["success"] is True
    assert result["stage"] == "complete"
    assert result["divisions"] == [10, 10, 10]
    assert result["node_count"] == 1331
    assert result["element_count"] == 1000
    assert result["visual_counts"]["elements"] == 1000
    assert result["visual_displayed_counts"]["elements"] == 1000
    assert result["visual_count_methods"]["elements"] == "entitylist"
    assert result["visual_count_methods"]["solids"] == "marklength"
    assert result["visual_display_count_methods"]["elements"] == "marklength_displayed"
    assert result["visual_refresh_ok"] is True
    assert result["visual_refresh_reason"] == "all_visual_steps_ok"
    assert result["visual_failed_steps"] == {}
    assert result["visual_failed_step_count"] == 0
    assert any(
        item["entity_type"] == "elements" and item["severity"] == "ok"
        for item in result["visual_diagnostics"]
    )
    assert result["visibility"]["elements"] == "displayed"
    assert result["visibility"]["solids"] == "absent"
    assert result["visual_steps"] == {}
    assert result["box"]["visual_count_methods"]["elements"] == "entitylist"
    assert captured["timeout"] == 33
    assert captured["kwargs"]["enforce_rules"] is False
    assert '*collectorcreateonly comps "soil_comp" "" 7' in captured["script"]
    assert "*createnode" in captured["script"]
    assert "*createlist nodes 1" in captured["script"]
    assert "*createelement 208 1 1 1" in captured["script"]
    assert "*solidblock" not in captured["script"]
    assert "*tetmesh" not in captured["script"]
    assert "HDM_VISUAL_REFRESH_BEGIN" in captured["script"]
    assert "VISUAL_REFRESH=attempted" in captured["script"]
    assert "hm_viewfit" in captured["script"]


def test_visual_refresh_tool_uses_caught_display_commands(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=15, **kwargs):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "OK\n"
                "VISUAL_ELEMENTS_ALL=8\n"
                "VISUAL_NODES_ALL=27\n"
                "VISUAL_SOLIDS_ALL=1\n"
                "VISUAL_SURFS_ALL=6\n"
                "VISUAL_LINES_ALL=1\n"
                "VISUAL_ELEMENTS_ALL_METHOD=entitylist\n"
                "VISUAL_NODES_ALL_METHOD=entitylist\n"
                "VISUAL_SOLIDS_ALL_METHOD=marklength\n"
                "VISUAL_SURFS_ALL_METHOD=marklength\n"
                "VISUAL_LINES_ALL_METHOD=marklength\n"
                "VISUAL_ELEMENTS_DISPLAYED=8\n"
                "VISUAL_NODES_DISPLAYED=27\n"
                "VISUAL_SOLIDS_DISPLAYED=1\n"
                "VISUAL_SURFS_DISPLAYED=6\n"
                "VISUAL_LINES_DISPLAYED=1\n"
                "VISUAL_ELEMENTS_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_NODES_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_SOLIDS_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_SURFS_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_LINES_DISPLAYED_METHOD=marklength_displayed\n"
                "VISUAL_STEP_hm_viewfit=ok\n"
                "VISUAL_STEP_hm_redraw=error\n"
                "VISUAL_STEP_hm_redraw_ERROR=bad redraw command\n"
                "VISUAL_REFRESH=attempted\n"
            ),
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.refresh_visualization(timeout=9)

    assert result["success"] is True
    assert captured["timeout"] == 9
    assert captured["kwargs"]["enforce_rules"] is False
    assert "VISUAL_ELEMENTS_ALL" in captured["script"]
    assert "VISUAL_SOLIDS_ALL" in captured["script"]
    assert "VISUAL_ELEMENTS_DISPLAYED" in captured["script"]
    assert "VISUAL_SOLIDS_DISPLAYED" in captured["script"]
    assert "VISUAL_ELEMENTS_ALL_METHOD" in captured["script"]
    assert "VISUAL_SOLIDS_DISPLAYED_METHOD" in captured["script"]
    assert "hm_entitylist elements id" in captured["script"]
    assert "proc _hdm_visual_try" in captured["script"]
    assert "_hdm_visual_try hm_viewfit {hm_viewfit}" in captured["script"]
    assert "_hdm_visual_try hm_redraw {hm_redraw}" in captured["script"]
    assert result["visual_counts"] == {
        "elements": 8,
        "nodes": 27,
        "solids": 1,
        "surfaces": 6,
        "lines": 1,
    }
    assert result["visual_displayed_counts"] == {
        "elements": 8,
        "nodes": 27,
        "solids": 1,
        "surfaces": 6,
        "lines": 1,
    }
    assert result["visual_count_methods"] == {
        "elements": "entitylist",
        "nodes": "entitylist",
        "solids": "marklength",
        "surfaces": "marklength",
        "lines": "marklength",
    }
    assert result["visual_display_count_methods"]["solids"] == "marklength_displayed"
    assert result["visibility"]["elements"] == "displayed"
    assert result["visibility"]["solids"] == "displayed"
    assert result["visual_steps"]["hm_viewfit"] == {"status": "ok", "error": None}
    assert result["visual_steps"]["hm_redraw"] == {"status": "error", "error": "bad redraw command"}
    assert result["visual_refresh_ok"] is True
    assert result["visual_refresh_reason"] == "visual_step_warnings"
    assert result["visual_failed_step_count"] == 1
    assert result["visual_failed_steps"]["hm_redraw"] == {
        "status": "error",
        "error": "bad redraw command",
    }


def test_visual_visibility_summary_distinguishes_hidden_entities():
    summary = _summarize_visibility(
        {"elements": 4, "nodes": 8, "solids": 1, "surfaces": 0},
        {"elements": 0, "nodes": -1, "solids": 1, "surfaces": 0},
    )

    assert summary == {
        "elements": "present_hidden",
        "nodes": "present_display_unknown",
        "solids": "displayed",
        "surfaces": "absent",
    }


def test_visual_diagnostics_explain_hidden_entities_and_optional_step_failures():
    parsed = _parse_visualization_response(
        "\n".join(
            [
                "VISUAL_ELEMENTS_ALL=4",
                "VISUAL_NODES_ALL=8",
                "VISUAL_SOLIDS_ALL=1",
                "VISUAL_SURFS_ALL=0",
                "VISUAL_ELEMENTS_DISPLAYED=0",
                "VISUAL_NODES_DISPLAYED=-1",
                "VISUAL_SOLIDS_DISPLAYED=1",
                "VISUAL_SURFS_DISPLAYED=0",
                "VISUAL_STEP_hm_redraw=error",
                "VISUAL_STEP_hm_redraw_ERROR=bad redraw command",
                "VISUAL_REFRESH=attempted",
            ]
        )
    )

    diagnostics = parsed["visual_diagnostics"]

    assert parsed["visibility"]["elements"] == "present_hidden"
    assert parsed["visibility"]["nodes"] == "present_display_unknown"
    assert parsed["visual_refresh_ok"] is True
    assert any(
        item["entity_type"] == "elements"
        and item["severity"] == "warning"
        and "not displayed" in item["message"]
        for item in diagnostics
    )
    assert any(
        item["entity_type"] == "nodes"
        and item["state"] == "present_display_unknown"
        for item in diagnostics
    )
    refresh_diagnostic = next(item for item in diagnostics if item["entity_type"] == "visual_refresh")
    assert refresh_diagnostic["state"] == "visual_step_warnings"
    assert refresh_diagnostic["severity"] == "info"
    assert refresh_diagnostic["failed_steps"]["hm_redraw"]["error"] == "bad redraw command"


def test_create_solid_box_executes_verified_route(monkeypatch):
    called = False
    captured = {}

    def fake_execute_tcl_gui(script, *args, **kwargs):
        nonlocal called
        called = True
        captured["script"] = script
        return {
            "success": True,
            "response": "OK\nSOLIDS_BEFORE=3\nSOLIDS_AFTER=4\nSOLID_ID=4\n",
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_solid_box(
        "solid_box",
        0,
        0,
        0,
        1,
        1,
        1,
        comp_name="solid_component",
    )

    assert result["success"] is True
    assert result["supported"] is True
    assert result["route_name"] == "create_geometry_solid_box"
    assert result["entity_kind"] == "geometry_solid"
    assert result["solid_id"] == 4
    assert "*solidblock" in captured["script"]
    assert called is True


def test_create_solid_box_fails_without_solids_count_increase(monkeypatch):
    monkeypatch.setattr(
        hm_model_writer,
        "execute_tcl_gui",
        lambda *args, **kwargs: {
            "success": True,
            "response": "OK\nSOLIDS_BEFORE=3\nSOLIDS_AFTER=3\nSOLID_ID=3\n",
        },
    )

    result = hm_model_writer.create_solid_box("solid_box", 0, 0, 0, 1, 1, 1)

    assert result["success"] is False
    assert result["created_count"] == 0
    assert "did not increase solids_count" in result["error"]


def test_create_solid_box_rejects_non_positive_dimensions_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": ""}

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_solid_box("flat_solid", 0, 0, 0, 1, 0, 1)

    assert result["success"] is False
    assert result["error_type"] == "invalid_geometry_dimensions"
    assert "dy" in result["error"]
    assert called is False


def test_create_surface_plate_uses_verified_nurbs_surface_route(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=30, **kwargs):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "OK\n"
                "SURFACES_BEFORE=0\n"
                "SURFACES_AFTER=1\n"
                "SURFACES_BEFORE_METHOD=entitylist\n"
                "SURFACES_AFTER_METHOD=entitylist\n"
                "SURFACE_ID=1\n"
                "VISUAL_ELEMENTS_ALL=0\n"
                "VISUAL_NODES_ALL=0\n"
                "VISUAL_SOLIDS_ALL=0\n"
                "VISUAL_SURFS_ALL=1\n"
                "VISUAL_ELEMENTS_DISPLAYED=0\n"
                "VISUAL_NODES_DISPLAYED=0\n"
                "VISUAL_SOLIDS_DISPLAYED=0\n"
                "VISUAL_SURFS_DISPLAYED=1\n"
                "VISUAL_REFRESH=attempted\n"
            ),
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_surface_plate(
        "surface_plate",
        width=200,
        height=100,
        origin_x=0,
        origin_y=0,
        origin_z=0,
        comp_name="TEST_SHELL_PLATE",
        timeout=44,
    )

    assert result["success"] is True
    assert result["supported"] is True
    assert result["entity_kind"] == "geometry_surface"
    assert result["surface_semantics"] == "geometry_surface_not_shell_fe_element"
    assert result["route_name"] == "create_geometry_surface_rect_nurbs"
    assert result["surface_id"] == 1
    assert result["created_count"] == 1
    assert result["visual_counts"]["surfaces"] == 1
    assert result["visual_displayed_counts"]["surfaces"] == 1
    assert result["visibility"]["surfaces"] == "displayed"
    assert captured["timeout"] == 44
    assert captured["kwargs"]["enforce_rules"] is False
    assert '*currentcollector comps "TEST_SHELL_PLATE"' in captured["script"]
    assert "*createdoublearray 16 0 1 0 1 0 0 0 200 0 0 0 100 0 200 100 0" in captured["script"]
    assert "*surfacecreatenurbs 1 1 2 2 2 2 0 1 16" in captured["script"]
    assert "*createelement" not in captured["script"]
    assert "*solidblock" not in captured["script"]
    assert 'puts "SURFACES_BEFORE=$_hdm_surfaces_before"' in captured["script"]
    assert "HDM_VISUAL_REFRESH_BEGIN" in captured["script"]


def test_create_surface_plate_rejects_non_positive_dimensions_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": ""}

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_surface_plate("flat_surface", width=0, height=100)

    assert result["success"] is False
    assert result["error_type"] == "invalid_geometry_dimensions"
    assert "width" in result["error"]
    assert called is False


def test_create_shell_plate_uses_verified_quad4_route(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=90, **kwargs):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "OK\n"
                "SHELL_NODE_COUNT=66\n"
                "SHELL_ELEM_COUNT=50\n"
                "SHELL_ELEM_FIRST=1\n"
                "SHELL_ELEM_LAST=50\n"
                "VISUAL_ELEMENTS_ALL=50\n"
                "VISUAL_NODES_ALL=66\n"
                "VISUAL_SOLIDS_ALL=0\n"
                "VISUAL_SURFS_ALL=0\n"
                "VISUAL_ELEMENTS_DISPLAYED=50\n"
                "VISUAL_NODES_DISPLAYED=66\n"
                "VISUAL_SOLIDS_DISPLAYED=0\n"
                "VISUAL_SURFS_DISPLAYED=0\n"
                "VISUAL_REFRESH=attempted\n"
            ),
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_shell_plate(
        "shell_plate",
        width=200,
        height=100,
        element_size=20,
        comp_name="TEST_SHELL_PLATE",
        timeout=55,
    )

    assert result["success"] is True
    assert result["entity_kind"] == "fe_shell_mesh"
    assert result["shell_semantics"] == "quad4_fe_shell_elements_not_geometry_surface"
    assert result["divisions"] == [10, 5]
    assert result["node_count"] == 66
    assert result["element_count"] == 50
    assert result["visual_counts"]["elements"] == 50
    assert result["visual_displayed_counts"]["elements"] == 50
    assert result["blocked_next_capabilities"]["surface_automesh"].startswith("unsupported")
    assert captured["timeout"] == 55
    assert captured["kwargs"]["enforce_rules"] is False
    assert '*currentcollector comps "TEST_SHELL_PLATE"' in captured["script"]
    assert "*createnode 0 0 0 0 0 0" in captured["script"]
    assert "*createnode 200 100 0 0 0 0" in captured["script"]
    assert "*createlist nodes 1" in captured["script"]
    assert "*createelement 104 1 1 1" in captured["script"]
    assert "*surfacecreatenurbs" not in captured["script"]
    assert "*solidblock" not in captured["script"]
    assert "*tetmesh" not in captured["script"]


def test_create_shell_plate_rejects_large_mesh_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": ""}

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_shell_plate("huge_shell", width=1000, height=1000, element_size=1)

    assert result["success"] is False
    assert result["stage"] == "create_shell_plate"
    assert result["plate"]["error_type"] == "mesh_size_limit"
    assert called is False


def test_create_discrete_spring_uses_verified_route(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=60, **kwargs):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "OK\n"
                "DISCRETE_NODE_COUNT=2\n"
                "DISCRETE_ELEM_COUNT=1\n"
                "DISCRETE_ELEM_ID=12\n"
                "DISCRETE_LAST_TYPE=DISCRETE\n"
                "DISCRETE_LAST_CONFIG=21\n"
                "VISUAL_ELEMENTS_ALL=1\n"
                "VISUAL_NODES_ALL=2\n"
                "VISUAL_ELEMENTS_DISPLAYED=1\n"
                "VISUAL_NODES_DISPLAYED=2\n"
                "VISUAL_REFRESH=attempted\n"
            ),
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_discrete_spring(
        "discrete_spring",
        node_a=(0, 0, 0),
        node_b=(100, 0, 0),
        comp_name="TEST_DISCRETE_ELEMENTS",
        timeout=44,
    )

    assert result["success"] is True
    assert result["entity_kind"] == "fe_discrete_element"
    assert result["discrete_semantics"] == "two_node_discrete_spring_config_21"
    assert result["node_count"] == 2
    assert result["element_count"] == 1
    assert result["element_type"] == "DISCRETE"
    assert result["element_config"] == 21
    assert result["blocked_next_capabilities"]["section_discrete_stiffness_damping"].startswith("unsupported")
    assert captured["timeout"] == 44
    assert captured["kwargs"]["enforce_rules"] is False
    assert '*currentcollector comps "TEST_DISCRETE_ELEMENTS"' in captured["script"]
    assert '*spring $_hdm_discrete_node_a $_hdm_discrete_node_b 1 "" 0' in captured["script"]
    assert "SECTION_DISCRETE" not in captured["script"]
    assert "stiffness" not in captured["script"]
    assert "damping" not in captured["script"]


def test_create_discrete_spring_rejects_coincident_nodes_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": ""}

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_discrete_spring("bad_discrete", node_a=(0, 0, 0), node_b=(0, 0, 0))

    assert result["success"] is False
    assert result["error_type"] == "invalid_node_coordinates"
    assert called is False


def test_create_lumped_mass_uses_verified_route(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=60, **kwargs):
        captured["script"] = script
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {
            "success": True,
            "response": (
                "OK\n"
                "MASS_NODE_COUNT=1\n"
                "MASS_ELEM_COUNT=1\n"
                "MASS_ELEM_ID=13\n"
                "MASS_LAST_TYPE=MASS\n"
                "MASS_LAST_CONFIG=1\n"
                "VISUAL_ELEMENTS_ALL=1\n"
                "VISUAL_NODES_ALL=1\n"
                "VISUAL_ELEMENTS_DISPLAYED=1\n"
                "VISUAL_NODES_DISPLAYED=1\n"
                "VISUAL_REFRESH=attempted\n"
            ),
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_lumped_mass(
        "lumped_mass",
        10.0,
        x=0,
        y=0,
        z=0,
        comp_name="TEST_DISCRETE_ELEMENTS",
        timeout=45,
    )

    assert result["success"] is True
    assert result["entity_kind"] == "fe_mass_element"
    assert result["mass_semantics"] == "one_node_mass_element_config_1"
    assert result["mass"] == 10.0
    assert result["node_count"] == 1
    assert result["element_count"] == 1
    assert result["element_type"] == "MASS"
    assert result["element_config"] == 1
    assert result["blocked_next_capabilities"]["element_mass_property_datanames"].startswith("unsupported")
    assert captured["timeout"] == 45
    assert captured["kwargs"]["enforce_rules"] is False
    assert '*currentcollector comps "TEST_DISCRETE_ELEMENTS"' in captured["script"]
    assert "*createmark nodes 1 $_hdm_mass_node" in captured["script"]
    assert '*masselement 1 10 "" 0' in captured["script"]
    assert "ELEMENT_MASS" not in captured["script"]


def test_create_lumped_mass_rejects_non_positive_mass_before_tcl(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": ""}

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_lumped_mass("bad_mass", 0)

    assert result["success"] is False
    assert result["error_type"] == "invalid_mass"
    assert called is False


def test_gui_modeling_smoke_runs_fe_solid_then_refresh(monkeypatch):
    calls = []

    def fake_create_fe_cube(*args, **kwargs):
        calls.append(("fe", args, kwargs))
        return {"success": True, "element_count": 1}

    def fake_create_solid_box(*args, **kwargs):
        calls.append(("solid", args, kwargs))
        return {
            "success": True,
            "created_count": 1,
            "solid_count_methods": {"before": "entitylist", "after": "marklength"},
        }

    def fake_refresh_visualization(*args, **kwargs):
        calls.append(("refresh", args, kwargs))
        return {
            "success": True,
            "response": "VISUAL_REFRESH=attempted",
            "visual_counts": {"elements": 1, "nodes": 8, "solids": 1, "surfaces": 6},
            "visual_displayed_counts": {"elements": 1, "nodes": 8, "solids": 1, "surfaces": 6},
            "visual_count_methods": {
                "elements": "entitylist",
                "nodes": "entitylist",
                "solids": "marklength",
                "surfaces": "marklength",
            },
            "visual_display_count_methods": {
                "elements": "marklength_displayed",
                "nodes": "marklength_displayed",
                "solids": "marklength_displayed",
                "surfaces": "marklength_displayed",
            },
            "visibility": {"elements": "displayed", "solids": "displayed"},
            "visual_steps": {
                "hm_viewfit": {"status": "ok", "error": None},
                "hm_redraw": {"status": "ok", "error": None},
            },
            "visual_refresh_ok": True,
            "visual_refresh_reason": "all_visual_steps_ok",
            "visual_failed_steps": {},
            "visual_failed_step_count": 0,
        }

    monkeypatch.setattr(hm_model_writer, "create_fe_cube", fake_create_fe_cube)
    monkeypatch.setattr(hm_model_writer, "create_solid_box", fake_create_solid_box)
    monkeypatch.setattr(hm_model_writer, "refresh_visualization", fake_refresh_visualization)

    result = hm_model_writer.run_gui_modeling_smoke(size=12.0, element_size=6.0, timeout=11)

    assert result["success"] is True
    assert result["stage"] == "complete"
    assert result["entity_paths"] == ["fe_mesh", "geometry_solid"]
    assert result["visual_counts"]["elements"] == 1
    assert result["visual_counts"]["solids"] == 1
    assert result["visual_displayed_counts"]["solids"] == 1
    assert result["visual_count_methods"]["solids"] == "marklength"
    assert result["visual_display_count_methods"]["solids"] == "marklength_displayed"
    assert result["visibility"]["elements"] == "displayed"
    assert result["visual_steps"]["hm_viewfit"] == {"status": "ok", "error": None}
    assert result["visual_refresh_ok"] is True
    assert result["visual_refresh_reason"] == "all_visual_steps_ok"
    assert result["visual_failed_steps"] == {}
    assert result["visual_counts_ok"] is True
    assert result["visual_display_ok"] is True
    evidence = result["runtime_validation_evidence"]
    assert evidence["route_name"] == "create_geometry_solid_box"
    assert evidence["runtime_validated"] is True
    assert evidence["verification_level_if_passed"] == "runtime_validated"
    assert evidence["criteria"]["solid_created_count_gt_0"] is True
    assert evidence["criteria"]["visual_display_has_elements"] is True
    assert evidence["criteria"]["visual_refresh_steps_have_no_errors"] is True
    assert evidence["solid"]["solid_count_methods"] == {"before": "entitylist", "after": "marklength"}
    assert evidence["visual_count_methods"]["solids"] == "marklength"
    assert evidence["visual_display_count_methods"]["solids"] == "marklength_displayed"
    assert evidence["visual_refresh"]["ok"] is True
    assert evidence["visual_refresh"]["failed_steps"] == {}
    update_candidate = evidence["command_map_update_candidate"]
    assert update_candidate["path"] == "templates/hm_command_map.json"
    assert update_candidate["route_name"] == "create_geometry_solid_box"
    assert update_candidate["set"]["tested_in_session"] is True
    assert update_candidate["expected_derived"]["runtime_validated"] is True
    assert update_candidate["expected_derived"]["verification_level"] == "runtime_validated"
    assert [call[0] for call in calls] == ["fe", "solid", "refresh"]
    assert calls[0][2]["comp_name"] == "gui_smoke_fe"
    assert calls[0][2]["timeout"] == 11
    assert calls[1][2]["comp_name"] == "gui_smoke_solid"
    assert calls[2][2]["timeout"] == 11


def test_gui_modeling_smoke_allows_missing_solid_counts_but_blocks_solid_promotion(monkeypatch):
    def fake_create_fe_cube(*args, **kwargs):
        return {"success": True, "element_count": 1}

    def fake_create_solid_box(*args, **kwargs):
        return {"success": True, "created_count": 1}

    def fake_refresh_visualization(*args, **kwargs):
        return {
            "success": True,
            "response": "VISUAL_REFRESH=attempted",
            "visual_counts": {"elements": 1, "nodes": 8, "solids": 0, "surfaces": 0},
            "visual_displayed_counts": {"elements": 1, "nodes": 8, "solids": 0, "surfaces": 0},
            "visibility": {"elements": "displayed", "solids": "absent"},
        }

    monkeypatch.setattr(hm_model_writer, "create_fe_cube", fake_create_fe_cube)
    monkeypatch.setattr(hm_model_writer, "create_solid_box", fake_create_solid_box)
    monkeypatch.setattr(hm_model_writer, "refresh_visualization", fake_refresh_visualization)

    result = hm_model_writer.run_gui_modeling_smoke()

    assert result["success"] is True
    assert result["stage"] == "complete"
    assert result["visual_counts_ok"] is True
    assert result["visual_counts_reason"] is None
    assert result["visual_display_ok"] is True
    assert result["runtime_validation_evidence"]["runtime_validated"] is False
    assert result["runtime_validation_evidence"]["criteria"]["solid_route_success"] is True
    assert result["runtime_validation_evidence"]["criteria"]["solid_created_count_gt_0"] is True
    assert result["runtime_validation_evidence"]["criteria"]["visual_counts_have_elements"] is True
    assert result["error"] is None


def test_gui_modeling_smoke_accepts_hidden_solid_display_for_fe_smoke(monkeypatch):
    def fake_create_fe_cube(*args, **kwargs):
        return {"success": True, "element_count": 1}

    def fake_create_solid_box(*args, **kwargs):
        return {"success": True, "created_count": 1}

    def fake_refresh_visualization(*args, **kwargs):
        return {
            "success": True,
            "response": "VISUAL_REFRESH=attempted",
            "visual_counts": {"elements": 1, "nodes": 8, "solids": 1, "surfaces": 6},
            "visual_displayed_counts": {"elements": 1, "nodes": 8, "solids": 0, "surfaces": 0},
            "visibility": {"elements": "displayed", "solids": "present_hidden"},
        }

    monkeypatch.setattr(hm_model_writer, "create_fe_cube", fake_create_fe_cube)
    monkeypatch.setattr(hm_model_writer, "create_solid_box", fake_create_solid_box)
    monkeypatch.setattr(hm_model_writer, "refresh_visualization", fake_refresh_visualization)

    result = hm_model_writer.run_gui_modeling_smoke()

    assert result["success"] is True
    assert result["stage"] == "complete"
    assert result["visual_counts_ok"] is True
    assert result["visual_display_ok"] is True
    assert result["visual_display_reason"] is None
    assert result["runtime_validation_evidence"]["runtime_validated"] is False
    assert result["error"] is None


def test_gui_modeling_smoke_requires_solid_stage_after_route_unblocked(monkeypatch):
    def fake_create_fe_cube(*args, **kwargs):
        return {"success": True, "element_count": 1}

    def fake_create_solid_box(*args, **kwargs):
        return {
            "success": False,
            "error_type": "experimental_route_not_executable",
            "mcp_execution_allowed": False,
        }

    def fake_refresh_visualization(*args, **kwargs):
        return {
            "success": True,
            "response": "VISUAL_REFRESH=attempted",
            "visual_counts": {"elements": 1, "nodes": 8, "solids": 0, "surfaces": 0},
            "visual_displayed_counts": {"elements": 1, "nodes": 8, "solids": 0, "surfaces": 0},
            "visibility": {"elements": "displayed", "solids": "absent"},
            "visual_refresh_ok": True,
            "visual_refresh_reason": "all_visual_steps_ok",
            "visual_failed_steps": {},
        }

    monkeypatch.setattr(hm_model_writer, "create_fe_cube", fake_create_fe_cube)
    monkeypatch.setattr(hm_model_writer, "create_solid_box", fake_create_solid_box)
    monkeypatch.setattr(hm_model_writer, "refresh_visualization", fake_refresh_visualization)

    result = hm_model_writer.run_gui_modeling_smoke()

    assert result["success"] is False
    assert result["stage"] == "solid_box"
    assert result["solid_route_state"] == "failed"
    assert result["solid_route_required_for_success"] is True
    assert result["stages"]["solid_box"]["error_type"] == "experimental_route_not_executable"


def test_gui_modeling_smoke_stops_after_fe_failure(monkeypatch):
    calls = []

    def fake_create_fe_cube(*args, **kwargs):
        calls.append("fe")
        return {"success": False, "error": "socket timeout"}

    def fake_create_solid_box(*args, **kwargs):
        calls.append("solid")
        return {"success": True}

    def fake_refresh_visualization(*args, **kwargs):
        calls.append("refresh")
        return {"success": True}

    monkeypatch.setattr(hm_model_writer, "create_fe_cube", fake_create_fe_cube)
    monkeypatch.setattr(hm_model_writer, "create_solid_box", fake_create_solid_box)
    monkeypatch.setattr(hm_model_writer, "refresh_visualization", fake_refresh_visualization)

    result = hm_model_writer.run_gui_modeling_smoke()

    assert result["success"] is False
    assert result["stage"] == "fe_cube"
    assert calls == ["fe"]
    assert result["stages"]["solid_box"]["stage"] == "not_run"
    assert result["stages"]["visual_refresh"]["reason"] == "fe_cube_failed"


def test_create_fe_cube_strips_mcp_from_created_names(monkeypatch):
    captured = {}

    def fake_execute_tcl_gui(script, timeout=60, **kwargs):
        captured["script"] = script
        return {
            "success": True,
            "response": "OK\nNODE_COUNT=8\nELEM_COUNT=1\nELEM_FIRST=1\nELEM_LAST=1\n",
        }

    monkeypatch.setattr(hm_model_writer, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_model_writer.create_fe_cube(
        "mcp_smoke_cube",
        10.0,
        10.0,
        comp_name="MCP_smoke_component",
    )

    assert result["success"] is True
    assert result["component"] == "smoke_component"
    assert "MCP" not in captured["script"]
    assert "mcp" not in captured["script"]
    assert '*collectorcreateonly comps "smoke_component" "" 7' in captured["script"]


def test_hmcustom_uses_configured_conda_python():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "HDM_PYTHON_EXE" in text
    assert "::env(HDM_PYTHON_EXE)" in text
    assert 'set ::HDM_PYTHON_EXE "python"' in text
    assert "exec python -m program.plugin_loop" not in text
    assert "exec $::HDM_PYTHON_EXE -m program.plugin_loop &" in text


def test_hmcustom_creates_error_log_directory():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "file mkdir [file dirname $::_hdm_error_log]" in text


def test_hmcustom_loop_clears_stale_stop_flag_before_start():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "proc mcp_clear_stop_flag" in text
    assert "file delete -force $flag" in text
    assert 'file mkdir "$::HDM_ROOT/ipc"' in text
    assert "mcp_clear_stop_flag" in text


def test_hmcustom_stop_closes_socket_listener():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "file mkdir [file dirname $flag]" in text
    assert "proc mcp_hm_channels" in text
    assert "proc mcp_hm_close_port" in text
    assert "chan names" in text
    assert "file channels" in text
    assert "foreach ch [mcp_hm_channels]" in text
    assert "-sockname" in text
    assert "set closed [mcp_hm_close_port $::mcp_hm_port]" in text
    assert "Socket listener closed on port" in text


def test_hmcustom_ping_uses_hm2024_compatible_fconfigure():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "proc mcp_hm_configure_socket {sock}" in text
    assert "mcp_hm_configure_socket $sock" in text
    assert "fconfigure $sock -blocking 0 -buffering none -translation binary -encoding utf-8" not in text
    assert "catch {fconfigure $sock -encoding utf-8}" in text


def test_hmcustom_status_requires_mcp_pong_not_only_tcp_port():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "if {[mcp_socket_ping]} {" in text
    assert "HyperMesh MCP listener active on port" in text
    assert "accepts connections but no MCP PONG was received" in text
    assert "Socket: Active on port" not in text


def test_hmcustom_can_start_specific_listener_port():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "proc mcp_start_on_port {port}" in text
    assert "proc mcp_listener_file_for_port {port}" in text
    assert 'hm_gui_listener_${port}.tcl' in text
    assert "set ::mcp_hm_port $port" in text
    assert "mcp_start_on_port $::mcp_hm_port" in text
    assert "mcp_start_on_port $::mcp_hm_port} err" in text
    assert "return $specific" in text


def test_hmcustom_non_default_port_does_not_fallback_to_default_listener():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "if {$port == 47883}" in text
    assert "return $specific" in text
    assert "set default_listener \"$::HDM_ROOT/runs/hm_gui_listener.tcl\"\n    if {[file exists $default_listener]} {\n        return $default_listener\n    }\n    return $specific" not in text


def test_hmcustom_start_verifies_listener_pong_after_source():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "if {[catch {source $listener} err]}" in text
    assert "if {[mcp_socket_ping]} {" in text
    assert "MCP listener verified on port $port" in text
    assert "listener was sourced but no MCP PONG was received" in text
    assert "Run mcp_status. If the TCP port is occupied without PONG" in text


def test_hmcustom_autostarts_listener():
    text = Path("hmcustom.tcl").read_text(encoding="utf-8")

    assert "HDM_AUTO_START" in text
    assert "proc mcp_ensure_listener" in text
    assert "proc mcp_socket_ping" in text
    assert "HYPERMESH_MCP_PONG" in text
    assert "after 1000 {catch {mcp_ensure_listener}}" in text


def test_configure_endpoint_updates_heartbeat_target():
    transport_manager.configure_endpoint("127.0.0.2", 50001)

    assert transport_manager._heartbeat_host == "127.0.0.2"
    assert transport_manager._heartbeat_port == 50001

    transport_manager.configure_endpoint()
