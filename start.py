#!/usr/bin/env python3
"""
Ready to Start - A game about settings menus.

Because what you really wanted was to configure things
that don't actually do anything. Enjoy.
"""

import curses
import sys
from pathlib import Path

import networkx as nx

from src.core.config_loader import DifficultyTier
from src.core.game_state import GameState
from src.generation.pipeline import GenerationPipeline
from src.ui.main_loop import UILoop


def create_game(difficulty: DifficultyTier = DifficultyTier.MEDIUM, seed: int | None = None, level_id: str | None = None):
    """Generate a procedural game using the generation pipeline.

    Args:
        difficulty: Difficulty tier (EASY, MEDIUM, HARD)
        seed: Optional random seed for reproducibility
        level_id: Optional level identifier (e.g., "Level_1")

    Returns:
        Generated GameState with procedural menus and dependencies
    """
    config_dir = Path(__file__).parent / "config"
    pipeline = GenerationPipeline(str(config_dir), difficulty=difficulty, level_id=level_id)

    return pipeline.generate(seed=seed, difficulty=difficulty)


def find_final_setting(game_state: GameState) -> str:
    """Find the final setting in the dependency chain.

    This finds a setting that would be one of the last to be enabled,
    typically one with the most dependencies or deepest in the chain.

    Args:
        game_state: The game state with all settings and dependencies

    Returns:
        The label of a final setting in the dependency chain
    """
    # Build dependency graph
    dep_graph = nx.DiGraph()

    for setting_id, deps in game_state.resolver.dependencies.items():
        for dep in deps:
            if hasattr(dep, 'setting_id'):
                # Edge from dependency to dependent (dep.setting_id -> setting_id)
                dep_graph.add_edge(dep.setting_id, setting_id)

    # Find settings with no outgoing edges (sink nodes - nothing depends on them)
    sink_nodes = [node for node in dep_graph.nodes() if dep_graph.out_degree(node) == 0]

    if not sink_nodes:
        # No sink nodes found, find the setting with the most dependencies
        max_deps = 0
        final_setting_id = None
        for setting_id, deps in game_state.resolver.dependencies.items():
            if len(deps) > max_deps:
                max_deps = len(deps)
                final_setting_id = setting_id

        if final_setting_id:
            setting = game_state.get_setting(final_setting_id)
            return setting.label if setting else "the final setting"
    else:
        # Return one of the sink nodes (prefer one with dependencies)
        for node in sink_nodes:
            if node in game_state.resolver.dependencies:
                setting = game_state.get_setting(node)
                return setting.label if setting else "the final setting"

        # If no sink node has dependencies, just return the first one
        setting = game_state.get_setting(sink_nodes[0])
        return setting.label if setting else "the final setting"

    return "the final setting"


def show_main_menu(stdscr):
    """Show the main menu and return the user's choice.

    Returns:
        str: 'play' or 'options'
    """
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(False)  # Blocking input
    stdscr.keypad(True)  # Enable arrow keys

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)

    selected = 0
    menu_items = ["Play", "Options"]

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Box dimensions - same as gameplay menus
        box_width = 80
        box_height = 10
        start_x = (width - box_width) // 2
        start_y = (height - box_height) // 2

        # Double-line box characters
        top_left, top_right = "╔", "╗"
        bottom_left, bottom_right = "╚", "╝"
        horizontal, vertical = "═", "║"
        divider_left, divider_right = "╠", "╣"

        try:
            # Top border
            stdscr.addstr(start_y, start_x, top_left + horizontal * (box_width - 2) + top_right)

            # Title line
            title = "READY TO START"
            title_line = title.center(box_width - 2)
            stdscr.addstr(start_y + 1, start_x, vertical + title_line + vertical)

            # Divider
            stdscr.addstr(start_y + 2, start_x, divider_left + horizontal * (box_width - 2) + divider_right)

            # Empty line
            stdscr.addstr(start_y + 3, start_x, vertical + " " * (box_width - 2) + vertical)

            # Menu items
            for idx, item in enumerate(menu_items):
                line_y = start_y + 4 + idx
                if idx == selected:
                    # Cyan color with bold for selected item
                    item_text = f"> {item} <".center(box_width - 2)
                    stdscr.addstr(line_y, start_x, vertical)
                    stdscr.addstr(line_y, start_x + 1, item_text, curses.color_pair(1) | curses.A_BOLD)
                    stdscr.addstr(line_y, start_x + box_width - 1, vertical)
                else:
                    item_text = f"  {item}  ".center(box_width - 2)
                    stdscr.addstr(line_y, start_x, vertical + item_text + vertical)

            # Empty lines to fill box
            for i in range(len(menu_items), 6):
                stdscr.addstr(start_y + 4 + i, start_x, vertical + " " * (box_width - 2) + vertical)

            # Bottom border
            stdscr.addstr(start_y + box_height - 1, start_x, bottom_left + horizontal * (box_width - 2) + bottom_right)

        except curses.error:
            pass

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


def show_play_error(stdscr, final_setting_name: str):
    """Show the error message when trying to play without configuring settings.

    Args:
        stdscr: The curses screen
        final_setting_name: The name of the final setting to configure
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Box dimensions
    box_width = 80
    box_height = 14
    start_x = (width - box_width) // 2
    start_y = (height - box_height) // 2

    # Double-line box characters
    top_left, top_right = "╔", "╗"
    bottom_left, bottom_right = "╚", "╝"
    horizontal, vertical = "═", "║"
    divider_left, divider_right = "╠", "╣"

    try:
        # Top border
        stdscr.addstr(start_y, start_x, top_left + horizontal * (box_width - 2) + top_right)

        # Title
        title = "ERROR: Cannot start game"
        stdscr.addstr(start_y + 1, start_x, vertical + title.center(box_width - 2) + vertical)

        # Divider
        stdscr.addstr(start_y + 2, start_x, divider_left + horizontal * (box_width - 2) + divider_right)

        # Message content
        messages = [
            "",
            f"Game requires '{final_setting_name}' setting to be configured.",
            "",
            f"Please enable '{final_setting_name}' in Options first.",
            "",
            "",
            "Press any key to return to menu..."
        ]

        for i, msg in enumerate(messages):
            line = msg.center(box_width - 2)
            stdscr.addstr(start_y + 3 + i, start_x, vertical + line + vertical)

        # Fill remaining lines
        for i in range(len(messages), box_height - 4):
            stdscr.addstr(start_y + 3 + i, start_x, vertical + " " * (box_width - 2) + vertical)

        # Bottom border
        stdscr.addstr(start_y + box_height - 1, start_x, bottom_left + horizontal * (box_width - 2) + bottom_right)

    except curses.error:
        pass

    stdscr.refresh()
    stdscr.getch()  # Wait for keypress


def main_menu_loop(stdscr, final_setting_name: str):
    """Main menu loop - shows menu and handles selection.

    Args:
        stdscr: The curses screen
        final_setting_name: The name of the final setting to configure
    """
    while True:
        choice = show_main_menu(stdscr)

        if choice == "play":
            # Show error about needing to configure settings
            show_play_error(stdscr, final_setting_name)
        elif choice == "options":
            # This is where the actual game starts
            return


def main():
    try:
        # Generate procedural game with Level 1 (introductory level)
        # (so we know what the final setting is for the main menu)
        game_state = create_game(difficulty=DifficultyTier.MEDIUM, seed=None, level_id="Level_1")

        # Find the final setting in the dependency chain
        final_setting_name = find_final_setting(game_state)

        # Show main menu with the final setting name
        curses.wrapper(main_menu_loop, final_setting_name)

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
