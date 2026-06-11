"""HyperMesh 2024+ Python API script channel.

The ``hm`` package is available inside the HyperMesh client runtime, not in
the project conda environment. This module therefore writes Python API scripts
and builds the configured HyperMesh launch command. Execution remains
``dry_run=True`` by default.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from program.tools.path_tools import load_yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RUNS_DIR = _PROJECT_ROOT / "runs"

_DANGEROUS_PATTERNS = (
    r"\bsubprocess\b",
    r"\bsocket\b",
    r"\bshutil\b",
    r"\brequests\b",
    r"\burllib\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\b__import__\s*\(",
    r"\bos\.(remove|unlink|rmdir|removedirs|rename|replace|system|popen|spawn|startfile)\b",
    r"\bPath\s*\([^)]*\)\.(unlink|rmdir|rename|replace)\b",
)


def _hm_cfg() -> dict[str, Any]:
    return load_yaml("hypermesh_paths").get("hypermesh", {})


def _python_api_cfg() -> dict[str, Any]:
    return _hm_cfg().get("python_api", {}) or {}


def resolve_hw_exe(override: str | Path | None = None) -> Path:
    """Resolve the HyperWorks GUI executable from override or config."""
    if override:
        return Path(override)

    cfg = _hm_cfg()
    explicit = cfg.get("hw_exe")
    if explicit:
        return Path(str(explicit))

    install_dir = cfg.get("install_dir")
    if not install_dir:
        raise FileNotFoundError("HyperMesh install_dir is not configured.")
    return Path(str(install_dir)) / "hw" / "bin" / "win64" / "hw.exe"


def check_python_api_environment() -> dict[str, Any]:
    """Check configured HyperMesh 2024+ Python API paths without importing hm."""
    cfg = _hm_cfg()
    api_cfg = _python_api_cfg()
    hw_exe = resolve_hw_exe()
    python_exe = Path(str(cfg.get("python_exe", ""))) if cfg.get("python_exe") else None
    version = str(cfg.get("version", ""))
    min_version = str(api_cfg.get("min_version", "2024"))

    return {
        "success": True,
        "enabled": bool(api_cfg.get("enabled", False)),
        "version": version,
        "min_version": min_version,
        "is_2024_plus": version >= min_version,
        "install_dir": cfg.get("install_dir"),
        "hw_exe": str(hw_exe),
        "hw_exe_exists": hw_exe.exists(),
        "python_exe": str(python_exe) if python_exe else None,
        "python_exe_exists": python_exe.exists() if python_exe else False,
        "script_arg": api_cfg.get("script_arg", "-python"),
        "note": "The hm module is loaded by the HyperMesh client runtime.",
    }


def check_python_api_policy(script: str, mode: str = "safe") -> str | None:
    """Return a policy error for unsafe Python API scripts, or None."""
    if not script.strip():
        return "Empty Python API script."

    for pattern in _DANGEROUS_PATTERNS:
        match = re.search(pattern, script, flags=re.IGNORECASE)
        if match:
            return f"Blocked unsafe Python API pattern: {match.group(0)}"

    if re.search(r"\bopen\s*\(", script) and not _extract_trusted_result_file(script):
        return "Blocked unsafe Python API pattern: open("

    if mode == "safe" and "import hm" not in script and "from hm" not in script:
        return "Safe mode requires an explicit HyperMesh Python API import (import hm)."

    return None


def build_model_info_script(model_path: str | None = None, result_path: str | Path | None = None) -> str:
    """Build a conservative HyperMesh Python API model-info script."""
    if result_path is None:
        _RUNS_DIR.mkdir(parents=True, exist_ok=True)
        result_path = _RUNS_DIR / f"hm_python_api_result_{time.strftime('%Y%m%d_%H%M%S')}_{os.getpid()}.json"
    result_file = str(result_path).replace("\\", "/").replace('"', '\\"')

    read_model = ""
    if model_path:
        safe_model_path = model_path.replace("\\", "/").replace('"', '\\"')
        read_model = (
            "\nmodel.hm_answernext('yes')"
            f"\nmodel.readfile(filename=r\"{safe_model_path}\", load_cad_geometry_as_graphics=0)"
        )

    return f'''# Hyper-Dyna-MCP HyperMesh Python API smoke script
# HDM_TRUSTED_RESULT_FILE={result_file}
import json
import hm
import hm.entities as ent

session = hm.Session()
model = hm.Model(session.get_all_models()[0]){read_model}
entity_types = {{
    "nodes": ent.Node,
    "elements": ent.Element,
    "components": ent.Component,
    "materials": ent.Material,
    "properties": ent.Property,
}}
summary = {{}}
for name, entity_type in entity_types.items():
    try:
        summary[name] = len(hm.Collection(model, entity_type))
    except Exception as exc:
        summary[name] = {{"error": f"{{type(exc).__name__}}: {{exc}}"}}
print("HDM_PYTHON_API_RESULT=" + json.dumps(summary, ensure_ascii=False))
with open(r"{result_file}", "w", encoding="utf-8") as result_fp:
    json.dump(summary, result_fp, ensure_ascii=False, indent=2)
'''


def write_python_api_script(script: str) -> Path:
    """Write a Python API script under runs/."""
    _RUNS_DIR.mkdir(parents=True, exist_ok=True)
    script_path = _RUNS_DIR / f"hm_python_api_{time.strftime('%Y%m%d_%H%M%S')}_{os.getpid()}.py"
    script_path.write_text(script, encoding="utf-8")
    return script_path


def generate_python_api_command(
    script_path: str | Path,
    *,
    hw_exe: str | Path | None = None,
) -> list[str]:
    """Generate a HyperMesh Python API launch command from config."""
    api_cfg = _python_api_cfg()
    exe = resolve_hw_exe(hw_exe)
    script_arg = str(api_cfg.get("script_arg", "-python"))
    client = api_cfg.get("client")

    command = [str(exe)]
    if client:
        command.extend(["-client", str(client)])
    command.extend([script_arg, str(script_path)])
    return command


def run_python_api_script(
    script: str,
    *,
    dry_run: bool | None = None,
    timeout: int = 300,
    mode: str = "safe",
    hw_exe: str | Path | None = None,
) -> dict[str, Any]:
    """Write a HyperMesh Python API script and optionally return its launch command.

    Real external launch is blocked in the current GUI-only MCP scope even when
    callers pass ``dry_run=False``.
    """
    if dry_run is None:
        api_cfg = _python_api_cfg()
        dry_run = bool(api_cfg.get("default_dry_run", True))

    policy_error = check_python_api_policy(script, mode=mode)
    if policy_error:
        return {
            "success": False,
            "error": policy_error,
            "error_type": "policy_error",
            "dry_run": dry_run,
            "executed": False,
        }

    if not dry_run:
        return {
            "success": False,
            "dry_run": False,
            "executed": False,
            "script_path": None,
            "command": [],
            "error": (
                "HyperMesh Python API external launch is outside the current MCP execution scope. "
                "Use dry_run=True to generate the script/command, or query the already-running GUI "
                "through hm_python_api_current_model_info."
            ),
            "error_type": "hypermesh_python_api_launch_out_of_scope",
            "result_file": _extract_trusted_result_file(script),
            "result": None,
        }

    script_path = write_python_api_script(script)
    command = generate_python_api_command(script_path, hw_exe=hw_exe)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "executed": False,
            "script_path": str(script_path),
            "command": command,
            "message": "dry_run=True; HyperMesh was not launched.",
        }


def _extract_trusted_result_file(script: str) -> str | None:
    for line in script.splitlines():
        if line.startswith("# HDM_TRUSTED_RESULT_FILE="):
            return line.partition("=")[2].strip()
    return None


def _read_trusted_result_file(script: str) -> Any:
    result_file = _extract_trusted_result_file(script)
    if not result_file:
        return None
    path = Path(result_file)
    if not path.exists():
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}", "path": str(path)}


def build_current_gui_model_info_tcl() -> str:
    """Build Tcl that queries the current GUI through HyperMesh Python API."""
    return r'''
set _py0 [::hw::HwxPyExec "import hm"]
set _py1 [::hw::HwxPyExec "import hm.entities as ent"]
set model_count [::hw::HwxPyExec "s = hm.Session(); HWXPY_RESULT = 1 if s.get_all_models() else 0"]
set _py2 [::hw::HwxPyExec "m = hm.Model(s.get_all_models()[0])"]
set comp_count [::hw::HwxPyExec "HWXPY_RESULT = len(hm.Collection(m, ent.Component))"]
set node_count [::hw::HwxPyExec "HWXPY_RESULT = len(hm.Collection(m, ent.Node))"]
set elem_count [::hw::HwxPyExec "HWXPY_RESULT = len(hm.Collection(m, ent.Element))"]
puts "PY_MODELS=$model_count"
puts "PY_COMPONENTS=$comp_count"
puts "PY_NODES=$node_count"
puts "PY_ELEMENTS=$elem_count"
'''


def query_current_gui_model_info_via_python(timeout: int = 30) -> dict[str, Any]:
    """Query current HyperMesh GUI model info using HM2024+ Python API."""
    from program.tools.hm_gui import execute_tcl_gui

    result = execute_tcl_gui(
        build_current_gui_model_info_tcl(),
        timeout=timeout,
        mode="raw",
    )
    response = result.get("response", "")
    info: dict[str, Any] = {}
    for line in response.splitlines():
        line = line.strip()
        if not line.startswith("PY_") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.removeprefix("PY_").lower()
        try:
            info[key] = int(value)
        except ValueError:
            info[key] = None if value == "None" else value

    if info.get("models") is None and all(key in info for key in ("components", "nodes", "elements")):
        info["models"] = 1

    # HM2025 can emit "UNKNOWN CMD: 0" around HwxPyExec even when the Python
    # calls complete and return the requested markers.
    ok = all(key in info for key in ("models", "components", "nodes", "elements"))
    return {
        "success": ok,
        "transport_success": result.get("success", False),
        "api": "HyperMesh Python API via ::hw::HwxPyExec",
        "info": info,
        "response": response,
        "error": None if ok else result.get("error"),
        "raw_result": result,
    }
