"""Tests for dependencies module."""

import pytest

from src.core.dependencies import (
    DependencyResolver,
    SimpleDependency,
    ValueDependency,
)
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting


def test_simple_dependency():
    """Test simple state dependency."""
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="A",
    )
    setting_b = Setting(
        id="b",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="B",
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    state.add_menu(menu)

    # B requires A to be enabled
    dep = SimpleDependency("a", SettingState.ENABLED)

    # A is disabled, so dependency not met
    assert dep.evaluate(state) is False

    # Enable A
    setting_a.state = SettingState.ENABLED
    assert dep.evaluate(state) is True


def test_value_dependency():
    """Test value comparison dependency."""
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.INTEGER,
        value=10,
        state=SettingState.ENABLED,
        label="A",
        min_value=0,
        max_value=100,
    )
    setting_b = Setting(
        id="b",
        type=SettingType.INTEGER,
        value=20,
        state=SettingState.ENABLED,
        label="B",
        min_value=0,
        max_value=100,
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    state.add_menu(menu)

    # Test greater than
    dep_gt = ValueDependency("b", ">", "a")
    assert dep_gt.evaluate(state) is True  # 20 > 10

    dep_lt = ValueDependency("a", "<", "b")
    assert dep_lt.evaluate(state) is True  # 10 < 20

    dep_eq = ValueDependency("a", "==", "b")
    assert dep_eq.evaluate(state) is False  # 10 != 20

    # Change values
    setting_a.value = 20
    assert dep_eq.evaluate(state) is True  # 20 == 20


def test_value_dependency_invalid_operator():
    """Test that invalid operators raise error."""
    with pytest.raises(ValueError):
        ValueDependency("a", "invalid", "b")


def test_dependency_resolver(game_state):
    """Test dependency resolver."""
    resolver = DependencyResolver()

    # Add a simple dependency
    dep = SimpleDependency("test_setting", SettingState.ENABLED)
    resolver.add_dependency("dependent_setting", dep)

    # Test that dependency is checked
    can_enable = resolver.can_enable("dependent_setting", game_state)
    assert can_enable is False  # test_setting is DISABLED

    # Enable test_setting
    setting = game_state.get_setting("test_setting")
    setting.state = SettingState.ENABLED

    can_enable = resolver.can_enable("dependent_setting", game_state)
    assert can_enable is True


def test_resolve_all():
    """Test resolving all dependencies."""
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="A",
    )
    setting_b = Setting(
        id="b",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="B",
    )
    setting_c = Setting(
        id="c",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="C",
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    menu.add_setting(setting_c)
    state.add_menu(menu)

    resolver = DependencyResolver()
    resolver.add_dependency("b", SimpleDependency("a", SettingState.ENABLED))
    resolver.add_dependency("c", SimpleDependency("a", SettingState.DISABLED))

    results = resolver.resolve_all(state)

    assert results["b"] is True  # a is enabled
    assert results["c"] is False  # a is not disabled


def test_multiple_dependencies():
    """Test setting with multiple dependencies."""
    state = GameState()

    setting_a = Setting(
        id="a",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="A",
    )
    setting_b = Setting(
        id="b",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.ENABLED,
        label="B",
    )
    setting_c = Setting(
        id="c",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="C",
    )

    menu = MenuNode(id="test", category="Test")
    menu.add_setting(setting_a)
    menu.add_setting(setting_b)
    menu.add_setting(setting_c)
    state.add_menu(menu)

    resolver = DependencyResolver()
    # C requires both A and B to be enabled
    resolver.add_dependency("c", SimpleDependency("a", SettingState.ENABLED))
    resolver.add_dependency("c", SimpleDependency("b", SettingState.ENABLED))

    # Both are enabled
    assert resolver.can_enable("c", state) is True

    # Disable B
    setting_b.state = SettingState.DISABLED
    assert resolver.can_enable("c", state) is False
