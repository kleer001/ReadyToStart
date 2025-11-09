from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class ModernRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("╭" + "─" * (self.width - 2) + "╮")
        output.append("│ " + menu_node.category.ljust(self.width - 4) + " │")
        output.append("├" + "─" * (self.width - 2) + "┤")
        output.append("│" + " " * (self.width - 2) + "│")

        for setting in settings[:self.height - 8]:
            toggle = "◉ On " if setting.state == SettingState.ENABLED else "○ Off"
            line = f"  {setting.label[:50]:<50s} {toggle}"
            output.append("│ " + line[:self.width - 4].ljust(self.width - 4) + " │")

        output.append("│" + " " * (self.width - 2) + "│")
        output.append("╰" + "─" * (self.width - 2) + "╯")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("╭" + "─" * 38 + "╮")
        output.append("│ Edit Setting" + " " * 26 + "│")
        output.append("├" + "─" * 38 + "┤")
        output.append("│" + " " * 38 + "│")
        output.append("│  " + setting.label[:34].ljust(34) + "  │")
        output.append("│  " + f"Value: {str(setting.value)[:28]:<28s}" + "  │")
        output.append("│" + " " * 38 + "│")
        output.append("│      [Save]        [Cancel]       │")
        output.append("╰" + "─" * 38 + "╯")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        icon = "⚠️ " if message_type == "warning" else "ℹ️ " if message_type == "info" else "❌ "
        output = []
        output.append("╭" + "─" * 38 + "╮")
        output.append("│ " + icon + message[:34].ljust(34) + " │")
        output.append("│" + " " * 38 + "│")
        output.append("│           [  OK  ]                │")
        output.append("╰" + "─" * 38 + "╯")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bar_width = 40
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        return f"{bar} {int(progress * 100)}%"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;248;249;250m",
            "text": "\033[38;2;33;37;41m",
            "accent": "\033[38;2;13;110;253m",
            "reset": "\033[0m",
        }
