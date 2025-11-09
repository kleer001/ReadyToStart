# Ready to Start - Phase 1 Detailed Roadmap

## Phase 1: Core Systems Foundation

### 1.1 Project Setup
**Goal:** Basic Python project structure

**Tasks:**
- Initialize project with `pyproject.toml` (use Poetry or pip-tools)
- Create directory structure:
  ```
  ready_to_start/
    core/          # Core systems
    generation/    # Generation (Phase 2)
    ui/            # UI (Phase 4)
    data/          # JSON templates
    tests/
  ```
- Setup pytest for testing
- Add pre-commit hooks (black, ruff)

**Libraries:**
- Python 3.11+
- pytest
- pytest-cov (coverage)
- black (formatting)
- ruff (linting)

**Procedural:** Project template generation script

---

### 1.2 Setting Type System
**Goal:** Core data structures for all setting types

**Files:**
- `core/types.py` - Setting type definitions
- `core/enums.py` - State enums
- `tests/test_types.py`

**Implementation:**
```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class SettingState(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    HIDDEN = "hidden"
    LOCKED = "locked"
    BLINKING = "blinking"

class SettingType(Enum):
    BOOLEAN = "bool"
    INTEGER = "int"
    FLOAT = "float"
    STRING = "string"

@dataclass
class Setting:
    id: str
    type: SettingType
    value: Any
    state: SettingState
    label: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    visit_count: int = 0
    last_modified: Optional[float] = None
```

**Testing:**
- Unit tests for each type
- State transition validation
- Value bounds checking
- Type coercion tests

**Procedural:** None (core definitions)

---

### 1.3 Menu Node Structure
**Goal:** Container for settings and navigation

**Files:**
- `core/menu.py`
- `tests/test_menu.py`

**Implementation:**
```python
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class CompletionState(Enum):
    INCOMPLETE = "incomplete"
    PARTIAL = "partial"
    COMPLETE = "complete"

@dataclass
class MenuNode:
    id: str
    category: str
    settings: List[Setting] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # Node IDs
    requirements: List[Dict] = field(default_factory=list)
    hidden_triggers: List[Dict] = field(default_factory=list)
    visited: bool = False
    completion_state: CompletionState = CompletionState.INCOMPLETE
    
    def add_setting(self, setting: Setting) -> None:
        self.settings.append(setting)
    
    def is_accessible(self, game_state: 'GameState') -> bool:
        # Check if requirements met
        pass
    
    def calculate_completion(self) -> CompletionState:
        # Evaluate setting states
        pass
```

**Testing:**
- Node creation/initialization
- Setting addition
- Connection management
- Completion calculation

**Procedural:** Menu template instantiation

---

### 1.4 State Machine
**Goal:** Manage setting state transitions

**Files:**
- `core/state_machine.py`
- `tests/test_state_machine.py`

**Implementation:**
```python
class SettingStateMachine:
    """Manages valid state transitions"""
    
    TRANSITIONS = {
        SettingState.DISABLED: [SettingState.ENABLED, SettingState.HIDDEN],
        SettingState.ENABLED: [SettingState.DISABLED, SettingState.LOCKED],
        SettingState.LOCKED: [SettingState.ENABLED],
        SettingState.HIDDEN: [SettingState.DISABLED, SettingState.ENABLED],
        SettingState.BLINKING: [SettingState.ENABLED, SettingState.DISABLED]
    }
    
    @staticmethod
    def can_transition(from_state: SettingState, to_state: SettingState) -> bool:
        return to_state in SettingStateMachine.TRANSITIONS.get(from_state, [])
    
    @staticmethod
    def transition(setting: Setting, new_state: SettingState) -> bool:
        if SettingStateMachine.can_transition(setting.state, new_state):
            setting.state = new_state
            return True
        return False
```

**Testing:**
- Valid transition tests
- Invalid transition blocking
- State history tracking
- Edge cases

**Procedural:** None (logic only)

---

### 1.5 Dependency Resolver
**Goal:** Evaluate and enforce setting dependencies

**Files:**
- `core/dependencies.py`
- `tests/test_dependencies.py`

**Implementation:**
```python
from typing import Protocol, Dict, Any

class Dependency(Protocol):
    def evaluate(self, game_state: 'GameState') -> bool:
        ...

class SimpleDependency:
    """A requires B to be in state X"""
    def __init__(self, setting_id: str, required_state: SettingState):
        self.setting_id = setting_id
        self.required_state = required_state
    
    def evaluate(self, game_state: 'GameState') -> bool:
        setting = game_state.get_setting(self.setting_id)
        return setting.state == self.required_state if setting else False

class ValueDependency:
    """A.value must be > B.value"""
    def __init__(self, setting_a: str, operator: str, setting_b: str):
        self.setting_a = setting_a
        self.operator = operator  # ">", "<", "==", "!="
        self.setting_b = setting_b
    
    def evaluate(self, game_state: 'GameState') -> bool:
        a = game_state.get_setting(self.setting_a)
        b = game_state.get_setting(self.setting_b)
        # Implement comparison logic
        pass

class DependencyResolver:
    def __init__(self):
        self.dependencies: Dict[str, List[Dependency]] = {}
    
    def add_dependency(self, setting_id: str, dependency: Dependency):
        if setting_id not in self.dependencies:
            self.dependencies[setting_id] = []
        self.dependencies[setting_id].append(dependency)
    
    def can_enable(self, setting_id: str, game_state: 'GameState') -> bool:
        deps = self.dependencies.get(setting_id, [])
        return all(dep.evaluate(game_state) for dep in deps)
    
    def resolve_all(self, game_state: 'GameState') -> Dict[str, bool]:
        """Check all settings against dependencies"""
        results = {}
        for setting_id in self.dependencies:
            results[setting_id] = self.can_enable(setting_id, game_state)
        return results
```

**Testing:**
- Simple dependency resolution
- Value comparisons
- Circular dependency detection
- Complex dependency chains

**Procedural:** Dependency graph generation

---

### 1.6 Game State Manager
**Goal:** Central state storage and queries

**Files:**
- `core/game_state.py`
- `tests/test_game_state.py`

**Implementation:**
```python
from typing import Dict, Optional, List

class GameState:
    """Central game state management"""
    
    def __init__(self):
        self.menus: Dict[str, MenuNode] = {}
        self.settings: Dict[str, Setting] = {}
        self.current_menu: Optional[str] = None
        self.visited_menus: List[str] = []
        self.resolver = DependencyResolver()
    
    def add_menu(self, menu: MenuNode):
        self.menus[menu.id] = menu
        for setting in menu.settings:
            self.settings[setting.id] = setting
    
    def get_setting(self, setting_id: str) -> Optional[Setting]:
        return self.settings.get(setting_id)
    
    def get_menu(self, menu_id: str) -> Optional[MenuNode]:
        return self.menus.get(menu_id)
    
    def navigate_to(self, menu_id: str) -> bool:
        menu = self.get_menu(menu_id)
        if menu and menu.is_accessible(self):
            self.current_menu = menu_id
            self.visited_menus.append(menu_id)
            menu.visited = True
            return True
        return False
    
    def update_setting(self, setting_id: str, value: Any) -> bool:
        setting = self.get_setting(setting_id)
        if setting and self.resolver.can_enable(setting_id, self):
            setting.value = value
            setting.visit_count += 1
            import time
            setting.last_modified = time.time()
            return True
        return False
```

**Testing:**
- State initialization
- Menu navigation
- Setting updates
- Query operations
- State persistence (JSON serialization)

**Procedural:** None (runtime state)

---

### 1.7 Basic Menu Navigation
**Goal:** Simple text-based menu system

**Files:**
- `core/navigator.py`
- `tests/test_navigator.py`

**Implementation:**
```python
class MenuNavigator:
    """Handle menu navigation logic"""
    
    def __init__(self, game_state: GameState):
        self.state = game_state
    
    def get_available_options(self) -> List[str]:
        """Get accessible menus from current location"""
        current = self.state.get_menu(self.state.current_menu)
        if not current:
            return []
        
        available = []
        for menu_id in current.connections:
            menu = self.state.get_menu(menu_id)
            if menu and menu.is_accessible(self.state):
                available.append(menu_id)
        return available
    
    def can_navigate_to(self, menu_id: str) -> bool:
        return menu_id in self.get_available_options()
    
    def navigate(self, menu_id: str) -> bool:
        if self.can_navigate_to(menu_id):
            return self.state.navigate_to(menu_id)
        return False
```

**Testing:**
- Navigation validation
- Available options calculation
- Dead-end detection
- Backtracking support

**Procedural:** None (navigation logic)

---

## Helper Scripts

### Build Script
**File:** `scripts/build.sh`
```bash
#!/bin/bash
# Format, lint, test, coverage
black ready_to_start/
ruff check ready_to_start/
pytest tests/ --cov=ready_to_start --cov-report=html
```

### Test Data Generator
**File:** `scripts/generate_test_data.py`
**Purpose:** Create sample menus/settings for testing

**Procedural:** ✓ Generates test fixtures

### Dependency Visualizer
**File:** `scripts/visualize_deps.py`
**Purpose:** Graph dependency chains for debugging
**Library:** graphviz or networkx

**Procedural:** ✓ Reads game state, outputs graph

---

## Testing Strategy

### Unit Tests
- Test each class in isolation
- Mock dependencies
- Focus on edge cases
- Use pytest fixtures for common setups

### Integration Tests
- Test class interactions
- Full dependency resolution
- Menu navigation flows
- State persistence

### Test Fixtures
**File:** `tests/conftest.py`
```python
import pytest

@pytest.fixture
def sample_setting():
    return Setting(
        id="test_setting",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Test Setting"
    )

@pytest.fixture
def sample_menu(sample_setting):
    menu = MenuNode(id="test_menu", category="Test")
    menu.add_setting(sample_setting)
    return menu

@pytest.fixture
def game_state(sample_menu):
    state = GameState()
    state.add_menu(sample_menu)
    return state
```

---

## Libraries Summary

**Core:**
- Python 3.11+ (dataclasses, typing)
- No external runtime dependencies for Phase 1

**Development:**
- pytest (testing)
- pytest-cov (coverage)
- black (formatting)
- ruff (linting)
- pre-commit (git hooks)

**Optional:**
- networkx (dependency visualization)
- graphviz (graph rendering)

---

## Phase 1 Completion Criteria

- [ ] All setting types implemented and tested
- [ ] Menu node structure complete
- [ ] State machine validates transitions
- [ ] Dependency resolver handles basic cases
- [ ] Game state manager functional
- [ ] Text-based navigation works
- [ ] 80%+ test coverage
- [ ] All tests pass
- [ ] Documentation in docstrings
- [ ] Helper scripts functional
