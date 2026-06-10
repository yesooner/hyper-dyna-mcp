"""HyperMesh GUI listener mode — socket-based interactive execution.

Adapted from times1234/hypermesh-mcp execute_tcl_gui pattern.
Communicates with a running HyperMesh GUI via TCP socket 127.0.0.1:47883.

Usage:
  1. Open HyperMesh GUI manually
  2. In HyperMesh's Tcl console, source the listener script:
     source "C:/path/to/hyper-dyna-mcp/runs/hm_gui_listener.tcl"
  3. Or launch HyperMesh with the listener:
     hmbatch.exe -tcl hm_gui_listener.tcl
  4. Then call execute_tcl_gui() from MCP tools
"""

from __future__ import annotations

import os
import csv
import re
import socket
import subprocess
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
from program.tools.hm_dictionary import validate_cardimage_in_script, validate_dataname_in_script
from program.tools.path_tools import load_yaml

# --- Command whitelist (safe mode) ---
# Commands that are allowed in safe mode.
_ALLOWED_CMD_RE = re.compile(
    r'(?m)^\s*(\*?\w+)',
)

_WHITELIST_PREFIXES = (
    '*createentity', '*setvalue', '*createmark', '*clearmark',
    '*readfile', '*writefile',
    '*currentcollector', '*collectorcreateonly', '*createmarkpanel',
    '*createlist', '*createelement',
    '*translatemark', '*duplicatemark', '*equivalence', '*findedges',
    '*createnode', '*linecreatestraight', '*nodecreate', '*linecreate',
    '*surfacecreate', '*solidblock', '*solidcreateruled', '*solidmap', '*surfacecreateruled',
    '*tetmesh', '*tet10mesh', '*boolean_merge_solids', '*trim_solids_by_surfaces',
    '*element', '*componentcreate', '*merge', '*renumber',
    'hm_getvalue', 'hm_entitylist', 'hm_marklength', 'hm_getmark',
    'hm_entityinfo', 'hm_nodevalue', 'hm_getentityvalue',
    'puts', 'set', 'if', 'else', 'elseif', 'for', 'foreach', 'while', 'proc',
    'catch', 'expr', 'list', 'lindex', 'llength', 'lappend',
    'string', 'format', 'scan', 'regexp', 'regsub',
    'after', 'update', 'incr', 'append', 'break', 'continue',
    'return', 'error', 'unset',
)

# Commands that are always blocked (destructive or non-productive).
_BLOCKED_CMD_RE = re.compile(
    r'(?m)^\s*\*('
    r'solidrc|solidcone|solidtorus|solidspherefull|'
    r'solidmesh\b|solidmeshwithsurfaces|solidmesh9lines|solidmesh12lines|'
    r'createsolidsfromshells|deletesolidswithelems|splitsolidelements|'
    r'deletemodel|deleteentity|deleteentities|clearmodel'
    r')',
    re.IGNORECASE,
)

# Dangerous Tcl commands.
_DANGEROUS_CMD_RE = re.compile(
    r'(?m)^\s*(source|exec|open|file\s+delete|file\s+rename|cd|pwd|exit)',
    re.IGNORECASE,
)


def _check_forbidden(script: str) -> str | None:
    """Check script against blocked commands. Returns error or None."""
    m = _BLOCKED_CMD_RE.search(script)
    if m:
        cmd = m.group(1)
        return (
            f"Blocked command: *{cmd}. "
            "This command is not productive for LS-DYNA modeling. "
            "Use hm_set_keyword for keyword cards, hm_create_box for geometry."
        )

    m = _DANGEROUS_CMD_RE.search(script)
    if m:
        cmd = m.group(1)
        return (
            f"Blocked dangerous command: {cmd}. "
            "File system and process commands are not allowed."
        )

    return None


def _check_whitelist(script: str) -> str | None:
    """Check if all commands in script are whitelisted. Returns error or None."""
    for line in script.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Extract first token
        m = re.match(r'^(\*?\w+)', line)
        if not m:
            continue
        cmd = m.group(1).lower()
        # Check whitelist
        if any(cmd.startswith(p.lower()) for p in _WHITELIST_PREFIXES):
            continue
        # Allow variable assignments and control flow
        if "=" in line.split()[0] if line.split() else False:
            continue
        return (
            f"Command not in safe-mode whitelist: '{cmd}'. "
            "Use hm_set_keyword for keyword cards, or call execute_tcl_gui with mode='raw'."
        )
    return None


def _listener_response_error(response: str) -> str | None:
    """Detect HyperMesh-side errors that can be printed without a Tcl error code."""
    for marker in ("UNKNOWN CMD:", "BGERROR:", "HDM ERROR:", "Listener fatal error:"):
        if marker in response:
            return f"HyperMesh listener reported {marker}"
    return None


def parse_listener_ping_response(response: str) -> dict[str, str]:
    """Parse metadata emitted by the HyperMesh Tcl listener ping response."""
    info: dict[str, str] = {}
    for line in response.splitlines():
        line = line.strip()
        if line == "HYPERMESH_MCP_PONG":
            info["pong"] = "true"
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        info[key.strip().lower()] = value.strip()
    return info


def _tcl_path(path: str | Path) -> str:
    """Return a Tcl-friendly path string for HyperMesh on Windows."""
    return Path(path).as_posix()


def _tcl_source_command(path: str | Path) -> str:
    """Build a HyperMesh Tcl Console source command with stable path slashes."""
    return f'source "{_tcl_path(path)}"'


def _tcl_start_or_source_command(port: int, path: str | Path) -> str:
    """Build a Tcl Console command that prefers hmcustom.tcl's verified starter."""
    source_command = _tcl_source_command(path)
    return (
        f"if {{[llength [info commands mcp_start_on_port]]}} "
        f"{{mcp_start_on_port {int(port)}}} else {{{source_command}}}"
    )


def diagnose_listener_port(
    host: str = "127.0.0.1",
    port: int | None = None,
    timeout: int = 3,
    include_alternate: bool = True,
) -> dict:
    """Diagnose the configured HyperMesh listener socket without side effects."""
    if port is None:
        port = current_gui_port()
    suggested_port = find_free_listener_port(start=int(port) + 1) if include_alternate else None
    listener_tcl = ensure_listener_tcl_for_port(int(port), host=host)
    alternate_listener_tcl = (
        ensure_listener_tcl_for_port(int(suggested_port), host=host)
        if include_alternate and suggested_port else None
    )
    ping = _raw_listener_ping(host, int(port), timeout=max(1, int(timeout)))
    owners = _netstat_port_owners(int(port))
    diagnosis = _listener_diagnosis(ping, owners)
    port_owner_summary = _port_owner_summary(owners)
    start_or_source_command = _tcl_start_or_source_command(int(port), listener_tcl)
    alternate_start_or_source_command = (
        _tcl_start_or_source_command(int(suggested_port), alternate_listener_tcl)
        if alternate_listener_tcl and suggested_port else None
    )
    return {
        "success": bool(ping.get("connected") and ping.get("listener_pong")),
        "host": host,
        "port": int(port),
        "suggested_free_port": suggested_port,
        "alternate_listener_included": bool(alternate_listener_tcl),
        "ping": ping,
        "diagnosis": diagnosis,
        "port_owners": owners,
        "port_owner_summary": port_owner_summary,
        "expected_listener_version": LISTENER_VERSION,
        "source_command": _tcl_source_command(listener_tcl),
        "start_or_source_command": start_or_source_command,
        "alternate_port_command": (
            _tcl_source_command(alternate_listener_tcl) if alternate_listener_tcl else None
        ),
        "alternate_start_or_source_command": alternate_start_or_source_command,
        "recovery_steps": [
            "In HyperMesh Tcl Console, run: mcp_stop",
            f"In HyperMesh Tcl Console, run: {start_or_source_command}",
            (
                f"If the same port still times out, run: {alternate_start_or_source_command}"
                if alternate_start_or_source_command else
                "If the same port still times out, set ::mcp_hm_port to a free port and source the listener."
            ),
        ],
    }


def _listener_diagnosis(ping: dict, port_owners: list[dict[str, str]]) -> dict[str, str]:
    """Classify listener state into stable reason/action fields for agents."""
    error = str(ping.get("error") or "")
    connected = bool(ping.get("connected"))
    pong = bool(ping.get("listener_pong"))
    version = ping.get("listener_version")
    owner_names = [
        str(item.get("process_name") or item.get("pid") or "")
        for item in port_owners
        if isinstance(item, dict)
    ]
    owner_text = ", ".join(name for name in owner_names if name)

    if connected and pong and version == LISTENER_VERSION:
        return {
            "reason": "listener_ready",
            "action": "Run connected GUI modeling smoke.",
            "detail": f"Listener returned HYPERMESH_MCP_PONG with version {LISTENER_VERSION}.",
        }
    if connected and pong and version != LISTENER_VERSION:
        return {
            "reason": "listener_version_mismatch",
            "action": "Run mcp_stop, then source the generated listener for the expected version.",
            "detail": f"Current listener version is {version or 'unknown'}; expected {LISTENER_VERSION}.",
        }
    if "connection_refused" in error:
        return {
            "reason": "listener_not_running",
            "action": "Source the generated listener Tcl in the HyperMesh Tcl Console.",
            "detail": "No process accepted the listener connection on the configured port.",
        }
    if "socket_timeout" in error and connected:
        detail = "A TCP endpoint accepted the connection but did not return HYPERMESH_MCP_PONG."
        if owner_text:
            detail += f" Port owner: {owner_text}."
        return {
            "reason": "port_occupied_without_pong",
            "action": "Run mcp_stop in HyperMesh, or start the listener on a different free port.",
            "detail": detail,
        }
    if "socket_error" in error:
        return {
            "reason": "socket_error",
            "action": "Check local firewall, port ownership, and HyperMesh listener state before retrying.",
            "detail": error,
        }
    if connected and not pong:
        return {
            "reason": "non_mcp_endpoint",
            "action": "Use mcp_stop or a different port, then source the generated listener.",
            "detail": "The endpoint responded without the expected HYPERMESH_MCP_PONG marker.",
        }
    return {
        "reason": "unknown_listener_state",
        "action": "Inspect ping, port_owners, and recovery_steps.",
        "detail": error or "No diagnostic error was reported.",
    }


def _port_owner_summary(port_owners: list[dict[str, str]]) -> list[str]:
    """Return compact, agent-readable port owner descriptions."""
    summary: list[str] = []
    for item in port_owners:
        if not isinstance(item, dict):
            continue
        if item.get("error"):
            summary.append(str(item["error"]))
            continue
        pid = str(item.get("pid") or "")
        process_name = str(item.get("process_name") or "unknown")
        state = str(item.get("state") or "")
        local_address = str(item.get("local_address") or "")
        parts = []
        if process_name:
            parts.append(process_name)
        if pid:
            parts.append(f"pid={pid}")
        if state:
            parts.append(f"state={state}")
        if local_address:
            parts.append(f"local={local_address}")
        if parts:
            summary.append(" ".join(parts))
    return summary


def find_free_listener_port(
    host: str = "127.0.0.1",
    start: int = 47884,
    stop: int = 47950,
) -> int | None:
    """Find a free local TCP port suitable for a HyperMesh listener."""
    for candidate in range(max(1024, int(start)), min(65535, int(stop)) + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, candidate))
            except OSError:
                continue
            return candidate
    return None


def _raw_listener_ping(host: str, port: int, timeout: int) -> dict:
    """Ping the socket directly, bypassing safe-mode validation and retries."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(b"__HDM_PING__")
            sock.shutdown(socket.SHUT_WR)
            chunks: list[bytes] = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
        response = b"".join(chunks).decode("utf-8", errors="replace")
        info = parse_listener_ping_response(response)
        return {
            "connected": True,
            "listener_pong": info.get("pong") == "true",
            "listener_version": info.get("listener_version"),
            "response": response,
            "error": None,
        }
    except ConnectionRefusedError as exc:
        return {
            "connected": False,
            "listener_pong": False,
            "listener_version": None,
            "response": "",
            "error": f"connection_refused: {exc}",
        }
    except socket.timeout as exc:
        return {
            "connected": True,
            "listener_pong": False,
            "listener_version": None,
            "response": "",
            "error": f"socket_timeout: {exc}",
        }
    except OSError as exc:
        return {
            "connected": False,
            "listener_pong": False,
            "listener_version": None,
            "response": "",
            "error": f"socket_error: {exc}",
        }


def _netstat_port_owners(port: int) -> list[dict[str, str]]:
    """Return Windows netstat rows for the local listener port."""
    try:
        proc = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"],
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        return [{"error": f"{type(exc).__name__}: {exc}"}]

    owners: list[dict[str, str]] = []
    needle_v4 = f"127.0.0.1:{port}"
    needle_any = f"0.0.0.0:{port}"
    output = proc.stdout.decode("mbcs", errors="replace") if isinstance(proc.stdout, bytes) else str(proc.stdout or "")
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0].upper() != "TCP":
            continue
        local_addr = parts[1]
        if local_addr not in {needle_v4, needle_any}:
            continue
        owners.append(
            {
                "protocol": parts[0],
                "local_address": parts[1],
                "remote_address": parts[2],
                "state": parts[3],
                "pid": parts[4],
                "process_name": _process_name_for_pid(parts[4]),
            }
        )
    return owners


def _process_name_for_pid(pid: str) -> str | None:
    try:
        proc = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return None
    output = proc.stdout.decode("mbcs", errors="replace") if isinstance(proc.stdout, bytes) else str(proc.stdout or "")
    line = output.strip().splitlines()[0] if output.strip() else ""
    if not line or "INFO:" in line.upper():
        return None
    try:
        return next(csv.reader([line]))[0]
    except Exception:
        return None
from program.transport_manager import (
    configure_endpoint,
    get_state,
    start_heartbeat,
    TransportState,
)

DEFAULT_GUI_HOST = "127.0.0.1"


def _configured_gui_port() -> int:
    """Resolve GUI listener port from env first, then path/hypermesh_paths.yaml."""
    env_port = os.environ.get("HDM_GUI_PORT")
    if env_port:
        return int(env_port)
    try:
        hm_cfg = load_yaml("hypermesh_paths").get("hypermesh", {})
        return int(hm_cfg.get("gui_port", 47883))
    except Exception:
        return 47883


DEFAULT_GUI_PORT = _configured_gui_port()
_RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"
LISTENER_VERSION = "2024-compat-v3"


def current_gui_port() -> int:
    """Return the current configured GUI listener port."""
    return _configured_gui_port()


def listener_filename_for_port(port: int) -> str:
    """Return the generated listener filename for a configured GUI port."""
    port = int(port)
    default_port = _configured_gui_port_from_file()
    return "hm_gui_listener.tcl" if port == default_port else f"hm_gui_listener_{port}.tcl"


def ensure_listener_tcl_for_port(port: int, host: str = DEFAULT_GUI_HOST) -> Path:
    """Write and return the listener Tcl path for a specific GUI port."""
    return save_listener_tcl(
        host=host,
        port=int(port),
        filename=listener_filename_for_port(int(port)),
    )


def configure_gui_port(port: int) -> dict:
    """Set the GUI listener port for the current MCP process and write Tcl."""
    port = int(port)
    if port < 1024 or port > 65535:
        return {"success": False, "error": "port must be between 1024 and 65535"}
    os.environ["HDM_GUI_PORT"] = str(port)
    path = ensure_listener_tcl_for_port(port)
    configure_endpoint(DEFAULT_GUI_HOST, port)
    source_command = _tcl_source_command(path)
    start_or_source_command = _tcl_start_or_source_command(port, path)
    return {
        "success": True,
        "host": DEFAULT_GUI_HOST,
        "port": port,
        "listener_tcl": str(path),
        "source_command": source_command,
        "start_or_source_command": start_or_source_command,
        "hypermesh_command": start_or_source_command,
        "next_hypermesh_commands": [
            "catch {mcp_stop}",
            start_or_source_command,
        ],
        "note": "This updates the current MCP process only. Persist the port in path/hypermesh_paths.yaml if needed.",
    }


def _configured_gui_port_from_file() -> int:
    """Resolve the YAML/default listener port without considering HDM_GUI_PORT."""
    try:
        hm_cfg = load_yaml("hypermesh_paths").get("hypermesh", {})
        return int(hm_cfg.get("gui_port", 47883))
    except Exception:
        return 47883


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
# Listener version: {LISTENER_VERSION}
# Source this file inside a visible HyperMesh session
set ::mcp_hm_listener_version "{LISTENER_VERSION}"
if {{![info exists ::mcp_hm_host]}} {{
    set ::mcp_hm_host "{host}"
}}
# Force the generated project port so stale Tcl session variables cannot
# override path/hypermesh_paths.yaml.
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

proc ::mcp_hm_channels {{}} {{
    if {{[catch {{set names [chan names]}}]}} {{
        if {{[catch {{set names [file channels]}}]}} {{
            return {{}}
        }}
    }}
    return $names
}}

proc ::mcp_hm_errorinfo {{options}} {{
    if {{[catch {{set info [dict get $options -errorinfo]}}] == 0}} {{
        return $info
    }}
    if {{[info exists ::errorInfo]}} {{
        return $::errorInfo
    }}
    return ""
}}

proc ::mcp_hm_configure_socket {{chan}} {{
    catch {{fconfigure $chan -blocking 0}}
    catch {{fconfigure $chan -buffering none}}
    catch {{fconfigure $chan -translation binary}}
    # HyperMesh 2024 Tcl builds may reject -encoding on binary sockets.
    catch {{fconfigure $chan -encoding utf-8}}
}}

proc ::mcp_hm_read_request {{chan}} {{
    set script ""
    set deadline [expr {{[clock milliseconds] + 3000}}]
    set quiet_deadline 0
    while {{[clock milliseconds] < $deadline}} {{
        set chunk ""
        if {{![catch {{set chunk [read $chan]}}] && $chunk ne ""}} {{
            append script $chunk
            set quiet_deadline [expr {{[clock milliseconds] + 250}}]
        }}
        if {{[catch {{eof $chan}} _mcp_eof]}} {{
            break
        }}
        if {{$_mcp_eof}} {{
            break
        }}
        if {{$script ne "" && $quiet_deadline > 0 && [clock milliseconds] >= $quiet_deadline}} {{
            break
        }}
        update
        after 20
    }}
    return $script
}}

proc ::mcp_hm_close_port {{port}} {{
    set closed 0
    if {{[info exists ::mcp_hm_server]}} {{
        catch {{close $::mcp_hm_server}}
        unset -nocomplain ::mcp_hm_server
        incr closed
    }}
    foreach ch [::mcp_hm_channels] {{
        set sockname ""
        if {{[catch {{set sockname [fconfigure $ch -sockname]}}]}} {{
            continue
        }}
        if {{[llength $sockname] >= 3 && [lindex $sockname 2] == $port}} {{
            catch {{close $ch}}
            incr closed
        }}
    }}
    return $closed
}}

proc ::mcp_hm_accept {{chan addr client_port}} {{
    set fatal [catch {{
        ::mcp_hm_configure_socket $chan
        set script [::mcp_hm_read_request $chan]

        if {{[string trim $script] eq ""}} {{
            puts $chan "ERROR: empty script"
            flush $chan
            close $chan
            return
        }}

        if {{[string trim $script] eq "__HDM_PING__"}} {{
            puts $chan "OK"
            puts $chan "HYPERMESH_MCP_PONG"
            puts $chan "LISTENER_VERSION=$::mcp_hm_listener_version"
            catch {{puts $chan "TCL_VERSION=[info tclversion]"}}
            catch {{puts $chan "TCL_PATCHLEVEL=[info patchlevel]"}}
            flush $chan
            close $chan
            return
        }}

        # Hook puts to capture script output.
        set ::mcp_capture ""
        proc ::mcp_hm_capture_puts {{args}} {{
            append ::mcp_capture [join $args " "] "\\n"
        }}
        if {{[llength [info commands puts]] > 0}} {{
            catch {{rename puts ::_mcp_base_puts}}
        }}
        rename ::mcp_hm_capture_puts puts

        set code [catch {{uplevel #0 $script}} result options]

        # Restore puts before writing to the socket.
        catch {{rename puts ""}}
        catch {{rename ::_mcp_base_puts puts}}

        # HyperMesh commands often return non-zero (e.g. *setvalue returns 1).
        # Only treat as error if result contains error keywords.
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
            set _mcp_errorinfo [::mcp_hm_errorinfo $options]
            if {{$_mcp_errorinfo ne ""}} {{
                puts $chan $_mcp_errorinfo
            }}
        }} else {{
            puts $chan "OK"
            if {{$::mcp_capture ne ""}} {{ puts $chan $::mcp_capture }}
            if {{$result ne ""}} {{ puts $chan $result }}
        }}
        flush $chan
        close $chan
    }} fatal_msg fatal_options]

    if {{$fatal}} {{
        ::mcp_hm_restore_puts
        catch {{puts $chan "ERROR"}}
        catch {{puts $chan "Listener fatal error: $fatal_msg"}}
        set _mcp_fatal_errorinfo [::mcp_hm_errorinfo $fatal_options]
        if {{$_mcp_fatal_errorinfo ne ""}} {{
            catch {{puts $chan $_mcp_fatal_errorinfo}}
        }}
        catch {{flush $chan}}
        catch {{close $chan}}
    }}
}}

set _mcp_closed [::mcp_hm_close_port $::mcp_hm_port]
if {{$_mcp_closed > 0}} {{
    after 300
}}
if {{[catch {{
    set ::mcp_hm_server [socket -server ::mcp_hm_accept -myaddr $::mcp_hm_host $::mcp_hm_port]
}} _mcp_bind_err]}} {{
    set _mcp_closed [::mcp_hm_close_port $::mcp_hm_port]
    if {{$_mcp_closed > 0}} {{ after 300 }}
    if {{[catch {{
        set ::mcp_hm_server [socket -server ::mcp_hm_accept -myaddr $::mcp_hm_host $::mcp_hm_port]
    }} _mcp_bind_err2]}} {{
        error "Cannot start HyperMesh MCP listener on $::mcp_hm_host:$::mcp_hm_port: $_mcp_bind_err2. Run mcp_stop, or generate and source runs/hm_gui_listener_<free_port>.tcl for another port."
    }}
}}
puts "Dyna-mcp GUI listener ready on $::mcp_hm_host:$::mcp_hm_port"
"""


def save_listener_tcl(
    host: str = DEFAULT_GUI_HOST,
    port: int | None = None,
    filename: str = "hm_gui_listener.tcl",
) -> Path:
    """Generate and save the listener Tcl to runs/ directory."""
    if port is None:
        port = current_gui_port()
    _RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = _RUNS_DIR / filename
    path.write_text(generate_listener_tcl(host, port), encoding="utf-8")
    logger.info(f"Saved GUI listener Tcl: {path}")
    return path


# --- Socket client ---


def send_tcl_to_gui(
    script: str,
    host: str = DEFAULT_GUI_HOST,
    port: int | None = None,
    timeout: int = 120,
    mode: str = "safe",
) -> dict:
    """Send a Tcl script to the HyperMesh GUI listener via TCP socket.

    Args:
        script: Tcl script to execute in HyperMesh GUI.
        host: Listener host (default 127.0.0.1).
        port: Listener port (default 47883).
        timeout: Socket timeout in seconds.
        mode: "safe" (default) enforces whitelist + dictionary validation.
              "raw" skips whitelist + dictionary validation, but still blocks
              destructive commands.

    Returns:
        dict with success, response, etc.
    """
    if not script.strip():
        return {"success": False, "error": "Empty script"}
    if port is None:
        port = current_gui_port()

    # Always block destructive commands
    forbidden = _check_forbidden(script)
    if forbidden:
        return {
            "success": False,
            "error": forbidden,
            "error_type": "blocked_command",
            "retry_allowed": False,
            "required_tool": "hm_set_keyword or hm_create_box",
        }

    # Safe mode: whitelist + dictionary validation
    if mode == "safe":
        whitelist_err = _check_whitelist(script)
        if whitelist_err:
            return {
                "success": False,
                "error": whitelist_err,
                "error_type": "not_in_whitelist",
                "retry_allowed": False,
                "required_tool": "hm_set_keyword",
            }

        cardimage_err = validate_cardimage_in_script(script)
        if cardimage_err:
            return {
                "success": False,
                "error": cardimage_err,
                "error_type": "invalid_cardimage",
                "retry_allowed": False,
                "required_tool": "hm_set_keyword",
            }

        dataname_err = validate_dataname_in_script(script)
        if dataname_err:
            return {
                "success": False,
                "error": dataname_err,
                "error_type": "invalid_dataname",
                "retry_allowed": False,
                "required_tool": "hm_set_keyword",
            }

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
        listener_error = _listener_response_error(response)
        if listener_error:
            return {
                "success": False,
                "host": host,
                "port": int(port),
                "response": response,
                "error": listener_error,
                "error_type": "listener_error",
            }
        return {
            "success": response.startswith("OK"),
            "host": host,
            "port": int(port),
            "response": response,
        }

    except ConnectionRefusedError:
        listener_tcl = ensure_listener_tcl_for_port(int(port), host=host)
        source_command = _tcl_source_command(listener_tcl)
        start_or_source_command = _tcl_start_or_source_command(int(port), listener_tcl)
        return {
            "success": False,
            "error": (
                f"Connection refused on {host}:{port}. "
                "Make sure HyperMesh GUI is open and the listener is sourced. "
                f"Run: {start_or_source_command}"
            ),
            "error_type": "connection_refused",
            "retry_allowed": False,
            "required_action": "source_listener",
            "source_command": source_command,
            "start_or_source_command": start_or_source_command,
            "next_hypermesh_commands": [
                "catch {mcp_stop}",
                start_or_source_command,
            ],
        }
    except socket.timeout:
        listener_tcl = ensure_listener_tcl_for_port(int(port), host=host)
        source_command = _tcl_source_command(listener_tcl)
        start_or_source_command = _tcl_start_or_source_command(int(port), listener_tcl)
        return {
            "success": False,
            "error": (
                f"Socket timeout on {host}:{port}. A process accepted the TCP connection "
                "but did not return a HyperMesh listener response. Re-source the listener "
                f"in the current HyperMesh Tcl Console: {start_or_source_command}"
            ),
            "error_type": "socket_timeout",
            "retry_allowed": False,
            "required_action": "source_listener",
            "source_command": source_command,
            "start_or_source_command": start_or_source_command,
            "next_hypermesh_commands": [
                "catch {mcp_stop}",
                start_or_source_command,
            ],
        }
    except OSError as exc:
        return {"success": False, "error": f"Socket error: {exc}", "error_type": "socket_error"}


# --- Model info query ---


def query_model_info(host: str = DEFAULT_GUI_HOST, port: int | None = None) -> dict:
    """Query current model info from HyperMesh GUI.

    Returns model name, component count/names, node/element counts.
    """
    if port is None:
        port = current_gui_port()
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


def _candidate_lsdyna_templates() -> list[str]:
    """Build LS-DYNA template candidates from path/hypermesh_paths.yaml."""
    try:
        hm_cfg = load_yaml("hypermesh_paths").get("hypermesh", {})
    except Exception:
        hm_cfg = {}

    explicit = hm_cfg.get("lsdyna_template") or hm_cfg.get("lsdyna_template_file")
    candidates: list[str] = []
    if explicit:
        candidates.append(str(explicit))

    install_dir = hm_cfg.get("install_dir")
    if install_dir:
        root = Path(str(install_dir))
        candidates.extend(
            str(path)
            for path in [
                root / "hm" / "templates" / "feoutput" / "lsdyna" / "lsdyna.key",
                root / "hm" / "templates" / "feoutput" / "lsdyna" / "lsyna.key",
                root / "hm" / "templates" / "feoutput" / "ls-dyna.key",
                root / "hm" / "templates" / "feoutput" / "lsdyna.key",
                root / "templates" / "feoutput" / "ls-dyna971" / "dyna.key",
                root / "templates" / "feoutput" / "lsdyna" / "lsdyna.key",
            ]
        )

    return list(dict.fromkeys(candidates))


def activate_lsdyne_template(host: str = DEFAULT_GUI_HOST, port: int | None = None, timeout: int = 15) -> dict:
    """Activate LS-DYNA solver template in HyperMesh.

    Must be called before any LS-DYNA card image operations.
    Uses *templatefileset to load the HyperMesh LS-DYNA template.
    """
    if port is None:
        port = current_gui_port()
    template_paths = _candidate_lsdyna_templates()
    if not template_paths:
        return {
            "success": False,
            "response": "",
            "error": "No HyperMesh LS-DYNA template candidates configured in path/hypermesh_paths.yaml",
        }

    tcl_candidates = " ".join(f'"{quote_tcl_path(path)}"' for path in template_paths)
    script = "\n".join(
        [
            'set template_path ""',
            f"foreach candidate {{{tcl_candidates}}} {{",
            "    if {[file exists $candidate]} {",
            "        set template_path $candidate",
            "        break",
            "    }",
            "}",
            'if {$template_path eq ""} {',
            f'    error "LS-DYNA template not found. Checked: {tcl_candidates}"',
            "}",
            "set code [catch {*templatefileset $template_path} err]",
            'puts "TEMPLATE_RESULT=$code"',
            'puts "TEMPLATE_PATH=$template_path"',
            'puts "TEMPLATE_MESSAGE=$err"',
            'catch {puts "SOLVER=[hm_getsolver]"}',
            'catch {puts "TEMPLATE_TYPE=[hm_info templatetype]"}',
        ]
    )
    result = send_tcl_to_gui(script, host=host, port=port, timeout=timeout)
    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
        "error": result.get("error"),
        "candidates": template_paths,
    }


# --- High-level API ---


def execute_tcl_gui(
    script: str,
    model_path: str | None = None,
    output_hm_path: str | None = None,
    host: str = DEFAULT_GUI_HOST,
    port: int | None = None,
    timeout: int = 120,
    enforce_rules: bool = True,
    mode: str = "safe",
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
        mode: "safe" (default) enforces whitelist + dictionary validation.
              "raw" skips whitelist + dictionary validation, but still blocks
              destructive commands.

    Returns:
        Unified dict: success, command_id, transport, fallback_used,
        retry_count, response, error_type, message.
        Backward-compatible: always has ``success`` and ``response``.
    """
    if port is None:
        port = current_gui_port()

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

    # Safe mode validation (before building GUI script)
    if mode == "safe":
        forbidden = _check_forbidden(script)
        if forbidden:
            return {"success": False, "error": forbidden, "error_type": "blocked_command",
                    "retry_allowed": False, "required_tool": "hm_set_keyword or hm_create_box"}

        whitelist_err = _check_whitelist(script)
        if whitelist_err:
            return {"success": False, "error": whitelist_err, "error_type": "not_in_whitelist",
                    "retry_allowed": False, "required_tool": "hm_set_keyword"}

        cardimage_err = validate_cardimage_in_script(script)
        if cardimage_err:
            return {"success": False, "error": cardimage_err, "error_type": "invalid_cardimage",
                    "retry_allowed": False, "required_tool": "hm_set_keyword"}

        dataname_err = validate_dataname_in_script(script)
        if dataname_err:
            return {"success": False, "error": dataname_err, "error_type": "invalid_dataname",
                    "retry_allowed": False, "required_tool": "hm_set_keyword"}

    # Build GUI script with optional readfile/writefile
    gui_parts: list[str] = []
    if model_path:
        gui_parts.append(f'*readfile "{quote_tcl_path(model_path)}"')
    gui_parts.append(script)
    if output_hm_path:
        gui_parts.append(f'*writefile "{quote_tcl_path(output_hm_path)}" 1')

    gui_script = "\n".join(gui_parts)

    # Ensure heartbeat is running
    configure_endpoint(host, port)
    start_heartbeat()

    state = get_state()

    if state.should_use_socket():
        return _execute_via_socket(gui_script, state, host, port, timeout, mode)
    else:
        return _execute_via_ipc(gui_script, state, timeout, mode=mode)


def _execute_via_socket(
    gui_script: str,
    state: TransportState,
    host: str,
    port: int,
    timeout: int,
    mode: str,
) -> dict:
    """Try socket transport with up to 3 retries; fallback to IPC on failure."""
    max_retries = 3
    for attempt in range(max_retries):
        result = send_tcl_to_gui(gui_script, host, port, timeout, mode=mode)

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
    return _execute_via_ipc(gui_script, state, timeout, fallback_used=True, mode=mode)


def _execute_via_ipc(
    gui_script: str,
    state: TransportState,
    timeout: int,
    fallback_used: bool = False,
    mode: str = "safe",
) -> dict:
    """Execute via IPC file-queue (plugin_loop submit_command + wait_result)."""
    from program.plugin_loop import submit_command, wait_result

    cmd_id = submit_command("execute_tcl", script=gui_script, timeout=timeout, mode=mode)
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
