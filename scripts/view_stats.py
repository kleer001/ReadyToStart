#!/usr/bin/env python3

from pathlib import Path
from sys import argv
import json


def format_value(value):
    if isinstance(value, dict):
        return f"{len(value)} items"
    if isinstance(value, list):
        return f"{len(value)} items"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def print_section(title, items):
    print(f"\n{title}:")
    for key, value in items.items():
        formatted = format_value(value)
        print(f"  {key:30s} {formatted}")


def view_stats(stats_file: str | Path):
    with open(stats_file) as f:
        stats = json.load(f)

    print("\n" + "=" * 60)
    print("GAME STATISTICS")
    print("=" * 60)

    basic_stats = {
        "Total Play Time": stats.get("total_play_time", 0),
        "Total Actions": stats.get("total_actions", 0),
        "Settings Enabled": stats.get("settings_enabled", 0),
        "Total Errors": stats.get("total_errors", 0),
    }
    print_section("Basic Stats", basic_stats)

    layer_stats = {
        "Layers Completed": stats.get("layers_completed", 0),
        "Current Depth": stats.get("current_layer_depth", 0),
        "Deepest Reached": stats.get("deepest_layer_reached", 0),
        "Perfect Layers": stats.get("perfect_layers", 0),
    }
    print_section("Layer Progress", layer_stats)

    efficiency_stats = {
        "Average Efficiency": stats.get("average_efficiency", 0),
        "Best Efficiency": stats.get("best_efficiency", 0),
        "Worst Efficiency": stats.get("worst_efficiency", 0),
    }
    print_section("Efficiency", efficiency_stats)

    meta_stats = {
        "Glitches Encountered": stats.get("glitches_encountered", 0),
        "Fourth Wall Breaks": stats.get("fourth_wall_breaks", 0),
        "Meta Comments": stats.get("meta_comments", 0),
        "Help Views": stats.get("help_views", 0),
        "Quit Attempts": stats.get("quit_attempts", 0),
    }
    print_section("Meta Stats", meta_stats)

    secrets = stats.get("secrets_found", [])
    if secrets:
        print(f"\nSecrets Found ({len(secrets)}):")
        for secret in secrets:
            print(f"  - {secret}")

    time_per_layer = stats.get("time_per_layer", {})
    if time_per_layer:
        print(f"\nTime Per Layer:")
        for layer_id, time_spent in time_per_layer.items():
            print(f"  {layer_id:30s} {time_spent:.1f}s")

    print("\n" + "=" * 60 + "\n")


def main():
    if len(argv) < 2:
        print("Usage: view_stats.py <stats.json>")
        return 1

    stats_file = Path(argv[1])
    if not stats_file.exists():
        print(f"Error: File not found: {stats_file}")
        return 1

    view_stats(stats_file)
    return 0


if __name__ == "__main__":
    exit(main())
