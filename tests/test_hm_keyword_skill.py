"""Tests for LS-DYNA keyword execution guardrails."""

from program.tools import hm_keyword_skill


def test_hm_set_keyword_executes_curated_section_template(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_keyword_skill.hm_set_keyword("SECTION_SOLID", {"SECID": 1, "ELFORM": 1})

    assert result["success"] is True
    assert result["keyword"] == "SECTION_SOLID"
    assert called is True


def test_hm_set_keyword_still_blocks_unverified_dyna_route(monkeypatch):
    called = False

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_keyword_skill.hm_set_keyword("MAT_3", {"MID": 1, "RHO": 7.85e-6, "E": 210000.0, "PR": 0.3})

    assert result["success"] is False
    assert result["error_type"] == "dyna_keyword_execution_not_verified"
    assert result["execution_ready"] is False
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["execution_decision"]["state"] == "blocked"
    assert called is False


def test_hm_set_keyword_allows_execution_ready_route(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        hm_keyword_skill,
        "query_dyna_keyword",
        lambda keyword: {
            "execution_ready": True,
            "execution_decision": {
                "state": "executable",
                "blocked_reasons": [],
                "required_verification": [],
            },
            "execution_blockers": [],
            "advisory_only": {"execution_allowed": False},
        },
    )
    monkeypatch.setattr(hm_keyword_skill._engine, "has_template", lambda keyword: True)
    monkeypatch.setattr(
        hm_keyword_skill._engine,
        "render",
        lambda keyword, params: "puts READY\nputs DONE",
    )

    def fake_execute_tcl_gui(script, timeout=30, **kwargs):
        captured.setdefault("scripts", []).append(script)
        captured["timeout"] = timeout
        captured["kwargs"] = kwargs
        return {"success": True, "response": f"OK {script}"}

    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", fake_execute_tcl_gui)
    monkeypatch.setattr(hm_keyword_skill.time, "sleep", lambda seconds: None)

    result = hm_keyword_skill.hm_set_keyword("MAT_SAFE", {"MID": 1}, timeout=17)

    assert result["success"] is True
    assert result["keyword"] == "MAT_SAFE"
    assert captured["scripts"] == ["puts READY", "puts DONE"]
    assert captured["timeout"] == 17
    assert captured["kwargs"]["enforce_rules"] is False


def test_hm_set_keyword_blocks_execution_ready_template_with_meshing_command(monkeypatch):
    called = False

    monkeypatch.setattr(
        hm_keyword_skill,
        "query_dyna_keyword",
        lambda keyword: {
            "execution_ready": True,
            "execution_decision": {"state": "executable", "blocked_reasons": []},
            "execution_blockers": [],
            "advisory_only": {"execution_allowed": False},
        },
    )
    monkeypatch.setattr(hm_keyword_skill._engine, "has_template", lambda keyword: True)
    monkeypatch.setattr(
        hm_keyword_skill._engine,
        "render",
        lambda keyword, params: '*createmark solids 1 "all"\n*tetmesh 1 1 1',
    )

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_keyword_skill.hm_set_keyword("MAT_SAFE", {"MID": 1})

    assert result["success"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "tetmesh_geometry_solid"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_modeling_action"
    assert called is False


def test_hm_set_keyword_blocks_execution_ready_template_with_file_io(monkeypatch):
    called = False

    monkeypatch.setattr(
        hm_keyword_skill,
        "query_dyna_keyword",
        lambda keyword: {
            "execution_ready": True,
            "execution_decision": {"state": "executable", "blocked_reasons": []},
            "execution_blockers": [],
            "advisory_only": {"execution_allowed": False},
        },
    )
    monkeypatch.setattr(hm_keyword_skill._engine, "has_template", lambda keyword: True)
    monkeypatch.setattr(
        hm_keyword_skill._engine,
        "render",
        lambda keyword, params: '*writefile "bad.k" 1',
    )

    def fake_execute_tcl_gui(*args, **kwargs):
        nonlocal called
        called = True
        return {"success": True, "response": "OK"}

    monkeypatch.setattr(hm_keyword_skill, "execute_tcl_gui", fake_execute_tcl_gui)

    result = hm_keyword_skill.hm_set_keyword("MAT_SAFE", {"MID": 1})

    assert result["success"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_auto_save"
    assert called is False
