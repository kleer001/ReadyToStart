from ready_to_start.ui.renderers.base import EraRenderer


class FinalRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("")
        output.append("")
        output.append("")
        output.append("")
        output.append("")
        output.append("")
        output.append("")
        output.append("                              .")
        output.append("")
        output.append("")
        output.append("")
        output.append("")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("")
        output.append("")
        output.append("")
        output.append("                         You're done.")
        output.append("")
        output.append("")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("")
        output.append("")
        output.append("                         " + message[:30])
        output.append("")
        output.append("")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        if progress >= 1.0:
            return "Complete."
        else:
            return "..."

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;0;0;0m",
            "text": "\033[38;2;100;100;100m",
            "reset": "\033[0m",
        }
