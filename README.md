# Ready to Start

A procedural menu-based puzzle game where players navigate through interconnected settings menus with dynamic dependencies and state changes.

## Current Status: Phase 2 Complete ✓

Phase 1 and Phase 2 have been successfully implemented with all core systems and procedural generation in place.

### Implemented Features

#### Phase 1: Core Systems
- **Core Type System**: Setting types (boolean, integer, float, string) with state management
- **Menu Node Structure**: Hierarchical menu organization with connections and requirements
- **State Machine**: Validates and manages state transitions for settings
- **Dependency Resolver**: Handles simple and value-based dependencies between settings
- **Game State Manager**: Central state storage with navigation tracking
- **Menu Navigator**: Navigation logic with accessibility checking

#### Phase 2: Procedural Generation
- **Wave Function Collapse**: Grid-based topology generation with constraint propagation
- **Topology Converter**: Transforms WFC grids into directed menu graphs
- **Mad Libs Engine**: Template-based content generation for settings and labels
- **Setting Compiler**: Generates settings based on category configurations
- **Dependency Generator**: Creates logical dependencies with cycle detection
- **Generation Pipeline**: Orchestrates full game state generation from seed values
- **Graph Analyzer**: Utility for critical path finding and graph analysis

#### Code Quality
- **180 unit tests** with comprehensive coverage
- **SOLID principles** applied throughout
- **DRY code** with shared utilities and zero duplication
- **KISS design** with focused, single-purpose methods

### Project Structure

```
ready_to_start/
├── core/              # Core game systems
│   ├── config_loader.py    # INI configuration loading
│   ├── enums.py           # State and type enumerations
│   ├── types.py           # Setting data structures
│   ├── menu.py            # Menu node implementation
│   ├── state_machine.py   # State transition logic
│   ├── dependencies.py    # Dependency resolution
│   ├── game_state.py      # Central state management
│   └── navigator.py       # Navigation logic
├── generation/        # ✓ Procedural generation (Phase 2)
│   ├── wfc.py            # Wave Function Collapse algorithm
│   ├── topology.py       # Grid-to-graph conversion
│   ├── graph_analyzer.py # Graph utilities and critical paths
│   ├── madlibs.py        # Template-based content generation
│   ├── compiler.py       # Setting compilation
│   ├── dep_generator.py  # Dependency generation
│   └── pipeline.py       # Generation orchestration
├── ui/               # (Phase 3) User interface
└── data/             # JSON templates and data

config/               # INI configuration files
tests/                # 180 unit tests
scripts/              # Helper scripts
```

### Getting Started

#### Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

#### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_pipeline.py -v
```

#### Quick Demo

```bash
# Run the game (if UI is available)
python start.py

# Generate a procedural game with seed
python -c "from ready_to_start.generation.pipeline import GenerationPipeline; \
           p = GenerationPipeline(); \
           state = p.generate(seed=42); \
           print(f'Generated {len(state.menus)} menus with {len(state.settings)} settings')"
```

### Development

#### Code Quality

The project uses:
- **Black** for code formatting
- **Ruff** for linting
- **pytest** for testing with coverage reporting
- **pre-commit** hooks for automated checks

#### Running Checks

```bash
# Format code
python -m black ready_to_start/ tests/

# Lint code
python -m ruff check ready_to_start/ tests/ --fix

# Run tests
python -m pytest tests/
```

### Development Roadmap

- ✓ **Phase 1**: Core game systems and data structures
- ✓ **Phase 2**: Procedural generation pipeline
- **Phase 3**: User interface and rendering (In Progress)
- **Phase 4**: Polish and gameplay refinement

See [Roadmap_Phase_2.md](Roadmap_Phase_2.md) for Phase 2 implementation details and [Roadmap_BirdseyeView.md](Roadmap_BirdseyeView.md) for the overall project roadmap.

**Coming in Phase 3**: Terminal-based UI with menu navigation, setting editors, and visual feedback.

## License

MIT License - See [LICENSE](LICENSE) for details.
