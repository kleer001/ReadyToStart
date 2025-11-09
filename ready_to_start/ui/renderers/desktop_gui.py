from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class DesktopGUIRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("┌" + "─" * (self.width - 2) + "┐")
        output.append("│ File  Edit  View  Tools  Help" + " " * (self.width - 33) + "│")
        output.append("├" + "─" * (self.width - 2) + "┤")
        output.append("│ " + menu_node.category.ljust(self.width - 4) + " │")
        output.append("├" + "─" * (self.width - 2) + "┤")

        for setting in settings[:self.height - 9]:
            check = "[✓]" if setting.state == SettingState.ENABLED else "[ ]"
            line = f" {check} {setting.label[:65]}"
            output.append("│" + line[:self.width - 2].ljust(self.width - 2) + "│")

        output.append("├" + "─" * (self.width - 2) + "┤")
        output.append("│ [  OK  ] [  Apply  ] [ Cancel ]" + " " * (self.width - 35) + "│")
        output.append("└" + "─" * (self.width - 2) + "┘")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("┌─────────────────────────────────┐")
        output.append("│ Properties                      │")
        output.append("├─────────────────────────────────┤")
        output.append("│ Name: " + setting.label[:25].ljust(25) + " │")
        output.append("│ Value: " + str(setting.value)[:24].ljust(24) + " │")
        output.append("│                                 │")
        output.append("│   [  OK  ]     [ Cancel ]       │")
        output.append("└─────────────────────────────────┘")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("┌─────────────────────────────────┐")
        output.append("│ Application Message             │")
        output.append("├─────────────────────────────────┤")
        output.append("│ " + message[:31].ljust(31) + " │")
        output.append("│                                 │")
        output.append("│          [  OK  ]               │")
        output.append("└─────────────────────────────────┘")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bar_width = 40
        filled = int(bar_width * progress)
        bar = "▓" * filled + "░" * (bar_width - filled)
        return f"[{bar}] {int(progress * 100)}%"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[47m",
            "text": "\033[30m",
            "menu_bar": "\033[46m",
            "reset": "\033[0m",
        }
