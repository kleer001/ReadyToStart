from src.core.enums import SettingState
from src.ui.renderers.base import EraRenderer


class DesktopGUIRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("┌" + "─" * (self.width - 2) + "┐")
        menu_bar = "File  Edit  View  Tools  Help"
        output.append("│ " + menu_bar[:self.width - 4].ljust(self.width - 4) + " │")
        output.append("├" + "─" * (self.width - 2) + "┤")
        output.append("│ " + menu_node.category[:self.width - 4].ljust(self.width - 4) + " │")
        output.append("├" + "─" * (self.width - 2) + "┤")

        for setting in settings[:self.height - 9]:
            check = "[✓]" if setting.state == SettingState.ENABLED else "[ ]"
            label_width = self.width - 2 - 1 - len(check) - 1
            line = f" {check} {setting.label[:label_width]}"
            output.append("│" + line[:self.width - 2].ljust(self.width - 2) + "│")

        output.append("├" + "─" * (self.width - 2) + "┤")
        buttons = "[  OK  ] [  Apply  ] [ Cancel ]"
        output.append("│ " + buttons[:self.width - 4].ljust(self.width - 4) + " │")
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
