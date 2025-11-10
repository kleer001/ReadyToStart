import curses
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
    def __init__(self):
        self.stdscr = None

    @abstractmethod
    def edit(self, setting: Setting, stdscr) -> EditorResult:
        pass

    @abstractmethod
    def validate(self, value: Any, setting: Setting) -> bool:
        pass


class BooleanEditor(TypeEditor):
    def edit(self, setting: Setting, stdscr) -> EditorResult:
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

    def _is_valid_input_char(self, char: str, buffer: str) -> bool:
        """Check if character is valid for numeric input."""
        raise NotImplementedError

    def edit(self, setting: Setting, stdscr) -> EditorResult:
        if not stdscr:
            return EditorResult(False, error="No screen available")

        current_value = self.parse_input(str(setting.value))
        min_val, max_val = self.get_bounds(setting)

        # Save screen state and configure for modal input
        curses.curs_set(1)  # Show cursor
        stdscr.nodelay(False)  # Blocking input

        # Clear and show editing interface
        stdscr.clear()
        y = 0
        stdscr.addstr(y, 0, f"{setting.label}: {self.format_value(current_value)}")
        y += 1

        if setting.min_value is not None and setting.max_value is not None:
            stdscr.addstr(y, 0, f"Range: {self.format_value(min_val)}-{self.format_value(max_val)}")
            y += 1

        step_text = f"by {self.format_value(self.step)}" if self.step != 1 else ""
        stdscr.addstr(y, 0, f"Use ↑/↓ to adjust{' ' + step_text if step_text else ''}, or type a number, then press Enter")
        y += 2

        value_y = y
        input_buffer = ""

        while True:
            # Display current value or buffer
            display = input_buffer if input_buffer else self.format_value(current_value)
            stdscr.move(value_y, 0)
            stdscr.clrtoeol()
            stdscr.addstr(value_y, 0, f"Value: {display}")
            if input_buffer:
                stdscr.addstr("_")
            stdscr.refresh()

            # Read key
            ch = stdscr.getch()

            if ch == curses.KEY_UP:
                input_buffer = ""
                current_value = self.adjust_value(current_value, 1, min_val, max_val)
            elif ch == curses.KEY_DOWN:
                input_buffer = ""
                current_value = self.adjust_value(current_value, -1, min_val, max_val)
            elif ch == ord('\n') or ch == ord('\r'):
                if input_buffer:
                    try:
                        typed_value = self.parse_input(input_buffer)
                        if min_val <= typed_value <= max_val:
                            current_value = typed_value
                    except ValueError:
                        pass
                break
            elif ch == 27:  # ESC
                curses.curs_set(0)
                stdscr.nodelay(True)
                return EditorResult(False, error="Cancelled")
            elif ch in (curses.KEY_BACKSPACE, 127, 8) and input_buffer:
                input_buffer = input_buffer[:-1]
            elif 0 <= ch < 256:
                char = chr(ch)
                if self._is_valid_input_char(char, input_buffer):
                    input_buffer += char

        # Restore screen state
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input

        if self.validate(current_value, setting):
            return EditorResult(True, value=current_value)
        return EditorResult(False, error="Value out of range")


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
    def edit(self, setting: Setting, stdscr) -> EditorResult:
        if not stdscr:
            return EditorResult(False, error="No screen available")

        # Save screen state
        curses.curs_set(1)  # Show cursor
        stdscr.nodelay(False)  # Blocking input
        curses.echo()  # Show typed characters

        # Clear and show editing interface
        stdscr.clear()
        stdscr.addstr(0, 0, f"{setting.label}")
        stdscr.addstr(1, 0, f"Current: {setting.value}")
        stdscr.addstr(2, 0, "Enter new value (or press Enter to keep current): ")
        stdscr.refresh()

        # Get input
        value = stdscr.getstr(3, 0, 100).decode('utf-8').strip()

        # Restore screen state
        curses.noecho()
        curses.curs_set(0)
        stdscr.nodelay(True)

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

    def edit_setting(self, setting: Setting, stdscr) -> EditorResult:
        editor = self.editors.get(setting.type)
        if not editor:
            return EditorResult(False, error=f"No editor for type {setting.type}")

        return editor.edit(setting, stdscr)
