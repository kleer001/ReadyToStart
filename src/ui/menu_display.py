from configparser import ConfigParser

from src.core.enums import SettingState
from src.core.menu import MenuNode
from src.ui.indicators import StateIndicator
from src.ui.renderer import Component, TextRenderer, pad_ansi


class MenuDisplay(Component):
    def __init__(
        self,
        menu: MenuNode,
        renderer: TextRenderer,
        indicator: StateIndicator,
        ui_config_path: str,
    ):
        self.menu = menu
        self.renderer = renderer
        self.indicator = indicator
        self.config = ConfigParser()
        self.config.read(ui_config_path)

    def render(self, selected_index: int = -1) -> str:
        width = int(self.config.get("display", "width", fallback="80"))
        padding = int(self.config.get("display", "padding", fallback="2"))
        border_style = self.config.get("display", "border_style", fallback="double")

        content_lines = []

        title = f" {self.menu.category.upper()} "
        content_lines.append(title.center(width - 2))
        content_lines.append("---")

        visible_settings = [s for s in self.menu.settings if s.state != SettingState.HIDDEN]

        if not visible_settings:
            content_lines.append(" No settings available ".center(width - 2))
        else:
            for idx, setting in enumerate(visible_settings):
                indicator = self.indicator.get_indicator(setting.state)

                # Format value display based on type
                type_abbrev = {
                    'bool': 'bool',
                    'int': 'int',
                    'float': 'float',
                    'string': 'str'
                }.get(setting.type.value, setting.type.value)

                value_str = str(setting.value)
                if len(value_str) > 20:
                    value_str = value_str[:17] + "..."

                state_label = f"[{setting.state.value}]"
                cursor = ">" if idx == selected_index else " "
                line = f"{cursor}{idx + 1}. {indicator} {setting.label}: {value_str} ({type_abbrev}) {state_label}"
                line = line[:width - 4]

                if idx == selected_index:
                    line = self.renderer.colorize(pad_ansi(line, width - 2), "cyan", bold=True)
                else:
                    line = pad_ansi(line, width - 2)

                content_lines.append(line)

        if self.menu.connections:
            content_lines.append("---")
            connection_names = ", ".join(self.menu.connections)
            available_text = f" Available Menus: {connection_names}"
            content_lines.append(pad_ansi(available_text[:width - 2], width - 2))

        box_lines = self.renderer.render_box(content_lines, width, border_style)
        return "\n".join(box_lines)
