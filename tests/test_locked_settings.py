#!/usr/bin/env python3
"""Test LOCKED settings unlock when dependencies are satisfied."""

from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting
from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.dependencies import SimpleDependency

def test_locked_settings_unlock():
    """Test that LOCKED settings unlock when dependencies are met."""
    print("Testing LOCKED settings unlock behavior...")

    # Create game state
    state = GameState()

    # Create menu with two settings
    menu = MenuNode(id="test_menu", category="Test")

    # Prerequisite setting
    prereq = Setting(
        id="prereq",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Prerequisite Setting"
    )

    # Locked setting that depends on prereq
    locked = Setting(
        id="locked",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.LOCKED,
        label="Locked Setting"
    )

    menu.add_setting(prereq)
    menu.add_setting(locked)
    state.add_menu(menu)

    # Add dependency: locked requires prereq to be ENABLED
    state.resolver.add_dependency(
        "locked",
        SimpleDependency("prereq", SettingState.ENABLED)
    )

    # Test 1: Locked setting should stay locked initially
    if locked.state == SettingState.LOCKED:
        print("✓ Setting starts as LOCKED")
    else:
        print(f"✗ FAILED: Setting should be LOCKED, got {locked.state}")
        return False

    # Test 2: Check we can get hints for the locked setting
    hints = state.get_dependency_hints("locked")
    if hints and "Prerequisite Setting" in hints[0]:
        print(f"✓ Got hints for LOCKED setting: {hints}")
    else:
        print(f"✗ FAILED: Expected hints with 'Prerequisite Setting', got {hints}")
        return False

    # Test 3: Enable prerequisite
    prereq.state = SettingState.ENABLED
    state.propagate_changes()

    # Test 4: Locked setting should now be unlocked (DISABLED)
    if locked.state == SettingState.DISABLED:
        print("✓ After satisfying dependencies, LOCKED → DISABLED")
    else:
        print(f"✗ FAILED: Setting should be DISABLED after dependencies met, got {locked.state}")
        return False

    # Test 5: Can now enable the unlocked setting
    can_enable = state.resolver.can_enable("locked", state)
    if can_enable:
        print("✓ Can now enable the previously locked setting")
    else:
        print("✗ FAILED: Should be able to enable the setting now")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing LOCKED settings unlock mechanism")
    print("=" * 60)

    if test_locked_settings_unlock():
        print("\n" + "=" * 60)
        print("✓ All LOCKED settings tests PASSED!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ LOCKED settings tests FAILED")
        print("=" * 60)
