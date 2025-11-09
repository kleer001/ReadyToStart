from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from random import Random
from typing import Any, Dict

from ready_to_start.core.game_state import GameState


@dataclass
class TriggerContext:
    game_state: GameState
    counters: Dict[str, int] = field(default_factory=dict)
    events: Dict[str, int] = field(default_factory=dict)
    random: Random = field(default_factory=Random)


class Trigger(ABC):
    def __init__(self, trigger_id: str):
        self.id = trigger_id
        self.activated_count = 0

    @abstractmethod
    def should_activate(self, context: TriggerContext) -> bool:
        pass

    def on_activate(self):
        self.activated_count += 1


class CounterTrigger(Trigger):
    def __init__(self, trigger_id: str, counter_name: str, threshold: int):
        super().__init__(trigger_id)
        self.counter_name = counter_name
        self.threshold = threshold

    def should_activate(self, context: TriggerContext) -> bool:
        current = context.counters.get(self.counter_name, 0)
        return current >= self.threshold


class RandomTrigger(Trigger):
    def __init__(self, trigger_id: str, probability: float):
        super().__init__(trigger_id)
        self.probability = max(0.0, min(1.0, probability))

    def should_activate(self, context: TriggerContext) -> bool:
        return context.random.random() < self.probability


class EventTrigger(Trigger):
    def __init__(self, trigger_id: str, event_name: str):
        super().__init__(trigger_id)
        self.event_name = event_name

    def should_activate(self, context: TriggerContext) -> bool:
        return self.event_name in context.events


class CompositeTrigger(Trigger):
    def __init__(self, trigger_id: str, triggers: list[Trigger], require_all: bool):
        super().__init__(trigger_id)
        self.triggers = triggers
        self.require_all = require_all

    def should_activate(self, context: TriggerContext) -> bool:
        if self.require_all:
            return all(t.should_activate(context) for t in self.triggers)
        return any(t.should_activate(context) for t in self.triggers)


class ProgressTrigger(Trigger):
    def __init__(self, trigger_id: str, min_progress: float, max_progress: float):
        super().__init__(trigger_id)
        self.min_progress = min_progress
        self.max_progress = max_progress

    def should_activate(self, context: TriggerContext) -> bool:
        total = len(context.game_state.settings)
        if total == 0:
            return False

        enabled = sum(
            1
            for s in context.game_state.settings.values()
            if s.state.value in ["enabled", "locked"]
        )
        progress = (enabled / total) * 100

        return self.min_progress <= progress <= self.max_progress


class IntervalTrigger(Trigger):
    def __init__(self, trigger_id: str, counter_name: str, interval: int):
        super().__init__(trigger_id)
        self.counter_name = counter_name
        self.interval = interval
        self.last_activation = -interval

    def should_activate(self, context: TriggerContext) -> bool:
        current = context.counters.get(self.counter_name, 0)
        if current - self.last_activation >= self.interval:
            self.last_activation = current
            return True
        return False


class OnceTrigger(Trigger):
    def __init__(self, trigger_id: str, base_trigger: Trigger):
        super().__init__(trigger_id)
        self.base_trigger = base_trigger
        self.has_fired = False

    def should_activate(self, context: TriggerContext) -> bool:
        if self.has_fired:
            return False
        if self.base_trigger.should_activate(context):
            self.has_fired = True
            return True
        return False


class TriggerFactory:
    @staticmethod
    def from_config(config_dict: Dict[str, Any]) -> Trigger:
        trigger_type = config_dict["type"]
        trigger_id = config_dict["id"]

        if trigger_type == "counter":
            return CounterTrigger(
                trigger_id, config_dict["counter"], config_dict["threshold"]
            )
        elif trigger_type == "random":
            return RandomTrigger(trigger_id, config_dict["probability"])
        elif trigger_type == "event":
            return EventTrigger(trigger_id, config_dict["event"])
        elif trigger_type == "progress":
            return ProgressTrigger(
                trigger_id, config_dict["min_progress"], config_dict["max_progress"]
            )
        elif trigger_type == "interval":
            return IntervalTrigger(
                trigger_id, config_dict["counter"], config_dict["interval"]
            )
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
