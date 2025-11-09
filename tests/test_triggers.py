from random import Random

import pytest

from src.anti_patterns.triggers import (
    CompositeTrigger,
    CounterTrigger,
    EventTrigger,
    IntervalTrigger,
    OnceTrigger,
    ProgressTrigger,
    RandomTrigger,
    TriggerContext,
    TriggerFactory,
)
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting


@pytest.fixture
def game_state():
    state = GameState()
    menu = MenuNode(id="test", category="Test")

    for i in range(10):
        menu.add_setting(
            Setting(
                id=f"test_setting_{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.DISABLED,
                label=f"Test {i}",
            )
        )

    state.add_menu(menu)
    return state


@pytest.fixture
def context(game_state):
    return TriggerContext(game_state=game_state, random=Random(42))


def test_counter_trigger_threshold_not_reached(context):
    trigger = CounterTrigger("test", "clicks", 10)
    context.counters["clicks"] = 5

    assert not trigger.should_activate(context)


def test_counter_trigger_threshold_reached(context):
    trigger = CounterTrigger("test", "clicks", 10)
    context.counters["clicks"] = 10

    assert trigger.should_activate(context)


def test_counter_trigger_threshold_exceeded(context):
    trigger = CounterTrigger("test", "clicks", 10)
    context.counters["clicks"] = 15

    assert trigger.should_activate(context)


def test_counter_trigger_missing_counter(context):
    trigger = CounterTrigger("test", "missing", 10)

    assert not trigger.should_activate(context)


def test_random_trigger_probability_zero(context):
    trigger = RandomTrigger("test", 0.0)

    for _ in range(100):
        assert not trigger.should_activate(context)


def test_random_trigger_probability_one(context):
    trigger = RandomTrigger("test", 1.0)

    for _ in range(100):
        assert trigger.should_activate(context)


def test_random_trigger_probability_clamping():
    trigger = RandomTrigger("test", 1.5)
    assert trigger.probability == 1.0

    trigger = RandomTrigger("test", -0.5)
    assert trigger.probability == 0.0


def test_event_trigger_event_not_present(context):
    trigger = EventTrigger("test", "test_event")

    assert not trigger.should_activate(context)


def test_event_trigger_event_present(context):
    trigger = EventTrigger("test", "test_event")
    context.events["test_event"] = 100

    assert trigger.should_activate(context)


def test_progress_trigger_below_range(context, game_state):
    trigger = ProgressTrigger("test", 50.0, 75.0)

    assert not trigger.should_activate(context)


def test_progress_trigger_within_range(context, game_state):
    trigger = ProgressTrigger("test", 50.0, 75.0)

    for i in range(6):
        setting = game_state.get_setting(f"test_setting_{i}")
        setting.state = SettingState.ENABLED

    assert trigger.should_activate(context)


def test_progress_trigger_above_range(context, game_state):
    trigger = ProgressTrigger("test", 10.0, 30.0)

    for i in range(10):
        setting = game_state.get_setting(f"test_setting_{i}")
        setting.state = SettingState.ENABLED

    assert not trigger.should_activate(context)


def test_progress_trigger_empty_state(context):
    empty_state = GameState()
    empty_context = TriggerContext(game_state=empty_state, random=Random(42))

    trigger = ProgressTrigger("test", 50.0, 75.0)

    assert not trigger.should_activate(empty_context)


def test_interval_trigger_first_activation(context):
    trigger = IntervalTrigger("test", "ticks", 10)
    context.counters["ticks"] = 10

    assert trigger.should_activate(context)


def test_interval_trigger_before_interval(context):
    trigger = IntervalTrigger("test", "ticks", 10)
    context.counters["ticks"] = 10

    trigger.should_activate(context)

    context.counters["ticks"] = 15
    assert not trigger.should_activate(context)


def test_interval_trigger_after_interval(context):
    trigger = IntervalTrigger("test", "ticks", 10)
    context.counters["ticks"] = 10

    trigger.should_activate(context)

    context.counters["ticks"] = 20
    assert trigger.should_activate(context)


def test_composite_trigger_all_required(context):
    t1 = CounterTrigger("t1", "clicks", 5)
    t2 = CounterTrigger("t2", "visits", 3)

    composite = CompositeTrigger("test", [t1, t2], require_all=True)

    context.counters["clicks"] = 10
    context.counters["visits"] = 2
    assert not composite.should_activate(context)

    context.counters["visits"] = 5
    assert composite.should_activate(context)


def test_composite_trigger_any_required(context):
    t1 = CounterTrigger("t1", "clicks", 5)
    t2 = CounterTrigger("t2", "visits", 3)

    composite = CompositeTrigger("test", [t1, t2], require_all=False)

    context.counters["clicks"] = 10
    context.counters["visits"] = 0
    assert composite.should_activate(context)

    context.counters["clicks"] = 0
    context.counters["visits"] = 5
    assert composite.should_activate(context)


def test_once_trigger_fires_once(context):
    base = CounterTrigger("base", "clicks", 5)
    once = OnceTrigger("test", base)

    context.counters["clicks"] = 10

    assert once.should_activate(context)
    assert not once.should_activate(context)
    assert not once.should_activate(context)


def test_once_trigger_waits_for_base(context):
    base = CounterTrigger("base", "clicks", 5)
    once = OnceTrigger("test", base)

    context.counters["clicks"] = 2
    assert not once.should_activate(context)

    context.counters["clicks"] = 10
    assert once.should_activate(context)
    assert not once.should_activate(context)


def test_trigger_on_activate():
    trigger = CounterTrigger("test", "clicks", 5)

    assert trigger.activated_count == 0

    trigger.on_activate()
    assert trigger.activated_count == 1

    trigger.on_activate()
    assert trigger.activated_count == 2


def test_trigger_factory_counter():
    config = {"id": "test", "type": "counter", "counter": "clicks", "threshold": 10}

    trigger = TriggerFactory.from_config(config)

    assert isinstance(trigger, CounterTrigger)
    assert trigger.counter_name == "clicks"
    assert trigger.threshold == 10


def test_trigger_factory_random():
    config = {"id": "test", "type": "random", "probability": 0.5}

    trigger = TriggerFactory.from_config(config)

    assert isinstance(trigger, RandomTrigger)
    assert trigger.probability == 0.5


def test_trigger_factory_event():
    config = {"id": "test", "type": "event", "event": "test_event"}

    trigger = TriggerFactory.from_config(config)

    assert isinstance(trigger, EventTrigger)
    assert trigger.event_name == "test_event"


def test_trigger_factory_progress():
    config = {"id": "test", "type": "progress", "min_progress": 25, "max_progress": 75}

    trigger = TriggerFactory.from_config(config)

    assert isinstance(trigger, ProgressTrigger)
    assert trigger.min_progress == 25
    assert trigger.max_progress == 75


def test_trigger_factory_interval():
    config = {"id": "test", "type": "interval", "counter": "ticks", "interval": 10}

    trigger = TriggerFactory.from_config(config)

    assert isinstance(trigger, IntervalTrigger)
    assert trigger.counter_name == "ticks"
    assert trigger.interval == 10


def test_trigger_factory_unknown_type():
    config = {"id": "test", "type": "unknown"}

    with pytest.raises(ValueError, match="Unknown trigger type"):
        TriggerFactory.from_config(config)
