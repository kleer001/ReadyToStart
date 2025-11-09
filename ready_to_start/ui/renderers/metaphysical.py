from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class MetaphysicalRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("∴" + "·" * (self.width - 2) + "∵")
        output.append("  " + menu_node.category.upper().center(self.width - 4) + "  ")
        output.append("∵" + "·" * (self.width - 2) + "∴")
        output.append("")

        for setting in settings[:self.height - 8]:
            essence = "⊕" if setting.state == SettingState.ENABLED else "⊖"
            line = f"  {essence} {setting.label[:60]}"
            output.append(line[:self.width])

        output.append("")
        output.append("  ∴ CONTEMPLATE THE ESSENCE ∵")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("     ∴═══════════════════════∵")
        output.append("     │ ESSENCE MODIFICATION  │")
        output.append("     ∵═══════════════════════∴")
        output.append("")
        output.append(f"     Platonic Form: {setting.label}")
        output.append(f"     Current State: {setting.value}")
        output.append("")
        output.append("     Reality Parameters:")
        output.append("     [ Being ] [ Non-Being ] [ Both ] [ Neither ]")
        output.append("")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("")
        output.append("     ∴═══════════════════════════════∵")
        output.append("     │ " + message[:27].center(27) + " │")
        output.append("     ∵═══════════════════════════════∴")
        output.append("")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        filled = int(30 * progress)
        bar = "∴" * filled + "·" * (30 - filled)
        return f"Transcendence: {bar}"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;0;0;0m",
            "text": "\033[38;2;200;200;200m",
            "void": "\033[38;2;50;50;50m",
            "reset": "\033[0m",
        }
