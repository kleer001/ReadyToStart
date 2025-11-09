import pytest

from src.core.dependencies import SimpleDependency, ValueDependency
from src.core.enums import SettingState, SettingType
from src.core.evaluator import DependencyEvaluator
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting


@pytest.fixture
def evaluator_state():
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="A",
    )
    setting_b = Setting(
        id="b",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="B",
    )
    setting_c = Setting(
        id="c",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="C",
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    menu.add_setting(setting_c)
    state.add_menu(menu)

    state.resolver.add_dependency("b", SimpleDependency("a", SettingState.ENABLED))
    state.resolver.add_dependency("c", SimpleDependency("b", SettingState.ENABLED))

    return state


def test_evaluator_basic(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)
    result = evaluator.evaluate("b")

    assert result.setting_id == "b"
    assert result.can_enable is True
    assert len(result.blocking_deps) == 0


def test_evaluator_blocked(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)
    result = evaluator.evaluate("c")

    assert result.setting_id == "c"
    assert result.can_enable is False
    assert len(result.blocking_deps) == 1
    assert "b must be enabled" in result.blocking_deps[0]


def test_evaluator_cache(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)

    result1 = evaluator.evaluate("b")
    result2 = evaluator.evaluate("b")

    assert result1 is result2


def test_evaluator_cache_invalidation(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)

    result1 = evaluator.evaluate("c")
    assert result1.can_enable is False

    evaluator_state.get_setting("b").state = SettingState.ENABLED
    evaluator.invalidate_cache("b")

    result2 = evaluator.evaluate("c")
    assert result2.can_enable is True


def test_evaluator_all(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)
    results = evaluator.evaluate_all()

    assert len(results) == 3
    assert results["a"].can_enable is True
    assert results["b"].can_enable is True
    assert results["c"].can_enable is False


def test_evaluator_missing_setting(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)
    result = evaluator.evaluate("nonexistent")

    assert result.setting_id == "nonexistent"
    assert result.can_enable is False
    assert result.reason == "Setting not found"


def test_evaluator_value_dependency():
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.INTEGER,
        value=10,
        state=SettingState.ENABLED,
        label="A",
        min_value=0,
        max_value=100,
    )
    setting_b = Setting(
        id="b",
        type=SettingType.INTEGER,
        value=5,
        state=SettingState.DISABLED,
        label="B",
        min_value=0,
        max_value=100,
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    state.add_menu(menu)

    state.resolver.add_dependency("b", ValueDependency("a", ">", "b"))

    evaluator = DependencyEvaluator(state)
    result = evaluator.evaluate("b")

    assert result.can_enable is True
    assert "a > b" in result.blocking_deps or len(result.blocking_deps) == 0


def test_evaluator_find_dependents(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)

    dependents_of_a = evaluator._find_dependents("a")
    assert "b" in dependents_of_a

    dependents_of_b = evaluator._find_dependents("b")
    assert "c" in dependents_of_b


def test_evaluator_cascade_invalidation(evaluator_state):
    evaluator = DependencyEvaluator(evaluator_state)

    evaluator.evaluate("b")
    evaluator.evaluate("c")

    evaluator.invalidate_cache("a")

    assert "a" in evaluator.dirty
    assert "b" in evaluator.dirty
    assert "c" in evaluator.dirty
