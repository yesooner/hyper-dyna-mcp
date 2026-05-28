"""Tests for HyperMesh Tcl policy enforcement."""

from program.tools.hm_policy import (
    check_meshing_rules,
    wrap_generated_tcl,
    unwrap_generated_tcl,
    MCP_SCRIPT_BEGIN,
    MCP_SCRIPT_END,
    TRUSTED_GENERATORS,
    FORBIDDEN_MESHING_COMMANDS,
)


def test_wrap_unwrap_roundtrip():
    body = '*createmark surfaces 1 "all"\n*automesh 0 2 2'
    wrapped = wrap_generated_tcl("test_gen", body)
    assert MCP_SCRIPT_BEGIN in wrapped
    assert MCP_SCRIPT_END in wrapped
    assert "MCP_GENERATED_BY=test_gen" in wrapped
    unwrapped = unwrap_generated_tcl(wrapped)
    assert "*createmark" in unwrapped
    assert "*automesh" in unwrapped


def test_unwrap_no_markers():
    script = '*createmark surfaces 1 "all"'
    assert unwrap_generated_tcl(script) == script


def test_trusted_generators_not_empty():
    assert len(TRUSTED_GENERATORS) > 0
    assert "generate_surface_automesh_tcl" in TRUSTED_GENERATORS
    assert "generate_plain_tetra_tcl" in TRUSTED_GENERATORS


def test_forbidden_commands_list():
    assert "*meshdragelements" in FORBIDDEN_MESHING_COMMANDS
    assert "*tetmesh" in FORBIDDEN_MESHING_COMMANDS


def test_allowed_script_passes():
    script = '*createmark nodes 1 "all"\nputs "hello"'
    assert check_meshing_rules(script) is None


def test_raw_meshing_blocked():
    script = '*createmark solids 1 "all"\n*tetmesh 1 1 1'
    result = check_meshing_rules(script)
    assert result is not None
    assert result["policy_violation"] is True


def test_generated_script_passes():
    body = '*createmark solids 1 "all"\n*tetmesh 1 1 1'
    script = wrap_generated_tcl("generate_plain_tetra_tcl", body)
    assert check_meshing_rules(script) is None


def test_unknown_generator_blocked():
    body = '*createmark solids 1 "all"\n*tetmesh 1 1 1'
    script = wrap_generated_tcl("evil_generator", body)
    result = check_meshing_rules(script)
    assert result is not None
    assert "unknown" in result["message"].lower()


def test_missing_markers_blocked():
    script = "# MCP_GENERATED_BY=generate_plain_tetra_tcl\n*tetmesh 1 1 1"
    result = check_meshing_rules(script)
    assert result is not None
    assert "marker" in result["message"].lower()


def test_forbidden_after_end_blocked():
    body = '*createmark solids 1 "all"'
    script = wrap_generated_tcl("generate_plain_tetra_tcl", body)
    script += "\n*tetmesh 1 1 1"
    result = check_meshing_rules(script)
    assert result is not None
    assert "after" in result["message"].lower()


def test_non_generated_script_with_meshing_blocked():
    script = '*createmark solids 1 "all"\n*meshdragelements 1 1 2 0 0 1 0 0 1 2 1 2'
    result = check_meshing_rules(script)
    assert result is not None
    assert "blocked" in result["message"].lower()
