# Ready to Start

A procedural menu-based puzzle game where players navigate through interconnected settings menus with dynamic dependencies and state changes.

## Current Status: Phase 1 Complete ✓

Phase 1 has been successfully implemented with all core systems in place.

### Implemented Features

- **Core Type System**: Setting types (boolean, integer, float, string) with state management
- **Menu Node Structure**: Hierarchical menu organization with connections and requirements
- **State Machine**: Validates and manages state transitions for settings
- **Dependency Resolver**: Handles simple and value-based dependencies between settings
- **Game State Manager**: Central state storage with navigation tracking
- **Menu Navigator**: Navigation logic with accessibility checking
- **Comprehensive Testing**: 37 unit tests with 95% code coverage

### Project Structure

```
ready_to_start/
├── core/              # Core game systems
│   ├── enums.py       # State and type enumerations
│   ├── types.py       # Setting data structures
│   ├── menu.py        # Menu node implementation
│   ├── state_machine.py    # State transition logic
│   ├── dependencies.py     # Dependency resolution
│   ├── game_state.py      # Central state management
│   └── navigator.py       # Navigation logic
├── generation/        # (Phase 2) Procedural generation
├── ui/               # (Phase 4) User interface
└── data/             # JSON templates and data

tests/                # Unit tests
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
# Run all tests with coverage
python -m pytest tests/ --cov=ready_to_start

# Or use the build script
./scripts/build.sh
```

#### Quick Demo

```bash
# Generate and display sample game state
python scripts/generate_test_data.py

# Visualize dependencies
python scripts/visualize_deps.py
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

### Next Steps

See [Roadmap_Phase_1.md](Roadmap_Phase_1.md) for detailed implementation notes and [Roadmap_BirdseyeView.md](Roadmap_BirdseyeView.md) for the overall project roadmap.

**Coming in Phase 2**: Procedural generation system for menus and settings.

## License

MIT License - See [LICENSE](LICENSE) for details.
