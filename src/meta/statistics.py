import json
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import Any


@dataclass
class GameStatistics:
    total_play_time: float = 0.0
    time_per_layer: dict[str, float] = field(default_factory=dict)
    session_start_time: float = field(default_factory=time)
    total_actions: int = 0
    settings_viewed: int = 0
    settings_enabled: int = 0
    settings_disabled: int = 0
    menus_visited: int = 0
    navigations: int = 0
    total_errors: int = 0
    locked_attempts: int = 0
    invalid_values: int = 0
    dependency_failures: int = 0
    layers_completed: int = 0
    current_layer_depth: int = 0
    deepest_layer_reached: int = 0
    perfect_layers: int = 0
    average_efficiency: float = 0.0
    best_efficiency: float = 0.0
    worst_efficiency: float = 100.0
    glitches_encountered: int = 0
    fake_errors_shown: int = 0
    fourth_wall_breaks: int = 0
    meta_comments: int = 0
    help_views: int = 0
    hints_viewed: int = 0
    secrets_found: list[str] = field(default_factory=list)
    quit_attempts: int = 0

    def get_total_time(self) -> float:
        return self.total_play_time + (time() - self.session_start_time)

    def get_summary(self) -> dict[str, Any]:
        return {
            "Total Time": f"{self.get_total_time():.1f}s",
            "Actions Taken": self.total_actions,
            "Settings Enabled": self.settings_enabled,
            "Errors Made": self.total_errors,
            "Layers Completed": self.layers_completed,
            "Deepest Layer": self.deepest_layer_reached,
            "Efficiency (Avg)": f"{self.average_efficiency:.1f}%",
            "Secrets Found": len(self.secrets_found),
            "Quit Attempts": self.quit_attempts,
        }

    def serialize(self) -> dict[str, Any]:
        return {
            "total_play_time": self.get_total_time(),
            "time_per_layer": self.time_per_layer,
            "total_actions": self.total_actions,
            "settings_viewed": self.settings_viewed,
            "settings_enabled": self.settings_enabled,
            "settings_disabled": self.settings_disabled,
            "menus_visited": self.menus_visited,
            "navigations": self.navigations,
            "total_errors": self.total_errors,
            "locked_attempts": self.locked_attempts,
            "invalid_values": self.invalid_values,
            "dependency_failures": self.dependency_failures,
            "layers_completed": self.layers_completed,
            "current_layer_depth": self.current_layer_depth,
            "deepest_layer_reached": self.deepest_layer_reached,
            "perfect_layers": self.perfect_layers,
            "average_efficiency": self.average_efficiency,
            "best_efficiency": self.best_efficiency,
            "worst_efficiency": self.worst_efficiency,
            "glitches_encountered": self.glitches_encountered,
            "fake_errors_shown": self.fake_errors_shown,
            "fourth_wall_breaks": self.fourth_wall_breaks,
            "meta_comments": self.meta_comments,
            "help_views": self.help_views,
            "hints_viewed": self.hints_viewed,
            "secrets_found": self.secrets_found,
            "quit_attempts": self.quit_attempts,
        }


class StatisticsTracker:
    def __init__(self):
        self.stats = GameStatistics()
        self._action_handlers = self._build_action_handlers()

    def _build_action_handlers(self) -> dict[str, callable]:
        return {
            "setting_viewed": lambda: self._increment("settings_viewed"),
            "setting_enabled": lambda: self._increment("settings_enabled"),
            "setting_disabled": lambda: self._increment("settings_disabled"),
            "menu_visited": lambda: self._increment("menus_visited"),
            "navigation": lambda: self._increment("navigations"),
            "error_locked": lambda: self._record_error("locked_attempts"),
            "error_invalid_value": lambda: self._record_error("invalid_values"),
            "error_dependency": lambda: self._record_error("dependency_failures"),
            "glitch": lambda: self._increment("glitches_encountered"),
            "fake_error": lambda: self._increment("fake_errors_shown"),
            "fourth_wall_break": lambda: self._increment("fourth_wall_breaks"),
            "meta_comment": lambda: self._increment("meta_comments"),
            "help_view": lambda: self._increment("help_views"),
            "hint_view": lambda: self._increment("hints_viewed"),
            "quit_attempt": lambda: self._increment("quit_attempts"),
        }

    def _increment(self, field: str):
        setattr(self.stats, field, getattr(self.stats, field) + 1)

    def _record_error(self, error_type: str):
        self.stats.total_errors += 1
        self._increment(error_type)

    def record_action(self, action_type: str, details: dict | None = None):
        self.stats.total_actions += 1
        handler = self._action_handlers.get(action_type)
        if handler:
            handler()

    def record_layer_completion(self, layer_id: str, layer_stats: dict):
        self.stats.layers_completed += 1
        self.stats.time_per_layer[layer_id] = layer_stats.get("time_spent", 0)

        efficiency = layer_stats.get("efficiency", 0)
        self._update_efficiency_tracking(efficiency)

        if layer_stats.get("errors", 0) == 0:
            self.stats.perfect_layers += 1

    def _update_efficiency_tracking(self, efficiency: float):
        self.stats.best_efficiency = max(self.stats.best_efficiency, efficiency)
        self.stats.worst_efficiency = min(self.stats.worst_efficiency, efficiency)

        total_layers = len(self.stats.time_per_layer)
        if total_layers > 0:
            current_total = self.stats.average_efficiency * (total_layers - 1)
            self.stats.average_efficiency = (current_total + efficiency) / total_layers

    def record_secret_found(self, secret_id: str):
        if secret_id not in self.stats.secrets_found:
            self.stats.secrets_found.append(secret_id)

    def update_layer_depth(self, depth: int):
        self.stats.current_layer_depth = depth
        self.stats.deepest_layer_reached = max(self.stats.deepest_layer_reached, depth)

    def save_to_file(self, filepath: str | Path):
        with open(filepath, "w") as f:
            json.dump(self.stats.serialize(), f, indent=2)

    def load_from_file(self, filepath: str | Path):
        with open(filepath) as f:
            data = json.load(f)

        for key, value in data.items():
            if hasattr(self.stats, key):
                setattr(self.stats, key, value)

        self.stats.session_start_time = time()
