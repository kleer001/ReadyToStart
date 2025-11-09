from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LayerGameState:
    layer_id: str
    settings_enabled: int = 0
    settings_total: int = 0
    time_spent: float = 0.0
    actions_taken: int = 0
    errors_encountered: int = 0
    hints_viewed: int = 0
    secrets_found: list[str] = field(default_factory=list)
    completed: bool = False
    completion_type: str = "none"


class LayerStateManager:
    def __init__(self):
        self.layer_states: dict[str, LayerGameState] = {}
        self.current_layer_id: Optional[str] = None

    def create_layer_state(self, layer_id: str, settings_count: int):
        state = LayerGameState(layer_id=layer_id, settings_total=settings_count)
        self.layer_states[layer_id] = state
        return state

    def get_current_state(self) -> Optional[LayerGameState]:
        if self.current_layer_id:
            return self.layer_states.get(self.current_layer_id)
        return None

    def mark_layer_complete(self, layer_id: str, completion_type: str = "full"):
        if layer_id in self.layer_states:
            state = self.layer_states[layer_id]
            state.completed = True
            state.completion_type = completion_type

    def get_completion_metrics(self) -> dict:
        total_layers = len(self.layer_states)
        completed_layers = sum(1 for s in self.layer_states.values() if s.completed)

        total_time = sum(s.time_spent for s in self.layer_states.values())
        total_actions = sum(s.actions_taken for s in self.layer_states.values())
        total_errors = sum(s.errors_encountered for s in self.layer_states.values())

        all_secrets = []
        for state in self.layer_states.values():
            all_secrets.extend(state.secrets_found)

        return {
            "layers_completed": completed_layers,
            "layers_total": total_layers,
            "total_time": total_time,
            "total_actions": total_actions,
            "total_errors": total_errors,
            "secrets_found": len(set(all_secrets)),
            "efficiency": self._calculate_efficiency(),
        }

    def _calculate_efficiency(self) -> float:
        total_actions = sum(s.actions_taken for s in self.layer_states.values())
        total_errors = sum(s.errors_encountered for s in self.layer_states.values())

        if total_actions == 0:
            return 0.0

        error_rate = total_errors / total_actions
        efficiency = max(0, 100 - (error_rate * 100))

        return efficiency

    def serialize(self) -> dict:
        return {
            "current_layer": self.current_layer_id,
            "layer_states": {
                lid: {
                    "layer_id": state.layer_id,
                    "settings_enabled": state.settings_enabled,
                    "settings_total": state.settings_total,
                    "time_spent": state.time_spent,
                    "actions_taken": state.actions_taken,
                    "errors_encountered": state.errors_encountered,
                    "hints_viewed": state.hints_viewed,
                    "secrets_found": state.secrets_found,
                    "completed": state.completed,
                    "completion_type": state.completion_type,
                }
                for lid, state in self.layer_states.items()
            },
            "metrics": self.get_completion_metrics(),
        }
