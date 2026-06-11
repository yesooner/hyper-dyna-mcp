"""Minimum verification model — comprehensive validation tests.

Tests the model_original.k against all requirements from the goal specification.
No GUI dependency — pure code validation.
"""

import pytest
from pathlib import Path
from program.tools.k_parser import parse_k_file, _classify_keyword
from program.tools.k_writer import (
    KModel, Material, Section, Part, Node, ShellElement,
    SolidElement, BoundaryCondition, generate_k_content, write_k_file,
)

_MODEL = Path(__file__).resolve().parents[1] / "output" / "model_original.k"


# --- Model structure tests ---


def test_model_file_exists():
    assert _MODEL.exists(), f"Model file not found: {_MODEL}"


def test_parse_model():
    kfile = parse_k_file(_MODEL)
    assert kfile.title
    assert len(kfile.keywords) > 0


def test_two_parts():
    kfile = parse_k_file(_MODEL)
    assert len(kfile.get_parts()) == 2


def test_materials_exist():
    kfile = parse_k_file(_MODEL)
    assert len(kfile.get_materials()) >= 2


def test_sections_exist():
    kfile = parse_k_file(_MODEL)
    assert len(kfile.get_sections()) >= 2


def test_elements_exist():
    kfile = parse_k_file(_MODEL)
    assert len(kfile.get_elements()) >= 2


def test_nodes_exist():
    kfile = parse_k_file(_MODEL)
    assert len(kfile.get_nodes()) >= 1


# --- Cross-reference validation ---


def test_part_material_refs():
    kfile = parse_k_file(_MODEL)
    refs = kfile.get_part_material_refs()
    mat_ids = kfile.get_material_ids()
    assert len(refs) == 2
    for pid, mid in refs.items():
        assert mid in mat_ids, f"Part {pid} references undefined material MID={mid}"


def test_part_section_refs():
    kfile = parse_k_file(_MODEL)
    refs = kfile.get_part_section_refs()
    sec_ids = kfile.get_section_ids()
    assert len(refs) == 2
    for pid, secid in refs.items():
        assert secid in sec_ids, f"Part {pid} references undefined section SECID={secid}"


# --- Keyword-specific tests ---


def test_contact_exists():
    kfile = parse_k_file(_MODEL)
    contacts = kfile.get_keywords_by_prefix("CONTACT_")
    assert len(contacts) >= 1
    assert contacts[0].name == "CONTACT_AUTOMATIC_SURFACE_TO_SURFACE"


def test_contact_has_data():
    kfile = parse_k_file(_MODEL)
    contacts = kfile.get_keywords_by_prefix("CONTACT_")
    assert len(contacts[0].data_lines) >= 1


def test_boundary_exists():
    kfile = parse_k_file(_MODEL)
    bcs = kfile.get_keywords_by_prefix("BOUNDARY_")
    assert len(bcs) >= 1


def test_load_exists():
    kfile = parse_k_file(_MODEL)
    loads = kfile.get_keywords_by_prefix("LOAD_")
    assert len(loads) >= 1


def test_define_curve_exists():
    kfile = parse_k_file(_MODEL)
    curves = kfile.get_keywords_by_prefix("DEFINE_")
    assert len(curves) >= 1


def test_sets_exist():
    kfile = parse_k_file(_MODEL)
    part_sets = kfile.get_keywords("SET_PART_LIST")
    node_sets = kfile.get_keywords("SET_NODE_LIST")
    seg_sets = kfile.get_keywords("SET_SEGMENT")
    assert len(part_sets) >= 2
    assert len(node_sets) >= 1
    assert len(seg_sets) >= 2


# --- Full validation ---


def test_validation_passes():
    kfile = parse_k_file(_MODEL)
    errors = kfile.validate()
    assert len(errors) == 0, f"Validation errors: {errors}"


# --- K file format compliance ---


def test_keyword_header():
    content = _MODEL.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    assert lines[0].strip() == "*KEYWORD"


def test_end_keyword():
    content = _MODEL.read_text(encoding="utf-8")
    assert "*END" in content


def test_title_keyword():
    content = _MODEL.read_text(encoding="utf-8")
    assert "*TITLE" in content


# --- Roundtrip test ---


def test_roundtrip_parse_write(tmp_path):
    """Parse model, write as new K, parse again, verify consistency."""
    kfile = parse_k_file(_MODEL)

    # Count original
    orig_parts = len(kfile.get_parts())
    orig_mats = len(kfile.get_materials())
    orig_secs = len(kfile.get_sections())

    # Build KModel from parsed data
    model = KModel(
        title=kfile.title,
        termination_time=0.005,
        d3plot_dt=0.0001,
    )

    # Extract materials
    for mk in kfile.get_materials():
        if mk.data_lines:
            fields = mk.data_lines[0].split()
            if len(fields) >= 4:
                model.materials.append(Material(
                    mid=int(fields[0]),
                    rho=float(fields[1]),
                    e=float(fields[2]),
                    pr=float(fields[3]),
                    mat_type=mk.name.replace("MAT_", ""),
                ))

    # Write
    outpath = tmp_path / "model_roundtrip.k"
    write_k_file(model, outpath)

    # Parse roundtrip
    kfile2 = parse_k_file(outpath)
    assert len(kfile2.get_materials()) == orig_mats


# --- Category classification ---


def test_keyword_categories():
    kfile = parse_k_file(_MODEL)
    categories = {k.name: _classify_keyword(k.name) for k in kfile.keywords}

    # Check specific keywords have correct categories
    assert categories.get("PART") == "part"
    assert categories.get("NODE") == "node"
    assert categories.get("KEYWORD") == "file"
    assert categories.get("END") == "file"
    assert categories.get("TITLE") == "file"


# --- ID uniqueness ---


def test_material_ids_unique():
    kfile = parse_k_file(_MODEL)
    ids = kfile.get_material_ids()
    assert len(ids) == len(set(ids))


def test_section_ids_unique():
    kfile = parse_k_file(_MODEL)
    ids = kfile.get_section_ids()
    assert len(ids) == len(set(ids))
