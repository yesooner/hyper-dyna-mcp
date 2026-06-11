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
    ShellThickness,
    BeamElement,
    BoundaryCondition,
    build_shell_plate_model,
    generate_k_content,
    write_k_file,
)
from program.tools.k_parser import parse_k_content


def test_k_writer_documents_offline_fixture_scope():
    import program.tools.k_writer as k_writer

    module_doc = k_writer.__doc__ or ""
    generate_doc = generate_k_content.__doc__ or ""
    write_doc = write_k_file.__doc__ or ""
    shell_doc = build_shell_plate_model.__doc__ or ""

    assert "offline" in module_doc
    assert "not a HyperMesh GUI route" in module_doc
    assert "final K export" in module_doc
    assert "offline fixture/review" in generate_doc
    assert "not evidence" in generate_doc
    assert "not a HyperMesh GUI export path" in write_doc
    assert "final K export" in write_doc
    assert "not a HyperMesh GUI creation" in shell_doc
    assert "final K export" in shell_doc


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


def test_shell_element_thickness_card():
    model = KModel(
        title="Shell Thickness Test",
        materials=[Material(mid=1, rho=7.85e-6, e=210000.0, pr=0.3)],
        sections=[Section(secid=1, sec_type="SHELL", elform=2, shrf=0.833, nip=5)],
        parts=[Part(pid=1, secid=1, mid=1)],
        nodes=[
            Node(nid=1, x=0, y=0, z=0),
            Node(nid=2, x=1, y=0, z=0),
            Node(nid=3, x=1, y=1, z=0),
            Node(nid=4, x=0, y=1, z=0),
        ],
        shell_elements=[ShellElement(eid=1, pid=1, nodes=[1, 2, 3, 4])],
        shell_thicknesses=[ShellThickness(eid=1, t1=5.0, t2=5.0, t3=5.0, t4=5.0)],
    )

    content = generate_k_content(model)
    assert "*ELEMENT_SHELL_THICKNESS" in content
    assert "    5.0000" in content

    kfile = parse_k_content(content)
    assert len(kfile.get_keywords("ELEMENT_SHELL_THICKNESS")) == 1
    assert kfile.get_part_material_refs()[1] == 1
    assert kfile.get_part_section_refs()[1] == 1


def test_build_shell_plate_model_matches_codex_smoke_dimensions(tmp_path):
    model = build_shell_plate_model(
        title="TEST_SHELL_PLATE - offline fixture only",
        part_name="TEST_SHELL_PLATE",
        width=200.0,
        height=100.0,
        mesh_size=20.0,
        thickness=5.0,
    )

    assert len(model.nodes) == 66
    assert len(model.shell_elements) == 50
    assert len(model.shell_thicknesses) == 50
    assert model.parts[0].title == "TEST_SHELL_PLATE"
    assert model.parts[0].pid == 1
    assert model.parts[0].secid == 1
    assert model.parts[0].mid == 1
    assert model.materials[0].rho == 7.85e-6

    outpath = tmp_path / "test_shell_plate.k"
    content = write_k_file(model, outpath)
    assert outpath.exists()
    assert "*NODE" in content
    assert "*ELEMENT_SHELL" in content
    assert "*ELEMENT_SHELL_THICKNESS" in content
    assert "*SECTION_SHELL" in content
    assert "*MAT_ELASTIC" in content
    assert "*PART" in content

    kfile = parse_k_content(content)
    assert kfile.validate() == []
    assert len(kfile.get_keywords("ELEMENT_SHELL")) == 1
    assert len(kfile.get_keywords("ELEMENT_SHELL_THICKNESS")) == 1


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
