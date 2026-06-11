"""Tests for blocked boundary-condition compatibility helpers."""

from program.tools import hm_boundary_safe, hm_keyword_skill


def _ok_execute(*args, **kwargs):
    return {"success": True, "response": "OK"}


def test_create_spc_on_nodes_executes_gui_templates(monkeypatch):
    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", _ok_execute)

    result = hm_boundary_safe.create_spc_on_nodes([1, 2, 3], collector_name="FIXED")

    assert result["success"] is True
    assert result["execution_allowed"] is True
    assert result["tcl_sent"] is True
    assert result["route_name"] == "apply_constraint_spc"
    assert result["target"] == "nodes"
    assert result["node_ids"] == [1, 2, 3]
    assert len(result["results"]) == 3


def test_create_spc_on_node_set_executes_gui_template(monkeypatch):
    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", _ok_execute)

    result = hm_boundary_safe.create_spc_on_node_set(42)

    assert result["success"] is True
    assert result["execution_allowed"] is True
    assert result["tcl_sent"] is True
    assert result["route_name"] == "apply_constraint_spc"
    assert result["target"] == "node_set"
    assert result["set_id"] == 42
