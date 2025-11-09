#!/usr/bin/env python3

import argparse

from src.generation.pipeline import GenerationPipeline
from src.testing.balance_tuner import BalanceTuner
from src.testing.difficulty_analyzer import DifficultyAnalyzer
from src.testing.solvability_checker import SolvabilityChecker


def apply_preset(seed: int, difficulty: str) -> None:
    pipeline = GenerationPipeline()

    print(f"Generating game with seed {seed}...")
    game_state = pipeline.generate(seed=seed)

    print("Analyzing before tuning...")
    analyzer_before = DifficultyAnalyzer(game_state)
    score_before = analyzer_before.analyze()
    checker_before = SolvabilityChecker(game_state)
    checker_before.validate()

    print()
    print("BEFORE TUNING:")
    print(f"  Difficulty: {score_before.overall}/100 ({score_before.rating.upper()})")
    print(f"  Issues: {len(checker_before.issues)}")

    print()
    print(f"Applying {difficulty.upper()} preset...")
    tuner = BalanceTuner(game_state)
    tuner.apply_preset(difficulty)

    print()
    print("Analyzing after tuning...")
    analyzer_after = DifficultyAnalyzer(game_state)
    score_after = analyzer_after.analyze()
    checker_after = SolvabilityChecker(game_state)
    checker_after.validate()

    print()
    print("AFTER TUNING:")
    print(f"  Difficulty: {score_after.overall}/100 ({score_after.rating.upper()})")
    print(f"  Issues: {len(checker_after.issues)}")

    print()
    print("=" * 60)
    print("Changes:")
    print(
        f"  Difficulty: {score_before.overall} → {score_after.overall} ({score_after.overall - score_before.overall:+d})"
    )
    print(
        f"  Issues: {len(checker_before.issues)} → {len(checker_after.issues)} ({len(checker_after.issues) - len(checker_before.issues):+d})"
    )


def custom_adjustments(seed: int, starters: int, density: float, chains: int) -> None:
    pipeline = GenerationPipeline()

    print(f"Generating game with seed {seed}...")
    game_state = pipeline.generate(seed=seed)

    print("Analyzing before tuning...")
    analyzer_before = DifficultyAnalyzer(game_state)
    score_before = analyzer_before.analyze()

    print()
    print("BEFORE TUNING:")
    print(analyzer_before.get_report())

    print()
    print("Applying custom adjustments...")
    tuner = BalanceTuner(game_state)

    if starters > 0:
        unlocked = tuner.unlock_starters(starters)
        print(f"  Unlocked {unlocked} starter settings")

    if density > 0:
        removed = tuner.reduce_density(density)
        print(f"  Removed {removed} dependencies")

    if chains > 0:
        simplified = tuner.simplify_chains(chains)
        print(f"  Simplified {simplified} long chains")

    print()
    print("Analyzing after tuning...")
    analyzer_after = DifficultyAnalyzer(game_state)
    score_after = analyzer_after.analyze()

    print()
    print("AFTER TUNING:")
    print(analyzer_after.get_report())


def interactive_mode(seed: int) -> None:
    pipeline = GenerationPipeline()

    print(f"Generating game with seed {seed}...")
    game_state = pipeline.generate(seed=seed)

    tuner = BalanceTuner(game_state)

    while True:
        print()
        print("=" * 60)
        print("Current State:")

        analyzer = DifficultyAnalyzer(game_state)
        score = analyzer.analyze()
        print(f"  Difficulty: {score.overall}/100 ({score.rating.upper()})")

        checker = SolvabilityChecker(game_state)
        checker.validate()
        print(f"  Issues: {len(checker.issues)}")

        print()
        print("Options:")
        print("  1. Apply easy preset")
        print("  2. Apply medium preset")
        print("  3. Apply hard preset")
        print("  4. Unlock starter settings")
        print("  5. Reduce dependency density")
        print("  6. Simplify long chains")
        print("  7. Show full difficulty report")
        print("  8. Show solvability report")
        print("  9. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            tuner.apply_preset("easy")
            print("Applied easy preset")
        elif choice == "2":
            tuner.apply_preset("medium")
            print("Applied medium preset")
        elif choice == "3":
            tuner.apply_preset("hard")
            print("Applied hard preset")
        elif choice == "4":
            count = int(input("Number of starters: ").strip())
            unlocked = tuner.unlock_starters(count)
            print(f"Unlocked {unlocked} settings")
        elif choice == "5":
            target = float(input("Target density: ").strip())
            removed = tuner.reduce_density(target)
            print(f"Removed {removed} dependencies")
        elif choice == "6":
            max_length = int(input("Max chain length: ").strip())
            simplified = tuner.simplify_chains(max_length)
            print(f"Simplified {simplified} chains")
        elif choice == "7":
            print()
            print(analyzer.get_report())
        elif choice == "8":
            print()
            print(checker.get_report())
        elif choice == "9":
            break
        else:
            print("Invalid option")


def main():
    parser = argparse.ArgumentParser(description="Adjust game balance")
    parser.add_argument("--seed", type=int, default=1, help="Game seed (default: 1)")
    parser.add_argument(
        "--preset",
        choices=["easy", "medium", "hard", "very_hard"],
        help="Apply difficulty preset",
    )
    parser.add_argument(
        "--starters", type=int, default=0, help="Number of starter settings to unlock"
    )
    parser.add_argument(
        "--density", type=float, default=0, help="Target dependency density"
    )
    parser.add_argument(
        "--chains", type=int, default=0, help="Maximum chain length"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Interactive adjustment mode"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.seed)
    elif args.preset:
        apply_preset(args.seed, args.preset)
    elif args.starters > 0 or args.density > 0 or args.chains > 0:
        custom_adjustments(args.seed, args.starters, args.density, args.chains)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
