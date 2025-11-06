"""Tests for game state module."""


from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting


def test_game_state_initialization():
    """Test game state initialization."""
    state = GameState()
    assert len(state.menus) == 0
    assert len(state.settings) == 0
    assert state.current_menu is None
    assert len(state.visited_menus) == 0


def test_add_menu(game_state):
    """Test adding menus to game state."""
    assert len(game_state.menus) == 1
    assert "test_menu" in game_state.menus
    assert "test_setting" in game_state.settings


def test_get_setting(game_state):
    """Test retrieving settings."""
    setting = game_state.get_setting("test_setting")
    assert setting is not None
    assert setting.id == "test_setting"

    # Non-existent setting
    assert game_state.get_setting("nonexistent") is None


def test_get_menu(game_state):
    """Test retrieving menus."""
    menu = game_state.get_menu("test_menu")
    assert menu is not None
    assert menu.id == "test_menu"

    # Non-existent menu
    assert game_state.get_menu("nonexistent") is None


def test_navigate_to(multi_menu_state):
    """Test menu navigation."""
    # Navigate to accessible menu
    result = multi_menu_state.navigate_to("submenu_a")
    assert result is True
    assert multi_menu_state.current_menu == "submenu_a"
    assert "submenu_a" in multi_menu_state.visited_menus

    # Try to navigate to inaccessible menu
    result = multi_menu_state.navigate_to("submenu_b")
    assert result is False
    assert multi_menu_state.current_menu == "submenu_a"  # Unchanged


def test_update_setting(game_state):
    """Test updating setting values."""
    setting = game_state.get_setting("test_setting")
    initial_visit_count = setting.visit_count

    # Update the setting
    result = game_state.update_setting("test_setting", True)
    assert result is True
    assert setting.value is True
    assert setting.visit_count == initial_visit_count + 1
    assert setting.last_modified is not None


def test_update_setting_bounds():
    """Test setting value bounds validation."""
    state = GameState()

    setting = Setting(
        id="bounded",
        type=SettingType.INTEGER,
        value=50,
        state=SettingState.ENABLED,
        label="Bounded",
        min_value=0,
        max_value=100,
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting)
    state.add_menu(menu)

    # Valid update
    assert state.update_setting("bounded", 75) is True
    assert setting.value == 75

    # Below minimum
    assert state.update_setting("bounded", -10) is False
    assert setting.value == 75  # Unchanged

    # Above maximum
    assert state.update_setting("bounded", 150) is False
    assert setting.value == 75  # Unchanged


def test_visited_menus(multi_menu_state):
    """Test visited menus tracking."""
    # Initially no menus visited (current_menu set directly without navigate_to)
    assert len(multi_menu_state.visited_menus) == 0

    multi_menu_state.navigate_to("submenu_a")
    assert len(multi_menu_state.visited_menus) == 1
    assert "submenu_a" in multi_menu_state.visited_menus

    # Navigating again shouldn't duplicate
    multi_menu_state.navigate_to("submenu_a")
    assert multi_menu_state.visited_menus.count("submenu_a") == 1


def test_menu_visited_flag(game_state):
    """Test menu visited flag."""
    menu = game_state.get_menu("test_menu")
    assert menu.visited is False

    game_state.navigate_to("test_menu")
    assert menu.visited is True
