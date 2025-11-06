"""Tests for core types module."""

import pytest

from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.types import Setting


def test_setting_creation(sample_setting):
    """Test basic setting creation."""
    assert sample_setting.id == "test_setting"
    assert sample_setting.type == SettingType.BOOLEAN
    assert sample_setting.value is False
    assert sample_setting.state == SettingState.DISABLED
    assert sample_setting.label == "Test Setting"
    assert sample_setting.visit_count == 0
    assert sample_setting.last_modified is None


def test_numeric_setting_bounds(numeric_setting):
    """Test numeric setting with bounds."""
    assert numeric_setting.min_value == 0
    assert numeric_setting.max_value == 100
    assert numeric_setting.value == 50


def test_setting_invalid_bounds():
    """Test that invalid bounds raise error."""
    with pytest.raises(ValueError):
        Setting(
            id="bad",
            type=SettingType.INTEGER,
            value=10,
            state=SettingState.ENABLED,
            label="Bad Setting",
            min_value=100,
            max_value=10,
        )


def test_setting_types():
    """Test different setting types."""
    bool_setting = Setting(
        id="bool",
        type=SettingType.BOOLEAN,
        value=True,
        state=SettingState.ENABLED,
        label="Bool",
    )
    assert bool_setting.value is True

    int_setting = Setting(
        id="int",
        type=SettingType.INTEGER,
        value=42,
        state=SettingState.ENABLED,
        label="Int",
    )
    assert int_setting.value == 42

    float_setting = Setting(
        id="float",
        type=SettingType.FLOAT,
        value=3.14,
        state=SettingState.ENABLED,
        label="Float",
    )
    assert float_setting.value == 3.14

    string_setting = Setting(
        id="str",
        type=SettingType.STRING,
        value="hello",
        state=SettingState.ENABLED,
        label="String",
    )
    assert string_setting.value == "hello"


def test_setting_states():
    """Test all setting states."""
    for state in SettingState:
        setting = Setting(
            id="test", type=SettingType.BOOLEAN, value=False, state=state, label="Test"
        )
        assert setting.state == state
