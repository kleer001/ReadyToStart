from dataclasses import dataclass

from ready_to_start.core.dependencies import SimpleDependency, ValueDependency
from ready_to_start.core.game_state import GameState


@dataclass
class EvaluationResult:
    setting_id: str
    can_enable: bool
    blocking_deps: list[str]
    reason: str


class DependencyEvaluator:
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.cache: dict[str, EvaluationResult] = {}
        self.dirty: set[str] = set()

    def invalidate_cache(self, setting_id: str) -> None:
        if setting_id in self.dirty:
            return
        self.dirty.add(setting_id)
        for dependent_id in self._find_dependents(setting_id):
            self.invalidate_cache(dependent_id)

    def evaluate(self, setting_id: str) -> EvaluationResult:
        if setting_id in self.cache and setting_id not in self.dirty:
            return self.cache[setting_id]

        result = self._evaluate_setting(setting_id)
        self.cache[setting_id] = result
        self.dirty.discard(setting_id)
        return result

    def evaluate_all(self) -> dict[str, EvaluationResult]:
        return {
            setting_id: self.evaluate(setting_id)
            for setting_id in self.state.settings
        }

    def _evaluate_setting(self, setting_id: str) -> EvaluationResult:
        setting = self.state.get_setting(setting_id)
        if not setting:
            return EvaluationResult(setting_id, False, [], "Setting not found")

        deps = self.state.resolver.dependencies.get(setting_id, [])
        blocking = [
            self._describe_dependency(dep)
            for dep in deps
            if not dep.evaluate(self.state)
        ]

        return EvaluationResult(
            setting_id=setting_id,
            can_enable=len(blocking) == 0,
            blocking_deps=blocking,
            reason="" if not blocking else f"Blocked by: {', '.join(blocking)}",
        )

    def _describe_dependency(self, dep) -> str:
        if isinstance(dep, SimpleDependency):
            return f"{dep.setting_id} must be {dep.required_state.value}"
        elif isinstance(dep, ValueDependency):
            return f"{dep.setting_a} {dep.operator} {dep.setting_b}"
        return str(dep)

    def _find_dependents(self, setting_id: str) -> set[str]:
        dependents = set()
        for dep_id, deps in self.state.resolver.dependencies.items():
            for dep in deps:
                if self._depends_on(dep, setting_id):
                    dependents.add(dep_id)
        return dependents

    def _depends_on(self, dep, setting_id: str) -> bool:
        if isinstance(dep, SimpleDependency):
            return dep.setting_id == setting_id
        elif isinstance(dep, ValueDependency):
            return dep.setting_a == setting_id or dep.setting_b == setting_id
        return False
