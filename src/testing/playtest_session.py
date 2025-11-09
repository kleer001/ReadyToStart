import json
import time
import uuid
from pathlib import Path
from typing import Any

from src.testing.playtest_metrics import (
    MenuVisit,
    PlaytestMetrics,
    SettingInteraction,
)


class PlaytestTracker:
    STUCK_THRESHOLD = 60.0

    def __init__(self, seed: int | None = None, session_id: str | None = None):
        self.metrics = PlaytestMetrics(
            session_id=session_id or str(uuid.uuid4()),
            seed=seed,
            start_time=time.time(),
        )
        self.current_menu: str | None = None
        self.menu_enter_time: float | None = None
        self.last_interaction_time: float = time.time()

    def record_setting_interaction(
        self, setting_id: str, action: str, value: Any = None, success: bool = True
    ) -> None:
        interaction = SettingInteraction(
            setting_id=setting_id,
            timestamp=time.time(),
            action=action,
            value=value,
            success=success,
        )
        self.metrics.setting_interactions.append(interaction)
        self.last_interaction_time = time.time()

    def record_menu_visit(self, menu_id: str) -> None:
        if self.current_menu and self.menu_enter_time:
            duration = time.time() - self.menu_enter_time
            visit = MenuVisit(
                menu_id=self.current_menu,
                timestamp=self.menu_enter_time,
                duration=duration,
            )
            self.metrics.menu_visits.append(visit)

        self.current_menu = menu_id
        self.menu_enter_time = time.time()
        self.last_interaction_time = time.time()

    def record_error(self, error: str) -> None:
        self.metrics.errors.append(error)

    def check_stuck(self) -> bool:
        idle_time = time.time() - self.last_interaction_time
        if idle_time > self.STUCK_THRESHOLD:
            self.metrics.stuck_events.append(
                {
                    "timestamp": time.time(),
                    "duration": idle_time,
                    "menu": self.current_menu,
                }
            )
            self.last_interaction_time = time.time()
            return True
        return False

    def complete_session(self, completed: bool = True) -> None:
        if self.current_menu and self.menu_enter_time:
            duration = time.time() - self.menu_enter_time
            visit = MenuVisit(
                menu_id=self.current_menu,
                timestamp=self.menu_enter_time,
                duration=duration,
            )
            self.metrics.menu_visits.append(visit)

        self.metrics.end_time = time.time()
        self.metrics.completed = completed

    def save(self, filepath: str | Path) -> None:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "session_id": self.metrics.session_id,
            "seed": self.metrics.seed,
            "start_time": self.metrics.start_time,
            "end_time": self.metrics.end_time,
            "completed": self.metrics.completed,
            "setting_interactions": [
                {
                    "setting_id": i.setting_id,
                    "timestamp": i.timestamp,
                    "action": i.action,
                    "value": i.value,
                    "success": i.success,
                }
                for i in self.metrics.setting_interactions
            ],
            "menu_visits": [
                {
                    "menu_id": v.menu_id,
                    "timestamp": v.timestamp,
                    "duration": v.duration,
                }
                for v in self.metrics.menu_visits
            ],
            "stuck_events": self.metrics.stuck_events,
            "errors": self.metrics.errors,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str | Path) -> "PlaytestTracker":
        with open(filepath) as f:
            data = json.load(f)

        tracker = cls(seed=data["seed"], session_id=data["session_id"])
        tracker.metrics.start_time = data["start_time"]
        tracker.metrics.end_time = data.get("end_time")
        tracker.metrics.completed = data.get("completed", False)

        for i_data in data.get("setting_interactions", []):
            tracker.metrics.setting_interactions.append(
                SettingInteraction(
                    setting_id=i_data["setting_id"],
                    timestamp=i_data["timestamp"],
                    action=i_data["action"],
                    value=i_data.get("value"),
                    success=i_data.get("success", True),
                )
            )

        for v_data in data.get("menu_visits", []):
            tracker.metrics.menu_visits.append(
                MenuVisit(
                    menu_id=v_data["menu_id"],
                    timestamp=v_data["timestamp"],
                    duration=v_data.get("duration", 0.0),
                )
            )

        tracker.metrics.stuck_events = data.get("stuck_events", [])
        tracker.metrics.errors = data.get("errors", [])

        return tracker

    def get_summary(self) -> str:
        m = self.metrics

        lines = [
            f"Playtest Session Summary",
            f"=" * 50,
            f"Session ID: {m.session_id}",
            f"Seed: {m.seed}",
            f"Duration: {m.duration:.1f}s",
            f"Completed: {m.completed}",
            f"",
            f"Interactions:",
            f"  Total: {m.total_interactions}",
            f"  Failed: {m.failed_interactions}",
            f"  Unique Settings: {m.unique_settings_touched}",
            f"  Unique Menus: {m.unique_menus_visited}",
            f"",
            f"Stuck Analysis:",
            f"  Events: {len(m.stuck_events)}",
            f"  Total Time: {m.total_stuck_time:.1f}s",
            f"  Avg Time: {m.avg_stuck_time:.1f}s",
        ]

        if m.errors:
            lines.append(f"\nErrors: {len(m.errors)}")
            for error in m.errors[:5]:
                lines.append(f"  - {error}")

        problem_settings = m.get_problem_settings()
        if problem_settings:
            lines.append(f"\nProblem Settings:")
            for setting_id, count in problem_settings[:5]:
                lines.append(f"  - {setting_id}: {count} failures")

        problem_menus = m.get_problem_menus()
        if problem_menus:
            lines.append(f"\nTime-Consuming Menus:")
            for menu_id, duration in problem_menus[:5]:
                lines.append(f"  - {menu_id}: {duration:.1f}s")

        return "\n".join(lines)
