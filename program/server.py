"""hyperdyna_mcp: HyperMesh-only MCP server.

The MCP surface is intentionally limited to tools that operate inside a
running HyperMesh GUI through the Tcl listener or the project IPC queue.
It does not expose LS-DYNA solver execution, LS-PrePost execution, or
HyperMesh hmbatch execution tools.
"""

from __future__ import annotations

import json
import os
import traceback
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, model_validator

from program.tools.env_check import check_environment
from program.tools.dyna_keyword_map import (
    dyna_keyword_policy_summary,
    query_dyna_keyword,
    validate_dyna_keyword_map,
)
from program.tools.hm_command_map import command_map_stats, get_verified_route, list_verified_routes
from program.tools.hm_gui import (
    DEFAULT_GUI_HOST,
    DEFAULT_GUI_PORT,
    configure_gui_port,
    current_gui_port,
    diagnose_listener_port,
    ensure_listener_tcl_for_port,
    execute_tcl_gui,
    parse_listener_ping_response,
    query_model_info,
    send_tcl_to_gui,
    LISTENER_VERSION,
    _tcl_start_or_source_command,
    _tcl_source_command,
)
from program.tools.hm_keyword_skill import hm_check_model, hm_keyword_help, hm_set_keyword
from program.tools.hm_model_converter import convert_model_to_lsdyne
from program.tools.hm_model_reader import read_all_components, read_all_materials
from program.tools.hm_model_writer import (
    create_box,
    create_fe_cube,
    create_solid_box,
    mesh_box,
    refresh_visualization,
    run_gui_modeling_smoke,
)
from program.tools.hm_python_api import (
    build_model_info_script,
    check_python_api_environment,
    query_current_gui_model_info_via_python,
    run_python_api_script,
)
from program.tools.hm_safe_save import auto_save
from program.tools.hm_template_engine import HmTemplateEngine
from program.tools.path_tools import load_yaml, validate_path


mcp = FastMCP("hyperdyna_mcp", log_level=os.getenv("FASTMCP_LOG_LEVEL", "INFO"))


# ===========================================================================
# Shared utilities
# ===========================================================================

def _json(data: Any) -> str:
    """Serialize to JSON string."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _success(data: Any) -> str:
    """Wrap successful result."""
    if isinstance(data, dict):
        data.setdefault("success", True)
    return _json(data)


def _error(message: str, **extra: Any) -> str:
    """Wrap error result with actionable message."""
    return _json({"success": False, "error": message, **extra})


def _safe_call(fn, *args, **kwargs) -> str:
    """Call a tool function with unified error handling."""
    try:
        result = fn(*args, **kwargs)
        return _json(result)
    except FileNotFoundError as e:
        return _error(f"File not found: {e}")
    except ConnectionRefusedError:
        return _error(
            "HyperMesh GUI connection refused. Is the listener active?",
            hint="Call start_hypermesh_gui_listener, then source the Tcl in HyperMesh.",
        )
    except TimeoutError:
        return _error("Operation timed out. HyperMesh may be unresponsive.")
    except Exception as e:
        return _error(f"{type(e).__name__}: {e}", traceback=traceback.format_exc())


# ===========================================================================
# Pydantic Input Models
# ===========================================================================

class CheckEnvironmentInput(BaseModel):
    """Input for environment check."""

    required_packages: Optional[list[str]] = Field(
        default=None,
        description="Package names to check.",
    )


class LoadPathConfigInput(BaseModel):
    """Input for loading YAML path config."""

    name: str = Field(
        ...,
        description="Config name without .yaml extension, such as local_paths or hypermesh_paths.",
        min_length=1,
    )

    @field_validator("name")
    @classmethod
    def no_yaml_extension(cls, v: str) -> str:
        return v.removesuffix(".yaml").removesuffix(".yml")


class ValidatePathInput(BaseModel):
    """Input for path validation."""

    path: str = Field(..., description="Filesystem path to check.", min_length=1)


class StartListenerInput(BaseModel):
    """Input for generating the HyperMesh listener Tcl."""

    port: int = Field(default_factory=current_gui_port, description="Listener port.", ge=1024, le=65535)


class DiagnoseListenerInput(BaseModel):
    """Input for diagnosing the HyperMesh listener socket."""

    port: int = Field(default_factory=current_gui_port, description="Listener port.", ge=1024, le=65535)
    timeout: int = Field(default=3, description="Socket ping timeout in seconds.", ge=1, le=30)
    include_alternate: bool = Field(default=True, description="Generate an alternate-port listener suggestion.")


class SetListenerPortInput(BaseModel):
    """Input for changing the current MCP process listener port."""

    port: int = Field(..., description="Listener port for this MCP process.", ge=1024, le=65535)


class ExecuteTclGuiInput(BaseModel):
    """Input for executing Tcl in HyperMesh GUI."""

    script: str = Field(..., description="Tcl script to execute in HyperMesh.", min_length=1)
    model_path: Optional[str] = Field(default=None, description="Optional .hm file to load first.")
    output_hm_path: Optional[str] = Field(default=None, description="Optional .hm save path after execution.")
    timeout: int = Field(default=120, description="Timeout in seconds.", ge=1)
    mode: str = Field(
        default="safe",
        description="Execution mode: 'safe' (whitelist+dictionary) or 'raw' (skips whitelist+dictionary; destructive commands remain blocked).",
        pattern=r"^(safe|raw)$",
    )


class ExecuteHmPythonApiInput(BaseModel):
    """Input for executing a HyperMesh 2024+ Python API script."""

    script: Optional[str] = Field(
        default=None,
        description="Python API script. If omitted, a model-info smoke script is generated.",
    )
    model_path: Optional[str] = Field(default=None, description="Optional .hm file for the smoke script.")
    dry_run: bool = Field(default=True, description="Do not launch HyperMesh unless explicitly false.")
    timeout: int = Field(default=300, description="Timeout in seconds when dry_run is false.", ge=1)
    mode: str = Field(
        default="safe",
        description="Execution policy: 'safe' requires import hm; 'raw' skips that import check. Dangerous Python remains blocked.",
        pattern=r"^(safe|raw)$",
    )


class HmPythonApiCurrentGuiInput(BaseModel):
    """Input for querying current GUI through HyperMesh Python API."""

    timeout: int = Field(default=30, description="Timeout in seconds.", ge=1)


class HmAutoSaveInput(BaseModel):
    """Input for auto-saving the current HyperMesh model."""

    step_name: str = Field(..., description="Step name for the saved model.", min_length=1)
    model_path: Optional[str] = Field(default=None, description="Custom save path.")
    timeout: int = Field(default=30, description="Timeout in seconds.", ge=1)


class HmSetKeywordInput(BaseModel):
    """Input for setting an LS-DYNA keyword card through HyperMesh."""

    keyword: str = Field(..., description="Keyword card image name.", min_length=1)
    params: dict[str, Any] = Field(..., description="Keyword parameters.")
    timeout: int = Field(default=15, description="Timeout in seconds.", ge=1)

    @field_validator("keyword")
    @classmethod
    def uppercase_keyword(cls, v: str) -> str:
        return v.upper().lstrip("*")


class HmKeywordHelpInput(BaseModel):
    """Input for keyword help."""

    keyword: str = Field(..., description="Keyword card image name.", min_length=1)

    @field_validator("keyword")
    @classmethod
    def uppercase_keyword(cls, v: str) -> str:
        return v.upper().lstrip("*")


class HmCreateBoxInput(BaseModel):
    """Input for creating a box solid in HyperMesh."""

    name: str = Field(..., description="Name for the solid.", min_length=1)
    x_min: float = Field(..., description="Minimum X coordinate.")
    y_min: float = Field(..., description="Minimum Y coordinate.")
    z_min: float = Field(..., description="Minimum Z coordinate.")
    x_max: float = Field(..., description="Maximum X coordinate.")
    y_max: float = Field(..., description="Maximum Y coordinate.")
    z_max: float = Field(..., description="Maximum Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=30, description="Timeout in seconds for the GUI operation.", ge=1, le=180)

    @model_validator(mode="after")
    def validate_positive_extents(self) -> "HmCreateBoxInput":
        if self.x_min >= self.x_max:
            raise ValueError("x_min must be less than x_max.")
        if self.y_min >= self.y_max:
            raise ValueError("y_min must be less than y_max.")
        if self.z_min >= self.z_max:
            raise ValueError("z_min must be less than z_max.")
        return self


class HmMeshBoxInput(BaseModel):
    """Input for meshing a box with tetrahedral elements."""

    comp_name: str = Field(..., description="Component name.", min_length=1)
    element_size: float = Field(..., description="Target element size.", gt=0)
    timeout: int = Field(default=60, description="Timeout in seconds.", ge=1)


class HmCreateFeCubeInput(BaseModel):
    """Input for creating and meshing a cube."""

    name: str = Field(default="soil_explosive_cube", description="Model/component name.", min_length=1)
    size: float = Field(..., description="Cube side length in current HyperMesh model units.", gt=0)
    element_size: float = Field(..., description="Target tetrahedral element size.", gt=0)
    origin_x: float = Field(default=0.0, description="Origin X coordinate.")
    origin_y: float = Field(default=0.0, description="Origin Y coordinate.")
    origin_z: float = Field(default=0.0, description="Origin Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=90, description="Timeout in seconds for each stage.", ge=1)


class HmSearchKeywordsInput(BaseModel):
    """Input for searching keyword index."""

    query: str = Field(..., description="Search string.", min_length=1)
    category: Optional[str] = Field(default=None, description="Optional category filter.")


class HmKeywordMapInput(BaseModel):
    """Input for listing keywords by category."""

    category: str = Field(..., description="Keyword category.", min_length=1)


class DynaKeywordQueryInput(BaseModel):
    """Input for structured LS-DYNA keyword lookup."""

    keyword: str = Field(..., description="LS-DYNA keyword, with or without leading '*'.", min_length=1)


class HmCommandRouteInput(BaseModel):
    """Input for querying verified HyperMesh Tcl command routes."""

    route_name: Optional[str] = Field(default=None, description="Optional route name, such as create_structured_hex8_box.")


class HmVisualRefreshInput(BaseModel):
    """Input for refreshing HyperMesh GUI visualization."""

    timeout: int = Field(default=15, description="Timeout in seconds.", ge=1)


class HmGuiModelingSmokeInput(BaseModel):
    """Input for running a small GUI modeling smoke workflow."""

    size: float = Field(default=10.0, description="Smoke cube/box side length.", gt=0)
    element_size: float = Field(default=10.0, description="FE cube element size.", gt=0)
    timeout: int = Field(default=30, description="Timeout in seconds for each GUI stage.", ge=1, le=180)


class HmReadMaterialsInput(BaseModel):
    """Input for reading materials with pagination."""

    limit: Optional[int] = Field(default=50, description="Max results to return.", ge=1, le=500)
    offset: Optional[int] = Field(default=0, description="Number to skip.", ge=0)


class HmReadComponentsInput(BaseModel):
    """Input for reading components with pagination."""

    limit: Optional[int] = Field(default=50, description="Max results to return.", ge=1, le=500)
    offset: Optional[int] = Field(default=0, description="Number to skip.", ge=0)


# ===========================================================================
# Tool Implementations
# ===========================================================================

# --- Connection & Status ---

@mcp.tool(
    name="ping",
    annotations={"title": "Ping", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def ping_tool() -> str:
    """Return a lightweight health response from the MCP server process."""
    return _success({
        "ok": True,
        "server": "hyperdyna_mcp",
        "scope": "hypermesh_gui_only",
        "transport": ["socket", "ipc"],
    })


@mcp.tool(
    name="check_environment",
    annotations={"title": "Check Environment", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def check_environment_tool(params: CheckEnvironmentInput) -> str:
    """Check Python version, conda env, and required Python packages."""
    return _safe_call(check_environment, params.required_packages)


@mcp.tool(
    name="load_path_config",
    annotations={"title": "Load Path Config", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def load_path_config_tool(params: LoadPathConfigInput) -> str:
    """Load a YAML path configuration file from path/."""
    return _safe_call(load_yaml, params.name)


@mcp.tool(
    name="validate_path",
    annotations={"title": "Validate Path", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def validate_path_tool(params: ValidatePathInput) -> str:
    """Check whether a filesystem path exists."""
    ok = validate_path(params.path)
    return _success({"path": params.path, "exists": ok})


# --- HyperMesh GUI Connection ---

@mcp.tool(
    name="start_hypermesh_gui_listener",
    annotations={"title": "Start GUI Listener", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def start_hypermesh_gui_listener_tool(params: StartListenerInput) -> str:
    """Generate the Tcl listener script that must be sourced inside HyperMesh."""
    path = ensure_listener_tcl_for_port(params.port)
    source_command = _tcl_source_command(path)
    start_or_source_command = _tcl_start_or_source_command(params.port, path)
    return _success({
        "listener_tcl": str(path),
        "host": DEFAULT_GUI_HOST,
        "port": params.port,
        "listener_version": LISTENER_VERSION,
        "source_command": source_command,
        "start_or_source_command": start_or_source_command,
        "hypermesh_command": start_or_source_command,
        "next_hypermesh_commands": [
            "catch {mcp_stop}",
            start_or_source_command,
        ],
        "next_step": "Run next_hypermesh_commands in the HyperMesh Tcl Console, then call check_hypermesh_connection.",
    })


@mcp.tool(
    name="check_hypermesh_connection",
    annotations={"title": "Check HyperMesh GUI Connection", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def check_hypermesh_connection_tool() -> str:
    """Verify the HyperMesh GUI Tcl listener socket is reachable."""
    port = current_gui_port()
    result = send_tcl_to_gui("__HDM_PING__", port=port, timeout=5, mode="raw")
    listener_info = parse_listener_ping_response(result.get("response", ""))
    return _success({
        "connected": result.get("success", False),
        "host": DEFAULT_GUI_HOST,
        "port": port,
        "listener_version": listener_info.get("listener_version"),
        "tcl_version": listener_info.get("tcl_version"),
        "tcl_patchlevel": listener_info.get("tcl_patchlevel"),
        "listener_pong": listener_info.get("pong") == "true",
        "response": result.get("response", ""),
        "error": result.get("error"),
    })


@mcp.tool(
    name="diagnose_hypermesh_listener",
    annotations={"title": "Diagnose HyperMesh Listener", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def diagnose_hypermesh_listener_tool(params: DiagnoseListenerInput) -> str:
    """Diagnose listener version, port owner PID, and recovery steps."""
    return _safe_call(
        diagnose_listener_port,
        port=params.port,
        timeout=params.timeout,
        include_alternate=params.include_alternate,
    )


@mcp.tool(
    name="set_hypermesh_listener_port",
    annotations={"title": "Set HyperMesh Listener Port", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def set_hypermesh_listener_port_tool(params: SetListenerPortInput) -> str:
    """Change the listener port used by this MCP process and regenerate Tcl."""
    return _safe_call(configure_gui_port, params.port)


@mcp.tool(
    name="get_model_info",
    annotations={"title": "Get Model Info", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def get_model_info_tool() -> str:
    """Query current model counts from HyperMesh GUI."""
    return _safe_call(query_model_info)


@mcp.tool(
    name="execute_tcl_gui",
    annotations={"title": "Execute Tcl in GUI", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def execute_tcl_gui_tool(params: ExecuteTclGuiInput) -> str:
    """Execute Tcl in the running HyperMesh GUI listener.

    DO NOT guess HyperMesh commands. Use these instead:
    - hm_set_keyword for keyword cards (MAT_*, SECTION_*, CONTROL_*, etc.)
    - hm_create_box for geometry creation
    - hm_mesh_box for meshing
    - hm_search_keywords / hm_keyword_map to discover available keywords

    Only use this for Tcl commands that have no dedicated tool.
    """
    result = execute_tcl_gui(
        script=params.script,
        model_path=params.model_path,
        output_hm_path=params.output_hm_path,
        timeout=params.timeout,
        mode=params.mode,
    )
    return _json(result)


@mcp.tool(
    name="hm_python_api_status",
    annotations={"title": "HyperMesh Python API Status", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_python_api_status_tool() -> str:
    """Check configured HyperMesh 2024+ Python API paths."""
    return _safe_call(check_python_api_environment)


@mcp.tool(
    name="execute_hm_python_api",
    annotations={"title": "Execute HyperMesh Python API", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def execute_hm_python_api_tool(params: ExecuteHmPythonApiInput) -> str:
    """Generate or run a HyperMesh 2024+ Python API script.

    The hm module is available inside HyperMesh 2024+ / 2025, not in the
    project conda interpreter. This tool writes the script and, by default,
    returns the launch command without starting HyperMesh.
    """
    script = params.script or build_model_info_script(params.model_path)
    result = run_python_api_script(
        script,
        dry_run=params.dry_run,
        timeout=params.timeout,
        mode=params.mode,
    )
    return _json(result)


@mcp.tool(
    name="hm_python_api_current_model_info",
    annotations={"title": "Current GUI Python API Model Info", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_python_api_current_model_info_tool(params: HmPythonApiCurrentGuiInput) -> str:
    """Query the current connected HyperMesh GUI using HM2024+ Python API."""
    return _safe_call(query_current_gui_model_info_via_python, params.timeout)


# --- Model Save ---

@mcp.tool(
    name="hm_auto_save",
    annotations={"title": "Auto-Save Model", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_auto_save_tool(params: HmAutoSaveInput) -> str:
    """Save the current HyperMesh model after a major operation."""
    return _safe_call(auto_save, params.step_name, params.model_path, params.timeout)


# --- Model Reading (with pagination) ---

@mcp.tool(
    name="hm_check_model",
    annotations={"title": "Check Model State", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_check_model_tool() -> str:
    """Check model state in HyperMesh GUI."""
    return _safe_call(hm_check_model)


@mcp.tool(
    name="hm_read_materials",
    annotations={"title": "Read Materials", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_read_materials_tool(params: HmReadMaterialsInput) -> str:
    """Read materials from HyperMesh GUI with pagination."""
    try:
        all_materials = read_all_materials()
        if isinstance(all_materials, list):
            total = len(all_materials)
            page = all_materials[params.offset : params.offset + params.limit]
            return _success({
                "total": total,
                "count": len(page),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": params.offset + params.limit < total,
                "materials": page,
            })
        return _json(all_materials)
    except Exception as e:
        return _error(f"{type(e).__name__}: {e}")


@mcp.tool(
    name="hm_read_components",
    annotations={"title": "Read Components", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_read_components_tool(params: HmReadComponentsInput) -> str:
    """Read components from HyperMesh GUI with pagination."""
    try:
        all_components = read_all_components()
        if isinstance(all_components, list):
            total = len(all_components)
            page = all_components[params.offset : params.offset + params.limit]
            return _success({
                "total": total,
                "count": len(page),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": params.offset + params.limit < total,
                "components": page,
            })
        return _json(all_components)
    except Exception as e:
        return _error(f"{type(e).__name__}: {e}")


# --- Model Conversion ---

@mcp.tool(
    name="hm_convert_model",
    annotations={"title": "Convert Model to LS-DYNA Profile", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_convert_model_tool() -> str:
    """Activate the LS-DYNA profile inside HyperMesh and set card images."""
    return _safe_call(convert_model_to_lsdyne)


# --- Keyword Operations ---

@mcp.tool(
    name="hm_set_keyword",
    annotations={"title": "Set Keyword Card", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_set_keyword_tool(params: HmSetKeywordInput) -> str:
    """Create or update a keyword card inside HyperMesh."""
    return _safe_call(hm_set_keyword, params.keyword, params.params, params.timeout)


@mcp.tool(
    name="hm_keyword_help",
    annotations={"title": "Keyword Help", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_keyword_help_tool(params: HmKeywordHelpInput) -> str:
    """Get fields and local metadata for a keyword card."""
    return _safe_call(hm_keyword_help, params.keyword)


# --- Geometry & Meshing ---

@mcp.tool(
    name="hm_create_box",
    annotations={"title": "Create Box Solid", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_box_tool(params: HmCreateBoxInput) -> str:
    """Create a box solid in HyperMesh from corner coordinates."""
    if params.x_min >= params.x_max or params.y_min >= params.y_max or params.z_min >= params.z_max:
        return _error("Min coordinates must be less than max coordinates.")
    return _safe_call(
        create_box,
        params.name, params.x_min, params.y_min, params.z_min,
        params.x_max, params.y_max, params.z_max, params.comp_name,
        params.timeout,
    )


@mcp.tool(
    name="hm_mesh_box",
    annotations={"title": "Mesh Box", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_mesh_box_tool(params: HmMeshBoxInput) -> str:
    """Mesh the current box solid with tetrahedral elements."""
    return _safe_call(mesh_box, params.comp_name, params.element_size, params.timeout)


@mcp.tool(
    name="hm_create_solid_box",
    annotations={"title": "Create Geometry Solid Box", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_solid_box_tool(params: HmCreateBoxInput) -> str:
    """Create a geometry solid box only after the Tcl route is verified."""
    if params.x_min >= params.x_max or params.y_min >= params.y_max or params.z_min >= params.z_max:
        return _error("Min coordinates must be less than max coordinates.")
    return _safe_call(
        create_solid_box,
        params.name, params.x_min, params.y_min, params.z_min,
        params.x_max, params.y_max, params.z_max, params.comp_name,
        params.timeout,
    )


@mcp.tool(
    name="hm_create_fe_cube",
    annotations={"title": "Create FE Cube", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_fe_cube_tool(params: HmCreateFeCubeInput) -> str:
    """Create a structured HEX8 finite-element cube, not a geometry solid."""
    return _safe_call(
        create_fe_cube,
        params.name,
        params.size,
        params.element_size,
        origin_x=params.origin_x,
        origin_y=params.origin_y,
        origin_z=params.origin_z,
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_visual_refresh",
    annotations={"title": "Refresh HyperMesh Visualization", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_visual_refresh_tool(params: HmVisualRefreshInput) -> str:
    """Refresh and fit visible FE/solid entities in the current HyperMesh GUI."""
    return _safe_call(refresh_visualization, timeout=params.timeout)


@mcp.tool(
    name="hm_gui_modeling_smoke",
    annotations={"title": "GUI Modeling Smoke", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_gui_modeling_smoke_tool(params: HmGuiModelingSmokeInput) -> str:
    """Create a small FE cube and geometry solid, then refresh the GUI."""
    return _safe_call(
        run_gui_modeling_smoke,
        size=params.size,
        element_size=params.element_size,
        timeout=params.timeout,
    )


# --- Keyword Index ---

@mcp.tool(
    name="hm_search_keywords",
    annotations={"title": "Search Keywords", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_search_keywords_tool(params: HmSearchKeywordsInput) -> str:
    """Search the local keyword template index."""
    engine = HmTemplateEngine()
    results = engine.search_keywords(query=params.query, category=params.category)[:20]
    return _success({"count": len(results), "results": results})


@mcp.tool(
    name="hm_keyword_map",
    annotations={"title": "Keyword Map", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_keyword_map_tool(params: HmKeywordMapInput) -> str:
    """List local keyword templates by category."""
    engine = HmTemplateEngine()
    results = engine.get_keyword_map(category=params.category)
    return _success({"category": params.category, "count": len(results), "keywords": results})


@mcp.tool(
    name="hm_command_map",
    annotations={"title": "HyperMesh Command Map", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_command_map_tool(params: HmCommandRouteInput) -> str:
    """List or inspect verified HyperMesh Tcl command routes."""
    if params.route_name:
        route = get_verified_route(params.route_name)
        if route is None:
            return _error(
                f"HyperMesh Tcl command route is not verified: {params.route_name}",
                route_name=params.route_name,
                stats=command_map_stats(),
            )
        return _success({"route_name": params.route_name, "route": route})
    routes = list_verified_routes()
    return _success({"stats": command_map_stats(), "routes": routes})


@mcp.tool(
    name="dyna_keyword_policy",
    annotations={"title": "Dyna Keyword Policy", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def dyna_keyword_policy_tool() -> str:
    """Return the structured Dyna keyword/manual/embedding execution policy."""
    return _success(dyna_keyword_policy_summary())


@mcp.tool(
    name="dyna_keyword_query",
    annotations={"title": "Dyna Keyword Query", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def dyna_keyword_query_tool(params: DynaKeywordQueryInput) -> str:
    """Query structured Dyna keyword/cardimage/manual-note guidance."""
    return _success(query_dyna_keyword(params.keyword))


@mcp.tool(
    name="dyna_keyword_map_validate",
    annotations={"title": "Dyna Keyword Map Validate", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def dyna_keyword_map_validate_tool() -> str:
    """Validate structured Dyna keyword MAP guardrails before execution use."""
    return _success(validate_dyna_keyword_map())


# ===========================================================================
# Entry point
# ===========================================================================

def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
