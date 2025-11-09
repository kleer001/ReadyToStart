from src.core.layer_manager import InterfaceLayer
from src.ui.renderers import (
    BIOSRenderer,
    DOSRenderer,
    DesktopGUIRenderer,
    FinalRenderer,
    MacOS9Renderer,
    MacSystem7Renderer,
    MetaphysicalRenderer,
    MobileRenderer,
    ModernRenderer,
    PunchCardRenderer,
    QuantumRenderer,
    RecursiveMetaRenderer,
    SwitchPanelRenderer,
    TerminalRenderer,
    UnixConfigRenderer,
    WebAppRenderer,
    Win95Renderer,
)
from src.ui.renderers.base import EraRenderer


class RendererFactory:
    RENDERER_MAP = {
        "flat_design": ModernRenderer,
        "web_2_0": WebAppRenderer,
        "mobile_first": MobileRenderer,
        "traditional_gui": DesktopGUIRenderer,
        "win95": Win95Renderer,
        "classic_mac": MacOS9Renderer,
        "classic_mac_early": MacSystem7Renderer,
        "text_menu": DOSRenderer,
        "firmware": BIOSRenderer,
        "text_files": UnixConfigRenderer,
        "teletype": TerminalRenderer,
        "batch_processing": PunchCardRenderer,
        "hardware_direct": SwitchPanelRenderer,
        "quantum_superposition": QuantumRenderer,
        "abstract_concepts": MetaphysicalRenderer,
        "self_reference": RecursiveMetaRenderer,
        "revelation": FinalRenderer,
    }

    @classmethod
    def create_renderer(cls, layer: InterfaceLayer) -> EraRenderer:
        renderer_class = cls.RENDERER_MAP.get(layer.ui_paradigm)

        if not renderer_class:
            renderer_class = DOSRenderer

        return renderer_class(layer.__dict__)
