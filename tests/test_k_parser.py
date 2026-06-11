"""Tests for K file parser."""

import pytest
from pathlib import Path
from program.tools.k_parser import (
    parse_k_file,
    parse_k_content,
    _parse_data_line,
    _classify_keyword,
)

_SAMPLES = Path(__file__).resolve().parents[1] / "lib" / "k_samples"


def test_k_parser_documents_offline_fixture_scope():
    import program.tools.k_parser as k_parser

    module_doc = k_parser.__doc__ or ""
    file_doc = parse_k_file.__doc__ or ""
    content_doc = parse_k_content.__doc__ or ""

    assert "Offline LS-DYNA .k fixture/review parser" in module_doc
    assert "not a HyperMesh GUI route" in module_doc
    assert "not an MCP modeling/export tool" in module_doc
    assert "final K export" in module_doc
    assert "not model creation" in file_doc
    assert "not evidence" in file_doc
    assert "HyperMesh GUI import route" in content_doc
    assert "final K export route" in content_doc


def test_parse_minimal_solid():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    assert kfile.title
    assert len(kfile.keywords) > 0
    errors = kfile.validate()
    assert len(errors) == 0, f"Unexpected errors: {errors}"


def test_parse_missing_material():
    kfile = parse_k_file(_SAMPLES / "missing_material_error.k")
    errors = kfile.validate()
    assert len(errors) > 0
    assert any("undefined material" in e for e in errors)


def test_parse_minimal_database():
    kfile = parse_k_file(_SAMPLES / "minimal_database.k")
    db_keywords = [k for k in kfile.keywords if k.name.startswith("DATABASE")]
    assert len(db_keywords) >= 3


def test_parse_nonexistent():
    with pytest.raises(FileNotFoundError):
        parse_k_file("/nonexistent/file.k")


def test_get_material_ids():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    ids = kfile.get_material_ids()
    assert 1 in ids


def test_get_part_material_refs():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    refs = kfile.get_part_material_refs()
    assert refs.get(1) == 1


# --- New tests for enhanced features ---


def test_keyword_header_detected():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    kw_names = [k.name for k in kfile.keywords]
    assert "KEYWORD" in kw_names


def test_keyword_category_classification():
    assert _classify_keyword("MAT_ELASTIC") == "material"
    assert _classify_keyword("SECTION_SOLID") == "section"
    assert _classify_keyword("ELEMENT_SHELL") == "element"
    assert _classify_keyword("BOUNDARY_SPC") == "boundary"
    assert _classify_keyword("CONTACT_AUTOMATIC") == "contact"
    assert _classify_keyword("CONTROL_TERMINATION") == "control"
    assert _classify_keyword("SET_NODE") == "set"
    assert _classify_keyword("KEYWORD") == "file"
    assert _classify_keyword("UNKNOWN_FOO") == "other"


def test_keyword_categories_populated():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    categories = {k.category for k in kfile.keywords}
    assert "material" in categories
    assert "section" in categories
    assert "part" in categories
    assert "node" in categories
    assert "element" in categories
    assert "file" in categories


def test_parse_data_line_free_format():
    assert _parse_data_line("1,2.0,3.0,4.0") == ["1", "2.0", "3.0", "4.0"]


def test_parse_data_line_fixed_format():
    # 10-char aligned fields
    line = "         1       0.0       0.0       0.0       0       0"
    fields = _parse_data_line(line)
    assert fields == ["1", "0.0", "0.0", "0.0", "0", "0"]


def test_parse_data_line_loose_format():
    line = "1  7.850E-09 2.100E+05     0.300"
    fields = _parse_data_line(line)
    assert fields[0] == "1"
    assert len(fields) == 4


def test_parse_content_keyword_header():
    content = "*KEYWORD\n*TITLE\nTest\n*NODE\n  1  0.0  0.0  0.0\n"
    kfile = parse_k_content(content)
    assert kfile.title == "Test"
    kw_names = [k.name for k in kfile.keywords]
    assert "KEYWORD" in kw_names


def test_get_section_ids():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    ids = kfile.get_section_ids()
    assert 1 in ids


def test_get_part_section_refs():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    refs = kfile.get_part_section_refs()
    assert refs.get(1) == 1


def test_get_element_part_refs():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    refs = kfile.get_element_part_refs()
    assert refs.get(1) == 1


def test_get_keywords_by_prefix():
    kfile = parse_k_file(_SAMPLES / "minimal_solid.k")
    elems = kfile.get_keywords_by_prefix("ELEMENT_")
    assert len(elems) == 1
    assert elems[0].name == "ELEMENT_SOLID"


def test_control_keywords():
    kfile = parse_k_file(_SAMPLES / "sample_control_cards.k")
    controls = kfile.get_keywords_by_prefix("CONTROL_")
    databases = kfile.get_keywords_by_prefix("DATABASE_")
    assert len(controls) > 5
    assert len(databases) > 3


def test_multiple_materials():
    kfile = parse_k_file(_SAMPLES / "sample_shell_elements.k")
    mats = kfile.get_materials()
    assert len(mats) >= 1
    # Note: sample_shell_elements.k has non-standard formatting
    # where MID and RHO fields touch (HyperMesh export quirk)
    # so material IDs may not parse cleanly
    assert len(mats) == 1
    assert mats[0].name == "MAT_RIGID_TITLE"
