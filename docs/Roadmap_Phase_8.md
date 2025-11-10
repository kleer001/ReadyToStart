# Ready to Start - Phase 8 Detailed Roadmap

## Phase 8: Polish & Meta (Self-Awareness & Commentary)

### 8.1 Self-Awareness System
**Goal:** Game acknowledges its own absurdity

**Files:**
- `meta/self_awareness.py`
- `data/meta_comments.json`
- `tests/test_self_awareness.py`

**Implementation:**
```python
from typing import List, Optional
import random
import time

class SelfAwarenessSystem:
    """System for meta-commentary and fourth-wall breaks"""

    def __init__(self):
        self.comments = []
        self.triggered_comments = set()
        self.awareness_level = 0  # Increases over time
        self.last_comment_time = 0.0
        self.comment_cooldown = 30.0  # seconds

    def load_comments(self, comments_file: str):
        """Load meta-commentary from JSON"""
        import json
        with open(comments_file) as f:
            data = json.load(f)

        self.comments = data['comments']

    def should_trigger_comment(self, context: dict) -> bool:
        """Determine if a comment should appear"""
        # Cooldown check
        if time.time() - self.last_comment_time < self.comment_cooldown:
            return False

        # Awareness level increases chance
        base_probability = 0.02 + (self.awareness_level * 0.01)

        return random.random() < base_probability

    def get_contextual_comment(self, context: dict) -> Optional[str]:
        """Get a comment appropriate for the situation"""
        eligible = []

        for comment_data in self.comments:
            # Check if already triggered and should only show once
            if comment_data.get('show_once', False):
                if comment_data['id'] in self.triggered_comments:
                    continue

            # Check trigger condition
            if self._check_trigger(comment_data['trigger'], context):
                # Check awareness level requirement
                if self.awareness_level >= comment_data.get('min_awareness', 0):
                    eligible.append(comment_data)

        if not eligible:
            return None

        # Select one
        selected = random.choice(eligible)
        self.triggered_comments.add(selected['id'])
        self.last_comment_time = time.time()

        return selected['text']

    def _check_trigger(self, trigger: str, context: dict) -> bool:
        """Check if trigger condition is met"""
        if trigger == "time_spent_excessive":
            return context.get('time_spent', 0) > 600  # 10 minutes

        elif trigger == "many_failed_attempts":
            return context.get('failed_attempts', 0) > 10

        elif trigger == "circular_dependency_attempt":
            return context.get('circular_detected', False)

        elif trigger == "progress_not_real":
            return context.get('fake_progress_shown', False)

        elif trigger == "glitch_occurred":
            return context.get('glitch_count', 0) > 0

        elif trigger == "layer_transition":
            return context.get('layer_changed', False)

        elif trigger == "deep_layer_reached":
            return context.get('layer_depth', 0) >= 5

        elif trigger == "found_secret":
            return context.get('secret_found', False)

        elif trigger == "quit_attempt":
            return context.get('tried_to_quit', False)

        elif trigger == "reading_help":
            return context.get('viewing_help', False)

        return False

    def increase_awareness(self, amount: int = 1):
        """Increase meta-awareness level"""
        self.awareness_level = min(10, self.awareness_level + amount)

    def get_awareness_level(self) -> int:
        """Get current awareness level"""
        return self.awareness_level
```

**Meta-Commentary Database:**
```json
{
  "comments": [
    {
      "id": "time_spent_1",
      "trigger": "time_spent_excessive",
      "min_awareness": 0,
      "show_once": true,
      "text": "You've been at this for a while. It's just a settings menu. Or is it?"
    },
    {
      "id": "circular_1",
      "trigger": "circular_dependency_attempt",
      "min_awareness": 1,
      "show_once": false,
      "text": "The dependency appears circular. But then again, so does this entire game."
    },
    {
      "id": "fake_progress_1",
      "trigger": "progress_not_real",
      "min_awareness": 2,
      "show_once": true,
      "text": "That progress bar is lying to you. But you already knew that, didn't you?"
    },
    {
      "id": "glitch_1",
      "trigger": "glitch_occurred",
      "min_awareness": 1,
      "show_once": false,
      "text": "Was that a bug? Or a feature? At this point, does it matter?"
    },
    {
      "id": "layer_5",
      "trigger": "deep_layer_reached",
      "min_awareness": 5,
      "show_once": true,
      "text": "Five layers deep. How many more do you think there are? (The answer will surprise you.)"
    },
    {
      "id": "secret_1",
      "trigger": "found_secret",
      "min_awareness": 3,
      "show_once": false,
      "text": "You found a secret. Your reward is: more settings menus."
    },
    {
      "id": "quit_1",
      "trigger": "quit_attempt",
      "min_awareness": 0,
      "show_once": true,
      "text": "Trying to quit? But you were so close to... wait, no, you're nowhere near done."
    },
    {
      "id": "help_1",
      "trigger": "reading_help",
      "min_awareness": 2,
      "show_once": true,
      "text": "Reading the help file? That's adorable. The help is part of the problem."
    },
    {
      "id": "transition_bios",
      "trigger": "layer_transition",
      "min_awareness": 4,
      "show_once": true,
      "text": "Transitioning to BIOS configuration. Because what's more fun than settings? Lower-level settings."
    },
    {
      "id": "punch_cards",
      "trigger": "layer_transition",
      "min_awareness": 6,
      "show_once": true,
      "text": "Punch cards. We've gone so deep we've hit the 1960s. Should I be worried about you?"
    },
    {
      "id": "meta_revelation",
      "trigger": "deep_layer_reached",
      "min_awareness": 8,
      "show_once": true,
      "text": "You're in a game about settings menus, trying to configure settings to unlock more settings. Think about that."
    }
  ]
}
```

**Testing:**
- Comment trigger conditions
- Cooldown enforcement
- Awareness level progression
- Show-once tracking
- Context matching

**Procedural:** ✓ Comments loaded from JSON

---

### 8.2 Fourth-Wall Breaks
**Goal:** Direct communication with the player

**Files:**
- `meta/fourth_wall.py`
- `data/fourth_wall_breaks.json`
- `tests/test_fourth_wall.py`

**Implementation:**
```python
from typing import Optional
import random

class FourthWallBreaker:
    """Breaks the fourth wall at appropriate moments"""

    def __init__(self):
        self.breaks = []
        self.triggered_breaks = set()

    def load_breaks(self, breaks_file: str):
        """Load fourth wall breaks from JSON"""
        import json
        with open(breaks_file) as f:
            data = json.load(f)
        self.breaks = data['breaks']

    def get_break(self, event_type: str, context: dict) -> Optional[dict]:
        """Get a fourth wall break for this event"""
        eligible = []

        for break_data in self.breaks:
            if break_data['event'] == event_type:
                # Check if already used (if show_once)
                if break_data.get('show_once', False):
                    if break_data['id'] in self.triggered_breaks:
                        continue

                # Check condition if present
                if 'condition' in break_data:
                    if not self._check_condition(break_data['condition'], context):
                        continue

                eligible.append(break_data)

        if not eligible:
            return None

        # Select one
        selected = random.choice(eligible)

        if selected.get('show_once', False):
            self.triggered_breaks.add(selected['id'])

        return selected

    def _check_condition(self, condition: str, context: dict) -> bool:
        """Check if condition is met"""
        if condition == "first_time":
            return context.get('is_first', False)
        elif condition == "frustrated":
            return context.get('failed_attempts', 0) > 5
        elif condition == "far_in_game":
            return context.get('layer_depth', 0) > 3
        return True

    def display_break(self, break_data: dict):
        """Display the fourth wall break"""
        print("\n" + "=" * 60)
        print(f"\n{break_data['text']}\n")

        if 'action' in break_data:
            self._perform_action(break_data['action'])

        print("=" * 60 + "\n")

        if break_data.get('pause', False):
            input("Press Enter to continue...")

    def _perform_action(self, action: str):
        """Perform special action"""
        if action == "cursor_movement":
            # Make cursor do something weird
            import time
            for i in range(5):
                print(f"\r{'>' * (i+1)}", end='', flush=True)
                time.sleep(0.3)
            print()

        elif action == "screen_shake":
            # Simulate screen shake with rapid redraws
            import time
            for _ in range(10):
                print("\n" * random.randint(-2, 2), end='')
                time.sleep(0.05)
```

**Fourth Wall Breaks:**
```json
{
  "breaks": [
    {
      "id": "game_start_meta",
      "event": "game_start",
      "condition": "first_time",
      "show_once": true,
      "text": "Welcome to a game about settings menus. Yes, really. No, there's no 'actual game' hidden underneath. This is it. Enjoy?",
      "pause": true
    },
    {
      "id": "first_lock_awareness",
      "event": "encounter_locked_setting",
      "condition": "first_time",
      "show_once": true,
      "text": "Ah, your first locked setting. This is the core 'gameplay.' You'll be doing this for a while. Sorry about that.",
      "pause": false
    },
    {
      "id": "frustrated_player",
      "event": "many_failures",
      "condition": "frustrated",
      "show_once": true,
      "text": "You seem frustrated. Would you like me to just tell you the answer? [Hint: I can't. I'm just text in a JSON file.]",
      "pause": true
    },
    {
      "id": "deep_layer_horror",
      "event": "layer_transition",
      "condition": "far_in_game",
      "show_once": true,
      "text": "You're STILL playing this? At this point you're not configuring settings, you're making life choices. Questionable ones.",
      "pause": true
    },
    {
      "id": "punch_card_absurdity",
      "event": "enter_punch_card_layer",
      "show_once": true,
      "text": "Punch cards. We've reached punch cards. I want you to really think about what you're doing with your time right now.",
      "pause": true,
      "action": "cursor_movement"
    },
    {
      "id": "quantum_confusion",
      "event": "enter_quantum_layer",
      "show_once": true,
      "text": "Quantum settings. The settings exist in superposition - both configured and unconfigured until you observe them. Which is nonsense, but so is this entire game.",
      "pause": true
    },
    {
      "id": "meta_layer_recursion",
      "event": "enter_meta_layer",
      "show_once": true,
      "text": "You're now configuring the settings that configure the settings. If you're experiencing an existential crisis, that's working as intended.",
      "pause": true
    },
    {
      "id": "near_end",
      "event": "approaching_final_layer",
      "show_once": true,
      "text": "You're almost at the end. Was it worth it? Will it ever be worth it? Are these questions the game is asking, or are you asking them? Yes.",
      "pause": true
    },
    {
      "id": "final_layer_reveal",
      "event": "enter_final_layer",
      "show_once": true,
      "text": "This is it. The final layer. After all those settings menus, all that configuration, it comes down to this. I hope you're ready.",
      "pause": true
    },
    {
      "id": "quit_commentary",
      "event": "player_quits",
      "show_once": false,
      "text": "Quitting? Fair. I wouldn't want to configure any more settings either. Your progress has been... well, it exists.",
      "pause": false
    }
  ]
}
```

**Testing:**
- Break triggering
- Condition checking
- Show-once enforcement
- Action execution
- Display formatting

**Procedural:** ✓ Breaks loaded from JSON

---

### 8.3 Achievement System
**Goal:** Track ridiculous achievements

**Files:**
- `meta/achievements.py`
- `data/achievements.json`
- `tests/test_achievements.py`

**Implementation:**
```python
from dataclasses import dataclass
from typing import List, Dict, Callable
import json

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    condition: str
    threshold: float
    secret: bool
    unlocked: bool = False
    unlock_time: float = 0.0
    rarity: str = "common"  # common, uncommon, rare, legendary

class AchievementSystem:
    """Tracks player achievements"""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_count = 0

    def load_achievements(self, achievements_file: str):
        """Load achievements from JSON"""
        with open(achievements_file) as f:
            data = json.load(f)

        for ach_data in data['achievements']:
            achievement = Achievement(
                id=ach_data['id'],
                name=ach_data['name'],
                description=ach_data['description'],
                condition=ach_data['condition'],
                threshold=ach_data.get('threshold', 0),
                secret=ach_data.get('secret', False),
                rarity=ach_data.get('rarity', 'common')
            )
            self.achievements[achievement.id] = achievement

    def check_achievements(self, game_state: dict) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        newly_unlocked = []

        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue

            if self._check_condition(achievement, game_state):
                achievement.unlocked = True
                achievement.unlock_time = game_state.get('time', 0)
                self.unlocked_count += 1
                newly_unlocked.append(achievement)

        return newly_unlocked

    def _check_condition(self, achievement: Achievement, game_state: dict) -> bool:
        """Check if achievement condition is met"""
        condition = achievement.condition

        if condition == "time_spent":
            return game_state.get('total_time', 0) >= achievement.threshold

        elif condition == "settings_enabled":
            return game_state.get('settings_enabled', 0) >= achievement.threshold

        elif condition == "layers_completed":
            return game_state.get('layers_completed', 0) >= achievement.threshold

        elif condition == "errors_made":
            return game_state.get('total_errors', 0) >= achievement.threshold

        elif condition == "efficiency_high":
            return game_state.get('efficiency', 0) >= achievement.threshold

        elif condition == "efficiency_low":
            return game_state.get('efficiency', 0) <= achievement.threshold

        elif condition == "secrets_found":
            return game_state.get('secrets_found', 0) >= achievement.threshold

        elif condition == "quit_attempts":
            return game_state.get('quit_attempts', 0) >= achievement.threshold

        elif condition == "help_views":
            return game_state.get('help_views', 0) >= achievement.threshold

        elif condition == "reached_final_layer":
            return game_state.get('layer_id') == 'final_layer'

        elif condition == "perfect_layer":
            return game_state.get('errors_in_layer', 0) == 0 and \
                   game_state.get('layer_completed', False)

        elif condition == "found_quantum_layer":
            return game_state.get('layer_id') == 'quantum_interface'

        return False

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [a for a in self.achievements.values() if a.unlocked]

    def get_locked_achievements(self, include_secret: bool = False) -> List[Achievement]:
        """Get all locked achievements"""
        locked = [a for a in self.achievements.values() if not a.unlocked]

        if not include_secret:
            locked = [a for a in locked if not a.secret]

        return locked

    def get_completion_percentage(self) -> float:
        """Get achievement completion percentage"""
        if not self.achievements:
            return 0.0
        return (self.unlocked_count / len(self.achievements)) * 100

    def display_achievement_unlock(self, achievement: Achievement):
        """Display achievement unlock notification"""
        rarity_symbols = {
            'common': '★',
            'uncommon': '★★',
            'rare': '★★★',
            'legendary': '★★★★'
        }

        symbol = rarity_symbols.get(achievement.rarity, '★')

        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + f"  🏆 ACHIEVEMENT UNLOCKED! {symbol}".ljust(58) + "║")
        print("║" + " " * 58 + "║")
        print("║" + f"  {achievement.name}".ljust(58) + "║")
        print("║" + f"  {achievement.description}".ljust(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "═" * 58 + "╝\n")

        input("Press Enter to continue...")
```

**Achievements Database:**
```json
{
  "achievements": [
    {
      "id": "first_setting",
      "name": "Baby Steps",
      "description": "Enable your first setting",
      "condition": "settings_enabled",
      "threshold": 1,
      "rarity": "common",
      "secret": false
    },
    {
      "id": "ten_settings",
      "name": "Getting the Hang of It",
      "description": "Enable 10 settings",
      "condition": "settings_enabled",
      "threshold": 10,
      "rarity": "common",
      "secret": false
    },
    {
      "id": "completionist",
      "name": "Completionist",
      "description": "Enable all settings in a layer",
      "condition": "perfect_layer",
      "threshold": 0,
      "rarity": "uncommon",
      "secret": false
    },
    {
      "id": "time_waster",
      "name": "Time is Relative",
      "description": "Spend over 1 hour in the game",
      "condition": "time_spent",
      "threshold": 3600,
      "rarity": "uncommon",
      "secret": false
    },
    {
      "id": "error_prone",
      "name": "Trial and Error (Mostly Error)",
      "description": "Make 50 errors",
      "condition": "errors_made",
      "threshold": 50,
      "rarity": "common",
      "secret": false
    },
    {
      "id": "efficient",
      "name": "Somehow Efficient",
      "description": "Achieve 90%+ efficiency in a layer",
      "condition": "efficiency_high",
      "threshold": 90,
      "rarity": "rare",
      "secret": false
    },
    {
      "id": "inefficient",
      "name": "Spectacularly Inefficient",
      "description": "Achieve less than 10% efficiency in a layer",
      "condition": "efficiency_low",
      "threshold": 10,
      "rarity": "rare",
      "secret": false
    },
    {
      "id": "layer_5",
      "name": "Going Deeper",
      "description": "Complete 5 interface layers",
      "condition": "layers_completed",
      "threshold": 5,
      "rarity": "uncommon",
      "secret": false
    },
    {
      "id": "quantum_discovered",
      "name": "Quantum Leap",
      "description": "Discover the quantum interface layer",
      "condition": "found_quantum_layer",
      "threshold": 0,
      "rarity": "legendary",
      "secret": true
    },
    {
      "id": "secret_hunter",
      "name": "Secret Hunter",
      "description": "Find 5 secrets",
      "condition": "secrets_found",
      "threshold": 5,
      "rarity": "rare",
      "secret": false
    },
    {
      "id": "help_seeker",
      "name": "RTFM",
      "description": "View the help file 10 times",
      "condition": "help_views",
      "threshold": 10,
      "rarity": "common",
      "secret": false
    },
    {
      "id": "quit_attempts",
      "name": "Commitment Issues",
      "description": "Try to quit 5 times without actually quitting",
      "condition": "quit_attempts",
      "threshold": 5,
      "rarity": "uncommon",
      "secret": false
    },
    {
      "id": "final_layer",
      "name": "The Truth",
      "description": "Reach the final layer",
      "condition": "reached_final_layer",
      "threshold": 0,
      "rarity": "legendary",
      "secret": false
    },
    {
      "id": "perfectionist",
      "name": "Unreasonable Standards",
      "description": "Complete every layer with zero errors",
      "condition": "perfect_all_layers",
      "threshold": 0,
      "rarity": "legendary",
      "secret": true
    }
  ]
}
```

**Testing:**
- Achievement unlocking
- Condition checking
- Secret achievement hiding
- Rarity classification
- Progress tracking

**Procedural:** ✓ Achievements loaded from JSON

---

### 8.4 Statistics Tracking
**Goal:** Comprehensive player statistics

**Files:**
- `meta/statistics.py`
- `tests/test_statistics.py`

**Implementation:**
```python
from dataclasses import dataclass, field
from typing import Dict, List
import time
import json

@dataclass
class GameStatistics:
    """Comprehensive game statistics"""

    # Time
    total_play_time: float = 0.0
    time_per_layer: Dict[str, float] = field(default_factory=dict)
    session_start_time: float = field(default_factory=time.time)

    # Actions
    total_actions: int = 0
    settings_viewed: int = 0
    settings_enabled: int = 0
    settings_disabled: int = 0
    menus_visited: int = 0
    navigations: int = 0

    # Errors
    total_errors: int = 0
    locked_attempts: int = 0
    invalid_values: int = 0
    dependency_failures: int = 0

    # Layers
    layers_completed: int = 0
    current_layer_depth: int = 0
    deepest_layer_reached: int = 0

    # Efficiency
    perfect_layers: int = 0
    average_efficiency: float = 0.0
    best_efficiency: float = 0.0
    worst_efficiency: float = 100.0

    # Meta
    glitches_encountered: int = 0
    fake_errors_shown: int = 0
    fourth_wall_breaks: int = 0
    meta_comments: int = 0

    # Help
    help_views: int = 0
    hints_viewed: int = 0

    # Secrets
    secrets_found: List[str] = field(default_factory=list)

    # Quit attempts
    quit_attempts: int = 0

    def get_total_time(self) -> float:
        """Get total time including current session"""
        return self.total_play_time + (time.time() - self.session_start_time)

    def get_summary(self) -> dict:
        """Get statistics summary"""
        return {
            'Total Time': f"{self.get_total_time():.1f}s",
            'Actions Taken': self.total_actions,
            'Settings Enabled': self.settings_enabled,
            'Errors Made': self.total_errors,
            'Layers Completed': self.layers_completed,
            'Deepest Layer': self.deepest_layer_reached,
            'Efficiency (Avg)': f"{self.average_efficiency:.1f}%",
            'Secrets Found': len(self.secrets_found),
            'Quit Attempts': self.quit_attempts
        }

    def serialize(self) -> dict:
        """Serialize to JSON-compatible dict"""
        return {
            'total_play_time': self.get_total_time(),
            'time_per_layer': self.time_per_layer,
            'total_actions': self.total_actions,
            'settings_viewed': self.settings_viewed,
            'settings_enabled': self.settings_enabled,
            'settings_disabled': self.settings_disabled,
            'menus_visited': self.menus_visited,
            'navigations': self.navigations,
            'total_errors': self.total_errors,
            'locked_attempts': self.locked_attempts,
            'invalid_values': self.invalid_values,
            'dependency_failures': self.dependency_failures,
            'layers_completed': self.layers_completed,
            'current_layer_depth': self.current_layer_depth,
            'deepest_layer_reached': self.deepest_layer_reached,
            'perfect_layers': self.perfect_layers,
            'average_efficiency': self.average_efficiency,
            'best_efficiency': self.best_efficiency,
            'worst_efficiency': self.worst_efficiency,
            'glitches_encountered': self.glitches_encountered,
            'fake_errors_shown': self.fake_errors_shown,
            'fourth_wall_breaks': self.fourth_wall_breaks,
            'meta_comments': self.meta_comments,
            'help_views': self.help_views,
            'hints_viewed': self.hints_viewed,
            'secrets_found': self.secrets_found,
            'quit_attempts': self.quit_attempts
        }

class StatisticsTracker:
    """Tracks and manages game statistics"""

    def __init__(self):
        self.stats = GameStatistics()

    def record_action(self, action_type: str, details: dict = None):
        """Record a player action"""
        self.stats.total_actions += 1

        if action_type == 'setting_viewed':
            self.stats.settings_viewed += 1
        elif action_type == 'setting_enabled':
            self.stats.settings_enabled += 1
        elif action_type == 'setting_disabled':
            self.stats.settings_disabled += 1
        elif action_type == 'menu_visited':
            self.stats.menus_visited += 1
        elif action_type == 'navigation':
            self.stats.navigations += 1
        elif action_type == 'error_locked':
            self.stats.total_errors += 1
            self.stats.locked_attempts += 1
        elif action_type == 'error_invalid_value':
            self.stats.total_errors += 1
            self.stats.invalid_values += 1
        elif action_type == 'error_dependency':
            self.stats.total_errors += 1
            self.stats.dependency_failures += 1
        elif action_type == 'glitch':
            self.stats.glitches_encountered += 1
        elif action_type == 'fake_error':
            self.stats.fake_errors_shown += 1
        elif action_type == 'fourth_wall_break':
            self.stats.fourth_wall_breaks += 1
        elif action_type == 'meta_comment':
            self.stats.meta_comments += 1
        elif action_type == 'help_view':
            self.stats.help_views += 1
        elif action_type == 'hint_view':
            self.stats.hints_viewed += 1
        elif action_type == 'quit_attempt':
            self.stats.quit_attempts += 1

    def record_layer_completion(self, layer_id: str, layer_stats: dict):
        """Record completion of a layer"""
        self.stats.layers_completed += 1

        # Track time for this layer
        self.stats.time_per_layer[layer_id] = layer_stats.get('time_spent', 0)

        # Update efficiency tracking
        efficiency = layer_stats.get('efficiency', 0)
        self.stats.best_efficiency = max(self.stats.best_efficiency, efficiency)
        self.stats.worst_efficiency = min(self.stats.worst_efficiency, efficiency)

        # Update average
        total_layers = len(self.stats.time_per_layer)
        if total_layers > 0:
            self.stats.average_efficiency = (
                (self.stats.average_efficiency * (total_layers - 1) + efficiency) / total_layers
            )

        # Check for perfect layer
        if layer_stats.get('errors', 0) == 0:
            self.stats.perfect_layers += 1

    def record_secret_found(self, secret_id: str):
        """Record discovery of a secret"""
        if secret_id not in self.stats.secrets_found:
            self.stats.secrets_found.append(secret_id)

    def update_layer_depth(self, depth: int):
        """Update current layer depth"""
        self.stats.current_layer_depth = depth
        self.stats.deepest_layer_reached = max(
            self.stats.deepest_layer_reached,
            depth
        )

    def save_to_file(self, filepath: str):
        """Save statistics to file"""
        with open(filepath, 'w') as f:
            json.dump(self.stats.serialize(), f, indent=2)

    def load_from_file(self, filepath: str):
        """Load statistics from file"""
        with open(filepath) as f:
            data = json.load(f)

        # Reconstruct statistics
        self.stats = GameStatistics(**data)
        self.stats.session_start_time = time.time()
```

**Testing:**
- Action recording
- Layer completion tracking
- Efficiency calculation
- Time tracking
- Serialization/deserialization

**Procedural:** None (tracking system)

---

### 8.5 End-Game Summary
**Goal:** Comprehensive summary when game ends

**Files:**
- `meta/end_game_summary.py`
- `tests/test_end_game_summary.py`

**Implementation:**
```python
class EndGameSummary:
    """Generate end-game summary screen"""

    def __init__(self, stats: GameStatistics, achievements: AchievementSystem):
        self.stats = stats
        self.achievements = achievements

    def generate_summary(self) -> str:
        """Generate complete end-game summary"""
        output = []

        output.append("=" * 80)
        output.append("")
        output.append("CONGRATULATIONS (?)".center(80))
        output.append("")
        output.append("You finished Ready to Start.".center(80))
        output.append("A game about settings menus.".center(80))
        output.append("That you actually completed.".center(80))
        output.append("")
        output.append("=" * 80)
        output.append("")

        # Statistics
        output.append("YOUR STATISTICS:")
        output.append("")

        for key, value in self.stats.get_summary().items():
            output.append(f"  {key:30s} {value}")

        output.append("")
        output.append("─" * 80)
        output.append("")

        # Achievements
        output.append("ACHIEVEMENTS:")
        output.append("")
        unlocked = self.achievements.get_unlocked_achievements()
        total = len(self.achievements.achievements)
        output.append(f"  Unlocked: {len(unlocked)}/{total} ({self.achievements.get_completion_percentage():.1f}%)")
        output.append("")

        for achievement in unlocked[-5:]:  # Show last 5
            rarity_symbol = "★" * (["common", "uncommon", "rare", "legendary"].index(achievement.rarity) + 1)
            output.append(f"  {rarity_symbol} {achievement.name}")

        output.append("")
        output.append("─" * 80)
        output.append("")

        # Commentary
        output.append(self._get_personalized_commentary())
        output.append("")

        output.append("=" * 80)
        output.append("")
        output.append("Thanks for playing (?).".center(80))
        output.append("")
        output.append("=" * 80)

        return "\n".join(output)

    def _get_personalized_commentary(self) -> str:
        """Generate personalized commentary based on stats"""
        comments = []

        # Time-based
        total_time = self.stats.get_total_time()
        if total_time > 7200:  # 2 hours
            comments.append("You spent over 2 hours on this. I'm not sure whether to be impressed or concerned.")
        elif total_time < 600:  # 10 minutes
            comments.append("You speedran through settings menus. That's... actually kind of impressive.")

        # Error-based
        if self.stats.total_errors == 0:
            comments.append("Zero errors. You're either very skilled or very lucky. Or you're a robot.")
        elif self.stats.total_errors > 100:
            comments.append("Over 100 errors. But you persisted. That's dedication, or stubbornness, or both.")

        # Efficiency
        if self.stats.average_efficiency > 90:
            comments.append("Your efficiency rating is suspiciously high. Are you sure you're human?")
        elif self.stats.average_efficiency < 20:
            comments.append("Your efficiency rating is abysmal. But you made it anyway. Respect.")

        # Secrets
        if len(self.stats.secrets_found) > 5:
            comments.append("You found a bunch of secrets. Your reward is... satisfaction? Sorry.")
        elif len(self.stats.secrets_found) == 0:
            comments.append("You found zero secrets. Probably for the best, they weren't that great anyway.")

        # Quit attempts
        if self.stats.quit_attempts > 10:
            comments.append("You tried to quit over 10 times. But here you are. What does that say about you?")

        # Layers
        if self.stats.layers_completed >= 15:
            comments.append("You went through EVERY layer. Every single one. I admire the commitment to the bit.")

        return "\n".join(f"  • {c}" for c in comments)

    def display(self):
        """Display the end game summary"""
        summary = self.generate_summary()
        print("\n" + summary + "\n")
        input("Press Enter to exit...")
```

**Testing:**
- Summary generation
- Statistic formatting
- Personalized commentary selection
- Achievement display
- Output formatting

**Procedural:** None (summary generation)

---

## Helper Scripts

**Note:** Statistics and achievement tracking is integrated into the main game and `scripts/playtest.py` tool. No separate helper scripts are needed.

---

## Phase 8 Completion Criteria

- [ ] Self-awareness system with meta-commentary
- [ ] Fourth-wall breaks implemented
- [ ] Achievement system with 15+ achievements
- [ ] Comprehensive statistics tracking
- [ ] End-game summary screen
- [ ] Personalized commentary based on play style
- [ ] Achievement unlock notifications
- [ ] Statistics persistence (save/load)
- [ ] All meta content in JSON files
- [ ] 80%+ test coverage
- [ ] Helper scripts functional
- [ ] Meta commentary feels natural
- [ ] Achievements are ridiculous but fun
- [ ] Statistics are comprehensive
