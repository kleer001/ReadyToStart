import pytest
from pathlib import Path

from src.core.layer_manager import InterfaceLayer, LayerManager


@pytest.fixture
def layer_manager():
    manager = LayerManager()
    layers_file = Path(__file__).parent.parent / "data" / "interface_layers.json"
    manager.load_layers(layers_file)
    return manager


def test_load_layers(layer_manager):
    assert len(layer_manager.layers) == 17
    assert "modern_settings_2020s" in layer_manager.layers
    assert "final_layer" in layer_manager.layers


def test_interface_layer_attributes():
    layer = InterfaceLayer(
        id="test",
        name="Test Layer",
        era="2020s",
        complexity=5,
        ui_paradigm="test_paradigm",
        features=["feature1", "feature2"],
        color_scheme="test_colors",
        next_layer_options=["next1", "next2"],
    )

    assert layer.id == "test"
    assert layer.name == "Test Layer"
    assert layer.complexity == 5
    assert len(layer.features) == 2
    assert len(layer.next_layer_options) == 2


def test_start_at_layer(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")

    assert layer_manager.current_layer_id == "modern_settings_2020s"
    assert layer_manager.layer_history == ["modern_settings_2020s"]


def test_start_at_invalid_layer(layer_manager):
    with pytest.raises(ValueError, match="Unknown layer"):
        layer_manager.start_at_layer("nonexistent_layer")


def test_get_current_layer(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")
    current = layer_manager.get_current_layer()

    assert current is not None
    assert current.id == "modern_settings_2020s"
    assert current.name == "Modern Settings Menu"


def test_get_current_layer_none():
    manager = LayerManager()
    assert manager.get_current_layer() is None


def test_get_next_layer_options_basic(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")
    options = layer_manager.get_next_layer_options({})

    assert "webapp_2010s" in options
    assert "mobile_2015" in options


def test_get_next_layer_options_high_efficiency(layer_manager):
    layer_manager.start_at_layer("desktop_gui_2000s")
    options = layer_manager.get_next_layer_options({"efficiency": 80})

    assert options == ["windows_95"]


def test_get_next_layer_options_low_efficiency(layer_manager):
    layer_manager.start_at_layer("desktop_gui_2000s")
    options = layer_manager.get_next_layer_options({"efficiency": 20})

    assert options == ["mac_os_9"]


def test_get_next_layer_options_took_too_long(layer_manager):
    layer_manager.start_at_layer("desktop_gui_2000s")
    options = layer_manager.get_next_layer_options({"time_spent": 700})

    assert options == ["dos_config"]


def test_get_next_layer_options_found_secret(layer_manager):
    layer_manager.start_at_layer("bios_setup")
    options = layer_manager.get_next_layer_options({"secrets_found": 1})

    assert options == ["quantum_interface"]


def test_transition_to_layer_valid(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")
    success = layer_manager.transition_to_layer("webapp_2010s")

    assert success is True
    assert layer_manager.current_layer_id == "webapp_2010s"
    assert layer_manager.layer_history == ["modern_settings_2020s", "webapp_2010s"]


def test_transition_to_layer_invalid_target(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")
    success = layer_manager.transition_to_layer("nonexistent")

    assert success is False
    assert layer_manager.current_layer_id == "modern_settings_2020s"


def test_transition_to_layer_invalid_path(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")
    success = layer_manager.transition_to_layer("final_layer")

    assert success is False
    assert layer_manager.current_layer_id == "modern_settings_2020s"


def test_get_layer_depth(layer_manager):
    layer_manager.start_at_layer("modern_settings_2020s")
    assert layer_manager.get_layer_depth() == 1

    layer_manager.transition_to_layer("webapp_2010s")
    assert layer_manager.get_layer_depth() == 2

    layer_manager.transition_to_layer("desktop_gui_2000s")
    assert layer_manager.get_layer_depth() == 3


def test_is_final_layer(layer_manager):
    layer_manager.start_at_layer("final_layer")
    assert layer_manager.is_final_layer() is True

    layer_manager.start_at_layer("modern_settings_2020s")
    assert layer_manager.is_final_layer() is False


def test_get_standard_path(layer_manager):
    standard_path = layer_manager.get_standard_path()

    assert len(standard_path) == 9
    assert standard_path[0] == "modern_settings_2020s"
    assert standard_path[-1] == "final_layer"


def test_get_alternate_paths(layer_manager):
    alternate_paths = layer_manager.get_alternate_paths()

    assert "mobile_branch" in alternate_paths
    assert "mac_branch" in alternate_paths
    assert "quantum_shortcut" in alternate_paths


def test_progression_rules_loaded(layer_manager):
    assert layer_manager.progression_rules is not None
    assert "standard_path" in layer_manager.progression_rules
    assert "alternate_paths" in layer_manager.progression_rules
    assert "branching_points" in layer_manager.progression_rules


def test_complete_standard_path(layer_manager):
    standard_path = layer_manager.get_standard_path()
    layer_manager.start_at_layer(standard_path[0])

    for i in range(len(standard_path) - 1):
        current_layer = layer_manager.get_current_layer()
        next_layer_id = standard_path[i + 1]

        assert next_layer_id in current_layer.next_layer_options
        success = layer_manager.transition_to_layer(next_layer_id)
        assert success is True

    assert layer_manager.is_final_layer() is True


def test_layer_complexity_progression(layer_manager):
    complexities = []
    for layer_id in layer_manager.get_standard_path():
        layer = layer_manager.layers[layer_id]
        complexities.append(layer.complexity)

    assert complexities[0] == 3
    assert max(complexities) in [9, 10]
    assert complexities[-1] == 1
