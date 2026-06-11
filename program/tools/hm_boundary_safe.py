"""Compatibility helpers for HyperMesh boundary-condition routes."""

from __future__ import annotations

from typing import Any

def _spc_params(
    *,
    cid: int = 0,
    dofx: int,
    dofy: int,
    dofz: int,
    dofrx: int,
    dofry: int,
    dofrz: int,
) -> dict[str, int]:
    return {
        "CID": cid,
        "DOFX": dofx,
        "DOFY": dofy,
        "DOFZ": dofz,
        "DOFRX": dofrx,
        "DOFRY": dofry,
        "DOFRZ": dofrz,
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
    """Create SPC cards for explicit node ids through GUI Tcl templates."""
    from program.tools.hm_keyword_skill import hm_set_keyword

    results = []
    base = _spc_params(dofx=dofx, dofy=dofy, dofz=dofz, dofrx=dofrx, dofry=dofry, dofrz=dofrz)
    for node_id in node_ids:
        params = {"NODEID": int(node_id), **base}
        results.append(hm_set_keyword("BOUNDARY_SPC", params, timeout=timeout))
    success = all(result.get("success") for result in results)
    return {
        "success": success,
        "target": "nodes",
        "node_ids": list(node_ids),
        "collector_name": collector_name,
        "execution_allowed": True,
        "tcl_sent": success,
        "route_name": "apply_constraint_spc",
        "keyword": "BOUNDARY_SPC",
        "results": results,
    }


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
    """Create an SPC card for a node set through GUI Tcl templates."""
    from program.tools.hm_keyword_skill import hm_set_keyword

    params = {
        "NSID": int(set_id),
        **_spc_params(dofx=dofx, dofy=dofy, dofz=dofz, dofrx=dofrx, dofry=dofry, dofrz=dofrz),
    }
    result = hm_set_keyword("BOUNDARY_SPC_SET", params, timeout=timeout)
    result.update(
        {
            "target": "node_set",
            "set_id": set_id,
            "collector_name": f"SPC_SET_{set_id}",
            "route_name": "apply_constraint_spc",
            "execution_allowed": result.get("success") is True,
        }
    )
    result.setdefault("tcl_sent", result.get("success") is True)
    return result
