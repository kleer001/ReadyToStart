import configparser
from dataclasses import dataclass
from random import Random
from typing import Any

from src.anti_patterns.effects import Effect, EffectContext, EffectFactory
from src.anti_patterns.glitches import GlitchEngine
from src.anti_patterns.messages import FakeMessageGenerator, MessageScheduler
from src.anti_patterns.triggers import (
    Trigger,
    TriggerContext,
    TriggerFactory,
)
from src.core.game_state import GameState


@dataclass
class AntiPattern:
    id: str
    trigger: Trigger
    effect: Effect
    cooldown: int = 0
    remaining_cooldown: int = 0
    enabled: bool = True


class AntiPatternEngine:
    def __init__(
        self,
        game_state: GameState,
        ui_state: dict[str, Any],
        seed: int | None = None,
    ):
        self.game_state = game_state
        self.ui_state = ui_state
        self.random = Random(seed)

        self.patterns: list[AntiPattern] = []
        self.active_effects: list[Effect] = []
        self.trigger_context = TriggerContext(game_state=game_state, random=self.random)
        self.effect_context = EffectContext(
            game_state=game_state, ui_state=ui_state, random=self.random
        )

        self.glitch_engine = GlitchEngine(intensity=0.3, random=self.random)
        self.message_generator = FakeMessageGenerator(random=self.random)
        self.message_scheduler = MessageScheduler(
            self.message_generator, random=self.random
        )

        self.enabled = True
        self.tick_count = 0

    def add_pattern(
        self, pattern_id: str, trigger: Trigger, effect: Effect, cooldown: int = 0
    ) -> None:
        pattern = AntiPattern(
            id=pattern_id, trigger=trigger, effect=effect, cooldown=cooldown
        )
        self.patterns.append(pattern)

    def load_from_config(self, config_path: str) -> None:
        parser = configparser.ConfigParser()
        parser.read(config_path)

        if "global" in parser.sections():
            self.enabled = parser["global"].getboolean("enabled", True)

        for section in parser.sections():
            if section.startswith("pattern_"):
                self._load_pattern(parser[section])

    def _load_pattern(self, config_section) -> None:
        pattern_id = config_section.name[8:]

        trigger_config = {
            "id": f"{pattern_id}_trigger",
            "type": config_section.get("trigger_type"),
        }

        for key in config_section:
            if key.startswith("trigger_"):
                trigger_config[key[8:]] = self._parse_value(config_section[key])

        effect_config = {
            "id": f"{pattern_id}_effect",
            "type": config_section.get("effect_type"),
        }

        for key in config_section:
            if key.startswith("effect_"):
                effect_config[key[7:]] = self._parse_value(config_section[key])

        trigger = TriggerFactory.from_config(trigger_config)
        effect = EffectFactory.from_config(effect_config)
        cooldown = int(config_section.get("cooldown", 0))

        self.add_pattern(pattern_id, trigger, effect, cooldown)

    def _parse_value(self, value: str) -> Any:
        value = value.strip()

        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def increment_counter(self, counter_name: str, amount: int = 1) -> None:
        current = self.trigger_context.counters.get(counter_name, 0)
        self.trigger_context.counters[counter_name] = current + amount

    def trigger_event(self, event_name: str) -> None:
        self.trigger_context.events[event_name] = self.tick_count

    def clear_event(self, event_name: str) -> None:
        self.trigger_context.events.pop(event_name, None)

    def update(self) -> None:
        if not self.enabled:
            return

        self.tick_count += 1

        self._update_active_effects()
        self._check_triggers()
        self._update_cooldowns()

        fake_messages = self.message_scheduler.tick()
        if fake_messages:
            self.ui_state.setdefault("fake_messages", []).extend(
                [{"type": msg.message_type, "text": msg.text} for msg in fake_messages]
            )

    def _update_active_effects(self) -> None:
        for effect in list(self.active_effects):
            effect.tick()
            if not effect.is_active():
                effect.revert(self.effect_context)
                self.active_effects.remove(effect)

    def _check_triggers(self) -> None:
        for pattern in self.patterns:
            if not pattern.enabled or pattern.remaining_cooldown > 0:
                continue

            if pattern.trigger.should_activate(self.trigger_context):
                self._activate_pattern(pattern)

    def _activate_pattern(self, pattern: AntiPattern) -> None:
        if pattern.effect not in self.active_effects:
            pattern.effect.apply(self.effect_context)
            pattern.trigger.on_activate()
            pattern.remaining_cooldown = pattern.cooldown
            self.active_effects.append(pattern.effect)
        else:
            pattern.remaining_cooldown = pattern.cooldown

    def _update_cooldowns(self) -> None:
        for pattern in self.patterns:
            if pattern.remaining_cooldown > 0:
                pattern.remaining_cooldown -= 1

    def apply_glitch(self, text: str) -> str:
        return self.glitch_engine.process_text(text)

    def enable_glitches(self, intensity: float = 0.3) -> None:
        self.glitch_engine.set_intensity(intensity)
        self.glitch_engine.enable()

    def disable_glitches(self) -> None:
        self.glitch_engine.disable()

    def schedule_fake_message(self, delay: int, category: str = "generic") -> None:
        self.message_scheduler.schedule_message(delay, category)

    def get_active_effect_ids(self) -> list[str]:
        return [effect.id for effect in self.active_effects]

    def is_effect_active(self, effect_id: str) -> bool:
        return any(effect.id == effect_id for effect in self.active_effects)

    # Global enable/disable methods
    def enable(self) -> None:
        """Enable the entire anti-pattern engine."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the entire anti-pattern engine."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if the anti-pattern engine is globally enabled."""
        return self.enabled

    def toggle(self) -> bool:
        """Toggle the anti-pattern engine on/off. Returns new state."""
        self.enabled = not self.enabled
        return self.enabled

    # Individual pattern enable/disable methods
    def enable_pattern(self, pattern_id: str) -> bool:
        """Enable a specific anti-pattern by ID.

        Args:
            pattern_id: The ID of the pattern to enable

        Returns:
            True if pattern was found and enabled, False otherwise
        """
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                pattern.enabled = True
                return True
        return False

    def disable_pattern(self, pattern_id: str) -> bool:
        """Disable a specific anti-pattern by ID.

        Args:
            pattern_id: The ID of the pattern to disable

        Returns:
            True if pattern was found and disabled, False otherwise
        """
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                pattern.enabled = False
                return True
        return False

    def toggle_pattern(self, pattern_id: str) -> bool | None:
        """Toggle a specific anti-pattern on/off.

        Args:
            pattern_id: The ID of the pattern to toggle

        Returns:
            New enabled state if pattern found, None if pattern not found
        """
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                pattern.enabled = not pattern.enabled
                return pattern.enabled
        return None

    def is_pattern_enabled(self, pattern_id: str) -> bool:
        """Check if a specific pattern is enabled.

        Args:
            pattern_id: The ID of the pattern to check

        Returns:
            True if pattern is enabled, False if disabled or not found
        """
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                return pattern.enabled
        return False

    def get_pattern_ids(self) -> list[str]:
        """Get list of all pattern IDs."""
        return [pattern.id for pattern in self.patterns]

    def get_enabled_pattern_ids(self) -> list[str]:
        """Get list of currently enabled pattern IDs."""
        return [pattern.id for pattern in self.patterns if pattern.enabled]

    def get_disabled_pattern_ids(self) -> list[str]:
        """Get list of currently disabled pattern IDs."""
        return [pattern.id for pattern in self.patterns if not pattern.enabled]

    def enable_all_patterns(self) -> None:
        """Enable all anti-patterns."""
        for pattern in self.patterns:
            pattern.enabled = True

    def disable_all_patterns(self) -> None:
        """Disable all anti-patterns."""
        for pattern in self.patterns:
            pattern.enabled = False

    def get_pattern_info(self, pattern_id: str) -> dict | None:
        """Get detailed information about a specific pattern.

        Args:
            pattern_id: The ID of the pattern to query

        Returns:
            Dictionary with pattern info, or None if not found
        """
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                return {
                    "id": pattern.id,
                    "enabled": pattern.enabled,
                    "cooldown": pattern.cooldown,
                    "remaining_cooldown": pattern.remaining_cooldown,
                    "trigger_type": type(pattern.trigger).__name__,
                    "effect_type": type(pattern.effect).__name__,
                    "trigger_activated_count": pattern.trigger.activated_count,
                }
        return None
