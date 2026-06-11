"""Tests for HyperMesh LS-DYNA template rendering."""

import pytest

from program.tools.hm_template_engine import HmTemplateEngine


def test_render_mat_elastic_uses_verified_hypermesh_mapping():
    engine = HmTemplateEngine()

    script = engine.render(
        "MAT_ELASTIC",
        {
            "MID": 900001,
            "RHO": 7.85e-9,
            "E": 210000,
            "PR": 0.3,
            "DA": 0,
            "DB": 0,
        },
    )

    assert "MAT_ELASTIC -> MATL1" in script
    assert "cardimage=MATL1" in script
    assert "Rho=7.85e-09" in script
    assert "E=210000" in script
    assert "Nu=0.3" in script
    assert "dataname=RHO" not in script
    assert "cardimage=MAT_ELASTIC" not in script


def test_mat_elastic_template_info_marks_verified_source():
    info = HmTemplateEngine().get_template_info("MAT_ELASTIC")

    assert info["source"] == "verified_hypermesh_mapping"
    assert info["cardimage"] == "MATL1"
    assert info["fields"] == {"RHO": "Rho", "E": "E", "PR": "Nu"}
    assert info["unsupported_fields"] == ["DA", "DB"]


def test_render_requires_verified_mapping_required_fields():
    engine = HmTemplateEngine()

    with pytest.raises(ValueError, match="Missing required parameters"):
        engine.render("MAT_ELASTIC", {"MID": 1, "RHO": 7.85e-9, "E": 210000})


def test_section_solid_uses_verified_cardimage_and_marks_unverified_fields():
    script = HmTemplateEngine().render(
        "SECTION_SOLID",
        {"SECID": 1, "ELFORM": 1, "AET": 0},
    )

    assert "SECTION_SOLID -> SectSld" in script
    assert "cardimage=SectSld" in script
    assert "Ignored unsupported fields" in script
    assert "cardimage=SECTION_SOLID" not in script


def test_part_uses_component_binding_without_cardimage():
    script = HmTemplateEngine().render(
        "PART",
        {
            "HEADING": "Part 1",
            "PID": 10,
            "SECID": 20,
            "MID": 30,
            "EOSID": 0,
            "HGID": 0,
            "GRAV": 0,
            "ADPOPT": 0,
            "TMID": 0,
        },
    )

    assert 'name="Part 1"' in script
    assert "cardimage=" not in script
    assert "propertyid=20" in script
    assert "materialid=30" in script
    assert "Ignored unsupported fields" in script


def test_part_template_info_marks_verified_source():
    info = HmTemplateEngine().get_template_info("PART")

    assert info["source"] == "verified_hypermesh_mapping"
    assert info["entity_type"] == "comps"
    assert info["cardimage"] is None
    assert info["fields"] == {"SECID": "propertyid", "MID": "materialid"}


def test_control_termination_uses_verified_card_mapping():
    script = HmTemplateEngine().render(
        "CONTROL_TERMINATION",
        {"ENDTIM": 1.0, "ENDCYC": 0, "DTMIN": 0, "ENDENG": 0, "ENDMAS": 0, "NOSOL": 0},
    )

    assert "CONTROL_TERMINATION -> Termin" in script
    assert "cardimage=Termin" in script
    assert "LSD_ENDTIM=1.0" in script
    assert "LSD_ENDCYCLE=0" in script
    assert "LSD_TSMIN=0" in script
    assert "LSD_TERMRAT=0" in script
    assert "LSD_PERMASS=0" in script
    assert "LSD_NOSOL=0" in script
    assert "cardimage=CONTROL_TERMINATION" not in script


def test_control_termination_template_info_includes_optional_fields():
    info = HmTemplateEngine().get_template_info("CONTROL_TERMINATION")

    assert info["source"] == "verified_hypermesh_mapping"
    assert info["entity_type"] == "cards"
    assert info["cardimage"] == "Termin"
    assert info["id_param"] is None
    assert info["fields"]["ENDTIM"] == "LSD_ENDTIM"
    assert info["optional_fields"] == {"NOSOL": "LSD_NOSOL"}


def test_database_binary_d3plot_uses_verified_card_mapping():
    script = HmTemplateEngine().render(
        "DATABASE_BINARY_D3PLOT",
        {"DT": 1e-4, "LCDT": 0, "BEAM": 0, "NPLTC": 10, "PSETID": 0, "IOOPT": 1},
    )

    assert "DATABASE_BINARY_D3PLOT -> DBplot" in script
    assert "cardimage=DBplot" in script
    assert "LSD_DT=0.0001" in script
    assert "LSD_LCID=0" in script
    assert "LSD_NOBEAM=0" in script
    assert "LSD_NPLTC=10" in script
    assert "LSD_PSID=0" in script
    assert "LSD_IOOPT=1" in script
    assert "cardimage=DATABASE_BINARY_D3PLOT" not in script


def test_database_binary_d3plot_can_omit_optional_ioopt():
    script = HmTemplateEngine().render(
        "DATABASE_BINARY_D3PLOT",
        {"DT": 1e-4, "LCDT": 0, "BEAM": 0, "NPLTC": 10, "PSETID": 0},
    )

    assert "LSD_IOOPT" not in script
