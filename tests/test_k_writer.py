"""Tests for K file writer."""

import pytest
from pathlib import Path
from program.tools.k_writer import (
    KModel,
    Material,
    Part,
    Section,
    Node,
    SolidElement,
    ShellElement,
    BeamElement,
    BoundaryCondition,
    generate_k_content,
    write_k_file,
)
from program.tools.k_parser import parse_k_content


def test_generate_basic():
    model = KModel(title="Test Model")
    content = generate_k_content(model)
    assert "*KEYWORD" in content
    assert "*TITLE" in content
    assert "Test Model" in content
    assert "*END" in content


def test_roundtrip_parse():
    """Generate a K file, then parse it and verify."""
    model = KModel(
        title="Roundtrip Test",
        materials=[Material(mid=1, rho=7.85e-9, e=210000.0, pr=0.3)],
        sections=[Section(secid=1, elform=1)],
        parts=[Part(pid=1, secid=1, mid=1, title="Test Part")],
    )
    content = generate_k_content(model)
    kfile = parse_k_content(content)

    assert kfile.title == "Roundtrip Test"
    mat_ids = kfile.get_material_ids()
    assert 1 in mat_ids
    part_refs = kfile.get_part_material_refs()
    assert part_refs.get(1) == 1


def test_write_to_file(tmp_path):
    model = KModel(title="File Write Test")
    outpath = tmp_path / "test_output.k"
    content = write_k_file(model, outpath)
    assert outpath.exists()
    assert "*KEYWORD" in outpath.read_text()


# --- New tests for enhanced features ---


def test_keyword_output_order():
    """Verify keywords appear in the correct LS-DYNA convention order."""
    model = KModel(
        title="Order Test",
        materials=[Material(mid=1, rho=7.85e-9, e=210000.0, pr=0.3)],
        sections=[Section(secid=1)],
        parts=[Part(pid=1, secid=1, mid=1)],
        nodes=[Node(nid=1, x=0, y=0, z=0)],
        solid_elements=[SolidElement(eid=1, pid=1, nodes=[1, 1, 1, 1, 1, 1, 1, 1])],
    )
    content = generate_k_content(model)
    lines = content.split("\n")

    # Find line indices of each keyword
    idx = {line: i for i, line in enumerate(lines) if line.startswith("*")}
    assert idx["*KEYWORD"] < idx["*TITLE"]
    assert idx["*TITLE"] < idx["*CONTROL_TERMINATION"]
    assert idx["*CONTROL_TERMINATION"] < idx["*DATABASE_BINARY_D3PLOT"]
    assert idx["*DATABASE_BINARY_D3PLOT"] < idx["*MAT_ELASTIC"]
    assert idx["*MAT_ELASTIC"] < idx["*SECTION_SOLID"]
    assert idx["*SECTION_SOLID"] < idx["*PART"]
    assert idx["*PART"] < idx["*NODE"]
    assert idx["*NODE"] < idx["*ELEMENT_SOLID"]
    assert idx["*ELEMENT_SOLID"] < idx["*END"]


def test_shell_elements():
    model = KModel(
        title="Shell Test",
        materials=[Material(mid=1, rho=7.85e-9, e=210000.0, pr=0.3)],
        sections=[Section(secid=1, sec_type="SHELL", elform=16, shrf=0.1, nip=5)],
        parts=[Part(pid=1, secid=1, mid=1)],
        nodes=[
            Node(nid=1, x=0, y=0, z=0),
            Node(nid=2, x=1, y=0, z=0),
            Node(nid=3, x=1, y=1, z=0),
            Node(nid=4, x=0, y=1, z=0),
        ],
        shell_elements=[ShellElement(eid=1, pid=1, nodes=[1, 2, 3, 4])],
    )
    content = generate_k_content(model)
    assert "*SECTION_SHELL" in content
    assert "*ELEMENT_SHELL" in content
    assert "ELFORM" in content

    kfile = parse_k_content(content)
    elems = kfile.get_elements()
    assert len(elems) == 1
    assert elems[0].name == "ELEMENT_SHELL"


def test_beam_elements():
    model = KModel(
        title="Beam Test",
        materials=[Material(mid=1, rho=7.85e-9, e=210000.0, pr=0.3)],
        sections=[Section(secid=1, sec_type="BEAM", elform=1)],
        parts=[Part(pid=1, secid=1, mid=1)],
        nodes=[Node(nid=1, x=0, y=0, z=0), Node(nid=2, x=1, y=0, z=0)],
        beam_elements=[BeamElement(eid=1, pid=1, nodes=[1, 2])],
    )
    content = generate_k_content(model)
    assert "*SECTION_BEAM" in content
    assert "*ELEMENT_BEAM" in content


def test_boundary_conditions():
    model = KModel(
        title="BC Test",
        boundaries=[BoundaryCondition(nsid=1, dofx=1, dofy=1, dofz=1)],
    )
    content = generate_k_content(model)
    assert "*BOUNDARY_SPC_SET" in content

    kfile = parse_k_content(content)
    bc_kws = kfile.get_keywords_by_prefix("BOUNDARY_")
    assert len(bc_kws) == 1


def test_part_with_eos_hgid():
    model = KModel(
        title="Part Options Test",
        parts=[Part(pid=1, secid=1, mid=1, eosid=0, hgid=1)],
    )
    content = generate_k_content(model)
    assert "HGID" in content


def test_nodes_with_bc():
    model = KModel(
        title="Node BC Test",
        nodes=[Node(nid=1, x=0, y=0, z=0, tc=7, rc=7)],
    )
    content = generate_k_content(model)
    lines = [l for l in content.split("\n") if l.strip().startswith("1")]
    assert len(lines) >= 1
    assert "7" in lines[0]
