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


class NumericEditor(TypeEditor):
    """Base class for integer and float editors to eliminate duplication (DRY principle)."""

    def __init__(self):
        super().__init__()
        self.step = 1  # Override in subclasses

    def get_bounds(self, setting: Setting) -> tuple[Any, Any]:
        """Get min/max bounds - subclasses override for type conversion."""
        raise NotImplementedError

    def format_value(self, value: Any) -> str:
        """Format value for display - subclasses override."""
        return str(value)

    def parse_input(self, input_str: str) -> Any:
        """Parse user input string - subclasses override."""
        raise NotImplementedError

    def adjust_value(self, current: Any, delta: int, min_val: Any, max_val: Any) -> Any:
        """Adjust value by step * delta, clamped to bounds."""
        raise NotImplementedError

    def _show_header(self, setting: Setting, current_value: Any, min_val: Any, max_val: Any):
        """Display editing header with instructions."""
        print(f"\n{setting.label}: {self.format_value(current_value)}")
        if setting.min_value is not None and setting.max_value is not None:
            print(f"Range: {self.format_value(min_val)}-{self.format_value(max_val)}")
        step_text = f"by {self.format_value(self.step)}" if self.step != 1 else ""
        print(f"Use ↑/↓ to adjust{' ' + step_text if step_text else ''}, or type a number, then press Enter")

    def _display_value(self, value: Any):
        """Update the displayed value in-place."""
        print(f"\rValue: {self.format_value(value)}  ", end="", flush=True)

    def _handle_typed_input(self, input_buffer: str, min_val: Any, max_val: Any) -> Any | None:
        """Parse and validate typed input. Returns value or None if invalid."""
        try:
            typed_value = self.parse_input(input_buffer)
            if min_val <= typed_value <= max_val:
                return typed_value
        except ValueError:
            pass
        return None

    def edit(self, setting: Setting) -> EditorResult:
        from src.ui.keyboard import Key

        if not self.keyboard:
            return EditorResult(False, error="No keyboard available")

        current_value = self.parse_input(str(setting.value))
        min_val, max_val = self.get_bounds(setting)

        # Show header in normal mode
        with self.keyboard.normal_mode():
            self._show_header(setting, current_value, min_val, max_val)
            self._display_value(current_value)

        # Interactive editing in raw mode
        self.keyboard.enable_raw_mode()
        input_buffer = ""

        while True:
            key = self.keyboard.read_key()
            if not key:
                continue

            if key == Key.UP:
                current_value = self.adjust_value(current_value, 1, min_val, max_val)
                with self.keyboard.normal_mode():
                    self._display_value(current_value)
                self.keyboard.enable_raw_mode()
            elif key == Key.DOWN:
                current_value = self.adjust_value(current_value, -1, min_val, max_val)
                with self.keyboard.normal_mode():
                    self._display_value(current_value)
                self.keyboard.enable_raw_mode()
            elif key == Key.ENTER:
                if input_buffer:
                    typed_value = self._handle_typed_input(input_buffer, min_val, max_val)
                    if typed_value is not None:
                        current_value = typed_value
                break
            elif key == Key.ESC:
                return EditorResult(False, error="Cancelled")
            elif self._is_valid_input_char(key, input_buffer):
                input_buffer += key
                with self.keyboard.normal_mode():
                    print(f"\rValue: {input_buffer}_  ", end="", flush=True)
                self.keyboard.enable_raw_mode()
            elif key == Key.BACKSPACE and input_buffer:
                input_buffer = input_buffer[:-1]
                display = input_buffer if input_buffer else self.format_value(current_value)
                with self.keyboard.normal_mode():
                    print(f"\rValue: {display}_  ", end="", flush=True)
                self.keyboard.enable_raw_mode()

        with self.keyboard.normal_mode():
            print()  # New line after editing

        if self.validate(current_value, setting):
            return EditorResult(True, value=current_value)
        return EditorResult(False, error="Value out of range")

    def _is_valid_input_char(self, char: str, buffer: str) -> bool:
        """Check if character is valid for numeric input."""
        raise NotImplementedError


class IntegerEditor(NumericEditor):
    def __init__(self):
        super().__init__()
        self.step = 1

    def get_bounds(self, setting: Setting) -> tuple[int, int]:
        min_val = int(setting.min_value) if setting.min_value is not None else 0
        max_val = int(setting.max_value) if setting.max_value is not None else 100
        return min_val, max_val

    def format_value(self, value: Any) -> str:
        return str(int(value))

    def parse_input(self, input_str: str) -> int:
        return int(input_str)

    def adjust_value(self, current: int, delta: int, min_val: int, max_val: int) -> int:
        return max(min_val, min(max_val, current + delta * self.step))

    def _is_valid_input_char(self, char: str, buffer: str) -> bool:
        return char.isdigit() or (char == '-' and not buffer)

    def validate(self, value: Any, setting: Setting) -> bool:
        if not isinstance(value, int):
            return False
        if setting.min_value is not None and value < setting.min_value:
            return False
        if setting.max_value is not None and value > setting.max_value:
            return False
        return True


class FloatEditor(NumericEditor):
    def __init__(self):
        super().__init__()
        self.step = 0.1

    def get_bounds(self, setting: Setting) -> tuple[float, float]:
        min_val = float(setting.min_value) if setting.min_value is not None else 0.0
        max_val = float(setting.max_value) if setting.max_value is not None else 100.0
        return min_val, max_val

    def format_value(self, value: Any) -> str:
        return f"{float(value):.1f}"

    def parse_input(self, input_str: str) -> float:
        return round(float(input_str), 1)

    def adjust_value(self, current: float, delta: int, min_val: float, max_val: float) -> float:
        return max(min_val, min(max_val, round(current + delta * self.step, 1)))

    def _is_valid_input_char(self, char: str, buffer: str) -> bool:
        return char.isdigit() or char in ['.', '-'] and (char != '-' or not buffer)

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
