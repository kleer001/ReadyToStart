from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class DOSRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])

        title = f" {menu_node.category} Configuration "
        output.append("═" * self.width)
        output.append(title.center(self.width))
        output.append("═" * self.width)
        output.append("")

        for i, setting in enumerate(settings[:self.height - 8], 1):
            status = "+" if setting.state == SettingState.ENABLED else "-"
            marker = "►" if i == 1 else " "
            line = f" {marker} [{status}] {setting.label}"
            output.append(line.ljust(self.width))

        output.append("")
        output.append("─" * self.width)
        output.append(" ↑↓: Navigate  ENTER: Select  ESC: Exit ".center(self.width))
        output.append(colors["reset"])

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append("╔" + "═" * (self.width - 2) + "╗")
        output.append("║ " + f"Edit: {setting.label}"[:self.width - 4].ljust(self.width - 4) + " ║")
        output.append("╠" + "═" * (self.width - 2) + "╣")
        output.append("║" + " " * (self.width - 2) + "║")
        output.append("║ Current: " + str(setting.value)[:self.width - 12].ljust(self.width - 12) + " ║")
        output.append("║ New:     " + "_" * 20 + " " * (self.width - 32) + " ║")
        output.append("║" + " " * (self.width - 2) + "║")
        output.append("╚" + "═" * (self.width - 2) + "╝")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append("╔" + "═" * (self.width - 2) + "╗")
        output.append("║ " + message[:self.width - 4].ljust(self.width - 4) + " ║")
        output.append("╚" + "═" * (self.width - 2) + "╝")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bar_width = 40
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        return f"[{bar}]"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[44m",
            "text": "\033[37m",
            "highlight": "\033[47;30m",
            "reset": "\033[0m",
        }
