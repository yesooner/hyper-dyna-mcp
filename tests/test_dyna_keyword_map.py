"""Tests for structured Dyna keyword lookup policy."""

from program.tools import dyna_keyword_map
from program.tools.dyna_keyword_map import (
    dyna_keyword_policy_summary,
    embedding_execution_allowed,
    normalize_keyword,
    query_dyna_keyword,
    validate_dyna_keyword_map,
)


def test_normalize_keyword_accepts_starless_input():
    assert normalize_keyword("mat_3") == "*MAT_3"


def test_query_dyna_keyword_uses_structured_index_not_embedding():
    result = query_dyna_keyword("*MAT_3")

    assert result["success"] is True
    assert result["known"] is True
    assert result["keyword"] == "*MAT_3"
    assert result["canonical_keyword"] == "*MAT_3"
    assert result["matched_alias"] is False
    assert result["suggestions"] == []
    assert result["entry"]["category"] == "mat"
    assert result["placeholders"] == ["E", "MID", "PR", "RHO"]
    assert result["direct_route"]["status"] == "cardimage_verified"
    assert result["cardimage"] == "MATL3"
    assert any(item["cardimage"] == "MATL3" for item in result["hm_cardimage_candidates"])
    assert "E" in result["dataname_candidates"]
    assert result["examples"][0]["execution_allowed"] is False
    assert result["manual_refs"][0]["role"] == "explanation_only"
    assert result["manual_notes"][0]["id"] == "manual_note:mat_3_plastic_kinematic"
    assert result["manual_notes"][0]["execution_allowed"] is False
    assert result["candidate_confidence"] == "cardimage_direct_datanames_unverified"
    assert result["execution_ready"] is False
    assert result["field_execution_status"]["E"]["executable"] is False
    assert result["field_execution_status"]["E"]["reason"] == "requires_hm_recording"
    assert result["field_execution_status"]["MID"]["route_status"] == "requires_hm_recording"
    assert result["field_execution_status"]["RHO"]["candidate_count"] == 0
    assert result["execution_decision"]["state"] == "blocked"
    assert result["execution_decision"]["allowed_execution_source"] == "structured_verified_map"
    assert result["execution_decision"]["advisory_candidates_are_executable"] is False
    assert "datanames_not_verified" in result["execution_decision"]["blocked_reasons"]
    assert "fields_require_hm_recording" in result["execution_decision"]["blocked_reasons"]
    assert result["execution_decision"]["unresolved_fields"] == ["E", "MID", "PR", "RHO"]
    assert result["execution_blockers"] == result["execution_decision"]["blocked_reasons"]
    assert result["advisory_only"]["execution_allowed"] is False
    assert result["advisory_only"]["dataname_candidates"] is True
    assert result["advisory_only"]["dataname_candidate_fields"] == ["E", "MID", "PR"]
    assert result["advisory_only"]["examples"] is True
    assert result["advisory_only"]["manual_refs"] is True
    assert result["advisory_only"]["manual_notes"] is True
    assert result["execution_allowed_from_embedding"] is False
    assert result["execution_policy"] == "structured_map_only"
    assert embedding_execution_allowed() is False


def test_query_dyna_keyword_alias_uses_direct_route():
    result = query_dyna_keyword("*MAT_003")

    assert result["success"] is True
    assert result["known"] is True
    assert result["direct_route"]["keyword"] == "*MAT_3"
    assert result["canonical_keyword"] == "*MAT_3"
    assert result["matched_alias"] is True
    assert result["cardimage"] == "MATL3"
    assert result["execution_ready"] is False


def test_query_unknown_keyword_returns_non_executable_suggestions():
    result = query_dyna_keyword("LOAD_BLAS")

    assert result["success"] is False
    assert result["known"] is False
    assert result["canonical_keyword"] == "*LOAD_BLAS"
    assert result["matched_alias"] is False
    assert result["execution_ready"] is False
    assert result["execution_decision"]["state"] == "blocked"
    assert "no_structured_keyword_route" in result["execution_blockers"]
    assert result["suggestions"]
    first = result["suggestions"][0]
    assert first["keyword"] == "*LOAD_BLAST"
    assert first["source"] == "dyna_keyword_map.keyword_routes"
    assert first["cardimage"] == "LOAD_BLAST"
    assert first["execution_allowed"] is False
    assert first["execution_ready"] is False


def test_query_control_termination_is_retrieval_only_until_verified():
    result = query_dyna_keyword("CONTROL_TERMINATION")

    assert result["success"] is True
    assert result["known"] is True
    assert result["keyword"] == "*CONTROL_TERMINATION"
    assert result["entity_type"] == "cards"
    assert result["placeholders"] == ["DTMIN", "ENDCYC", "ENDENG", "ENDMAS", "ENDTIM"]
    assert result["direct_route"]["status"] == "keyword_index_only"
    assert result["cardimage"] is None
    assert result["hm_cardimage_candidates"][0]["cardimage"] == "Termin"
    assert result["examples"][0]["execution_allowed"] is False
    assert result["manual_refs"][0]["ref_id"] == "manual_note:control_termination_overview"
    assert result["manual_notes"][0]["id"] == "manual_note:control_termination_overview"
    assert result["candidate_confidence"] == "cardimage_candidate_datanames_advisory"
    assert result["execution_ready"] is False
    assert result["field_execution_status"]["ENDTIM"]["executable"] is False
    assert result["field_execution_status"]["ENDTIM"]["reason"] == "requires_hm_recording"
    assert result["execution_decision"]["state"] == "blocked"
    assert result["execution_decision"]["cardimage"] is None
    assert "cardimage_not_verified" in result["execution_decision"]["blocked_reasons"]
    assert "datanames_not_verified" in result["execution_decision"]["blocked_reasons"]
    assert result["advisory_only"]["dataname_candidate_fields"] == [
        "DTMIN",
        "ENDCYC",
        "ENDENG",
        "ENDMAS",
        "ENDTIM",
    ]
    assert result["execution_decision"]["unresolved_fields"] == [
        "DTMIN",
        "ENDCYC",
        "ENDENG",
        "ENDMAS",
        "ENDTIM",
    ]


def test_query_database_binary_d3plot_is_cardimage_verified_but_not_executable():
    result = query_dyna_keyword("DATABASE_BINARY_D3PLOT")

    assert result["success"] is True
    assert result["known"] is True
    assert result["keyword"] == "*DATABASE_BINARY_D3PLOT"
    assert result["entity_type"] == "cards"
    assert result["cardimage"] == "DBplot"
    assert result["direct_route"]["status"] == "cardimage_verified"
    assert result["placeholders"] == ["DT", "TSTART", "TTERM", "LCDT"]
    assert result["examples"][0]["execution_allowed"] is False
    assert result["manual_refs"][0]["ref_id"] == "manual_note:database_binary_d3plot_overview"
    assert result["manual_notes"][0]["id"] == "manual_note:database_binary_d3plot_overview"
    assert result["execution_ready"] is False
    assert result["execution_decision"]["state"] == "blocked"
    assert result["execution_decision"]["cardimage"] == "DBplot"
    assert "datanames_not_verified" in result["execution_decision"]["blocked_reasons"]
    assert result["execution_decision"]["advisory_candidates_are_executable"] is False
    assert all(item["executable"] is False for item in result["field_execution_status"].values())


def test_query_control_timestep_is_structured_but_not_executable():
    result = query_dyna_keyword("CONTROL_TIMESTEP")

    assert result["success"] is True
    assert result["known"] is True
    assert result["keyword"] == "*CONTROL_TIMESTEP"
    assert result["entity_type"] == "cards"
    assert result["cardimage"] == "Timestep"
    assert result["direct_route"]["status"] == "cardimage_verified"
    assert result["placeholders"] == [
        "DTINIT",
        "TSSFAC",
        "ISDO",
        "TSLIMT",
        "DT2MS",
        "LCTM",
        "ERODE",
        "MS1ST",
    ]
    assert result["manual_refs"][0]["ref_id"] == "manual_note:control_timestep_overview"
    assert result["manual_notes"][0]["id"] == "manual_note:control_timestep_overview"
    assert result["manual_notes"][0]["execution_allowed"] is False
    assert result["execution_ready"] is False
    assert result["execution_decision"]["state"] == "blocked"
    assert "datanames_not_verified" in result["execution_decision"]["blocked_reasons"]
    assert result["execution_decision"]["advisory_candidates_are_executable"] is False
    assert all(item["executable"] is False for item in result["field_execution_status"].values())


def test_query_blast_setup_keywords_are_structured_but_not_executable():
    initial = query_dyna_keyword("INITIAL_DETONATION")
    blast = query_dyna_keyword("LOAD_BLAST")

    assert initial["success"] is True
    assert initial["cardimage"] == "INITIAL_DETONATION"
    assert initial["entity_type"] == "groups"
    assert initial["manual_notes"][0]["id"] == "manual_note:initial_detonation_overview"
    assert initial["execution_ready"] is False
    assert initial["execution_decision"]["state"] == "blocked"
    assert initial["field_execution_status"]["SETID"]["executable"] is False

    assert blast["success"] is True
    assert blast["cardimage"] == "LOAD_BLAST"
    assert blast["entity_type"] == "groups"
    assert blast["manual_notes"][0]["id"] == "manual_note:load_blast_overview"
    assert blast["execution_ready"] is False
    assert blast["execution_decision"]["state"] == "blocked"
    assert blast["field_execution_status"]["SID"]["executable"] is False


def test_query_dyna_keyword_dictionary_datanames_stay_advisory(monkeypatch):
    dictionary_with_unverified_datanames = {
        "mats": {"MATL3": "ELASTIC-PLASTIC"},
        "cards": [
            {
                "entity_type": "mats",
                "cardimage": "MATL3",
                "datanames": ["E", "MID", "PR", "RHO"],
            }
        ],
    }
    monkeypatch.setattr(
        dyna_keyword_map,
        "load_hm_dictionary",
        lambda: dictionary_with_unverified_datanames,
    )

    result = query_dyna_keyword("*MAT_3")

    assert result["datanames"] == ["E", "MID", "PR", "RHO"]
    assert result["candidate_confidence"] == "cardimage_direct_dictionary_datanames_advisory"
    assert result["execution_ready"] is False
    assert all(item["executable"] is False for item in result["field_execution_status"].values())
    assert result["execution_decision"]["state"] == "blocked"
    assert result["execution_decision"]["advisory_candidates_are_executable"] is False


def test_query_unknown_keyword_is_explicitly_unknown():
    result = query_dyna_keyword("*DOES_NOT_EXIST_FOR_HDM")

    assert result["success"] is False
    assert result["known"] is False
    assert result["field_execution_status"] == {}
    assert result["execution_decision"]["state"] == "blocked"
    assert "no_structured_keyword_route" in result["execution_decision"]["blocked_reasons"]
    assert result["execution_allowed_from_embedding"] is False


def test_execution_decision_can_be_executable_only_with_verified_route(monkeypatch):
    verified_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_SAFE": {
                "status": "datanames_verified",
                "keyword": "*MAT_SAFE",
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": "LSD_E", "status": "dataname_verified"},
                ],
                "execution_ready": True,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: verified_map)
    monkeypatch.setattr(
        dyna_keyword_map,
        "load_keyword_index",
        lambda: {"*MAT_SAFE": {"category": "mat", "entity_type": "mats", "placeholders": ["E"]}},
    )
    monkeypatch.setattr(dyna_keyword_map, "load_hm_dictionary", lambda: {})

    result = query_dyna_keyword("*MAT_SAFE")

    assert result["execution_ready"] is True
    assert result["execution_decision"]["state"] == "executable"
    assert result["execution_decision"]["blocked_reasons"] == []
    assert result["execution_decision"]["advisory_candidates_are_executable"] is False


def test_dyna_keyword_map_validation_keeps_execution_guardrails_closed():
    validation = validate_dyna_keyword_map()
    summary = dyna_keyword_policy_summary()

    assert validation["success"] is True
    assert validation["errors"] == []
    assert validation["embedding_execution_allowed"] is False
    assert validation["routes_checked"] >= 2
    assert summary["map_valid"] is True
    assert summary["map_errors"] == []


def test_dyna_keyword_map_validation_rejects_executable_manual_notes(monkeypatch):
    monkeypatch.setattr(
        dyna_keyword_map,
        "list_manual_notes",
        lambda limit=20: [{"type": "workflow", "execution_allowed": True}],
    )

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("manual_notes[0]: execution_allowed must be false." in item for item in validation["errors"])


def test_dyna_keyword_map_validation_rejects_unverified_execution_ready(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_UNSAFE": {
                "status": "cardimage_verified",
                "keyword": "*MAT_UNSAFE",
                "entity_type": "mats",
                "cardimage": "MATL999",
                "fields": [
                    {"field": "E", "dataname": "E", "status": "requires_hm_recording"},
                ],
                "execution_ready": True,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("execution_ready=true requires datanames_verified" in item for item in validation["errors"])
    assert any("every field" in item for item in validation["errors"])


def test_dyna_keyword_map_validation_rejects_verified_field_without_dataname(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_BAD_FIELD": {
                "status": "cardimage_verified",
                "keyword": "*MAT_BAD_FIELD",
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": None, "status": "dataname_verified"},
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("*MAT_BAD_FIELD.E: verified field status requires dataname." in item for item in validation["errors"])


def test_dyna_keyword_map_validation_warns_for_unverified_dataname(monkeypatch):
    advisory_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_WARN_FIELD": {
                "status": "cardimage_verified",
                "keyword": "*MAT_WARN_FIELD",
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": "LSD_E", "status": "requires_hm_recording"},
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: advisory_map)

    validation = validate_dyna_keyword_map()

    assert validation["success"] is True
    assert any(
        "*MAT_WARN_FIELD.E: dataname is present but field status is not verified." in item
        for item in validation["warnings"]
    )


def test_dyna_keyword_map_validation_rejects_executable_examples_and_manual_refs(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_DOC_UNSAFE": {
                "status": "cardimage_verified",
                "keyword": "*MAT_DOC_UNSAFE",
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": None, "status": "requires_hm_recording"},
                ],
                "examples": [
                    {
                        "purpose": "execution",
                        "keyword_block": ["*MAT_DOC_UNSAFE"],
                        "execution_allowed": True,
                    }
                ],
                "manual_refs": [
                    {
                        "ref_id": "manual_note:mat_3_plastic_kinematic",
                        "source": "templates/dyna_manual_notes.jsonl",
                        "role": "execution_source",
                        "execution_allowed": True,
                    }
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("examples[0]: execution_allowed must be false" in item for item in validation["errors"])
    assert any("examples[0]: purpose must be planning_only" in item for item in validation["errors"])
    assert any("manual_refs[0]: role must be explanation_only" in item for item in validation["errors"])
    assert any("manual_refs[0]: execution_allowed must be false" in item for item in validation["errors"])


def test_dyna_keyword_map_validation_rejects_executable_examples(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_BAD_EXAMPLE": {
                "status": "cardimage_verified",
                "keyword": "*MAT_BAD_EXAMPLE",
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": None, "status": "requires_hm_recording"},
                ],
                "examples": [{"execution_allowed": True}],
                "manual_refs": [
                    {
                        "ref_id": "manual_note:bad",
                        "source": "templates/dyna_manual_notes.jsonl",
                        "role": "explanation_only",
                    }
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("execution_allowed must be false" in item for item in validation["errors"])


def test_dyna_keyword_map_validation_rejects_executable_manual_refs(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_BAD_REF": {
                "status": "cardimage_verified",
                "keyword": "*MAT_BAD_REF",
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": None, "status": "requires_hm_recording"},
                ],
                "examples": [{"execution_allowed": False}],
                "manual_refs": [
                    {
                        "ref_id": "manual_note:bad",
                        "source": "templates/dyna_manual_notes.jsonl",
                        "role": "execution_hint",
                    }
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("role must be explanation_only" in item for item in validation["errors"])


def test_dyna_keyword_map_validation_rejects_missing_manual_ref(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_MISSING_REF": {
                "status": "cardimage_verified",
                "keyword": "*MAT_MISSING_REF",
                "aliases": ["*MAT_ALIAS"],
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": None, "status": "requires_hm_recording"},
                ],
                "examples": [{"execution_allowed": False}],
                "manual_refs": [
                    {
                        "ref_id": "manual_note:not_present",
                        "source": "templates/dyna_manual_notes.jsonl",
                        "role": "explanation_only",
                    }
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)
    monkeypatch.setattr(dyna_keyword_map, "list_manual_notes", lambda limit=20: [])

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("ref_id not found" in item for item in validation["errors"])


def test_dyna_keyword_map_validation_rejects_alias_without_star(monkeypatch):
    unsafe_map = {
        "version": 1,
        "execution_guardrails": {"allow_embedding_to_fill_execution_fields": False},
        "keyword_routes": {
            "*MAT_BAD_ALIAS": {
                "status": "cardimage_verified",
                "keyword": "*MAT_BAD_ALIAS",
                "aliases": ["MAT_BAD_ALIAS_2"],
                "entity_type": "mats",
                "cardimage": "MATL1",
                "fields": [
                    {"field": "E", "dataname": None, "status": "requires_hm_recording"},
                ],
                "examples": [{"execution_allowed": False}],
                "manual_refs": [
                    {
                        "ref_id": "manual_note:bad_alias",
                        "source": "templates/dyna_manual_notes.jsonl",
                        "role": "explanation_only",
                    }
                ],
                "execution_ready": False,
            }
        },
    }
    monkeypatch.setattr(dyna_keyword_map, "load_dyna_keyword_map", lambda: unsafe_map)
    monkeypatch.setattr(
        dyna_keyword_map,
        "list_manual_notes",
        lambda limit=20: [{"id": "manual_note:bad_alias", "execution_allowed": False}],
    )

    validation = validate_dyna_keyword_map()

    assert validation["success"] is False
    assert any("alias must be a string starting with '*'" in item for item in validation["errors"])
