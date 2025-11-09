#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.layer_manager import LayerManager
from src.core.menu import MenuNode
from src.core.types import Setting
from src.core.enums import SettingState, SettingType
from src.ui.renderer_factory import RendererFactory


def test_layer(layer_id: str):
    layer_mgr = LayerManager()
    layers_file = Path(__file__).parent.parent / "data" / "interface_layers.json"
    layer_mgr.load_layers(layers_file)

    layer = layer_mgr.layers.get(layer_id)
    if not layer:
        print(f"Unknown layer: {layer_id}")
        print("\nAvailable layers:")
        for lid in layer_mgr.layers.keys():
            print(f"  - {lid}")
        return

    sample_menu = MenuNode(
        id="test_menu",
        category=layer.name,
        settings=[],
        connections=[],
    )

    sample_settings = [
        Setting(
            id=f"setting_{i}",
            type=SettingType.BOOLEAN,
            value=True if i % 2 == 0 else False,
            state=SettingState.ENABLED if i % 2 == 0 else SettingState.DISABLED,
            label=f"Sample Setting {i}: {layer.features[i % len(layer.features)]}",
        )
        for i in range(min(10, len(layer.features) * 2))
    ]

    renderer = RendererFactory.create_renderer(layer)

    print("\n" + "=" * 80)
    print(f"Testing Layer: {layer.name} ({layer.era})")
    print(f"UI Paradigm: {layer.ui_paradigm}")
    print(f"Complexity: {layer.complexity}")
    print("=" * 80 + "\n")

    output = renderer.render_menu(sample_menu, sample_settings)
    print(output)

    print("\n" + "=" * 80)
    print("Setting Editor:")
    print("=" * 80 + "\n")

    editor_output = renderer.render_setting_editor(sample_settings[0])
    print(editor_output)

    print("\n" + "=" * 80)
    print("Message Dialog:")
    print("=" * 80 + "\n")

    message_output = renderer.render_message("This is a test message", "info")
    print(message_output)

    print("\n" + "=" * 80)
    print("Progress Indicator:")
    print("=" * 80 + "\n")

    progress_output = renderer.render_progress(0.75)
    print(progress_output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: test_layer.py <layer_id>")
        print("\nAvailable layers:")
        layer_mgr = LayerManager()
        layers_file = Path(__file__).parent.parent / "data" / "interface_layers.json"
        layer_mgr.load_layers(layers_file)
        for lid in layer_mgr.layers.keys():
            print(f"  - {lid}")
    else:
        test_layer(sys.argv[1])
