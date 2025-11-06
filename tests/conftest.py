"""Pytest fixtures for Ready to Start tests."""

import pytest

from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting


@pytest.fixture
def sample_setting():
    """Create a sample setting for testing."""
    return Setting(
        id="test_setting",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Test Setting",
    )


@pytest.fixture
def numeric_setting():
    """Create a numeric setting with bounds."""
    return Setting(
        id="volume",
        type=SettingType.INTEGER,
        value=50,
        state=SettingState.ENABLED,
        label="Volume",
        min_value=0,
        max_value=100,
    )


@pytest.fixture
def sample_menu(sample_setting):
    """Create a sample menu with a setting."""
    menu = MenuNode(id="test_menu", category="Test")
    menu.add_setting(sample_setting)
    return menu


@pytest.fixture
def game_state(sample_menu):
    """Create a game state with a sample menu."""
    state = GameState()
    state.add_menu(sample_menu)
    state.current_menu = "test_menu"
    return state


@pytest.fixture
def multi_menu_state():
    """Create a game state with multiple connected menus."""
    state = GameState()

    # Create main menu
    main_menu = MenuNode(id="main", category="Main")
    main_setting = Setting(
        id="main_enabled",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Enable Main",
    )
    main_menu.add_setting(main_setting)
    main_menu.connections = ["submenu_a", "submenu_b"]

    # Create submenu A (accessible)
    submenu_a = MenuNode(id="submenu_a", category="SubA")
    setting_a = Setting(
        id="setting_a",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Setting A",
    )
    submenu_a.add_setting(setting_a)

    # Create submenu B (requires main_enabled)
    submenu_b = MenuNode(id="submenu_b", category="SubB")
    submenu_b.requirements = [{"setting_id": "main_enabled", "state": "enabled"}]
    setting_b = Setting(
        id="setting_b",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Setting B",
    )
    submenu_b.add_setting(setting_b)

    state.add_menu(main_menu)
    state.add_menu(submenu_a)
    state.add_menu(submenu_b)
    state.current_menu = "main"

    return state
