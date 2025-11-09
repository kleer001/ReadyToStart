import json
import time
from dataclasses import dataclass, field

from src.core.game_state import GameState


@dataclass
class SessionMetrics:
    start_time: float = field(default_factory=time.time)
    settings_viewed: int = 0
    settings_modified: int = 0
    menus_visited: int = 0
    clicks: int = 0
    hovers: int = 0
    total_time: float = 0.0
    progress_percentage: float = 0.0

    def to_dict(self) -> dict:
        return {
            "duration": time.time() - self.start_time,
            "settings_viewed": self.settings_viewed,
            "settings_modified": self.settings_modified,
            "menus_visited": self.menus_visited,
            "clicks": self.clicks,
            "hovers": self.hovers,
            "progress": self.progress_percentage,
        }


class SessionManager:
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.metrics = SessionMetrics()
        self.events: list[dict] = []

    def record_event(self, event_type: str, data: dict | None = None) -> None:
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data or {},
        }
        self.events.append(event)
        self._update_metrics(event_type)

    def update_progress(self, progress: float) -> None:
        self.metrics.progress_percentage = progress

    def get_efficiency_score(self) -> float:
        if self.metrics.settings_modified == 0:
            return 0.0

        base = (
            self.metrics.settings_modified / max(1, self.metrics.settings_viewed)
        ) * 100

        time_penalty = min(50, (time.time() - self.metrics.start_time) / 60)
        click_penalty = min(30, self.metrics.clicks / 10)

        return max(1.0, base - time_penalty - click_penalty)

    def serialize(self) -> dict:
        return {
            "metrics": self.metrics.to_dict(),
            "efficiency": self.get_efficiency_score(),
            "events": self.events[-100:],
        }

    def save_to_file(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            json.dump(self.serialize(), f, indent=2)

    def _update_metrics(self, event_type: str) -> None:
        metric_map = {
            "setting_viewed": lambda: setattr(
                self.metrics, "settings_viewed", self.metrics.settings_viewed + 1
            ),
            "setting_modified": lambda: setattr(
                self.metrics, "settings_modified", self.metrics.settings_modified + 1
            ),
            "menu_visited": lambda: setattr(
                self.metrics, "menus_visited", self.metrics.menus_visited + 1
            ),
            "click": lambda: setattr(self.metrics, "clicks", self.metrics.clicks + 1),
            "hover": lambda: setattr(self.metrics, "hovers", self.metrics.hovers + 1),
        }

        handler = metric_map.get(event_type)
        if handler:
            handler()
