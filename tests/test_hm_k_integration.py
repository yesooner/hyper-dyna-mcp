"""Tests for offline K-file to HyperMesh integration helpers."""

from pathlib import Path

from program.tools import hm_k_integration
from program.tools.hm_k_integration import generate_integration_script, integrate_k_file

_SAMPLES = Path(__file__).resolve().parents[1] / "lib" / "k_samples"


def test_integrate_k_file_dry_run_is_offline_plan_only():
    result = integrate_k_file(_SAMPLES / "minimal_solid.k", dry_run=True)

    assert result.success is True
    assert result.execution_allowed is False
    assert result.tcl_sent is False
    assert result.error_type is None


def test_integrate_k_file_blocks_real_execution(monkeypatch):
    def fail_execute(*args, **kwargs):
        raise AssertionError("K-file integration must not send Tcl to HyperMesh")

    monkeypatch.setattr(hm_k_integration, "execute_tcl_gui", fail_execute, raising=False)

    result = integrate_k_file(_SAMPLES / "minimal_solid.k", dry_run=False)

    assert result.success is False
    assert result.error_type == "k_file_integration_execution_not_verified"
    assert result.execution_allowed is False
    assert result.tcl_sent is False
    assert result.errors


def test_generate_integration_script_is_advisory_only():
    doc = generate_integration_script.__doc__ or ""
    assert "must not be" in doc
    assert "comments" in doc
    assert "manual execution" not in doc
    assert "batch mode" not in doc

    script = generate_integration_script(_SAMPLES / "minimal_solid.k")

    assert isinstance(script, str)
    assert "*createnode" in script or "*createentity" in script
    assert "ADVISORY ONLY" in script

    executable_lines = [
        line
        for line in script.splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and (line.lstrip().startswith("*") or line.lstrip().startswith("hm_"))
    ]
    assert executable_lines == []


def test_k_integration_private_helpers_document_advisory_text_lines():
    import inspect

    helper_sources = [
        inspect.getsource(hm_k_integration._generate_mat_tcl),
        inspect.getsource(hm_k_integration._generate_section_tcl),
        inspect.getsource(hm_k_integration._generate_part_tcl),
        inspect.getsource(hm_k_integration._generate_node_tcl),
        inspect.getsource(hm_k_integration._generate_element_tcl),
        inspect.getsource(hm_k_integration._generate_contact_tcl),
        inspect.getsource(hm_k_integration._generate_boundary_tcl),
        inspect.getsource(hm_k_integration._generate_load_tcl),
        inspect.getsource(hm_k_integration._generate_set_tcl),
    ]

    for source in helper_sources:
        assert "advisory Tcl text lines" in source
        assert "Generate Tcl commands" not in source
