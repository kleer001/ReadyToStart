#!/usr/bin/env python3
"""
Ready to Start - A game about settings menus.

Because what you really wanted was to configure things
that don't actually do anything. Enjoy.
"""

import sys
from pathlib import Path

from src.core.config_loader import DifficultyTier
from src.generation.pipeline import GenerationPipeline
from src.ui.main_loop import UILoop


def create_game(difficulty: DifficultyTier = DifficultyTier.MEDIUM, seed: int | None = None):
    """Generate a procedural game using the generation pipeline.

    Args:
        difficulty: Difficulty tier (EASY, MEDIUM, HARD)
        seed: Optional random seed for reproducibility

    Returns:
        Generated GameState with procedural menus and dependencies
    """
    config_dir = Path(__file__).parent / "config"
    pipeline = GenerationPipeline(str(config_dir), difficulty=difficulty)

    return pipeline.generate(seed=seed, difficulty=difficulty)


def show_intro():
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║                    READY TO START                         ║")
    print("║                                                           ║")
    print("║          A game about settings menus. Yes, really.        ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    print("Your mission: Enable all the settings.")
    print("Your obstacle: The settings themselves.")
    print()
    print("Press 'h' for help once you're in the game.")
    print()
    input("Press Enter to begin your journey into configuration hell...")
    print()


def main():
    try:
        show_intro()

        # Generate procedural game with medium difficulty
        game_state = create_game(difficulty=DifficultyTier.MEDIUM, seed=None)

        config_dir = Path(__file__).parent / "config"
        ui_loop = UILoop(game_state, str(config_dir))

        # Start at the first menu
        start_menu = game_state.current_menu or list(game_state.menus.keys())[0]
        ui_loop.start(start_menu)

        # Ensure terminal is restored on successful exit
        print("\n\nThanks for playing!")

    except KeyboardInterrupt:
        print("\n\nGame interrupted. Your settings remain unsaved. Forever.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        print("The game has crashed. Ironically fitting for a settings menu.")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
