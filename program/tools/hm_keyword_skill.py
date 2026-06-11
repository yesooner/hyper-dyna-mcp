"""MCP Skill for LS-DYNA keyword operations in HyperMesh.

Provides tools for AI agents to set/query/help LS-DYNA keywords
via Tcl templates sent to HyperMesh GUI.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from program.tools.hm_template_engine import HmTemplateEngine
from program.tools.hm_gui import execute_tcl_gui, _check_file_io
from program.tools.dyna_keyword_map import query_dyna_keyword
from program.tools.hm_policy import check_meshing_rules

_engine = HmTemplateEngine()

# --- Manual reference ---
MANUAL_DIR = Path(__file__).resolve().parents[2] / "lsdyna-maunal"
REF_FILE = Path(__file__).resolve().parents[2] / "ref" / "lsdyna_keyword_reference.md"


def hm_set_keyword(
    keyword: str,
    params: dict[str, Any],
    timeout: int = 30,
) -> dict[str, Any]:
    """Set a single LS-DYNA keyword in HyperMesh.

    Args:
        keyword: LS-DYNA keyword name (e.g., "MAT_ELASTIC")
        params: Parameter values (e.g., {"MID": 1, "RHO": 7.85e-9})
        timeout: Socket timeout in seconds

    Returns:
        dict with success status and details.
    """
    keyword = keyword.upper().lstrip("*")
    policy = query_dyna_keyword(keyword)
    if policy.get("execution_ready") is not True:
        return {
            "success": False,
            "keyword": keyword,
            "params": params,
            "error_type": "dyna_keyword_execution_not_verified",
            "error": (
                "This LS-DYNA keyword route is not execution-ready. "
                "Use dyna_keyword_query for cardimage/dataname evidence and promote the route only after "
                "HyperMesh command recording verifies every required dataname."
            ),
            "execution_ready": policy.get("execution_ready"),
            "execution_allowed": False,
            "tcl_sent": False,
            "execution_decision": policy.get("execution_decision"),
            "execution_blockers": policy.get("execution_blockers"),
            "advisory_only": policy.get("advisory_only"),
            "required_verification": (policy.get("execution_decision") or {}).get("required_verification", []),
        }

    if not _engine.has_template(keyword):
        return {
            "success": False,
            "error": f"No template for keyword: {keyword}",
            "suggestion": f"Use hm_keyword_help('{keyword}') to check if it exists",
        }

    try:
        script = _engine.render(keyword, params)
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Template render error: {e}"}

    violation = check_meshing_rules(script)
    if violation:
        message = violation.get("error", violation.get("message", "Rule violation"))
        return {
            "success": False,
            "keyword": keyword,
            "params": params,
            "error_type": violation.get("error_type", "mesh_route_not_verified"),
            "error": message,
            "policy_violation": violation.get("policy_violation", True),
            "blocked_command": violation.get("blocked_command"),
            "blocked_route_name": violation.get("blocked_route_name"),
            "execution_allowed": violation.get("execution_allowed", False),
            "tcl_sent": violation.get("tcl_sent", False),
            "required_tool": "hm_modeling_action",
        }

    file_io_error = _check_file_io(script)
    if file_io_error:
        return {
            "success": False,
            "keyword": keyword,
            "params": params,
            "error_type": "file_io_route_not_allowed",
            "error": file_io_error,
            "execution_allowed": False,
            "tcl_sent": False,
            "required_tool": "hm_auto_save",
        }

    # Execute line by line with segfault protection
    lines = [l.strip() for l in script.split("\n") if l.strip() and not l.strip().startswith("#")]
    last_result = {"success": True, "response": ""}
    count = 0
    for line in lines:
        result = execute_tcl_gui(line, timeout=timeout, enforce_rules=False)
        count += 1
        if not result.get("success"):
            # Check for connection loss (segfault)
            err = str(result.get("error", ""))
            if "connection" in err.lower() or "refused" in err.lower():
                return {"success": False, "keyword": keyword, "params": params,
                        "error": f"HyperMesh connection lost after {count} commands (possible segfault)",
                        "response": ""}
            last_result = result
        time.sleep(0.05)

    return {
        "success": last_result.get("success", False),
        "keyword": keyword,
        "params": params,
        "response": last_result.get("response", ""),
        "error": last_result.get("error"),
        "next_steps": [
            "Call hm_auto_save(step_name='...') to save the model",
            "Use hm_set_keyword for next keyword (e.g., SECTION_SOLID, PART, CONTACT_...)",
            "Use hm_keyword_map('category') to discover available keywords",
        ],
    }


def hm_batch_keywords(
    steps: list[dict[str, Any]],
    timeout: int = 60,
) -> dict[str, Any]:
    """Set multiple LS-DYNA keywords in sequence.

    Args:
        steps: List of {"keyword": "MAT_ELASTIC", "params": {...}}
        timeout: Socket timeout in seconds

    Returns:
        dict with results for each step.
    """
    results = []
    for step in steps:
        keyword = step.get("keyword", "")
        params = step.get("params", {})
        r = hm_set_keyword(keyword, params, timeout=timeout)
        results.append(r)
        if not r.get("success"):
            return {
                "success": False,
                "error": f"Failed at keyword: {keyword}",
                "step_results": results,
            }

    return {
        "success": True,
        "n_keywords": len(results),
        "step_results": results,
    }


def hm_check_model(timeout: int = 15) -> dict[str, Any]:
    """Check current model state in HyperMesh.

    Returns:
        dict with model info (components, nodes, elements, materials, etc.)
    """
    script = '''
    set info {}
    catch {
        *createmark components 1 "all"
        dict set info components [hm_getmark components 1]
    }
    catch {
        *createmark nodes 1 "all"
        dict set info nodes [hm_getmark nodes 1]
    }
    catch {
        *createmark elements 1 "all"
        dict set info elements [hm_getmark elements 1]
    }
    catch {
        *createmark mats 1 "all"
        dict set info materials [hm_getmark mats 1]
    }
    catch {
        *createmark props 1 "all"
        dict set info properties [hm_getmark props 1]
    }
    catch {
        *createmark groups 1 "all"
        dict set info groups [hm_getmark groups 1]
    }
    puts "MODEL_INFO=$info"
    '''

    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "response": result.get("response", ""),
    }


def hm_query_keyword(
    keyword: str,
    entity_id: int | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Query a keyword's current settings in HyperMesh.

    Args:
        keyword: LS-DYNA keyword name
        entity_id: Entity ID to query (optional)

    Returns:
        dict with current keyword settings.
    """
    keyword = keyword.upper().lstrip("*")
    info = _engine.get_template_info(keyword)

    if not info.get("exists"):
        return {"success": False, "error": f"No template for: {keyword}"}

    # Build query script based on keyword type
    placeholders = info.get("placeholders", [])
    id_field = None
    entity_type = "cards"

    if keyword.startswith("MAT_"):
        id_field = "MID"
        entity_type = "mats"
    elif keyword.startswith("SECTION_"):
        id_field = "SECID"
        entity_type = "props"
    elif keyword.startswith("PART"):
        id_field = "PID"
        entity_type = "comps"
    elif keyword.startswith("CONTACT_") or keyword.startswith("BOUNDARY_") or keyword.startswith("LOAD_") or keyword.startswith("SET_"):
        id_field = "SID"
        entity_type = "groups"

    if entity_id and id_field:
        # Query specific entity
        query_parts = []
        for p in placeholders:
            if p != id_field:
                query_parts.append(f'catch {{puts "{p}=[hm_getvalue {entity_type} id={entity_id} dataname={p}]"}}')
        script = "\n".join(query_parts)
    else:
        # List all entities of this type
        script = f'''
        *createmark {entity_type} 1 "all"
        set ids [hm_getmark {entity_type} 1]
        puts "{entity_type} IDs: $ids"
        '''

    result = execute_tcl_gui(script, timeout=timeout)
    return {
        "success": result.get("success", False),
        "keyword": keyword,
        "entity_id": entity_id,
        "response": result.get("response", ""),
    }


def hm_keyword_help(keyword: str) -> dict[str, Any]:
    """Get help text for a keyword from the manual reference.

    Args:
        keyword: LS-DYNA keyword name

    Returns:
        dict with keyword description, parameters, and manual reference.
    """
    keyword = keyword.upper().lstrip("*")

    # Check template
    info = _engine.get_template_info(keyword)

    # Search in reference file
    ref_text = ""
    if REF_FILE.exists():
        content = REF_FILE.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if f"`*{keyword}`" in line:
                ref_text = line.strip()
                break

    # Search in manual (first volume)
    manual_page = None
    if REF_FILE.exists():
        content = REF_FILE.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if f"`*{keyword}`" in line and "p." in line:
                import re
                match = re.search(r"p\.(\d+)", line)
                if match:
                    manual_page = int(match.group(1))
                break

    return {
        "keyword": keyword,
        "exists": info.get("exists", False),
        "description": info.get("description", ""),
        "parameters": info.get("parameters", ""),
        "placeholders": info.get("placeholders", []),
        "reference": ref_text,
        "manual_page": manual_page,
        "manual_volume": "I" if manual_page and manual_page < 4000 else "II" if manual_page else None,
    }
