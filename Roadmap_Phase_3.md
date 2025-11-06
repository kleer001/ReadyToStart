# Ready to Start - Phase 3 Detailed Roadmap

## Phase 3: Game Logic

### 3.1 Dependency Evaluation Engine
**Goal:** Real-time dependency checking and state updates

**Files:**
- `core/evaluator.py`
- `tests/test_evaluator.py`

**Implementation:**
```python
from typing import Dict, Set, List
from dataclasses import dataclass

@dataclass
class EvaluationResult:
    setting_id: str
    can_enable: bool
    blocking_deps: List[str]
    reason: str

class DependencyEvaluator:
    """Real-time dependency evaluation"""
    
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.cache: Dict[str, EvaluationResult] = {}
        self.dirty: Set[str] = set()
    
    def invalidate_cache(self, setting_id: str):
        """Mark setting and dependents as needing re-evaluation"""
        self.dirty.add(setting_id)
        # Find all settings that depend on this one
        for sid, deps in self.state.resolver.dependencies.items():
            for dep in deps:
                if hasattr(dep, 'setting_id') and dep.setting_id == setting_id:
                    self.dirty.add(sid)
    
    def evaluate(self, setting_id: str) -> EvaluationResult:
        """Check if setting can be enabled"""
        if setting_id in self.cache and setting_id not in self.dirty:
            return self.cache[setting_id]
        
        setting = self.state.get_setting(setting_id)
        if not setting:
            return EvaluationResult(setting_id, False, [], "Setting not found")
        
        deps = self.state.resolver.dependencies.get(setting_id, [])
        blocking = []
        
        for dep in deps:
            if not dep.evaluate(self.state):
                blocking.append(self._get_dep_description(dep))
        
        result = EvaluationResult(
            setting_id=setting_id,
            can_enable=len(blocking) == 0,
            blocking_deps=blocking,
            reason="" if not blocking else f"Blocked by: {', '.join(blocking)}"
        )
        
        self.cache[setting_id] = result
        self.dirty.discard(setting_id)
        return result
    
    def _get_dep_description(self, dep: Dependency) -> str:
        """Human-readable dependency description"""
        if isinstance(dep, SimpleDependency):
            return f"{dep.setting_id} must be {dep.required_state.value}"
        elif isinstance(dep, ValueDependency):
            return f"{dep.setting_a} {dep.operator} {dep.setting_b}"
        return str(dep)
    
    def evaluate_all(self) -> Dict[str, EvaluationResult]:
        """Evaluate all settings"""
        results = {}
        for setting_id in self.state.settings:
            results[setting_id] = self.evaluate(setting_id)
        return results
```

**Testing:**
- Cache invalidation
- Dependency chain evaluation
- Circular dependency detection
- Performance with large graphs

**Procedural:** None (runtime logic)

---

### 3.2 State Propagation System
**Goal:** Automatic state changes based on actions

**Files:**
- `core/propagation.py`
- `tests/test_propagation.py`

**Implementation:**
```python
from typing import List, Callable
from dataclasses import dataclass

@dataclass
class PropagationRule:
    """Rule for automatic state changes"""
    trigger_setting: str
    trigger_condition: Callable[[Setting], bool]
    affected_settings: List[str]
    effect: Callable[[Setting], None]

class StatePropagator:
    """Handle cascading state changes"""
    
    def __init__(self, game_state: GameState, evaluator: DependencyEvaluator):
        self.state = game_state
        self.evaluator = evaluator
        self.rules: List[PropagationRule] = []
        self.propagation_depth = 0
        self.max_depth = 10  # Prevent infinite loops
    
    def add_rule(self, rule: PropagationRule):
        self.rules.append(rule)
    
    def propagate(self, changed_setting_id: str) -> List[str]:
        """Propagate changes from a setting modification"""
        if self.propagation_depth >= self.max_depth:
            return []
        
        self.propagation_depth += 1
        affected = []
        
        setting = self.state.get_setting(changed_setting_id)
        if not setting:
            self.propagation_depth -= 1
            return affected
        
        # Apply matching rules
        for rule in self.rules:
            if rule.trigger_setting == changed_setting_id:
                if rule.trigger_condition(setting):
                    for target_id in rule.affected_settings:
                        target = self.state.get_setting(target_id)
                        if target:
                            rule.effect(target)
                            affected.append(target_id)
                            self.evaluator.invalidate_cache(target_id)
                            # Recursively propagate
                            affected.extend(self.propagate(target_id))
        
        self.propagation_depth -= 1
        return affected
    
    def load_rules_from_config(self, config_path: str):
        """Load propagation rules from INI"""
        parser = configparser.ConfigParser()
        parser.read(config_path)
        
        for section in parser.sections():
            trigger = parser[section]['trigger_setting']
            condition_str = parser[section]['condition']
            affected = [s.strip() for s in parser[section]['affected'].split(',')]
            effect_str = parser[section]['effect']
            
            # Parse condition and effect strings into callables
            condition = self._parse_condition(condition_str)
            effect = self._parse_effect(effect_str)
            
            self.add_rule(PropagationRule(trigger, condition, affected, effect))
    
    def _parse_condition(self, cond_str: str) -> Callable:
        """Parse condition string to callable"""
        # Simple parser: "value > 50", "state == enabled"
        if "==" in cond_str:
            attr, val = cond_str.split("==")
            return lambda s: str(getattr(s, attr.strip())) == val.strip()
        elif ">" in cond_str:
            attr, val = cond_str.split(">")
            return lambda s: float(getattr(s, attr.strip())) > float(val.strip())
        return lambda s: True
    
    def _parse_effect(self, effect_str: str) -> Callable:
        """Parse effect string to callable"""
        # Simple parser: "state = disabled", "value = 0"
        if "=" in effect_str:
            attr, val = effect_str.split("=")
            attr = attr.strip()
            val = val.strip()
            return lambda s: setattr(s, attr, self._parse_value(val, type(getattr(s, attr))))
        return lambda s: None
    
    def _parse_value(self, val_str: str, target_type):
        """Convert string to appropriate type"""
        if target_type == SettingState:
            return SettingState(val_str)
        elif target_type == bool:
            return val_str.lower() == "true"
        elif target_type == int:
            return int(val_str)
        elif target_type == float:
            return float(val_str)
        return val_str
```

**Sample propagation.ini:**
```ini
[audio_affects_graphics]
trigger_setting = audio_enabled
condition = state == enabled
affected = graphics_audio_output
effect = state = enabled

[resolution_resets_refresh]
trigger_setting = resolution
condition = value > 0
affected = refresh_rate
effect = value = 60
```

**Testing:**
- Single rule application
- Chain propagation
- Infinite loop prevention
- Rule parsing from INI

**Procedural:** ✓ Rules from config

---

### 3.3 Hidden Condition Tracker
**Goal:** Track non-obvious unlock conditions

**Files:**
- `core/hidden_conditions.py`
- `tests/test_hidden_conditions.py`

**Implementation:**
```python
from typing import Dict, Callable
from dataclasses import dataclass, field

@dataclass
class HiddenCondition:
    id: str
    description: str
    check: Callable[[GameState], bool]
    triggered: bool = False
    trigger_count: int = 0

class HiddenConditionTracker:
    """Track easter eggs and hidden unlocks"""
    
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.conditions: Dict[str, HiddenCondition] = {}
        self.counters: Dict[str, int] = {}
    
    def register_condition(self, condition: HiddenCondition):
        self.conditions[condition.id] = condition
    
    def increment_counter(self, key: str):
        """Track arbitrary events"""
        self.counters[key] = self.counters.get(key, 0) + 1
    
    def check_all(self) -> List[str]:
        """Check all conditions, return newly triggered IDs"""
        newly_triggered = []
        
        for cond_id, condition in self.conditions.items():
            if not condition.triggered and condition.check(self.state):
                condition.triggered = True
                condition.trigger_count += 1
                newly_triggered.append(cond_id)
        
        return newly_triggered
    
    def load_from_config(self, config_path: str):
        """Load hidden conditions from INI"""
        parser = configparser.ConfigParser()
        parser.read(config_path)
        
        for section in parser.sections():
            cond_id = section
            description = parser[section]['description']
            check_str = parser[section]['check']
            
            # Parse check string
            check_func = self._parse_check(check_str)
            
            self.register_condition(
                HiddenCondition(cond_id, description, check_func)
            )
    
    def _parse_check(self, check_str: str) -> Callable:
        """Parse check condition from string"""
        # Examples:
        # "counter:menu_visits > 10"
        # "setting:audio_volume == 42"
        # "visited:Audio,Graphics,Network"
        
        if check_str.startswith("counter:"):
            parts = check_str[8:].split()
            counter_name = parts[0]
            operator = parts[1]
            value = int(parts[2])
            
            def counter_check(state):
                count = self.counters.get(counter_name, 0)
                if operator == ">":
                    return count > value
                elif operator == "==":
                    return count == value
                elif operator == ">=":
                    return count >= value
                return False
            
            return counter_check
        
        elif check_str.startswith("setting:"):
            # Parse setting condition
            parts = check_str[8:].split()
            setting_id = parts[0]
            operator = parts[1]
            value = parts[2]
            
            return lambda state: self._check_setting(state, setting_id, operator, value)
        
        elif check_str.startswith("visited:"):
            menus = check_str[8:].split(',')
            return lambda state: all(m.strip() in state.visited_menus for m in menus)
        
        return lambda state: False
    
    def _check_setting(self, state: GameState, setting_id: str, op: str, value: str) -> bool:
        setting = state.get_setting(setting_id)
        if not setting:
            return False
        
        if op == "==":
            return str(setting.value) == value
        elif op == ">":
            return float(setting.value) > float(value)
        return False
```

**Sample hidden_conditions.ini:**
```ini
[persistent_visitor]
description = Visit the same menu 5 times
check = counter:menu_revisits > 5

[magic_number]
description = Set volume to exactly 42
check = setting:audio_volume == 42

[completionist]
description = Visit all essential menus
check = visited:Audio,Graphics,User,Network
```

**Testing:**
- Counter tracking
- Condition evaluation
- Config parsing
- Multiple trigger detection

**Procedural:** ✓ Conditions from config

---

### 3.4 Progress Calculator
**Goal:** Determine completion percentage

**Files:**
- `core/progress.py`
- `tests/test_progress.py`

**Implementation:**
```python
from typing import Dict

class ProgressCalculator:
    """Calculate game completion metrics"""
    
    def __init__(self, game_state: GameState, evaluator: DependencyEvaluator):
        self.state = game_state
        self.evaluator = evaluator
    
    def calculate_overall_progress(self) -> float:
        """Calculate total completion (intentionally misleading)"""
        total_settings = len(self.state.settings)
        if total_settings == 0:
            return 0.0
        
        # Count "configured" settings
        configured = sum(
            1 for s in self.state.settings.values()
            if s.state in [SettingState.ENABLED, SettingState.LOCKED]
        )
        
        # Add misleading boost
        visited_bonus = len(self.state.visited_menus) * 0.5
        
        raw_progress = (configured + visited_bonus) / total_settings
        return min(99.0, raw_progress * 100)  # Cap at 99%
    
    def calculate_menu_completion(self, menu_id: str) -> CompletionState:
        """Determine menu completion state"""
        menu = self.state.get_menu(menu_id)
        if not menu:
            return CompletionState.INCOMPLETE
        
        total = len(menu.settings)
        if total == 0:
            return CompletionState.COMPLETE
        
        enabled = sum(
            1 for s in menu.settings
            if s.state == SettingState.ENABLED
        )
        
        if enabled == 0:
            return CompletionState.INCOMPLETE
        elif enabled == total:
            return CompletionState.COMPLETE
        else:
            return CompletionState.PARTIAL
    
    def get_critical_path_progress(self) -> float:
        """Progress along critical path specifically"""
        # Requires knowing critical path from generation
        # For now, simplified version
        visited_count = len(self.state.visited_menus)
        total_menus = len(self.state.menus)
        
        return (visited_count / total_menus) * 100 if total_menus > 0 else 0.0
    
    def is_victory_condition_met(self) -> bool:
        """Check if player has "won" current layer"""
        # Simple version: all critical settings enabled
        results = self.evaluator.evaluate_all()
        
        # Count critical settings (marked during generation)
        critical_enabled = 0
        critical_total = 0
        
        for setting_id, setting in self.state.settings.items():
            # Check if setting was marked critical during generation
            # For now, check if it has dependencies (heuristic)
            if setting_id in self.state.resolver.dependencies:
                critical_total += 1
                if setting.state == SettingState.ENABLED:
                    critical_enabled += 1
        
        return critical_total > 0 and critical_enabled == critical_total
```

**Testing:**
- Progress calculation accuracy
- Menu completion states
- Victory detection
- Edge cases (no settings, all disabled)

**Procedural:** None (calculation logic)

---

### 3.5 Victory Condition Detector
**Goal:** Determine when to transition layers

**Files:**
- `core/victory.py`
- `tests/test_victory.py`

**Implementation:**
```python
from enum import Enum

class VictoryType(Enum):
    NONE = "none"
    PARTIAL = "partial"
    COMPLETE = "complete"
    SECRET = "secret"

@dataclass
class VictoryCondition:
    victory_type: VictoryType
    requirements: List[Callable[[GameState], bool]]
    next_layer: Optional[str] = None

class VictoryDetector:
    """Detect victory conditions and layer transitions"""
    
    def __init__(self, game_state: GameState, progress_calc: ProgressCalculator):
        self.state = game_state
        self.progress = progress_calc
        self.conditions: List[VictoryCondition] = []
        self.current_layer = 0
    
    def add_condition(self, condition: VictoryCondition):
        self.conditions.append(condition)
    
    def check_victory(self) -> Optional[VictoryCondition]:
        """Check if any victory condition met"""
        for condition in self.conditions:
            if all(req(self.state) for req in condition.requirements):
                return condition
        return None
    
    def load_from_config(self, config_path: str):
        """Load victory conditions from INI"""
        parser = configparser.ConfigParser()
        parser.read(config_path)
        
        for section in parser.sections():
            victory_type = VictoryType(parser[section]['type'])
            req_strings = parser[section]['requirements'].split('&&')
            next_layer = parser[section].get('next_layer', None)
            
            requirements = [self._parse_requirement(r.strip()) for r in req_strings]
            
            self.add_condition(
                VictoryCondition(victory_type, requirements, next_layer)
            )
    
    def _parse_requirement(self, req_str: str) -> Callable:
        """Parse requirement string to callable"""
        # Examples:
        # "progress > 95"
        # "critical_path_complete"
        # "menu:Audio == complete"
        
        if req_str == "critical_path_complete":
            return lambda state: self.progress.is_victory_condition_met()
        
        elif req_str.startswith("progress"):
            parts = req_str.split()
            threshold = float(parts[2])
            return lambda state: self.progress.calculate_overall_progress() >= threshold
        
        elif req_str.startswith("menu:"):
            parts = req_str.split()
            menu_id = parts[0][5:]
            required_state = CompletionState(parts[2])
            return lambda state: self.progress.calculate_menu_completion(menu_id) == required_state
        
        return lambda state: False
```

**Sample victory.ini:**
```ini
[standard_victory]
type = complete
requirements = critical_path_complete && progress > 90
next_layer = radio_1940s

[impatient_victory]
type = partial
requirements = progress > 50 && menu:Audio == complete
next_layer = tv_1950s

[secret_victory]
type = secret
requirements = hidden:magic_number && hidden:completionist
next_layer = developer_console
```

**Testing:**
- Condition parsing
- Multiple requirement evaluation
- Victory detection
- Layer transition logic

**Procedural:** ✓ Conditions from config

---

### 3.6 Session State Manager
**Goal:** Track session data and metrics

**Files:**
- `core/session.py`
- `tests/test_session.py`

**Implementation:**
```python
import time
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class SessionMetrics:
    start_time: float = field(default_factory=time.time)
    settings_viewed: int = 0
    settings_modified: int = 0
    menus_visited: int = 0
    clicks: int = 0
    hovers: int = 0
    total_time: float = 0.0
    progress_percentage: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'duration': time.time() - self.start_time,
            'settings_viewed': self.settings_viewed,
            'settings_modified': self.settings_modified,
            'menus_visited': self.menus_visited,
            'clicks': self.clicks,
            'hovers': self.hovers,
            'progress': self.progress_percentage
        }

class SessionManager:
    """Track session state and statistics"""
    
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.metrics = SessionMetrics()
        self.events: List[Dict] = []
    
    def record_event(self, event_type: str, data: Dict = None):
        """Log game event"""
        event = {
            'type': event_type,
            'timestamp': time.time(),
            'data': data or {}
        }
        self.events.append(event)
        
        # Update metrics
        if event_type == "setting_viewed":
            self.metrics.settings_viewed += 1
        elif event_type == "setting_modified":
            self.metrics.settings_modified += 1
        elif event_type == "menu_visited":
            self.metrics.menus_visited += 1
        elif event_type == "click":
            self.metrics.clicks += 1
        elif event_type == "hover":
            self.metrics.hovers += 1
    
    def update_progress(self, progress: float):
        """Update current progress"""
        self.metrics.progress_percentage = progress
    
    def get_efficiency_score(self) -> float:
        """Calculate 'efficiency' (always terrible)"""
        if self.metrics.settings_modified == 0:
            return 0.0
        
        # Intentionally poor calculation
        base = (self.metrics.settings_modified / 
                max(1, self.metrics.settings_viewed)) * 100
        
        # Penalties for normal behavior
        time_penalty = min(50, (time.time() - self.metrics.start_time) / 60)
        click_penalty = min(30, self.metrics.clicks / 10)
        
        return max(1.0, base - time_penalty - click_penalty)
    
    def serialize(self) -> Dict:
        """Export session data"""
        return {
            'metrics': self.metrics.to_dict(),
            'efficiency': self.get_efficiency_score(),
            'events': self.events[-100:]  # Last 100 events
        }
    
    def save_to_file(self, filepath: str):
        """Save session to JSON"""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.serialize(), f, indent=2)
```

**Testing:**
- Event recording
- Metric updates
- Efficiency calculation
- Serialization
- File I/O

**Procedural:** None (session tracking)

---

## Helper Scripts

### Logic Tester
**File:** `scripts/test_logic.py`
```python
#!/usr/bin/env python3
from generation.pipeline import GenerationPipeline
from core.evaluator import DependencyEvaluator
from core.propagation import StatePropagator

def test_game_logic():
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=42)
    
    evaluator = DependencyEvaluator(state)
    propagator = StatePropagator(state, evaluator)
    
    print("Testing dependency evaluation...")
    results = evaluator.evaluate_all()
    print(f"  Total settings: {len(results)}")
    print(f"  Can enable: {sum(1 for r in results.values() if r.can_enable)}")
    
    print("\nTesting propagation...")
    first_setting = list(state.settings.keys())[0]
    affected = propagator.propagate(first_setting)
    print(f"  Affected settings: {len(affected)}")

if __name__ == "__main__":
    test_game_logic()
```

### Session Analyzer
**File:** `scripts/analyze_session.py`
```python
#!/usr/bin/env python3
import json
import sys

def analyze_session(filepath: str):
    with open(filepath) as f:
        data = json.load(f)
    
    metrics = data['metrics']
    print(f"Duration: {metrics['duration']:.1f}s")
    print(f"Settings viewed: {metrics['settings_viewed']}")
    print(f"Settings modified: {metrics['settings_modified']}")
    print(f"Efficiency: {data['efficiency']:.1f}%")
    print(f"Progress: {metrics['progress']:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: analyze_session.py <session.json>")
    else:
        analyze_session(sys.argv[1])
```

---

## Config Files

**config/propagation.ini** - State propagation rules
**config/hidden_conditions.ini** - Easter egg conditions  
**config/victory.ini** - Victory conditions

---

## Libraries Summary

**Core:**
- time (stdlib)
- json (stdlib)
- configparser (stdlib)

**No new external dependencies**

---

## Phase 3 Completion Criteria

- [ ] Dependency evaluation with caching
- [ ] State propagation with rules
- [ ] Hidden condition tracking
- [ ] Progress calculation (misleading)
- [ ] Victory detection
- [ ] Session metrics tracking
- [ ] All logic configurable via INI
- [ ] Propagation depth limiting
- [ ] 80%+ test coverage
- [ ] Helper scripts functional
