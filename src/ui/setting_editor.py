from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from src.core.enums import SettingType
from src.core.types import Setting

if TYPE_CHECKING:
    from src.ui.keyboard import KeyboardReader


class EditorResult:
    def __init__(self, success: bool, value: Any = None, error: str = ""):
        self.success = success
        self.value = value
        self.error = error


class TypeEditor(ABC):
    def __init__(self):
        self.keyboard = None

    def set_keyboard(self, keyboard: "KeyboardReader"):
        self.keyboard = keyboard

    @abstractmethod
    def edit(self, setting: Setting) -> EditorResult:
        pass

    @abstractmethod
    def validate(self, value: Any, setting: Setting) -> bool:
        pass


class BooleanEditor(TypeEditor):
    def edit(self, setting: Setting) -> EditorResult:
        # Just toggle the boolean instantly - no confirmation needed!
        value = not setting.value

        if self.validate(value, setting):
            return EditorResult(True, value=value)
        return EditorResult(False, error="Validation failed")

    def validate(self, value: Any, setting: Setting) -> bool:
        return isinstance(value, bool)


class IntegerEditor(TypeEditor):
    def edit(self, setting: Setting) -> EditorResult:
        from src.ui.keyboard import Key

        if not self.keyboard:
            return EditorResult(False, error="No keyboard available")

        current_value = setting.value
        min_val = int(setting.min_value) if setting.min_value is not None else 0
        max_val = int(setting.max_value) if setting.max_value is not None else 100

        # Interactive editing with arrow keys
        with self.keyboard.normal_mode():
            print(f"\n{setting.label}: {current_value}")
            if setting.min_value is not None and setting.max_value is not None:
                print(f"Range: {min_val}-{max_val}")
            print("Use ↑/↓ to adjust, or type a number, then press Enter")
            print(f"Value: {current_value}", end="", flush=True)

        # Re-enable raw mode for interactive editing
        self.keyboard.enable_raw_mode()
        input_buffer = ""

        while True:
            key = self.keyboard.read_key()
            if not key:
                continue

            if key == Key.UP:
                current_value = min(current_value + 1, max_val)
                with self.keyboard.normal_mode():
                    print(f"\rValue: {current_value}  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.DOWN:
                current_value = max(current_value - 1, min_val)
                with self.keyboard.normal_mode():
                    print(f"\rValue: {current_value}  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.ENTER:
                if input_buffer:
                    try:
                        typed_value = int(input_buffer)
                        if min_val <= typed_value <= max_val:
                            current_value = typed_value
                    except ValueError:
                        pass
                break
            elif key == Key.ESC:
                return EditorResult(False, error="Cancelled")
            elif key.isdigit() or (key == '-' and not input_buffer):
                input_buffer += key
                with self.keyboard.normal_mode():
                    print(f"\rValue: {input_buffer}_  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.BACKSPACE and input_buffer:
                input_buffer = input_buffer[:-1]
                with self.keyboard.normal_mode():
                    print(f"\rValue: {input_buffer or current_value}_  ", end="", flush=True)
                self.keyboard.enable_raw_mode()

        with self.keyboard.normal_mode():
            print()  # New line after editing

        if self.validate(current_value, setting):
            return EditorResult(True, value=current_value)
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
        from src.ui.keyboard import Key

        if not self.keyboard:
            return EditorResult(False, error="No keyboard available")

        current_value = float(setting.value)
        min_val = float(setting.min_value) if setting.min_value is not None else 0.0
        max_val = float(setting.max_value) if setting.max_value is not None else 100.0
        step = 0.1  # Increment step for arrow keys

        # Interactive editing with arrow keys
        with self.keyboard.normal_mode():
            print(f"\n{setting.label}: {current_value}")
            if setting.min_value is not None and setting.max_value is not None:
                print(f"Range: {min_val}-{max_val}")
            print("Use ↑/↓ to adjust by 0.1, or type a number, then press Enter")
            print(f"Value: {current_value:.1f}", end="", flush=True)

        # Re-enable raw mode for interactive editing
        self.keyboard.enable_raw_mode()
        input_buffer = ""

        while True:
            key = self.keyboard.read_key()
            if not key:
                continue

            if key == Key.UP:
                current_value = min(round(current_value + step, 1), max_val)
                with self.keyboard.normal_mode():
                    print(f"\rValue: {current_value:.1f}  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.DOWN:
                current_value = max(round(current_value - step, 1), min_val)
                with self.keyboard.normal_mode():
                    print(f"\rValue: {current_value:.1f}  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.ENTER:
                if input_buffer:
                    try:
                        typed_value = float(input_buffer)
                        if min_val <= typed_value <= max_val:
                            current_value = round(typed_value, 1)
                    except ValueError:
                        pass
                break
            elif key == Key.ESC:
                return EditorResult(False, error="Cancelled")
            elif key.isdigit() or key in ['.', '-'] or (key == '-' and not input_buffer):
                input_buffer += key
                with self.keyboard.normal_mode():
                    print(f"\rValue: {input_buffer}_  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.BACKSPACE and input_buffer:
                input_buffer = input_buffer[:-1]
                with self.keyboard.normal_mode():
                    print(f"\rValue: {input_buffer or f'{current_value:.1f}'}_  ", end="", flush=True)
                self.keyboard.enable_raw_mode()

        with self.keyboard.normal_mode():
            print()  # New line after editing

        if self.validate(current_value, setting):
            return EditorResult(True, value=current_value)
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
        # For strings, use normal input mode
        if self.keyboard and hasattr(self.keyboard, 'normal_mode'):
            with self.keyboard.normal_mode():
                print(f"\n{setting.label}")
                print(f"Current: {setting.value}")
                print("Enter new value (or press Enter to keep current): ", end="")
                value = input().strip()
                if not value:  # If empty, keep current value
                    value = setting.value
        else:
            print(f"\n{setting.label}")
            print(f"Current: {setting.value}")
            print("Enter new value (or press Enter to keep current): ", end="")
            value = input().strip()
            if not value:  # If empty, keep current value
                value = setting.value

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
        self.keyboard = None

    def set_keyboard(self, keyboard: "KeyboardReader"):
        self.keyboard = keyboard
        for editor in self.editors.values():
            editor.set_keyboard(keyboard)

    def edit_setting(self, setting: Setting) -> EditorResult:
        editor = self.editors.get(setting.type)
        if not editor:
            return EditorResult(False, error=f"No editor for type {setting.type}")

        return editor.edit(setting)
