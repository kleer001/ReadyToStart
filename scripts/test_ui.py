#!/usr/bin/env python3

from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting
from ready_to_start.ui.main_loop import UILoop


def create_sample_game_state() -> GameState:
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
            value=True,
            state=SettingState.ENABLED,
            label="Enable Audio",
        )
    )
    audio_menu.add_setting(
        Setting(
            id="audio_speaker_config",
            type=SettingType.STRING,
            value="stereo",
            state=SettingState.LOCKED,
            label="Speaker Config",
        )
    )

    graphics_menu = MenuNode(id="graphics", category="Graphics Settings")
    graphics_menu.add_setting(
        Setting(
            id="graphics_resolution",
            type=SettingType.STRING,
            value="1920x1080",
            state=SettingState.ENABLED,
            label="Resolution",
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
            state=SettingState.ENABLED,
            label="Quality Level",
            min_value=1,
            max_value=5,
        )
    )

    audio_menu.connections = ["graphics"]
    graphics_menu.connections = ["audio"]

    game_state.add_menu(audio_menu)
    game_state.add_menu(graphics_menu)

    return game_state


def main():
    print("Ready to Start - UI Test")
    print("=" * 40)
    print()

    game_state = create_sample_game_state()
    ui_loop = UILoop(game_state, "config")

    ui_loop.start("audio")


if __name__ == "__main__":
    main()
