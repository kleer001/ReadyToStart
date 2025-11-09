#!/usr/bin/env python3

import json
from pathlib import Path


def visualize_progression():
    layers_file = Path(__file__).parent.parent / "data" / "interface_layers.json"

    with open(layers_file) as f:
        data = json.load(f)

    layers = {layer["id"]: layer for layer in data["layers"]}
    standard_path = data["progression_rules"]["standard_path"]

    print("=== STANDARD PROGRESSION PATH ===\n")

    for i, layer_id in enumerate(standard_path, 1):
        layer = layers.get(layer_id)
        if layer:
            print(f"{i:2d}. {layer['name']:40s} ({layer['era']})")
            if i < len(standard_path):
                print("    │")
                print("    ↓")

    print("\n=== ALTERNATE PATHS ===\n")

    alternate_paths = data["progression_rules"].get("alternate_paths", {})
    for path_name, path_layers in alternate_paths.items():
        print(f"\n{path_name}:")
        for layer_id in path_layers[:5]:
            if layer_id != "...":
                layer = layers.get(layer_id)
                if layer:
                    print(f"  → {layer['name']}")

    print("\n=== LAYER DETAILS ===\n")
    for layer in data["layers"]:
        print(f"\n{layer['name']} ({layer['id']})")
        print(f"  Era: {layer['era']}")
        print(f"  Complexity: {layer['complexity']}")
        print(f"  UI Paradigm: {layer['ui_paradigm']}")
        print(f"  Features: {', '.join(layer['features'])}")
        print(f"  Next options: {', '.join(layer['next_layer_options']) if layer['next_layer_options'] else 'FINAL'}")


if __name__ == "__main__":
    visualize_progression()
