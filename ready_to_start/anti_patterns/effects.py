from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random
from typing import Any, Dict, Optional

from ready_to_start.core.enums import SettingState
from ready_to_start.core.game_state import GameState


@dataclass
class EffectContext:
    game_state: GameState
    ui_state: Dict[str, Any]
    random: Random


class Effect(ABC):
    def __init__(self, effect_id: str, duration: int = 1):
        self.id = effect_id
        self.duration = duration
        self.remaining = 0

    @abstractmethod
    def apply(self, context: EffectContext) -> None:
        pass

    def revert(self, context: EffectContext) -> None:
        pass

    def is_active(self) -> bool:
        return self.remaining > 0

    def tick(self) -> None:
        if self.remaining > 0:
            self.remaining -= 1


class HideSettingEffect(Effect):
    def __init__(self, effect_id: str, setting_pattern: str, duration: int = 5):
        super().__init__(effect_id, duration)
        self.setting_pattern = setting_pattern
        self.hidden_settings: list[str] = []

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        self.hidden_settings = []

        for setting_id, setting in context.game_state.settings.items():
            if self.setting_pattern in setting_id or self.setting_pattern == "*":
                if setting.state != SettingState.HIDDEN:
                    self.hidden_settings.append(setting_id)
                    context.ui_state.setdefault("hidden_settings", set()).add(
                        setting_id
                    )

    def revert(self, context: EffectContext) -> None:
        for setting_id in self.hidden_settings:
            hidden_set = context.ui_state.get("hidden_settings", set())
            hidden_set.discard(setting_id)


class ShuffleMenuEffect(Effect):
    def __init__(self, effect_id: str, duration: int = 3):
        super().__init__(effect_id, duration)
        self.original_order: Dict[str, list[str]] = {}

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        self.original_order = {}

        for menu_id, menu in context.game_state.menus.items():
            self.original_order[menu_id] = [s.id for s in menu.settings]
            shuffled = list(menu.settings)
            context.random.shuffle(shuffled)
            menu.settings = shuffled

    def revert(self, context: EffectContext) -> None:
        for menu_id, original_ids in self.original_order.items():
            menu = context.game_state.menus.get(menu_id)
            if menu:
                id_to_setting = {s.id: s for s in menu.settings}
                menu.settings = [id_to_setting[sid] for sid in original_ids]


class FakeErrorEffect(Effect):
    def __init__(self, effect_id: str, message: str):
        super().__init__(effect_id, duration=1)
        self.message = message

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        messages = context.ui_state.setdefault("fake_messages", [])
        messages.append({"type": "error", "text": self.message})


class FreezeProgressEffect(Effect):
    def __init__(self, effect_id: str, duration: int = 10):
        super().__init__(effect_id, duration)

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        context.ui_state["progress_frozen"] = True

    def revert(self, context: EffectContext) -> None:
        context.ui_state.pop("progress_frozen", None)


class ReverseProgressEffect(Effect):
    def __init__(self, effect_id: str, duration: int = 5):
        super().__init__(effect_id, duration)

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        context.ui_state["progress_reversed"] = True

    def revert(self, context: EffectContext) -> None:
        context.ui_state.pop("progress_reversed", None)


class BlinkSettingEffect(Effect):
    def __init__(self, effect_id: str, setting_id: str, duration: int = 8):
        super().__init__(effect_id, duration)
        self.setting_id = setting_id
        self.original_state: Optional[SettingState] = None

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        setting = context.game_state.get_setting(self.setting_id)
        if setting:
            self.original_state = setting.state
            setting.state = SettingState.BLINKING

    def revert(self, context: EffectContext) -> None:
        if self.original_state:
            setting = context.game_state.get_setting(self.setting_id)
            if setting:
                setting.state = self.original_state


class SwapSettingsEffect(Effect):
    def __init__(
        self, effect_id: str, setting_a: str, setting_b: str, duration: int = 5
    ):
        super().__init__(effect_id, duration)
        self.setting_a = setting_a
        self.setting_b = setting_b

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        setting_a = context.game_state.get_setting(self.setting_a)
        setting_b = context.game_state.get_setting(self.setting_b)

        if setting_a and setting_b:
            setting_a.label, setting_b.label = setting_b.label, setting_a.label

    def revert(self, context: EffectContext) -> None:
        setting_a = context.game_state.get_setting(self.setting_a)
        setting_b = context.game_state.get_setting(self.setting_b)

        if setting_a and setting_b:
            setting_a.label, setting_b.label = setting_b.label, setting_a.label


class GlitchTextEffect(Effect):
    def __init__(self, effect_id: str, intensity: float = 0.3, duration: int = 3):
        super().__init__(effect_id, duration)
        self.intensity = intensity

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        context.ui_state["glitch_intensity"] = self.intensity

    def revert(self, context: EffectContext) -> None:
        context.ui_state.pop("glitch_intensity", None)


class DisableInputEffect(Effect):
    def __init__(self, effect_id: str, duration: int = 2):
        super().__init__(effect_id, duration)

    def apply(self, context: EffectContext) -> None:
        self.remaining = self.duration
        context.ui_state["input_disabled"] = True

    def revert(self, context: EffectContext) -> None:
        context.ui_state.pop("input_disabled", None)


class EffectFactory:
    @staticmethod
    def from_config(config_dict: Dict[str, Any]) -> Effect:
        effect_type = config_dict["type"]
        effect_id = config_dict["id"]

        if effect_type == "hide_setting":
            return HideSettingEffect(
                effect_id,
                config_dict["pattern"],
                config_dict.get("duration", 5),
            )
        elif effect_type == "shuffle_menu":
            return ShuffleMenuEffect(effect_id, config_dict.get("duration", 3))
        elif effect_type == "fake_error":
            return FakeErrorEffect(effect_id, config_dict["message"])
        elif effect_type == "freeze_progress":
            return FreezeProgressEffect(effect_id, config_dict.get("duration", 10))
        elif effect_type == "reverse_progress":
            return ReverseProgressEffect(effect_id, config_dict.get("duration", 5))
        elif effect_type == "blink_setting":
            return BlinkSettingEffect(
                effect_id, config_dict["setting"], config_dict.get("duration", 8)
            )
        elif effect_type == "swap_settings":
            return SwapSettingsEffect(
                effect_id,
                config_dict["setting_a"],
                config_dict["setting_b"],
                config_dict.get("duration", 5),
            )
        elif effect_type == "glitch_text":
            return GlitchTextEffect(
                effect_id,
                config_dict.get("intensity", 0.3),
                config_dict.get("duration", 3),
            )
        elif effect_type == "disable_input":
            return DisableInputEffect(effect_id, config_dict.get("duration", 2))
        else:
            raise ValueError(f"Unknown effect type: {effect_type}")
