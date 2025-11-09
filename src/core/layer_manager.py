from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json


@dataclass
class InterfaceLayer:
    id: str
    name: str
    era: str
    complexity: int
    ui_paradigm: str
    features: list[str]
    color_scheme: str
    next_layer_options: list[str]


class LayerManager:
    def __init__(self):
        self.layers: dict[str, InterfaceLayer] = {}
        self.current_layer_id: Optional[str] = None
        self.layer_history: list[str] = []
        self.progression_rules: dict = {}

    def load_layers(self, layers_file: str | Path):
        with open(layers_file) as f:
            data = json.load(f)

        for layer_data in data["layers"]:
            layer = InterfaceLayer(**layer_data)
            self.layers[layer.id] = layer

        self.progression_rules = data.get("progression_rules", {})

    def start_at_layer(self, layer_id: str):
        if layer_id not in self.layers:
            raise ValueError(f"Unknown layer: {layer_id}")

        self.current_layer_id = layer_id
        self.layer_history = [layer_id]

    def get_current_layer(self) -> Optional[InterfaceLayer]:
        if self.current_layer_id:
            return self.layers.get(self.current_layer_id)
        return None

    def get_next_layer_options(self, game_metrics: dict) -> list[str]:
        current = self.get_current_layer()
        if not current:
            return []

        branching_points = self.progression_rules.get("branching_points", {})
        if current.id in branching_points:
            branching = branching_points[current.id]
            conditions = branching["conditions"]

            if game_metrics.get("secrets_found", 0) > 0 and "found_secret" in conditions:
                return [conditions["found_secret"]]
            elif game_metrics.get("time_spent", 0) > 600 and "took_too_long" in conditions:
                return [conditions["took_too_long"]]
            elif game_metrics.get("efficiency", 0) > 75 and "efficiency_high" in conditions:
                return [conditions["efficiency_high"]]
            elif game_metrics.get("efficiency", 0) < 25 and "efficiency_low" in conditions:
                return [conditions["efficiency_low"]]

        return current.next_layer_options

    def transition_to_layer(self, layer_id: str) -> bool:
        if layer_id not in self.layers:
            return False

        current = self.get_current_layer()
        if current and layer_id not in current.next_layer_options:
            return False

        self.current_layer_id = layer_id
        self.layer_history.append(layer_id)
        return True

    def get_layer_depth(self) -> int:
        return len(self.layer_history)

    def is_final_layer(self) -> bool:
        current = self.get_current_layer()
        return current and len(current.next_layer_options) == 0

    def get_standard_path(self) -> list[str]:
        return self.progression_rules.get("standard_path", [])

    def get_alternate_paths(self) -> dict[str, list[str]]:
        return self.progression_rules.get("alternate_paths", {})
