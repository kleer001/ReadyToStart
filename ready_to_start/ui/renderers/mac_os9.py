from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class MacOS9Renderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("╔" + "═" * (self.width - 2) + "╗")
        output.append("║ " + menu_node.category[:self.width - 6].ljust(self.width - 6) + " ║░")
        output.append("╠" + "═" * (self.width - 2) + "╣")

        for setting in settings[:self.height - 7]:
            radio = "◉" if setting.state == SettingState.ENABLED else "○"
            line = f" {radio} {setting.label[:self.width - 10]}"
            output.append("║" + line.ljust(self.width - 3) + " ║░")

        output.append("╠" + "═" * (self.width - 2) + "╣")
        output.append("║  (Revert)       (Cancel)     (OK)  ║░")
        output.append("╚" + "═" * (self.width - 2) + "╝░")
        output.append(" " + "░" * (self.width - 1))

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("╔════════════════════════════════════╗")
        output.append("║ Edit Control Panel                ║░")
        output.append("╠════════════════════════════════════╣")
        output.append("║ " + setting.label[:34].ljust(34) + " ║░")
        output.append("║ Value: " + str(setting.value)[:27].ljust(27) + " ║░")
        output.append("║                                    ║░")
        output.append("║       (Cancel)       (OK)          ║░")
        output.append("╚════════════════════════════════════╝░")
        output.append(" " + "░" * 37)
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        icon = "⚠" if message_type == "warning" else "ℹ" if message_type == "info" else "✖"
        output = []
        output.append("╔════════════════════════════════════╗")
        output.append("║ Mac OS 9                          ║░")
        output.append("╠════════════════════════════════════╣")
        output.append("║ " + icon + " " + message[:31].ljust(31) + " ║░")
        output.append("║                                    ║░")
        output.append("║              (OK)                  ║░")
        output.append("╚════════════════════════════════════╝░")
        output.append(" " + "░" * 37)
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        filled = int(20 * progress)
        bar = "▓" * filled + "░" * (20 - filled)
        return f"[{bar}]"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[47m",
            "text": "\033[30m",
            "shadow": "\033[90m",
            "reset": "\033[0m",
        }
