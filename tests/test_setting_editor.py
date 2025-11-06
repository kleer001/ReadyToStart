import pytest

from ready_to_start.core.enums import SettingType
from ready_to_start.core.types import Setting
from ready_to_start.ui.setting_editor import (
    BooleanEditor,
    FloatEditor,
    IntegerEditor,
    SettingEditor,
    StringEditor,
)


def test_boolean_editor_validate():
    editor = BooleanEditor()
    setting = Setting(
        id="test", type=SettingType.BOOLEAN, value=False, state=None, label="Test"
    )

    assert editor.validate(True, setting) is True
    assert editor.validate(False, setting) is True
    assert editor.validate("true", setting) is False


def test_integer_editor_validate():
    editor = IntegerEditor()
    setting = Setting(
        id="test",
        type=SettingType.INTEGER,
        value=50,
        state=None,
        label="Test",
        min_value=0,
        max_value=100,
    )

    assert editor.validate(50, setting) is True
    assert editor.validate(0, setting) is True
    assert editor.validate(100, setting) is True
    assert editor.validate(-1, setting) is False
    assert editor.validate(101, setting) is False


def test_float_editor_validate():
    editor = FloatEditor()
    setting = Setting(
        id="test",
        type=SettingType.FLOAT,
        value=0.5,
        state=None,
        label="Test",
        min_value=0.0,
        max_value=1.0,
    )

    assert editor.validate(0.5, setting) is True
    assert editor.validate(0.0, setting) is True
    assert editor.validate(1.0, setting) is True
    assert editor.validate(-0.1, setting) is False
    assert editor.validate(1.1, setting) is False


def test_string_editor_validate():
    editor = StringEditor()
    setting = Setting(id="test", type=SettingType.STRING, value="test", state=None, label="Test")

    assert editor.validate("valid", setting) is True
    assert editor.validate("", setting) is False


def test_setting_editor_has_all_editors():
    editor = SettingEditor()

    assert SettingType.BOOLEAN in editor.editors
    assert SettingType.INTEGER in editor.editors
    assert SettingType.FLOAT in editor.editors
    assert SettingType.STRING in editor.editors
