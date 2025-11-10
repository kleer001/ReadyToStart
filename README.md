# Ready to Start

A procedural menu-based puzzle game where players navigate through interconnected settings menus with dynamic dependencies and state changes.

## Current Status: Phase 4 Complete ✓

Phases 1-4 have been successfully implemented with all core systems, procedural generation, game logic, and UI in place.

### Implemented Features

#### Phase 1: Core Systems ✓
- **Core Type System**: Setting types (boolean, integer, float, string) with state management
- **Menu Node Structure**: Hierarchical menu organization with connections and requirements
- **State Machine**: Validates and manages state transitions for settings
- **Dependency Resolver**: Handles simple and value-based dependencies between settings
- **Game State Manager**: Central state storage with navigation tracking
- **Menu Navigator**: Navigation logic with accessibility checking

#### Phase 2: Procedural Generation ✓
- **Wave Function Collapse**: Grid-based topology generation with constraint propagation
- **Topology Converter**: Transforms WFC grids into directed menu graphs
- **Mad Libs Engine**: Template-based content generation for settings and labels
- **Setting Compiler**: Generates settings based on category configurations
- **Dependency Generator**: Creates logical dependencies with cycle detection
- **Generation Pipeline**: Orchestrates full game state generation from seed values
- **Graph Analyzer**: Utility for critical path finding and graph analysis

#### Phase 3: Game Logic ✓
- **Dependency Evaluation**: Real-time dependency checking with caching
- **State Propagation**: Automatic cascading state changes based on actions
- **Progress Tracking**: Calculation of completion metrics
- **Victory Detection**: Determines when layer transitions occur
- **Session Management**: Tracks player metrics and statistics

#### Phase 4: UI Implementation ✓
- **ncurses-based Display**: Professional terminal UI with native curses support
- **Menu Renderer**: Displays menus with colored settings and state indicators
- **Setting Editors**: Type-specific editors for booleans, integers, floats, and strings
- **Navigation System**: Command-based and keyboard navigation
- **Message Display**: Error/warning/info/success message system
- **State Indicators**: Visual feedback for setting states with animations
- **Input Handling**: Native curses keyboard input (arrow keys, WASD, vim keys)
- **Main Game Loop**: Integrated UI loop with proper screen management

#### Code Quality
- **180+ unit tests** with comprehensive coverage
- **SOLID principles** applied throughout
- **DRY code** with shared utilities and zero duplication
- **KISS design** with focused, single-purpose methods
- **ncurses integration** for robust, flicker-free terminal display

### Project Structure

```
ready_to_start/
├── src/
│   ├── core/              # ✓ Core game systems (Phase 1)
│   │   ├── config_loader.py    # INI configuration loading
│   │   ├── enums.py           # State and type enumerations
│   │   ├── types.py           # Setting data structures
│   │   ├── menu.py            # Menu node implementation
│   │   ├── state_machine.py   # State transition logic
│   │   ├── dependencies.py    # Dependency resolution
│   │   ├── game_state.py      # Central state management
│   │   └── navigator.py       # Navigation logic
│   ├── generation/        # ✓ Procedural generation (Phase 2)
│   │   ├── wfc.py            # Wave Function Collapse algorithm
│   │   ├── topology.py       # Grid-to-graph conversion
│   │   ├── graph_analyzer.py # Graph utilities and critical paths
│   │   ├── madlibs.py        # Template-based content generation
│   │   ├── compiler.py       # Setting compilation
│   │   ├── dep_generator.py  # Dependency generation
│   │   └── pipeline.py       # Generation orchestration
│   ├── ui/               # ✓ User interface (Phase 4)
│   │   ├── renderer.py        # ncurses text rendering
│   │   ├── menu_display.py    # Menu component
│   │   ├── setting_editor.py  # Setting modification
│   │   ├── navigation.py      # Navigation controller
│   │   ├── messages.py        # Message display
│   │   ├── indicators.py      # State indicators
│   │   ├── input_handler.py   # Command parsing
│   │   └── main_loop.py       # Main game loop
│   ├── anti_patterns/    # (Phase 5) Deception mechanics
│   ├── meta/             # (Phase 8) Achievements, stats
│   └── testing/          # Testing framework
├── data/                 # JSON templates and content
├── config/               # INI configuration files
├── tests/                # 180+ unit tests
└── scripts/              # Gameplay testing scripts
    ├── playtest.py            # Interactive playtesting tool
    ├── check_solvability.py   # Validate game solvability
    ├── adjust_balance.py      # Apply difficulty presets
    └── validate_*.py          # Content validation
```

### Getting Started

#### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

#### Playing the Game

```bash
# Start the game
python start.py
```

**Controls:**
- **↑↓/ws/jk** - Navigate settings
- **←→/ad** - Navigate menus
- **Enter** - Select/edit setting
- **:** - Enter command mode
- **h** - Show help
- **q** - Quit

#### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_pipeline.py -v
```

#### Playtesting

```bash
# Interactive playtesting tool
python scripts/playtest.py

# Check game solvability
python scripts/check_solvability.py --seed 42

# Validate content
python scripts/validate_all_content.py
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
python -m black src/ tests/

# Lint code
python -m ruff check src/ tests/ --fix

# Run tests
python -m pytest tests/
```

### Development Roadmap

- ✓ **Phase 1**: Core game systems and data structures
- ✓ **Phase 2**: Procedural generation pipeline
- ✓ **Phase 3**: Game logic (dependency evaluation, state propagation, progress tracking)
- ✓ **Phase 4**: User interface with ncurses (COMPLETE)
- **Phase 5**: Anti-patterns (deception mechanics) - In Progress
- **Phase 6**: Content expansion
- **Phase 7**: Victory sequence & nested layers
- **Phase 8**: Meta features & polish
- **Phase 9**: Testing & balance
- **Phase 10**: Documentation

See [docs/Roadmap_BirdseyeView.md](docs/Roadmap_BirdseyeView.md) for the overall project roadmap.

## License

MIT License - See [LICENSE](LICENSE) for details.
