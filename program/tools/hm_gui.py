"""HyperMesh GUI listener mode — socket-based interactive execution.

Adapted from times1234/hypermesh-mcp execute_tcl_gui pattern.
Communicates with a running HyperMesh GUI via TCP socket 127.0.0.1:47881.

Usage:
  1. Open HyperMesh GUI manually
  2. In HyperMesh's Tcl console, source the listener script:
     source "F:/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
  3. Or launch HyperMesh with the listener:
     hmbatch.exe -tcl hm_gui_listener.tcl
  4. Then call execute_tcl_gui() from MCP tools
"""

from __future__ import annotations

import socket
import time
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_policy import check_meshing_rules
from program.tools.hm_tcl_generator import quote_tcl_path

DEFAULT_GUI_HOST = "127.0.0.1"
DEFAULT_GUI_PORT = 47881
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
set ::mcp_hm_host "{host}"
set ::mcp_hm_port {port}

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

    if {{$code == 0 || $code == 2}} {{
        puts $chan "OK"
        if {{$::mcp_capture ne ""}} {{ puts $chan $::mcp_capture }}
        if {{$result ne ""}} {{ puts $chan $result }}
    }} else {{
        puts $chan "ERROR"
        puts $chan $result
        if {{[info exists options(-errorinfo)]}} {{
            puts $chan $options(-errorinfo)
        }}
    }}
    flush $chan
    close $chan
}}

if {{[info exists ::mcp_hm_server]}} {{
    catch {{close ::mcp_hm_server}}
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
        port: Listener port (default 47881).
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
    """Execute a Tcl script in HyperMesh GUI via socket listener.

    Args:
        script: Tcl script to execute.
        model_path: Optional .hm file to load first (*readfile).
        output_hm_path: Optional .hm file to save after (*writefile).
        host: Listener host.
        port: Listener port.
        timeout: Socket timeout.
        enforce_rules: If True, check meshing safety rules.

    Returns:
        dict with success, response, etc.
    """
    # Validate script
    if not script.strip():
        return {"success": False, "error": "Empty script"}

    # Enforce meshing rules
    if enforce_rules:
        violation = check_meshing_rules(script)
        if violation:
            return violation

    # Build GUI script with optional readfile/writefile
    gui_parts: list[str] = []
    if model_path:
        gui_parts.append(f'*readfile "{quote_tcl_path(model_path)}"')
    gui_parts.append(script)
    if output_hm_path:
        gui_parts.append(f'*writefile "{quote_tcl_path(output_hm_path)}" 1')

    gui_script = "\n".join(gui_parts)

    # Send to GUI
    return send_tcl_to_gui(gui_script, host, port, timeout)
