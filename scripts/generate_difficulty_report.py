#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from src.generation.pipeline import GenerationPipeline
from src.testing.difficulty_analyzer import DifficultyAnalyzer


def analyze_single(seed: int, output_file: str | None = None) -> None:
    pipeline = GenerationPipeline()

    print(f"Analyzing difficulty for seed {seed}...")
    print()

    try:
        game_state = pipeline.generate(seed=seed)
        analyzer = DifficultyAnalyzer(game_state)
        score = analyzer.analyze()

        report = analyzer.get_report()
        print(report)

        if output_file:
            data = {
                "seed": seed,
                "overall_score": score.overall,
                "rating": score.rating,
                "metrics": {
                    "total_settings": score.metrics.total_settings,
                    "total_dependencies": score.metrics.total_dependencies,
                    "dependency_density": score.metrics.dependency_density,
                    "max_chain_length": score.metrics.max_chain_length,
                    "avg_chain_length": score.metrics.avg_chain_length,
                    "locked_setting_ratio": score.metrics.locked_setting_ratio,
                    "branching_factor": score.metrics.branching_factor,
                    "critical_path_length": score.metrics.critical_path_length,
                },
                "suggestions": score.suggestions,
            }

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            print(f"\nReport saved to: {output_file}")

    except Exception as e:
        print(f"✗ Analysis failed: {e}")


def analyze_batch(start_seed: int, count: int, output_file: str | None = None) -> None:
    pipeline = GenerationPipeline()

    print(f"Analyzing difficulty for {count} games starting from seed {start_seed}...")
    print()

    ratings_count = {"trivial": 0, "easy": 0, "medium": 0, "hard": 0, "very_hard": 0}
    scores = []
    all_data = []

    for i in range(count):
        seed = start_seed + i
        try:
            game_state = pipeline.generate(seed=seed)
            analyzer = DifficultyAnalyzer(game_state)
            score = analyzer.analyze()

            ratings_count[score.rating] += 1
            scores.append(score.overall)

            print(f"Seed {seed}: {score.overall}/100 ({score.rating.upper()})")

            all_data.append(
                {
                    "seed": seed,
                    "overall_score": score.overall,
                    "rating": score.rating,
                    "metrics": {
                        "dependency_density": score.metrics.dependency_density,
                        "max_chain_length": score.metrics.max_chain_length,
                        "avg_chain_length": score.metrics.avg_chain_length,
                        "locked_setting_ratio": score.metrics.locked_setting_ratio,
                    },
                }
            )

        except Exception as e:
            print(f"Seed {seed}: Failed - {e}")

    if scores:
        print()
        print("=" * 60)
        print("Summary:")
        print(f"  Average Score: {sum(scores)/len(scores):.1f}/100")
        print(f"  Min Score: {min(scores)}")
        print(f"  Max Score: {max(scores)}")
        print()
        print("  Rating Distribution:")
        for rating, count in sorted(ratings_count.items()):
            if count > 0:
                print(f"    {rating.capitalize():12} {count:3} ({count/len(scores)*100:.1f}%)")

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            summary = {
                "total_games": len(scores),
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "rating_distribution": ratings_count,
                "games": all_data,
            }

            with open(output_path, "w") as f:
                json.dump(summary, f, indent=2)

            print(f"\nReport saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate difficulty analysis report")
    parser.add_argument("--seed", type=int, default=1, help="Starting seed (default: 1)")
    parser.add_argument(
        "--count", type=int, default=10, help="Number of games to analyze (default: 10)"
    )
    parser.add_argument(
        "--single", action="store_true", help="Analyze only a single seed"
    )
    parser.add_argument(
        "--output", type=str, help="Output JSON file for report"
    )

    args = parser.parse_args()

    if args.single:
        analyze_single(args.seed, args.output)
    else:
        analyze_batch(args.seed, args.count, args.output)


if __name__ == "__main__":
    main()
