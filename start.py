#!/usr/bin/env python3
"""
Ready to Start - A game about settings menus.

Because what you really wanted was to configure things
that don't actually do anything. Enjoy.
"""

import random
import sys
from pathlib import Path

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.ui.main_loop import UILoop


def _create_main_menu() -> MenuNode:
    """Create the main menu with the Start Game button."""
    main_menu = MenuNode(id="main", category="Main Menu")
    main_menu.add_setting(
        Setting(
            id="start_game",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="▶ Start Game",
        )
    )
    return main_menu


def _create_audio_menu() -> MenuNode:
    """Create audio settings menu with random initial values."""
    audio_menu = MenuNode(id="audio", category="Audio Settings")
    audio_menu.add_setting(
        Setting(
            id="audio_master_volume",
            type=SettingType.INTEGER,
            value=random.randint(0, 100),
            state=SettingState.DISABLED,
            label="Master Volume",
            min_value=0,
            max_value=100,
        )
    )
    audio_menu.add_setting(
        Setting(
            id="audio_enable",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.DISABLED,
            label="Enable Audio",
        )
    )
    audio_menu.add_setting(
        Setting(
            id="audio_speaker_config",
            type=SettingType.STRING,
            value=random.choice(["mono", "stereo", "5.1", "7.1"]),
            state=SettingState.LOCKED,
            label="Speaker Configuration",
        )
    )
    audio_menu.add_setting(
        Setting(
            id="audio_3d_sound",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.DISABLED,
            label="3D Audio Processing",
        )
    )
    return audio_menu


def _create_graphics_menu() -> MenuNode:
    """Create graphics settings menu with random initial values."""
    graphics_menu = MenuNode(id="graphics", category="Graphics Settings")
    graphics_menu.add_setting(
        Setting(
            id="graphics_resolution",
            type=SettingType.STRING,
            value=random.choice(["640x480", "800x600", "1024x768", "1280x720", "1920x1080", "2560x1440", "3840x2160"]),
            state=SettingState.ENABLED,  # Pre-configured! The only "free" setting
            label="Screen Resolution",
        )
    )
    graphics_menu.add_setting(
        Setting(
            id="graphics_vsync",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.DISABLED,
            label="V-Sync",
        )
    )
    graphics_menu.add_setting(
        Setting(
            id="graphics_quality",
            type=SettingType.INTEGER,
            value=random.randint(1, 5),
            state=SettingState.DISABLED,
            label="Quality Level",
            min_value=1,
            max_value=5,
        )
    )
    graphics_menu.add_setting(
        Setting(
            id="graphics_antialiasing",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.LOCKED,
            label="Anti-Aliasing",
        )
    )
    return graphics_menu


def _create_gameplay_menu() -> MenuNode:
    """Create gameplay settings menu with random initial values."""
    gameplay_menu = MenuNode(id="gameplay", category="Gameplay Settings")
    gameplay_menu.add_setting(
        Setting(
            id="gameplay_difficulty",
            type=SettingType.INTEGER,
            value=random.randint(1, 5),
            state=SettingState.DISABLED,
            label="Difficulty Level",
            min_value=1,
            max_value=5,
        )
    )
    gameplay_menu.add_setting(
        Setting(
            id="gameplay_autosave",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.DISABLED,
            label="Auto-Save",
        )
    )
    gameplay_menu.add_setting(
        Setting(
            id="gameplay_tutorials",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.DISABLED,
            label="Show Tutorials",
        )
    )
    return gameplay_menu


def _create_controls_menu() -> MenuNode:
    """Create controls settings menu with random initial values."""
    controls_menu = MenuNode(id="controls", category="Control Settings")
    controls_menu.add_setting(
        Setting(
            id="controls_mouse_sensitivity",
            type=SettingType.FLOAT,
            value=round(random.uniform(0.1, 5.0), 1),
            state=SettingState.DISABLED,
            label="Mouse Sensitivity",
            min_value=0.1,
            max_value=5.0,
        )
    )
    controls_menu.add_setting(
        Setting(
            id="controls_invert_y",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.DISABLED,
            label="Invert Y-Axis",
        )
    )
    controls_menu.add_setting(
        Setting(
            id="controls_vibration",
            type=SettingType.BOOLEAN,
            value=random.choice([True, False]),
            state=SettingState.LOCKED,
            label="Controller Vibration",
        )
    )
    return controls_menu


def _setup_menu_connections(
    main_menu: MenuNode,
    audio_menu: MenuNode,
    graphics_menu: MenuNode,
    gameplay_menu: MenuNode,
    controls_menu: MenuNode,
) -> None:
    """Configure navigation connections between menus."""
    main_menu.connections = ["audio", "graphics", "gameplay", "controls"]
    audio_menu.connections = ["main", "graphics", "gameplay"]
    graphics_menu.connections = ["main", "audio", "controls"]
    gameplay_menu.connections = ["main", "audio", "controls"]
    controls_menu.connections = ["main", "graphics", "gameplay"]


def _setup_dependencies(game_state: GameState) -> None:
    """Configure all setting dependencies to create the gameplay challenge web."""
    resolver = game_state.resolver

    # Audio dependencies
    resolver.add_dependency("audio_master_volume", SimpleDependency("graphics_resolution", SettingState.ENABLED))
    resolver.add_dependency("audio_enable", SimpleDependency("audio_master_volume", SettingState.ENABLED))
    resolver.add_dependency("audio_speaker_config", SimpleDependency("audio_enable", SettingState.ENABLED))
    resolver.add_dependency("audio_speaker_config", SimpleDependency("gameplay_difficulty", SettingState.ENABLED))
    resolver.add_dependency("audio_3d_sound", SimpleDependency("audio_speaker_config", SettingState.ENABLED))
    resolver.add_dependency("audio_3d_sound", SimpleDependency("graphics_quality", SettingState.ENABLED))

    # Graphics dependencies
    resolver.add_dependency("graphics_vsync", SimpleDependency("gameplay_autosave", SettingState.ENABLED))
    resolver.add_dependency("graphics_quality", SimpleDependency("controls_mouse_sensitivity", SettingState.ENABLED))
    resolver.add_dependency("graphics_antialiasing", SimpleDependency("graphics_vsync", SettingState.ENABLED))
    resolver.add_dependency("graphics_antialiasing", SimpleDependency("gameplay_tutorials", SettingState.ENABLED))

    # Gameplay dependencies
    resolver.add_dependency("gameplay_difficulty", SimpleDependency("graphics_resolution", SettingState.ENABLED))
    resolver.add_dependency("gameplay_autosave", SimpleDependency("gameplay_difficulty", SettingState.ENABLED))
    resolver.add_dependency("gameplay_tutorials", SimpleDependency("controls_invert_y", SettingState.ENABLED))

    # Controls dependencies
    resolver.add_dependency("controls_mouse_sensitivity", SimpleDependency("graphics_resolution", SettingState.ENABLED))
    resolver.add_dependency("controls_invert_y", SimpleDependency("controls_mouse_sensitivity", SettingState.ENABLED))
    resolver.add_dependency("controls_vibration", SimpleDependency("controls_invert_y", SettingState.ENABLED))
    resolver.add_dependency("controls_vibration", SimpleDependency("audio_enable", SettingState.ENABLED))

    # Start Game requires ALL settings
    for setting_id in [
        "audio_master_volume", "audio_enable", "audio_speaker_config", "audio_3d_sound",
        "graphics_resolution", "graphics_vsync", "graphics_quality", "graphics_antialiasing",
        "gameplay_difficulty", "gameplay_autosave", "gameplay_tutorials",
        "controls_mouse_sensitivity", "controls_invert_y", "controls_vibration",
    ]:
        resolver.add_dependency("start_game", SimpleDependency(setting_id, SettingState.ENABLED))


def create_demo_game() -> GameState:
    """Orchestrate creation of game state with menus and dependencies.

    Follows Single Responsibility Principle by delegating to specialized functions.
    """
    game_state = GameState()

    # Create all menus
    main_menu = _create_main_menu()
    audio_menu = _create_audio_menu()
    graphics_menu = _create_graphics_menu()
    gameplay_menu = _create_gameplay_menu()
    controls_menu = _create_controls_menu()

    # Setup navigation connections
    _setup_menu_connections(main_menu, audio_menu, graphics_menu, gameplay_menu, controls_menu)

    # Add menus to game state
    game_state.add_menu(main_menu)
    game_state.add_menu(audio_menu)
    game_state.add_menu(graphics_menu)
    game_state.add_menu(gameplay_menu)
    game_state.add_menu(controls_menu)

    # Setup dependency web
    _setup_dependencies(game_state)

    return game_state


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

        game_state = create_demo_game()

        config_dir = Path(__file__).parent / "config"
        ui_loop = UILoop(game_state, str(config_dir))

        ui_loop.start("main")

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
