from abc import ABC, abstractmethod


class EraRenderer(ABC):
    def __init__(self, layer_info: dict):
        self.layer_info = layer_info
        self.width = 80
        self.height = 24

    @abstractmethod
    def render_menu(self, menu_node, settings: list) -> str:
        pass

    @abstractmethod
    def render_setting_editor(self, setting) -> str:
        pass

    @abstractmethod
    def render_message(self, message: str, message_type: str) -> str:
        pass

    @abstractmethod
    def render_progress(self, progress: float) -> str:
        pass

    @abstractmethod
    def get_color_scheme(self) -> dict:
        pass
