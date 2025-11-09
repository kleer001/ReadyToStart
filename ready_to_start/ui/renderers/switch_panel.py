from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class SwitchPanelRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("╔" + "═" * (self.width - 2) + "╗")
        output.append("║ FRONT PANEL - " + menu_node.category.upper().ljust(self.width - 17) + "║")
        output.append("╚" + "═" * (self.width - 2) + "╝")
        output.append("")

        for i, setting in enumerate(settings[:self.height - 8]):
            binary_state = "1" if setting.state == SettingState.ENABLED else "0"
            led = "●" if setting.state == SettingState.ENABLED else "○"
            switch = "▓" if setting.state == SettingState.ENABLED else "▒"

            line = f" [{i:02d}] {led} {switch} {setting.label[:50]} [{binary_state}]"
            output.append(line[:self.width])

        output.append("")
        output.append("TOGGLE SWITCH BY NUMBER")
        output.append("HALT/RESET: H    LOAD: L    RUN: R")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        binary = "1" if setting.state == SettingState.ENABLED else "0"
        led = "●●●●" if setting.state == SettingState.ENABLED else "○○○○"

        output.append("╔════════════════════════════════════╗")
        output.append("║ SWITCH CONFIGURATION               ║")
        output.append("╚════════════════════════════════════╝")
        output.append("")
        output.append(f"  {setting.label}")
        output.append(f"  LED: {led}")
        output.append(f"  BIT: {binary}")
        output.append("")
        output.append("  TOGGLE? (Y/N)")

        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("╔════════════════════════════════════╗")
        output.append("║ SYSTEM MESSAGE                     ║")
        output.append("╚════════════════════════════════════╝")
        output.append("")
        output.append(f"  {message}")
        output.append("")
        output.append("  ACKNOWLEDGE")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bits = 16
        filled = int(bits * progress)
        binary = "1" * filled + "0" * (bits - filled)
        leds = "●" * filled + "○" * (bits - filled)
        return f"{leds} {binary}"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[40m",
            "text": "\033[37m",
            "led_on": "\033[91m",
            "led_off": "\033[90m",
            "reset": "\033[0m",
        }
