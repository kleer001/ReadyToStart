from configparser import ConfigParser

from ready_to_start.core.enums import SettingState
from ready_to_start.core.menu import MenuNode
from ready_to_start.ui.indicators import StateIndicator
from ready_to_start.ui.renderer import Component, TextRenderer


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

    def render(self) -> str:
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
            for idx, setting in enumerate(visible_settings, 1):
                indicator = self.indicator.get_indicator(setting.state)
                state_label = f"({setting.state.value})"
                line = f" {idx}. {indicator} {setting.label} {state_label}"
                line = line[:width - 4]
                content_lines.append(line.ljust(width - 2))

        if self.menu.connections:
            content_lines.append("---")
            connection_names = ", ".join(self.menu.connections)
            available_text = f" Available Menus: {connection_names}"
            content_lines.append(available_text[:width - 2].ljust(width - 2))

        box_lines = self.renderer.render_box(content_lines, width, border_style)
        return "\n".join(box_lines)
