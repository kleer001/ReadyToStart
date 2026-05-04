#!/usr/bin/env python3
"""Drive UILoop with a scripted sequence of keys, no curses surface.

Useful for reproducing UI bugs without an interactive terminal. Two
modes:

  --keys UP,DOWN,ENTER,...   feed an explicit script
  --auto-solve               drive the real UI to victory by walking
                             the dependency chain through navigation +
                             Enter (proves the UI layer is solvable end
                             to end, not just the raw state machine)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config_loader import DifficultyTier
from src.testing.scripted_player import ScriptedPlayer
from start import create_game


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--level", default="Level_1")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--difficulty", default="medium", choices=["easy", "medium", "hard"]
    )
    ap.add_argument(
        "--keys",
        default="",
        help="Comma-separated key names (UP,DOWN,LEFT,RIGHT,ENTER,ESC,a,1,...)",
    )
    ap.add_argument("--auto-solve", action="store_true")
    ap.add_argument("--screen", action="store_true", help="Print final screen")
    ap.add_argument("--log", action="store_true", help="Print transition log")
    args = ap.parse_args()

    game_state = create_game(
        difficulty=DifficultyTier(args.difficulty),
        seed=args.seed,
        level_id=args.level,
    )
    config_dir = str(Path(__file__).parent.parent / "config")

    player = ScriptedPlayer(game_state, config_dir)
    start_menu = game_state.current_menu or list(game_state.menus.keys())[0]
    player.start(start_menu)

    if args.auto_solve:
        result = player.auto_solve()
        print(f"Auto-solve: {result['steps']} keypresses")
    else:
        script = [k.strip() for k in args.keys.split(",") if k.strip()]
        result = player.play(script)
        print(f"Script: {script} ({len(script)} keys)")

    print(f"Level: {args.level}, seed: {args.seed}")
    print(f"Transitions logged: {len(result['log'])}")
    print(f"Final state: {result['final']}")

    if args.screen:
        print("\n=== Final screen ===")
        print(result["screen"])
    if args.log:
        print("\n=== Log ===")
        print(json.dumps(result["log"], indent=2, default=str))

    final = result["final"]
    enabled, total = final["enabled"].split("/")
    sys.exit(0 if enabled == total and int(total) > 0 else 1)


if __name__ == "__main__":
    main()
