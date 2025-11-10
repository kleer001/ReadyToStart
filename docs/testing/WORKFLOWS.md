# Playtesting Workflows & Recipes

Common workflows for testing Ready to Start games.

---

## Table of Contents

1. [Quick Validation](#quick-validation)
2. [Full Playtest Session](#full-playtest-session)
3. [Batch Testing](#batch-testing)
4. [Difficulty Tuning](#difficulty-tuning)
5. [Regression Testing](#regression-testing)
6. [Problem Investigation](#problem-investigation)
7. [Statistical Analysis](#statistical-analysis)
8. [CI/CD Integration](#cicd-integration)

---

## Quick Validation

**Goal**: Quickly check if a game is solvable and appropriately difficult.

**Time**: ~1 minute

### Steps

```bash
# 1. Check solvability
python scripts/check_solvability.py --seed 12345 --single

# 2. Use playtest tool for difficulty analysis
python scripts/playtest.py
# (Interactive - generate with seed 12345, view difficulty metrics)

# 3. Review output
# ✓ = good, ✗ = needs attention
```

### Expected Output

```
✓ Game is solvable - no issues detected

Difficulty Analysis Report
==================================================
Overall Score: 45/100 (MEDIUM)
...
```

### When to Use

- After changing generation code
- Spot-checking specific seeds
- Pre-playtest validation

---

## Full Playtest Session

**Goal**: Complete manual playtest with full metrics.

**Time**: 5-30 minutes (depending on difficulty)

### Steps

```bash
# 1. Launch tool
python scripts/playtest.py

# 2. Select option 1 (Generate & Playtest)
# 3. Enter seed (or press Enter for random)
# 4. Choose difficulty preset (easy recommended for first time)
# 5. Play through the game
# 6. Review analysis at end
```

### During Gameplay

```
Initial State:
- Check dashboard (settings enabled, menus visited)
- Explore available settings
- Use 'h' to see hints

Mid-Game:
- Track progress with 'p' command
- Use 's' to check metrics
- Save periodically with 'save'

End-Game:
- Complete all settings or exit
- Review final analysis
- Export if needed
```

### Post-Session

```bash
# Review the session
python scripts/playtest.py
# Select option 3 (Review Sessions)
# Select the session to view details
```

### When to Use

- Testing new features
- Validating balance changes
- Collecting player experience data
- Training new testers

---

## Batch Testing

**Goal**: Test many games for statistical analysis.

**Time**: 5-15 minutes (50-100 games)

### Method 1: Using Playtest Tool

```bash
python scripts/playtest.py
# Select option 4 (Batch Test)
# Starting seed: 1000
# Count: 50
# Preset: medium

# Results:
# ✓ Seed 1000: MEDIUM (45/100) - 0 issues
# ✗ Seed 1001: HARD (72/100) - 3 issues
# ...
```

### Method 2: Using Scripts

```bash
# Solvability check
python scripts/check_solvability.py --seed 1000 --count 50

# For difficulty analysis, use playtest.py interactively with each seed
```

### Analyzing Results

```bash
# View JSON report
cat batch_report.json | jq '.rating_distribution'

# Output:
# {
#   "easy": 12,
#   "medium": 28,
#   "hard": 9,
#   "very_hard": 1
# }
```

### Success Criteria

- Solvability rate > 80%
- Avg difficulty: 40-60
- No "trivial" games
- <10% "very_hard"

### When to Use

- Validating generation algorithm
- Finding edge cases
- Difficulty distribution check
- Pre-release testing

---

## Difficulty Tuning

**Goal**: Adjust game to target difficulty level.

**Time**: 5-10 minutes

### Interactive Tuning

```bash
python scripts/adjust_balance.py --seed 12345 --interactive

# Menu:
# 1. Apply easy preset
# 2. Apply medium preset
# ...
# 4. Unlock starter settings
# 5. Reduce dependency density
# 6. Simplify long chains
# 7. Show full difficulty report

# After each change, see updated metrics
```

### Preset-Based Tuning

```bash
# Generate → too hard? → tune easy → test
python scripts/adjust_balance.py --seed 12345 --preset easy

# Before:
# Difficulty: 75/100 (HARD)

# After:
# Difficulty: 35/100 (EASY)
```

### Custom Tuning

```bash
# Specific adjustments
python scripts/adjust_balance.py --seed 12345 \
  --starters 5 \
  --density 2.0 \
  --chains 5

# Unlocked 5 starter settings
# Removed 12 dependencies
# Simplified 8 long chains
```

### Workflow

```
1. Generate game (random or specific seed)
2. Analyze difficulty
3. Too hard? → Apply easy preset
4. Too easy? → Apply hard preset
5. Fine-tune with custom adjustments
6. Playtest to verify
7. Repeat if needed
```

### When to Use

- Game too hard/easy
- Targeting specific difficulty
- Creating tutorial levels
- Accessibility adjustments

---

## Regression Testing

**Goal**: Ensure changes don't break known good games.

**Time**: 2-5 minutes

### Setup Test Suite

```python
# tests/test_known_seeds.py
import unittest
from src.generation.pipeline import GenerationPipeline
from src.testing import SolvabilityChecker, DifficultyAnalyzer

KNOWN_GOOD_SEEDS = [42, 123, 456, 789, 1000]

class TestKnownSeeds(unittest.TestCase):
    def setUp(self):
        self.pipeline = GenerationPipeline()

    def test_solvability(self):
        for seed in KNOWN_GOOD_SEEDS:
            game = self.pipeline.generate(seed=seed)
            checker = SolvabilityChecker(game)
            self.assertTrue(
                checker.validate(),
                f"Seed {seed} became unsolvable"
            )

    def test_difficulty_range(self):
        for seed in KNOWN_GOOD_SEEDS:
            game = self.pipeline.generate(seed=seed)
            analyzer = DifficultyAnalyzer(game)
            score = analyzer.analyze()
            self.assertGreaterEqual(score.overall, 20)
            self.assertLessEqual(score.overall, 80)
```

### Run Tests

```bash
python -m unittest tests.test_known_seeds
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Regression Tests
  run: |
    python -m unittest tests.test_known_seeds
    python scripts/check_solvability.py --seed 1 --count 10
```

### When to Use

- After code changes
- Before releases
- Continuous integration
- Validating refactors

---

## Problem Investigation

**Goal**: Identify why players are getting stuck.

**Time**: 10-20 minutes

### Step 1: Review Sessions

```bash
python scripts/playtest.py
# Select option 3 (Review Sessions)
# Select "all" to compare sessions
```

### Step 2: Identify Patterns

```
SESSION COMPARISON REPORT
======================================
Total Sessions: 15
Completed: 8 (53.3%)  ← Low completion rate!

Averages:
  Duration: 450.2s
  Stuck Time: 125.5s  ← High stuck time!

Most Problematic Settings:
  advanced_mode: 12 failures  ← Common problem
  expert_settings: 8 failures
```

### Step 3: Investigate Specific Setting

```bash
# Generate game with that seed
python scripts/check_solvability.py --seed 12345 --single

# Look for:
# - Circular dependencies involving problematic setting
# - Unreachable dependencies
# - Very long dependency chains
```

### Step 4: Fix & Validate

```bash
# If generation issue: fix code, regenerate
# If balance issue: apply tuning

python scripts/adjust_balance.py --seed 12345 --preset easy

# Test again
python scripts/playtest.py
# Generate same seed, see if problem resolved
```

### Common Problems & Solutions

| Problem | Symptom | Solution |
|---------|---------|----------|
| Circular dependency | Settings never unlock | Fix generation code |
| Long chains | High stuck time | Apply `simplify_chains` |
| High density | Too many failures | Apply `reduce_density` |
| No starters | Can't begin | Apply `unlock_starters` |

### When to Use

- Low completion rates
- High stuck times
- Player complaints
- Debugging generation

---

## Statistical Analysis

**Goal**: Understand generation quality across many games.

**Time**: 15-30 minutes

### Collect Data

```bash
# Check solvability for 100 seeds
python scripts/check_solvability.py --seed 1 --count 100

# For detailed analysis, use playtest.py interactively
```

### Analyze with Python

```python
import json
import statistics

with open('data/batch_100.json') as f:
    data = json.load(f)

games = data['games']

# Difficulty distribution
scores = [g['overall_score'] for g in games]
print(f"Mean difficulty: {statistics.mean(scores):.1f}")
print(f"Std dev: {statistics.stdev(scores):.1f}")
print(f"Range: {min(scores)}-{max(scores)}")

# Rating counts
ratings = [g['rating'] for g in games]
from collections import Counter
print(Counter(ratings))

# Density analysis
densities = [g['metrics']['dependency_density'] for g in games]
print(f"Avg density: {statistics.mean(densities):.2f}")
```

### Visualize (Optional)

```python
import matplotlib.pyplot as plt

plt.hist(scores, bins=20)
plt.xlabel('Difficulty Score')
plt.ylabel('Count')
plt.title('Difficulty Distribution (100 games)')
plt.savefig('difficulty_dist.png')
```

### Key Metrics

- **Mean Difficulty**: Target 40-50
- **Std Deviation**: <15 (consistency)
- **Rating Distribution**: Bell curve centered on "medium"
- **Solvability Rate**: >90%
- **Avg Density**: 1.5-3.0
- **Avg Chain Length**: 2-5

### When to Use

- Validating generation algorithm
- Research & tuning
- Publication/reporting
- Algorithm comparison

---

## CI/CD Integration

**Goal**: Automated testing in build pipeline.

**Time**: Setup once, runs automatically

### GitHub Actions Example

```yaml
name: Game Quality Tests

on: [push, pull_request]

jobs:
  test-quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run unit tests
      run: |
        python -m unittest tests.test_solvability
        python -m unittest tests.test_difficulty_analyzer
        python -m unittest tests.test_balance_tuner

    - name: Batch solvability check
      run: |
        python scripts/check_solvability.py --seed 1 --count 20

    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: test-reports
        path: ci_report.json
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running game quality checks..."

# Quick validation
python scripts/check_solvability.py --seed 42 --single > /dev/null

if [ $? -ne 0 ]; then
    echo "❌ Solvability check failed!"
    exit 1
fi

echo "✅ Game quality checks passed"
exit 0
```

### When to Use

- Every code push
- Pull request validation
- Release gates
- Continuous monitoring

---

## Recipe Summary

| Workflow | Time | Use Case |
|----------|------|----------|
| Quick Validation | 1 min | Spot checks |
| Full Playtest | 5-30 min | Manual testing |
| Batch Testing | 5-15 min | Statistical validation |
| Difficulty Tuning | 5-10 min | Balance adjustment |
| Regression Testing | 2-5 min | Code changes |
| Problem Investigation | 10-20 min | Debugging issues |
| Statistical Analysis | 15-30 min | Research & reporting |
| CI/CD Integration | Setup once | Automation |

---

## Tips & Tricks

### Efficient Testing

```bash
# Test multiple presets quickly
for preset in easy medium hard; do
  python scripts/adjust_balance.py --seed 42 --preset $preset
done
```

### Finding Good Seeds

```bash
# Check solvability for many seeds
python scripts/check_solvability.py --seed 1 --count 100

# For difficulty analysis, use playtest.py interactively
# Test specific seeds that passed solvability
```

### Session Management

```bash
# Clean old sessions
find playtest_sessions/ -mtime +30 -delete

# Archive important sessions
mkdir -p archives/
cp playtest_sessions/session_xxx.json archives/
```

---

**Happy Testing!** 🧪
