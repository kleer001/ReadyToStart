from src.core.enums import SettingState
from src.ui.renderers.base import EraRenderer


class TerminalRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append(f"TERMINAL CONFIGURATION - {menu_node.category.upper()}")
        output.append("=" * self.width)
        output.append("")

        for i, setting in enumerate(settings[:self.height - 6], 1):
            status = "ON " if setting.state == SettingState.ENABLED else "OFF"
            line = f"{i:2d}. [{status}] {setting.label}"
            output.append(line[:self.width])

        output.append("")
        output.append("ENTER NUMBER TO TOGGLE, Q TO QUIT")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append(f"EDIT: {setting.label}")
        output.append("-" * self.width)
        output.append(f"CURRENT VALUE: {setting.value}")
        output.append("NEW VALUE: _")
        output.append("")
        output.append("PRESS ENTER TO CONFIRM")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append("")
        output.append(message.upper())
        output.append("")
        output.append("PRESS ANY KEY TO CONTINUE")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        filled = int(50 * progress)
        return "#" * filled

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[40m",
            "text": "\033[33m",
            "reset": "\033[0m",
        }
