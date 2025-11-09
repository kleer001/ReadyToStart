# Ready to Start - Phase 5 Detailed Roadmap

## Phase 5: Anti-Patterns (Deception & Frustration)

### 5.1 Unreliable Progress System
**Goal:** Progress bars that lie, backtrack, and spawn children

**Files:**
- `ui/unreliable_progress.py`
- `tests/test_unreliable_progress.py`

**Implementation:**
```python
from typing import List, Optional
from dataclasses import dataclass
import random
import time

@dataclass
class ProgressBehavior:
    """Defines how a progress bar misbehaves"""
    type: str  # "backtrack", "spawn", "stuck", "oscillate", "jump"
    trigger_percent: float  # When to activate behavior
    intensity: float  # How severe the behavior is
    duration: float  # How long it lasts

class UnreliableProgressBar:
    """A progress bar that actively lies"""

    def __init__(self, label: str, behavior: ProgressBehavior):
        self.label = label
        self.behavior = behavior
        self.current_percent = 0.0
        self.visual_percent = 0.0  # What the user sees
        self.children: List['UnreliableProgressBar'] = []
        self.stuck = False
        self.oscillate_direction = 1
        self.last_update = time.time()

    def update(self, real_progress: float):
        """Update based on real progress, but lie about it"""
        self.current_percent = real_progress

        if self.behavior.type == "backtrack":
            if random.random() < 0.1:  # 10% chance per update
                self.visual_percent = max(0, self.visual_percent - random.uniform(5, 20))
            else:
                self.visual_percent = min(99, self.visual_percent + random.uniform(0, 2))

        elif self.behavior.type == "spawn":
            if self.visual_percent >= self.behavior.trigger_percent and not self.children:
                # Spawn 2-4 child progress bars
                num_children = random.randint(2, 4)
                for i in range(num_children):
                    child_behavior = ProgressBehavior(
                        type=random.choice(["stuck", "oscillate", "backtrack"]),
                        trigger_percent=50.0,
                        intensity=0.5,
                        duration=5.0
                    )
                    child = UnreliableProgressBar(
                        f"  Subprocess {i+1}",
                        child_behavior
                    )
                    self.children.append(child)

            # Parent bar waits for children
            if self.children:
                avg_child_progress = sum(c.visual_percent for c in self.children) / len(self.children)
                self.visual_percent = min(self.behavior.trigger_percent + avg_child_progress * 0.4, 99)
            else:
                self.visual_percent = min(99, self.visual_percent + 1)

        elif self.behavior.type == "stuck":
            if self.visual_percent >= self.behavior.trigger_percent:
                self.stuck = True
            if not self.stuck:
                self.visual_percent = min(self.behavior.trigger_percent, self.visual_percent + 1)

        elif self.behavior.type == "oscillate":
            self.visual_percent += self.oscillate_direction * 2
            if self.visual_percent >= 80 or self.visual_percent <= 20:
                self.oscillate_direction *= -1

        elif self.behavior.type == "jump":
            # Suddenly jump to random percentage
            if random.random() < 0.05:
                self.visual_percent = random.uniform(0, 99)
            else:
                self.visual_percent = min(99, self.visual_percent + random.uniform(-1, 3))

    def render(self, width: int = 40) -> str:
        """Render the progress bar"""
        filled = int(width * (self.visual_percent / 100))
        bar = "=" * filled + ">" + " " * (width - filled - 1)
        result = f"{self.label}: [{bar}] {self.visual_percent:.1f}%"

        # Render children
        for child in self.children:
            result += "\n" + child.render(width - 2)

        return result

class ProgressSystemController:
    """Manages multiple unreliable progress bars"""

    def __init__(self):
        self.bars: List[UnreliableProgressBar] = []
        self.active = False

    def add_bar(self, bar: UnreliableProgressBar):
        self.bars.append(bar)

    def show_fake_loading(self, duration: float = 5.0):
        """Show fake loading screen with unreliable bars"""
        self.active = True
        start_time = time.time()

        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            fake_progress = (elapsed / duration) * 100

            # Update all bars
            for bar in self.bars:
                bar.update(fake_progress)

            # Render (in real usage, this would clear screen first)
            output = "\n".join(bar.render() for bar in self.bars)
            print(f"\033[H\033[J{output}")  # Clear and print
            time.sleep(0.1)

        self.active = False

    def load_behaviors_from_config(self, config_path: str):
        """Load progress bar behaviors from INI"""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            if section.startswith("bar_"):
                label = parser[section].get('label', 'Loading')
                behavior_type = parser[section]['type']
                trigger = float(parser[section].get('trigger_percent', 50))
                intensity = float(parser[section].get('intensity', 0.5))
                duration = float(parser[section].get('duration', 5.0))

                behavior = ProgressBehavior(behavior_type, trigger, intensity, duration)
                bar = UnreliableProgressBar(label, behavior)
                self.add_bar(bar)
```

**Sample config/unreliable_progress.ini:**
```ini
[bar_main]
label = Loading Game State
type = spawn
trigger_percent = 40
intensity = 1.0
duration = 10.0

[bar_verify]
label = Verifying Settings
type = backtrack
trigger_percent = 0
intensity = 0.8
duration = 8.0

[bar_optimize]
label = Optimizing Configuration
type = stuck
trigger_percent = 99
intensity = 1.0
duration = 5.0

[bar_quantum]
label = Quantum Menu Stabilization
type = oscillate
trigger_percent = 0
intensity = 0.7
duration = 6.0
```

**Testing:**
- Each behavior type (backtrack, spawn, stuck, oscillate, jump)
- Child bar spawning and rendering
- Visual percentage vs real progress divergence
- Config loading
- Rendering with nested bars

**Procedural:** ✓ Bar behaviors from config

---

### 5.2 Moving UI Elements
**Goal:** Settings that change position when you're not looking

**Files:**
- `ui/moving_elements.py`
- `tests/test_moving_elements.py`

**Implementation:**
```python
from typing import Dict, List, Tuple
import random
import time

class MovingElement:
    """A UI element that changes position"""

    def __init__(self, element_id: str, movement_type: str):
        self.element_id = element_id
        self.movement_type = movement_type  # "shuffle", "swap", "vanish", "duplicate"
        self.original_position = 0
        self.current_position = 0
        self.last_move_time = time.time()
        self.move_cooldown = random.uniform(3.0, 10.0)
        self.visible = True
        self.duplicates = 0

    def should_move(self) -> bool:
        """Check if enough time has passed to move"""
        return time.time() - self.last_move_time > self.move_cooldown

    def move(self, available_positions: List[int]) -> int:
        """Move to a new position"""
        if not self.should_move():
            return self.current_position

        old_position = self.current_position

        if self.movement_type == "shuffle":
            # Move to random position
            if available_positions:
                self.current_position = random.choice(available_positions)

        elif self.movement_type == "swap":
            # Swap with another element (handled by controller)
            pass

        elif self.movement_type == "vanish":
            # Temporarily disappear
            self.visible = not self.visible

        elif self.movement_type == "duplicate":
            # Create duplicates (only one is real)
            if random.random() < 0.3:
                self.duplicates = random.randint(1, 3)
            else:
                self.duplicates = 0

        self.last_move_time = time.time()
        self.move_cooldown = random.uniform(5.0, 15.0)

        return old_position

class MovingElementController:
    """Manages all moving UI elements"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.moving_elements: Dict[str, MovingElement] = {}
        self.last_interaction_time = time.time()
        self.interaction_cooldown = 3.0  # Wait 3s after interaction before moving

    def register_element(self, element_id: str, movement_type: str):
        """Register an element as movable"""
        element = MovingElement(element_id, movement_type)
        self.moving_elements[element_id] = element

    def on_user_interaction(self):
        """Called when user interacts with UI"""
        self.last_interaction_time = time.time()

    def can_move_elements(self) -> bool:
        """Check if enough time has passed since last interaction"""
        return time.time() - self.last_interaction_time > self.interaction_cooldown

    def update(self, current_menu_settings: List[str]) -> Dict[str, int]:
        """Update positions of all moving elements"""
        if not self.can_move_elements():
            return {}

        new_positions = {}
        available_positions = list(range(len(current_menu_settings)))

        # Shuffle movement
        for elem_id, element in self.moving_elements.items():
            if element.movement_type == "shuffle" and elem_id in current_menu_settings:
                old_pos = current_menu_settings.index(elem_id)
                element.current_position = old_pos

                if element.should_move():
                    available = [p for p in available_positions if p != old_pos]
                    element.move(available)
                    new_positions[elem_id] = element.current_position

        # Swap movement (pairs)
        swap_candidates = [
            (id, elem) for id, elem in self.moving_elements.items()
            if elem.movement_type == "swap" and elem.should_move()
        ]

        for i in range(0, len(swap_candidates) - 1, 2):
            elem1_id, elem1 = swap_candidates[i]
            elem2_id, elem2 = swap_candidates[i + 1]

            if elem1_id in current_menu_settings and elem2_id in current_menu_settings:
                pos1 = current_menu_settings.index(elem1_id)
                pos2 = current_menu_settings.index(elem2_id)

                new_positions[elem1_id] = pos2
                new_positions[elem2_id] = pos1

                elem1.last_move_time = time.time()
                elem2.last_move_time = time.time()

        return new_positions

    def reorder_settings(self, settings_list: List[str]) -> List[str]:
        """Reorder settings list based on current positions"""
        result = settings_list.copy()

        for elem_id, element in self.moving_elements.items():
            if elem_id in result:
                current_idx = result.index(elem_id)
                if current_idx != element.current_position:
                    # Move element
                    result.pop(current_idx)
                    result.insert(element.current_position, elem_id)

        return result

    def get_visible_elements(self) -> List[str]:
        """Get list of currently visible elements"""
        visible = []
        for elem_id, element in self.moving_elements.items():
            if element.visible:
                visible.append(elem_id)
        return visible

    def get_duplicated_elements(self) -> Dict[str, int]:
        """Get elements with their duplicate counts"""
        duplicates = {}
        for elem_id, element in self.moving_elements.items():
            if element.duplicates > 0:
                duplicates[elem_id] = element.duplicates
        return duplicates

    def load_from_config(self, config_path: str):
        """Load moving element configuration"""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            if section.startswith("moving_"):
                setting_pattern = parser[section]['pattern']  # e.g., "audio_*"
                movement_type = parser[section]['type']

                # Register matching settings
                for setting_id in self.game_state.settings:
                    if self._matches_pattern(setting_id, setting_pattern):
                        self.register_element(setting_id, movement_type)

    def _matches_pattern(self, setting_id: str, pattern: str) -> bool:
        """Simple pattern matching (supports * wildcard)"""
        if pattern == "*":
            return True
        if "*" in pattern:
            prefix = pattern.split("*")[0]
            return setting_id.startswith(prefix)
        return setting_id == pattern
```

**Sample config/moving_elements.ini:**
```ini
[moving_volume_settings]
pattern = *_volume
type = shuffle

[moving_quality_settings]
pattern = *_quality
type = swap

[moving_advanced_settings]
pattern = *_advanced*
type = vanish

[moving_experimental]
pattern = experimental_*
type = duplicate
```

**Testing:**
- Each movement type (shuffle, swap, vanish, duplicate)
- Interaction cooldown behavior
- Position tracking and reordering
- Visibility toggling
- Pattern matching for config loading

**Procedural:** ✓ Movement behaviors from config

---

### 5.3 Fake System Messages
**Goal:** Misleading error messages and fake system dialogs

**Files:**
- `ui/fake_messages.py`
- `tests/test_fake_messages.py`

**Implementation:**
```python
from typing import List, Optional, Callable
from dataclasses import dataclass
import random
import time

@dataclass
class FakeMessage:
    """A fake system message"""
    text: str
    message_type: str  # "error", "warning", "system", "critical"
    believability: float  # 0.0-1.0, how believable it is
    trigger_condition: Optional[Callable] = None
    shown: bool = False

class FakeMessageGenerator:
    """Generates fake system messages"""

    def __init__(self):
        self.message_templates = {
            "error": [
                "CRITICAL ERROR: {setting} has caused a system instability",
                "Failed to initialize {setting}: Error code 0x{code}",
                "Warning: {setting} conflicts with system configuration",
                "{setting} requires administrator privileges",
                "Unable to apply {setting}: Dependency not found"
            ],
            "warning": [
                "Performance degradation detected in {category}",
                "{setting} may cause unexpected behavior",
                "Recommended to restart after changing {setting}",
                "{count} settings require validation",
                "Configuration drift detected: {count} mismatches"
            ],
            "system": [
                "Updating system registry...",
                "Synchronizing configuration database...",
                "Validating setting dependencies... ({percent}%)",
                "Checking for configuration conflicts...",
                "Rebuilding settings cache..."
            ],
            "critical": [
                "FATAL: Configuration corruption detected",
                "System will restart in {seconds} seconds",
                "Emergency rollback initiated",
                "All settings will be reset to defaults",
                "Contact system administrator immediately"
            ]
        }

        self.active_messages: List[FakeMessage] = []
        self.message_history: List[FakeMessage] = []

    def generate(self, message_type: str, context: dict) -> FakeMessage:
        """Generate a fake message"""
        template = random.choice(self.message_templates[message_type])

        # Fill in template
        text = template
        if "{setting}" in text:
            text = text.replace("{setting}", context.get("setting", "Unknown Setting"))
        if "{category}" in text:
            text = text.replace("{category}", context.get("category", "System"))
        if "{code}" in text:
            text = text.replace("{code}", f"{random.randint(1000, 9999):04X}")
        if "{count}" in text:
            text = text.replace("{count}", str(random.randint(1, 10)))
        if "{percent}" in text:
            text = text.replace("{percent}", str(random.randint(0, 100)))
        if "{seconds}" in text:
            text = text.replace("{seconds}", str(random.randint(3, 10)))

        # Determine believability
        believability = random.uniform(0.3, 0.9)
        if message_type == "critical":
            believability = random.uniform(0.6, 0.95)  # More believable

        return FakeMessage(text, message_type, believability)

    def should_trigger_message(self, game_state) -> bool:
        """Determine if a fake message should appear"""
        # Random chance based on user actions
        if random.random() < 0.05:  # 5% chance
            return True

        # Triggered by specific conditions
        if len(game_state.settings_history) > 0:
            last_change = game_state.settings_history[-1]
            # Higher chance after enabling many settings
            if last_change['state'] == 'enabled':
                if random.random() < 0.1:  # 10% chance
                    return True

        return False

    def create_contextual_message(self, game_state, event_type: str) -> Optional[FakeMessage]:
        """Create a message based on current game state"""
        context = {
            "setting": game_state.current_setting_label,
            "category": game_state.current_menu_category,
        }

        if event_type == "setting_change":
            if random.random() < 0.15:
                return self.generate("error", context)
            elif random.random() < 0.25:
                return self.generate("warning", context)

        elif event_type == "menu_navigate":
            if random.random() < 0.05:
                return self.generate("system", context)

        elif event_type == "rapid_changes":
            # User is changing settings quickly
            if random.random() < 0.3:
                return self.generate("critical", context)

        return None

    def add_scheduled_message(self, delay: float, message_type: str, context: dict):
        """Schedule a fake message to appear after delay"""
        message = self.generate(message_type, context)
        message.trigger_condition = lambda: time.time() > time.time() + delay
        self.active_messages.append(message)

    def get_pending_messages(self) -> List[FakeMessage]:
        """Get messages that should be shown now"""
        pending = []
        remaining = []

        for msg in self.active_messages:
            if msg.trigger_condition is None or msg.trigger_condition():
                if not msg.shown:
                    pending.append(msg)
                    msg.shown = True
                    self.message_history.append(msg)
            else:
                remaining.append(msg)

        self.active_messages = remaining
        return pending

    def load_templates_from_config(self, config_path: str):
        """Load message templates from INI"""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            if section.startswith("template_"):
                msg_type = parser[section]['type']
                templates = parser[section]['messages'].split('\n')
                templates = [t.strip() for t in templates if t.strip()]

                if msg_type not in self.message_templates:
                    self.message_templates[msg_type] = []

                self.message_templates[msg_type].extend(templates)

class FakeDialogSystem:
    """Shows fake modal dialogs"""

    def __init__(self):
        self.active_dialog: Optional[dict] = None

    def show_fake_confirmation(self, title: str, message: str, options: List[str]) -> str:
        """Show a fake confirmation dialog (all options do nothing)"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
        print(f"\n{message}\n")

        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        print("\n" + "=" * 60)

        while True:
            choice = input("\nSelect option (1-{}): ".format(len(options)))
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    # All options do nothing, but pretend they work
                    print(f"\n[System] {options[idx]} - Operation completed.")
                    time.sleep(1)
                    return options[idx]
            except ValueError:
                pass
            print("Invalid option. Try again.")

    def show_fake_loading_dialog(self, message: str, duration: float):
        """Show a fake loading dialog"""
        print(f"\n{message}")

        start = time.time()
        while time.time() - start < duration:
            elapsed = time.time() - start
            percent = min(99, (elapsed / duration) * 100)
            bar = "=" * int(percent / 2)
            print(f"\r[{bar:50s}] {percent:.0f}%", end="", flush=True)
            time.sleep(0.1)

        print(f"\r[{'=' * 50}] 100%")
        print("Complete.\n")
```

**Sample config/fake_messages.ini:**
```ini
[template_errors]
type = error
messages =
    Configuration validation failed for {setting}
    Unable to persist {setting} to disk
    {setting} exceeds maximum allowable value
    Circular dependency detected involving {setting}

[template_warnings]
type = warning
messages =
    {setting} is deprecated and will be removed
    Changes to {setting} require system restart
    {setting} may impact performance

[template_critical]
type = critical
messages =
    ALERT: {setting} has triggered failsafe mechanism
    Configuration rollback required immediately
    System integrity check failed
```

**Testing:**
- Message generation with templates
- Context variable substitution
- Believability scoring
- Conditional triggering
- Dialog display and input handling
- Config template loading

**Procedural:** ✓ Message templates from config

---

### 5.4 UI Glitch System
**Goal:** Visual glitches and rendering artifacts

**Files:**
- `ui/glitch_effects.py`
- `tests/test_glitch_effects.py`

**Implementation:**
```python
import random
import time
from typing import List, Tuple

class GlitchEffect:
    """Base class for visual glitches"""

    def __init__(self, intensity: float = 0.5, duration: float = 1.0):
        self.intensity = intensity  # 0.0-1.0
        self.duration = duration
        self.start_time = time.time()
        self.active = False

    def is_active(self) -> bool:
        """Check if effect is still active"""
        if not self.active:
            return False
        return time.time() - self.start_time < self.duration

    def activate(self):
        """Start the glitch effect"""
        self.active = True
        self.start_time = time.time()

    def apply(self, text: str) -> str:
        """Apply glitch to text (override in subclasses)"""
        return text

class TextCorruptionGlitch(GlitchEffect):
    """Corrupts random characters in text"""

    def apply(self, text: str) -> str:
        if not self.is_active():
            return text

        chars = list(text)
        num_corrupt = int(len(chars) * self.intensity * 0.1)

        corrupt_chars = ['█', '▓', '▒', '░', '�', '@', '#', '$', '%']

        for _ in range(num_corrupt):
            if chars:
                idx = random.randint(0, len(chars) - 1)
                chars[idx] = random.choice(corrupt_chars)

        return ''.join(chars)

class ColorBleedGlitch(GlitchEffect):
    """Adds random ANSI color codes"""

    def apply(self, text: str) -> str:
        if not self.is_active():
            return text

        colors = ['\033[31m', '\033[32m', '\033[33m', '\033[34m',
                  '\033[35m', '\033[36m', '\033[91m', '\033[92m']

        lines = text.split('\n')
        result = []

        for line in lines:
            if random.random() < self.intensity:
                color = random.choice(colors)
                result.append(f"{color}{line}\033[0m")
            else:
                result.append(line)

        return '\n'.join(result)

class PositionShiftGlitch(GlitchEffect):
    """Shifts text position randomly"""

    def apply(self, text: str) -> str:
        if not self.is_active():
            return text

        lines = text.split('\n')
        result = []

        for line in lines:
            if random.random() < self.intensity * 0.5:
                shift = random.randint(-3, 3)
                if shift > 0:
                    line = ' ' * shift + line
                elif shift < 0:
                    line = line[abs(shift):]
            result.append(line)

        return '\n'.join(result)

class DuplicateLineGlitch(GlitchEffect):
    """Duplicates random lines"""

    def apply(self, text: str) -> str:
        if not self.is_active():
            return text

        lines = text.split('\n')
        result = []

        for line in lines:
            result.append(line)
            if random.random() < self.intensity * 0.2:
                # Duplicate this line 1-3 times
                duplicates = random.randint(1, 3)
                for _ in range(duplicates):
                    result.append(line)

        return '\n'.join(result)

class StaticNoiseGlitch(GlitchEffect):
    """Adds static noise lines"""

    def apply(self, text: str) -> str:
        if not self.is_active():
            return text

        lines = text.split('\n')
        result = []

        noise_chars = ['░', '▒', '▓', '█', '·', '∙', '•']

        for line in lines:
            result.append(line)
            if random.random() < self.intensity * 0.15:
                # Insert noise line
                noise_length = len(line) if line else 40
                noise = ''.join(random.choice(noise_chars) for _ in range(noise_length))
                result.append(noise)

        return '\n'.join(result)

class GlitchController:
    """Manages all glitch effects"""

    def __init__(self):
        self.effects: List[GlitchEffect] = []
        self.base_probability = 0.01  # 1% chance per render
        self.effect_types = {
            'corruption': TextCorruptionGlitch,
            'color_bleed': ColorBleedGlitch,
            'position_shift': PositionShiftGlitch,
            'duplicate': DuplicateLineGlitch,
            'static': StaticNoiseGlitch,
        }

    def should_trigger_glitch(self) -> bool:
        """Determine if a glitch should occur"""
        return random.random() < self.base_probability

    def trigger_random_glitch(self, intensity: float = 0.5, duration: float = 1.0):
        """Trigger a random glitch effect"""
        effect_class = random.choice(list(self.effect_types.values()))
        effect = effect_class(intensity, duration)
        effect.activate()
        self.effects.append(effect)

    def trigger_specific_glitch(self, effect_type: str, intensity: float = 0.5, duration: float = 1.0):
        """Trigger a specific glitch type"""
        if effect_type in self.effect_types:
            effect_class = self.effect_types[effect_type]
            effect = effect_class(intensity, duration)
            effect.activate()
            self.effects.append(effect)

    def apply_all(self, text: str) -> str:
        """Apply all active glitch effects"""
        result = text

        # Remove expired effects
        self.effects = [e for e in self.effects if e.is_active()]

        # Apply each active effect
        for effect in self.effects:
            result = effect.apply(result)

        return result

    def increase_glitch_probability(self, multiplier: float):
        """Increase likelihood of glitches (for specific game events)"""
        self.base_probability = min(0.5, self.base_probability * multiplier)

    def clear_all_glitches(self):
        """Remove all glitch effects"""
        self.effects.clear()

    def load_from_config(self, config_path: str):
        """Load glitch configuration"""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        if 'glitch_settings' in parser:
            self.base_probability = float(parser['glitch_settings'].get('base_probability', 0.01))
```

**Sample config/glitch_effects.ini:**
```ini
[glitch_settings]
base_probability = 0.02
max_simultaneous = 3

[trigger_conditions]
after_menu_visits = 10
after_setting_changes = 25
on_locked_attempt = true

[effect_weights]
corruption = 0.2
color_bleed = 0.3
position_shift = 0.15
duplicate = 0.2
static = 0.15
```

**Testing:**
- Each glitch effect type
- Effect activation and expiration
- Multiple simultaneous effects
- Text preservation (glitches are visual only)
- Intensity scaling
- Config loading

**Procedural:** ✓ Glitch behaviors from config

---

### 5.5 Freeze and Delay System
**Goal:** Fake UI freezes and artificial delays

**Files:**
- `ui/freeze_system.py`
- `tests/test_freeze_system.py`

**Implementation:**
```python
import time
import random
from typing import Callable, Optional

class FreezeEvent:
    """Represents a fake UI freeze"""

    def __init__(self, duration: float, freeze_type: str):
        self.duration = duration
        self.freeze_type = freeze_type  # "full", "partial", "thinking"
        self.start_time = 0.0
        self.active = False

    def start(self):
        """Begin the freeze"""
        self.active = True
        self.start_time = time.time()

    def update(self) -> bool:
        """Returns True if freeze is still active"""
        if not self.active:
            return False

        elapsed = time.time() - self.start_time
        return elapsed < self.duration

    def get_progress(self) -> float:
        """Get freeze progress (0.0-1.0)"""
        if not self.active:
            return 1.0

        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / self.duration)

class FreezeController:
    """Manages fake freezes and delays"""

    def __init__(self):
        self.current_freeze: Optional[FreezeEvent] = None
        self.freeze_probability = 0.03  # 3% chance
        self.minimum_freeze_duration = 1.0
        self.maximum_freeze_duration = 5.0

    def should_trigger_freeze(self, action_type: str) -> bool:
        """Determine if freeze should occur"""
        # Higher chance for certain actions
        multipliers = {
            'enable_setting': 1.5,
            'navigate_menu': 1.0,
            'open_locked': 3.0,  # Much higher for locked settings
            'rapid_action': 2.0,
        }

        probability = self.freeze_probability * multipliers.get(action_type, 1.0)
        return random.random() < probability

    def trigger_freeze(self, freeze_type: str = "full") -> FreezeEvent:
        """Start a freeze event"""
        duration = random.uniform(self.minimum_freeze_duration, self.maximum_freeze_duration)

        # Thinking freezes are shorter
        if freeze_type == "thinking":
            duration = random.uniform(0.5, 2.0)

        freeze = FreezeEvent(duration, freeze_type)
        freeze.start()
        self.current_freeze = freeze
        return freeze

    def execute_with_freeze(self, action: Callable, freeze_type: str = "full"):
        """Execute action with potential freeze before it"""
        if self.current_freeze and self.current_freeze.update():
            # Currently frozen
            self._show_freeze_indicator(self.current_freeze)
            return None

        # Check if should trigger new freeze
        if self.should_trigger_freeze("action"):
            freeze = self.trigger_freeze(freeze_type)
            self._show_freeze_indicator(freeze)

        # Execute the actual action
        return action()

    def _show_freeze_indicator(self, freeze: FreezeEvent):
        """Display freeze indicator"""
        if freeze.freeze_type == "full":
            # Completely frozen, show nothing or frozen cursor
            print("▂", end="", flush=True)
            time.sleep(0.1)

        elif freeze.freeze_type == "thinking":
            # Show thinking indicator
            spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            idx = int((freeze.get_progress() * len(spinners))) % len(spinners)
            print(f"\r{spinners[idx]} Processing...", end="", flush=True)
            time.sleep(0.1)

        elif freeze.freeze_type == "partial":
            # Show partial progress
            progress = freeze.get_progress()
            bar_width = 30
            filled = int(bar_width * progress)
            bar = "=" * filled + " " * (bar_width - filled)
            print(f"\r[{bar}] {progress*100:.0f}%", end="", flush=True)
            time.sleep(0.1)

    def add_artificial_delay(self, base_delay: float, variance: float = 0.5):
        """Add an artificial delay to simulate processing"""
        actual_delay = base_delay + random.uniform(-variance, variance)
        actual_delay = max(0.1, actual_delay)  # At least 0.1s

        # Show fake progress during delay
        steps = int(actual_delay / 0.1)
        for i in range(steps):
            spinners = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
            print(f"\r{spinners[i % len(spinners)]}", end="", flush=True)
            time.sleep(0.1)

        print("\r ", end="", flush=True)  # Clear spinner

    def load_from_config(self, config_path: str):
        """Load freeze configuration"""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(config_path)

        if 'freeze_settings' in parser:
            self.freeze_probability = float(parser['freeze_settings'].get('base_probability', 0.03))
            self.minimum_freeze_duration = float(parser['freeze_settings'].get('min_duration', 1.0))
            self.maximum_freeze_duration = float(parser['freeze_settings'].get('max_duration', 5.0))

class DelayedAction:
    """An action that executes after a delay"""

    def __init__(self, action: Callable, delay: float, show_progress: bool = True):
        self.action = action
        self.delay = delay
        self.show_progress = show_progress
        self.started = False
        self.completed = False
        self.start_time = 0.0

    def start(self):
        """Begin the delayed action"""
        self.started = True
        self.start_time = time.time()

    def update(self) -> bool:
        """Update and execute if ready. Returns True when complete."""
        if self.completed:
            return True

        if not self.started:
            return False

        elapsed = time.time() - self.start_time

        if self.show_progress:
            progress = min(1.0, elapsed / self.delay)
            bar = "█" * int(progress * 20)
            print(f"\r{bar:<20}", end="", flush=True)

        if elapsed >= self.delay:
            self.action()
            self.completed = True
            if self.show_progress:
                print()  # New line after progress
            return True

        return False
```

**Sample config/freeze_system.ini:**
```ini
[freeze_settings]
base_probability = 0.03
min_duration = 1.0
max_duration = 5.0

[action_multipliers]
enable_setting = 1.5
navigate_menu = 1.0
open_locked = 3.0
rapid_action = 2.0

[delays]
menu_load = 0.5
setting_change = 0.3
dependency_check = 0.8
```

**Testing:**
- Freeze triggering and duration
- Different freeze types (full, partial, thinking)
- Freeze indicators
- Artificial delays with progress
- Delayed action execution
- Config loading

**Procedural:** ✓ Freeze behaviors from config

---

## Helper Scripts

### Anti-Pattern Tester
**File:** `scripts/test_antipatterns.py`
```python
#!/usr/bin/env python3
"""Test all anti-pattern systems"""

from ready_to_start.ui.unreliable_progress import ProgressSystemController
from ready_to_start.ui.moving_elements import MovingElementController
from ready_to_start.ui.fake_messages import FakeMessageGenerator
from ready_to_start.ui.glitch_effects import GlitchController
from ready_to_start.ui.freeze_system import FreezeController

def test_progress_bars():
    print("=== Testing Unreliable Progress Bars ===")
    controller = ProgressSystemController()
    controller.load_behaviors_from_config("config/unreliable_progress.ini")
    controller.show_fake_loading(duration=5.0)

def test_moving_elements():
    print("\n=== Testing Moving Elements ===")
    # Create mock game state
    from ready_to_start.generation.pipeline import GenerationPipeline
    pipeline = GenerationPipeline()
    game_state = pipeline.generate(seed=42)

    controller = MovingElementController(game_state)
    controller.load_from_config("config/moving_elements.ini")

    # Simulate element movement
    for i in range(5):
        print(f"\nIteration {i+1}:")
        settings = list(game_state.settings.keys())[:10]
        new_positions = controller.update(settings)
        print(f"Elements moved: {len(new_positions)}")

def test_fake_messages():
    print("\n=== Testing Fake Messages ===")
    generator = FakeMessageGenerator()
    generator.load_templates_from_config("config/fake_messages.ini")

    context = {"setting": "Audio Volume", "category": "Audio"}

    for msg_type in ["error", "warning", "system", "critical"]:
        msg = generator.generate(msg_type, context)
        print(f"[{msg.message_type.upper()}] {msg.text}")

def test_glitches():
    print("\n=== Testing Glitch Effects ===")
    controller = GlitchController()

    sample_text = """
    ╔═══════════════════════════════════════╗
    ║ AUDIO SETTINGS                        ║
    ╠═══════════════════════════════════════╣
    ║ 1. [ ] Master Volume (disabled)       ║
    ║ 2. [X] Enable Audio (enabled)         ║
    ╚═══════════════════════════════════════╝
    """

    for effect_type in ['corruption', 'color_bleed', 'position_shift', 'duplicate', 'static']:
        print(f"\n--- {effect_type} ---")
        controller.trigger_specific_glitch(effect_type, intensity=0.7, duration=1.0)
        glitched = controller.apply_all(sample_text)
        print(glitched)

def test_freezes():
    print("\n=== Testing Freeze System ===")
    controller = FreezeController()

    print("Simulating normal action...")
    controller.add_artificial_delay(1.0)

    print("\nTriggering freeze...")
    freeze = controller.trigger_freeze("thinking")
    while freeze.update():
        controller._show_freeze_indicator(freeze)
    print("\nFreeze complete!")

if __name__ == "__main__":
    test_progress_bars()
    test_moving_elements()
    test_fake_messages()
    test_glitches()
    test_freezes()
```

### Glitch Intensity Controller
**File:** `scripts/control_glitches.py`
```python
#!/usr/bin/env python3
"""Adjust glitch intensity dynamically"""

import sys
from ready_to_start.ui.glitch_effects import GlitchController

def set_intensity(level: str):
    """Set glitch intensity level"""
    controller = GlitchController()

    levels = {
        'none': 0.0,
        'low': 0.01,
        'medium': 0.05,
        'high': 0.15,
        'extreme': 0.50
    }

    if level not in levels:
        print(f"Invalid level. Use: {', '.join(levels.keys())}")
        return

    controller.base_probability = levels[level]
    print(f"Glitch intensity set to: {level} ({levels[level]*100:.1f}%)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: control_glitches.py <none|low|medium|high|extreme>")
    else:
        set_intensity(sys.argv[1])
```

---

## Config Files

See sample configs embedded in each section above. All configs go in `config/` directory:

- `config/unreliable_progress.ini`
- `config/moving_elements.ini`
- `config/fake_messages.ini`
- `config/glitch_effects.ini`
- `config/freeze_system.ini`

---

## Libraries Summary

**Core:**
- time (stdlib)
- random (stdlib)
- configparser (stdlib)

**No external dependencies needed**

---

## Phase 5 Completion Criteria

- [ ] Unreliable progress bars with all behavior types
- [ ] Moving UI elements (shuffle, swap, vanish, duplicate)
- [ ] Fake system messages with templates
- [ ] Fake modal dialogs
- [ ] Visual glitch effects (5+ types)
- [ ] Freeze system with indicators
- [ ] Artificial delay system
- [ ] All behaviors configurable via INI
- [ ] 80%+ test coverage
- [ ] Helper scripts functional
- [ ] Anti-patterns trigger based on game events
- [ ] User can't tell what's real vs fake (goal achieved)
