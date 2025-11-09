from ready_to_start.core.enums import SettingState
from ready_to_start.ui.renderers.base import EraRenderer


class RecursiveMetaRenderer(EraRenderer):
    def render_menu(self, menu_node, settings: list) -> str:
        output = []

        output.append("Settings{")
        output.append("  Settings{")
        output.append(f"    category: \"{menu_node.category}\",")
        output.append("    settings: [")

        for setting in settings[:self.height - 10]:
            state_str = "enabled" if setting.state == SettingState.ENABLED else "disabled"
            line = f"      Setting{{ label: \"{setting.label}\", state: {state_str} }},"
            output.append(line[:self.width])

        output.append("    ]")
        output.append("  }")
        output.append("}")
        output.append("")
        output.append("// Configure the configuration")

        return "\n".join(output)

    def render_setting_editor(self, setting) -> str:
        output = []
        output.append("SettingEditor{")
        output.append("  Setting{")
        output.append(f"    label: \"{setting.label}\",")
        output.append(f"    value: {setting.value},")
        output.append("    editor: SettingEditor{")
        output.append("      Setting{")
        output.append("        editor: ...")
        output.append("      }")
        output.append("    }")
        output.append("  }")
        output.append("}")
        return "\n".join(output)

    def render_message(self, message: str, message_type: str) -> str:
        output = []
        output.append("Message{")
        output.append("  Message{")
        output.append(f"    text: \"{message}\",")
        output.append("    type: Message{")
        output.append(f"      text: \"A message about: '{message}'\",")
        output.append("      type: ...")
        output.append("    }")
        output.append("  }")
        output.append("}")
        return "\n".join(output)

    def render_progress(self, progress: float) -> str:
        depth = int(progress * 10)
        indent = "  " * depth
        return f"{indent}Progress{{ progress: {progress:.2f} }}"

    def get_color_scheme(self) -> dict:
        return {
            "background": "\033[48;2;30;30;30m",
            "text": "\033[38;2;150;150;150m",
            "keyword": "\033[38;2;200;100;200m",
            "reset": "\033[0m",
        }
