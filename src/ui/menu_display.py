from configparser import ConfigParser

from src.core.enums import SettingState
from src.core.menu import MenuNode
from src.ui.indicators import StateIndicator
from src.ui.renderer import Component, TextRenderer


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

    def render(self, window=None, selected_index: int = -1, start_y: int = 0, start_x: int = 0):
        """
        Render the menu to the ncurses window.
        Returns the number of lines rendered.
        """
        width = int(self.config.get("display", "width", fallback="80"))
        height = 40  # Max height for the box
        border_style = self.config.get("display", "border_style", fallback="double")

        # Build content as list of (text, color, bold) tuples
        content = []

        # Title
        title = f" {self.menu.category.upper()} "
        content.append((title.center(width - 2), "", False))
        content.append("---")

        visible_settings = [s for s in self.menu.settings if s.state != SettingState.HIDDEN]

        if not visible_settings:
            content.append((" No settings available ".center(width - 2), "", False))
        else:
            for idx, setting in enumerate(visible_settings):
                indicator_symbol = self.indicator.get_indicator(setting.state)

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
                line = f"{cursor}{idx + 1}. {indicator_symbol} {setting.label}: {value_str} ({type_abbrev}) {state_label}"
                line = line[:width - 2]

                if idx == selected_index:
                    content.append((line, "cyan", True))
                else:
                    content.append((line, "", False))

        if self.menu.connections:
            content.append("---")
            connection_names = ", ".join(self.menu.connections)
            available_text = f" Available Menus: {connection_names}"
            content.append((available_text[:width - 2], "", False))

        # Render the box with colored content
        lines_rendered = self.renderer.render_box_with_colors(
            start_y, start_x, height, width, content, border_style
        )

        return lines_rendered
