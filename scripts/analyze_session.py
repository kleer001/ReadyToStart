#!/usr/bin/env python3

import json
import sys


def analyze_session(filepath: str):
    try:
        with open(filepath) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{filepath}'")
        return

    metrics = data["metrics"]

    print("=" * 60)
    print("SESSION ANALYSIS")
    print("=" * 60)

    print("\n[Time]")
    print(f"  Duration: {metrics['duration']:.1f}s ({metrics['duration']/60:.1f}m)")

    print("\n[Activity]")
    print(f"  Settings viewed: {metrics['settings_viewed']}")
    print(f"  Settings modified: {metrics['settings_modified']}")
    print(f"  Menus visited: {metrics['menus_visited']}")
    print(f"  Total clicks: {metrics['clicks']}")
    print(f"  Total hovers: {metrics['hovers']}")

    print("\n[Performance]")
    print(f"  Progress: {metrics['progress']:.1f}%")
    print(f"  Efficiency: {data['efficiency']:.1f}%")

    if metrics["settings_viewed"] > 0:
        modification_rate = (
            metrics["settings_modified"] / metrics["settings_viewed"]
        ) * 100
        print(f"  Modification rate: {modification_rate:.1f}%")

    if metrics["duration"] > 0:
        settings_per_minute = (metrics["settings_modified"] / metrics["duration"]) * 60
        print(f"  Settings/minute: {settings_per_minute:.1f}")

    print("\n[Events]")
    print(f"  Total events: {len(data['events'])}")
    if data["events"]:
        event_types = {}
        for event in data["events"]:
            event_type = event["type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print("  Event breakdown:")
        for event_type, count in sorted(
            event_types.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"    {event_type}: {count}")

    print("\n" + "=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_session.py <session.json>")
        print("\nAnalyzes session data saved by SessionManager")
        sys.exit(1)

    analyze_session(sys.argv[1])


if __name__ == "__main__":
    main()
