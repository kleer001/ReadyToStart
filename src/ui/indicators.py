import time
from configparser import ConfigParser

from src.core.enums import SettingState


class StateIndicator:
    def __init__(self, config_path: str):
        self.config = ConfigParser()
        self.config.read(config_path)
        self.frame_counter = 0
        self.last_update = time.time()

    def _get_symbol(self, state: SettingState) -> str:
        return self.config.get("symbols", state.value, fallback="[?]")

    def _get_color(self, state: SettingState) -> str:
        return self.config.get("colors", state.value, fallback="white")

    def _should_update_frame(self) -> bool:
        current_time = time.time()
        blink_speed = float(self.config.get("animation", "blink_speed", fallback="0.5"))

        if current_time - self.last_update >= blink_speed:
            self.last_update = current_time
            self.frame_counter = (self.frame_counter + 1) % 2
            return True
        return False

    def get_indicator(self, state: SettingState) -> str:
        """Return indicator symbol for a setting state.

        Note: Colors are now handled by the ncurses renderer, not by ANSI codes.
        This method just returns the plain symbol.
        """
        if state == SettingState.BLINKING:
            self._should_update_frame()
            if self.frame_counter == 0:
                symbol = self._get_symbol(SettingState.ENABLED)
            else:
                symbol = self._get_symbol(SettingState.DISABLED)
        else:
            symbol = self._get_symbol(state)

        return symbol if symbol else ""

    def reset_animation(self):
        self.frame_counter = 0
        self.last_update = time.time()
