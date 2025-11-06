# Ready to Start - Phase 2a Bug Fixes

## Issues Identified

### Issue 1: Dependencies Not Created (Critical)
**Symptom:** All generated games show 0 dependencies
**Root Cause:** DependencyGenerator creates dependencies keyed by menu node IDs (e.g., "Audio_2_3"), but the game expects setting IDs (e.g., "Audio_2_3_setting_0")
**Impact:** Game is unplayable - no constraints between settings

### Issue 2: Invalid Graph Generation (~20% failure rate)
**Symptom:** WFC occasionally generates graphs that fail validation
**Root Cause:**
- WFC can produce incomplete grids with contradictions
- Grids may not have sufficient path length after conversion
- No retry mechanism when validation fails
**Impact:** Inconsistent generation, wasted computation

---

## Phase 2a: Reliability Fixes

### 2a.1 Fix Dependency Generation
**Goal:** Generate dependencies at setting level, not menu level

**Changes to `generation/dep_generator.py`:**
```python
class DependencyGenerator:
    def __init__(self, graph: nx.DiGraph, config: GenerationConfig, menus: dict[str, MenuNode]):
        self.graph = graph
        self.config = config
        self.menus = menus
        self.critical_path: list[str] = []

    def generate_dependencies(self) -> dict[str, list[Dependency]]:
        self.critical_path = self._find_critical_path()
        deps = {}

        self._add_menu_navigation_dependencies(deps)
        self._add_critical_path_dependencies(deps)
        self._add_cross_dependencies(deps)

        return deps

    def _add_menu_navigation_dependencies(self, deps: dict[str, list[Dependency]]) -> None:
        """Require completing a menu before accessing its children"""
        for node_id in self.graph.nodes():
            successors = list(self.graph.successors(node_id))
            if not successors:
                continue

            menu = self.menus.get(node_id)
            if not menu or not menu.settings:
                continue

            # Pick a critical setting from current menu
            critical_setting = menu.settings[0]

            # All successor menus depend on this setting
            for successor_id in successors:
                successor_menu = self.menus.get(successor_id)
                if successor_menu and successor_menu.settings:
                    # First setting of successor depends on current
                    target_setting = successor_menu.settings[0]
                    if target_setting.id not in deps:
                        deps[target_setting.id] = []
                    deps[target_setting.id].append(
                        SimpleDependency(critical_setting.id, SettingState.ENABLED)
                    )

    def _add_critical_path_dependencies(self, deps: dict[str, list[Dependency]]) -> None:
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

            # Pick random settings from each menu
            current_setting = random.choice(current_menu.settings)
            next_setting = random.choice(next_menu.settings)

            if next_setting.id not in deps:
                deps[next_setting.id] = []

            deps[next_setting.id].append(
                SimpleDependency(current_setting.id, SettingState.ENABLED)
            )

    def _add_cross_dependencies(self, deps: dict[str, list[Dependency]]) -> None:
        """Add dependencies between non-connected settings"""
        all_settings = []
        for menu in self.menus.values():
            all_settings.extend(menu.settings)

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

**Changes to `generation/pipeline.py`:**
```python
def generate(self, seed: int | None = None) -> GameState:
    if seed is not None:
        random.seed(seed)

    # Generate with retry mechanism
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            game_state = self._generate_once()
            return game_state
        except ValueError as e:
            if attempt == max_attempts - 1:
                raise
            continue

    raise ValueError("Failed to generate valid game after max attempts")

def _generate_once(self) -> GameState:
    wfc = WFCGenerator(self.wfc_rules, self.config)
    grid = wfc.generate()

    converter = TopologyConverter(self.config)
    graph = converter.grid_to_graph(grid)

    if not converter.validate_graph():
        raise ValueError("Generated invalid graph")

    converter.prune_dead_ends()

    game_state = GameState()
    critical_path = converter.get_critical_path()

    for node_id in graph.nodes():
        category = graph.nodes[node_id]["category"]
        is_critical = node_id in critical_path

        menu = MenuNode(
            id=node_id,
            category=category,
            connections=list(graph.successors(node_id)),
        )

        settings = self.compiler.compile_settings(node_id, category, is_critical)
        for setting in settings:
            menu.add_setting(setting)

        game_state.add_menu(menu)

    # FIXED: Pass menus to DependencyGenerator
    dep_gen = DependencyGenerator(graph, self.config, game_state.menus)
    dependencies = dep_gen.generate_dependencies()

    # FIXED: Now dependencies have setting IDs as keys
    for setting_id, deps in dependencies.items():
        for dep in deps:
            game_state.resolver.add_dependency(setting_id, dep)

    start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
    game_state.current_menu = (
        start_nodes[0] if start_nodes else list(graph.nodes())[0]
    )

    return game_state
```

---

### 2a.2 Improve WFC Reliability
**Goal:** Reduce invalid graph generation to <5%

**Changes to `generation/wfc.py`:**
```python
class WFCGenerator:
    def __init__(
        self, rules: dict[str, dict[str, list[str]]], config: GenerationConfig
    ):
        self.rules = rules
        self.config = config
        self.grid = WFCGrid(width=5, height=5)
        self.max_retries = 3

    def generate(self) -> WFCGrid:
        """Generate with retry on contradiction"""
        for attempt in range(self.max_retries):
            self.grid = WFCGrid(width=5, height=5)

            try:
                return self._generate_once()
            except ContradictionError:
                if attempt == self.max_retries - 1:
                    # Last attempt: return partial grid
                    return self.grid
                continue

        return self.grid

    def _generate_once(self) -> WFCGrid:
        all_categories = set(self.rules.keys())
        self.initialize(all_categories)

        # Start from center
        start_pos = (self.grid.width // 2, self.grid.height // 2)
        start_cell = self.grid.cells[start_pos]
        start_cell.collapse()
        self.propagate(start_cell)

        max_iterations = self.grid.width * self.grid.height * 2
        iterations = 0

        while not self.grid.is_complete() and iterations < max_iterations:
            if self.grid.has_contradiction():
                raise ContradictionError("WFC reached contradiction")

            cell = self.grid.get_lowest_entropy_cell()
            if not cell:
                break

            cell.collapse()
            self.propagate(cell)
            iterations += 1

        return self.grid

class ContradictionError(Exception):
    """Raised when WFC reaches an unresolvable state"""
    pass
```

**Changes to `generation/topology.py`:**
```python
def validate_graph(self) -> bool:
    """Validate graph meets requirements"""
    if not self.graph.nodes():
        return False

    # Must have minimum nodes
    if len(self.graph.nodes()) < 3:
        return False

    # Must be connected
    if not nx.is_weakly_connected(self.graph):
        return False

    # Must have valid critical path
    return self._has_valid_critical_path()
```

---

## Testing Strategy

### Unit Tests
- `test_dep_generator.py`: Verify setting-level dependencies
- `test_pipeline.py`: Verify retry mechanism
- `test_wfc.py`: Verify contradiction handling

### Integration Tests
```python
def test_generated_game_has_dependencies():
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=42)

    # Should have dependencies
    assert len(state.resolver.dependencies) > 0

    # Dependencies should reference actual settings
    for setting_id in state.resolver.dependencies:
        assert setting_id in state.settings

def test_generation_retry_on_invalid_graph():
    pipeline = GenerationPipeline()

    # Should succeed within max attempts
    for i in range(100):
        state = pipeline.generate(seed=i)
        assert len(state.menus) >= 3
        assert len(state.settings) > 0
        assert len(state.resolver.dependencies) > 0
```

---

## Success Criteria

- [ ] 100% of generations have dependencies > 0
- [ ] <5% invalid graph generation rate
- [ ] All existing tests pass
- [ ] New tests for dependency generation pass
- [ ] Average generation time < 100ms
- [ ] Deterministic with seed

---

## Implementation Order

1. Add ContradictionError to wfc.py
2. Implement retry in WFCGenerator.generate()
3. Update DependencyGenerator constructor to accept menus
4. Implement setting-level dependency generation
5. Update pipeline to pass menus to DependencyGenerator
6. Add retry mechanism to pipeline.generate()
7. Add integration tests
8. Run full test suite
9. Run 100 generation test runs
