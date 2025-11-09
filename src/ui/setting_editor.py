from abc import ABC, abstractmethod
from typing import Any

from src.core.enums import SettingType
from src.core.types import Setting


class EditorResult:
    def __init__(self, success: bool, value: Any = None, error: str = ""):
        self.success = success
        self.value = value
        self.error = error


class TypeEditor(ABC):
    @abstractmethod
    def edit(self, setting: Setting) -> EditorResult:
        pass

    @abstractmethod
    def validate(self, value: Any, setting: Setting) -> bool:
        pass


class BooleanEditor(TypeEditor):
    def edit(self, setting: Setting) -> EditorResult:
        print(f"\nEdit: {setting.label} (boolean)")
        print(f"Current value: {setting.value}")
        print("Enter 'true' or 'false' (or 't'/'f'): ", end="")

        user_input = input().strip().lower()

        if user_input in ["true", "t", "1", "yes", "y"]:
            value = True
        elif user_input in ["false", "f", "0", "no", "n"]:
            value = False
        else:
            return EditorResult(False, error="Invalid boolean value")

        if self.validate(value, setting):
            return EditorResult(True, value=value)
        return EditorResult(False, error="Validation failed")

    def validate(self, value: Any, setting: Setting) -> bool:
        return isinstance(value, bool)


class IntegerEditor(TypeEditor):
    def edit(self, setting: Setting) -> EditorResult:
        print(f"\nEdit: {setting.label} (integer)")
        print(f"Current value: {setting.value}")

        if setting.min_value is not None and setting.max_value is not None:
            print(f"Range: {int(setting.min_value)}-{int(setting.max_value)}")

        print("Enter new value: ", end="")
        user_input = input().strip()

        try:
            value = int(user_input)
        except ValueError:
            return EditorResult(False, error="Invalid integer value")

        if self.validate(value, setting):
            return EditorResult(True, value=value)
        return EditorResult(False, error="Value out of range")

    def validate(self, value: Any, setting: Setting) -> bool:
        if not isinstance(value, int):
            return False

        if setting.min_value is not None and value < setting.min_value:
            return False

        if setting.max_value is not None and value > setting.max_value:
            return False

        return True


class FloatEditor(TypeEditor):
    def edit(self, setting: Setting) -> EditorResult:
        print(f"\nEdit: {setting.label} (float)")
        print(f"Current value: {setting.value}")

        if setting.min_value is not None and setting.max_value is not None:
            print(f"Range: {setting.min_value}-{setting.max_value}")

        print("Enter new value: ", end="")
        user_input = input().strip()

        try:
            value = float(user_input)
        except ValueError:
            return EditorResult(False, error="Invalid float value")

        if self.validate(value, setting):
            return EditorResult(True, value=value)
        return EditorResult(False, error="Value out of range")

    def validate(self, value: Any, setting: Setting) -> bool:
        if not isinstance(value, (int, float)):
            return False

        if setting.min_value is not None and value < setting.min_value:
            return False

        if setting.max_value is not None and value > setting.max_value:
            return False

        return True


class StringEditor(TypeEditor):
    def edit(self, setting: Setting) -> EditorResult:
        print(f"\nEdit: {setting.label} (string)")
        print(f"Current value: {setting.value}")
        print("Enter new value: ", end="")

        value = input().strip()

        if self.validate(value, setting):
            return EditorResult(True, value=value)
        return EditorResult(False, error="Invalid string value")

    def validate(self, value: Any, setting: Setting) -> bool:
        return isinstance(value, str) and len(value) > 0


class SettingEditor:
    def __init__(self):
        self.editors = {
            SettingType.BOOLEAN: BooleanEditor(),
            SettingType.INTEGER: IntegerEditor(),
            SettingType.FLOAT: FloatEditor(),
            SettingType.STRING: StringEditor(),
        }

    def edit_setting(self, setting: Setting) -> EditorResult:
        editor = self.editors.get(setting.type)
        if not editor:
            return EditorResult(False, error=f"No editor for type {setting.type}")

        return editor.edit(setting)
