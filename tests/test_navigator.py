"""Tests for navigator module."""


from ready_to_start.core.enums import SettingState
from ready_to_start.core.navigator import MenuNavigator


def test_navigator_initialization(game_state):
    """Test navigator initialization."""
    navigator = MenuNavigator(game_state)
    assert navigator.state == game_state


def test_get_available_options(multi_menu_state):
    """Test getting available navigation options."""
    navigator = MenuNavigator(multi_menu_state)

    # From main menu
    options = navigator.get_available_options()
    assert "submenu_a" in options
    assert "submenu_b" not in options  # Requires main_enabled

    # Enable the requirement
    setting = multi_menu_state.get_setting("main_enabled")
    setting.state = SettingState.ENABLED

    options = navigator.get_available_options()
    assert "submenu_a" in options
    assert "submenu_b" in options  # Now accessible


def test_can_navigate_to(multi_menu_state):
    """Test checking navigation possibility."""
    navigator = MenuNavigator(multi_menu_state)

    assert navigator.can_navigate_to("submenu_a") is True
    assert navigator.can_navigate_to("submenu_b") is False
    assert navigator.can_navigate_to("nonexistent") is False


def test_navigate(multi_menu_state):
    """Test navigation method."""
    navigator = MenuNavigator(multi_menu_state)

    # Navigate to accessible menu
    result = navigator.navigate("submenu_a")
    assert result is True
    assert multi_menu_state.current_menu == "submenu_a"

    # Try to navigate to inaccessible menu
    multi_menu_state.current_menu = "main"  # Reset
    result = navigator.navigate("submenu_b")
    assert result is False
    assert multi_menu_state.current_menu == "main"  # Unchanged


def test_available_options_no_current_menu():
    """Test available options when no current menu."""
    from ready_to_start.core.game_state import GameState

    state = GameState()
    navigator = MenuNavigator(state)

    options = navigator.get_available_options()
    assert len(options) == 0


def test_navigation_chain(multi_menu_state):
    """Test navigating through multiple menus."""
    navigator = MenuNavigator(multi_menu_state)

    # Main -> Submenu A
    assert navigator.navigate("submenu_a") is True

    # Enable requirement for submenu B
    setting = multi_menu_state.get_setting("main_enabled")
    setting.state = SettingState.ENABLED

    # Go back to main
    multi_menu_state.current_menu = "main"

    # Main -> Submenu B (now accessible)
    assert navigator.navigate("submenu_b") is True
    assert multi_menu_state.current_menu == "submenu_b"
