# Anti-Pattern Engine Developer Reference

## Overview

The anti-pattern engine provides a system for creating unpredictable, frustrating, or humorous UI behaviors that enhance the game's satirical nature. Anti-patterns consist of triggers (conditions that activate them) and effects (what happens when they activate).

## Architecture

```
AntiPatternEngine
├── Global enable/disable state
├── List of AntiPattern instances
│   ├── id: Unique identifier
│   ├── trigger: Condition that activates the pattern
│   ├── effect: What happens when activated
│   ├── cooldown: Ticks before can trigger again
│   └── enabled: Individual enable/disable flag
└── Active effects being applied
```

## Global Engine Control

### Enable/Disable Entire Engine

```python
# Enable the entire anti-pattern engine
engine.enable()

# Disable the entire anti-pattern engine (all patterns stop triggering)
engine.disable()

# Check if engine is enabled
is_enabled = engine.is_enabled()  # Returns: bool

# Toggle engine on/off
new_state = engine.toggle()  # Returns: bool (new state)
```

**Example Use Case:**
```python
# Allow player to disable anti-patterns via settings menu
if player_selected_disable_antipatterns:
    engine.disable()
    print("Anti-patterns disabled. Playing in peace mode.")
```

## Individual Pattern Control

### Enable/Disable Specific Patterns

```python
# Enable a specific pattern by ID
success = engine.enable_pattern("hide_on_midgame")  # Returns: bool

# Disable a specific pattern by ID
success = engine.disable_pattern("shuffle_chaos")  # Returns: bool

# Toggle a specific pattern
new_state = engine.toggle_pattern("random_glitch")  # Returns: bool | None

# Check if a pattern is enabled
is_enabled = engine.is_pattern_enabled("hide_on_midgame")  # Returns: bool
```

**Example Use Case:**
```python
# Disable specific annoying patterns during tutorial
if in_tutorial:
    engine.disable_pattern("disable_input_frustration")
    engine.disable_pattern("shuffle_chaos")
```

### Bulk Operations

```python
# Enable all patterns at once
engine.enable_all_patterns()

# Disable all patterns at once
engine.disable_all_patterns()
```

**Example Use Case:**
```python
# Progressive difficulty: enable patterns gradually
if player_progress < 20:
    engine.disable_all_patterns()
elif player_progress < 50:
    engine.enable_pattern("random_glitch")
    engine.enable_pattern("fake_error_milestone")
else:
    engine.enable_all_patterns()  # Full chaos mode
```

## Query Methods

### Get Pattern Information

```python
# Get all pattern IDs
all_patterns = engine.get_pattern_ids()
# Returns: ['hide_on_midgame', 'shuffle_chaos', 'random_glitch', ...]

# Get only enabled pattern IDs
enabled = engine.get_enabled_pattern_ids()
# Returns: ['random_glitch', 'fake_error_milestone']

# Get only disabled pattern IDs
disabled = engine.get_disabled_pattern_ids()
# Returns: ['hide_on_midgame', 'shuffle_chaos']

# Get detailed info about a specific pattern
info = engine.get_pattern_info("hide_on_midgame")
# Returns: {
#     "id": "hide_on_midgame",
#     "enabled": True,
#     "cooldown": 25,
#     "remaining_cooldown": 5,
#     "trigger_type": "ProgressTrigger",
#     "effect_type": "HideSettingEffect",
#     "trigger_activated_count": 2
# }
```

**Example Use Case:**
```python
# Debug menu showing anti-pattern status
def show_antipattern_debug():
    print(f"Engine enabled: {engine.is_enabled()}")
    print(f"\nEnabled patterns ({len(engine.get_enabled_pattern_ids())}):")
    for pattern_id in engine.get_enabled_pattern_ids():
        info = engine.get_pattern_info(pattern_id)
        print(f"  - {pattern_id}: {info['trigger_type']} → {info['effect_type']}")
        print(f"    Activated: {info['trigger_activated_count']} times")
```

## Available Triggers

### CounterTrigger
Activates when a counter reaches a threshold.

```python
from src.anti_patterns.triggers import CounterTrigger

trigger = CounterTrigger("my_trigger", "clicks", 50)
# Activates when "clicks" counter >= 50
```

**Config Format:**
```ini
trigger_type = counter
trigger_counter = clicks
trigger_threshold = 50
```

### RandomTrigger
Activates randomly with a given probability each update.

```python
from src.anti_patterns.triggers import RandomTrigger

trigger = RandomTrigger("my_trigger", 0.05)
# 5% chance to activate each update
```

**Config Format:**
```ini
trigger_type = random
trigger_probability = 0.05
```

### ProgressTrigger
Activates when game progress is within a range.

```python
from src.anti_patterns.triggers import ProgressTrigger

trigger = ProgressTrigger("my_trigger", 40.0, 70.0)
# Activates when player has enabled 40-70% of settings
```

**Config Format:**
```ini
trigger_type = progress
trigger_min_progress = 40
trigger_max_progress = 70
```

### IntervalTrigger
Activates every N increments of a counter.

```python
from src.anti_patterns.triggers import IntervalTrigger

trigger = IntervalTrigger("my_trigger", "ui_renders", 20)
# Activates every 20 UI renders
```

**Config Format:**
```ini
trigger_type = interval
trigger_counter = ui_renders
trigger_interval = 20
```

### EventTrigger
Activates when a specific event is triggered.

```python
from src.anti_patterns.triggers import EventTrigger

trigger = EventTrigger("my_trigger", "menu_enter")
# Activates when "menu_enter" event occurs

# Trigger the event elsewhere in code:
engine.trigger_event("menu_enter")
```

**Config Format:**
```ini
trigger_type = event
trigger_event = menu_enter
```

## Available Effects

### HideSettingEffect
Temporarily hides settings matching a pattern.

```python
from src.anti_patterns.effects import HideSettingEffect

effect = HideSettingEffect("my_effect", "audio", duration=5)
# Hides all settings with "audio" in their ID for 5 ticks
```

**Config Format:**
```ini
effect_type = hide_setting
effect_pattern = audio
effect_duration = 5
```

### ShuffleMenuEffect
Randomizes the order of settings in all menus.

```python
from src.anti_patterns.effects import ShuffleMenuEffect

effect = ShuffleMenuEffect("my_effect", duration=4)
# Shuffles menu settings for 4 ticks
```

**Config Format:**
```ini
effect_type = shuffle_menu
effect_duration = 4
```

### FakeErrorEffect
Displays a fake error message.

```python
from src.anti_patterns.effects import FakeErrorEffect

effect = FakeErrorEffect("my_effect", "System resources exhausted")
# Shows fake error message once
```

**Config Format:**
```ini
effect_type = fake_error
effect_message = System resources exhausted
```

### FreezeProgressEffect
Prevents progress bar from updating (visual only).

```python
from src.anti_patterns.effects import FreezeProgressEffect

effect = FreezeProgressEffect("my_effect", duration=12)
# Freezes progress display for 12 ticks
```

**Config Format:**
```ini
effect_type = freeze_progress
effect_duration = 12
```

### ReverseProgressEffect
Makes progress bar go backwards (visual only).

```python
from src.anti_patterns.effects import ReverseProgressEffect

effect = ReverseProgressEffect("my_effect", duration=6)
# Reverses progress display for 6 ticks
```

**Config Format:**
```ini
effect_type = reverse_progress
effect_duration = 6
```

### GlitchTextEffect
Corrupts text display with random characters.

```python
from src.anti_patterns.effects import GlitchTextEffect

effect = GlitchTextEffect("my_effect", intensity=0.35, duration=2)
# Glitches text at 35% intensity for 2 ticks
```

**Config Format:**
```ini
effect_type = glitch_text
effect_intensity = 0.35
effect_duration = 2
```

### DisableInputEffect
Temporarily ignores player input.

```python
from src.anti_patterns.effects import DisableInputEffect

effect = DisableInputEffect("my_effect", duration=2)
# Disables input for 2 ticks
```

**Config Format:**
```ini
effect_type = disable_input
effect_duration = 2
```

### BlinkSettingEffect
Makes a specific setting blink/flash.

```python
from src.anti_patterns.effects import BlinkSettingEffect

effect = BlinkSettingEffect("my_effect", "setting_123", duration=8)
# Makes setting blink for 8 ticks
```

**Config Format:**
```ini
effect_type = blink_setting
effect_setting = setting_123
effect_duration = 8
```

### SwapSettingsEffect
Swaps the labels of two settings.

```python
from src.anti_patterns.effects import SwapSettingsEffect

effect = SwapSettingsEffect("my_effect", "setting_a", "setting_b", duration=5)
# Swaps labels for 5 ticks
```

**Config Format:**
```ini
effect_type = swap_settings
effect_setting_a = setting_a
effect_setting_b = setting_b
effect_duration = 5
```

## Configuration File Format

Anti-patterns can be loaded from an INI file (`config/anti_patterns.ini`):

```ini
[global]
enabled = true

[pattern_hide_on_midgame]
trigger_type = progress
trigger_min_progress = 40
trigger_max_progress = 70
effect_type = hide_setting
effect_pattern = audio
effect_duration = 5
cooldown = 25

[pattern_shuffle_chaos]
trigger_type = interval
trigger_counter = ui_renders
trigger_interval = 20
effect_type = shuffle_menu
effect_duration = 4
cooldown = 15

[pattern_random_glitch]
trigger_type = random
trigger_probability = 0.08
effect_type = glitch_text
effect_intensity = 0.35
effect_duration = 2
cooldown = 8
```

### Loading from Config

```python
engine.load_from_config("config/anti_patterns.ini")
```

The `[global]` section controls the initial enabled state of the entire engine.

## Programmatic Pattern Creation

### Creating Patterns Dynamically

```python
from src.anti_patterns.engine import AntiPatternEngine
from src.anti_patterns.triggers import ProgressTrigger
from src.anti_patterns.effects import ShuffleMenuEffect

# Initialize engine
engine = AntiPatternEngine(game_state, ui_state, seed=42)

# Create pattern components
trigger = ProgressTrigger("late_game_trigger", 75.0, 95.0)
effect = ShuffleMenuEffect("chaos_effect", duration=5)

# Add pattern to engine
engine.add_pattern(
    pattern_id="late_game_chaos",
    trigger=trigger,
    effect=effect,
    cooldown=30
)
```

### Complete Example: Dynamic Difficulty

```python
class AdaptiveDifficulty:
    def __init__(self, engine: AntiPatternEngine):
        self.engine = engine

    def update_based_on_player_skill(self, player_struggles: int):
        """Adjust anti-patterns based on player performance."""

        if player_struggles > 10:
            # Player is struggling, reduce frustration
            self.engine.disable_pattern("disable_input_frustration")
            self.engine.disable_pattern("shuffle_chaos")
            print("Anti-patterns reduced due to player difficulty")

        elif player_struggles < 3:
            # Player is doing too well, increase challenge
            self.engine.enable_all_patterns()
            print("Maximum chaos engaged!")

        else:
            # Balanced difficulty
            enabled = self.engine.get_enabled_pattern_ids()
            if len(enabled) < 4:
                # Enable a few more patterns
                disabled = self.engine.get_disabled_pattern_ids()
                if disabled:
                    self.engine.enable_pattern(disabled[0])
```

## Counters and Events

### Incrementing Counters

Counters are used by CounterTrigger and IntervalTrigger:

```python
# Increment a counter (used for triggering patterns)
engine.increment_counter("clicks")
engine.increment_counter("settings_enabled")
engine.increment_counter("menu_visits")
engine.increment_counter("ui_renders")

# Increment by custom amount
engine.increment_counter("points", amount=10)
```

### Triggering Events

Events are used by EventTrigger:

```python
# Trigger an event
engine.trigger_event("boss_defeated")
engine.trigger_event("secret_found")
engine.trigger_event("menu_opened")

# Clear an event (stops EventTriggers from activating)
engine.clear_event("menu_opened")
```

## Glitch System

The engine includes a separate glitch system for text corruption:

```python
# Enable glitches with intensity
engine.enable_glitches(intensity=0.3)  # 30% of characters affected

# Disable glitches
engine.disable_glitches()

# Apply glitch effect to text
corrupted = engine.apply_glitch("Normal text")  # Returns: "N̴o̷r̸m̵a̶l̷ ̴t̶e̸x̷t̴"
```

## Fake Message System

Schedule fake error/warning messages:

```python
# Schedule a fake message to appear after delay
engine.schedule_fake_message(delay=50, category="error")
engine.schedule_fake_message(delay=100, category="warning")

# Messages are automatically added to ui_state["fake_messages"]
```

## Active Effects

### Checking Active Effects

```python
# Get list of active effect IDs
active = engine.get_active_effect_ids()
# Returns: ['effect1', 'effect2']

# Check if specific effect is active
is_active = engine.is_effect_active("glitch_effect")
# Returns: bool
```

**Example Use Case:**
```python
# Only show certain UI elements when not glitching
if not engine.is_effect_active("glitch_text_effect"):
    render_detailed_stats()
```

## Update Loop

The engine must be updated each frame:

```python
# In your main game loop
def game_loop():
    while running:
        # ... game logic ...

        # Update anti-pattern engine
        engine.update()

        # ... render ...
```

The `update()` method:
1. Checks all triggers
2. Activates patterns whose triggers fire
3. Updates active effects
4. Handles cooldowns
5. Generates scheduled fake messages

## Best Practices

### 1. Use Cooldowns Appropriately
```python
# Short cooldown for minor annoyances
engine.add_pattern("minor_glitch", trigger, effect, cooldown=5)

# Long cooldown for major disruptions
engine.add_pattern("major_chaos", trigger, effect, cooldown=50)
```

### 2. Balance Frustration with Fun
```python
# Disable the most frustrating patterns by default
engine.disable_pattern("disable_input_frustration")
engine.disable_pattern("reverse_progress_cruelty")

# Let player discover them later or enable via difficulty settings
```

### 3. Provide Player Control
```python
# Always allow players to disable anti-patterns
if settings.get("easy_mode"):
    engine.disable()

# Or granular control
if settings.get("disable_input_blocks"):
    engine.disable_pattern("disable_input_frustration")
```

### 4. Debug Visibility
```python
# Add debug command to inspect patterns
def debug_antipatterns():
    print(f"Engine: {'ON' if engine.is_enabled() else 'OFF'}")
    print(f"Active effects: {engine.get_active_effect_ids()}")
    print(f"Enabled patterns: {engine.get_enabled_pattern_ids()}")

    for pattern_id in engine.get_pattern_ids():
        info = engine.get_pattern_info(pattern_id)
        status = "✓" if info["enabled"] else "✗"
        print(f"{status} {pattern_id}: {info['trigger_activated_count']} activations")
```

### 5. Progressive Activation
```python
# Start gentle, increase chaos over time
class ProgressiveAntiPatterns:
    def __init__(self, engine: AntiPatternEngine):
        self.engine = engine
        self.phase = 0

    def advance_phase(self):
        self.phase += 1

        if self.phase == 1:
            # Phase 1: Just cosmetic
            self.engine.enable_pattern("random_glitch")

        elif self.phase == 2:
            # Phase 2: Mild confusion
            self.engine.enable_pattern("shuffle_chaos")
            self.engine.enable_pattern("hide_on_midgame")

        elif self.phase == 3:
            # Phase 3: Full chaos
            self.engine.enable_all_patterns()
```

## Common Patterns

### Player Frustration Meter
```python
class FrustrationMeter:
    def __init__(self, engine: AntiPatternEngine):
        self.engine = engine
        self.frustration = 0

    def on_player_mistake(self):
        self.frustration += 1

        # More mistakes = more chaos
        if self.frustration > 5:
            self.engine.enable_pattern("shuffle_chaos")
        if self.frustration > 10:
            self.engine.enable_pattern("disable_input_frustration")

    def on_player_success(self):
        self.frustration = max(0, self.frustration - 1)

        if self.frustration < 3:
            self.engine.disable_pattern("disable_input_frustration")
```

### Time-Based Escalation
```python
def update_time_based_patterns(engine: AntiPatternEngine, elapsed_seconds: float):
    """Enable more patterns as time passes."""

    if elapsed_seconds > 60:
        engine.enable_pattern("random_glitch")

    if elapsed_seconds > 300:  # 5 minutes
        engine.enable_pattern("shuffle_chaos")

    if elapsed_seconds > 600:  # 10 minutes
        engine.enable_all_patterns()
```

### Achievement-Based Unlocks
```python
def on_achievement_unlocked(engine: AntiPatternEngine, achievement_id: str):
    """Unlock special anti-patterns for achievements."""

    if achievement_id == "speed_runner":
        # Punish speedrunners with extra chaos
        engine.enable_pattern("disable_input_frustration")

    elif achievement_id == "completionist":
        # Reward completionists by disabling annoyances
        engine.disable_all_patterns()
```

## Summary

The anti-pattern engine provides fine-grained control over game behavior disruptions:

- **Global control**: Enable/disable entire engine
- **Pattern control**: Enable/disable individual patterns
- **Query system**: Inspect pattern states and info
- **Flexible triggers**: Progress, counters, random, intervals, events
- **Varied effects**: Hide, shuffle, glitch, freeze, disable input, fake errors
- **Configuration**: Load from files or create programmatically
- **Dynamic adjustment**: Adapt patterns based on player behavior

Use these tools to create a dynamic, unpredictable experience that enhances the satirical nature of the game!
