#!/usr/bin/env python3
"""Quick test to verify the fixes for propagate_changes and dependency hints."""

from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.core.enums import SettingState, SettingType
from src.core.dependencies import SimpleDependency

def test_propagate_changes():
    """Test that propagate_changes() method exists and works."""
    print("Testing propagate_changes()...")

    # Create game state
    state = GameState()

    # Create a simple menu with settings
    menu = MenuNode(id="test_menu", category="Test")
    setting1 = Setting(
        id="setting1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Test Setting 1"
    )
    setting2 = Setting(
        id="setting2",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Test Setting 2"
    )
    menu.add_setting(setting1)
    menu.add_setting(setting2)
    state.add_menu(menu)

    # Call propagate_changes - should not raise AttributeError
    try:
        state.propagate_changes()
        print("✓ propagate_changes() method exists and works")
    except AttributeError as e:
        print(f"✗ FAILED: {e}")
        return False

    return True

def test_dependency_hints():
    """Test that dependency hints work correctly."""
    print("\nTesting dependency hints...")

    # Create game state
    state = GameState()

    # Create two menus with settings
    menu1 = MenuNode(id="menu1", category="Audio")
    audio_setting = Setting(
        id="audio_enable",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Enable Audio"
    )
    menu1.add_setting(audio_setting)
    state.add_menu(menu1)

    menu2 = MenuNode(id="menu2", category="Sound")
    volume_setting = Setting(
        id="master_volume",
        type=SettingType.INTEGER,
        value=50,
        state=SettingState.DISABLED,
        label="Master Volume",
        min_value=0,
        max_value=100
    )
    menu2.add_setting(volume_setting)
    state.add_menu(menu2)

    # Add dependency: master_volume requires audio_enable to be ENABLED
    state.resolver.add_dependency(
        "master_volume",
        SimpleDependency("audio_enable", SettingState.ENABLED)
    )

    # Test 1: Audio disabled, volume should not be able to enable
    can_enable = state.resolver.can_enable("master_volume", state)
    if not can_enable:
        print("✓ Correctly detects that master_volume cannot be enabled")
    else:
        print("✗ FAILED: master_volume should not be able to enable")
        return False

    # Test 2: Get hints for why master_volume can't be enabled
    hints = state.get_dependency_hints("master_volume")
    if hints:
        print(f"✓ Got dependency hints: {hints}")
        expected_hint = "Requires 'Enable Audio' to be enabled"
        if expected_hint in hints:
            print(f"✓ Hint message is correct: '{expected_hint}'")
        else:
            print(f"✗ FAILED: Expected hint '{expected_hint}' not found in {hints}")
            return False
    else:
        print("✗ FAILED: No hints returned")
        return False

    # Test 3: Enable audio, then volume should be able to enable
    audio_setting.state = SettingState.ENABLED
    can_enable = state.resolver.can_enable("master_volume", state)
    if can_enable:
        print("✓ After enabling audio, master_volume can be enabled")
    else:
        print("✗ FAILED: master_volume should be able to enable after audio is enabled")
        return False

    # Test 4: Hints should be empty now
    hints = state.get_dependency_hints("master_volume")
    if not hints:
        print("✓ No hints when dependencies are satisfied")
    else:
        print(f"✗ FAILED: Got hints when dependencies are satisfied: {hints}")
        return False

    return True

def test_completion_propagation():
    """Test that completion states are updated after propagate_changes."""
    print("\nTesting completion state propagation...")

    # Create game state
    state = GameState()

    # Create menu with settings
    menu = MenuNode(id="test_menu", category="Test")
    setting1 = Setting(
        id="setting1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Setting 1"
    )
    setting2 = Setting(
        id="setting2",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Setting 2"
    )
    menu.add_setting(setting1)
    menu.add_setting(setting2)
    state.add_menu(menu)

    # Initially, menu should be incomplete
    from src.core.enums import CompletionState
    initial_completion = menu.calculate_completion()
    if initial_completion == CompletionState.INCOMPLETE:
        print("✓ Menu starts as incomplete")
    else:
        print(f"✗ FAILED: Menu should start as incomplete, got {initial_completion}")
        return False

    # Enable one setting and propagate
    setting1.state = SettingState.ENABLED
    state.propagate_changes()

    # Menu should now be partial
    if menu.completion_state == CompletionState.PARTIAL:
        print("✓ After enabling one setting, menu is partial")
    else:
        print(f"✗ FAILED: Menu should be partial, got {menu.completion_state}")
        return False

    # Enable second setting and propagate
    setting2.state = SettingState.ENABLED
    state.propagate_changes()

    # Menu should now be complete
    if menu.completion_state == CompletionState.COMPLETE:
        print("✓ After enabling all settings, menu is complete")
    else:
        print(f"✗ FAILED: Menu should be complete, got {menu.completion_state}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Testing fixes for propagate_changes and dependency hints")
    print("=" * 60)

    all_pass = True

    all_pass &= test_propagate_changes()
    all_pass &= test_dependency_hints()
    all_pass &= test_completion_propagation()

    print("\n" + "=" * 60)
    if all_pass:
        print("✓ All tests PASSED!")
    else:
        print("✗ Some tests FAILED")
    print("=" * 60)
