#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generation.pipeline import GenerationPipeline


def validate_state(state):
    if not state.menus:
        return False
    if not state.settings:
        return False
    if state.current_menu not in state.menus:
        return False
    for menu in state.menus.values():
        if not menu.settings:
            return False
    return True


def test_generation(num_runs: int = 10):
    pipeline = GenerationPipeline()

    for i in range(num_runs):
        print(f"Run {i + 1}/{num_runs}...")
        try:
            state = pipeline.generate(seed=i)
            valid = validate_state(state)
            print(f"  Menus: {len(state.menus)}")
            print(f"  Settings: {len(state.settings)}")
            print(f"  Dependencies: {len(state.resolver.dependencies)}")
            print(f"  Valid: {valid}")
            if not valid:
                print("  ERROR: Invalid state generated!")
        except Exception as e:
            print(f"  ERROR: {e}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test procedural generation")
    parser.add_argument(
        "--runs", type=int, default=10, help="Number of generation runs"
    )
    args = parser.parse_args()

    test_generation(args.runs)
