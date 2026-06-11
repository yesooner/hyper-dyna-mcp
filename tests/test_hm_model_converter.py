from program.tools import hm_model_converter


def test_convert_model_to_lsdyne_is_blocked_before_verified_routes(monkeypatch):
    result = hm_model_converter.convert_model_to_lsdyne()

    assert result["success"] is False
    assert result["error_type"] == "lsdyna_profile_conversion_not_verified"
    assert result["execution_allowed"] is False
    assert result["tcl_sent"] is False
    assert "assign_material_to_hex_part" in result["required_routes"]
    assert result["required_tool"] == "hm_modeling_action"


def test_all_converter_compatibility_helpers_are_blocked():
    calls = [
        hm_model_converter.check_connection(),
        hm_model_converter.get_material_ids(),
        hm_model_converter.get_property_ids(),
        hm_model_converter.find_lsdyna_template(),
        hm_model_converter.convert_materials_to_lsdyne(),
        hm_model_converter.convert_properties_to_lsdyne(),
        hm_model_converter.verify_conversion(),
    ]

    for result in calls:
        assert result["success"] is False
        assert result["error_type"] == "lsdyna_profile_conversion_not_verified"
        assert result["execution_allowed"] is False
        assert result["tcl_sent"] is False
        assert result["required_tool"] == "hm_modeling_action"


def test_converter_module_does_not_import_gui_execution_helpers():
    assert not hasattr(hm_model_converter, "execute_tcl_gui")
    assert not hasattr(hm_model_converter, "send_tcl_to_gui")
    assert not hasattr(hm_model_converter, "activate_lsdyne_template")
