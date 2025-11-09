"""Tests for menu module."""

from src.core.enums import CompletionState, SettingState, SettingType
from src.core.menu import MenuNode
from src.core.types import Setting


def test_menu_creation(sample_menu):
    """Test basic menu creation."""
    assert sample_menu.id == "test_menu"
    assert sample_menu.category == "Test"
    assert len(sample_menu.settings) == 1
    assert sample_menu.visited is False


def test_add_setting(sample_menu, numeric_setting):
    """Test adding settings to menu."""
    initial_count = len(sample_menu.settings)
    sample_menu.add_setting(numeric_setting)
    assert len(sample_menu.settings) == initial_count + 1


def test_menu_accessibility(game_state):
    """Test menu accessibility without requirements."""
    menu = game_state.get_menu("test_menu")
    assert menu.is_accessible(game_state) is True


def test_menu_accessibility_with_requirements(multi_menu_state):
    """Test menu accessibility with requirements."""
    submenu_a = multi_menu_state.get_menu("submenu_a")
    submenu_b = multi_menu_state.get_menu("submenu_b")

    # Submenu A has no requirements
    assert submenu_a.is_accessible(multi_menu_state) is True

    # Submenu B requires main_enabled to be enabled
    assert submenu_b.is_accessible(multi_menu_state) is False

    # Enable the required setting
    main_enabled = multi_menu_state.get_setting("main_enabled")
    main_enabled.state = SettingState.ENABLED

    # Now submenu B should be accessible
    assert submenu_b.is_accessible(multi_menu_state) is True


def test_calculate_completion():
    """Test completion state calculation."""
    menu = MenuNode(id="test", category="Test")

    # Empty menu is complete
    assert menu.calculate_completion() == CompletionState.COMPLETE

    # Add disabled settings
    setting1 = Setting(
        id="s1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="S1",
    )
    setting2 = Setting(
        id="s2",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="S2",
    )
    menu.add_setting(setting1)
    menu.add_setting(setting2)

    # All disabled = incomplete
    assert menu.calculate_completion() == CompletionState.INCOMPLETE

    # One enabled = partial
    setting1.state = SettingState.ENABLED
    assert menu.calculate_completion() == CompletionState.PARTIAL

    # All enabled = complete
    setting2.state = SettingState.ENABLED
    assert menu.calculate_completion() == CompletionState.COMPLETE


def test_menu_connections():
    """Test menu connection management."""
    menu = MenuNode(id="main", category="Main")
    menu.connections = ["sub1", "sub2", "sub3"]

    assert len(menu.connections) == 3
    assert "sub1" in menu.connections
