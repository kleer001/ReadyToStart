import tempfile

import pytest

from src.core.enums import SettingState, SettingType
from src.core.evaluator import DependencyEvaluator
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.propagation import PropagationRule, StatePropagator
from src.core.types import Setting


@pytest.fixture
def propagation_state():
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
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
        type=SettingType.INTEGER,
        value=50,
        state=SettingState.ENABLED,
        label="C",
        min_value=0,
        max_value=100,
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    menu.add_setting(setting_c)
    state.add_menu(menu)

    return state


def test_propagator_basic(propagation_state):
    evaluator = DependencyEvaluator(propagation_state)
    propagator = StatePropagator(propagation_state, evaluator)

    rule = PropagationRule(
        trigger_setting="a",
        trigger_condition=lambda s: s.state == SettingState.ENABLED,
        affected_settings=["b"],
        effect=lambda s: setattr(s, "state", SettingState.ENABLED),
    )
    propagator.add_rule(rule)

    propagation_state.get_setting("a").state = SettingState.ENABLED
    affected = propagator.propagate("a")

    assert "b" in affected
    assert propagation_state.get_setting("b").state == SettingState.ENABLED


def test_propagator_no_match(propagation_state):
    evaluator = DependencyEvaluator(propagation_state)
    propagator = StatePropagator(propagation_state, evaluator)

    rule = PropagationRule(
        trigger_setting="a",
        trigger_condition=lambda s: s.state == SettingState.ENABLED,
        affected_settings=["b"],
        effect=lambda s: setattr(s, "state", SettingState.ENABLED),
    )
    propagator.add_rule(rule)

    affected = propagator.propagate("a")

    assert len(affected) == 0


def test_propagator_chain(propagation_state):
    evaluator = DependencyEvaluator(propagation_state)
    propagator = StatePropagator(propagation_state, evaluator)

    rule1 = PropagationRule(
        trigger_setting="a",
        trigger_condition=lambda s: s.state == SettingState.ENABLED,
        affected_settings=["b"],
        effect=lambda s: setattr(s, "state", SettingState.ENABLED),
    )
    rule2 = PropagationRule(
        trigger_setting="b",
        trigger_condition=lambda s: s.state == SettingState.ENABLED,
        affected_settings=["c"],
        effect=lambda s: setattr(s, "value", 100),
    )

    propagator.add_rule(rule1)
    propagator.add_rule(rule2)

    propagation_state.get_setting("a").state = SettingState.ENABLED
    affected = propagator.propagate("a")

    assert "b" in affected
    assert "c" in affected
    assert propagation_state.get_setting("c").value == 100


def test_propagator_depth_limit(propagation_state):
    evaluator = DependencyEvaluator(propagation_state)
    propagator = StatePropagator(propagation_state, evaluator)

    rule = PropagationRule(
        trigger_setting="a",
        trigger_condition=lambda s: True,
        affected_settings=["a"],
        effect=lambda s: None,
    )
    propagator.add_rule(rule)

    propagation_state.get_setting("a").state = SettingState.ENABLED
    affected = propagator.propagate("a")

    assert len(affected) <= StatePropagator.MAX_DEPTH


def test_propagator_parse_condition():
    state = GameState()
    evaluator = DependencyEvaluator(state)
    propagator = StatePropagator(state, evaluator)

    cond_eq = propagator._parse_condition("state == enabled")
    setting = Setting(
        id="test",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="Test",
    )
    assert cond_eq(setting) is True

    cond_gt = propagator._parse_condition("value > 50")
    setting.value = 60
    assert cond_gt(setting) is True


def test_propagator_parse_effect():
    state = GameState()
    evaluator = DependencyEvaluator(state)
    propagator = StatePropagator(state, evaluator)

    effect = propagator._parse_effect("value = 100")
    setting = Setting(
        id="test",
        type=SettingType.INTEGER,
        value=0,
        state=SettingState.ENABLED,
        label="Test",
        min_value=0,
        max_value=200,
    )

    effect(setting)
    assert setting.value == 100


def test_propagator_config_loading(propagation_state):
    evaluator = DependencyEvaluator(propagation_state)
    propagator = StatePropagator(propagation_state, evaluator)

    config_content = """[test_rule]
trigger_setting = a
condition = state == enabled
affected = b
effect = state = enabled
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    propagator.load_rules_from_config(config_path)

    assert len(propagator.rules) == 1
    assert propagator.rules[0].trigger_setting == "a"


def test_propagator_invalidates_cache(propagation_state):
    evaluator = DependencyEvaluator(propagation_state)
    propagator = StatePropagator(propagation_state, evaluator)

    evaluator.evaluate("b")
    assert "b" in evaluator.cache

    rule = PropagationRule(
        trigger_setting="a",
        trigger_condition=lambda s: s.state == SettingState.ENABLED,
        affected_settings=["b"],
        effect=lambda s: setattr(s, "state", SettingState.ENABLED),
    )
    propagator.add_rule(rule)

    propagation_state.get_setting("a").state = SettingState.ENABLED
    propagator.propagate("a")

    assert "b" in evaluator.dirty
