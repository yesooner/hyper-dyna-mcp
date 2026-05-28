"""Tests for HyperMesh GUI listener mode."""

from program.tools.hm_gui import (
    generate_listener_tcl,
    save_listener_tcl,
    send_tcl_to_gui,
    execute_tcl_gui,
    DEFAULT_GUI_PORT,
)


def test_generate_listener_tcl():
    script = generate_listener_tcl()
    assert "socket -server" in script
    assert str(DEFAULT_GUI_PORT) in script
    assert "127.0.0.1" in script
    assert "mcp_hm_accept" in script


def test_generate_listener_tcl_custom_port():
    script = generate_listener_tcl(port=50000)
    assert "50000" in script


def test_save_listener_tcl():
    path = save_listener_tcl()
    assert path.exists()
    assert path.name == "hm_gui_listener.tcl"
    content = path.read_text(encoding="utf-8")
    assert "socket -server" in content


def test_send_tcl_to_gui_refused():
    """Connection refused when no listener is running."""
    result = send_tcl_to_gui('puts "hello"', timeout=2)
    assert result["success"] is False
    assert "refused" in result["error"].lower() or "error" in result["error"].lower()


def test_execute_tcl_gui_empty():
    result = execute_tcl_gui("")
    assert result["success"] is False
    assert "empty" in result["error"].lower()


def test_execute_tcl_gui_refused():
    """Connection refused when no listener is running."""
    result = execute_tcl_gui('puts "hello"', timeout=2)
    assert result["success"] is False
