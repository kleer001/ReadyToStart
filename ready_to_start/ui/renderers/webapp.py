from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class WebAppRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("┌" + "─" * (self.width - 2) + "┐")
        header = f"Settings › {menu_node.category}"
        output.append("│ " + header[:self.width - 4].ljust(self.width - 4) + " │")
        output.append("├" + "─" * (self.width - 2) + "┤")
        tabs = "General | Advanced | Tools"
        output.append("│ " + tabs[:self.width - 4].ljust(self.width - 4) + " │")
        output.append("├" + "─" * (self.width - 2) + "┤")

        for setting in settings[:self.height - 9]:
            toggle = "[ON ]" if setting.state == SettingState.ENABLED else "[OFF]"
            label_width = self.width - 4 - 2 - len(toggle) - 1
            line = f"  {toggle} {setting.label[:label_width]}"
            output.append("│ " + line[:self.width - 4].ljust(self.width - 4) + " │")

        output.append("│" + " " * (self.width - 2) + "│")
        output.append("├" + "─" * (self.width - 2) + "┤")
        footer = "< Back" + "Save Changes >".rjust(self.width - 10)
        output.append("│ " + footer[:self.width - 4].ljust(self.width - 4) + " │")
        output.append("└" + "─" * (self.width - 2) + "┘")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("┌─────────────────────────────────┐")
        output.append("│ Configure Setting               │")
        output.append("├─────────────────────────────────┤")
        output.append("│ " + setting.label[:31].ljust(31) + " │")
        output.append("│                                 │")
        output.append("│ Value: " + str(setting.value)[:24].ljust(24) + " │")
        output.append("│                                 │")
        output.append("│  [Update]      [Cancel]         │")
        output.append("└─────────────────────────────────┘")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        indicator = "!" if message_type == "warning" else "i" if message_type == "info" else "×"
        output = []
        output.append("┌─────────────────────────────────┐")
        output.append("│ [" + indicator + "] " + message[:28].ljust(28) + " │")
        output.append("│                                 │")
        output.append("│         [Dismiss]               │")
        output.append("└─────────────────────────────────┘")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bar_width = 30
        filled = int(bar_width * progress)
        bar = "▓" * filled + "░" * (bar_width - filled)
        return f"Loading: [{bar}] {int(progress * 100)}%"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;255;255;255m",
            "text": "\033[38;2;51;51;51m",
            "accent": "\033[38;2;0;123;255m",
            "reset": "\033[0m",
        }
