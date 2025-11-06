#!/usr/bin/env python3
"""
Ready to Start - A game about settings menus.

Because what you really wanted was to configure things
that don't actually do anything. Enjoy.
"""

import sys
from pathlib import Path

from ready_to_start.core.dependencies import SimpleDependency
from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting
from ready_to_start.ui.main_loop import UILoop


def create_demo_game() -> GameState:
    game_state = GameState()

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
            state=SettingState.DISABLED,
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

    audio_menu.connections = ["graphics", "gameplay"]
    graphics_menu.connections = ["audio", "controls"]
    gameplay_menu.connections = ["audio", "controls"]
    controls_menu.connections = ["graphics", "gameplay"]

    game_state.add_menu(audio_menu)
    game_state.add_menu(graphics_menu)
    game_state.add_menu(gameplay_menu)
    game_state.add_menu(controls_menu)

    # Add dependencies for locked settings
    # Speaker Configuration requires audio to be enabled first
    game_state.resolver.add_dependency(
        "audio_speaker_config",
        SimpleDependency("audio_enable", SettingState.ENABLED)
    )

    # Anti-aliasing requires V-Sync to be enabled first
    game_state.resolver.add_dependency(
        "graphics_antialiasing",
        SimpleDependency("graphics_vsync", SettingState.ENABLED)
    )

    # Controller vibration requires Y-axis inversion to be configured
    game_state.resolver.add_dependency(
        "controls_vibration",
        SimpleDependency("controls_invert_y", SettingState.ENABLED)
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

        ui_loop.start("audio")

    except KeyboardInterrupt:
        print("\n\nGame interrupted. Your settings remain unsaved. Forever.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        print("The game has crashed. Ironically fitting for a settings menu.")
        sys.exit(1)


if __name__ == "__main__":
    main()
