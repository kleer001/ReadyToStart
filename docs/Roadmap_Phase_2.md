# Ready to Start - Phase 2 Detailed Roadmap

## Phase 2: Generation Pipeline

### 2.1 Configuration System
**Goal:** INI-based configuration for all generation parameters

**Files:**
- `config/wfc_rules.ini` - WFC constraints
- `config/templates.ini` - Mad Libs templates
- `config/categories.ini` - Menu category definitions
- `config/generation.ini` - Generation parameters
- `core/config_loader.py` - Config parser
- `tests/test_config_loader.py`

**Implementation:**
```python
import configparser
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class GenerationConfig:
    min_path_length: int
    max_depth: int
    required_categories: int
    gate_distribution: float
    critical_ratio: float
    decoy_ratio: float
    noise_ratio: float

class ConfigLoader:
    def __init__(self, config_dir: str = "config/"):
        self.config_dir = config_dir
        self.parser = configparser.ConfigParser()
    
    def load_generation_params(self) -> GenerationConfig:
        self.parser.read(f"{self.config_dir}generation.ini")
        section = self.parser['generation']
        return GenerationConfig(
            min_path_length=section.getint('min_path_length'),
            max_depth=section.getint('max_depth'),
            required_categories=section.getint('required_categories'),
            gate_distribution=section.getfloat('gate_distribution'),
            critical_ratio=section.getfloat('critical_ratio'),
            decoy_ratio=section.getfloat('decoy_ratio'),
            noise_ratio=section.getfloat('noise_ratio')
        )
    
    def load_wfc_rules(self) -> Dict[str, List[str]]:
        self.parser.read(f"{self.config_dir}wfc_rules.ini")
        rules = {}
        for section in self.parser.sections():
            rules[section] = [
                item.strip() 
                for item in self.parser[section]['connections'].split(',')
            ]
        return rules
    
    def load_templates(self) -> Dict[str, List[str]]:
        self.parser.read(f"{self.config_dir}templates.ini")
        templates = {}
        for section in self.parser.sections():
            templates[section] = [
                self.parser[section][key] 
                for key in self.parser[section]
            ]
        return templates
```

**Sample INI Files:**

`config/generation.ini`:
```ini
[generation]
min_path_length = 5
max_depth = 15
required_categories = 10
gate_distribution = 0.3
critical_ratio = 0.25
decoy_ratio = 0.35
noise_ratio = 0.40
```

`config/wfc_rules.ini`:
```ini
[Audio]
connections = Graphics, User, Network
requires = 

[Graphics]
connections = Audio, Display, Performance
requires = Audio

[User]
connections = Security, Privacy, Profile
requires = Audio, Graphics
```

`config/templates.ini`:
```ini
[requirement_templates]
template1 = {category} requires {requirement} to be {state}
template2 = Cannot {action} while {condition}
template3 = {setting} must be {comparison} {other_setting}

[error_templates]
template1 = Error: {setting} incompatible with {other_setting}
template2 = Warning: {action} may cause {consequence}
```

`config/categories.ini`:
```ini
[Audio]
setting_count = 8
complexity = 2
dependencies = 

[Graphics]
setting_count = 12
complexity = 3
dependencies = Audio

[Network]
setting_count = 6
complexity = 4
dependencies = Security, Privacy
```

**Testing:**
- Config loading validation
- Missing file handling
- Malformed INI handling
- Default value fallback

**Procedural:** ✓ All generation rules configurable

---

### 2.2 Wave Function Collapse Core
**Goal:** WFC algorithm for menu topology

**Files:**
- `generation/wfc.py`
- `generation/wfc_types.py`
- `tests/test_wfc.py`

**Libraries:**
- No external dependencies (pure Python)

**Implementation:**
```python
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional
import random
from enum import Enum

class CellState(Enum):
    COLLAPSED = "collapsed"
    SUPERPOSITION = "superposition"

@dataclass
class WFCCell:
    """Represents a menu node position in generation"""
    position: tuple  # (x, y) coordinate
    possible_states: Set[str]  # Possible menu categories
    collapsed: bool = False
    state: Optional[str] = None
    entropy: float = float('inf')
    
    def collapse(self) -> str:
        """Collapse to single state"""
        self.state = random.choice(list(self.possible_states))
        self.collapsed = True
        self.possible_states = {self.state}
        self.entropy = 0
        return self.state
    
    def constrain(self, allowed: Set[str]):
        """Remove invalid possibilities"""
        self.possible_states &= allowed
        self.entropy = len(self.possible_states)

@dataclass
class WFCGrid:
    """Grid of cells for WFC generation"""
    width: int
    height: int
    cells: Dict[tuple, WFCCell] = field(default_factory=dict)
    
    def __post_init__(self):
        for x in range(self.width):
            for y in range(self.height):
                self.cells[(x, y)] = WFCCell(
                    position=(x, y),
                    possible_states=set()
                )
    
    def get_neighbors(self, pos: tuple) -> List[WFCCell]:
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.cells:
                neighbors.append(self.cells[(nx, ny)])
        return neighbors
    
    def get_lowest_entropy_cell(self) -> Optional[WFCCell]:
        uncollapsed = [
            cell for cell in self.cells.values() 
            if not cell.collapsed and cell.entropy > 0
        ]
        if not uncollapsed:
            return None
        return min(uncollapsed, key=lambda c: c.entropy)

class WFCGenerator:
    def __init__(self, rules: Dict[str, List[str]], config: GenerationConfig):
        self.rules = rules  # From INI
        self.config = config
        self.grid = WFCGrid(width=5, height=5)  # Adjustable
    
    def initialize(self, all_categories: Set[str]):
        """Set initial possibilities for all cells"""
        for cell in self.grid.cells.values():
            cell.possible_states = all_categories.copy()
            cell.entropy = len(all_categories)
    
    def propagate(self, cell: WFCCell):
        """Propagate constraints to neighbors"""
        queue = [cell]
        visited = set()
        
        while queue:
            current = queue.pop(0)
            if current.position in visited:
                continue
            visited.add(current.position)
            
            if not current.collapsed:
                continue
            
            # Get valid neighbor states based on rules
            valid_neighbors = set(self.rules.get(current.state, []))
            
            for neighbor in self.grid.get_neighbors(current.position):
                if neighbor.collapsed:
                    continue
                
                old_entropy = neighbor.entropy
                neighbor.constrain(valid_neighbors)
                
                if neighbor.entropy < old_entropy and neighbor.entropy > 0:
                    queue.append(neighbor)
    
    def generate(self) -> WFCGrid:
        """Run WFC algorithm"""
        all_categories = set(self.rules.keys())
        self.initialize(all_categories)
        
        # Start with random cell
        start_pos = (self.grid.width // 2, self.grid.height // 2)
        start_cell = self.grid.cells[start_pos]
        start_cell.collapse()
        self.propagate(start_cell)
        
        # Iteratively collapse cells
        while True:
            cell = self.grid.get_lowest_entropy_cell()
            if not cell:
                break
            
            if cell.entropy == 0:
                # Contradiction - backtrack or restart
                # For now, just break
                break
            
            cell.collapse()
            self.propagate(cell)
        
        return self.grid
```

**Testing:**
- Grid initialization
- Constraint propagation
- Entropy calculation
- Contradiction handling
- Complete generation runs

**Procedural:** ✓ Generates topology from rules

---

### 2.3 Topology Converter
**Goal:** Convert WFC grid to menu graph

**Files:**
- `generation/topology.py`
- `tests/test_topology.py`

**Implementation:**
```python
from typing import Dict, List, Set
import networkx as nx

class TopologyConverter:
    """Convert WFC grid to menu graph"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.graph = nx.DiGraph()
    
    def grid_to_graph(self, grid: WFCGrid) -> nx.DiGraph:
        """Convert collapsed grid to directed graph"""
        # Add nodes
        for pos, cell in grid.cells.items():
            if cell.collapsed:
                self.graph.add_node(
                    f"{cell.state}_{pos[0]}_{pos[1]}",
                    category=cell.state,
                    position=pos
                )
        
        # Add edges based on adjacency
        for pos, cell in grid.cells.items():
            if not cell.collapsed:
                continue
            
            node_id = f"{cell.state}_{pos[0]}_{pos[1]}"
            
            for neighbor in grid.get_neighbors(pos):
                if neighbor.collapsed:
                    neighbor_id = f"{neighbor.state}_{neighbor.position[0]}_{neighbor.position[1]}"
                    self.graph.add_edge(node_id, neighbor_id)
        
        return self.graph
    
    def validate_graph(self) -> bool:
        """Ensure graph is valid (connected, acyclic paths exist)"""
        if not nx.is_weakly_connected(self.graph):
            return False
        
        # Check for critical path
        start_nodes = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        end_nodes = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
        
        for start in start_nodes:
            for end in end_nodes:
                if nx.has_path(self.graph, start, end):
                    path = nx.shortest_path(self.graph, start, end)
                    if len(path) >= self.config.min_path_length:
                        return True
        
        return False
    
    def prune_dead_ends(self):
        """Remove nodes with no path to victory"""
        end_nodes = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
        
        reachable = set()
        for end in end_nodes:
            ancestors = nx.ancestors(self.graph, end)
            reachable.update(ancestors)
            reachable.add(end)
        
        to_remove = set(self.graph.nodes()) - reachable
        self.graph.remove_nodes_from(to_remove)
```

**Testing:**
- Grid conversion accuracy
- Edge creation validation
- Graph connectivity
- Path validation
- Dead-end pruning

**Procedural:** ✓ Automatic graph construction

---

### 2.4 Mad Libs Engine
**Goal:** Template-based content generation

**Files:**
- `generation/madlibs.py`
- `tests/test_madlibs.py`

**Implementation:**
```python
import re
import random
from typing import Dict, List

class MadLibsEngine:
    """Fill templates with generated content"""
    
    def __init__(self, templates: Dict[str, List[str]], config_loader: ConfigLoader):
        self.templates = templates
        self.config = config_loader
        self.vocab = self._load_vocabulary()
    
    def _load_vocabulary(self) -> Dict[str, List[str]]:
        """Load word pools from config"""
        vocab = {}
        parser = configparser.ConfigParser()
        parser.read(f"{self.config.config_dir}vocabulary.ini")
        
        for section in parser.sections():
            vocab[section] = [
                parser[section][key] 
                for key in parser[section]
            ]
        return vocab
    
    def fill_template(self, template: str, context: Dict[str, str] = None) -> str:
        """Replace {placeholders} in template"""
        if context is None:
            context = {}
        
        # Find all placeholders
        placeholders = re.findall(r'\{(\w+)\}', template)
        
        result = template
        for placeholder in placeholders:
            if placeholder in context:
                value = context[placeholder]
            elif placeholder in self.vocab:
                value = random.choice(self.vocab[placeholder])
            else:
                value = f"[{placeholder}]"  # Fallback
            
            result = result.replace(f"{{{placeholder}}}", value, 1)
        
        return result
    
    def generate_requirement(self, node_id: str, category: str) -> str:
        """Generate requirement text for menu node"""
        template = random.choice(self.templates['requirement_templates'])
        context = {
            'category': category,
            'node_id': node_id
        }
        return self.fill_template(template, context)
    
    def generate_error(self, setting_id: str) -> str:
        """Generate error message"""
        template = random.choice(self.templates['error_templates'])
        context = {'setting': setting_id}
        return self.fill_template(template, context)
    
    def generate_setting_label(self, category: str, index: int) -> str:
        """Generate setting name"""
        template = random.choice(self.templates.get('setting_labels', ['{category} Setting {index}']))
        context = {
            'category': category,
            'index': str(index)
        }
        return self.fill_template(template, context)
```

**Sample vocabulary.ini:**
```ini
[action]
word1 = configure
word2 = calibrate
word3 = validate
word4 = initialize
word5 = synchronize

[condition]
word1 = system is ready
word2 = network is available
word3 = user is authenticated
word4 = drivers are loaded

[consequence]
word1 = data loss
word2 = system instability
word3 = reduced performance
word4 = unexpected behavior
```

**Testing:**
- Template parsing
- Placeholder replacement
- Context override
- Missing vocabulary handling
- Template variety

**Procedural:** ✓ Content from templates

---

### 2.5 Setting Compiler
**Goal:** Generate settings for menu nodes

**Files:**
- `generation/compiler.py`
- `tests/test_compiler.py`

**Implementation:**
```python
class SettingCompiler:
    """Generate settings based on category and requirements"""
    
    def __init__(self, config: GenerationConfig, madlibs: MadLibsEngine):
        self.config = config
        self.madlibs = madlibs
        self.categories_config = self._load_category_config()
    
    def _load_category_config(self) -> Dict[str, Dict]:
        """Load category definitions from INI"""
        parser = configparser.ConfigParser()
        parser.read("config/categories.ini")
        
        config = {}
        for section in parser.sections():
            config[section] = {
                'setting_count': parser[section].getint('setting_count'),
                'complexity': parser[section].getint('complexity'),
                'dependencies': [
                    d.strip() 
                    for d in parser[section].get('dependencies', '').split(',')
                    if d.strip()
                ]
            }
        return config
    
    def compile_settings(self, node_id: str, category: str, is_critical: bool) -> List[Setting]:
        """Generate settings for a menu node"""
        cat_config = self.categories_config.get(category, {})
        count = cat_config.get('setting_count', 8)
        
        settings = []
        for i in range(count):
            setting_type = self._choose_type(is_critical)
            label = self.madlibs.generate_setting_label(category, i)
            
            setting = Setting(
                id=f"{node_id}_setting_{i}",
                type=setting_type,
                value=self._default_value(setting_type),
                state=SettingState.DISABLED if is_critical else SettingState.ENABLED,
                label=label
            )
            
            if setting_type in [SettingType.INTEGER, SettingType.FLOAT]:
                setting.min_value = 0
                setting.max_value = 100
            
            settings.append(setting)
        
        return settings
    
    def _choose_type(self, is_critical: bool) -> SettingType:
        """Select setting type based on criticality"""
        if is_critical:
            # Critical settings favor boolean for clear pass/fail
            weights = [0.5, 0.2, 0.2, 0.1]  # bool, int, float, string
        else:
            weights = [0.25, 0.25, 0.25, 0.25]
        
        types = [SettingType.BOOLEAN, SettingType.INTEGER, SettingType.FLOAT, SettingType.STRING]
        return random.choices(types, weights=weights)[0]
    
    def _default_value(self, setting_type: SettingType) -> Any:
        """Get default value for type"""
        defaults = {
            SettingType.BOOLEAN: False,
            SettingType.INTEGER: 0,
            SettingType.FLOAT: 0.0,
            SettingType.STRING: ""
        }
        return defaults[setting_type]
```

**Testing:**
- Setting generation counts
- Type distribution
- Critical vs decoy ratios
- Value range assignment
- Label uniqueness

**Procedural:** ✓ Settings from category config

---

### 2.6 Dependency Generator
**Goal:** Create logical dependencies between settings

**Files:**
- `generation/dep_generator.py`
- `tests/test_dep_generator.py`

**Implementation:**
```python
class DependencyGenerator:
    """Generate logical dependencies for menu graph"""
    
    def __init__(self, graph: nx.DiGraph, config: GenerationConfig):
        self.graph = graph
        self.config = config
        self.critical_path = None
    
    def generate_dependencies(self) -> Dict[str, List[Dependency]]:
        """Create dependency map for all settings"""
        deps = {}
        
        # Find critical path first
        self.critical_path = self._find_critical_path()
        
        # Add dependencies along critical path
        for i in range(len(self.critical_path) - 1):
            current = self.critical_path[i]
            next_node = self.critical_path[i + 1]
            
            # Current node completion required for next
            deps[next_node] = [
                SimpleDependency(current, SettingState.ENABLED)
            ]
        
        # Add cross-dependencies for complexity
        self._add_cross_dependencies(deps)
        
        return deps
    
    def _find_critical_path(self) -> List[str]:
        """Find longest path through graph"""
        start_nodes = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        end_nodes = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
        
        longest = []
        for start in start_nodes:
            for end in end_nodes:
                if nx.has_path(self.graph, start, end):
                    path = nx.shortest_path(self.graph, start, end)
                    if len(path) > len(longest):
                        longest = path
        
        return longest
    
    def _add_cross_dependencies(self, deps: Dict[str, List[Dependency]]):
        """Add dependencies between non-sequential nodes"""
        nodes = list(self.graph.nodes())
        num_cross = int(len(nodes) * 0.2)  # 20% cross-dependencies
        
        for _ in range(num_cross):
            node_a = random.choice(nodes)
            node_b = random.choice(nodes)
            
            if node_a != node_b and not nx.has_path(self.graph, node_a, node_b):
                if node_b not in deps:
                    deps[node_b] = []
                deps[node_b].append(
                    SimpleDependency(node_a, SettingState.ENABLED)
                )
```

**Testing:**
- Critical path identification
- Dependency graph validity
- Circular dependency prevention
- Cross-dependency distribution
- Solvability validation

**Procedural:** ✓ Dependencies from graph

---

### 2.7 Generation Pipeline
**Goal:** Orchestrate full generation process

**Files:**
- `generation/pipeline.py`
- `tests/test_pipeline.py`

**Implementation:**
```python
class GenerationPipeline:
    """Orchestrate full menu generation"""
    
    def __init__(self, config_dir: str = "config/"):
        self.loader = ConfigLoader(config_dir)
        self.config = self.loader.load_generation_params()
        self.wfc_rules = self.loader.load_wfc_rules()
        self.templates = self.loader.load_templates()
        
        self.madlibs = MadLibsEngine(self.templates, self.loader)
        self.compiler = SettingCompiler(self.config, self.madlibs)
    
    def generate(self, seed: Optional[int] = None) -> GameState:
        """Run full generation pipeline"""
        if seed:
            random.seed(seed)
        
        # Phase 1: WFC topology
        wfc = WFCGenerator(self.wfc_rules, self.config)
        grid = wfc.generate()
        
        # Phase 2: Convert to graph
        converter = TopologyConverter(self.config)
        graph = converter.grid_to_graph(grid)
        
        if not converter.validate_graph():
            raise ValueError("Generated invalid graph")
        
        converter.prune_dead_ends()
        
        # Phase 3: Create menu nodes
        game_state = GameState()
        
        for node_id in graph.nodes():
            category = graph.nodes[node_id]['category']
            is_critical = node_id in converter.get_critical_path()
            
            menu = MenuNode(
                id=node_id,
                category=category,
                connections=list(graph.successors(node_id))
            )
            
            # Generate settings
            settings = self.compiler.compile_settings(node_id, category, is_critical)
            for setting in settings:
                menu.add_setting(setting)
            
            game_state.add_menu(menu)
        
        # Phase 4: Generate dependencies
        dep_gen = DependencyGenerator(graph, self.config)
        dependencies = dep_gen.generate_dependencies()
        
        for setting_id, deps in dependencies.items():
            for dep in deps:
                game_state.resolver.add_dependency(setting_id, dep)
        
        # Phase 5: Set starting menu
        start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        game_state.current_menu = start_nodes[0] if start_nodes else list(graph.nodes())[0]
        
        return game_state
```

**Testing:**
- Full pipeline execution
- Seed determinism
- Invalid graph handling
- State completeness
- Generation performance

**Procedural:** ✓ Complete generation

---

## Helper Scripts

### Generation Tester
**File:** `scripts/test_generation.py`
```python
#!/usr/bin/env python3
from generation.pipeline import GenerationPipeline

def test_generation(num_runs: int = 10):
    pipeline = GenerationPipeline()
    
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...")
        state = pipeline.generate(seed=i)
        print(f"  Menus: {len(state.menus)}")
        print(f"  Settings: {len(state.settings)}")
        print(f"  Valid: {validate_state(state)}")

if __name__ == "__main__":
    test_generation()
```

### Graph Visualizer
**File:** `scripts/visualize_graph.py`
```python
#!/usr/bin/env python3
import networkx as nx
import matplotlib.pyplot as plt
from generation.pipeline import GenerationPipeline

def visualize_generation(seed: int = 42):
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=seed)
    
    # Build nx graph from state
    G = nx.DiGraph()
    for menu_id, menu in state.menus.items():
        G.add_node(menu_id, category=menu.category)
        for conn in menu.connections:
            G.add_edge(menu_id, conn)
    
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue')
    plt.savefig(f"graph_seed_{seed}.png")
    print(f"Saved graph_seed_{seed}.png")

if __name__ == "__main__":
    visualize_generation()
```

---

## Libraries Summary

**Core:**
- configparser (stdlib)
- random (stdlib)
- re (stdlib)

**Development:**
- networkx (graph operations)
- matplotlib (visualization only)

---

## Phase 2 Completion Criteria

- [ ] INI config system functional
- [ ] WFC generates valid topologies
- [ ] Topology converts to valid graphs
- [ ] Mad Libs fills templates
- [ ] Settings compiler generates appropriate settings
- [ ] Dependencies logically sound
- [ ] Pipeline produces playable game states
- [ ] Deterministic generation (seeded)
- [ ] All config externalized to INI
- [ ] 80%+ test coverage
- [ ] Visualization scripts work
