# Ready to Start - Playtesting Manual

**Version:** 1.0
**For:** Junior Developers, QA Testers, Game Designers

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Playtest Tool](#using-the-playtest-tool)
4. [Understanding the Game](#understanding-the-game)
5. [Gameplay Commands](#gameplay-commands)
6. [Analyzing Results](#analyzing-results)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [API Reference](#api-reference)

---

## Introduction

Welcome to the Ready to Start playtesting system! This tool helps you test procedurally generated puzzle games where the goal is to enable all settings by solving dependency chains.

### What You'll Test

- **Solvability**: Can the game be completed?
- **Difficulty**: Is it too hard or too easy?
- **Playability**: Are players getting stuck?
- **Balance**: Do the dependencies make sense?

### Who This Is For

- 👨‍💻 **Junior Developers**: Learn game testing fundamentals
- 🧪 **QA Testers**: Systematic testing workflows
- 🎮 **Game Designers**: Balance and difficulty tuning

---

## Getting Started

### Installation

The playtesting system is already installed with the project. Ensure you have:

```bash
# Check Python version (3.11+)
python --version

# Verify dependencies
pip install networkx
```

### First Launch

```bash
cd /home/user/ReadyToStart
python scripts/playtest.py
```

You'll see the welcome screen with the main menu.

### Your First Playtest

1. Select option `1` (Generate & Playtest New Game)
2. Press Enter for a random seed
3. Type `easy` for difficulty preset
4. Press Enter to start playing
5. Use number keys to toggle settings
6. Type `help` anytime for assistance

**Tip**: Start with `easy` difficulty to learn the mechanics!

---

## Using the Playtest Tool

### Main Menu Options

#### 1. Generate & Playtest New Game

The primary workflow for playtesting:

```
What it does:
├── Generates a new game (random or specific seed)
├── Optionally applies difficulty preset
├── Shows pre-game analysis
└── Starts interactive gameplay session

When to use:
• Full playtest session
• Testing specific seeds
• Collecting gameplay metrics
```

**Example:**
```
Enter seed: 12345
Difficulty preset: easy
[Game generates]
[Pre-game analysis shows]
[Gameplay begins]
```

#### 2. Analyze Existing Game

Quick analysis without playing:

```
What it does:
├── Generates game from seed
├── Checks solvability
├── Calculates difficulty
└── Exports analysis (optional)

When to use:
• Quick validation
• Checking specific seeds
• Batch analysis prep
```

#### 3. Review Past Sessions

View historical playtest data:

```
What it does:
├── Lists all saved sessions
├── View individual sessions
├── Compare multiple sessions
└── Export comparison reports

When to use:
• Identifying patterns
• Finding problematic areas
• Progress tracking
```

#### 4. Batch Test Multiple Games

Test many games automatically:

```
What it does:
├── Generates N games from starting seed
├── Analyzes each (solvability + difficulty)
├── Shows aggregate statistics
└── Difficulty distribution

When to use:
• Validating generation quality
• Finding edge cases
• Statistical analysis
```

---

## Understanding the Game

### Game Structure

```
Game
├── Menus (nodes in navigation graph)
│   └── Settings (things to enable/disable)
└── Dependencies (requirements between settings)
```

### Setting States

| State | Symbol | Meaning |
|-------|--------|---------|
| ENABLED | [X] | Turned ON, counts toward victory |
| DISABLED | [ ] | Turned OFF, can be enabled |
| LOCKED | [LOCKED] | Cannot change yet, needs dependencies |

### Navigation

```
Start Menu
    ├── Settings (some locked, some available)
    └── Connected Menus (appear when accessible)
        └── More Settings...
```

### Victory Condition

**Enable ALL settings = WIN!**

The game is won when every setting in every menu is turned ON.

### Dependencies

Settings can depend on other settings:

```
Setting B LOCKED
  ↓
Requires Setting A to be ENABLED
  ↓
Enable Setting A first
  ↓
Setting B unlocks automatically
```

---

## Gameplay Commands

### During Gameplay

| Command | Description | Example |
|---------|-------------|---------|
| `[number]` | Toggle setting by number | `1` toggles first setting |
| `l` | List all settings in menu | Shows complete list |
| `m` | Show available menus | Navigate to other areas |
| `h` | Show dependency hints | Why settings are locked |
| `s` | Session statistics | View playtest metrics |
| `d` | Toggle live dashboard | Show/hide stats |
| `p` | Progress report | See completion % |
| `help` | Show help screen | Full command list |
| `save` | Save and continue | Preserve progress |
| `exit` | Save and quit | End session |
| `quit` | Quit without saving | Abandon session |

### Live Dashboard

When enabled (default), shows:

```
LIVE DASHBOARD
--------------------------------------------------------------
Settings: 5/20 (25.0%)     ← Progress toward victory
Menus:    2/5 (40.0%)      ← Exploration progress
Actions:  12 (3 failed)    ← Interaction count
Duration: 145.2s           ← Time elapsed
Stuck:    1 times (45.0s)  ← Idle detection
--------------------------------------------------------------
```

### Understanding Hints

Press `h` to see why settings are locked:

```
LOCKED SETTINGS HINTS:
--------------------------------------------------------------

Advanced Mode:
  → Requires 'Enable Features' to be enabled
  → Requires 'Tutorial Completed' to be enabled

Expert Settings:
  → Requires 'Advanced Mode' to be enabled
--------------------------------------------------------------
```

This shows the dependency chain you need to solve.

---

## Analyzing Results

### Solvability Analysis

After gameplay, you'll see a solvability report:

```
✓ Game is solvable - no issues detected
```

Or if there are issues:

```
Found 3 solvability issues:

Critical Issues (2):
  - Circular dependency detected: s1 -> s2 -> s1
  - Setting 'X' can never be unlocked

Warnings (1):
  - Menus unreachable from start: [menu3, menu4]
```

### Difficulty Analysis

```
Difficulty Analysis Report
==================================================

Overall Score: 45/100 (MEDIUM)

Metrics:
  Total Settings: 20
  Total Dependencies: 35
  Dependency Density: 1.75
  Max Chain Length: 5
  Avg Chain Length: 2.3
  Locked Ratio: 65.0%
  Branching Factor: 2.1
  Critical Path: 4 menus

Suggestions:
  - Consider adding more parallel unlocking paths
```

**Understanding Scores:**

| Score | Rating | Meaning |
|-------|--------|---------|
| 0-19 | Trivial | Too easy, boring |
| 20-39 | Easy | Good for beginners |
| 40-59 | Medium | Balanced |
| 60-79 | Hard | Challenging |
| 80-100 | Very Hard | May frustrate players |

### Session Metrics

```
Playtest Session Summary
==================================================
Session ID: 4a7b2c...
Seed: 12345
Duration: 342.5s
Completed: True

Interactions:
  Total: 45
  Failed: 8
  Unique Settings: 18
  Unique Menus: 5

Stuck Analysis:
  Events: 2
  Total Time: 78.0s
  Avg Time: 39.0s

Problem Settings:
  - setting_x: 4 failures
  - setting_y: 3 failures

Time-Consuming Menus:
  - menu2: 145.3s
  - menu4: 98.7s
```

---

## Advanced Features

### Custom Seeds

Test specific game configurations:

```bash
# In the tool, enter seed when prompted
Seed: 12345

# Or use scripts directly
python scripts/check_solvability.py --seed 12345 --single
python scripts/generate_difficulty_report.py --seed 12345 --single
```

### Difficulty Presets

Apply before playing:

| Preset | Max Chain | Density | Starters | Best For |
|--------|-----------|---------|----------|----------|
| easy | 3 | 1.5 | 5 | New players, learning |
| medium | 5 | 2.5 | 3 | Standard gameplay |
| hard | 7 | 3.5 | 2 | Experienced players |
| very_hard | 10 | 5.0 | 1 | Expert challenge |

```python
# Programmatic usage
from src.testing.balance_tuner import BalanceTuner

tuner = BalanceTuner(game_state)
tuner.apply_preset("easy")
```

### Session Management

Sessions are auto-saved to `playtest_sessions/`:

```
playtest_sessions/
├── session_a1b2c3d4.json
├── session_e5f6g7h8.json
└── ...
```

Load and review:

```python
from src.testing.session_reviewer import SessionReviewer

tracker = SessionReviewer.load_session("playtest_sessions/session_xxx.json")
print(tracker.get_summary())
```

### Batch Testing

Test multiple games:

```bash
python scripts/check_solvability.py --seed 1000 --count 50
python scripts/generate_difficulty_report.py --seed 1000 --count 50 --output report.json
```

### Exporting Data

All analysis tools support export:

```python
# In playtest tool
interface.export_analysis("reports/game_12345.json")

# Session comparison
SessionReviewer.export_comparison(sessions, "reports/comparison.json")
```

---

## Troubleshooting

### Common Issues

#### Game Generation Fails

**Symptom:** Error when generating game

**Solution:**
```bash
# Check config files exist
ls config/

# Verify templates
ls data/setting_templates/

# Check dependencies
pip install networkx
```

#### Can't Enable Any Settings

**Symptom:** All settings locked

**Solution:**
- Press `h` to see dependency hints
- Check if game is solvable with analysis
- Try `easy` difficulty preset
- May be circular dependency (bug)

#### Stuck Detection Triggers Incorrectly

**Symptom:** False positives for being stuck

**Solution:**
- Threshold is 60 seconds idle
- Any action resets the timer
- Press any key to continue
- Adjust in `PlaytestTracker.STUCK_THRESHOLD`

#### Sessions Not Saving

**Symptom:** Can't find saved sessions

**Solution:**
```bash
# Check directory exists
ls playtest_sessions/

# Create if missing
mkdir -p playtest_sessions

# Check permissions
chmod 755 playtest_sessions
```

---

## Best Practices

### For QA Testers

1. **Test Multiple Seeds**
   - Don't just test one game
   - Use batch testing for coverage
   - Track problematic seeds

2. **Document Everything**
   - Save all sessions
   - Export analysis reports
   - Note unusual behavior

3. **Use Metrics**
   - Watch for high stuck times
   - Track completion rates
   - Identify common failures

4. **Systematic Approach**
   ```
   ┌─ Generate game
   ├─ Quick analysis
   ├─ Manual playtest
   ├─ Review metrics
   └─ Report findings
   ```

### For Game Designers

1. **Balance Tuning Workflow**
   ```
   Generate → Too Hard? → Apply easy preset → Test again
                ↓
            Just Right? → Ship it!
   ```

2. **Difficulty Targeting**
   - Easy: 20-30 difficulty score
   - Medium: 40-50
   - Hard: 60-70

3. **Watch These Metrics**
   - Completion rate > 60%
   - Avg stuck time < 5 minutes
   - Max chain length < 6

### For Developers

1. **Integration Testing**
   ```python
   # Use in CI/CD
   from src.testing import SolvabilityChecker

   checker = SolvabilityChecker(game_state)
   assert checker.validate(), "Game not solvable!"
   ```

2. **Regression Testing**
   - Keep good seeds in test suite
   - Re-test after generation changes
   - Track metrics over time

3. **Debugging**
   ```python
   # Detailed analysis
   checker.validate()
   for issue in checker.issues:
       print(f"{issue.severity}: {issue.description}")
   ```

---

## API Reference

### Core Classes

#### SolvabilityChecker

```python
from src.testing import SolvabilityChecker

checker = SolvabilityChecker(game_state)
is_valid = checker.validate()  # Returns bool
report = checker.get_report()  # Returns str
issues = checker.issues        # List[SolvabilityIssue]
```

#### DifficultyAnalyzer

```python
from src.testing import DifficultyAnalyzer

analyzer = DifficultyAnalyzer(game_state)
score = analyzer.analyze()     # Returns DifficultyScore

print(score.overall)           # 0-100
print(score.rating)            # "easy", "medium", etc.
print(score.metrics)           # Detailed metrics
print(score.suggestions)       # List[str]
```

#### PlaytestTracker

```python
from src.testing import PlaytestTracker

tracker = PlaytestTracker(seed=12345)
tracker.record_setting_interaction("s1", "toggle", True, success=True)
tracker.record_menu_visit("menu2")
tracker.complete_session(completed=True)
tracker.save("session.json")

# Load later
tracker = PlaytestTracker.load("session.json")
```

#### BalanceTuner

```python
from src.testing import BalanceTuner

tuner = BalanceTuner(game_state)

# Apply preset
tuner.apply_preset("easy")

# Or custom tuning
tuner.unlock_starters(5)
tuner.reduce_density(2.0)
tuner.simplify_chains(5)
```

#### PlaytestInterface

```python
from src.testing.playtest_interface import PlaytestInterface

interface = PlaytestInterface(game_state, seed=12345)
interface.run_gameplay_loop()        # Interactive play
analysis = interface.run_analysis()   # Get analysis dict
interface.export_analysis("out.json") # Export to file
```

### Helper Functions

#### SessionReviewer

```python
from src.testing.session_reviewer import SessionReviewer

# List sessions
sessions = SessionReviewer.list_sessions()

# Load
tracker = SessionReviewer.load_session(sessions[0])

# Compare
comparison = SessionReviewer.compare_sessions([t1, t2, t3])
report = SessionReviewer.generate_comparison_report([t1, t2, t3])

# Export
SessionReviewer.export_comparison(sessions, "report.json")
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│         READY TO START - QUICK REFERENCE                │
├─────────────────────────────────────────────────────────┤
│ LAUNCH:                                                 │
│   python scripts/playtest.py                            │
│                                                         │
│ GAMEPLAY COMMANDS:                                      │
│   [number] Toggle setting    | h  Show hints           │
│   l  List settings           | s  Statistics           │
│   m  Show menus             | p  Progress             │
│   save  Save session        | exit  Save & quit       │
│                                                         │
│ DIFFICULTY RATINGS:                                     │
│   0-19   Trivial    | 40-59  Medium                    │
│   20-39  Easy       | 60-79  Hard                      │
│   80-100 Very Hard                                      │
│                                                         │
│ KEY METRICS:                                            │
│   • Completion rate > 60%                               │
│   • Avg stuck time < 5 min                              │
│   • Chain length < 6                                    │
│                                                         │
│ GET HELP:                                               │
│   docs/testing/PLAYTESTING_MANUAL.md                    │
│   Type 'help' in any menu                               │
└─────────────────────────────────────────────────────────┘
```

---

## Support & Resources

- **Documentation**: `docs/testing/`
- **Examples**: `docs/testing/WORKFLOWS.md`
- **Code**: `src/testing/`
- **Scripts**: `scripts/playtest.py`, `scripts/check_solvability.py`, etc.

---

**Last Updated**: Phase 9 Implementation
**Maintained By**: Ready to Start Development Team
