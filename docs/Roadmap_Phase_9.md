# Ready to Start - Phase 9 Detailed Roadmap

## Phase 9: Testing & Balance (Playability & Difficulty)

### 9.1 Solvability Validation
**Goal:** Ensure all generated games can be completed

**Files:**
- `testing/solvability_checker.py`
- `tests/test_solvability.py`

**Implementation:**
```python
from typing import List, Set, Dict, Optional
from ready_to_start.core.game_state import GameState
from ready_to_start.core.enums import SettingState

class SolvabilityChecker:
    """Verifies that a generated game state is solvable"""

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.errors = []
        self.warnings = []

    def check_solvability(self) -> bool:
        """Run all solvability checks"""
        self.errors = []
        self.warnings = []

        checks = [
            self._check_no_impossible_dependencies,
            self._check_no_true_circular_dependencies,
            self._check_reachable_victory_conditions,
            self._check_all_settings_can_unlock,
            self._check_menu_connectivity,
            self._check_dependency_chain_lengths,
        ]

        for check in checks:
            check()

        return len(self.errors) == 0

    def _check_no_impossible_dependencies(self):
        """Check that no setting depends on non-existent settings"""
        for setting_id, deps in self.game_state.resolver.dependencies.items():
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    dep_id = dep.setting_id
                    if dep_id not in self.game_state.settings:
                        self.errors.append(
                            f"Setting '{setting_id}' depends on non-existent setting '{dep_id}'"
                        )

    def _check_no_true_circular_dependencies(self):
        """Check for unresolvable circular dependencies"""
        visited = set()
        recursion_stack = set()

        def has_cycle(setting_id: str, path: List[str]) -> Optional[List[str]]:
            if setting_id in recursion_stack:
                # Found a cycle
                cycle_start = path.index(setting_id)
                return path[cycle_start:]

            if setting_id in visited:
                return None

            visited.add(setting_id)
            recursion_stack.add(setting_id)

            # Check dependencies
            deps = self.game_state.resolver.dependencies.get(setting_id, [])
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    cycle = has_cycle(dep.setting_id, path + [setting_id])
                    if cycle:
                        return cycle

            recursion_stack.remove(setting_id)
            return None

        for setting_id in self.game_state.settings:
            if setting_id not in visited:
                cycle = has_cycle(setting_id, [])
                if cycle:
                    self.errors.append(
                        f"Circular dependency detected: {' -> '.join(cycle + [cycle[0]])}"
                    )

    def _check_reachable_victory_conditions(self):
        """Check that victory conditions are achievable"""
        # Simulate attempting to enable all critical settings
        simulation_state = self._simulate_optimal_play()

        critical_settings = self._identify_critical_settings()

        for setting_id in critical_settings:
            if setting_id not in simulation_state:
                self.warnings.append(
                    f"Critical setting '{setting_id}' may not be reachable"
                )

    def _check_all_settings_can_unlock(self):
        """Check that every locked setting can eventually be unlocked"""
        # Simulate enabling all settings
        enabled = set()
        changed = True
        iterations = 0
        max_iterations = 1000

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1

            for setting_id, setting in self.game_state.settings.items():
                if setting_id in enabled:
                    continue

                # Check if dependencies are satisfied
                can_enable = True
                deps = self.game_state.resolver.dependencies.get(setting_id, [])

                for dep in deps:
                    if hasattr(dep, 'setting_id'):
                        if dep.setting_id not in enabled:
                            can_enable = False
                            break
                    elif hasattr(dep, 'setting_a') and hasattr(dep, 'setting_b'):
                        # Value dependency - harder to check
                        pass  # Simplified for now

                if can_enable:
                    enabled.add(setting_id)
                    changed = True

        # Check if all settings were enabled
        locked_settings = set(self.game_state.settings.keys()) - enabled

        if locked_settings:
            self.errors.append(
                f"{len(locked_settings)} settings permanently locked: {list(locked_settings)[:5]}"
            )

    def _check_menu_connectivity(self):
        """Check that all menus are reachable"""
        # Start from first menu, follow connections
        if not self.game_state.menus:
            self.errors.append("No menus in game state")
            return

        start_menu = list(self.game_state.menus.keys())[0]
        reachable = set()
        to_visit = [start_menu]

        while to_visit:
            current = to_visit.pop(0)
            if current in reachable:
                continue

            reachable.add(current)

            menu = self.game_state.menus.get(current)
            if menu:
                for connection in menu.connections:
                    if connection not in reachable:
                        to_visit.append(connection)

        unreachable = set(self.game_state.menus.keys()) - reachable

        if unreachable:
            self.warnings.append(
                f"{len(unreachable)} menus unreachable: {list(unreachable)}"
            )

    def _check_dependency_chain_lengths(self):
        """Check for excessively long dependency chains"""
        max_depth = 10

        def get_depth(setting_id: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()

            if setting_id in visited:
                return 0  # Cycle detected

            visited.add(setting_id)

            deps = self.game_state.resolver.dependencies.get(setting_id, [])
            if not deps:
                return 0

            max_dep_depth = 0
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    depth = get_depth(dep.setting_id, visited.copy())
                    max_dep_depth = max(max_dep_depth, depth)

            return max_dep_depth + 1

        for setting_id in self.game_state.settings:
            depth = get_depth(setting_id)
            if depth > max_depth:
                self.warnings.append(
                    f"Setting '{setting_id}' has dependency chain depth {depth} (max {max_depth})"
                )

    def _simulate_optimal_play(self) -> Set[str]:
        """Simulate perfect play to see what's achievable"""
        enabled = set()

        # Iteratively enable all possible settings
        for _ in range(100):  # Max iterations
            changed = False

            for setting_id in self.game_state.settings:
                if setting_id not in enabled:
                    # Try to enable
                    deps_satisfied = self._check_deps_satisfied(setting_id, enabled)
                    if deps_satisfied:
                        enabled.add(setting_id)
                        changed = True

            if not changed:
                break

        return enabled

    def _check_deps_satisfied(self, setting_id: str, enabled: Set[str]) -> bool:
        """Check if setting's dependencies are satisfied"""
        deps = self.game_state.resolver.dependencies.get(setting_id, [])

        for dep in deps:
            if hasattr(dep, 'setting_id'):
                if dep.setting_id not in enabled:
                    return False

        return True

    def _identify_critical_settings(self) -> List[str]:
        """Identify settings critical for victory"""
        # Simplified: settings with many dependents
        critical = []

        for setting_id in self.game_state.settings:
            dependent_count = sum(
                1 for deps in self.game_state.resolver.dependencies.values()
                for dep in deps
                if hasattr(dep, 'setting_id') and dep.setting_id == setting_id
            )

            if dependent_count >= 3:  # Arbitrary threshold
                critical.append(setting_id)

        return critical

    def get_report(self) -> str:
        """Generate solvability report"""
        lines = []

        lines.append("=== SOLVABILITY REPORT ===\n")

        if not self.errors and not self.warnings:
            lines.append("✓ All checks passed! Game is solvable.\n")
        else:
            if self.errors:
                lines.append(f"ERRORS ({len(self.errors)}):")
                for error in self.errors:
                    lines.append(f"  ✗ {error}")
                lines.append("")

            if self.warnings:
                lines.append(f"WARNINGS ({len(self.warnings)}):")
                for warning in self.warnings:
                    lines.append(f"  ⚠ {warning}")
                lines.append("")

        return "\n".join(lines)
```

**Testing:**
- Impossible dependency detection
- Circular dependency detection
- Victory condition reachability
- Menu connectivity
- Dependency chain length limits
- Simulation of optimal play

**Procedural:** None (validation tool)

---

### 9.2 Difficulty Curve Analysis
**Goal:** Ensure appropriate difficulty progression

**Files:**
- `testing/difficulty_analyzer.py`
- `tests/test_difficulty_analyzer.py`

**Implementation:**
```python
from dataclasses import dataclass
from typing import List, Dict
import statistics

@dataclass
class DifficultyMetrics:
    """Metrics for difficulty analysis"""
    setting_count: int
    dependency_count: int
    dependency_density: float
    avg_chain_length: float
    max_chain_length: int
    circular_dependencies: int
    locked_settings_ratio: float
    menu_count: int

class DifficultyAnalyzer:
    """Analyzes and balances game difficulty"""

    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def analyze(self) -> DifficultyMetrics:
        """Analyze difficulty of current game state"""

        setting_count = len(self.game_state.settings)
        dependency_count = sum(
            len(deps) for deps in self.game_state.resolver.dependencies.values()
        )

        dependency_density = 0.0
        if setting_count > 0:
            dependency_density = dependency_count / setting_count

        # Chain lengths
        chain_lengths = self._calculate_chain_lengths()
        avg_chain_length = statistics.mean(chain_lengths) if chain_lengths else 0
        max_chain_length = max(chain_lengths) if chain_lengths else 0

        # Circular dependencies
        circular_count = self._count_circular_dependencies()

        # Locked settings
        locked_count = sum(
            1 for s in self.game_state.settings.values()
            if s.state == SettingState.LOCKED
        )
        locked_ratio = locked_count / setting_count if setting_count > 0 else 0

        menu_count = len(self.game_state.menus)

        return DifficultyMetrics(
            setting_count=setting_count,
            dependency_count=dependency_count,
            dependency_density=dependency_density,
            avg_chain_length=avg_chain_length,
            max_chain_length=max_chain_length,
            circular_dependencies=circular_count,
            locked_settings_ratio=locked_ratio,
            menu_count=menu_count
        )

    def _calculate_chain_lengths(self) -> List[int]:
        """Calculate dependency chain lengths"""
        lengths = []

        def get_depth(setting_id: str, visited: set) -> int:
            if setting_id in visited:
                return 0

            visited.add(setting_id)

            deps = self.game_state.resolver.dependencies.get(setting_id, [])
            if not deps:
                return 0

            max_depth = 0
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    depth = get_depth(dep.setting_id, visited.copy())
                    max_depth = max(max_depth, depth)

            return max_depth + 1

        for setting_id in self.game_state.settings:
            lengths.append(get_depth(setting_id, set()))

        return lengths

    def _count_circular_dependencies(self) -> int:
        """Count circular dependencies"""
        count = 0
        visited = set()

        def has_cycle(setting_id: str, path: set) -> bool:
            if setting_id in path:
                return True

            if setting_id in visited:
                return False

            visited.add(setting_id)
            path.add(setting_id)

            deps = self.game_state.resolver.dependencies.get(setting_id, [])
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    if has_cycle(dep.setting_id, path.copy()):
                        return True

            return False

        for setting_id in self.game_state.settings:
            if setting_id not in visited:
                if has_cycle(setting_id, set()):
                    count += 1

        return count

    def calculate_difficulty_score(self, metrics: DifficultyMetrics) -> float:
        """Calculate overall difficulty score (0-100)"""

        # Weighted factors
        score = 0.0

        # Setting count (more settings = slightly harder)
        score += min(20, metrics.setting_count / 5)

        # Dependency density (more dependencies = harder)
        score += min(30, metrics.dependency_density * 10)

        # Chain length (longer chains = harder)
        score += min(25, metrics.avg_chain_length * 5)

        # Circular dependencies (confusing = harder)
        score += min(15, metrics.circular_dependencies * 3)

        # Locked ratio (more locked = harder)
        score += min(10, metrics.locked_settings_ratio * 10)

        return min(100, score)

    def suggest_adjustments(self, target_difficulty: float) -> List[str]:
        """Suggest adjustments to reach target difficulty"""
        current_metrics = self.analyze()
        current_difficulty = self.calculate_difficulty_score(current_metrics)

        suggestions = []

        if current_difficulty < target_difficulty:
            # Make harder
            suggestions.append(f"Add more dependencies (current density: {current_metrics.dependency_density:.2f})")
            suggestions.append("Increase dependency chain lengths")
            suggestions.append("Add more locked settings")

        elif current_difficulty > target_difficulty:
            # Make easier
            suggestions.append("Remove some dependencies")
            suggestions.append("Reduce dependency chain lengths")
            suggestions.append("Unlock some settings by default")

        return suggestions

    def generate_report(self) -> str:
        """Generate difficulty analysis report"""
        metrics = self.analyze()
        difficulty = self.calculate_difficulty_score(metrics)

        lines = []
        lines.append("=== DIFFICULTY ANALYSIS ===\n")
        lines.append(f"Overall Difficulty: {difficulty:.1f}/100\n")
        lines.append("Metrics:")
        lines.append(f"  Settings: {metrics.setting_count}")
        lines.append(f"  Dependencies: {metrics.dependency_count}")
        lines.append(f"  Dependency Density: {metrics.dependency_density:.2f}")
        lines.append(f"  Avg Chain Length: {metrics.avg_chain_length:.2f}")
        lines.append(f"  Max Chain Length: {metrics.max_chain_length}")
        lines.append(f"  Circular Dependencies: {metrics.circular_dependencies}")
        lines.append(f"  Locked Ratio: {metrics.locked_settings_ratio:.2%}")
        lines.append(f"  Menu Count: {metrics.menu_count}")

        return "\n".join(lines)
```

**Testing:**
- Difficulty calculation
- Chain length analysis
- Circular dependency counting
- Adjustment suggestions
- Report generation

**Procedural:** None (analysis tool)

---

### 9.3 Playtesting Framework
**Goal:** Systematic playtesting and feedback collection

**Files:**
- `testing/playtest_session.py`
- `testing/playtest_metrics.py`
- `tests/test_playtesting.py`

**Implementation:**
```python
import time
from dataclasses import dataclass, field
from typing import List, Dict
import json

@dataclass
class PlaytestEvent:
    """Single event during playtesting"""
    timestamp: float
    event_type: str
    details: dict

@dataclass
class PlaytestSession:
    """Complete playtest session"""
    session_id: str
    start_time: float
    end_time: float = 0.0
    events: List[PlaytestEvent] = field(default_factory=list)
    completed: bool = False
    quit_reason: str = ""

    # Metrics
    total_actions: int = 0
    total_errors: int = 0
    settings_enabled: int = 0
    time_stuck: float = 0.0  # Time spent without progress
    frustration_indicators: List[str] = field(default_factory=list)

class PlaytestTracker:
    """Tracks playtest sessions"""

    def __init__(self):
        self.current_session: Optional[PlaytestSession] = None
        self.sessions: List[PlaytestSession] = []

    def start_session(self, session_id: str):
        """Start a new playtest session"""
        self.current_session = PlaytestSession(
            session_id=session_id,
            start_time=time.time()
        )

    def record_event(self, event_type: str, details: dict):
        """Record an event in current session"""
        if not self.current_session:
            return

        event = PlaytestEvent(
            timestamp=time.time(),
            event_type=event_type,
            details=details
        )

        self.current_session.events.append(event)

        # Update metrics
        if event_type == 'action':
            self.current_session.total_actions += 1
        elif event_type == 'error':
            self.current_session.total_errors += 1
        elif event_type == 'setting_enabled':
            self.current_session.settings_enabled += 1
        elif event_type in ['rage_quit_attempt', 'help_spam', 'random_clicking']:
            self.current_session.frustration_indicators.append(event_type)

    def end_session(self, completed: bool, quit_reason: str = ""):
        """End current playtest session"""
        if not self.current_session:
            return

        self.current_session.end_time = time.time()
        self.current_session.completed = completed
        self.current_session.quit_reason = quit_reason

        # Calculate time stuck
        self.current_session.time_stuck = self._calculate_time_stuck()

        # Save session
        self.sessions.append(self.current_session)
        self.current_session = None

    def _calculate_time_stuck(self) -> float:
        """Calculate time spent without progress"""
        if not self.current_session:
            return 0.0

        time_stuck = 0.0
        last_progress_time = self.current_session.start_time

        for event in self.current_session.events:
            if event.event_type in ['setting_enabled', 'menu_unlocked', 'layer_complete']:
                # Progress made
                gap = event.timestamp - last_progress_time
                if gap > 60:  # More than 1 minute = stuck
                    time_stuck += gap - 60
                last_progress_time = event.timestamp

        return time_stuck

    def analyze_sessions(self) -> dict:
        """Analyze all playtest sessions"""
        if not self.sessions:
            return {}

        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for s in self.sessions if s.completed)
        completion_rate = completed_sessions / total_sessions if total_sessions > 0 else 0

        avg_duration = statistics.mean(
            s.end_time - s.start_time for s in self.sessions
        ) if self.sessions else 0

        avg_errors = statistics.mean(
            s.total_errors for s in self.sessions
        ) if self.sessions else 0

        avg_time_stuck = statistics.mean(
            s.time_stuck for s in self.sessions
        ) if self.sessions else 0

        frustration_frequency = sum(
            len(s.frustration_indicators) for s in self.sessions
        ) / total_sessions if total_sessions > 0 else 0

        quit_reasons = {}
        for session in self.sessions:
            if not session.completed and session.quit_reason:
                quit_reasons[session.quit_reason] = quit_reasons.get(session.quit_reason, 0) + 1

        return {
            'total_sessions': total_sessions,
            'completion_rate': completion_rate,
            'avg_duration': avg_duration,
            'avg_errors': avg_errors,
            'avg_time_stuck': avg_time_stuck,
            'frustration_frequency': frustration_frequency,
            'quit_reasons': quit_reasons
        }

    def identify_problem_areas(self) -> List[str]:
        """Identify areas that need adjustment"""
        analysis = self.analyze_sessions()
        problems = []

        if analysis.get('completion_rate', 0) < 0.5:
            problems.append("LOW COMPLETION RATE: Less than 50% of players finish")

        if analysis.get('avg_time_stuck', 0) > 300:  # 5 minutes
            problems.append("EXCESSIVE STUCK TIME: Players spend too long without progress")

        if analysis.get('frustration_frequency', 0) > 5:
            problems.append("HIGH FRUSTRATION: Many frustration indicators per session")

        if analysis.get('avg_errors', 0) > 50:
            problems.append("TOO MANY ERRORS: Average error count is very high")

        return problems

    def save_sessions(self, filepath: str):
        """Save all sessions to file"""
        data = {
            'sessions': [
                {
                    'session_id': s.session_id,
                    'start_time': s.start_time,
                    'end_time': s.end_time,
                    'completed': s.completed,
                    'quit_reason': s.quit_reason,
                    'total_actions': s.total_actions,
                    'total_errors': s.total_errors,
                    'settings_enabled': s.settings_enabled,
                    'time_stuck': s.time_stuck,
                    'frustration_indicators': s.frustration_indicators,
                    'events': [
                        {
                            'timestamp': e.timestamp,
                            'event_type': e.event_type,
                            'details': e.details
                        }
                        for e in s.events
                    ]
                }
                for s in self.sessions
            ],
            'analysis': self.analyze_sessions()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
```

**Testing:**
- Session recording
- Event tracking
- Metric calculation
- Time stuck calculation
- Problem identification
- Session serialization

**Procedural:** None (tracking tool)

---

### 9.4 Balance Tuning System
**Goal:** Tools for adjusting game balance

**Files:**
- `testing/balance_tuner.py`
- `tests/test_balance_tuner.py`

**Implementation:**
```python
class BalanceTuner:
    """Tools for adjusting game balance"""

    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def reduce_dependency_density(self, target_density: float):
        """Reduce number of dependencies to target density"""
        current_count = sum(
            len(deps) for deps in self.game_state.resolver.dependencies.values()
        )
        setting_count = len(self.game_state.settings)
        current_density = current_count / setting_count if setting_count > 0 else 0

        if current_density <= target_density:
            return  # Already at or below target

        # Calculate how many to remove
        target_count = int(target_density * setting_count)
        to_remove = current_count - target_count

        # Remove least important dependencies
        removed = 0
        for setting_id in list(self.game_state.resolver.dependencies.keys()):
            if removed >= to_remove:
                break

            deps = self.game_state.resolver.dependencies[setting_id]
            if len(deps) > 1:  # Keep at least one dependency
                # Remove one dependency
                self.game_state.resolver.dependencies[setting_id] = deps[:-1]
                removed += 1

    def unlock_starter_settings(self, count: int = 3):
        """Unlock initial settings to give players a starting point"""
        locked_settings = [
            sid for sid, s in self.game_state.settings.items()
            if s.state == SettingState.LOCKED
        ]

        # Find settings with fewest dependencies
        settings_with_deps = [
            (sid, len(self.game_state.resolver.dependencies.get(sid, [])))
            for sid in locked_settings
        ]

        settings_with_deps.sort(key=lambda x: x[1])

        # Unlock the easiest ones
        for sid, _ in settings_with_deps[:count]:
            setting = self.game_state.settings[sid]
            setting.state = SettingState.DISABLED  # Unlocked but not enabled

    def add_hints_to_dependencies(self):
        """Add helpful hints to locked settings"""
        for setting_id, deps in self.game_state.resolver.dependencies.items():
            setting = self.game_state.settings.get(setting_id)
            if not setting:
                continue

            # Build hint text
            hint_parts = []
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    dep_setting = self.game_state.settings.get(dep.setting_id)
                    if dep_setting:
                        hint_parts.append(f"Enable '{dep_setting.label}'")

            if hint_parts:
                setting.hint = "Requires: " + ", ".join(hint_parts)

    def simplify_long_chains(self, max_length: int = 5):
        """Simplify dependency chains that are too long"""
        # Find settings with long chains
        def get_chain_length(setting_id: str, visited: set) -> int:
            if setting_id in visited:
                return 0

            visited.add(setting_id)

            deps = self.game_state.resolver.dependencies.get(setting_id, [])
            if not deps:
                return 0

            max_depth = 0
            for dep in deps:
                if hasattr(dep, 'setting_id'):
                    depth = get_chain_length(dep.setting_id, visited.copy())
                    max_depth = max(max_depth, depth)

            return max_depth + 1

        for setting_id in self.game_state.settings:
            chain_length = get_chain_length(setting_id, set())

            if chain_length > max_length:
                # Remove some dependencies
                deps = self.game_state.resolver.dependencies.get(setting_id, [])
                if len(deps) > 1:
                    # Keep only the most direct dependency
                    self.game_state.resolver.dependencies[setting_id] = deps[:1]

    def rebalance_for_difficulty(self, target_difficulty: str):
        """Rebalance entire game for target difficulty"""

        if target_difficulty == "easy":
            self.unlock_starter_settings(count=5)
            self.reduce_dependency_density(target_density=0.5)
            self.simplify_long_chains(max_length=3)
            self.add_hints_to_dependencies()

        elif target_difficulty == "medium":
            self.unlock_starter_settings(count=3)
            self.reduce_dependency_density(target_density=1.0)
            self.simplify_long_chains(max_length=5)
            self.add_hints_to_dependencies()

        elif target_difficulty == "hard":
            self.unlock_starter_settings(count=1)
            # Don't reduce density
            self.simplify_long_chains(max_length=8)
            # No hints

        elif target_difficulty == "very_hard":
            # Don't unlock any starters
            # Don't reduce density
            # Don't simplify chains
            # No hints
            pass
```

**Testing:**
- Dependency reduction
- Starter setting unlocking
- Hint addition
- Chain simplification
- Difficulty presets

**Procedural:** None (tuning tool)

---

### 9.5 Automated Testing Suite
**Goal:** Comprehensive automated tests

**Files:**
- `tests/test_full_game_flow.py`
- `tests/test_generation_quality.py`
- `tests/test_ui_rendering.py`

**Full Game Flow Test:**
```python
import pytest
from ready_to_start.generation.pipeline import GenerationPipeline
from ready_to_start.testing.solvability_checker import SolvabilityChecker

class TestFullGameFlow:
    """Test complete game flow from generation to completion"""

    def test_generated_games_are_solvable(self):
        """Test that generated games can be solved"""
        pipeline = GenerationPipeline()

        # Test multiple seeds
        for seed in range(10):
            game_state = pipeline.generate(seed=seed)

            checker = SolvabilityChecker(game_state)
            assert checker.check_solvability(), \
                f"Game with seed {seed} is not solvable:\n{checker.get_report()}"

    def test_difficulty_progression(self):
        """Test that difficulty increases appropriately"""
        from ready_to_start.testing.difficulty_analyzer import DifficultyAnalyzer

        pipeline = GenerationPipeline()

        # Generate games for different layers (complexity increases)
        difficulties = []

        for layer_depth in range(5):
            game_state = pipeline.generate(seed=layer_depth * 1000)
            analyzer = DifficultyAnalyzer(game_state)
            metrics = analyzer.analyze()
            difficulty = analyzer.calculate_difficulty_score(metrics)
            difficulties.append(difficulty)

        # Check that difficulty generally increases
        # (allowing for some variation)
        assert difficulties[-1] > difficulties[0], \
            f"Difficulty should increase: {difficulties}"

    def test_layer_transitions(self):
        """Test transitioning between layers"""
        from ready_to_start.core.layer_manager import LayerManager

        layer_mgr = LayerManager()
        layer_mgr.load_layers("data/interface_layers.json")

        # Start at first layer
        start_layer = "modern_settings_2020s"
        layer_mgr.start_at_layer(start_layer)

        # Should be able to transition to next layer
        next_options = layer_mgr.get_next_layer_options({})
        assert len(next_options) > 0, "Should have next layer options"

        # Transition should succeed
        success = layer_mgr.transition_to_layer(next_options[0])
        assert success, "Transition should succeed"

        # Layer depth should increase
        assert layer_mgr.get_layer_depth() == 2

    def test_complete_playthrough(self):
        """Test a complete playthrough (simulated)"""
        pipeline = GenerationPipeline()
        game_state = pipeline.generate(seed=42)

        # Simulate enabling all settings
        enabled_count = 0

        for _ in range(1000):  # Max iterations
            # Find a setting we can enable
            for setting_id, setting in game_state.settings.items():
                if setting.state == SettingState.ENABLED:
                    continue

                # Check dependencies
                deps = game_state.resolver.dependencies.get(setting_id, [])
                can_enable = all(
                    game_state.settings[dep.setting_id].state == SettingState.ENABLED
                    for dep in deps
                    if hasattr(dep, 'setting_id')
                )

                if can_enable:
                    setting.state = SettingState.ENABLED
                    enabled_count += 1
                    break
            else:
                # No more settings can be enabled
                break

        # Should have enabled most settings
        total_settings = len(game_state.settings)
        completion_rate = enabled_count / total_settings
        assert completion_rate > 0.8, \
            f"Should enable at least 80% of settings, got {completion_rate:.1%}"
```

**Testing:**
- Multiple seed generation
- Solvability verification
- Difficulty progression
- Layer transitions
- Complete playthroughs

**Procedural:** None (test suite)

---

## Helper Scripts

### Batch Solvability Checker
**File:** `scripts/check_solvability.py`
```python
#!/usr/bin/env python3
"""Check solvability of multiple generated games"""

from ready_to_start.generation.pipeline import GenerationPipeline
from ready_to_start.testing.solvability_checker import SolvabilityChecker

def check_multiple_seeds(num_seeds: int = 100):
    pipeline = GenerationPipeline()

    unsolvable = []

    for seed in range(num_seeds):
        print(f"\rChecking seed {seed+1}/{num_seeds}...", end='', flush=True)

        game_state = pipeline.generate(seed=seed)
        checker = SolvabilityChecker(game_state)

        if not checker.check_solvability():
            unsolvable.append((seed, checker.errors))

    print()

    if unsolvable:
        print(f"\n✗ Found {len(unsolvable)} unsolvable games:")
        for seed, errors in unsolvable[:5]:  # Show first 5
            print(f"\n  Seed {seed}:")
            for error in errors:
                print(f"    - {error}")
    else:
        print(f"\n✓ All {num_seeds} seeds are solvable!")

if __name__ == "__main__":
    check_multiple_seeds()
```

### Difficulty Report Generator
**File:** `scripts/generate_difficulty_report.py`
```python
#!/usr/bin/env python3
"""Generate difficulty analysis for multiple seeds"""

from ready_to_start.generation.pipeline import GenerationPipeline
from ready_to_start.testing.difficulty_analyzer import DifficultyAnalyzer
import statistics

def generate_report(num_seeds: int = 50):
    pipeline = GenerationPipeline()

    difficulties = []

    for seed in range(num_seeds):
        game_state = pipeline.generate(seed=seed)
        analyzer = DifficultyAnalyzer(game_state)
        metrics = analyzer.analyze()
        difficulty = analyzer.calculate_difficulty_score(metrics)
        difficulties.append(difficulty)

    print("\n=== DIFFICULTY REPORT ===\n")
    print(f"Analyzed {num_seeds} generated games\n")
    print(f"Average Difficulty: {statistics.mean(difficulties):.1f}/100")
    print(f"Min Difficulty: {min(difficulties):.1f}/100")
    print(f"Max Difficulty: {max(difficulties):.1f}/100")
    print(f"Std Deviation: {statistics.stdev(difficulties):.1f}")

    # Distribution
    ranges = [(0, 25), (25, 50), (50, 75), (75, 100)]
    print("\nDistribution:")
    for low, high in ranges:
        count = sum(1 for d in difficulties if low <= d < high)
        percentage = (count / num_seeds) * 100
        bar = "█" * int(percentage / 5)
        print(f"  {low:3d}-{high:3d}: {bar:20s} {count:3d} ({percentage:.1f}%)")

if __name__ == "__main__":
    generate_report()
```

### Balance Adjustment Tool
**File:** `scripts/adjust_balance.py`
```python
#!/usr/bin/env python3
"""Interactive balance adjustment tool"""

import sys
from ready_to_start.generation.pipeline import GenerationPipeline
from ready_to_start.testing.balance_tuner import BalanceTuner
from ready_to_start.testing.difficulty_analyzer import DifficultyAnalyzer

def interactive_balance(seed: int = 42):
    pipeline = GenerationPipeline()
    game_state = pipeline.generate(seed=seed)

    tuner = BalanceTuner(game_state)
    analyzer = DifficultyAnalyzer(game_state)

    print("\n=== BALANCE ADJUSTMENT TOOL ===\n")

    while True:
        metrics = analyzer.analyze()
        difficulty = analyzer.calculate_difficulty_score(metrics)

        print(f"\nCurrent Difficulty: {difficulty:.1f}/100")
        print(f"  Settings: {metrics.setting_count}")
        print(f"  Dependencies: {metrics.dependency_count}")
        print(f"  Density: {metrics.dependency_density:.2f}")
        print(f"  Avg Chain: {metrics.avg_chain_length:.2f}")

        print("\nOptions:")
        print("  1. Reduce dependency density")
        print("  2. Unlock starter settings")
        print("  3. Simplify long chains")
        print("  4. Add dependency hints")
        print("  5. Rebalance to difficulty preset")
        print("  q. Quit")

        choice = input("\nSelect option: ").strip().lower()

        if choice == '1':
            target = float(input("Target density: "))
            tuner.reduce_dependency_density(target)
            print("✓ Dependency density reduced")

        elif choice == '2':
            count = int(input("Number to unlock: "))
            tuner.unlock_starter_settings(count)
            print(f"✓ Unlocked {count} starter settings")

        elif choice == '3':
            max_len = int(input("Max chain length: "))
            tuner.simplify_long_chains(max_len)
            print("✓ Long chains simplified")

        elif choice == '4':
            tuner.add_hints_to_dependencies()
            print("✓ Hints added")

        elif choice == '5':
            print("Presets: easy, medium, hard, very_hard")
            preset = input("Select preset: ").strip().lower()
            tuner.rebalance_for_difficulty(preset)
            print(f"✓ Rebalanced to {preset}")

        elif choice == 'q':
            break

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    interactive_balance(seed)
```

---

## Phase 9 Completion Criteria

- [ ] Solvability checker implemented
- [ ] All generated games verified solvable
- [ ] Difficulty analyzer functional
- [ ] Difficulty scoring accurate
- [ ] Playtesting framework implemented
- [ ] Balance tuning tools working
- [ ] Automated test suite passing
- [ ] Multiple difficulty presets defined
- [ ] Batch testing scripts functional
- [ ] Problem area identification working
- [ ] 100+ playtests completed
- [ ] Balance adjustments applied
- [ ] Completion rate > 60%
- [ ] Average stuck time < 5 minutes
- [ ] Frustration indicators minimized
