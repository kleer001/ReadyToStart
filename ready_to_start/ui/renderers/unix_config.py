from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class UnixConfigRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append(f"# {menu_node.category} configuration")
        output.append("# Edit with vi - :wq to save, :q! to quit")
        output.append("")

        for setting in settings[:self.height - 6]:
            if setting.state == SettingState.ENABLED:
                line = f"{setting.id}={setting.value}"
            else:
                line = f"# {setting.id}={setting.value}  # disabled"
            output.append(line[:self.width])

        output.append("")
        output.append("~")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append("-- INSERT --")
        output.append("")
        output.append(f"{setting.id}={setting.value}_")
        output.append("")
        output.append("~")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        colors = self.get_color_scheme()
        output = []

        output.append(colors["background"] + colors["text"])
        output.append("")
        output.append(f"# {message}")
        output.append("")
        output.append("Press ENTER to continue...")
        output.append(colors["reset"])

        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        dots = int(40 * progress)
        return "." * dots

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[40m",
            "text": "\033[32m",
            "reset": "\033[0m",
        }
