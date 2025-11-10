#!/usr/bin/env python3
"""Generate sample menus and settings for testing.

This script creates a sample game state with multiple menus
and settings that can be used for manual testing and development.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.navigator import MenuNavigator
from src.core.types import Setting


def create_sample_game_state() -> GameState:
    """Create a sample game state with menus and settings."""
    state = GameState()

    # Main Menu
    main_menu = MenuNode(id="main_menu", category="Main")
    main_menu.connections = ["graphics_menu", "audio_menu", "gameplay_menu"]

    enable_advanced = Setting(
        id="enable_advanced",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Enable Advanced Settings",
    )
    main_menu.add_setting(enable_advanced)

    # Graphics Menu
    graphics_menu = MenuNode(id="graphics_menu", category="Graphics")
    graphics_menu.connections = ["main_menu", "advanced_graphics"]

    resolution = Setting(
        id="resolution_width",
        type=SettingType.INTEGER,
        value=1920,
        state=SettingState.ENABLED,
        label="Resolution Width",
        min_value=640,
        max_value=3840,
    )
    vsync = Setting(
        id="vsync",
        type=SettingType.BOOLEAN,
        value=True,
        state=SettingState.ENABLED,
        label="VSync",
    )
    graphics_menu.add_setting(resolution)
    graphics_menu.add_setting(vsync)

    # Advanced Graphics (requires enable_advanced)
    advanced_graphics = MenuNode(id="advanced_graphics", category="Advanced Graphics")
    advanced_graphics.requirements = [
        {"setting_id": "enable_advanced", "state": "enabled"}
    ]

    shadow_quality = Setting(
        id="shadow_quality",
        type=SettingType.INTEGER,
        value=2,
        state=SettingState.DISABLED,
        label="Shadow Quality",
        min_value=0,
        max_value=4,
    )
    advanced_graphics.add_setting(shadow_quality)

    # Audio Menu
    audio_menu = MenuNode(id="audio_menu", category="Audio")
    audio_menu.connections = ["main_menu"]

    master_volume = Setting(
        id="master_volume",
        type=SettingType.INTEGER,
        value=80,
        state=SettingState.ENABLED,
        label="Master Volume",
        min_value=0,
        max_value=100,
    )
    music_volume = Setting(
        id="music_volume",
        type=SettingType.INTEGER,
        value=70,
        state=SettingState.ENABLED,
        label="Music Volume",
        min_value=0,
        max_value=100,
    )
    audio_menu.add_setting(master_volume)
    audio_menu.add_setting(music_volume)

    # Gameplay Menu
    gameplay_menu = MenuNode(id="gameplay_menu", category="Gameplay")
    gameplay_menu.connections = ["main_menu"]

    difficulty = Setting(
        id="difficulty",
        type=SettingType.STRING,
        value="Normal",
        state=SettingState.ENABLED,
        label="Difficulty",
    )
    gameplay_menu.add_setting(difficulty)

    # Add all menus to state
    state.add_menu(main_menu)
    state.add_menu(graphics_menu)
    state.add_menu(advanced_graphics)
    state.add_menu(audio_menu)
    state.add_menu(gameplay_menu)

    # Set starting menu
    state.current_menu = "main_menu"

    # Add dependency: shadow_quality requires enable_advanced
    state.resolver.add_dependency(
        "shadow_quality", SimpleDependency("enable_advanced", SettingState.ENABLED)
    )

    return state


def print_game_state(state: GameState):
    """Print game state information."""
    print("\n=== Game State Information ===")
    print(f"Current Menu: {state.current_menu}")
    print(f"Total Menus: {len(state.menus)}")
    print(f"Total Settings: {len(state.settings)}")
    print(f"Visited Menus: {state.visited_menus}")

    print("\n=== Menus ===")
    for menu_id, menu in state.menus.items():
        print(f"\n{menu_id} ({menu.category})")
        print(f"  Settings: {len(menu.settings)}")
        print(f"  Connections: {menu.connections}")
        print(f"  Accessible: {menu.is_accessible(state)}")
        for setting in menu.settings:
            print(f"    - {setting.label}: {setting.value} ({setting.state.value})")


def demo_navigation(state: GameState):
    """Demonstrate navigation."""
    print("\n=== Navigation Demo ===")
    navigator = MenuNavigator(state)

    print(f"Starting at: {state.current_menu}")
    print(f"Available options: {navigator.get_available_options()}")

    # Navigate to graphics
    print("\nNavigating to graphics_menu...")
    navigator.navigate("graphics_menu")
    print(f"Current menu: {state.current_menu}")
    print(f"Available options: {navigator.get_available_options()}")

    # Try to access advanced graphics (should fail)
    print("\nTrying to navigate to advanced_graphics (should fail)...")
    result = navigator.navigate("advanced_graphics")
    print(f"Navigation result: {result}")

    # Enable advanced settings
    print("\nEnabling advanced settings...")
    state.navigate_to("main_menu")
    enable_advanced = state.get_setting("enable_advanced")
    enable_advanced.state = SettingState.ENABLED
    state.navigate_to("graphics_menu")

    print(f"Available options: {navigator.get_available_options()}")
    print("\nTrying to navigate to advanced_graphics again...")
    result = navigator.navigate("advanced_graphics")
    print(f"Navigation result: {result}")
    print(f"Current menu: {state.current_menu}")


if __name__ == "__main__":
    print("Generating sample game state...")
    game_state = create_sample_game_state()
    print_game_state(game_state)
    demo_navigation(game_state)
    print("\n=== Done! ===")
