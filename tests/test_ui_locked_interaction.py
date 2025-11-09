#!/usr/bin/env python3
"""Test simulating actual UI interaction with LOCKED settings."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent))

from start import create_demo_game
from ready_to_start.ui.main_loop import UILoop
from ready_to_start.ui.messages import MessageType
from ready_to_start.core.enums import SettingState

def test_ui_locked_interaction():
    """Simulate user trying to select a LOCKED setting."""
    print("=" * 70)
    print("TEST: UI Interaction with LOCKED Settings")
    print("=" * 70)

    game_state = create_demo_game()
    config_dir = Path(__file__).parent / "config"
    ui_loop = UILoop(game_state, str(config_dir))

    # Navigate to audio menu
    success, error = ui_loop.navigation.navigate_to("audio")
    if not success:
        print(f"❌ Failed to navigate to audio menu: {error}")
        return False

    print("\n1. Initial State:")
    print("-" * 70)

    # Check the audio_speaker_config setting
    speaker_setting = game_state.get_setting("audio_speaker_config")
    print(f"  audio_speaker_config state: {speaker_setting.state}")
    print(f"  audio_speaker_config value: {speaker_setting.value}")

    # Get visible settings
    visible_settings = [
        s for s in ui_loop.navigation.current_menu.settings
        if s.state != SettingState.HIDDEN
    ]
    print(f"  Number of visible settings: {len(visible_settings)}")

    # Find the index of the speaker config setting
    speaker_index = None
    for idx, setting in enumerate(visible_settings):
        print(f"    {idx}: {setting.label} - {setting.state}")
        if setting.id == "audio_speaker_config":
            speaker_index = idx

    if speaker_index is None:
        print("❌ Could not find audio_speaker_config in visible settings")
        return False

    print(f"\n  audio_speaker_config is at index {speaker_index}")

    print("\n2. Simulating user selecting LOCKED setting:")
    print("-" * 70)

    # Set selection to the speaker config
    ui_loop.selected_index = speaker_index

    # Clear any existing messages
    ui_loop.message_display.clear_current()

    # Call _select_current() which should block LOCKED settings
    print("  Calling _select_current()...")
    ui_loop._select_current()

    # Check messages
    messages = ui_loop.message_display.current_messages
    print(f"  Messages added: {len(messages)}")
    for msg in messages:
        print(f"    [{msg.type.value}] {msg.text}")

    # Verify setting wasn't modified
    if speaker_setting.state == SettingState.LOCKED:
        print(f"  ✅ Setting still LOCKED (not modified)")
    else:
        print(f"  ❌ WARNING: Setting changed to {speaker_setting.state}")

    # Check if hints were shown
    hint_shown = any("Enable Audio" in msg.text for msg in messages)
    if hint_shown:
        print(f"  ✅ Hints about dependencies shown")
    else:
        print(f"  ❌ WARNING: No hints about dependencies")

    print("\n3. Simulating enabling prerequisite:")
    print("-" * 70)

    # Find and enable audio_enable
    audio_enable = game_state.get_setting("audio_enable")
    print(f"  Before: audio_enable state = {audio_enable.state}")

    # Simulate editing audio_enable
    audio_enable.state = SettingState.ENABLED
    audio_enable.value = True
    print(f"  After manual enable: audio_enable state = {audio_enable.state}")

    # Call propagate_changes
    print(f"  Calling propagate_changes()...")
    game_state.propagate_changes()

    # Check if speaker config was unlocked
    print(f"  After propagate: audio_speaker_config state = {speaker_setting.state}")

    if speaker_setting.state == SettingState.DISABLED:
        print(f"  ✅ LOCKED setting auto-unlocked to DISABLED")
    else:
        print(f"  ❌ WARNING: Expected DISABLED, got {speaker_setting.state}")

    print("\n4. Verifying unlocked setting can now be selected:")
    print("-" * 70)

    # Clear messages
    ui_loop.message_display.clear_current()

    # Try selecting again
    print("  Calling _select_current() on now-unlocked setting...")

    # Mock the setting_editor to avoid actual user input
    with patch.object(ui_loop.setting_editor, 'edit_setting') as mock_edit:
        mock_result = Mock()
        mock_result.success = True
        mock_result.value = "surround"
        mock_edit.return_value = mock_result

        ui_loop._select_current()

    # Check if edit was called (meaning it wasn't blocked)
    if mock_edit.called:
        print(f"  ✅ Setting editor was called (setting is editable)")
    else:
        print(f"  ❌ WARNING: Setting editor was not called")

    # Check final state
    if speaker_setting.state == SettingState.ENABLED:
        print(f"  ✅ Setting transitioned to ENABLED after edit")
    else:
        print(f"  ❌ WARNING: Expected ENABLED, got {speaker_setting.state}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    return True

if __name__ == "__main__":
    test_ui_locked_interaction()
