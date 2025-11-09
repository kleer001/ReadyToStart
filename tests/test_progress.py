import pytest

from ready_to_start.core.dependencies import SimpleDependency
from ready_to_start.core.enums import CompletionState, SettingState, SettingType
from ready_to_start.core.evaluator import DependencyEvaluator
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.progress import ProgressCalculator
from ready_to_start.core.types import Setting


@pytest.fixture
def progress_state():
    state = GameState()

    menu1 = MenuNode(id="menu1", category="Test1")
    menu2 = MenuNode(id="menu2", category="Test2")

    setting1 = Setting(
        id="s1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="S1",
    )
    setting2 = Setting(
        id="s2",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="S2",
    )
    setting3 = Setting(
        id="s3",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.LOCKED,
        label="S3",
    )

    menu1.add_setting(setting1)
    menu1.add_setting(setting2)
    menu2.add_setting(setting3)

    state.add_menu(menu1)
    state.add_menu(menu2)

    return state


def test_progress_calculator_basic(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress = calculator.calculate_overall_progress()

    assert progress >= 0.0
    assert progress <= 99.0


def test_progress_calculator_empty_state():
    state = GameState()
    evaluator = DependencyEvaluator(state)
    calculator = ProgressCalculator(state, evaluator)

    progress = calculator.calculate_overall_progress()

    assert progress == 0.0


def test_progress_calculator_visited_bonus(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress_before = calculator.calculate_overall_progress()

    progress_state.visited_menus.append("menu1")
    progress_state.visited_menus.append("menu2")

    progress_after = calculator.calculate_overall_progress()

    assert progress_after > progress_before


def test_progress_menu_completion_incomplete(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress_state.get_setting("s1").state = SettingState.DISABLED

    completion = calculator.calculate_menu_completion("menu1")

    assert completion == CompletionState.INCOMPLETE


def test_progress_menu_completion_partial(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress_state.get_setting("s1").state = SettingState.ENABLED

    completion = calculator.calculate_menu_completion("menu1")

    assert completion == CompletionState.PARTIAL


def test_progress_menu_completion_complete(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress_state.get_setting("s1").state = SettingState.ENABLED
    progress_state.get_setting("s2").state = SettingState.ENABLED

    completion = calculator.calculate_menu_completion("menu1")

    assert completion == CompletionState.COMPLETE


def test_progress_menu_completion_nonexistent(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    completion = calculator.calculate_menu_completion("nonexistent")

    assert completion == CompletionState.INCOMPLETE


def test_progress_critical_path(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress_state.visited_menus.append("menu1")

    critical_progress = calculator.get_critical_path_progress()

    assert critical_progress == 50.0


def test_progress_victory_condition(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    progress_state.resolver.add_dependency("s2", SimpleDependency("s1", SettingState.ENABLED))

    victory = calculator.is_victory_condition_met()
    assert victory is False

    progress_state.get_setting("s1").state = SettingState.ENABLED
    progress_state.get_setting("s2").state = SettingState.ENABLED

    victory = calculator.is_victory_condition_met()
    assert victory is True


def test_progress_victory_no_critical_settings():
    state = GameState()

    setting = Setting(
        id="s1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="S1",
    )

    menu = MenuNode(id="menu", category="Test")
    menu.add_setting(setting)
    state.add_menu(menu)

    evaluator = DependencyEvaluator(state)
    calculator = ProgressCalculator(state, evaluator)

    victory = calculator.is_victory_condition_met()
    assert victory is False


def test_progress_count_configured_settings(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    count = calculator._count_configured_settings()

    assert count == 2


def test_progress_capped_at_99(progress_state):
    evaluator = DependencyEvaluator(progress_state)
    calculator = ProgressCalculator(progress_state, evaluator)

    for setting in progress_state.settings.values():
        setting.state = SettingState.ENABLED

    for i in range(100):
        progress_state.visited_menus.append(f"menu{i}")

    progress = calculator.calculate_overall_progress()

    assert progress == 99.0
