import tempfile

import pytest

from ready_to_start.core.enums import CompletionState, SettingState, SettingType
from ready_to_start.core.evaluator import DependencyEvaluator
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.progress import ProgressCalculator
from ready_to_start.core.types import Setting
from ready_to_start.core.victory import VictoryCondition, VictoryDetector, VictoryType


@pytest.fixture
def victory_state():
    state = GameState()

    menu1 = MenuNode(id="menu1", category="Test1")
    setting1 = Setting(
        id="s1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="S1",
    )
    menu1.add_setting(setting1)

    state.add_menu(menu1)

    return state


def test_victory_detector_basic(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    condition = VictoryCondition(
        victory_type=VictoryType.COMPLETE,
        requirements=[lambda state: True],
        next_layer="next",
    )
    detector.add_condition(condition)

    result = detector.check_victory()

    assert result is not None
    assert result.victory_type == VictoryType.COMPLETE
    assert result.next_layer == "next"


def test_victory_detector_not_met(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    condition = VictoryCondition(
        victory_type=VictoryType.COMPLETE,
        requirements=[lambda state: False],
    )
    detector.add_condition(condition)

    result = detector.check_victory()

    assert result is None


def test_victory_detector_multiple_requirements(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    condition = VictoryCondition(
        victory_type=VictoryType.COMPLETE,
        requirements=[lambda state: True, lambda state: True],
    )
    detector.add_condition(condition)

    result = detector.check_victory()

    assert result is not None


def test_victory_detector_partial_requirements(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    condition = VictoryCondition(
        victory_type=VictoryType.COMPLETE,
        requirements=[lambda state: True, lambda state: False],
    )
    detector.add_condition(condition)

    result = detector.check_victory()

    assert result is None


def test_victory_parse_progress_requirement(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    req = detector._parse_requirement("progress > 50")

    assert callable(req)


def test_victory_parse_critical_path_requirement(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    req = detector._parse_requirement("critical_path_complete")

    assert callable(req)
    assert req(victory_state) is False


def test_victory_parse_menu_requirement(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    req = detector._parse_requirement("menu:menu1 == complete")

    assert callable(req)


def test_victory_config_loading(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    config_content = """[test_victory]
type = complete
requirements = progress > 90
next_layer = next_level
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    detector.load_from_config(config_path)

    assert len(detector.conditions) == 1
    assert detector.conditions[0].victory_type == VictoryType.COMPLETE
    assert detector.conditions[0].next_layer == "next_level"


def test_victory_multiple_conditions(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    condition1 = VictoryCondition(
        victory_type=VictoryType.PARTIAL,
        requirements=[lambda state: False],
    )
    condition2 = VictoryCondition(
        victory_type=VictoryType.COMPLETE,
        requirements=[lambda state: True],
    )

    detector.add_condition(condition1)
    detector.add_condition(condition2)

    result = detector.check_victory()

    assert result.victory_type == VictoryType.COMPLETE


def test_victory_types():
    assert VictoryType.NONE.value == "none"
    assert VictoryType.PARTIAL.value == "partial"
    assert VictoryType.COMPLETE.value == "complete"
    assert VictoryType.SECRET.value == "secret"


def test_victory_hidden_requirement(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    req = detector._parse_requirement("hidden:magic_number")

    assert callable(req)
    assert req(victory_state) is False


def test_victory_complex_config(victory_state):
    evaluator = DependencyEvaluator(victory_state)
    progress = ProgressCalculator(victory_state, evaluator)
    detector = VictoryDetector(victory_state, progress)

    config_content = """[partial_victory]
type = partial
requirements = progress > 50

[complete_victory]
type = complete
requirements = progress > 90 && menu:menu1 == complete
next_layer = final_level
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    detector.load_from_config(config_path)

    assert len(detector.conditions) == 2
