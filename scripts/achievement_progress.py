#!/usr/bin/env python3

from pathlib import Path
import json


def get_rarity_symbol(rarity: str) -> str:
    symbols = {
        "common": "★",
        "uncommon": "★★",
        "rare": "★★★",
        "legendary": "★★★★",
    }
    return symbols.get(rarity, "★")


def show_progress():
    project_root = Path(__file__).parent.parent
    achievements_file = project_root / "data/achievements.json"

    if not achievements_file.exists():
        print("Error: achievements.json not found in data/ directory")
        return 1

    with open(achievements_file) as f:
        data = json.load(f)

    achievements = data["achievements"]
    by_rarity = {}

    for ach in achievements:
        rarity = ach.get("rarity", "common")
        if rarity not in by_rarity:
            by_rarity[rarity] = []
        by_rarity[rarity].append(ach)

    print("\n" + "=" * 70)
    print("ACHIEVEMENTS BY RARITY")
    print("=" * 70)

    total_count = len(achievements)
    secret_count = sum(1 for a in achievements if a.get("secret", False))

    print(f"\nTotal Achievements: {total_count}")
    print(f"Secret Achievements: {secret_count}")

    for rarity in ["common", "uncommon", "rare", "legendary"]:
        if rarity not in by_rarity:
            continue

        print(f"\n{rarity.upper()} {get_rarity_symbol(rarity)}")
        print("─" * 70)

        for ach in by_rarity[rarity]:
            secret = " [SECRET]" if ach.get("secret", False) else ""
            print(f"\n  {ach['name']}{secret}")
            print(f"  {ach['description']}")

            condition = ach.get("condition", "unknown")
            threshold = ach.get("threshold", 0)

            if threshold > 0:
                print(f"  Requirement: {condition} >= {threshold}")
            else:
                print(f"  Requirement: {condition}")

    print("\n" + "=" * 70 + "\n")
    return 0


def main():
    return show_progress()


if __name__ == "__main__":
    exit(main())
