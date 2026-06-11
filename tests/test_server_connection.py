import asyncio
import json

import program.server as server


def test_check_hypermesh_connection_reports_failure_when_no_pong(monkeypatch):
    monkeypatch.setattr(server, "current_gui_port", lambda: 47883)
    monkeypatch.setattr(
        server,
        "send_tcl_to_gui",
        lambda *args, **kwargs: {
            "success": False,
            "response": "",
            "error": "connection_refused",
        },
    )

    payload = json.loads(asyncio.run(server.check_hypermesh_connection_tool()))

    assert payload["success"] is False
    assert payload["connected"] is False
    assert payload["listener_pong"] is False
    assert payload["socket_success"] is False
    assert payload["error"] == "connection_refused"


def test_check_hypermesh_connection_reports_success_only_with_pong(monkeypatch):
    monkeypatch.setattr(server, "current_gui_port", lambda: 47883)
    monkeypatch.setattr(
        server,
        "send_tcl_to_gui",
        lambda *args, **kwargs: {
            "success": True,
            "response": "\n".join(
                [
                    "HYPERMESH_MCP_PONG",
                    f"LISTENER_VERSION={server.LISTENER_VERSION}",
                    "TCL_VERSION=8.6",
                    "TCL_PATCHLEVEL=8.6.13",
                ]
            ),
            "error": None,
        },
    )

    payload = json.loads(asyncio.run(server.check_hypermesh_connection_tool()))

    assert payload["success"] is True
    assert payload["connected"] is True
    assert payload["listener_pong"] is True
    assert payload["socket_success"] is True
    assert payload["listener_version"] == server.LISTENER_VERSION
    assert payload["tcl_version"] == "8.6"
    assert payload["tcl_patchlevel"] == "8.6.13"
