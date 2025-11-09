from dataclasses import dataclass, field
from typing import Any


@dataclass
class SettingInteraction:
    setting_id: str
    timestamp: float
    action: str
    value: Any = None
    success: bool = True


@dataclass
class MenuVisit:
    menu_id: str
    timestamp: float
    duration: float = 0.0


@dataclass
class PlaytestMetrics:
    session_id: str
    seed: int | None
    start_time: float
    end_time: float | None = None
    completed: bool = False
    setting_interactions: list[SettingInteraction] = field(default_factory=list)
    menu_visits: list[MenuVisit] = field(default_factory=list)
    stuck_events: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    @property
    def total_interactions(self) -> int:
        return len(self.setting_interactions)

    @property
    def failed_interactions(self) -> int:
        return sum(1 for i in self.setting_interactions if not i.success)

    @property
    def unique_settings_touched(self) -> int:
        return len(set(i.setting_id for i in self.setting_interactions))

    @property
    def unique_menus_visited(self) -> int:
        return len(set(v.menu_id for v in self.menu_visits))

    @property
    def total_stuck_time(self) -> float:
        return sum(event.get("duration", 0.0) for event in self.stuck_events)

    @property
    def avg_stuck_time(self) -> float:
        count = len(self.stuck_events)
        return self.total_stuck_time / count if count > 0 else 0.0

    def get_problem_settings(self) -> list[tuple[str, int]]:
        failed_counts = {}
        for interaction in self.setting_interactions:
            if not interaction.success:
                failed_counts[interaction.setting_id] = (
                    failed_counts.get(interaction.setting_id, 0) + 1
                )

        return sorted(failed_counts.items(), key=lambda x: x[1], reverse=True)

    def get_problem_menus(self) -> list[tuple[str, float]]:
        menu_times = {}
        for visit in self.menu_visits:
            menu_times[visit.menu_id] = (
                menu_times.get(visit.menu_id, 0.0) + visit.duration
            )

        return sorted(menu_times.items(), key=lambda x: x[1], reverse=True)
