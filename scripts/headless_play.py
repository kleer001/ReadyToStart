#!/usr/bin/env python3
"""Headless playtest harness.

Generates a level, prints its dependency layout, then auto-solves by
finding any setting whose dependencies are met and "enabling" it
(simulating what the curses UI does when the player presses Enter).
Reports whether the level reaches the victory condition.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config_loader import DifficultyTier
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from start import create_game


def describe_dep(game_state: GameState, dep) -> str:
    target = game_state.get_setting(getattr(dep, "setting_id", ""))
    target_label = target.label if target else "?"
    return f"{getattr(dep, 'setting_id', '?')} ({target_label}) == {dep.required_state.value}"


def print_layout(game_state: GameState) -> None:
    print(f"\nMenus ({len(game_state.menus)}):")
    for menu_id, menu in game_state.menus.items():
        print(f"  {menu_id} '{menu.category}' connections={menu.connections}")
        for s in menu.settings:
            deps = game_state.resolver.dependencies.get(s.id, [])
            dep_strs = [describe_dep(game_state, d) for d in deps]
            print(
                f"    - {s.id} [{s.state.value}] {s.type.value} "
                f"label='{s.label}' deps={dep_strs or 'NONE'}"
            )


def simulate_edit_value(setting_type: SettingType, current):
    if setting_type == SettingType.BOOLEAN:
        return not bool(current)
    if setting_type == SettingType.INTEGER:
        return int(current) + 1
    if setting_type == SettingType.FLOAT:
        return float(current) + 0.1
    if setting_type == SettingType.STRING:
        return (current or "") + "x"
    return current


def find_enabling_candidate(game_state: GameState):
    """Find a DISABLED setting whose dependencies are all satisfied."""
    for menu in game_state.menus.values():
        for s in menu.settings:
            if s.state != SettingState.DISABLED:
                continue
            if game_state.resolver.can_enable(s.id, game_state):
                return s
    return None


def play(game_state: GameState, max_steps: int = 1000, verbose: bool = False) -> dict:
    """Drive the game by repeatedly enabling any setting whose deps are met."""
    steps = 0
    enabled = []
    while steps < max_steps:
        candidate = find_enabling_candidate(game_state)
        if not candidate:
            break
        candidate.value = simulate_edit_value(candidate.type, candidate.value)
        candidate.state = SettingState.ENABLED
        enabled.append(candidate.id)
        if verbose:
            print(f"  step {steps+1}: enabled {candidate.id} ({candidate.label})")
        game_state.propagate_changes()
        steps += 1

    total = sum(len(m.settings) for m in game_state.menus.values())
    enabled_count = sum(
        1
        for m in game_state.menus.values()
        for s in m.settings
        if s.state == SettingState.ENABLED
    )
    stuck = []
    for m in game_state.menus.values():
        for s in m.settings:
            if s.state == SettingState.DISABLED:
                stuck.append(s.id)

    return {
        "steps": steps,
        "enabled_count": enabled_count,
        "total_settings": total,
        "victory": enabled_count == total,
        "stuck_settings": stuck,
        "enabled_order": enabled,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Headless playtest harness")
    parser.add_argument("--level", default="Level_1", help="Level ID (default Level_1)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--difficulty", default="medium", choices=["easy", "medium", "hard"]
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--show-layout", action="store_true")
    args = parser.parse_args()

    game_state = create_game(
        difficulty=DifficultyTier(args.difficulty),
        seed=args.seed,
        level_id=args.level,
    )

    print(f"Level: {args.level}, seed: {args.seed}, difficulty: {args.difficulty}")

    if args.show_layout:
        print_layout(game_state)

    result = play(game_state, verbose=args.verbose)

    print()
    print("=" * 60)
    print(f"Steps:           {result['steps']}")
    print(f"Enabled:         {result['enabled_count']}/{result['total_settings']}")
    print(f"Victory:         {result['victory']}")
    if result["stuck_settings"]:
        print(f"Stuck settings:  {len(result['stuck_settings'])}")
        for sid in result["stuck_settings"][:10]:
            s = game_state.get_setting(sid)
            deps = game_state.resolver.dependencies.get(sid, [])
            unmet = [
                describe_dep(game_state, d)
                for d in deps
                if not d.evaluate(game_state)
            ]
            print(f"  {sid} '{s.label}' unmet={unmet}")

    sys.exit(0 if result["victory"] else 1)


if __name__ == "__main__":
    main()
