
import pytest

from ready_to_start.anti_patterns.effects import FakeErrorEffect, FreezeProgressEffect
from ready_to_start.anti_patterns.engine import AntiPatternEngine
from ready_to_start.anti_patterns.triggers import CounterTrigger, RandomTrigger
from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting


@pytest.fixture
def game_state():
    state = GameState()
    menu = MenuNode(id="test_menu", category="Test")

    for i in range(5):
        menu.add_setting(
            Setting(
                id=f"setting_{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.DISABLED,
                label=f"Setting {i}",
            )
        )

    state.add_menu(menu)
    return state


@pytest.fixture
def ui_state():
    return {}


@pytest.fixture
def engine(game_state, ui_state):
    return AntiPatternEngine(game_state, ui_state, seed=42)


def test_engine_initialization(engine):
    assert engine.enabled
    assert engine.tick_count == 0
    assert len(engine.patterns) == 0
    assert len(engine.active_effects) == 0


def test_add_pattern(engine):
    trigger = CounterTrigger("test_trigger", "clicks", 10)
    effect = FakeErrorEffect("test_effect", "Test message")

    engine.add_pattern("test_pattern", trigger, effect, cooldown=5)

    assert len(engine.patterns) == 1
    assert engine.patterns[0].id == "test_pattern"
    assert engine.patterns[0].cooldown == 5


def test_increment_counter(engine):
    engine.increment_counter("clicks", 1)

    assert engine.trigger_context.counters["clicks"] == 1

    engine.increment_counter("clicks", 5)

    assert engine.trigger_context.counters["clicks"] == 6


def test_trigger_event(engine):
    engine.trigger_event("test_event")

    assert "test_event" in engine.trigger_context.events
    assert engine.trigger_context.events["test_event"] == 0


def test_clear_event(engine):
    engine.trigger_event("test_event")
    engine.clear_event("test_event")

    assert "test_event" not in engine.trigger_context.events


def test_update_increments_tick_count(engine):
    assert engine.tick_count == 0

    engine.update()
    assert engine.tick_count == 1

    engine.update()
    assert engine.tick_count == 2


def test_pattern_activation(engine, ui_state):
    trigger = CounterTrigger("test_trigger", "clicks", 5)
    effect = FakeErrorEffect("test_effect", "Test error")

    engine.add_pattern("test_pattern", trigger, effect)

    engine.increment_counter("clicks", 10)
    engine.update()

    assert len(engine.active_effects) == 1
    assert "fake_messages" in ui_state


def test_pattern_cooldown(engine, ui_state):
    trigger = CounterTrigger("test_trigger", "clicks", 1)
    effect = FakeErrorEffect("test_effect", "Test")

    engine.add_pattern("test_pattern", trigger, effect, cooldown=10)

    engine.increment_counter("clicks", 10)

    engine.update()
    assert len(ui_state.get("fake_messages", [])) == 1

    engine.update()
    assert len(ui_state.get("fake_messages", [])) == 1


def test_pattern_cooldown_expires(engine, ui_state):
    trigger = CounterTrigger("test_trigger", "clicks", 1)
    effect = FakeErrorEffect("test_effect", "Test")

    engine.add_pattern("test_pattern", trigger, effect, cooldown=3)

    engine.increment_counter("clicks", 10)

    engine.update()
    initial_count = len(ui_state.get("fake_messages", []))

    for _ in range(3):
        engine.update()

    engine.update()
    final_count = len(ui_state.get("fake_messages", []))

    assert final_count > initial_count


def test_effect_duration_expiration(engine):
    from ready_to_start.anti_patterns.triggers import OnceTrigger

    base_trigger = CounterTrigger("test_trigger", "clicks", 1)
    trigger = OnceTrigger("once", base_trigger)
    effect = FreezeProgressEffect("test_effect", duration=3)

    engine.add_pattern("test_pattern", trigger, effect)

    engine.increment_counter("clicks", 10)
    engine.update()

    assert len(engine.active_effects) == 1
    assert effect.remaining == 3

    engine.update()
    assert effect.remaining == 2

    engine.update()
    assert effect.remaining == 1

    engine.update()
    assert effect.remaining == 0
    assert len(engine.active_effects) == 0


def test_multiple_patterns(engine, ui_state):
    trigger1 = CounterTrigger("t1", "clicks", 5)
    effect1 = FakeErrorEffect("e1", "Error 1")

    trigger2 = CounterTrigger("t2", "visits", 3)
    effect2 = FakeErrorEffect("e2", "Error 2")

    engine.add_pattern("p1", trigger1, effect1)
    engine.add_pattern("p2", trigger2, effect2)

    engine.increment_counter("clicks", 10)
    engine.increment_counter("visits", 10)
    engine.update()

    assert len(ui_state.get("fake_messages", [])) == 2


def test_get_active_effect_ids(engine):
    trigger = CounterTrigger("test_trigger", "clicks", 1)
    effect = FreezeProgressEffect("test_effect", duration=5)

    engine.add_pattern("test_pattern", trigger, effect)

    assert len(engine.get_active_effect_ids()) == 0

    engine.increment_counter("clicks", 10)
    engine.update()

    assert "test_effect" in engine.get_active_effect_ids()


def test_is_effect_active(engine):
    trigger = CounterTrigger("test_trigger", "clicks", 1)
    effect = FreezeProgressEffect("test_effect", duration=5)

    engine.add_pattern("test_pattern", trigger, effect)

    assert not engine.is_effect_active("test_effect")

    engine.increment_counter("clicks", 10)
    engine.update()

    assert engine.is_effect_active("test_effect")


def test_glitch_engine_integration(engine):
    text = "Test text"

    result = engine.apply_glitch(text)
    assert result == text

    engine.enable_glitches(0.8)

    glitched_count = 0
    for _ in range(100):
        result = engine.apply_glitch(text)
        if result != text:
            glitched_count += 1

    assert glitched_count > 0


def test_disable_glitches(engine):
    engine.enable_glitches(1.0)
    engine.disable_glitches()

    text = "Test text"
    result = engine.apply_glitch(text)

    assert result == text


def test_schedule_fake_message(engine, ui_state):
    engine.message_generator.templates["test"] = ["Test message"]

    engine.schedule_fake_message(2, "test")

    engine.update()
    assert len(ui_state.get("fake_messages", [])) == 0

    engine.update()
    assert len(ui_state.get("fake_messages", [])) == 1


def test_engine_disabled(engine, ui_state):
    trigger = CounterTrigger("test_trigger", "clicks", 1)
    effect = FakeErrorEffect("test_effect", "Test")

    engine.add_pattern("test_pattern", trigger, effect)
    engine.enabled = False

    engine.increment_counter("clicks", 10)
    engine.update()

    assert len(ui_state.get("fake_messages", [])) == 0


def test_load_from_config(engine, tmp_path):
    config_content = """[global]
enabled = true

[pattern_test]
trigger_type = counter
trigger_counter = clicks
trigger_threshold = 5
effect_type = fake_error
effect_message = Test error message
cooldown = 10
"""

    config_path = tmp_path / "test_anti_patterns.ini"
    config_path.write_text(config_content)

    engine.load_from_config(str(config_path))

    assert len(engine.patterns) == 1
    assert engine.patterns[0].id == "test"
    assert engine.patterns[0].cooldown == 10


def test_parse_value_boolean(engine):
    assert engine._parse_value("true") is True
    assert engine._parse_value("false") is False
    assert engine._parse_value("True") is True
    assert engine._parse_value("False") is False


def test_parse_value_integer(engine):
    assert engine._parse_value("42") == 42
    assert engine._parse_value("-10") == -10


def test_parse_value_float(engine):
    assert engine._parse_value("3.14") == 3.14
    assert engine._parse_value("-2.5") == -2.5


def test_parse_value_string(engine):
    assert engine._parse_value("hello") == "hello"
    assert engine._parse_value("test message") == "test message"


def test_multiple_active_effects(engine):
    trigger1 = CounterTrigger("t1", "clicks", 1)
    effect1 = FreezeProgressEffect("e1", duration=10)

    trigger2 = CounterTrigger("t2", "visits", 1)
    effect2 = FreezeProgressEffect("e2", duration=10)

    engine.add_pattern("p1", trigger1, effect1)
    engine.add_pattern("p2", trigger2, effect2)

    engine.increment_counter("clicks", 10)
    engine.increment_counter("visits", 10)
    engine.update()

    assert len(engine.active_effects) == 2


def test_deterministic_behavior():
    state = GameState()
    ui_state1 = {}
    ui_state2 = {}

    engine1 = AntiPatternEngine(state, ui_state1, seed=42)
    engine2 = AntiPatternEngine(state, ui_state2, seed=42)

    trigger = RandomTrigger("test", 0.5)
    effect = FakeErrorEffect("test", "Test")

    engine1.add_pattern("test", trigger, effect)
    engine2.add_pattern("test", trigger, effect)

    for _ in range(100):
        engine1.update()
        engine2.update()

    assert len(ui_state1.get("fake_messages", [])) == len(
        ui_state2.get("fake_messages", [])
    )
