"""Tests for blocked boundary-condition compatibility helpers."""

from program.tools import hm_boundary_safe


def test_create_spc_on_nodes_is_blocked_without_tcl():
    result = hm_boundary_safe.create_spc_on_nodes([1, 2, 3], collector_name="FIXED")

    assert result["success"] is False
    assert result["error_type"] == "constraint_route_not_verified"
    assert result["blocked_route_name"] == "apply_constraint_spc"
    assert result["blocked_route_status"] == "unsupported"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_modeling_action"
    assert result["target"] == "nodes"
    assert result["node_ids"] == [1, 2, 3]
    assert {"tool": "hm_modeling_action", "action": "recording_requirements", "route_name": "apply_constraint_spc"} in result["next_supported_actions"]


def test_create_spc_on_node_set_is_blocked_without_tcl():
    result = hm_boundary_safe.create_spc_on_node_set(42)

    assert result["success"] is False
    assert result["error_type"] == "constraint_route_not_verified"
    assert result["blocked_route_name"] == "apply_constraint_spc"
    assert result["blocked_route_status"] == "unsupported"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_modeling_action"
    assert result["target"] == "node_set"
    assert result["set_id"] == 42
    assert {"tool": "hm_modeling_action", "action": "validate_recording", "route_name": "apply_constraint_spc"} in result["next_supported_actions"]
