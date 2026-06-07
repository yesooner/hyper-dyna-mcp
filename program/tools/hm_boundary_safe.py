"""Safe boundary condition creation for HyperMesh.

Avoids *loadcreate which causes segfaults in HyperMesh 2021.
Uses loadcollector + loadstep approach instead.
"""

from __future__ import annotations

from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_gui import execute_tcl_gui


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
    """Create SPC boundary conditions on nodes using safe method.

    Args:
        node_ids: List of node IDs to constrain
        dofx/y/z: Translation DOF constraints (1=fixed, 0=free)
        dofrx/y/z: Rotation DOF constraints (1=fixed, 0=free)
        collector_name: Name for the load collector
        timeout: Socket timeout

    Returns:
        dict with success status and details
    """
    if not node_ids:
        return {"success": False, "error": "No node IDs provided"}

    # Step 1: Create load collector
    script1 = f'*createentity loadcols cardimage=SPC name={collector_name}'
    r1 = execute_tcl_gui(script1, timeout=timeout)
    if not r1.get("success"):
        return {"success": False, "error": "Failed to create load collector"}

    # Step 2: Set as current collector
    script2 = f'*currentcollector loadcols "{collector_name}"'
    r2 = execute_tcl_gui(script2, timeout=timeout)
    if not r2.get("success"):
        return {"success": False, "error": "Failed to set current collector"}

    # Step 3: Create node mark
    node_str = " ".join(str(n) for n in node_ids)
    script3 = f'*createmark nodes 1 {node_str}'
    r3 = execute_tcl_gui(script3, timeout=timeout)
    if not r3.get("success"):
        return {"success": False, "error": "Failed to mark nodes"}

    # Step 4: Create SPC using *loadcreateonentity (safer than *loadcreate)
    # *loadcreateonentity syntax: type mark_id mask dofx dofy dofz dofrx dofrx dofrz
    mask = dofx + 2 * dofy + 4 * dofz + 8 * dofrx + 16 * dofry + 32 * dofrz
    script4 = f'*loadcreateonentity nodes 1 1 {mask} {dofx} {dofy} {dofz} {dofrx} {dofry} {dofrz}'
    r4 = execute_tcl_gui(script4, timeout=timeout)

    if not r4.get("success"):
        # Fallback: try individual node SPC
        logger.warning("*loadcreateonentity failed, trying individual node SPC")
        success_count = 0
        for nid in node_ids:
            script5 = f'*createmark nodes 1 {nid}\n*loadcreateonentity nodes 1 1 {mask} {dofx} {dofy} {dofz} {dofrx} {dofry} {dofrz}'
            r5 = execute_tcl_gui(script5, timeout=timeout)
            if r5.get("success"):
                success_count += 1

        return {
            "success": success_count > 0,
            "method": "individual_node_spc",
            "nodes_processed": success_count,
            "total_nodes": len(node_ids),
        }

    return {
        "success": True,
        "method": "bulk_spc",
        "nodes_processed": len(node_ids),
        "collector_name": collector_name,
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
    """Create SPC on a node set (safer than individual nodes).

    Args:
        set_id: Node set ID
        dofx/y/z: Translation DOF constraints
        dofrx/y/z: Rotation DOF constraints
        timeout: Socket timeout

    Returns:
        dict with success status
    """
    # Create load collector
    script1 = f'*createentity loadcols cardimage=SPC name=SPC_SET_{set_id}'
    r1 = execute_tcl_gui(script1, timeout=timeout)
    if not r1.get("success"):
        return {"success": False, "error": "Failed to create load collector"}

    # Set as current
    script2 = f'*currentcollector loadcols "SPC_SET_{set_id}"'
    r2 = execute_tcl_gui(script2, timeout=timeout)

    # Create SPC on set
    mask = dofx + 2 * dofy + 4 * dofz + 8 * dofrx + 16 * dofry + 32 * dofrz
    script3 = f'*createmark nodes 1 "by set" {set_id}\n*loadcreateonentity nodes 1 1 {mask} {dofx} {dofy} {dofz} {dofrx} {dofry} {dofrz}'
    r3 = execute_tcl_gui(script3, timeout=timeout)

    return {
        "success": r3.get("success", False),
        "set_id": set_id,
        "collector_name": f"SPC_SET_{set_id}",
    }
