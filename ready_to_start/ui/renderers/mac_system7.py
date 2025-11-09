from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class MacSystem7Renderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("┏" + "━" * (self.width - 2) + "┓")
        output.append("┃ " + menu_node.category[:self.width - 4].ljust(self.width - 4) + " ┃")
        output.append("┣" + "━" * (self.width - 2) + "┫")

        for setting in settings[:self.height - 6]:
            checkbox = "☑" if setting.state == SettingState.ENABLED else "☐"
            line = f" {checkbox} {setting.label[:self.width - 8]}"
            output.append("┃" + line.ljust(self.width - 2) + "┃")

        output.append("┣" + "━" * (self.width - 2) + "┫")
        output.append("┃    Cancel           OK             ┃")
        output.append("┗" + "━" * (self.width - 2) + "┛")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        output.append("┃ Control Panel                     ┃")
        output.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
        output.append("┃ " + setting.label[:33].ljust(33) + " ┃")
        output.append("┃ Value: " + str(setting.value)[:26].ljust(26) + " ┃")
        output.append("┃                                   ┃")
        output.append("┃     Cancel           OK           ┃")
        output.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        bomb = "💣" if message_type == "error" else ""
        output = []
        output.append("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        output.append("┃ System 7                          ┃")
        output.append("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
        output.append("┃ " + bomb + " " + message[:30].ljust(30) + " ┃")
        output.append("┃                                   ┃")
        output.append("┃             OK                    ┃")
        output.append("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        filled = int(24 * progress)
        bar = "▪" * filled + "▫" * (24 - filled)
        return f"[{bar}]"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[47m",
            "text": "\033[30m",
            "reset": "\033[0m",
        }
