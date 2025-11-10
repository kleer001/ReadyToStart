#!/usr/bin/env python3
"""
Ready to Start - A game about settings menus.

Because what you really wanted was to configure things
that don't actually do anything. Enjoy.
"""

import sys
from pathlib import Path

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.ui.main_loop import UILoop


def create_demo_game() -> GameState:
    game_state = GameState()

    # MAIN MENU - The core of the game loop
    # The "Start Game" button is locked and requires all other settings to be configured
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

    audio_menu = MenuNode(id="audio", category="Audio Settings")
    audio_menu.add_setting(
        Setting(
            id="audio_master_volume",
            type=SettingType.INTEGER,
            value=50,
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
            value=False,
            state=SettingState.DISABLED,
            label="Enable Audio",
        )
    )
    audio_menu.add_setting(
        Setting(
            id="audio_speaker_config",
            type=SettingType.STRING,
            value="stereo",
            state=SettingState.LOCKED,
            label="Speaker Configuration",
        )
    )
    audio_menu.add_setting(
        Setting(
            id="audio_3d_sound",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.DISABLED,
            label="3D Audio Processing",
        )
    )

    graphics_menu = MenuNode(id="graphics", category="Graphics Settings")
    graphics_menu.add_setting(
        Setting(
            id="graphics_resolution",
            type=SettingType.STRING,
            value="1920x1080",
            state=SettingState.ENABLED,  # Pre-configured! The only "free" setting
            label="Screen Resolution",
        )
    )
    graphics_menu.add_setting(
        Setting(
            id="graphics_vsync",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.DISABLED,
            label="V-Sync",
        )
    )
    graphics_menu.add_setting(
        Setting(
            id="graphics_quality",
            type=SettingType.INTEGER,
            value=3,
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
            value=False,
            state=SettingState.LOCKED,
            label="Anti-Aliasing",
        )
    )

    gameplay_menu = MenuNode(id="gameplay", category="Gameplay Settings")
    gameplay_menu.add_setting(
        Setting(
            id="gameplay_difficulty",
            type=SettingType.INTEGER,
            value=2,
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
            value=False,
            state=SettingState.DISABLED,
            label="Auto-Save",
        )
    )
    gameplay_menu.add_setting(
        Setting(
            id="gameplay_tutorials",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.DISABLED,
            label="Show Tutorials",
        )
    )

    controls_menu = MenuNode(id="controls", category="Control Settings")
    controls_menu.add_setting(
        Setting(
            id="controls_mouse_sensitivity",
            type=SettingType.FLOAT,
            value=1.0,
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
            value=False,
            state=SettingState.DISABLED,
            label="Invert Y-Axis",
        )
    )
    controls_menu.add_setting(
        Setting(
            id="controls_vibration",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Controller Vibration",
        )
    )

    # Main menu connects to all settings menus
    main_menu.connections = ["audio", "graphics", "gameplay", "controls"]
    audio_menu.connections = ["main", "graphics", "gameplay"]
    graphics_menu.connections = ["main", "audio", "controls"]
    gameplay_menu.connections = ["main", "audio", "controls"]
    controls_menu.connections = ["main", "graphics", "gameplay"]

    game_state.add_menu(main_menu)
    game_state.add_menu(audio_menu)
    game_state.add_menu(graphics_menu)
    game_state.add_menu(gameplay_menu)
    game_state.add_menu(controls_menu)

    # COMPLEX WEB OF DEPENDENCIES - Not a straight line!
    # Creates the frustrating "need X to configure Y, but need Z to configure X" loop
    # NOTE: Only graphics_resolution is pre-configured (ENABLED). Everything else requires dependencies!

    # Audio dependencies
    # Master volume needs resolution configured (makes no sense, that's the point)
    game_state.resolver.add_dependency(
        "audio_master_volume",
        SimpleDependency("graphics_resolution", SettingState.ENABLED)
    )

    # Enable Audio requires master volume to be set first
    game_state.resolver.add_dependency(
        "audio_enable",
        SimpleDependency("audio_master_volume", SettingState.ENABLED)
    )

    # Speaker Configuration requires audio to be enabled AND difficulty set
    game_state.resolver.add_dependency(
        "audio_speaker_config",
        SimpleDependency("audio_enable", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "audio_speaker_config",
        SimpleDependency("gameplay_difficulty", SettingState.ENABLED)
    )

    # 3D sound requires speaker config AND quality level
    game_state.resolver.add_dependency(
        "audio_3d_sound",
        SimpleDependency("audio_speaker_config", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "audio_3d_sound",
        SimpleDependency("graphics_quality", SettingState.ENABLED)
    )

    # Graphics dependencies
    # V-Sync needs autosave configured (circular-ish dependency fun)
    game_state.resolver.add_dependency(
        "graphics_vsync",
        SimpleDependency("gameplay_autosave", SettingState.ENABLED)
    )

    # Quality needs mouse sensitivity
    game_state.resolver.add_dependency(
        "graphics_quality",
        SimpleDependency("controls_mouse_sensitivity", SettingState.ENABLED)
    )

    # Anti-aliasing requires V-Sync AND tutorials
    game_state.resolver.add_dependency(
        "graphics_antialiasing",
        SimpleDependency("graphics_vsync", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "graphics_antialiasing",
        SimpleDependency("gameplay_tutorials", SettingState.ENABLED)
    )

    # Gameplay dependencies
    # Difficulty needs resolution (you need to see the difficulty, obviously)
    game_state.resolver.add_dependency(
        "gameplay_difficulty",
        SimpleDependency("graphics_resolution", SettingState.ENABLED)
    )

    # Autosave needs difficulty set (need to know what to save!)
    game_state.resolver.add_dependency(
        "gameplay_autosave",
        SimpleDependency("gameplay_difficulty", SettingState.ENABLED)
    )

    # Tutorials needs invert Y configured (must learn controls first!)
    game_state.resolver.add_dependency(
        "gameplay_tutorials",
        SimpleDependency("controls_invert_y", SettingState.ENABLED)
    )

    # Controls dependencies
    # Mouse sensitivity needs resolution set (need screen space calibration!)
    game_state.resolver.add_dependency(
        "controls_mouse_sensitivity",
        SimpleDependency("graphics_resolution", SettingState.ENABLED)
    )

    # Invert Y needs mouse sensitivity set first
    game_state.resolver.add_dependency(
        "controls_invert_y",
        SimpleDependency("controls_mouse_sensitivity", SettingState.ENABLED)
    )

    # Controller vibration requires Y-axis inversion AND audio enabled
    game_state.resolver.add_dependency(
        "controls_vibration",
        SimpleDependency("controls_invert_y", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "controls_vibration",
        SimpleDependency("audio_enable", SettingState.ENABLED)
    )

    # THE KEY GAMEPLAY MECHANIC:
    # Start Game requires ALL other settings to be enabled
    # This creates the core frustration loop
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("audio_master_volume", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("audio_enable", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("audio_speaker_config", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("audio_3d_sound", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("graphics_resolution", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("graphics_vsync", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("graphics_quality", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("graphics_antialiasing", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("gameplay_difficulty", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("gameplay_autosave", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("gameplay_tutorials", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("controls_mouse_sensitivity", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("controls_invert_y", SettingState.ENABLED)
    )
    game_state.resolver.add_dependency(
        "start_game",
        SimpleDependency("controls_vibration", SettingState.ENABLED)
    )

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
