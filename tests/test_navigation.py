import pytest

from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.ui.navigation import NavigationController


@pytest.fixture
def game_state():
    gs = GameState()

    menu1 = MenuNode(id="menu1", category="Menu 1")
    menu2 = MenuNode(id="menu2", category="Menu 2")

    menu1.connections = ["menu2"]
    menu2.connections = ["menu1"]

    gs.add_menu(menu1)
    gs.add_menu(menu2)

    return gs


def test_navigation_navigate_to(game_state):
    nav = NavigationController(game_state)

    success, error = nav.navigate_to("menu1")
    assert success is True
    assert nav.current_menu.id == "menu1"


def test_navigation_navigate_to_invalid(game_state):
    nav = NavigationController(game_state)

    success, error = nav.navigate_to("invalid")
    assert success is False
    assert "not found" in error


def test_navigation_go_back(game_state):
    nav = NavigationController(game_state)

    nav.navigate_to("menu1")
    nav.navigate_to("menu2")

    success, error = nav.go_back()
    assert success is True
    assert nav.current_menu.id == "menu1"


def test_navigation_go_back_at_root(game_state):
    nav = NavigationController(game_state)

    nav.navigate_to("menu1")

    success, error = nav.go_back()
    assert success is False
    assert "root menu" in error


def test_navigation_find_menu_by_name(game_state):
    nav = NavigationController(game_state)

    menu = nav.find_menu_by_name("Menu 1")
    assert menu is not None
    assert menu.id == "menu1"


def test_navigation_find_menu_by_name_case_insensitive(game_state):
    nav = NavigationController(game_state)

    menu = nav.find_menu_by_name("menu 1")
    assert menu is not None
    assert menu.id == "menu1"


def test_navigation_get_available_menus(game_state):
    nav = NavigationController(game_state)

    nav.navigate_to("menu1")
    available = nav.get_available_menus()

    assert len(available) == 1
    assert available[0].id == "menu2"


def test_navigation_command_history(game_state):
    nav = NavigationController(game_state)

    nav.add_command_to_history("list")
    nav.add_command_to_history("edit 1")

    history = nav.get_command_history()
    assert len(history) == 2
    assert history[0] == "list"
