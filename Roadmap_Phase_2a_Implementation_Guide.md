# Phase 2a Implementation Guide

## Overview
Phase 2a fixes two critical bugs in the procedural generation system:
1. Dependencies generating at wrong level (menu vs setting)
2. Unreliable graph generation (~20% failure rate)

**Estimated Time:** 4-6 hours
**Prerequisites:** Phase 2 complete, tests passing
**Skills Required:** Python, graph algorithms, test-driven development

---

## Pre-Implementation Checklist

- [ ] Read Phase 2 implementation
- [ ] Understand WFC algorithm basics
- [ ] Review dependency system in `core/dependencies.py`
- [ ] Run `python scripts/test_generation.py` to observe current bugs
- [ ] Confirm all Phase 2 tests pass

---

## Bug Analysis

### Bug 1: Zero Dependencies
**Observe:**
```bash
python scripts/test_generation.py
# Output shows: Dependencies: 0
```

**Root Cause:**
- `DependencyGenerator.generate_dependencies()` returns dict keyed by menu node IDs (e.g., "Audio_2_3")
- `GameState.resolver` expects setting IDs (e.g., "Audio_2_3_setting_0")
- Mismatch means dependencies never apply to actual settings

**Verify in code:**
- Check `generation/dep_generator.py` line 49: returns `deps[next_node]`
- Check `generation/pipeline.py` line 60: passes to `resolver.add_dependency(setting_id, dep)`
- Note the ID mismatch

### Bug 2: Invalid Graph Generation
**Observe:**
```bash
python scripts/test_generation.py --runs 20
# ~20% show: ERROR: Generated invalid graph
```

**Root Cause:**
- WFC can reach contradictions (cell with 0 entropy, not collapsed)
- No retry mechanism when WFC fails
- Validation doesn't check minimum viable graph size

**Verify in code:**
- Check `generation/wfc.py` line 123: `break` on contradiction (doesn't retry)
- Check `generation/pipeline.py` line 34: raises on first failure (doesn't retry)
- Check `generation/topology.py` line 19: doesn't check minimum node count

---

## Implementation Plan

### Step 1: Add WFC Contradiction Handling (45 min)

**File:** `ready_to_start/generation/wfc.py`

**Task 1.1:** Create exception class
```python
# Add at top of file after imports
class ContradictionError(Exception):
    """Raised when WFC reaches an unresolvable state"""
    pass
```

**Task 1.2:** Add retry field to WFCGenerator
```python
class WFCGenerator:
    def __init__(self, rules: dict[str, dict[str, list[str]]], config: GenerationConfig):
        self.rules = rules
        self.config = config
        self.grid = WFCGrid(width=5, height=5)
        self.max_retries = 3  # ADD THIS LINE
```

**Task 1.3:** Extract generation logic to `_generate_once()`
- Rename current `generate()` method to `_generate_once()`
- Have it raise `ContradictionError` instead of breaking on contradiction

```python
def _generate_once(self) -> WFCGrid:
    all_categories = set(self.rules.keys())
    self.initialize(all_categories)

    start_pos = (self.grid.width // 2, self.grid.height // 2)
    start_cell = self.grid.cells[start_pos]
    start_cell.collapse()
    self.propagate(start_cell)

    max_iterations = self.grid.width * self.grid.height * 2
    iterations = 0

    while not self.grid.is_complete() and iterations < max_iterations:
        if self.grid.has_contradiction():
            raise ContradictionError("WFC reached contradiction")  # CHANGE THIS

        cell = self.grid.get_lowest_entropy_cell()
        if not cell:
            break

        cell.collapse()
        self.propagate(cell)
        iterations += 1

    return self.grid
```

**Task 1.4:** Create new `generate()` with retry logic
```python
def generate(self) -> WFCGrid:
    """Generate with retry on contradiction"""
    for attempt in range(self.max_retries):
        self.grid = WFCGrid(width=5, height=5)  # Fresh grid each attempt

        try:
            return self._generate_once()
        except ContradictionError:
            if attempt == self.max_retries - 1:
                return self.grid  # Return partial on last attempt
            continue

    return self.grid
```

**Acceptance Criteria:**
- [ ] `ContradictionError` defined
- [ ] `generate()` retries up to 3 times
- [ ] Existing WFC tests still pass
- [ ] No new test failures

**Verify:**
```bash
python -m pytest tests/test_wfc.py -v
```

---

### Step 2: Add Pipeline Retry Mechanism (30 min)

**File:** `ready_to_start/generation/pipeline.py`

**Task 2.1:** Extract generation logic to `_generate_once()`
- Rename current `generate()` body to `_generate_once()`
- Keep all current logic unchanged

```python
def _generate_once(self) -> GameState:
    wfc = WFCGenerator(self.wfc_rules, self.config)
    grid = wfc.generate()

    converter = TopologyConverter(self.config)
    graph = converter.grid_to_graph(grid)

    if not converter.validate_graph():
        raise ValueError("Generated invalid graph")

    # ... rest of current generate() logic ...

    return game_state
```

**Task 2.2:** Create new `generate()` with retry wrapper
```python
def generate(self, seed: int | None = None) -> GameState:
    if seed is not None:
        random.seed(seed)

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            return self._generate_once()
        except ValueError:
            if attempt == max_attempts - 1:
                raise
            continue

    raise ValueError("Failed to generate valid game after max attempts")
```

**Acceptance Criteria:**
- [ ] `generate()` retries up to 5 times
- [ ] Seed still works correctly
- [ ] Existing pipeline tests still pass

**Verify:**
```bash
python -m pytest tests/test_pipeline.py -v
```

---

### Step 3: Strengthen Graph Validation (20 min)

**File:** `ready_to_start/generation/topology.py`

**Task 3.1:** Add minimum node check
```python
def validate_graph(self) -> bool:
    if not self.graph.nodes():
        return False

    # NEW: Must have minimum nodes for viable game
    if len(self.graph.nodes()) < 3:
        return False

    if not nx.is_weakly_connected(self.graph):
        return False

    return self._has_valid_critical_path()
```

**Acceptance Criteria:**
- [ ] Graphs with <3 nodes rejected
- [ ] Existing topology tests still pass

**Verify:**
```bash
python -m pytest tests/test_topology.py -v
python scripts/test_generation.py --runs 20
# Should see 0 invalid graph errors
```

---

### Step 4: Fix Dependency Generation (90 min)

**File:** `ready_to_start/generation/dep_generator.py`

**Task 4.1:** Update constructor to accept menus
```python
class DependencyGenerator:
    def __init__(
        self,
        graph: nx.DiGraph,
        config: GenerationConfig,
        menus: dict[str, MenuNode]  # ADD THIS
    ):
        self.graph = graph
        self.config = config
        self.menus = menus  # ADD THIS
        self.critical_path: list[str] = []
```

**Task 4.2:** Add menu navigation dependencies
```python
def _add_menu_navigation_dependencies(
    self, deps: dict[str, list[Dependency]]
) -> None:
    """Require completing a menu before accessing its children"""
    for node_id in self.graph.nodes():
        successors = list(self.graph.successors(node_id))
        if not successors:
            continue

        menu = self.menus.get(node_id)
        if not menu or not menu.settings:
            continue

        critical_setting = menu.settings[0]

        for successor_id in successors:
            successor_menu = self.menus.get(successor_id)
            if successor_menu and successor_menu.settings:
                target_setting = successor_menu.settings[0]
                if target_setting.id not in deps:
                    deps[target_setting.id] = []
                deps[target_setting.id].append(
                    SimpleDependency(critical_setting.id, SettingState.ENABLED)
                )
```

**Task 4.3:** Update critical path dependencies for settings
```python
def _add_critical_path_dependencies(
    self, deps: dict[str, list[Dependency]]
) -> None:
    """Add dependencies along critical path settings"""
    for i in range(len(self.critical_path) - 1):
        current_menu_id = self.critical_path[i]
        next_menu_id = self.critical_path[i + 1]

        current_menu = self.menus.get(current_menu_id)
        next_menu = self.menus.get(next_menu_id)

        if not current_menu or not next_menu:
            continue
        if not current_menu.settings or not next_menu.settings:
            continue

        current_setting = random.choice(current_menu.settings)
        next_setting = random.choice(next_menu.settings)

        if next_setting.id not in deps:
            deps[next_setting.id] = []

        deps[next_setting.id].append(
            SimpleDependency(current_setting.id, SettingState.ENABLED)
        )
```

**Task 4.4:** Update cross dependencies for settings
```python
def _add_cross_dependencies(self, deps: dict[str, list[Dependency]]) -> None:
    """Add dependencies between non-connected settings"""
    all_settings = []
    for menu in self.menus.values():
        all_settings.extend(menu.settings)

    if not all_settings:
        return

    num_cross = min(int(len(all_settings) * 0.1), 20)

    for _ in range(num_cross):
        setting_a = random.choice(all_settings)
        setting_b = random.choice(all_settings)

        if setting_a.id != setting_b.id:
            if setting_b.id not in deps:
                deps[setting_b.id] = []
            deps[setting_b.id].append(
                SimpleDependency(setting_a.id, SettingState.ENABLED)
            )
```

**Task 4.5:** Update generate_dependencies to call new method
```python
def generate_dependencies(self) -> dict[str, list[Dependency]]:
    self.critical_path = self._find_critical_path()
    deps = {}

    self._add_menu_navigation_dependencies(deps)  # ADD THIS
    self._add_critical_path_dependencies(deps)
    self._add_cross_dependencies(deps)

    return deps
```

**Acceptance Criteria:**
- [ ] Dependencies keyed by setting IDs, not menu IDs
- [ ] Three types of dependencies generated
- [ ] Returns dict with >0 entries

---

### Step 5: Update Pipeline to Pass Menus (15 min)

**File:** `ready_to_start/generation/pipeline.py`

**Task 5.1:** Pass menus to DependencyGenerator
Find this line in `_generate_once()`:
```python
dep_gen = DependencyGenerator(graph, self.config)
```

Change to:
```python
dep_gen = DependencyGenerator(graph, self.config, game_state.menus)
```

**Acceptance Criteria:**
- [ ] DependencyGenerator receives menus dict
- [ ] Pipeline tests pass

---

### Step 6: Update Tests (60 min)

**File:** `tests/test_dep_generator.py`

**Task 6.1:** Add fixture for test menus
```python
@pytest.fixture
def simple_menus(self):
    menus = {}
    for node_id in ["A", "B", "C"]:
        menu = MenuNode(id=node_id, category="Test", connections=[])
        for i in range(3):
            setting = Setting(
                id=f"{node_id}_setting_{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.ENABLED,
                label=f"{node_id} Setting {i}",
            )
            menu.add_setting(setting)
        menus[node_id] = menu
    return menus
```

**Task 6.2:** Update all test methods to pass menus
For each test method, add `simple_menus` parameter and pass to constructor:
```python
def test_find_critical_path(self, config, simple_graph, simple_menus):
    gen = DependencyGenerator(simple_graph, config, simple_menus)
    # ... rest of test
```

**Task 6.3:** Update test assertions for setting-level deps
Change assertions that check for menu node IDs to check for setting IDs:
```python
# OLD: assert "B" in deps
# NEW: Check that deps keys are setting IDs
assert len(deps) > 0
for setting_id in deps.keys():
    assert "_setting_" in setting_id  # Verify it's a setting ID
```

**Acceptance Criteria:**
- [ ] All dependency generator tests pass
- [ ] Tests verify setting-level dependencies
- [ ] Add imports: `SettingType`, `MenuNode`, `Setting`

---

### Step 7: Format and Lint (10 min)

```bash
black ready_to_start/generation/
ruff check ready_to_start/generation/
```

**Fix any issues:**
- Line length >88 characters
- Unused imports
- Type annotation issues

**Acceptance Criteria:**
- [ ] Black reports no formatting needed
- [ ] Ruff reports all checks passed

---

### Step 8: Full Test Suite (10 min)

```bash
python -m pytest tests/ -v
```

**Expected Results:**
- [ ] All 125 tests pass
- [ ] Coverage ≥93%
- [ ] No new warnings

---

### Step 9: Integration Testing (20 min)

**Run generation test:**
```bash
python scripts/test_generation.py --runs 20
```

**Expected Results:**
- [ ] 20/20 successful generations
- [ ] Dependencies: 10-44 per game (not 0!)
- [ ] No "invalid graph" errors
- [ ] Menus: 5-25 per game
- [ ] Settings: 50-290 per game

**Verify determinism:**
```bash
python scripts/test_generation.py --runs 2
# Run twice with same seeds, should get identical results
```

---

## Validation Checklist

### Functional Requirements
- [ ] Dependencies generate at setting level
- [ ] All games have >0 dependencies
- [ ] Graph generation 100% reliable
- [ ] Retry mechanisms work correctly
- [ ] Deterministic with seed

### Code Quality
- [ ] All tests pass (125/125)
- [ ] Coverage ≥93%
- [ ] No linting errors
- [ ] No formatting issues
- [ ] Type hints correct

### Documentation
- [ ] Update Roadmap_Phase_2a.md with completion status
- [ ] Add docstrings to new methods
- [ ] Update comments for clarity

---

## Common Issues & Solutions

### Issue: Tests fail after adding menus parameter
**Solution:** Update ALL test calls to DependencyGenerator, including fixtures

### Issue: Dependencies still showing as 0
**Solution:** Verify pipeline passes `game_state.menus` not `graph.nodes()`

### Issue: Some WFC attempts still fail
**Solution:** Check `max_retries` is 3+, verify fresh grid created each attempt

### Issue: Circular dependency in imports
**Solution:** Import `MenuNode` in function scope if needed, not module level

### Issue: Random seed not working correctly
**Solution:** Ensure `random.seed()` called BEFORE retry loop in pipeline

---

## Commit Strategy

**Commit 1: WFC retry mechanism**
```
Add WFC contradiction handling and retry mechanism

- Add ContradictionError exception
- Implement retry logic in WFCGenerator.generate()
- Extract _generate_once() for clean separation
- Tests: test_wfc.py passes
```

**Commit 2: Pipeline retry mechanism**
```
Add pipeline retry mechanism for invalid graphs

- Extract _generate_once() in GenerationPipeline
- Implement 5-attempt retry logic
- Improve validation with min node check
- Tests: test_pipeline.py passes
```

**Commit 3: Setting-level dependencies**
```
Fix dependency generation to work at setting level

- Update DependencyGenerator to accept menus dict
- Implement menu navigation dependencies
- Update critical path and cross dependencies for settings
- Update pipeline to pass menus to generator
- Tests: test_dep_generator.py updated and passing
```

**Commit 4: Polish and integration**
```
Phase 2a: Bug fixes complete

- Format with black
- Lint with ruff
- All 125 tests passing
- 20/20 generation runs successful
- Dependencies: 10-44 per game (was 0)
```

---

## Success Metrics

### Before Phase 2a
- Dependencies: 0
- Invalid graphs: ~20%
- Coverage: 93%

### After Phase 2a
- Dependencies: 10-44
- Invalid graphs: 0%
- Coverage: ≥93%

### Performance
- Average generation time: <100ms
- Max retries needed: <5

---

## Next Steps After Completion

1. Run extended test: `python scripts/test_generation.py --runs 100`
2. Create pull request with changes
3. Update Phase 3 roadmap with Phase 2a learnings
4. Consider: Should WFC grid size be configurable?
5. Consider: Should dependency ratios be tunable?

---

## Resources

- Wave Function Collapse: https://github.com/mxgmn/WaveFunctionCollapse
- NetworkX docs: https://networkx.org/documentation/stable/
- Dependency injection patterns in Python
- Graph validation techniques

---

## Time Estimates

| Task | Est. Time | Actual Time |
|------|-----------|-------------|
| 1. WFC retry | 45 min | _____ |
| 2. Pipeline retry | 30 min | _____ |
| 3. Graph validation | 20 min | _____ |
| 4. Dependency fix | 90 min | _____ |
| 5. Pipeline update | 15 min | _____ |
| 6. Test updates | 60 min | _____ |
| 7. Format/lint | 10 min | _____ |
| 8. Test suite | 10 min | _____ |
| 9. Integration | 20 min | _____ |
| **Total** | **5 hrs** | **_____** |

---

## Notes

_Use this space for implementation notes, gotchas, or insights discovered during implementation._
