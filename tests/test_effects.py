from random import Random

import pytest

from ready_to_start.anti_patterns.effects import (
    BlinkSettingEffect,
    DisableInputEffect,
    EffectContext,
    EffectFactory,
    FakeErrorEffect,
    FreezeProgressEffect,
    GlitchTextEffect,
    HideSettingEffect,
    ReverseProgressEffect,
    ShuffleMenuEffect,
    SwapSettingsEffect,
)
from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting


@pytest.fixture
def game_state():
    state = GameState()

    menu = MenuNode(id="test_menu", category="Test Menu")
    menu.add_setting(
        Setting(
            id="setting_a",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.DISABLED,
            label="Setting A",
        )
    )
    menu.add_setting(
        Setting(
            id="setting_b",
            type=SettingType.INTEGER,
            value=50,
            state=SettingState.ENABLED,
            label="Setting B",
        )
    )
    menu.add_setting(
        Setting(
            id="audio_test",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.DISABLED,
            label="Audio Test",
        )
    )

    state.add_menu(menu)
    return state


@pytest.fixture
def ui_state():
    return {}


@pytest.fixture
def context(game_state, ui_state):
    return EffectContext(game_state=game_state, ui_state=ui_state, random=Random(42))


def test_hide_setting_effect_apply(context, ui_state):
    effect = HideSettingEffect("test", "audio", duration=5)

    effect.apply(context)

    assert "hidden_settings" in ui_state
    assert "audio_test" in ui_state["hidden_settings"]
    assert effect.remaining == 5


def test_hide_setting_effect_wildcard(context, ui_state):
    effect = HideSettingEffect("test", "*", duration=5)

    effect.apply(context)

    assert len(ui_state["hidden_settings"]) == 3


def test_hide_setting_effect_revert(context, ui_state):
    effect = HideSettingEffect("test", "audio", duration=5)

    effect.apply(context)
    effect.revert(context)

    assert "audio_test" not in ui_state.get("hidden_settings", set())


def test_shuffle_menu_effect_apply(context, game_state):
    menu = game_state.get_menu("test_menu")
    original_order = [s.id for s in menu.settings]

    effect = ShuffleMenuEffect("test", duration=3)
    effect.apply(context)

    shuffled_order = [s.id for s in menu.settings]

    assert set(original_order) == set(shuffled_order)
    assert original_order != shuffled_order


def test_shuffle_menu_effect_revert(context, game_state):
    menu = game_state.get_menu("test_menu")
    original_order = [s.id for s in menu.settings]

    effect = ShuffleMenuEffect("test", duration=3)
    effect.apply(context)
    effect.revert(context)

    restored_order = [s.id for s in menu.settings]

    assert original_order == restored_order


def test_fake_error_effect_apply(context, ui_state):
    effect = FakeErrorEffect("test", "Test error message")

    effect.apply(context)

    assert "fake_messages" in ui_state
    assert len(ui_state["fake_messages"]) == 1
    assert ui_state["fake_messages"][0]["text"] == "Test error message"
    assert ui_state["fake_messages"][0]["type"] == "error"


def test_freeze_progress_effect_apply(context, ui_state):
    effect = FreezeProgressEffect("test", duration=10)

    effect.apply(context)

    assert ui_state["progress_frozen"] is True
    assert effect.remaining == 10


def test_freeze_progress_effect_revert(context, ui_state):
    effect = FreezeProgressEffect("test", duration=10)

    effect.apply(context)
    effect.revert(context)

    assert "progress_frozen" not in ui_state


def test_reverse_progress_effect_apply(context, ui_state):
    effect = ReverseProgressEffect("test", duration=5)

    effect.apply(context)

    assert ui_state["progress_reversed"] is True
    assert effect.remaining == 5


def test_reverse_progress_effect_revert(context, ui_state):
    effect = ReverseProgressEffect("test", duration=5)

    effect.apply(context)
    effect.revert(context)

    assert "progress_reversed" not in ui_state


def test_blink_setting_effect_apply(context, game_state):
    effect = BlinkSettingEffect("test", "setting_a", duration=8)

    original_state = game_state.get_setting("setting_a").state

    effect.apply(context)

    assert game_state.get_setting("setting_a").state == SettingState.BLINKING
    assert effect.original_state == original_state


def test_blink_setting_effect_revert(context, game_state):
    effect = BlinkSettingEffect("test", "setting_a", duration=8)

    original_state = game_state.get_setting("setting_a").state

    effect.apply(context)
    effect.revert(context)

    assert game_state.get_setting("setting_a").state == original_state


def test_blink_setting_effect_missing_setting(context):
    effect = BlinkSettingEffect("test", "nonexistent", duration=8)

    effect.apply(context)

    assert effect.original_state is None


def test_swap_settings_effect_apply(context, game_state):
    effect = SwapSettingsEffect("test", "setting_a", "setting_b", duration=5)

    original_a = game_state.get_setting("setting_a").label
    original_b = game_state.get_setting("setting_b").label

    effect.apply(context)

    assert game_state.get_setting("setting_a").label == original_b
    assert game_state.get_setting("setting_b").label == original_a


def test_swap_settings_effect_revert(context, game_state):
    effect = SwapSettingsEffect("test", "setting_a", "setting_b", duration=5)

    original_a = game_state.get_setting("setting_a").label
    original_b = game_state.get_setting("setting_b").label

    effect.apply(context)
    effect.revert(context)

    assert game_state.get_setting("setting_a").label == original_a
    assert game_state.get_setting("setting_b").label == original_b


def test_glitch_text_effect_apply(context, ui_state):
    effect = GlitchTextEffect("test", intensity=0.5, duration=3)

    effect.apply(context)

    assert ui_state["glitch_intensity"] == 0.5
    assert effect.remaining == 3


def test_glitch_text_effect_revert(context, ui_state):
    effect = GlitchTextEffect("test", intensity=0.5, duration=3)

    effect.apply(context)
    effect.revert(context)

    assert "glitch_intensity" not in ui_state


def test_disable_input_effect_apply(context, ui_state):
    effect = DisableInputEffect("test", duration=2)

    effect.apply(context)

    assert ui_state["input_disabled"] is True
    assert effect.remaining == 2


def test_disable_input_effect_revert(context, ui_state):
    effect = DisableInputEffect("test", duration=2)

    effect.apply(context)
    effect.revert(context)

    assert "input_disabled" not in ui_state


def test_effect_tick_countdown():
    effect = FreezeProgressEffect("test", duration=5)

    effect.remaining = 5
    assert effect.is_active()

    effect.tick()
    assert effect.remaining == 4
    assert effect.is_active()

    effect.tick()
    effect.tick()
    effect.tick()
    assert effect.remaining == 1
    assert effect.is_active()

    effect.tick()
    assert effect.remaining == 0
    assert not effect.is_active()


def test_effect_factory_hide_setting():
    config = {"id": "test", "type": "hide_setting", "pattern": "audio", "duration": 5}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, HideSettingEffect)
    assert effect.setting_pattern == "audio"
    assert effect.duration == 5


def test_effect_factory_shuffle_menu():
    config = {"id": "test", "type": "shuffle_menu", "duration": 3}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, ShuffleMenuEffect)
    assert effect.duration == 3


def test_effect_factory_fake_error():
    config = {"id": "test", "type": "fake_error", "message": "Test error"}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, FakeErrorEffect)
    assert effect.message == "Test error"


def test_effect_factory_freeze_progress():
    config = {"id": "test", "type": "freeze_progress", "duration": 10}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, FreezeProgressEffect)
    assert effect.duration == 10


def test_effect_factory_reverse_progress():
    config = {"id": "test", "type": "reverse_progress", "duration": 5}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, ReverseProgressEffect)
    assert effect.duration == 5


def test_effect_factory_blink_setting():
    config = {"id": "test", "type": "blink_setting", "setting": "test_setting"}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, BlinkSettingEffect)
    assert effect.setting_id == "test_setting"


def test_effect_factory_swap_settings():
    config = {
        "id": "test",
        "type": "swap_settings",
        "setting_a": "a",
        "setting_b": "b",
        "duration": 5,
    }

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, SwapSettingsEffect)
    assert effect.setting_a == "a"
    assert effect.setting_b == "b"


def test_effect_factory_glitch_text():
    config = {"id": "test", "type": "glitch_text", "intensity": 0.7, "duration": 2}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, GlitchTextEffect)
    assert effect.intensity == 0.7


def test_effect_factory_disable_input():
    config = {"id": "test", "type": "disable_input"}

    effect = EffectFactory.from_config(config)

    assert isinstance(effect, DisableInputEffect)


def test_effect_factory_unknown_type():
    config = {"id": "test", "type": "unknown"}

    with pytest.raises(ValueError, match="Unknown effect type"):
        EffectFactory.from_config(config)
