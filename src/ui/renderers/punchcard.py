from src.core.enums import SettingState
from src.ui.renderers.base import EraRenderer


class PunchCardRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("=" * self.width)
        output.append("JOB CONTROL LANGUAGE - CONFIGURATION DECK".center(self.width))
        output.append("=" * self.width)
        output.append("")

        for i, setting in enumerate(settings[:self.height - 6], 1):
            seq = f"{i:08d}"
            enabled = "ENABLED" if setting.state == SettingState.ENABLED else "DISABLED"
            card_line = f"//SET{i:03d}  EXEC PGM={setting.label[:20]:20s} PARM='{enabled}'"
            card_line = f"{card_line[:72]:<72s}{seq}"
            output.append(card_line)

        output.append("")
        output.append("/*")
        output.append("// END OF CONFIGURATION DECK")
        output.append("=" * self.width)

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("=" * self.width)
        output.append(f"EDIT CARD: {setting.label}".center(self.width))
        output.append("=" * self.width)
        output.append("")
        output.append(f"// Column 1-8:   //SET{setting.id[:3]:3s}")
        output.append("// Column 9-16:  EXEC PGM=")
        output.append(f"// Column 17-72: {setting.label}")
        output.append(f"// Column 73-80: {1:08d}")
        output.append("")
        output.append("PUNCH NEW CARD? (Y/N): _")
        output.append("")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("=" * self.width)
        output.append("JOB CONTROL LANGUAGE - MESSAGE".center(self.width))
        output.append("=" * self.width)
        output.append("")
        output.append(message)
        output.append("")
        output.append("PRESS ENTER TO CONTINUE")
        output.append("=" * self.width)
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        cards_total = 80
        cards_processed = int(cards_total * progress)
        return f"CARDS PROCESSED: {cards_processed:03d}/{cards_total:03d}"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[47m",
            "text": "\033[30m",
            "reset": "\033[0m",
        }
