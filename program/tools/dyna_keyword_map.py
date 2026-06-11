"""Structured LS-DYNA keyword knowledge policy.

This module records the repository policy that manual distillation and
embeddings are retrieval aids, not execution sources. Execution must be
resolved through structured keyword/cardimage/dataname maps.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any

_MAP_PATH = Path(__file__).resolve().parents[2] / "templates" / "dyna_keyword_map.json"
_NOTES_PATH = Path(__file__).resolve().parents[2] / "templates" / "dyna_manual_notes.jsonl"

_GUI_TEMPLATE_EXECUTABLE_KEYWORDS = {
    "*MAT_ELASTIC",
    "*SECTION_SOLID",
    "*SECTION_SHELL",
    "*SECTION_BEAM",
    "*SECTION_DISCRETE",
    "*EOS_LINEAR_POLYNOMIAL",
    "*BOUNDARY_SPC",
    "*BOUNDARY_SPC_NODE",
    "*BOUNDARY_SPC_SET",
    "*LOAD_NODE",
    "*LOAD_NODE_SET",
    "*LOAD_SEGMENT",
    "*LOAD_SEGMENT_SET",
    "*LOAD_SHELL",
    "*LOAD_SHELL_SET",
}


@lru_cache(maxsize=1)
def load_dyna_keyword_map() -> dict[str, Any]:
    """Load the structured Dyna keyword policy map."""
    if not _MAP_PATH.exists():
        return {"version": 0, "policy": {}, "sources": {}, "execution_guardrails": {}}
    return json.loads(_MAP_PATH.read_text(encoding="utf-8"))


def embedding_execution_allowed() -> bool:
    """Return whether embedding/manual notes may drive execution directly."""
    guardrails = load_dyna_keyword_map().get("execution_guardrails", {})
    return bool(guardrails.get("allow_embedding_to_fill_execution_fields", False))


def list_manual_notes(limit: int = 20) -> list[dict[str, Any]]:
    """Read distilled manual notes for explanation/retrieval workflows."""
    if not _NOTES_PATH.exists():
        return []
    notes: list[dict[str, Any]] = []
    for line in _NOTES_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            notes.append(json.loads(line))
        if len(notes) >= limit:
            break
    return notes


@lru_cache(maxsize=1)
def load_keyword_index() -> dict[str, Any]:
    """Load structured keyword index referenced by the Dyna policy map."""
    path = Path(__file__).resolve().parents[2] / "templates" / "keyword_index.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_hm_dictionary() -> dict[str, Any]:
    """Load HyperMesh cardimage/dataname dictionary for keyword lookups."""
    path = Path(__file__).resolve().parents[2] / "templates" / "hm_dictionary.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_keyword(keyword: str) -> str:
    """Normalize LS-DYNA keyword names for structured lookup."""
    value = keyword.strip().upper()
    if value and not value.startswith("*"):
        value = f"*{value}"
    return value


def query_dyna_keyword(keyword: str) -> dict[str, Any]:
    """Return structured keyword/cardimage/manual-note guidance.

    This is a retrieval helper only. It never authorizes execution from manual
    notes or embedding hits.
    """
    normalized = normalize_keyword(keyword)
    keyword_index = load_keyword_index()
    dictionary = load_hm_dictionary()
    direct_route = _lookup_keyword_route(normalized)
    canonical_keyword = _canonical_keyword(normalized, direct_route)
    entry = _lookup_case_insensitive(keyword_index, normalized)
    if entry is None:
        entry = _lookup_case_insensitive(keyword_index, normalized.lstrip("*"))
    cardimage = _route_cardimage(direct_route) or _entry_cardimage(entry)
    entity_type = _route_entity_type(direct_route) or _entry_entity_type(entry)
    placeholders = _route_placeholders(direct_route) or _entry_placeholders(entry)
    hm_cardimage_candidates = _hm_cardimage_candidates(dictionary, normalized, entity_type)
    if cardimage:
        hm_cardimage_candidates = _dedupe_dicts(
            [
                {
                    "cardimage": cardimage,
                    "family": str((direct_route or {}).get("hm_family") or ""),
                    "source": "dyna_keyword_map.keyword_routes" if direct_route else "keyword_index",
                },
                *hm_cardimage_candidates,
            ],
            "cardimage",
        )
    datanames = _dictionary_datanames(dictionary, entity_type, cardimage)
    route_datanames = _route_datanames(direct_route)
    if route_datanames:
        datanames = sorted(dict.fromkeys([*route_datanames, *datanames]))
    dataname_candidates = _dataname_candidates(dictionary, placeholders)
    examples = _route_examples(direct_route)
    manual_refs = _route_manual_refs(direct_route)
    field_execution_status = _field_execution_status(
        direct_route=direct_route,
        placeholders=placeholders,
        dataname_candidates=dataname_candidates,
    )
    route_execution_ready = _route_execution_ready(direct_route, field_execution_status)
    template_execution_ready = _template_execution_ready(normalized)
    if template_execution_ready:
        route_execution_ready = True
    execution_decision = _execution_decision(
        keyword=normalized,
        direct_route=direct_route,
        cardimage=cardimage,
        entity_type=entity_type,
        field_execution_status=field_execution_status,
        execution_ready=route_execution_ready,
    )
    related_notes = _related_manual_notes(normalized, keyword, manual_refs)
    execution_ready = route_execution_ready
    advisory_only = _advisory_only_summary(
        dataname_candidates=dataname_candidates,
        examples=examples,
        manual_refs=manual_refs,
        manual_notes=related_notes,
    )

    return {
        "success": bool(entry or direct_route),
        "keyword": normalized,
        "canonical_keyword": canonical_keyword,
        "matched_alias": bool(direct_route and canonical_keyword != normalized),
        "known": bool(entry or direct_route),
        "entry": entry,
        "direct_route": direct_route,
        "cardimage": cardimage,
        "hm_cardimage_candidates": hm_cardimage_candidates,
        "entity_type": entity_type,
        "placeholders": placeholders,
        "datanames": datanames,
        "dataname_candidates": dataname_candidates,
        "examples": examples,
        "manual_refs": manual_refs,
        "field_execution_status": field_execution_status,
        "execution_decision": execution_decision,
        "execution_blockers": execution_decision.get("blocked_reasons", []),
        "advisory_only": advisory_only,
        "candidate_confidence": _candidate_confidence(
            direct_route=direct_route,
            cardimage=cardimage,
            hm_cardimage_candidates=hm_cardimage_candidates,
            datanames=datanames,
            dataname_candidates=dataname_candidates,
        ),
        "execution_ready": execution_ready,
        "suggestions": _keyword_suggestions(normalized, keyword_index, limit=8)
        if not bool(entry or direct_route)
        else [],
        "manual_notes": related_notes,
        "execution_allowed_from_embedding": embedding_execution_allowed(),
        "execution_policy": "structured_map_only",
    }


def _lookup_case_insensitive(mapping: Any, key: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    if key in mapping:
        return mapping[key]
    lower_key = key.lower()
    for candidate, value in mapping.items():
        if str(candidate).lower() == lower_key:
            return value
    return None


def _entry_cardimage(entry: Any) -> str | None:
    if isinstance(entry, dict):
        for key in ("cardimage", "card_image", "hm_cardimage"):
            if entry.get(key):
                return str(entry[key])
    return None


def _entry_entity_type(entry: Any) -> str | None:
    if isinstance(entry, dict):
        for key in ("entity_type", "entity", "hm_entity"):
            if entry.get(key):
                return str(entry[key])
    return None


def _entry_placeholders(entry: Any) -> list[str]:
    if not isinstance(entry, dict):
        return []
    placeholders = entry.get("placeholders") or entry.get("fields") or []
    if isinstance(placeholders, dict):
        return [str(key) for key in placeholders]
    if isinstance(placeholders, list):
        return [str(item) for item in placeholders]
    return []


def _lookup_keyword_route(keyword: str) -> dict[str, Any] | None:
    routes = load_dyna_keyword_map().get("keyword_routes", {})
    route = _lookup_case_insensitive(routes, keyword)
    if route:
        return route
    clean = keyword.strip().upper()
    for candidate in routes.values() if isinstance(routes, dict) else []:
        if not isinstance(candidate, dict):
            continue
        aliases = [str(item).upper() for item in candidate.get("aliases", [])]
        if clean in aliases:
            return candidate
    return None


def _canonical_keyword(keyword: str, route: dict[str, Any] | None) -> str:
    if isinstance(route, dict) and route.get("keyword"):
        return normalize_keyword(str(route["keyword"]))
    return normalize_keyword(keyword)


def _route_cardimage(route: dict[str, Any] | None) -> str | None:
    if isinstance(route, dict) and route.get("cardimage"):
        return str(route["cardimage"])
    return None


def _route_entity_type(route: dict[str, Any] | None) -> str | None:
    if isinstance(route, dict) and route.get("entity_type"):
        return str(route["entity_type"])
    return None


def _route_placeholders(route: dict[str, Any] | None) -> list[str]:
    if not isinstance(route, dict):
        return []
    fields = route.get("fields", [])
    if isinstance(fields, list):
        names = []
        for field in fields:
            if isinstance(field, dict) and field.get("field"):
                names.append(str(field["field"]))
            elif isinstance(field, str):
                names.append(field)
        return names
    if isinstance(fields, dict):
        return [str(key) for key in fields]
    return []


def _route_datanames(route: dict[str, Any] | None) -> list[str]:
    if not isinstance(route, dict):
        return []
    datanames: list[str] = []
    for field in route.get("fields", []):
        if isinstance(field, dict) and field.get("dataname"):
            datanames.append(str(field["dataname"]))
    return datanames


def _route_examples(route: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(route, dict):
        return []
    examples = route.get("examples", [])
    if not isinstance(examples, list):
        return []
    return [example for example in examples if isinstance(example, dict)]


def _route_manual_refs(route: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(route, dict):
        return []
    manual_refs = route.get("manual_refs", [])
    if not isinstance(manual_refs, list):
        return []
    return [manual_ref for manual_ref in manual_refs if isinstance(manual_ref, dict)]


def _related_manual_notes(
    normalized_keyword: str,
    original_keyword: str,
    manual_refs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    notes = list_manual_notes(limit=200)
    ref_ids = {
        str(manual_ref.get("ref_id"))
        for manual_ref in manual_refs
        if manual_ref.get("ref_id")
    }
    related: list[dict[str, Any]] = []
    for note in notes:
        if str(note.get("id") or "") in ref_ids:
            related.append(note)

    if len(related) < 5:
        for note in notes:
            serialized = json.dumps(note, ensure_ascii=False).lower()
            if (
                normalized_keyword.strip("*").lower() in serialized
                or original_keyword.strip().lower() in serialized
            ) and note not in related:
                related.append(note)
            if len(related) >= 5:
                break
    return related[:5]


def _field_execution_status(
    *,
    direct_route: dict[str, Any] | None,
    placeholders: list[str],
    dataname_candidates: dict[str, list[dict[str, str]]],
) -> dict[str, dict[str, Any]]:
    route_fields: dict[str, dict[str, Any]] = {}
    if isinstance(direct_route, dict):
        for field in direct_route.get("fields", []):
            if isinstance(field, dict) and field.get("field"):
                route_fields[str(field["field"])] = field

    status: dict[str, dict[str, Any]] = {}
    for placeholder in placeholders:
        route_field = route_fields.get(placeholder, {})
        dataname = route_field.get("dataname")
        route_status = str(route_field.get("status") or "")
        candidates = dataname_candidates.get(placeholder, [])
        executable = bool(dataname and route_status.endswith("verified"))
        if executable:
            reason = "verified_dataname"
        elif route_status == "requires_hm_recording":
            reason = "requires_hm_recording"
        elif candidates:
            reason = "advisory_candidates_only"
        else:
            reason = "no_dataname_candidate"
        status[placeholder] = {
            "field": placeholder,
            "dataname": dataname,
            "route_status": route_status or None,
            "candidate_count": len(candidates),
            "executable": executable,
            "reason": reason,
        }
    return status


def _execution_decision(
    *,
    keyword: str,
    direct_route: dict[str, Any] | None,
    cardimage: str | None,
    entity_type: str | None,
    field_execution_status: dict[str, dict[str, Any]],
    execution_ready: bool,
) -> dict[str, Any]:
    """Return a compact go/no-go decision for agents before any Tcl/K action."""
    route_status = str((direct_route or {}).get("status") or "")
    if execution_ready and _template_execution_ready(keyword):
        return {
            "state": "executable",
            "keyword": keyword,
            "route_status": route_status or "gui_template_verified",
            "cardimage": cardimage,
            "entity_type": entity_type,
            "allowed_execution_source": "structured_gui_tcl_template",
            "blocked_reasons": [],
            "required_verification": [],
            "advisory_candidates_are_executable": False,
        }
    unresolved_fields = [
        field
        for field, status in field_execution_status.items()
        if status.get("executable") is not True
    ]
    if execution_ready:
        return {
            "state": "executable",
            "keyword": keyword,
            "route_status": route_status,
            "cardimage": cardimage,
            "entity_type": entity_type,
            "allowed_execution_source": "structured_verified_map",
            "blocked_reasons": [],
            "required_verification": [],
            "advisory_candidates_are_executable": False,
        }

    blocked_reasons: list[str] = []
    if not isinstance(direct_route, dict):
        blocked_reasons.append("no_structured_keyword_route")
    elif route_status in {"keyword_index_only", "cardimage_verified"}:
        blocked_reasons.append("datanames_not_verified")
    elif route_status not in {"datanames_verified", "execution_verified"}:
        blocked_reasons.append("route_not_execution_verified")
    if not cardimage:
        blocked_reasons.append("cardimage_not_verified")
    if unresolved_fields:
        blocked_reasons.append("fields_require_hm_recording")
    if embedding_execution_allowed():
        blocked_reasons.append("embedding_execution_guardrail_open")

    return {
        "state": "blocked",
        "keyword": keyword,
        "route_status": route_status or None,
        "cardimage": cardimage,
        "entity_type": entity_type,
        "allowed_execution_source": "structured_verified_map",
        "blocked_reasons": sorted(dict.fromkeys(blocked_reasons)),
        "required_verification": [
            "Record the keyword card creation/edit in HyperMesh command recording.",
            "Verify the cardimage for the target HyperMesh profile.",
            "Verify every field dataname against the recorded Tcl or trusted local dictionary.",
            "Promote the route to datanames_verified or execution_verified only after tests prove the Tcl action.",
        ],
        "unresolved_fields": unresolved_fields,
        "advisory_candidates_are_executable": False,
    }


def _advisory_only_summary(
    *,
    dataname_candidates: dict[str, list[dict[str, str]]],
    examples: list[dict[str, Any]],
    manual_refs: list[dict[str, Any]],
    manual_notes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize non-executable evidence so agents do not promote it implicitly."""
    candidate_fields = sorted(dataname_candidates)
    return {
        "dataname_candidates": bool(candidate_fields),
        "dataname_candidate_fields": candidate_fields,
        "examples": bool(examples),
        "manual_refs": bool(manual_refs),
        "manual_notes": bool(manual_notes),
        "execution_allowed": False,
        "reason": (
            "Dictionary candidates, examples, manual refs, and distilled notes are advisory only; "
            "execution requires structured verified route fields with datanames."
        ),
    }


def _route_execution_ready(
    direct_route: dict[str, Any] | None,
    field_execution_status: dict[str, dict[str, Any]],
) -> bool:
    """Return whether a route is verified enough to drive execution.

    Advisory dictionary hits must never flip a Dyna keyword route into an
    executable state. Execution requires an explicit route flag plus verified
    datanames for every declared field.
    """
    if not isinstance(direct_route, dict):
        return False
    if direct_route.get("execution_ready") is not True:
        return False
    status = str(direct_route.get("status") or "")
    if status not in {"datanames_verified", "execution_verified"}:
        return False
    if not field_execution_status:
        return False
    return all(item.get("executable") is True for item in field_execution_status.values())


def _template_execution_ready(keyword: str) -> bool:
    """Allow curated GUI Tcl templates for requested card families.

    These templates still execute through the HyperMesh GUI listener and are
    not LS-DYNA backend K writers. The allow-list is intentionally family-level
    and local-template backed so agents cannot execute arbitrary keywords from
    manual notes or embeddings.
    """
    normalized = normalize_keyword(keyword)
    if normalized not in _GUI_TEMPLATE_EXECUTABLE_KEYWORDS:
        return False
    template_key = normalized.lstrip("*")
    template_path = Path(__file__).resolve().parents[2] / "templates" / "keyword"
    category = template_key.split("_", 1)[0].lower()
    return (template_path / category / f"{template_key}.tcl").exists()


def _candidate_confidence(
    *,
    direct_route: dict[str, Any] | None,
    cardimage: str | None,
    hm_cardimage_candidates: list[dict[str, str]],
    datanames: list[str],
    dataname_candidates: dict[str, list[dict[str, str]]],
) -> str:
    if direct_route and cardimage and datanames:
        route_datanames = _route_datanames(direct_route)
        if route_datanames:
            return "direct"
        return "cardimage_direct_dictionary_datanames_advisory"
    if direct_route and cardimage:
        return "cardimage_direct_datanames_unverified"
    if direct_route and hm_cardimage_candidates and dataname_candidates:
        return "cardimage_candidate_datanames_advisory"
    if direct_route and hm_cardimage_candidates:
        return "cardimage_candidate_only"
    if dataname_candidates and not cardimage:
        return "low"
    if dataname_candidates:
        return "advisory_candidates_only"
    return "none"


def _hm_cardimage_candidates(dictionary: dict[str, Any], keyword: str, entity_type: str | None) -> list[dict[str, str]]:
    """Infer possible HyperMesh cardimages without treating them as verified execution fields."""
    candidates: list[dict[str, str]] = []
    if entity_type == "mats":
        mat_table = dictionary.get("mats", {})
        for mat_id in _keyword_numeric_ids(keyword):
            card = f"MATL{mat_id}"
            if isinstance(mat_table, dict) and card in mat_table:
                candidates.append({"cardimage": card, "family": str(mat_table[card]), "source": "hm_dictionary.mats"})

    cardmenu = dictionary.get("cardmenuitem", {})
    clean_keyword = keyword.strip("*")
    if isinstance(cardmenu, dict) and clean_keyword in cardmenu:
        candidates.append(
            {
                "cardimage": str(cardmenu[clean_keyword]),
                "family": "",
                "source": "hm_dictionary.cardmenuitem",
            }
        )
    return _dedupe_dicts(candidates, "cardimage")


def _keyword_numeric_ids(keyword: str) -> list[int]:
    ids: list[int] = []
    for match in re.finditer(r"MAT[_ ]*0*(\d+)", keyword.upper()):
        ids.append(int(match.group(1)))
    return list(dict.fromkeys(ids))


def _dataname_candidates(dictionary: dict[str, Any], placeholders: list[str]) -> dict[str, list[dict[str, str]]]:
    """Find possible HyperMesh datanames for K fields across local lsd_fields."""
    lsd_fields = dictionary.get("lsd_fields", {})
    if not isinstance(lsd_fields, dict):
        return {}
    result: dict[str, list[dict[str, str]]] = {}
    for placeholder in placeholders:
        matches: list[dict[str, str]] = []
        for cardimage, fields in lsd_fields.items():
            if not isinstance(fields, dict) or placeholder not in fields:
                continue
            matches.append(
                {
                    "cardimage": str(cardimage),
                    "dataname": str(fields[placeholder]),
                    "source": "hm_dictionary.lsd_fields",
                }
            )
            if len(matches) >= 20:
                break
        if matches:
            result[placeholder] = matches
    return result


def _dedupe_dicts(items: list[dict[str, str]], key: str) -> list[dict[str, str]]:
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for item in items:
        value = item.get(key, "")
        if value in seen:
            continue
        seen.add(value)
        deduped.append(item)
    return deduped


def _keyword_suggestions(
    keyword: str,
    keyword_index: dict[str, Any],
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Suggest structured keyword candidates without making them executable."""
    query = normalize_keyword(keyword)
    query_clean = query.strip("*")
    candidates: dict[str, dict[str, Any]] = {}

    routes = load_dyna_keyword_map().get("keyword_routes", {})
    if isinstance(routes, dict):
        for route_name, route in routes.items():
            if not isinstance(route, dict):
                continue
            route_keyword = normalize_keyword(str(route.get("keyword") or route_name))
            names = [route_keyword, *[normalize_keyword(str(alias)) for alias in route.get("aliases", [])]]
            score = max(_keyword_similarity(query, name) for name in names)
            substring = any(query_clean in name.strip("*") or name.strip("*") in query_clean for name in names)
            if score >= 0.68 or substring:
                candidates[route_keyword] = {
                    "keyword": route_keyword,
                    "source": "dyna_keyword_map.keyword_routes",
                    "status": route.get("status"),
                    "cardimage": route.get("cardimage"),
                    "entity_type": route.get("entity_type"),
                    "score": round(score, 3),
                    "execution_ready": route.get("execution_ready") is True,
                    "execution_allowed": False,
                    "reason": "suggestion_only_requires_verified_route_query",
                }

    if isinstance(keyword_index, dict):
        for index_key, entry in keyword_index.items():
            candidate_keyword = normalize_keyword(str(index_key))
            score = _keyword_similarity(query, candidate_keyword)
            substring = query_clean in candidate_keyword.strip("*") or candidate_keyword.strip("*") in query_clean
            if score < 0.78 and not substring:
                continue
            existing = candidates.get(candidate_keyword)
            if existing and existing.get("source") == "dyna_keyword_map.keyword_routes":
                existing["score"] = max(float(existing.get("score") or 0.0), round(score, 3))
                continue
            candidates[candidate_keyword] = {
                "keyword": candidate_keyword,
                "source": "templates/keyword_index.json",
                "status": "keyword_index_only",
                "cardimage": _entry_cardimage(entry),
                "entity_type": _entry_entity_type(entry),
                "score": round(score, 3),
                "execution_ready": False,
                "execution_allowed": False,
                "reason": "suggestion_only_requires_structured_route_verification",
            }

    return sorted(candidates.values(), key=lambda item: (-float(item["score"]), str(item["keyword"])))[:limit]


def _keyword_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left.strip("*"), right.strip("*")).ratio()


def _dictionary_datanames(dictionary: dict[str, Any], entity_type: str | None, cardimage: str | None) -> list[str]:
    if not entity_type and not cardimage:
        return []
    found: list[str] = []
    stack: list[Any] = [dictionary]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            current_entity = str(current.get("entity_type") or current.get("entity") or "")
            current_card = str(current.get("cardimage") or current.get("card_image") or "")
            if (
                (not entity_type or current_entity.lower() == entity_type.lower())
                and (not cardimage or current_card.lower() == cardimage.lower())
            ):
                fields = current.get("datanames") or current.get("fields")
                if isinstance(fields, dict):
                    found.extend(str(key) for key in fields)
                elif isinstance(fields, list):
                    found.extend(str(item) for item in fields)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return sorted(dict.fromkeys(found))


def validate_dyna_keyword_map() -> dict[str, Any]:
    """Validate that keyword routes cannot silently authorize unsafe execution."""
    data = load_dyna_keyword_map()
    errors: list[str] = []
    warnings: list[str] = []
    allowed_statuses = {
        "keyword_index_only",
        "cardimage_verified",
        "datanames_verified",
        "execution_verified",
    }
    routes = data.get("keyword_routes", {})
    if not isinstance(routes, dict):
        errors.append("keyword_routes must be an object.")
        routes = {}

    guardrails = data.get("execution_guardrails", {})
    if guardrails.get("allow_embedding_to_fill_execution_fields") is not False:
        errors.append("allow_embedding_to_fill_execution_fields must be false.")
    manual_notes = list_manual_notes(limit=10000)
    manual_note_ids = {
        str(note.get("id"))
        for note in manual_notes
        if isinstance(note, dict) and note.get("id")
    }
    for index, note in enumerate(manual_notes):
        if not isinstance(note, dict):
            errors.append(f"manual_notes[{index}]: note must be an object.")
            continue
        if note.get("execution_allowed") is not False:
            errors.append(f"manual_notes[{index}]: execution_allowed must be false.")

    for route_name, route in routes.items():
        if not isinstance(route, dict):
            errors.append(f"{route_name}: route must be an object.")
            continue
        status = str(route.get("status") or "")
        if status not in allowed_statuses:
            errors.append(f"{route_name}: unsupported status {status!r}.")
        keyword = str(route.get("keyword") or "")
        if not keyword.startswith("*"):
            errors.append(f"{route_name}: keyword must start with '*'.")
        aliases = route.get("aliases", [])
        if aliases is not None and not isinstance(aliases, list):
            errors.append(f"{route_name}: aliases must be a list when present.")
            aliases = []
        for index, alias in enumerate(aliases):
            if not isinstance(alias, str) or not alias.startswith("*"):
                errors.append(f"{route_name}.aliases[{index}]: alias must be a string starting with '*'.")
        fields = route.get("fields", [])
        if not isinstance(fields, list):
            errors.append(f"{route_name}: fields must be a list.")
            fields = []
        execution_ready = route.get("execution_ready") is True
        verified_datanames = [
            field for field in fields
            if isinstance(field, dict)
            and field.get("field")
            and field.get("dataname")
            and str(field.get("status") or "").endswith("verified")
        ]
        missing_datanames = [
            str(field.get("field"))
            for field in fields
            if isinstance(field, dict) and field.get("field") and not field.get("dataname")
        ]
        for field in fields:
            if not isinstance(field, dict):
                continue
            field_name = str(field.get("field") or "<unknown>")
            field_status = str(field.get("status") or "")
            has_dataname = bool(field.get("dataname"))
            if field_status.endswith("verified") and not has_dataname:
                errors.append(f"{route_name}.{field_name}: verified field status requires dataname.")
            if has_dataname and not field_status.endswith("verified"):
                warnings.append(
                    f"{route_name}.{field_name}: dataname is present but field status is not verified."
                )
        if execution_ready and missing_datanames:
            errors.append(
                f"{route_name}: execution_ready=true but fields lack verified datanames: "
                + ", ".join(missing_datanames)
            )
        if execution_ready and status not in {"datanames_verified", "execution_verified"}:
            errors.append(
                f"{route_name}: execution_ready=true requires datanames_verified or execution_verified status."
            )
        if execution_ready and len(verified_datanames) != len(fields):
            errors.append(f"{route_name}: execution_ready=true requires every field to have a verified dataname.")
        if status in {"datanames_verified", "execution_verified"} and not verified_datanames:
            errors.append(f"{route_name}: {status} requires at least one verified dataname.")
        if status == "cardimage_verified" and not route.get("cardimage"):
            errors.append(f"{route_name}: cardimage_verified requires cardimage.")
        if status == "keyword_index_only" and route.get("cardimage"):
            warnings.append(f"{route_name}: keyword_index_only route has a cardimage; consider cardimage_verified.")
        examples = route.get("examples")
        if not isinstance(examples, list) or not examples:
            warnings.append(f"{route_name}: route should include planning-only examples.")
        else:
            for index, example in enumerate(examples):
                if not isinstance(example, dict):
                    warnings.append(f"{route_name}.examples[{index}]: example should be an object.")
                    continue
                if example.get("execution_allowed") is not False:
                    errors.append(f"{route_name}.examples[{index}]: execution_allowed must be false.")
                if example.get("purpose") not in {None, "planning_only", "explanation_only"}:
                    errors.append(
                        f"{route_name}.examples[{index}]: purpose must be planning_only or explanation_only."
                    )
        manual_refs = route.get("manual_refs")
        if not isinstance(manual_refs, list) or not manual_refs:
            warnings.append(f"{route_name}: route should include manual_refs.")
        else:
            for index, manual_ref in enumerate(manual_refs):
                if not isinstance(manual_ref, dict):
                    warnings.append(f"{route_name}.manual_refs[{index}]: manual_ref should be an object.")
                    continue
                if manual_ref.get("role") != "explanation_only":
                    errors.append(f"{route_name}.manual_refs[{index}]: role must be explanation_only.")
                if manual_ref.get("execution_allowed") not in {None, False}:
                    errors.append(f"{route_name}.manual_refs[{index}]: execution_allowed must be false when present.")
                ref_id = manual_ref.get("ref_id")
                if not isinstance(ref_id, str) or not ref_id:
                    errors.append(f"{route_name}.manual_refs[{index}]: ref_id is required.")
                elif ref_id not in manual_note_ids:
                    errors.append(f"{route_name}.manual_refs[{index}]: ref_id not found in manual notes: {ref_id}.")

    return {
        "success": not errors,
        "errors": errors,
        "warnings": warnings,
        "routes_checked": len(routes),
        "embedding_execution_allowed": embedding_execution_allowed(),
    }


def dyna_keyword_policy_summary() -> dict[str, Any]:
    """Return a compact summary of Dyna keyword knowledge policy."""
    data = load_dyna_keyword_map()
    validation = validate_dyna_keyword_map()
    return {
        "version": data.get("version", 0),
        "embedding_execution_allowed": embedding_execution_allowed(),
        "embedding_role": data.get("policy", {}).get("embedding_role"),
        "lookup_flow": data.get("lookup_flow", []),
        "sources": data.get("sources", {}),
        "keyword_routes_count": len(data.get("keyword_routes", {})) if isinstance(data.get("keyword_routes"), dict) else 0,
        "notes_count_sample": len(list_manual_notes()),
        "map_valid": validation["success"],
        "map_errors": validation["errors"],
    }
