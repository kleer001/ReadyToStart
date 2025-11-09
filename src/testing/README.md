# Testing Module - Quick Reference

Phase 9 testing and balance framework for Ready to Start.

## Quick Start

```bash
# Interactive playtesting
python scripts/playtest.py

# Check solvability
python scripts/check_solvability.py --seed 12345 --single

# Difficulty analysis
python scripts/generate_difficulty_report.py --seed 12345 --single

# Balance tuning
python scripts/adjust_balance.py --seed 12345 --preset easy
```

## Modules

### Core Testing

- **`solvability_checker.py`** - Validates game completability
- **`difficulty_analyzer.py`** - Calculates difficulty metrics (0-100 scale)
- **`balance_tuner.py`** - Adjusts game balance with presets

### Playtesting

- **`playtest_interface.py`** - Interactive CLI interface
- **`playtest_session.py`** - Session tracking and persistence
- **`playtest_metrics.py`** - Metrics data structures
- **`gameplay_simulator.py`** - Manual gameplay handler
- **`session_reviewer.py`** - Session analysis and comparison

## Usage Examples

### Solvability Check

```python
from src.testing import SolvabilityChecker

checker = SolvabilityChecker(game_state)
if checker.validate():
    print("Game is solvable!")
else:
    print(checker.get_report())
```

### Difficulty Analysis

```python
from src.testing import DifficultyAnalyzer

analyzer = DifficultyAnalyzer(game_state)
score = analyzer.analyze()

print(f"Difficulty: {score.overall}/100")
print(f"Rating: {score.rating}")
print(f"Suggestions: {score.suggestions}")
```

### Balance Tuning

```python
from src.testing import BalanceTuner

tuner = BalanceTuner(game_state)
tuner.apply_preset("easy")  # or "medium", "hard", "very_hard"

# Custom tuning
tuner.unlock_starters(5)
tuner.reduce_density(2.0)
tuner.simplify_chains(5)
```

### Manual Playtesting

```python
from src.testing.playtest_interface import PlaytestInterface

interface = PlaytestInterface(game_state, seed=12345)
interface.run_gameplay_loop()  # Interactive session
interface.show_final_analysis()
interface.export_analysis("analysis.json")
```

### Session Review

```python
from src.testing.session_reviewer import SessionReviewer

sessions = SessionReviewer.list_sessions()
tracker = SessionReviewer.load_session(sessions[0])
print(tracker.get_summary())

# Compare multiple sessions
comparison = SessionReviewer.compare_sessions([t1, t2, t3])
report = SessionReviewer.generate_comparison_report([t1, t2, t3])
```

## Difficulty Ratings

| Score | Rating | Description |
|-------|--------|-------------|
| 0-19 | trivial | Too easy |
| 20-39 | easy | Good for beginners |
| 40-59 | medium | Balanced |
| 60-79 | hard | Challenging |
| 80-100 | very_hard | Very difficult |

## Key Metrics

### Solvability
- ✓ No circular dependencies
- ✓ All settings unlockable
- ✓ Menus connected
- ✓ Victory reachable

### Difficulty
- **Dependency Density**: Avg dependencies per setting
- **Chain Length**: Max/avg dependency chain
- **Locked Ratio**: Proportion of locked settings
- **Branching Factor**: Parallel unlock paths

### Playtest Sessions
- **Completion Rate**: % of games finished
- **Stuck Time**: Time idle (threshold: 60s)
- **Failed Interactions**: Unsuccessful actions
- **Problem Areas**: High-failure settings/menus

## Presets

| Preset | Density | Chain | Starters | Use Case |
|--------|---------|-------|----------|----------|
| easy | 1.5 | 3 | 5 | New players |
| medium | 2.5 | 5 | 3 | Standard |
| hard | 3.5 | 7 | 2 | Experienced |
| very_hard | 5.0 | 10 | 1 | Expert |

## Scripts

### `scripts/playtest.py`
Interactive playtesting tool with:
- Game generation & playtesting
- Session review & comparison
- Batch testing
- Analysis export

### `scripts/check_solvability.py`
```bash
# Single game
python scripts/check_solvability.py --seed 42 --single

# Batch
python scripts/check_solvability.py --seed 1 --count 10
```

### `scripts/generate_difficulty_report.py`
```bash
# Single game
python scripts/generate_difficulty_report.py --seed 42 --single --output report.json

# Batch
python scripts/generate_difficulty_report.py --seed 1 --count 20 --output batch.json
```

### `scripts/adjust_balance.py`
```bash
# Preset
python scripts/adjust_balance.py --seed 42 --preset easy

# Custom
python scripts/adjust_balance.py --seed 42 --starters 5 --density 2.0 --chains 5

# Interactive
python scripts/adjust_balance.py --seed 42 --interactive
```

## Testing

```bash
# Run Phase 9 tests
python -m unittest tests.test_solvability
python -m unittest tests.test_difficulty_analyzer
python -m unittest tests.test_playtesting
python -m unittest tests.test_balance_tuner
python -m unittest tests.test_full_game_flow

# All tests
python -m unittest discover tests/
```

## Documentation

- **Comprehensive Manual**: `docs/testing/PLAYTESTING_MANUAL.md`
- **Workflow Examples**: `docs/testing/WORKFLOWS.md`
- **API Reference**: See manual, section 10

## Architecture

```
src/testing/
├── Core Analysis
│   ├── solvability_checker.py    (validates completability)
│   ├── difficulty_analyzer.py    (calculates metrics)
│   └── balance_tuner.py          (adjusts balance)
├── Playtesting
│   ├── playtest_interface.py     (UI/UX)
│   ├── playtest_session.py       (tracking)
│   ├── playtest_metrics.py       (data)
│   ├── gameplay_simulator.py     (game logic)
│   └── session_reviewer.py       (analysis)
└── __init__.py                   (exports)
```

## Design Principles

- **DRY**: Zero code duplication
- **SOLID**: Clean separation of concerns
- **KISS**: Simple, understandable interfaces
- **Self-documenting**: No comments needed

## Output Directories

- `playtest_sessions/` - Saved gameplay sessions (JSON)
- `analysis_reports/` - Exported analysis data (JSON)

## Common Workflows

### 1. Quick Validation
```bash
python scripts/check_solvability.py --seed 12345 --single
python scripts/generate_difficulty_report.py --seed 12345 --single
```

### 2. Full Playtest
```bash
python scripts/playtest.py
# Select option 1, enter seed, play through
```

### 3. Batch Analysis
```bash
python scripts/check_solvability.py --seed 1000 --count 50
python scripts/generate_difficulty_report.py --seed 1000 --count 50 --output report.json
```

### 4. Balance & Test
```bash
python scripts/adjust_balance.py --seed 42 --preset easy
python scripts/playtest.py  # Test the tuned game
```

### 5. Review & Compare
```bash
python scripts/playtest.py
# Select option 3 (Review Sessions)
# Select "all" to compare
```

## Integration

```python
# Use in CI/CD
from src.generation.pipeline import GenerationPipeline
from src.testing import SolvabilityChecker, DifficultyAnalyzer

pipeline = GenerationPipeline()
game_state = pipeline.generate(seed=42)

checker = SolvabilityChecker(game_state)
assert checker.validate(), f"Game not solvable: {checker.get_report()}"

analyzer = DifficultyAnalyzer(game_state)
score = analyzer.analyze()
assert 20 <= score.overall <= 80, f"Difficulty out of range: {score.overall}"
```

## Support

For detailed documentation, see `docs/testing/PLAYTESTING_MANUAL.md`.

For workflow examples, see `docs/testing/WORKFLOWS.md`.

For issues, check the Troubleshooting section in the manual.
