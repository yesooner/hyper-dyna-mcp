"""LS-PrePost GUI interaction via file-queue IPC.

Adapted from ANSYS-Workbench-mcp file-queue pattern.
MCP server writes JSON commands → LS-PrePost bridge journal polls → executes → writes results.

Usage:
  1. start_lsprepost_bridge() → 生成 runs/lsprepost_bridge.cfile
  2. 手动启动: lsprepost4.13 cfile=runs/lsprepost_bridge.cfile
  3. lsprepost_command(action="open_d3plot", path="model.d3plot") → 发送命令
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

_RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"
_COMMANDS_DIR = _RUNS_DIR / "lsprepost_commands"
_RESULTS_DIR = _RUNS_DIR / "lsprepost_results"


def _ensure_dirs() -> tuple[Path, Path]:
    _COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return _COMMANDS_DIR, _RESULTS_DIR


# --- Supported actions ---

SUPPORTED_ACTIONS = {
    # File operations
    "open_d3plot": "Open a d3plot results file",
    "open_key": "Open a keyword (.k) file",
    "open_ascii": "Open an ASCII output file",
    # View control
    "view": "Set viewport (front, top, iso, right, left, back, bottom)",
    "zoom_fit": "Zoom to fit all",
    "zoom_reset": "Reset zoom",
    # Plot commands
    "plot_undeformed": "Show undeformed shape",
    "plot_deformed": "Show deformed shape",
    "plot_stress": "Show von Mises stress contour",
    "plot_strain": "Show effective plastic strain contour",
    "plot_energy": "Show energy time history plot",
    "plot_velocity": "Show velocity vector plot",
    "plot_displacement": "Show displacement contour",
    # Export
    "export_png": "Export viewport as PNG image",
    "export_stl": "Export mesh as STL",
    "export_key": "Export model as keyword file",
    # Query
    "query_state": "Query current model state (loaded file, frame, etc.)",
    # Execution
    "tcl": "Execute arbitrary Tcl script",
    "exit": "Close the bridge and exit",
}


# --- Bridge journal generator ---


def generate_bridge_journal(
    poll_interval: float = 1.0,
    commands_dir: str | Path | None = None,
    results_dir: str | Path | None = None,
) -> str:
    """Generate an LS-PrePost cfile that acts as a command bridge.

    The bridge polls commands/ for .json files, executes them, writes results/.
    """
    cmd_dir = str(commands_dir or _COMMANDS_DIR).replace("\\", "/")
    res_dir = str(results_dir or _RESULTS_DIR).replace("\\", "/")

    return f"""# Dyna-mcp LS-PrePost bridge journal
# Launch: lsprepost4.13 cfile=this_file.cfile

set ::mcp_cmd_dir "{cmd_dir}"
set ::mcp_res_dir "{res_dir}"
set ::mcp_poll_ms {int(poll_interval * 1000)}
set ::mcp_running 1

proc ::mcp_bridge_poll {{}} {{
    if {{!$::mcp_running}} return

    set files [glob -nocomplain "$::mcp_cmd_dir/*.json"]
    foreach f $files {{
        if {{![file exists $f]}} continue

        set fp [open $f r]
        set data [read $fp]
        close $fp

        set basename [file tail $f]
        set res_file "$::mcp_res_dir/$basename"
        if {{[file exists $res_file]}} continue

        set action [dict get $data action]
        set result ""
        set success 1

        # --- File operations ---
        if {{$action eq "open_d3plot"}} {{
            set path [dict get $data path]
            catch {{d3plot $path}} err
            set result "opened $path"
        }} elseif {{$action eq "open_key"}} {{
            set path [dict get $data path]
            catch {{keyword $path}} err
            set result "opened $path"
        }} elseif {{$action eq "open_ascii"}} {{
            set path [dict get $data path]
            catch {{ascii $path}} err
            set result "opened $path"

        # --- View control ---
        }} elseif {{$action eq "view"}} {{
            set view [dict get $data view]
            catch {{$view}} err
            set result "view: $view"
        }} elseif {{$action eq "zoom_fit"}} {{
            catch {{zoom fit}} err
            set result "zoom fit"
        }} elseif {{$action eq "zoom_reset"}} {{
            catch {{zoom reset}} err
            set result "zoom reset"

        # --- Plot commands ---
        }} elseif {{$action eq "plot_undeformed"}} {{
            catch {{plot undeform all 1}} err
            set result "undeformed plot"
        }} elseif {{$action eq "plot_deformed"}} {{
            set scale [dict get $data scale 1.0]
            catch {{plot deformed all 1 $scale}} err
            set result "deformed plot (scale=$scale)"
        }} elseif {{$action eq "plot_stress"}} {{
            catch {{
                result 1
                fringe stress
                plot fringe all 1
            }} err
            set result "stress contour"
        }} elseif {{$action eq "plot_strain"}} {{
            catch {{
                result 1
                fringe塑性应变
                plot fringe all 1
            }} err
            set result "strain contour"
        }} elseif {{$action eq "plot_energy"}} {{
            catch {{xypLOT energy}} err
            set result "energy plot"
        }} elseif {{$action eq "plot_velocity"}} {{
            catch {{
                result 1
                vector velocity
                plot vector all 1
            }} err
            set result "velocity plot"
        }} elseif {{$action eq "plot_displacement"}} {{
            catch {{
                result 1
                fringe displacement
                plot fringe all 1
            }} err
            set result "displacement contour"

        # --- Export ---
        }} elseif {{$action eq "export_png"}} {{
            set path [dict get $data path]
            set w [dict get $data width 1920]
            set h [dict get $data height 1080]
            catch {{
                screen width $w
                screen height $h
                capture $path
            }} err
            set result "exported: $path"
        }} elseif {{$action eq "export_stl"}} {{
            set path [dict get $data path]
            catch {{stl write $path}} err
            set result "exported STL: $path"
        }} elseif {{$action eq "export_key"}} {{
            set path [dict get $data path]
            catch {{keyword write $path}} err
            set result "exported keyword: $path"

        # --- Query ---
        }} elseif {{$action eq "query_state"}} {{
            set loaded ""
            catch {{set loaded [d3post getinfo]}} err
            set result "state: $loaded"

        # --- Execution ---
        }} elseif {{$action eq "tcl"}} {{
            set script [dict get $data script]
            set code [catch {{uplevel #0 $script}} res]
            set result $res
            set success [expr {{$code == 0}}]
        }} elseif {{$action eq "exit"}} {{
            set ::mcp_running 0
            set fp [open $res_file w]
            puts $fp "{{\\"success\\": 1, \\"action\\": \\"exit\\"}}"
            close $fp
            return
        }} else {{
            set result "unknown action: $action"
            set success 0
        }}

        # Write result
        set fp [open $res_file w]
        puts $fp "{{\\"success\\": $success, \\"action\\": \\"$action\\", \\"result\\": \\"$result\\"}}"
        close $fp
    }}

    if {{$::mcp_running}} {{
        after $::mcp_poll_ms ::mcp_bridge_poll
    }}
}}

puts "Dyna-mcp LS-PrePost bridge active on $::mcp_cmd_dir"
::mcp_bridge_poll
"""


def save_bridge_journal(poll_interval: float = 1.0) -> Path:
    """Generate and save the bridge journal cfile."""
    _ensure_dirs()
    path = _RUNS_DIR / "lsprepost_bridge.cfile"
    path.write_text(generate_bridge_journal(poll_interval), encoding="utf-8")
    logger.info(f"Saved bridge journal: {path}")
    return path


# --- Command/result management ---


def write_command(action: str, **kwargs: Any) -> str:
    """Write a command JSON file. Returns command ID."""
    _ensure_dirs()
    cmd_id = uuid4().hex[:12]
    cmd_file = _COMMANDS_DIR / f"{cmd_id}.json"
    data = {"action": action, **kwargs}
    cmd_file.write_text(json.dumps(data), encoding="utf-8")
    logger.info(f"Queued command: {action} → {cmd_file.name}")
    return cmd_id


def poll_result(cmd_id: str, timeout: float = 30.0, interval: float = 0.5) -> dict | None:
    """Poll for a command result. Returns None on timeout."""
    result_file = _RESULTS_DIR / f"{cmd_id}.json"
    start = time.time()
    while time.time() - start < timeout:
        if result_file.exists():
            try:
                data = json.loads(result_file.read_text(encoding="utf-8"))
                result_file.unlink(missing_ok=True)
                return data
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(interval)
    return None


# --- High-level API ---


def send_command(action: str, timeout: float = 30.0, **kwargs: Any) -> dict:
    """Send a command to LS-PrePost and wait for result."""
    if action not in SUPPORTED_ACTIONS:
        return {
            "success": False,
            "error": f"Unknown action: {action}",
            "supported": list(SUPPORTED_ACTIONS.keys()),
        }

    cmd_id = write_command(action, **kwargs)
    result = poll_result(cmd_id, timeout=timeout)

    if result is None:
        return {
            "success": False,
            "timeout": True,
            "message": f"No result within {timeout}s. Is LS-PrePost bridge running?",
            "hint": f"Launch: lsprepost4.13 cfile={save_bridge_journal()}",
        }

    return result


# --- Convenience functions ---


def open_d3plot(d3plot_path: str, timeout: float = 30.0) -> dict:
    """Open a d3plot file in LS-PrePost."""
    return send_command("open_d3plot", path=d3plot_path, timeout=timeout)


def open_key(key_path: str, timeout: float = 30.0) -> dict:
    """Open a keyword file in LS-PrePost."""
    return send_command("open_key", path=key_path, timeout=timeout)


def set_view(view: str, timeout: float = 10.0) -> dict:
    """Set viewport: front, top, iso, right, left, back, bottom."""
    return send_command("view", view=view, timeout=timeout)


def plot_stress(timeout: float = 30.0) -> dict:
    """Show von Mises stress contour."""
    return send_command("plot_stress", timeout=timeout)


def plot_deformed(scale: float = 1.0, timeout: float = 30.0) -> dict:
    """Show deformed shape."""
    return send_command("plot_deformed", scale=scale, timeout=timeout)


def export_png(
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    timeout: float = 30.0,
) -> dict:
    """Export current viewport as PNG."""
    return send_command(
        "export_png", path=output_path, width=width, height=height, timeout=timeout
    )


def execute_tcl_in_gui(script: str, timeout: float = 60.0) -> dict:
    """Execute arbitrary Tcl in LS-PrePost GUI."""
    return send_command("tcl", script=script, timeout=timeout)


def close_bridge(timeout: float = 10.0) -> dict:
    """Tell the bridge to exit."""
    return send_command("exit", timeout=timeout)


def full_post_processing(
    d3plot_path: str,
    output_dir: str,
    views: list[str] | None = None,
    timeout: float = 60.0,
) -> dict:
    """Run a complete post-processing sequence.

    Opens d3plot, shows stress contour, captures screenshots from multiple views.
    """
    if views is None:
        views = ["front", "top", "iso"]

    results: dict[str, Any] = {}

    # Open d3plot
    r = open_d3plot(d3plot_path, timeout=timeout)
    results["open"] = r
    if not r.get("success"):
        return results

    # Stress contour
    r = plot_stress(timeout=timeout)
    results["stress"] = r

    # Capture views
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for view in views:
        set_view(view, timeout=10)
        r = export_png(f"{output_dir}/stress_{view}.png", timeout=timeout)
        results[f"export_{view}"] = r

    results["success"] = True
    return results
