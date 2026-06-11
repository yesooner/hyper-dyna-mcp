"""Tests for HyperMesh Tcl generation."""

from program.tools.hm_tcl_generator import (
    generate_surface_automesh_tcl,
    generate_solid_mesh_tcl,
    generate_info_tcl,
    generate_save_tcl,
    validate_tcl_script,
    tcl_escape_name,
    quote_tcl_path,
)
from program.tools.hm_policy import MCP_SCRIPT_BEGIN, MCP_SCRIPT_END


def test_surface_automesh_has_markers():
    script = generate_surface_automesh_tcl(element_size=2.0)
    assert MCP_SCRIPT_BEGIN in script
    assert MCP_SCRIPT_END in script
    assert "MCP_GENERATED_BY=generate_surface_automesh_tcl" in script


def test_surface_automesh_has_commands():
    script = generate_surface_automesh_tcl(element_size=3.0)
    assert "*createmark surfaces" in script
    assert "*interactiveremeshsurf" in script
    assert "*automesh" in script
    assert "3.0" in script


def test_surface_automesh_with_output():
    script = generate_surface_automesh_tcl(element_size=2.0, output_hm_path="C:/test/output.hm")
    assert "*writefile" in script
    assert "output.hm" in script


def test_solid_mesh_has_markers():
    script = generate_solid_mesh_tcl(element_size=5.0)
    assert MCP_SCRIPT_BEGIN in script
    assert MCP_SCRIPT_END in script
    assert "MCP_GENERATED_BY=generate_plain_tetra_tcl" in script


def test_solid_mesh_has_commands():
    script = generate_solid_mesh_tcl(element_size=3.0)
    assert "*createmark solids" in script
    assert "*meshsolidsonly" in script
    assert "3.0" in script


def test_info_tcl():
    script = generate_info_tcl()
    assert "hm_getmark" in script
    assert "hm_gettotalcomponents" in script
    assert "MCP_INFO" in script


def test_save_tcl():
    script = generate_save_tcl("C:/models/test.hm")
    assert "*writefile" in script
    assert "test.hm" in script


def test_validate_save_tcl_is_file_io_blocked():
    script = generate_save_tcl("C:/models/test.hm")
    result = validate_tcl_script(script)
    assert result["valid"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["blocked_command"] == "*writefile"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["required_tool"] == "hm_auto_save"


def test_validate_unverified_surface_automesh_script_is_blocked():
    script = generate_surface_automesh_tcl(element_size=2.0)
    result = validate_tcl_script(script)
    assert result["valid"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "surface_automesh"


def test_validate_unverified_solid_mesh_script_is_blocked():
    script = generate_solid_mesh_tcl(element_size=2.0)
    result = validate_tcl_script(script)
    assert result["valid"] is False
    assert result["error_type"] == "mesh_route_not_verified"
    assert result["blocked_route_name"] == "tetmesh_geometry_solid"


def test_validate_bad_script():
    script = '*createmark solids 1 "all"\n*tetmesh 1 1 1'
    result = validate_tcl_script(script)
    assert result["valid"] is False
    assert result["policy_violation"] is True


def test_validate_plain_file_io_script_is_blocked():
    result = validate_tcl_script('*feoutputwithdata "bad.k" 0 0 0 0 0')
    assert result["valid"] is False
    assert result["error_type"] == "file_io_route_not_allowed"
    assert result["blocked_command"] == "*feoutputwithdata"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False


def test_tcl_escape_name():
    assert tcl_escape_name('hello "world"') == 'hello \\"world\\"'
    assert tcl_escape_name("test$var") == "test\\$var"
    assert tcl_escape_name("a{b}") == "a\\{b\\}"


def test_quote_tcl_path():
    assert quote_tcl_path("C:\\Users\\test\\file.hm") == "C:/Users/test/file.hm"
    assert quote_tcl_path('path with "quotes"') == 'path with \\"quotes\\"'
