"""Tests for offline HyperMesh template review guardrails."""

from program.tools import hm_template_validator


def test_validate_template_defaults_to_offline_blocked(tmp_path, monkeypatch):
    tpl_dir = tmp_path / "templates" / "keyword" / "control"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "CONTROL_TEST.tcl").write_text(
        '*createentity cards name=CONTROL_TEST cardimage=Test\n'
        '*setvalue cards id=1 dataname=FOO value={{FOO}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(hm_template_validator, "TEMPLATES_DIR", tmp_path / "templates" / "keyword")

    assert not hasattr(hm_template_validator, "execute_tcl_gui")

    result = hm_template_validator.validate_template("CONTROL_TEST")

    assert result["status"] == "blocked"
    assert result["error_type"] == "template_execution_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["first_command"].startswith("*createentity")
    assert result["requested_execute"] is False


def test_validate_template_execute_true_still_blocks_tcl(tmp_path, monkeypatch):
    tpl_dir = tmp_path / "templates" / "keyword" / "control"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "CONTROL_TEST.tcl").write_text(
        '*createentity cards name=CONTROL_TEST cardimage=Test\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(hm_template_validator, "TEMPLATES_DIR", tmp_path / "templates" / "keyword")

    assert not hasattr(hm_template_validator, "execute_tcl_gui")

    result = hm_template_validator.validate_template("CONTROL_TEST", execute=True)

    assert result["status"] == "blocked"
    assert result["error_type"] == "template_execution_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert result["requested_execute"] is True
    assert result["first_command"].startswith("*createentity")


def test_validate_all_counts_blocked_templates(tmp_path, monkeypatch):
    tpl_dir = tmp_path / "templates" / "keyword" / "control"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "CONTROL_TEST.tcl").write_text(
        '*createentity cards name=CONTROL_TEST cardimage=Test\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(hm_template_validator, "TEMPLATES_DIR", tmp_path / "templates" / "keyword")

    report = hm_template_validator.validate_all(batch_size=10)

    assert report["total"] == 1
    assert report["blocked"] == ["control/CONTROL_TEST"]
    assert report["categories"]["control"]["blocked"] == 1
    assert report["ok"] == []
    assert report["fail"] == []
