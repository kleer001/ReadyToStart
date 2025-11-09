# Ready to Start - Phase 5 Detailed Roadmap

## Phase 5: Anti-Patterns

### 5.1 Trigger System
**Goal:** Detect when to activate anti-patterns

**Files:**
- `anti_patterns/triggers.py` ✓
- `tests/test_triggers.py`

**Implementation:**
```python
class Trigger(ABC):
    def should_activate(self, context: TriggerContext) -> bool
    def on_activate(self) -> None

class CounterTrigger(Trigger)
class RandomTrigger(Trigger)
class EventTrigger(Trigger)
class ProgressTrigger(Trigger)
class IntervalTrigger(Trigger)
class CompositeTrigger(Trigger)
class OnceTrigger(Trigger)
```

**Trigger Types:**
- **CounterTrigger**: Activate when counter reaches threshold (e.g., clicks > 50)
- **RandomTrigger**: Activate based on probability (e.g., 30% chance per tick)
- **EventTrigger**: Activate when specific event occurs
- **ProgressTrigger**: Activate within progress range (e.g., 40-60%)
- **IntervalTrigger**: Activate every N ticks
- **CompositeTrigger**: Combine multiple triggers with AND/OR logic
- **OnceTrigger**: Wrap any trigger to fire only once

**Testing:**
- Counter threshold detection
- Random probability distribution
- Event firing
- Progress range checking
- Interval timing
- Composite logic (AND/OR)
- Once-only behavior

**Procedural:** ✓ Configurable via INI

---

### 5.2 Effect System
**Goal:** Apply anti-patterns to game and UI

**Files:**
- `anti_patterns/effects.py` ✓
- `tests/test_effects.py`

**Implementation:**
```python
class Effect(ABC):
    def apply(self, context: EffectContext) -> None
    def revert(self, context: EffectContext) -> None
    def tick(self) -> None

class HideSettingEffect(Effect)
class ShuffleMenuEffect(Effect)
class FakeErrorEffect(Effect)
class FreezeProgressEffect(Effect)
class ReverseProgressEffect(Effect)
class BlinkSettingEffect(Effect)
class SwapSettingsEffect(Effect)
class GlitchTextEffect(Effect)
class DisableInputEffect(Effect)
```

**Effect Types:**
- **HideSettingEffect**: Temporarily hide settings matching pattern
- **ShuffleMenuEffect**: Randomize setting order in menus
- **FakeErrorEffect**: Display fake error messages
- **FreezeProgressEffect**: Freeze progress bar display
- **ReverseProgressEffect**: Make progress bar go backwards
- **BlinkSettingEffect**: Change setting state to BLINKING
- **SwapSettingsEffect**: Swap labels between two settings
- **GlitchTextEffect**: Apply visual glitches to UI text
- **DisableInputEffect**: Temporarily disable user input

**Features:**
- Duration-based effects with automatic revert
- Clean state management
- Composable effects
- UI state isolation

**Testing:**
- Effect application and reversion
- Duration tracking
- State restoration
- Multiple concurrent effects
- UI state isolation

**Procedural:** ✓ Configurable via INI

---

### 5.3 Fake Message Generator
**Goal:** Create convincing fake error messages

**Files:**
- `anti_patterns/messages.py` ✓
- `tests/test_messages.py`

**Implementation:**
```python
class FakeMessageGenerator:
    def load_from_config(self, config_path: str)
    def generate(self, category: str) -> FakeMessage
    def generate_system_message() -> FakeMessage
    def generate_permission_error() -> FakeMessage

class MessageScheduler:
    def schedule_message(self, delay: int, category: str)
    def schedule_random(self, min_delay: int, max_delay: int, category: str)
    def tick() -> List[FakeMessage]
```

**Message Categories:**
- Generic system errors
- Permission denied errors
- Dependency errors
- Resource errors
- Network errors
- Configuration errors

**Template System:**
- Mad Libs style templates with {placeholders}
- Component pools for variety
- Random selection for unpredictability
- Scheduled delivery for realism

**Sample Templates:**
```
"Cannot {action}: {resource} is {state}"
"Permission denied: {operation} requires {permission}"
"Dependency error: {setting_a} conflicts with {setting_b}"
```

**Testing:**
- Template parsing
- Component substitution
- Message scheduling
- Tick-based delivery
- Random generation

**Procedural:** ✓ Templates from config

---

### 5.4 Glitch Engine
**Goal:** Apply visual corruption to text

**Files:**
- `anti_patterns/glitches.py` ✓
- `tests/test_glitches.py`

**Implementation:**
```python
class Glitch(ABC):
    def apply(self, text: str, random: Random) -> str

class CharacterCorruptionGlitch(Glitch)
class CharacterDuplicationGlitch(Glitch)
class CharacterDeletionGlitch(Glitch)
class ColorGlitch(Glitch)
class OffsetGlitch(Glitch)

class GlitchEngine:
    def enable() -> None
    def set_intensity(intensity: float) -> None
    def process_text(text: str) -> str
```

**Glitch Types:**
- **CharacterCorruption**: Replace chars with ░▒▓█▄▀■□▪▫
- **CharacterDuplication**: Duplicate random characters
- **CharacterDeletion**: Remove random characters
- **ColorGlitch**: Add random ANSI color codes
- **OffsetGlitch**: Add random spacing

**Features:**
- Intensity-based probability
- Composable glitch application
- Non-destructive (original text preserved)
- Deterministic with seed support

**Testing:**
- Individual glitch types
- Intensity scaling
- Composite application
- Edge cases (empty strings, special chars)

**Procedural:** Runtime only

---

### 5.5 Anti-Pattern Orchestration Engine
**Goal:** Coordinate all anti-patterns

**Files:**
- `anti_patterns/engine.py` ✓
- `tests/test_engine.py`

**Implementation:**
```python
class AntiPatternEngine:
    def __init__(self, game_state: GameState, ui_state: Dict)
    def load_from_config(self, config_path: str)
    def add_pattern(self, pattern_id: str, trigger: Trigger, effect: Effect, cooldown: int)
    def increment_counter(self, counter_name: str)
    def trigger_event(self, event_name: str)
    def update() -> None
    def apply_glitch(self, text: str) -> str
```

**Core Responsibilities:**
- Manage trigger-effect pairs (AntiPattern)
- Track cooldowns to prevent spam
- Maintain active effects list
- Coordinate with GlitchEngine
- Integrate MessageScheduler
- Provide counter/event API for UI

**Update Cycle:**
1. Tick all active effects
2. Revert expired effects
3. Check all triggers
4. Activate matching patterns (respecting cooldowns)
5. Deliver scheduled messages
6. Update cooldowns

**Integration Points:**
- GameState for setting manipulation
- ui_state dict for UI coordination
- Random for determinism
- Config files for patterns

**Testing:**
- Pattern activation
- Cooldown enforcement
- Effect lifecycle
- Message delivery
- Counter/event tracking
- Config loading

**Procedural:** ✓ Patterns from config

---

## Configuration Files

### config/anti_patterns.ini
**Purpose:** Define trigger-effect pairs

```ini
[global]
enabled = true

[pattern_hide_on_progress]
trigger_type = progress
trigger_min_progress = 50
trigger_max_progress = 70
effect_type = hide_setting
effect_pattern = audio
effect_duration = 5
cooldown = 20

[pattern_shuffle_frequently]
trigger_type = interval
trigger_counter = ui_renders
trigger_interval = 15
effect_type = shuffle_menu
effect_duration = 3
cooldown = 10

[pattern_random_glitch]
trigger_type = random
trigger_probability = 0.05
effect_type = glitch_text
effect_intensity = 0.4
effect_duration = 2
cooldown = 5

[pattern_fake_error_on_click]
trigger_type = counter
trigger_counter = clicks
trigger_threshold = 25
effect_type = fake_error
effect_message = Cannot enable: System resources exhausted
cooldown = 30
```

### config/fake_messages.ini
**Purpose:** Message templates and components

```ini
[template_generic]
messages =
    Cannot {action}: {resource} is {state}
    Error {code}: {operation} failed
    {resource} unavailable: {reason}
    Operation denied: {permission} required

[template_system]
messages =
    System error {code}: Please restart
    Critical failure in {component}
    {resource} has stopped responding

[template_permission]
messages =
    Access denied: {operation} requires {permission}
    Insufficient privileges for {action}
    {resource} is locked by {process}

[template_dependency]
messages =
    Dependency conflict: {setting_a} requires {setting_b}
    Cannot enable {setting}: {dependency} must be configured first
    Circular dependency detected

[components_action]
values =
    enable setting
    modify value
    access resource
    apply changes
    save configuration

[components_resource]
values =
    audio device
    graphics adapter
    network interface
    configuration file
    system memory

[components_state]
values =
    unavailable
    locked
    in use
    corrupted
    uninitialized

[components_code]
values =
    0x80004005
    0xC0000005
    0x800706BE
    ERR_TIMEOUT
    ERR_ACCESS_DENIED
```

---

## Helper Scripts

### Anti-Pattern Tester
**File:** `scripts/test_anti_patterns.py`
```python
#!/usr/bin/env python3
from generation.pipeline import GenerationPipeline
from anti_patterns.engine import AntiPatternEngine

def test_anti_patterns():
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=42)

    ui_state = {}
    engine = AntiPatternEngine(state, ui_state, seed=42)
    engine.load_from_config("config/anti_patterns.ini")

    print("Testing anti-pattern triggers...")

    for i in range(100):
        engine.increment_counter("clicks", 1)
        engine.update()

        if i % 10 == 0:
            print(f"Tick {i}: Active effects = {engine.get_active_effect_ids()}")

    print(f"\nFinal active effects: {engine.get_active_effect_ids()}")
    print(f"UI state modifications: {list(ui_state.keys())}")

if __name__ == "__main__":
    test_anti_patterns()
```

---

## Libraries Summary

**Core:**
- abc (abstract base classes)
- dataclasses (clean data structures)
- random (deterministic randomness)
- configparser (INI loading)

**No new external dependencies**

---

## Phase 5 Completion Criteria

- [x] Trigger system with 7 trigger types
- [x] Effect system with 9 effect types
- [x] Fake message generator with templates
- [x] Message scheduler with tick-based delivery
- [x] Glitch engine with 5 glitch types
- [x] Anti-pattern orchestration engine
- [ ] Configuration files (anti_patterns.ini, fake_messages.ini)
- [ ] Integration with UI loop
- [ ] 80%+ test coverage for all modules
- [ ] Helper scripts functional
- [ ] All code passes linting (ruff)
- [ ] All code formatted (black)

---

## Implementation Notes

**Design Principles Applied:**

1. **Single Responsibility:** Each class has one clear purpose
   - Triggers detect conditions
   - Effects apply changes
   - Engine orchestrates
   - Generator creates messages
   - Glitches corrupt text

2. **Open/Closed:** Easy to extend
   - Add new trigger types by subclassing Trigger
   - Add new effects by subclassing Effect
   - Factories handle instantiation

3. **Liskov Substitution:** All triggers/effects interchangeable
   - Common interfaces
   - Consistent lifecycle
   - No special cases

4. **Interface Segregation:** Minimal interfaces
   - Trigger: just should_activate()
   - Effect: just apply() and revert()
   - No bloated base classes

5. **Dependency Inversion:** Depend on abstractions
   - Engine depends on Trigger/Effect interfaces
   - Not concrete implementations
   - Configurable composition

**KISS Applied:**
- Simple state management
- No complex state machines
- Straightforward tick-based updates
- Clear data flow

**DRY Applied:**
- Factories eliminate duplication
- Base classes share common logic
- Composition over inheritance
- Shared Random instance

---

## Integration Strategy

The AntiPatternEngine integrates into the main UI loop:

```python
# In UILoop.__init__
self.anti_pattern_engine = AntiPatternEngine(
    self.game_state,
    self.ui_state,
    seed=42
)
self.anti_pattern_engine.load_from_config(config_dir / "anti_patterns.ini")

# In UILoop.update_cycle
self.anti_pattern_engine.increment_counter("ui_renders")
self.anti_pattern_engine.update()

# When rendering text
display_text = self.anti_pattern_engine.apply_glitch(text)

# On user actions
self.anti_pattern_engine.increment_counter("clicks")
self.anti_pattern_engine.trigger_event("setting_enabled")
```

No changes required to existing game logic - completely isolated system.
