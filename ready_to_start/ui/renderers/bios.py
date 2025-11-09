from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class BIOSRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("\033[44;37m")

        top_bar = " PhoenixBIOS Setup Utility "
        output.append(top_bar.ljust(self.width))
        output.append("─" * self.width)

        categories = "Main  Advanced  Security  Boot  Exit"
        output.append(categories.ljust(self.width))
        output.append("─" * self.width)

        for setting in settings[:self.height - 8]:
            value_str = str(setting.value) if setting.state == SettingState.ENABLED else "[Disabled]"
            line = f"  {setting.label[:40]:40s} [{value_str[:15]:>15s}]"
            output.append(line.ljust(self.width))

        remaining = self.height - len(output) - 4
        for _ in range(max(0, remaining)):
            output.append(" " * self.width)

        output.append("─" * self.width)
        output.append(" ←→:Navigate  ↑↓:Select  Enter:Change  F10:Save  ESC:Exit".ljust(self.width))
        output.append("\033[0m")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []

        output.append("\033[44;37m")
        output.append("╔" + "═" * (self.width - 2) + "╗")
        output.append("║ " + f"Change Setting: {setting.label}"[:self.width - 4].ljust(self.width - 4) + " ║")
        output.append("╠" + "═" * (self.width - 2) + "╣")
        output.append("║" + " " * (self.width - 2) + "║")
        output.append("║ Current: " + str(setting.value)[:self.width - 12].ljust(self.width - 12) + " ║")
        output.append("║" + " " * (self.width - 2) + "║")
        output.append("╚" + "═" * (self.width - 2) + "╝")
        output.append("\033[0m")

        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []

        output.append("\033[44;37m")
        output.append("╔" + "═" * 38 + "╗")
        output.append("║ WARNING: " + message[:28].ljust(28) + " ║")
        output.append("║" + " " * 38 + "║")
        output.append("║  Press any key to continue...      ║")
        output.append("╚" + "═" * 38 + "╝")
        output.append("\033[0m")

        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        percentage = int(progress * 100)
        return f"Loading... {percentage}%"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[44m",
            "text": "\033[37m",
            "selected": "\033[47;30m",
            "reset": "\033[0m",
        }
