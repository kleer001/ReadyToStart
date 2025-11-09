#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generation.pipeline import GenerationPipeline
from src.testing.solvability_checker import SolvabilityChecker


def check_batch(start_seed: int, count: int) -> None:
    pipeline = GenerationPipeline()

    results = {"solvable": 0, "issues": 0, "failed": 0}
    issue_details = []

    print(f"Checking solvability for {count} games starting from seed {start_seed}...")
    print()

    for i in range(count):
        seed = start_seed + i
        try:
            game_state = pipeline.generate(seed=seed)
            checker = SolvabilityChecker(game_state)

            if checker.validate():
                results["solvable"] += 1
                print(f"✓ Seed {seed}: Solvable")
            else:
                results["issues"] += 1
                print(f"✗ Seed {seed}: Issues found ({len(checker.issues)})")
                issue_details.append((seed, checker.issues))

        except Exception as e:
            results["failed"] += 1
            print(f"✗ Seed {seed}: Generation failed - {e}")

    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Solvable: {results['solvable']}/{count} ({results['solvable']/count*100:.1f}%)")
    print(f"  Issues:   {results['issues']}/{count} ({results['issues']/count*100:.1f}%)")
    print(f"  Failed:   {results['failed']}/{count} ({results['failed']/count*100:.1f}%)")

    if issue_details:
        print()
        print("Detailed Issues:")
        for seed, issues in issue_details:
            print(f"\nSeed {seed}:")
            for issue in issues:
                print(f"  [{issue.severity}] {issue.type}: {issue.description}")


def check_single(seed: int) -> None:
    pipeline = GenerationPipeline()

    print(f"Checking solvability for seed {seed}...")
    print()

    try:
        game_state = pipeline.generate(seed=seed)
        checker = SolvabilityChecker(game_state)
        checker.validate()

        print(checker.get_report())

        if not checker.validate():
            sys.exit(1)

    except Exception as e:
        print(f"✗ Generation failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Check game solvability")
    parser.add_argument("--seed", type=int, default=1, help="Starting seed (default: 1)")
    parser.add_argument(
        "--count", type=int, default=10, help="Number of games to check (default: 10)"
    )
    parser.add_argument(
        "--single", action="store_true", help="Check only a single seed"
    )

    args = parser.parse_args()

    if args.single:
        check_single(args.seed)
    else:
        check_batch(args.seed, args.count)


if __name__ == "__main__":
    main()
