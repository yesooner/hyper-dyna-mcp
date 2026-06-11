"""HyperMesh plugin loop — file-queue IPC command dispatcher.

MCP server writes JSON commands to ipc/commands/.
This loop polls, dispatches, executes via HyperMesh, writes results to ipc/results/.
"""

from __future__ import annotations

import json
import time
import shutil
import traceback
from pathlib import Path
from typing import Any, Callable

# --- Paths ---

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IPC_DIR = PROJECT_ROOT / "ipc"
COMMAND_DIR = IPC_DIR / "commands"
RESULT_DIR = IPC_DIR / "results"
ARCHIVE_DIR = IPC_DIR / "archive"
STATUS_FILE = IPC_DIR / "status.json"
STOP_FILE = IPC_DIR / "stop.flag"


def ensure_dirs() -> None:
    for p in [COMMAND_DIR, RESULT_DIR, ARCHIVE_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def write_status(state: str, message: str = "") -> None:
    STATUS_FILE.write_text(
        json.dumps(
            {
                "state": state,
                "message": message,
                "timestamp": time.time(),
                "project": "hyper-dyna-mcp",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def read_status() -> dict[str, Any] | None:
    if not STATUS_FILE.exists():
        return None
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def write_result(command_id: str, ok: bool, payload: dict[str, Any]) -> None:
    result_path = RESULT_DIR / f"{command_id}.json"
    result_path.write_text(
        json.dumps(
            {
                "id": command_id,
                "ok": ok,
                "timestamp": time.time(),
                "payload": payload,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def archive_command(cmd_path: Path) -> None:
    target = ARCHIVE_DIR / cmd_path.name
    if target.exists():
        target = ARCHIVE_DIR / f"{cmd_path.stem}_{int(time.time())}{cmd_path.suffix}"
    shutil.move(str(cmd_path), str(target))


# --- Command handlers ---


def ping(command: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "ping",
        "project": "hyper-dyna-mcp",
        "status": "alive",
        "timestamp": time.time(),
    }


def execute_tcl(command: dict[str, Any]) -> dict[str, Any]:
    """Execute Tcl via the HyperMesh GUI socket listener."""
    from program.tools.hm_gui import send_tcl_to_gui

    script = command.get("script", "")
    if not script:
        return {"type": "execute_tcl", "error": "Empty script"}

    timeout = command.get("timeout", 30)
    mode = command.get("mode", "safe")
    # IPC command files are an external boundary. Do not trust command payloads
    # to enable file I/O; dedicated in-process helpers must use socket mode.
    allow_file_io = False
    result = send_tcl_to_gui(script, timeout=timeout, mode=mode, allow_file_io=allow_file_io)
    return {
        "type": "execute_tcl",
        "success": result.get("success", False),
        "response": result.get("response", ""),
        "error": result.get("error"),
        "error_type": result.get("error_type"),
        "policy_violation": result.get("policy_violation"),
        "blocked_command": result.get("blocked_command"),
        "blocked_route_name": result.get("blocked_route_name"),
        "execution_allowed": result.get("execution_allowed"),
        "tcl_sent": result.get("tcl_sent"),
        "retry_allowed": result.get("retry_allowed"),
        "required_tool": result.get("required_tool"),
        "allow_file_io": allow_file_io,
    }


def get_model_info(command: dict[str, Any]) -> dict[str, Any]:
    """Query current model info from HyperMesh GUI."""
    from program.tools.hm_gui import send_tcl_to_gui

    script = '''
    set info {}
    catch {
        *createmark components 1 "all"
        set comps [hm_getmark components 1]
        dict set info components $comps
    }
    catch {
        *createmark nodes 1 "all"
        set nodes [hm_getmark nodes 1]
        dict set info nodes $nodes
    }
    catch {
        *createmark elements 1 "all"
        set elems [hm_getmark elements 1]
        dict set info elements $elems
    }
    puts "MODEL_INFO=$info"
    '''

    result = send_tcl_to_gui(script, timeout=15)
    return {
        "type": "get_model_info",
        "success": result.get("success", False),
        "response": result.get("response", ""),
    }


def export_keyword(command: dict[str, Any]) -> dict[str, Any]:
    """Block LS-DYNA keyword export in the current GUI-only MCP scope."""
    output = command.get("output", "output/exported.k")
    return {
        "type": "export_keyword",
        "success": False,
        "error_type": "k_export_not_verified",
        "error": "K export is outside the current HyperMesh GUI-only MCP scope until a verified GUI export route exists.",
        "output": output,
        "execution_allowed": False,
        "tcl_sent": False,
    }


# --- Dispatch table ---

DISPATCH: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "ping": ping,
    "execute_tcl": execute_tcl,
    "get_model_info": get_model_info,
    "export_keyword": export_keyword,
}


# --- Command handler ---


def handle_command(cmd_path: Path) -> None:
    """Load, dispatch, and archive a single command."""
    try:
        command = json.loads(cmd_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        write_result(cmd_path.stem, False, {"error": f"Bad command file: {exc}"})
        archive_command(cmd_path)
        return

    command_id = str(command.get("id", cmd_path.stem))
    command_type = command.get("type")

    # Special: stop command
    if command_type == "stop":
        write_result(command_id, True, {"message": "stop requested"})
        STOP_FILE.write_text("stop", encoding="utf-8")
        archive_command(cmd_path)
        return

    handler = DISPATCH.get(command_type)
    if handler is None:
        write_result(
            command_id,
            False,
            {
                "error": f"Unknown command type: {command_type}",
                "allowed": list(DISPATCH.keys()) + ["stop"],
            },
        )
        archive_command(cmd_path)
        return

    try:
        payload = handler(command)
        write_result(command_id, True, payload)
    except Exception as exc:
        write_result(
            command_id,
            False,
            {"error": str(exc), "traceback": traceback.format_exc()},
        )
    finally:
        archive_command(cmd_path)


# --- Main loop ---


def mcp_loop(poll_interval: float = 0.5) -> None:
    """Blocking command poll loop.

    Reads ipc/commands/*.json, dispatches, writes ipc/results/*.json.
    Stops when ipc/stop.flag exists.
    """
    ensure_dirs()

    if STOP_FILE.exists():
        STOP_FILE.unlink()

    write_status("running", "blocking loop started")
    print("[mcp_loop] Started. Waiting for commands...")

    while True:
        if STOP_FILE.exists():
            write_status("stopped", "stop.flag detected")
            print("[mcp_loop] Stopped by stop.flag")
            break

        command_files = sorted(COMMAND_DIR.glob("*.json"))
        for cmd_path in command_files:
            handle_command(cmd_path)

        time.sleep(poll_interval)


def submit_command(command_type: str, **kwargs: Any) -> str:
    """Submit a command to the IPC queue. Returns command ID."""
    ensure_dirs()
    import uuid
    cmd_id = uuid.uuid4().hex[:12]
    cmd_path = COMMAND_DIR / f"{cmd_id}.json"
    cmd_path.write_text(
        json.dumps({"id": cmd_id, "type": command_type, **kwargs}, ensure_ascii=False),
        encoding="utf-8",
    )
    return cmd_id


def wait_result(command_id: str, timeout: float = 30.0) -> dict[str, Any] | None:
    """Wait for a command result. Returns None on timeout."""
    result_path = RESULT_DIR / f"{command_id}.json"
    start = time.time()
    while time.time() - start < timeout:
        if result_path.exists():
            try:
                data = json.loads(result_path.read_text(encoding="utf-8"))
                return data
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(0.3)
    return None


if __name__ == "__main__":
    mcp_loop()
