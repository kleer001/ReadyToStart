#!/usr/bin/env python3
"""
Ready to Start - A game about settings menus.

Because what you really wanted was to configure things
that don't actually do anything. Enjoy.
"""

import curses
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


def show_main_menu(stdscr):
    """Show the main menu and return the user's choice.

    Returns:
        str: 'play' or 'options'
    """
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(False)  # Blocking input
    stdscr.keypad(True)  # Enable arrow keys

    selected = 0
    menu_items = ["Play", "Options"]

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = "READY TO START"
        y = height // 2 - 4
        stdscr.addstr(y, (width - len(title)) // 2, title, curses.A_BOLD)

        # Menu items
        y += 3
        for idx, item in enumerate(menu_items):
            x = width // 2 - 10
            if idx == selected:
                stdscr.addstr(y, x, f"> {item} <", curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, f"  {item}  ")
            y += 2

        stdscr.refresh()

        # Handle input
        key = stdscr.getch()

        if key == curses.KEY_UP or key == ord('w') or key == ord('k'):
            selected = (selected - 1) % len(menu_items)
        elif key == curses.KEY_DOWN or key == ord('s') or key == ord('j'):
            selected = (selected + 1) % len(menu_items)
        elif key == ord('\n') or key == ord('\r') or key == ord(' '):
            return menu_items[selected].lower()
        elif key == ord('q'):
            sys.exit(0)


def show_play_error(stdscr):
    """Show the error message when trying to play without configuring settings."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    y = height // 2 - 5

    messages = [
        "ERROR: Cannot start game",
        "",
        "Game requires 'Enable Gameplay' setting to be configured.",
        "",
        "Please enable 'Enable Gameplay' in Options first.",
        "",
        "",
        "Press any key to return to menu..."
    ]

    for msg in messages:
        if msg:
            stdscr.addstr(y, (width - len(msg)) // 2, msg)
        y += 1

    stdscr.refresh()
    stdscr.getch()  # Wait for keypress


def main_menu_loop(stdscr):
    """Main menu loop - shows menu and handles selection."""
    while True:
        choice = show_main_menu(stdscr)

        if choice == "play":
            # Show error about needing to configure settings
            show_play_error(stdscr)
        elif choice == "options":
            # This is where the actual game starts
            return


def main():
    try:
        # Show main menu first
        curses.wrapper(main_menu_loop)

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
