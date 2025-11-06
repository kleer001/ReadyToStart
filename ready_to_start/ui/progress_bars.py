import random
import time
from abc import ABC, abstractmethod
from configparser import ConfigParser


class ProgressBar(ABC):
    def __init__(self, label: str, config: ConfigParser):
        self.label = label
        self.config = config
        self.progress = 0.0
        self.last_update = time.time()
        self.children = []

    @abstractmethod
    def update(self, delta_time: float) -> float:
        pass

    def _get_width(self) -> int:
        return int(self.config.get("bar_defaults", "width", fallback="40"))

    def _get_character(self) -> str:
        return self.config.get("bar_defaults", "character", fallback="=")

    def render(self, indent: int = 0) -> list[str]:
        width = self._get_width()
        char = self._get_character()
        percentage = int(self.progress * 100)

        filled = int(width * self.progress)
        bar = char * filled + " " * (width - filled)

        indent_str = " " * indent
        line = f"{indent_str}{self.label}: [{bar}] {percentage}%"
        lines = [line]

        for child in self.children:
            lines.extend(child.render(indent + 2))

        return lines


class ReliableProgressBar(ProgressBar):
    def update(self, delta_time: float) -> float:
        if self.progress < 1.0:
            increment = random.uniform(0.01, 0.05)
            self.progress = min(1.0, self.progress + increment)
        return self.progress


class UnreliableProgressBar(ProgressBar):
    def update(self, delta_time: float) -> float:
        if self.progress < 1.0:
            if random.random() < 0.3:
                decrement = random.uniform(0.05, 0.15)
                self.progress = max(0.0, self.progress - decrement)
            else:
                increment = random.uniform(0.01, 0.08)
                self.progress = min(1.0, self.progress + increment)
        return self.progress


class StuckProgressBar(ProgressBar):
    def __init__(self, label: str, config: ConfigParser, stuck_at: float = 0.99):
        super().__init__(label, config)
        self.stuck_at = stuck_at
        self.is_stuck = False

    def update(self, delta_time: float) -> float:
        if self.is_stuck:
            return self.progress

        if self.progress < self.stuck_at:
            increment = random.uniform(0.02, 0.06)
            self.progress = min(self.stuck_at, self.progress + increment)
        else:
            self.is_stuck = True
            self.progress = self.stuck_at

        return self.progress


class OscillatingProgressBar(ProgressBar):
    def __init__(self, label: str, config: ConfigParser):
        super().__init__(label, config)
        self.direction = 1

    def update(self, delta_time: float) -> float:
        increment = random.uniform(0.02, 0.05) * self.direction
        self.progress += increment

        if self.progress >= 1.0:
            self.progress = 1.0
            self.direction = -1
        elif self.progress <= 0.0:
            self.progress = 0.0
            self.direction = 1

        return self.progress


class NestedProgressBar(ProgressBar):
    def __init__(self, label: str, config: ConfigParser, child_count: int = 2):
        super().__init__(label, config)
        self.child_count = child_count
        self._spawn_children()

    def _spawn_children(self):
        bar_types = ["reliable", "unreliable", "stuck"]
        for i in range(self.child_count):
            bar_type = random.choice(bar_types)
            child_label = f"Subtask {i+1}"

            if bar_type == "reliable":
                child = ReliableProgressBar(child_label, self.config)
            elif bar_type == "unreliable":
                child = UnreliableProgressBar(child_label, self.config)
            else:
                child = StuckProgressBar(child_label, self.config, stuck_at=random.uniform(0.7, 0.99))

            self.children.append(child)

    def update(self, delta_time: float) -> float:
        if not self.children:
            return self.progress

        for child in self.children:
            child.update(delta_time)

        total_progress = sum(child.progress for child in self.children)
        self.progress = total_progress / len(self.children)

        return self.progress


class ProgressBarFactory:
    @staticmethod
    def create(label: str, bar_type: str, config: ConfigParser) -> ProgressBar:
        if bar_type == "reliable":
            return ReliableProgressBar(label, config)
        elif bar_type == "unreliable":
            return UnreliableProgressBar(label, config)
        elif bar_type == "stuck":
            return StuckProgressBar(label, config)
        elif bar_type == "oscillating":
            return OscillatingProgressBar(label, config)
        elif bar_type == "nested":
            return NestedProgressBar(label, config)
        else:
            return ReliableProgressBar(label, config)

    @staticmethod
    def create_random(label: str, config: ConfigParser) -> ProgressBar:
        weights = {
            "reliable": float(config.get("behavior_weights", "reliable", fallback="0.3")),
            "unreliable": float(config.get("behavior_weights", "unreliable", fallback="0.4")),
            "stuck": float(config.get("behavior_weights", "stuck", fallback="0.2")),
            "nested": float(config.get("behavior_weights", "nested", fallback="0.1")),
        }

        bar_types = list(weights.keys())
        weight_values = list(weights.values())
        chosen_type = random.choices(bar_types, weights=weight_values)[0]

        return ProgressBarFactory.create(label, chosen_type, config)
