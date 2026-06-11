"""Blocked compatibility helpers for HyperMesh boundary-condition routes.

SPC/constraint Tcl routes are not execution-verified in the current
HyperMesh GUI-only MCP scope. These helpers are kept for legacy imports, but
must not send Tcl until ``apply_constraint_spc`` is promoted through command
recording and verified MAP evidence.
"""

from __future__ import annotations

from typing import Any

_BLOCKED_ROUTE = "apply_constraint_spc"


def _blocked_constraint_result(target: str, **extra: Any) -> dict[str, Any]:
    return {
        "success": False,
        "error_type": "constraint_route_not_verified",
        "blocked_route_name": _BLOCKED_ROUTE,
        "blocked_route_status": "unsupported",
        "execution_allowed": False,
        "tcl_sent": False,
        "target": target,
        "required_tool": "hm_modeling_action",
        "next_supported_actions": [
            {"tool": "hm_modeling_action", "action": "recording_requirements", "route_name": _BLOCKED_ROUTE},
            {"tool": "hm_modeling_action", "action": "validate_recording", "route_name": _BLOCKED_ROUTE},
        ],
        "error": (
            "SPC/constraint creation is not verified for MCP execution. "
            "Record and validate apply_constraint_spc before enabling this route."
        ),
        **extra,
    }


def create_spc_on_nodes(
    node_ids: list[int],
    dofx: int = 1,
    dofy: int = 1,
    dofz: int = 1,
    dofrx: int = 0,
    dofry: int = 0,
    dofrz: int = 0,
    collector_name: str = "SPC_BC",
    timeout: int = 30,
) -> dict:
    """Return a blocked result for legacy SPC-on-nodes callers.

    Constraint creation must go through ``hm_modeling_action`` recording
    requirements and verified route promotion before any Tcl is sent.
    """
    return _blocked_constraint_result(
        "nodes",
        node_ids=list(node_ids),
        collector_name=collector_name,
        dofs={"x": dofx, "y": dofy, "z": dofz, "rx": dofrx, "ry": dofry, "rz": dofrz},
    )


def create_spc_on_node_set(
    set_id: int,
    dofx: int = 1,
    dofy: int = 1,
    dofz: int = 1,
    dofrx: int = 0,
    dofry: int = 0,
    dofrz: int = 0,
    timeout: int = 30,
) -> dict:
    """Return a blocked result for legacy SPC-on-node-set callers.

    Constraint creation must go through ``hm_modeling_action`` recording
    requirements and verified route promotion before any Tcl is sent.
    """
    return _blocked_constraint_result(
        "node_set",
        set_id=set_id,
        collector_name=f"SPC_SET_{set_id}",
        dofs={"x": dofx, "y": dofy, "z": dofz, "rx": dofrx, "ry": dofry, "rz": dofrz},
    )
