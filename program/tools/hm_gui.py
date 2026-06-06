"""HyperMesh GUI listener mode — socket-based interactive execution.

Adapted from times1234/hypermesh-mcp execute_tcl_gui pattern.
Communicates with a running HyperMesh GUI via TCP socket 127.0.0.1:47882.

Usage:
  1. Open HyperMesh GUI manually
  2. In HyperMesh's Tcl console, source the listener script:
     source "F:/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
  3. Or launch HyperMesh with the listener:
     hmbatch.exe -tcl hm_gui_listener.tcl
  4. Then call execute_tcl_gui() from MCP tools
"""

from __future__ import annotations

import os
import socket
import time
import uuid
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_policy import check_meshing_rules
from program.tools.hm_tcl_generator import quote_tcl_path
from program.transport_manager import get_state, start_heartbeat, TransportState

DEFAULT_GUI_HOST = "127.0.0.1"
DEFAULT_GUI_PORT = int(os.environ.get("HDM_GUI_PORT", "47882"))
_RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"


# --- Tcl listener script generator ---


def generate_listener_tcl(
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
) -> str:
    """Generate the Tcl listener script for HyperMesh GUI.

    This script creates a socket server inside HyperMesh that accepts
    Tcl commands from the MCP server.

    Usage in HyperMesh Tcl console:
      source "path/to/listener.tcl"

    Or save to runs/hm_gui_listener.tcl and source from there.
    """
    return f"""
# Dyna-mcp HyperMesh GUI listener
# Source this file inside a visible HyperMesh session
if {{![info exists ::mcp_hm_host]}} {{
    set ::mcp_hm_host "{host}"
}}
if {{![info exists ::mcp_hm_port]}} {{
    set ::mcp_hm_port {port}
}}

proc ::mcp_hm_restore_puts {{}} {{
    if {{[llength [info commands ::_mcp_orig_puts]] > 0}} {{
        catch {{rename puts ""}}
        catch {{rename ::_mcp_orig_puts puts}}
    }}
    if {{[llength [info commands ::_mcp_base_puts]] > 0}} {{
        catch {{rename puts ""}}
        catch {{rename ::_mcp_base_puts puts}}
    }}
}}
::mcp_hm_restore_puts

proc ::mcp_hm_accept {{chan addr client_port}} {{
    fconfigure $chan -blocking 1 -translation binary -encoding utf-8
    set script [read $chan]

    if {{[string trim $script] eq ""}} {{
        puts $chan "ERROR: empty script"
        flush $chan
        close $chan
        return
    }}

    # Hook puts to capture output
    set ::mcp_capture ""
    proc ::mcp_hm_capture_puts {{args}} {{
        append ::mcp_capture [join $args " "] "\\n"
    }}
    if {{[llength [info commands puts]] > 0}} {{
        catch {{rename puts ::_mcp_base_puts}}
    }}
    rename ::mcp_hm_capture_puts puts

    set code [catch {{uplevel #0 $script}} result options]

    # Restore puts
    catch {{rename puts ""}}
    catch {{rename ::_mcp_base_puts puts}}

    # HyperMesh commands often return non-zero (e.g. *setvalue returns 1)
    # Only treat as error if result contains error keywords
    set is_error 0
    if {{$code == 1}} {{
        set lower_result [string tolower $result]
        if {{[string match "*error*" $lower_result] || \
             [string match "*invalid*" $lower_result] || \
             [string match "*failed*" $lower_result] || \
             [string match "*not found*" $lower_result]}} {{
            set is_error 1
        }}
    }}
    if {{$is_error}} {{
        puts $chan "ERROR"
        puts $chan $result
        if {{[info exists options(-errorinfo)]}} {{
            puts $chan $options(-errorinfo)
        }}
    }} else {{
        puts $chan "OK"
        if {{$::mcp_capture ne ""}} {{ puts $chan $::mcp_capture }}
        if {{$result ne ""}} {{ puts $chan $result }}
    }}
    flush $chan
    close $chan
}}

if {{[info exists ::mcp_hm_server]}} {{
    catch {{close $::mcp_hm_server}}
    unset -nocomplain ::mcp_hm_server
    after 200
}}
set ::mcp_hm_server [socket -server ::mcp_hm_accept -myaddr $::mcp_hm_host $::mcp_hm_port]
puts "Dyna-mcp GUI listener ready on $::mcp_hm_host:$::mcp_hm_port"
"""


def save_listener_tcl(
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
) -> Path:
    """Generate and save the listener Tcl to runs/ directory."""
    _RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = _RUNS_DIR / "hm_gui_listener.tcl"
    path.write_text(generate_listener_tcl(host, port), encoding="utf-8")
    logger.info(f"Saved GUI listener Tcl: {path}")
    return path


# --- Socket client ---


def send_tcl_to_gui(
    script: str,
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
    timeout: int = 120,
) -> dict:
    """Send a Tcl script to the HyperMesh GUI listener via TCP socket.

    Args:
        script: Tcl script to execute in HyperMesh GUI.
        host: Listener host (default 127.0.0.1).
        port: Listener port (default 47882).
        timeout: Socket timeout in seconds.

    Returns:
        dict with success, response, etc.
    """
    if not script.strip():
        return {"success": False, "error": "Empty script"}

    try:
        with socket.create_connection(
            (host, int(port)), timeout=max(1, int(timeout))
        ) as sock:
            sock.settimeout(max(1, int(timeout)))
            sock.sendall(script.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)

            chunks: list[bytes] = []
            while True:
                data = sock.recv(65536)
                if not data:
                    break
                chunks.append(data)

        response = b"".join(chunks).decode("utf-8", errors="replace")
        return {
            "success": response.startswith("OK"),
            "host": host,
            "port": int(port),
            "response": response,
        }

    except ConnectionRefusedError:
        return {
            "success": False,
            "error": (
                f"Connection refused on {host}:{port}. "
                "Make sure HyperMesh GUI is open and the listener is sourced. "
                f"Run: source \"{save_listener_tcl()}\""
            ),
        }
    except OSError as exc:
        return {"success": False, "error": f"Socket error: {exc}"}


# --- Model info query ---


def query_model_info(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT) -> dict:
    """Query current model info from HyperMesh GUI.

    Returns model name, component count/names, node/element counts.
    """
    script = '''
    *createmark comps 1 "all"
    puts "COMPS=[llength [hm_getmark comps 1]]"
    *createmark nodes 1 "all"
    puts "NODES=[llength [hm_getmark nodes 1]]"
    *createmark elements 1 "all"
    puts "ELEMS=[llength [hm_getmark elements 1]]"
    *createmark mats 1 "all"
    puts "MATS=[llength [hm_getmark mats 1]]"
    *createmark props 1 "all"
    puts "PROPS=[llength [hm_getmark props 1]]"
    *createmark groups 1 "all"
    puts "GROUPS=[llength [hm_getmark groups 1]]"
    puts "TITLE=[wm title .]"
    '''

    result = send_tcl_to_gui(script, host=host, port=port, timeout=15)

    if not result.get("success"):
        return {"connected": False, "error": result.get("error")}

    info = {"connected": True}
    resp = result.get("response", "")
    for line in resp.split("\n"):
        line = line.strip()
        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if key in ("COMPS", "NODES", "ELEMS", "MATS", "PROPS", "GROUPS"):
                try:
                    info[key.lower() + "_count"] = int(val)
                except ValueError:
                    info[key.lower() + "_count"] = val
            elif key == "TITLE":
                info["window_title"] = val

    return info


def activate_lsdyne_template(host: str = DEFAULT_GUI_HOST, port: int = DEFAULT_GUI_PORT, timeout: int = 15) -> dict:
    """Activate LS-DYNA solver template in HyperMesh.

    Must be called before any LS-DYNA card image operations.
    Uses *templatefileset to load the HyperMesh LS-DYNA template.
    """
    script = '''
    set template_path {E:/HM2021/2021/hwdesktop/templates/feoutput/ls-dyna971/dyna.key}
    if {![file exists $template_path]} {
        error "LS-DYNA template not found: $template_path"
    }
    set code [catch {*templatefileset $template_path} err]
    puts "TEMPLATE_RESULT=$code"
    puts "TEMPLATE_MESSAGE=$err"
    catch {puts "SOLVER=[hm_getsolver]"}
    catch {puts "TEMPLATE_TYPE=[hm_info templatetype]"}
    '''
    result = send_tcl_to_gui(script, host=host, port=port, timeout=timeout)
    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
    }


# --- High-level API ---


def execute_tcl_gui(
    script: str,
    model_path: str | None = None,
    output_hm_path: str | None = None,
    host: str = DEFAULT_GUI_HOST,
    port: int = DEFAULT_GUI_PORT,
    timeout: int = 120,
    enforce_rules: bool = True,
) -> dict:
    """Execute a Tcl script in HyperMesh GUI with automatic fallback.

    Transport selection (managed by transport_manager):
      1. If socket mode: try send_tcl_to_gui, retry up to 3 times on failure.
      2. After 3 consecutive failures: switch to IPC (submit_command + wait_result).
      3. Heartbeat thread recovers to socket when listener comes back.

    Args:
        script: Tcl script to execute.
        model_path: Optional .hm file to load first (*readfile).
        output_hm_path: Optional .hm file to save after (*writefile).
        host: Listener host.
        port: Listener port.
        timeout: Socket timeout.
        enforce_rules: If True, check meshing safety rules.

    Returns:
        Unified dict: success, command_id, transport, fallback_used,
        retry_count, response, error_type, message.
        Backward-compatible: always has ``success`` and ``response``.
    """
    # Validate script
    if not script.strip():
        return {
            "success": False,
            "command_id": None,
            "transport": None,
            "fallback_used": False,
            "retry_count": 0,
            "response": "",
            "error": "Empty script",
            "error_type": "execution_error",
            "message": "Empty script",
        }

    # Enforce meshing rules
    if enforce_rules:
        violation = check_meshing_rules(script)
        if violation:
            # Wrap legacy violation dict in unified format
            return {
                "success": False,
                "command_id": None,
                "transport": None,
                "fallback_used": False,
                "retry_count": 0,
                "response": "",
                "error": violation.get("error", violation.get("message", "Rule violation")),
                "error_type": "execution_error",
                "message": violation.get("error", violation.get("message", "Rule violation")),
            }

    # Build GUI script with optional readfile/writefile
    gui_parts: list[str] = []
    if model_path:
        gui_parts.append(f'*readfile "{quote_tcl_path(model_path)}"')
    gui_parts.append(script)
    if output_hm_path:
        gui_parts.append(f'*writefile "{quote_tcl_path(output_hm_path)}" 1')

    gui_script = "\n".join(gui_parts)

    # Ensure heartbeat is running
    start_heartbeat()

    state = get_state()

    if state.should_use_socket():
        return _execute_via_socket(gui_script, state, host, port, timeout)
    else:
        return _execute_via_ipc(gui_script, state, timeout)


def _execute_via_socket(
    gui_script: str,
    state: TransportState,
    host: str,
    port: int,
    timeout: int,
) -> dict:
    """Try socket transport with up to 3 retries; fallback to IPC on failure."""
    max_retries = 3
    for attempt in range(max_retries):
        result = send_tcl_to_gui(gui_script, host, port, timeout)

        if result.get("success"):
            state.record_success()
            return _unified_result(
                success=True,
                transport="socket",
                fallback_used=False,
                retry_count=attempt,
                response=result.get("response", ""),
            )

        # Check if this is a connection error (no response) or execution error (has response)
        has_response = bool(result.get("response", "").strip())
        if has_response:
            # Command executed but returned error — don't retry, return immediately
            state.record_success()  # Connection was fine
            return _unified_result(
                success=False,
                transport="socket",
                fallback_used=False,
                retry_count=attempt,
                response=result.get("response", ""),
                error_type="execution_error",
                message="HyperMesh Tcl command returned error",
            )

        # Connection error — retry
        state.record_failure()
        logger.warning(
            f"Socket attempt {attempt + 1}/{max_retries} failed: "
            f"{result.get('error', 'connection error')}"
        )

        # If state switched to IPC after recording failure, break to IPC path
        if not state.should_use_socket():
            break

    if host != DEFAULT_GUI_HOST or int(port) != DEFAULT_GUI_PORT:
        return _unified_result(
            success=False,
            transport="socket",
            fallback_used=False,
            retry_count=max_retries,
            response="",
            error_type="connection_error",
            message=f"Connection failed on explicit socket target {host}:{port}",
        )

    # All socket attempts exhausted or state switched to IPC -> fallback
    logger.info("Falling back to IPC transport")
    return _execute_via_ipc(gui_script, state, timeout, fallback_used=True)


def _execute_via_ipc(
    gui_script: str,
    state: TransportState,
    timeout: int,
    fallback_used: bool = False,
) -> dict:
    """Execute via IPC file-queue (plugin_loop submit_command + wait_result)."""
    from program.plugin_loop import submit_command, wait_result

    cmd_id = submit_command("execute_tcl", script=gui_script, timeout=timeout)
    result = wait_result(cmd_id, timeout=float(timeout) + 10)

    if result is None:
        return _unified_result(
            success=False,
            command_id=cmd_id,
            transport="ipc",
            fallback_used=fallback_used,
            retry_count=0,
            response="",
            error_type="timeout",
            message=f"IPC wait_result timed out after {timeout + 10}s",
        )

    payload = result.get("payload", {})
    ok = result.get("ok", False)
    return _unified_result(
        success=ok,
        command_id=cmd_id,
        transport="ipc",
        fallback_used=fallback_used,
        retry_count=0,
        response=payload.get("response", ""),
        error_type=None if ok else "execution_error",
        message=payload.get("error"),
    )


def _unified_result(
    success: bool,
    command_id: str | None = None,
    transport: str | None = None,
    fallback_used: bool = False,
    retry_count: int = 0,
    response: str = "",
    error_type: str | None = None,
    message: str | None = None,
) -> dict:
    """Build a unified result dict (backward-compatible with legacy callers)."""
    return {
        "success": success,
        "command_id": command_id or f"cmd_{uuid.uuid4().hex[:8]}",
        "transport": transport,
        "fallback_used": fallback_used,
        "retry_count": retry_count,
        "response": response,
        "error": message,
        "error_type": error_type,
        "message": message,
    }
