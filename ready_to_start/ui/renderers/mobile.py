from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class MobileRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("╭" + "─" * (self.width - 2) + "╮")
        header = f"☰  {menu_node.category}"
        header_padded = header[:self.width - 8].ljust(self.width - 8) + " ⋮"
        output.append("│ " + header_padded[:self.width - 4].ljust(self.width - 4) + " │")
        output.append("╰" + "─" * (self.width - 2) + "╯")
        output.append("")

        for setting in settings[:self.height - 6]:
            toggle = " ●" if setting.state == SettingState.ENABLED else " ○"
            label_width = self.width - 4 - len(toggle)
            line = setting.label[:label_width].ljust(label_width) + toggle
            output.append("┌" + "─" * (self.width - 2) + "┐")
            output.append("│ " + line[:self.width - 4].ljust(self.width - 4) + " │")
            output.append("└" + "─" * (self.width - 2) + "┘")
            output.append("")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("╭" + "─" * 36 + "╮")
        output.append("│ ←  Edit" + " " * 28 + "│")
        output.append("╰" + "─" * 36 + "╯")
        output.append("")
        output.append("╭" + "─" * 36 + "╮")
        output.append("│ " + setting.label[:34].ljust(34) + " │")
        output.append("│" + " " * 36 + "│")
        output.append("│ " + str(setting.value)[:34].ljust(34) + " │")
        output.append("╰" + "─" * 36 + "╯")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("")
        output.append("╭" + "─" * 36 + "╮")
        output.append("│ " + message[:34].center(34) + " │")
        output.append("│" + " " * 36 + "│")
        output.append("│" + "[ Tap to dismiss ]".center(36) + "│")
        output.append("╰" + "─" * 36 + "╯")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bar_width = 30
        filled = int(bar_width * progress)
        bar = "━" * filled + "─" * (bar_width - filled)
        return f"│{bar}│"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;250;250;250m",
            "text": "\033[38;2;33;33;33m",
            "accent": "\033[38;2;76;175;80m",
            "reset": "\033[0m",
        }
