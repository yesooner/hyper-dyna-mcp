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
from program.tools.hm_command_map import (
    canonical_element_type,
    command_map_stats,
    element_capability_matrix,
    get_experimental_route,
    get_unsupported_route,
    get_verified_route,
    known_element_types,
    list_verified_routes,
)
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
    create_beam_line,
    create_discrete_spring,
    create_fe_cube,
    create_lumped_mass,
    create_shell_plate,
    create_surface_plate,
    create_solid_box,
    create_tet4,
    create_tria3,
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
from program.tools.hm_recording_requirements import (
    recording_requirements,
    validate_recorded_route,
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
    model_path: Optional[str] = Field(
        default=None,
        description="Compatibility field only. Loading files through execute_tcl_gui is blocked; use dedicated verified tools.",
    )
    output_hm_path: Optional[str] = Field(
        default=None,
        description="Compatibility field only. Saving/export through execute_tcl_gui is blocked; use hm_auto_save for .hm saves.",
    )
    timeout: int = Field(default=120, description="Timeout in seconds.", ge=1)
    mode: str = Field(
        default="safe",
        description="Execution mode: 'safe' (whitelist+dictionary) or 'raw' (skips whitelist+dictionary; destructive commands remain blocked).",
        pattern=r"^(safe|raw)$",
    )


class ExecuteHmPythonApiInput(BaseModel):
    """Input for generating a HyperMesh 2024+ Python API script/command."""

    script: Optional[str] = Field(
        default=None,
        description="Python API script. If omitted, a model-info smoke script is generated.",
    )
    model_path: Optional[str] = Field(default=None, description="Optional .hm file for the smoke script.")
    dry_run: bool = Field(
        default=True,
        description="Keep true for script/command planning. False is accepted for compatibility but returns hypermesh_python_api_launch_out_of_scope.",
    )
    timeout: int = Field(default=300, description="Compatibility timeout field; external launch is blocked.", ge=1)
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
    """Input for the unsupported geometry-solid tetmesh route."""

    comp_name: str = Field(..., description="Component name.", min_length=1)
    element_size: float = Field(..., description="Requested target element size for future verified meshing route.", gt=0)
    timeout: int = Field(default=60, description="Timeout in seconds.", ge=1)


class HmCreateFeCubeInput(BaseModel):
    """Input for creating a structured HEX8 FE cube."""

    name: str = Field(default="soil_explosive_cube", description="Model/component name.", min_length=1)
    size: float = Field(..., description="Cube side length in current HyperMesh model units.", gt=0)
    element_size: float = Field(..., description="Target structured HEX8 element edge length.", gt=0)
    origin_x: float = Field(default=0.0, description="Origin X coordinate.")
    origin_y: float = Field(default=0.0, description="Origin Y coordinate.")
    origin_z: float = Field(default=0.0, description="Origin Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=90, description="Timeout in seconds for each stage.", ge=1)


class HmCreateSurfacePlateInput(BaseModel):
    """Input for creating a rectangular geometry surface plate."""

    name: str = Field(default="surface_plate", description="Model/component name.", min_length=1)
    width: float = Field(..., description="Plate width along +X in current model units.", gt=0)
    height: float = Field(..., description="Plate height along +Y in current model units.", gt=0)
    origin_x: float = Field(default=0.0, description="Origin X coordinate.")
    origin_y: float = Field(default=0.0, description="Origin Y coordinate.")
    origin_z: float = Field(default=0.0, description="Origin Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=60, description="Timeout in seconds for the GUI operation.", ge=1, le=180)


class HmCreateShellPlateInput(BaseModel):
    """Input for creating a structured QUAD4 FE shell plate."""

    name: str = Field(default="shell_plate", description="Model/component name.", min_length=1)
    width: float = Field(..., description="Plate width along +X in current model units.", gt=0)
    height: float = Field(..., description="Plate height along +Y in current model units.", gt=0)
    element_size: float = Field(..., description="Target QUAD4 shell element edge length.", gt=0)
    origin_x: float = Field(default=0.0, description="Origin X coordinate.")
    origin_y: float = Field(default=0.0, description="Origin Y coordinate.")
    origin_z: float = Field(default=0.0, description="Origin Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=90, description="Timeout in seconds for the GUI operation.", ge=1, le=180)


class HmCreateBeamLineInput(BaseModel):
    """Input for creating a structured BAR2/BEAM line."""

    name: str = Field(default="beam_line", description="Model/component name.", min_length=1)
    length: float = Field(..., description="Beam length in current model units.", gt=0)
    element_size: float = Field(..., description="Target beam element length.", gt=0)
    origin_x: float = Field(default=0.0, description="Origin X coordinate.")
    origin_y: float = Field(default=0.0, description="Origin Y coordinate.")
    origin_z: float = Field(default=0.0, description="Origin Z coordinate.")
    direction_x: float = Field(default=1.0, description="Direction vector X component.")
    direction_y: float = Field(default=0.0, description="Direction vector Y component.")
    direction_z: float = Field(default=0.0, description="Direction vector Z component.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=90, description="Timeout in seconds for the GUI operation.", ge=1, le=180)

    @model_validator(mode="after")
    def validate_direction(self) -> "HmCreateBeamLineInput":
        norm = (self.direction_x ** 2 + self.direction_y ** 2 + self.direction_z ** 2) ** 0.5
        if norm <= 0:
            raise ValueError("direction vector must be non-zero.")
        return self


class HmCreateDiscreteSpringInput(BaseModel):
    """Input for creating a two-node DISCRETE spring element."""

    name: str = Field(default="discrete_spring", description="Model/component name.", min_length=1)
    node_a_x: float = Field(default=0.0, description="Node A X coordinate.")
    node_a_y: float = Field(default=0.0, description="Node A Y coordinate.")
    node_a_z: float = Field(default=0.0, description="Node A Z coordinate.")
    node_b_x: float = Field(default=100.0, description="Node B X coordinate.")
    node_b_y: float = Field(default=0.0, description="Node B Y coordinate.")
    node_b_z: float = Field(default=0.0, description="Node B Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=60, description="Timeout in seconds for the GUI operation.", ge=1, le=180)

    @model_validator(mode="after")
    def validate_non_coincident_nodes(self) -> "HmCreateDiscreteSpringInput":
        if (
            self.node_a_x == self.node_b_x
            and self.node_a_y == self.node_b_y
            and self.node_a_z == self.node_b_z
        ):
            raise ValueError("node A and node B must not be coincident.")
        return self


class HmCreateLumpedMassInput(BaseModel):
    """Input for creating a one-node MASS element."""

    name: str = Field(default="lumped_mass", description="Model/component name.", min_length=1)
    mass: float = Field(..., description="Mass value passed to the verified *masselement route.", gt=0)
    x: float = Field(default=0.0, description="Node X coordinate.")
    y: float = Field(default=0.0, description="Node Y coordinate.")
    z: float = Field(default=0.0, description="Node Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=60, description="Timeout in seconds for the GUI operation.", ge=1, le=180)


class HmCreateTria3Input(BaseModel):
    """Input for creating one direct TRIA3 shell element."""

    name: str = Field(default="tria3", description="Model/component name.", min_length=1)
    node1_x: float = Field(default=0.0, description="Node 1 X coordinate.")
    node1_y: float = Field(default=0.0, description="Node 1 Y coordinate.")
    node1_z: float = Field(default=0.0, description="Node 1 Z coordinate.")
    node2_x: float = Field(default=100.0, description="Node 2 X coordinate.")
    node2_y: float = Field(default=0.0, description="Node 2 Y coordinate.")
    node2_z: float = Field(default=0.0, description="Node 2 Z coordinate.")
    node3_x: float = Field(default=0.0, description="Node 3 X coordinate.")
    node3_y: float = Field(default=100.0, description="Node 3 Y coordinate.")
    node3_z: float = Field(default=0.0, description="Node 3 Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=60, description="Timeout in seconds for the GUI operation.", ge=1, le=180)


class HmCreateTet4Input(BaseModel):
    """Input for creating one direct TET4 solid element."""

    name: str = Field(default="tet4", description="Model/component name.", min_length=1)
    node1_x: float = Field(default=0.0, description="Node 1 X coordinate.")
    node1_y: float = Field(default=0.0, description="Node 1 Y coordinate.")
    node1_z: float = Field(default=0.0, description="Node 1 Z coordinate.")
    node2_x: float = Field(default=100.0, description="Node 2 X coordinate.")
    node2_y: float = Field(default=0.0, description="Node 2 Y coordinate.")
    node2_z: float = Field(default=0.0, description="Node 2 Z coordinate.")
    node3_x: float = Field(default=0.0, description="Node 3 X coordinate.")
    node3_y: float = Field(default=100.0, description="Node 3 Y coordinate.")
    node3_z: float = Field(default=0.0, description="Node 3 Z coordinate.")
    node4_x: float = Field(default=0.0, description="Node 4 X coordinate.")
    node4_y: float = Field(default=0.0, description="Node 4 Y coordinate.")
    node4_z: float = Field(default=100.0, description="Node 4 Z coordinate.")
    comp_name: Optional[str] = Field(default=None, description="Optional component name.")
    timeout: int = Field(default=60, description="Timeout in seconds for the GUI operation.", ge=1, le=180)


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


class HmElementCapabilityInput(BaseModel):
    """Input for querying element creation/meshing/material capability."""

    element_type: Optional[str] = Field(
        default=None,
        description="Optional element type such as HEX, TET, shell, quad, tria, line, beam, lumped, or discrete.",
    )


class HmModelingActionInput(BaseModel):
    """Unified guarded modeling action input.

    This is the preferred agent-facing entry for deciding whether a modeling
    action can execute. It dispatches only to verified command-map routes or
    curated GUI Tcl keyword templates.
    """

    action: str = Field(
        ...,
        description="Action: capability, create_mesh, create_element, recording_requirements, validate_recording, assign_material, assign_property, assign_section, assign_eos, apply_constraint, or apply_load.",
        pattern=r"^(capability|create_mesh|create_element|recording_requirements|validate_recording|assign_material|assign_property|assign_section|assign_eos|apply_constraint|apply_load)$",
    )
    element_type: Optional[str] = Field(
        default=None,
        description="Element family/type, such as solid_hex, HEX8, shell_quad, QUAD4, beam, TET4, TRIA3, lumped_mass, or discrete.",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters. Use dry_run=true to get the verified route and required parameters without executing Tcl.",
    )
    dry_run: bool = Field(default=False, description="Return the planned verified route without sending Tcl.")
    timeout: int = Field(default=90, description="Timeout in seconds for executable GUI actions.", ge=1, le=180)

    @field_validator("action")
    @classmethod
    def lowercase_action(cls, v: str) -> str:
        return v.lower()

    @field_validator("element_type")
    @classmethod
    def normalize_element_type_text(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v


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
# Guarded modeling action dispatcher
# ===========================================================================

def _modeling_element_key(element_type: Optional[str]) -> Optional[str]:
    return canonical_element_type(element_type)


def _modeling_blocked(
    *,
    action: str,
    element_type: Optional[str],
    error_type: str,
    reason: str,
    required_verification: list[str],
    next_supported_actions: Optional[list[dict[str, Any]]] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    result = {
        "success": False,
        "action": action,
        "element_type": element_type,
        "error_type": error_type,
        "error": reason,
        "execution_allowed": False,
        "tcl_sent": False,
        "required_verification": required_verification,
        "policy": "Only verified HyperMesh command-map routes may execute Tcl.",
    }
    if next_supported_actions:
        result["next_supported_actions"] = next_supported_actions
    if extra:
        result.update(extra)
    return result


def _verified_alternative_actions(element_key: Optional[str], requested_action: str) -> list[dict[str, Any]]:
    if requested_action != "create_mesh":
        return []
    direct_element_metadata = {
        "solid_tet": {
            "scope": "direct single TET4 FE element, not geometry tetmesh",
            "required_parameters": ["node1", "node2", "node3", "node4"],
        },
        "shell_tria": {
            "scope": "direct single TRIA3 FE element, not surface automesh",
            "required_parameters": ["node1", "node2", "node3"],
        },
        "lumped_mass": {
            "scope": "direct one-node MASS FE element, not node-set meshing",
            "required_parameters": ["mass"],
        },
        "discrete": {
            "scope": "direct two-node DISCRETE spring element, not geometry meshing",
            "required_parameters": ["node_a", "node_b"],
        },
        "line_beam": {
            "scope": "direct generated straight BAR2/BEAM line, not existing-line meshing",
            "required_parameters": ["length", "element_size"],
        },
    }
    metadata = direct_element_metadata.get(element_key)
    if not metadata:
        return []
    capability = element_capability_matrix(element_key)
    creation = capability.get("capability", {}).get("creation", {})
    if (
        creation.get("supported") is not True
        or creation.get("route_status") != "verified"
        or not creation.get("tool")
        or not creation.get("route_name")
    ):
        return []
    return [
        {
            "action": "create_element",
            "tool": creation["tool"],
            "route_name": creation["route_name"],
            **metadata,
        }
    ]


def _blocked_recording_actions(route_name: str, scope: str) -> list[dict[str, Any]]:
    return [
        {
            "action": "recording_requirements",
            "route_name": route_name,
            "scope": scope,
        },
        {
            "action": "validate_recording",
            "route_name": route_name,
            "scope": "validate HyperMesh command recording text and runtime evidence before route promotion",
        },
    ]


def _material_assignment_route_name(element_key: Optional[str]) -> Optional[str]:
    if element_key is None:
        return None
    capability = element_capability_matrix(element_key)
    material = capability.get("capability", {}).get("material_assignment", {})
    route_name = material.get("route_name")
    return str(route_name) if route_name else None


def _mesh_route_name(element_key: Optional[str]) -> Optional[str]:
    if element_key is None:
        return None
    capability = element_capability_matrix(element_key)
    meshing = capability.get("capability", {}).get("meshing", {})
    route_name = meshing.get("route_name")
    return str(route_name) if route_name else None


def _blocked_workflow_route_name(action: str, element_key: Optional[str]) -> Optional[str]:
    if action == "create_mesh":
        if element_key == "mixed":
            return "mixed_mesh_workflow"
        return _mesh_route_name(element_key)
    if action == "assign_material":
        if element_key == "mixed":
            return "mixed_material_assignment"
        return _material_assignment_route_name(element_key)
    if action == "assign_eos":
        return "assign_eos_to_material"
    if action == "apply_constraint":
        return "apply_constraint_spc"
    if action == "apply_load":
        return "apply_load_nodal_or_pressure"
    return None


def _required_modeling_param(parameters: dict[str, Any], key: str) -> Any:
    if key not in parameters:
        raise ValueError(f"missing required parameter: {key}")
    return parameters[key]


def _modeling_plan(
    *,
    action: str,
    element_type: str,
    tool: str,
    route_name: str,
    required_parameters: list[str],
) -> dict[str, Any]:
    return {
        "success": True,
        "action": action,
        "element_type": element_type,
        "tool": tool,
        "route_name": route_name,
        "dry_run": True,
        "execution_allowed": True,
        "tcl_sent": False,
        "required_parameters": required_parameters,
        "policy": "Execution will dispatch only through the verified command-map route.",
    }


def _keyword_modeling_plan(
    *,
    action: str,
    element_type: str | None,
    keyword: str,
    required_parameters: list[str],
) -> dict[str, Any]:
    return {
        "success": True,
        "action": action,
        "element_type": element_type,
        "tool": "hm_set_keyword",
        "route_name": keyword.upper().lstrip("*"),
        "keyword": keyword.upper().lstrip("*"),
        "dry_run": True,
        "execution_allowed": True,
        "tcl_sent": False,
        "required_parameters": required_parameters,
        "policy": "Execution dispatches through structured GUI Tcl keyword templates, not backend K writing.",
    }


def _keyword_for_modeling_action(action: str, parameters: dict[str, Any]) -> str:
    explicit = parameters.get("keyword")
    if explicit:
        return str(explicit).upper().lstrip("*")
    if action == "assign_material":
        return str(parameters.get("mat_type", "MAT_ELASTIC")).upper().lstrip("*")
    if action in {"assign_property", "assign_section"}:
        return str(parameters.get("section_type", parameters.get("sec_type", "SECTION_SOLID"))).upper().lstrip("*")
    if action == "assign_eos":
        return str(parameters.get("eos_type", "EOS_LINEAR_POLYNOMIAL")).upper().lstrip("*")
    if action == "apply_constraint":
        return str(parameters.get("constraint_type", parameters.get("bc_type", "BOUNDARY_SPC"))).upper().lstrip("*")
    if action == "apply_load":
        return str(parameters.get("load_type", "LOAD_NODE")).upper().lstrip("*")
    return str(action).upper()


def _params_for_keyword_action(action: str, parameters: dict[str, Any]) -> dict[str, Any]:
    skip = {
        "keyword",
        "mat_type",
        "section_type",
        "sec_type",
        "eos_type",
        "constraint_type",
        "bc_type",
        "load_type",
    }
    return {key: value for key, value in parameters.items() if key not in skip}


def _execute_keyword_modeling_action(
    *,
    action: str,
    element_type: str | None,
    parameters: dict[str, Any],
    dry_run: bool,
    timeout: int,
) -> dict[str, Any]:
    keyword = _keyword_for_modeling_action(action, parameters)
    keyword_params = _params_for_keyword_action(action, parameters)
    if dry_run:
        return _keyword_modeling_plan(
            action=action,
            element_type=element_type,
            keyword=keyword,
            required_parameters=sorted(keyword_params),
        )
    result = hm_set_keyword(keyword, keyword_params, timeout=timeout)
    result.update(
        {
            "action": action,
            "element_type": element_type,
            "tool": "hm_set_keyword",
            "route_name": keyword,
            "execution_allowed": result.get("success") is True,
        }
    )
    result.setdefault("tcl_sent", result.get("success") is True)
    return result


def run_modeling_action(params: HmModelingActionInput) -> dict[str, Any]:
    """Run one guarded modeling action or return a blocked/planning result."""
    element_key = _modeling_element_key(params.element_type)
    p = params.parameters

    if params.action == "capability":
        return element_capability_matrix(params.element_type)

    if params.action == "recording_requirements":
        return recording_requirements(element_key, p)

    if params.action == "validate_recording":
        return validate_recorded_route(element_key, p)

    if element_key is not None and element_key not in known_element_types():
        return _modeling_blocked(
            action=params.action,
            element_type=element_key,
            error_type="unknown_element_type",
            reason=f"{params.element_type} is not a known HyperMesh MCP element type.",
            required_verification=[
                "Use hm_element_capability_matrix without element_type to list supported canonical element types and aliases.",
                "Do not record or execute Tcl for unknown element families until the capability matrix is extended.",
            ],
            next_supported_actions=[
                {
                    "action": "capability",
                    "tool": "hm_element_capability_matrix",
                    "scope": "list known element types and aliases before planning modeling actions",
                }
            ],
            extra={"known_types": known_element_types()},
        )

    if params.action in {"assign_material", "assign_property", "assign_section", "assign_eos", "apply_constraint", "apply_load"}:
        return _execute_keyword_modeling_action(
            action=params.action,
            element_type=element_key,
            parameters=p,
            dry_run=params.dry_run,
            timeout=params.timeout,
        )

    if element_key in {None, "mixed"}:
        return _modeling_blocked(
            action=params.action,
            element_type=element_key,
            error_type="unsupported_element_type",
            reason="Mixed or unspecified element workflows are not a single verified MCP route.",
            required_verification=[
                "Split the workflow into verified element-family routes.",
                "Verify transition rules between HEX/TET/SHELL/BEAM regions in HyperMesh command recording.",
                "Promote the mixed workflow only after connected-GUI runtime validation.",
            ],
            next_supported_actions=[
                {
                    "action": "capability",
                    "tool": "hm_element_capability_matrix",
                    "scope": "inspect per-family verified creation and blocked workflow routes",
                },
                {
                    "action": "recording_requirements",
                    "route_name": "mixed_mesh_workflow",
                    "scope": "inspect evidence required before mixed mesh can be promoted",
                },
            ],
        )

    if params.action == "create_mesh":
        if element_key == "solid_hex":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_fe_cube",
                    route_name="create_structured_hex8_box",
                    required_parameters=["size", "element_size"],
                )
            return create_fe_cube(
                str(p.get("name", "solid_hex_mesh")),
                float(_required_modeling_param(p, "size")),
                float(_required_modeling_param(p, "element_size")),
                origin_x=float(p.get("origin_x", 0.0)),
                origin_y=float(p.get("origin_y", 0.0)),
                origin_z=float(p.get("origin_z", 0.0)),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )
        if element_key == "shell_quad":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_shell_plate",
                    route_name="create_structured_quad4_shell_plate",
                    required_parameters=["width", "height", "element_size"],
                )
            return create_shell_plate(
                str(p.get("name", "shell_quad_mesh")),
                float(_required_modeling_param(p, "width")),
                float(_required_modeling_param(p, "height")),
                float(_required_modeling_param(p, "element_size")),
                origin_x=float(p.get("origin_x", 0.0)),
                origin_y=float(p.get("origin_y", 0.0)),
                origin_z=float(p.get("origin_z", 0.0)),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )
        blocked_route_name = _blocked_workflow_route_name(params.action, element_key)
        unsupported_route = get_unsupported_route(blocked_route_name) if blocked_route_name else None
        next_supported_actions = _verified_alternative_actions(element_key, params.action)
        if blocked_route_name:
            next_supported_actions.extend(
                _blocked_recording_actions(
                    blocked_route_name,
                    f"inspect evidence required before {element_key} automatic meshing can execute",
                )
            )
        return _modeling_blocked(
            action=params.action,
            element_type=element_key,
            error_type="mesh_route_not_verified",
            reason=f"{element_key} automatic meshing is not verified for MCP execution.",
            required_verification=(
                unsupported_route.get("required_verification", [])
                if unsupported_route
                else [
                    "Record the meshing workflow in HyperMesh command recording.",
                    "Verify entity marks, mesh controls, element count increase, and GUI display state.",
                    "Add a verified route before allowing MCP execution.",
                ]
            ),
            next_supported_actions=next_supported_actions,
            extra={
                "blocked_route_name": blocked_route_name,
                "blocked_route_status": unsupported_route.get("status") if unsupported_route else "missing",
                "blocked_route_entity_kind": unsupported_route.get("entity_kind") if unsupported_route else None,
            },
        )

    if params.action == "create_element":
        if element_key == "solid_tet":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_tet4",
                    route_name="create_tet_element",
                    required_parameters=["node1", "node2", "node3", "node4"],
                )
            return create_tet4(
                str(p.get("name", "tet4")),
                node1=tuple(p.get("node1", (0.0, 0.0, 0.0))),
                node2=tuple(p.get("node2", (100.0, 0.0, 0.0))),
                node3=tuple(p.get("node3", (0.0, 100.0, 0.0))),
                node4=tuple(p.get("node4", (0.0, 0.0, 100.0))),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )
        if element_key == "shell_tria":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_tria3",
                    route_name="create_shell_tria3",
                    required_parameters=["node1", "node2", "node3"],
                )
            return create_tria3(
                str(p.get("name", "tria3")),
                node1=tuple(p.get("node1", (0.0, 0.0, 0.0))),
                node2=tuple(p.get("node2", (100.0, 0.0, 0.0))),
                node3=tuple(p.get("node3", (0.0, 100.0, 0.0))),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )
        if element_key == "discrete":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_discrete_spring",
                    route_name="create_discrete_element",
                    required_parameters=["node_a", "node_b"],
                )
            return create_discrete_spring(
                str(p.get("name", "discrete_spring")),
                node_a=tuple(p.get("node_a", (0.0, 0.0, 0.0))),
                node_b=tuple(p.get("node_b", (100.0, 0.0, 0.0))),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )
        if element_key == "lumped_mass":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_lumped_mass",
                    route_name="create_lumped_mass",
                    required_parameters=["mass"],
                )
            return create_lumped_mass(
                str(p.get("name", "lumped_mass")),
                float(_required_modeling_param(p, "mass")),
                x=float(p.get("x", 0.0)),
                y=float(p.get("y", 0.0)),
                z=float(p.get("z", 0.0)),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )
        if element_key == "line_beam":
            if params.dry_run:
                return _modeling_plan(
                    action=params.action,
                    element_type=element_key,
                    tool="hm_create_beam_line",
                    route_name="create_beam_line",
                    required_parameters=["length", "element_size"],
                )
            return create_beam_line(
                str(p.get("name", "beam_line")),
                float(_required_modeling_param(p, "length")),
                float(_required_modeling_param(p, "element_size")),
                origin_x=float(p.get("origin_x", 0.0)),
                origin_y=float(p.get("origin_y", 0.0)),
                origin_z=float(p.get("origin_z", 0.0)),
                direction_x=float(p.get("direction_x", 1.0)),
                direction_y=float(p.get("direction_y", 0.0)),
                direction_z=float(p.get("direction_z", 0.0)),
                comp_name=p.get("comp_name"),
                timeout=params.timeout,
            )

    return _modeling_blocked(
        action=params.action,
        element_type=element_key,
        error_type="action_not_supported_for_element_type",
        reason=f"{params.action} is not supported for {element_key}.",
        required_verification=[
            "Check hm_element_capability_matrix for the current supported route.",
            "Add a verified command-map route before exposing execution.",
        ],
    )



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
    listener_pong = listener_info.get("pong") == "true"
    connected = bool(result.get("success", False) and listener_pong)
    return _success({
        "success": connected,
        "connected": connected,
        "host": DEFAULT_GUI_HOST,
        "port": port,
        "listener_version": listener_info.get("listener_version"),
        "tcl_version": listener_info.get("tcl_version"),
        "tcl_patchlevel": listener_info.get("tcl_patchlevel"),
        "listener_pong": listener_pong,
        "socket_success": result.get("success", False),
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
    annotations={"title": "Execute Tcl in GUI", "readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False},
)
async def execute_tcl_gui_tool(params: ExecuteTclGuiInput) -> str:
    """Execute Tcl in the running HyperMesh GUI listener.

    High-risk fallback only. Do not use this for agent-planned modeling,
    meshing, material/property, EOS, load, constraint, export, file I/O, or
    solver workflows. Use hm_modeling_action first; it dispatches verified
    routes and returns recording_requirements/validate_recording for blocked
    routes. Only call execute_tcl_gui for explicit, user-provided Tcl that is
    outside the dedicated tool surface and is safe to run in the current GUI.
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
    annotations={"title": "Plan HyperMesh Python API Script", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def execute_hm_python_api_tool(params: ExecuteHmPythonApiInput) -> str:
    """Generate a HyperMesh 2024+ Python API script and launch command.

    The hm module is available inside HyperMesh 2024+ / 2025, not in the
    project conda interpreter. This tool writes the script and, by default,
    returns the launch command without starting HyperMesh. Real external
    launch is outside the current GUI-only MCP scope, so dry_run=false is
    blocked by run_python_api_script with hypermesh_python_api_launch_out_of_scope.
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
    annotations={"title": "Blocked LS-DYNA Profile Conversion", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_convert_model_tool() -> str:
    """Return a blocked compatibility result for unverified profile conversion.

    LS-DYNA profile activation and bulk cardimage conversion are outside the
    current verified HyperMesh GUI-only MCP routes.
    """
    return _safe_call(convert_model_to_lsdyne)


# --- Keyword Operations ---

@mcp.tool(
    name="hm_set_keyword",
    annotations={"title": "MAP-Gated Keyword Card", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_set_keyword_tool(params: HmSetKeywordInput) -> str:
    """Set a keyword card only when the structured keyword MAP is execution-ready."""
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
    """Legacy geometry tool. Prefer hm_modeling_action before direct use."""
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
    """Report that geometry-solid tetmesh is not verified yet.

    Prefer hm_modeling_action(action=create_mesh, element_type=TET4) for
    planning; it returns the direct TET4 alternative and tetmesh recording
    requirements.

    Current executable mesh support is hm_create_fe_cube, which directly
    creates structured HEX8 FE mesh. Geometry-solid meshing must first be
    verified through HyperMesh command recording before this tool can send Tcl.
    """
    return _safe_call(mesh_box, params.comp_name, params.element_size, params.timeout)


@mcp.tool(
    name="hm_create_solid_box",
    annotations={"title": "Create Geometry Solid Box", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_solid_box_tool(params: HmCreateBoxInput) -> str:
    """Geometry solid target. Prefer hm_modeling_action before direct use."""
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
    """Create a structured HEX8 finite-element cube, not a geometry solid.

    Verified execution target. Prefer hm_modeling_action before direct use.
    """
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
    name="hm_create_surface_plate",
    annotations={"title": "Create Geometry Surface Plate", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_surface_plate_tool(params: HmCreateSurfacePlateInput) -> str:
    """Geometry surface target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_surface_plate,
        params.name,
        params.width,
        params.height,
        origin_x=params.origin_x,
        origin_y=params.origin_y,
        origin_z=params.origin_z,
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_create_shell_plate",
    annotations={"title": "Create QUAD4 Shell FE Plate", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_shell_plate_tool(params: HmCreateShellPlateInput) -> str:
    """Verified QUAD4 shell target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_shell_plate,
        params.name,
        params.width,
        params.height,
        params.element_size,
        origin_x=params.origin_x,
        origin_y=params.origin_y,
        origin_z=params.origin_z,
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_create_beam_line",
    annotations={"title": "Create BEAM Line", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_beam_line_tool(params: HmCreateBeamLineInput) -> str:
    """Verified BAR2/BEAM target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_beam_line,
        params.name,
        params.length,
        params.element_size,
        origin_x=params.origin_x,
        origin_y=params.origin_y,
        origin_z=params.origin_z,
        direction_x=params.direction_x,
        direction_y=params.direction_y,
        direction_z=params.direction_z,
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_create_discrete_spring",
    annotations={"title": "Create DISCRETE Spring", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_discrete_spring_tool(params: HmCreateDiscreteSpringInput) -> str:
    """Verified DISCRETE target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_discrete_spring,
        params.name,
        node_a=(params.node_a_x, params.node_a_y, params.node_a_z),
        node_b=(params.node_b_x, params.node_b_y, params.node_b_z),
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_create_lumped_mass",
    annotations={"title": "Create Lumped MASS", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_lumped_mass_tool(params: HmCreateLumpedMassInput) -> str:
    """Verified MASS target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_lumped_mass,
        params.name,
        params.mass,
        x=params.x,
        y=params.y,
        z=params.z,
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_create_tria3",
    annotations={"title": "Create TRIA3 Shell", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_tria3_tool(params: HmCreateTria3Input) -> str:
    """Verified TRIA3 target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_tria3,
        params.name,
        node1=(params.node1_x, params.node1_y, params.node1_z),
        node2=(params.node2_x, params.node2_y, params.node2_z),
        node3=(params.node3_x, params.node3_y, params.node3_z),
        comp_name=params.comp_name,
        timeout=params.timeout,
    )


@mcp.tool(
    name="hm_create_tet4",
    annotations={"title": "Create TET4 Solid", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_create_tet4_tool(params: HmCreateTet4Input) -> str:
    """Verified TET4 target. Prefer hm_modeling_action before direct use."""
    return _safe_call(
        create_tet4,
        params.name,
        node1=(params.node1_x, params.node1_y, params.node1_z),
        node2=(params.node2_x, params.node2_y, params.node2_z),
        node3=(params.node3_x, params.node3_y, params.node3_z),
        node4=(params.node4_x, params.node4_y, params.node4_z),
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
        if route is not None:
            return _success({"route_name": params.route_name, "route": route})
        experimental = get_experimental_route(params.route_name)
        if experimental is not None:
            return _success({"route_name": params.route_name, "route": experimental, "experimental": True})
        if route is None:
            return _error(
                f"HyperMesh Tcl command route is not verified: {params.route_name}",
                route_name=params.route_name,
                stats=command_map_stats(),
            )
    routes = list_verified_routes()
    return _success({"stats": command_map_stats(), "routes": routes})


@mcp.tool(
    name="hm_element_capability_matrix",
    annotations={"title": "Element Capability Matrix", "readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def hm_element_capability_matrix_tool(params: HmElementCapabilityInput) -> str:
    """Report element creation, meshing, and material-assignment support.

    This is a planning/guardrail tool. It does not execute Tcl. It prevents
    agents from assuming unsupported element families can already be created,
    meshed, or assigned materials through MCP.
    """
    return _success(element_capability_matrix(params.element_type))


@mcp.tool(
    name="hm_modeling_action",
    annotations={"title": "Guarded Modeling Action", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
)
async def hm_modeling_action_tool(params: HmModelingActionInput) -> str:
    """Unified guarded modeling entry.

    Use this before choosing narrow create tools. It only dispatches to verified
    command-map routes. Material, EOS, constraint, load, mixed mesh, tetmesh, and
    surface automesh requests return blocked results until command recording
    and connected-GUI validation promote those routes.
    """
    return _safe_call(run_modeling_action, params)


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
