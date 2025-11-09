from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class Win95Renderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        title = f" {menu_node.category} "
        output.append("┌" + "─" * (self.width - 2) + "┐")
        output.append("│" + title.ljust(self.width - 4) + " [X]│")
        output.append("├" + "─" * (self.width - 2) + "┤")

        output.append("│ General | Advanced | About │" + " " * (self.width - 35) + "│")
        output.append("├" + "─" * (self.width - 2) + "┤")

        for setting in settings[:self.height - 8]:
            checkbox = "[X]" if setting.state == SettingState.ENABLED else "[ ]"
            label = f" {checkbox} {setting.label}"
            output.append("│" + label.ljust(self.width - 2) + "│")

        output.append("├" + "─" * (self.width - 2) + "┤")

        buttons = " [ OK ] [ Cancel ] [ Apply ] "
        output.append("│" + buttons.center(self.width - 2) + "│")
        output.append("└" + "─" * (self.width - 2) + "┘")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("┌─────────────────────────────────┐")
        output.append("│ " + setting.label[:29].ljust(30) + " [X]│")
        output.append("├─────────────────────────────────┤")
        output.append("│                                 │")
        output.append("│ Current value:                  │")
        output.append("│ " + f"[ {str(setting.value):^27s} ]" + " │")
        output.append("│                                 │")
        output.append("├─────────────────────────────────┤")
        output.append("│     [ OK ]      [ Cancel ]      │")
        output.append("└─────────────────────────────────┘")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        icon = "⚠" if message_type == "warning" else "ⓘ" if message_type == "info" else "✖"
        output = []
        output.append("┌─────────────────────────────────┐")
        output.append("│ Windows                      [X]│")
        output.append("├─────────────────────────────────┤")
        output.append("│                                 │")
        output.append("│  " + icon + "  " + message[:26].ljust(26) + " │")
        output.append("│                                 │")
        output.append("├─────────────────────────────────┤")
        output.append("│           [ OK ]                │")
        output.append("└─────────────────────────────────┘")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        bar_width = 30
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        return f"[{bar}] {int(progress * 100)}%"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[47m",
            "text": "\033[30m",
            "title_bar": "\033[44m",
            "button": "\033[47;30m",
            "reset": "\033[0m",
        }
