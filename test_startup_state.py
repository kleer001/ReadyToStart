#!/usr/bin/env python3
"""Diagnostic script to check game state at startup."""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from start import create_demo_game
from ready_to_start.core.enums import SettingState

def diagnose_startup_state():
    """Check the state of the game at startup."""
    print("=" * 70)
    print("DIAGNOSTIC: Game State at Startup")
    print("=" * 70)

    game_state = create_demo_game()

    print("\n1. CHECKING LOCKED SETTINGS STATE:")
    print("-" * 70)

    locked_settings = [
        "audio_speaker_config",
        "graphics_antialiasing",
        "controls_vibration"
    ]

    for setting_id in locked_settings:
        setting = game_state.get_setting(setting_id)
        if setting:
            print(f"\n  {setting.label} ({setting_id}):")
            print(f"    State: {setting.state}")
            print(f"    Value: {setting.value}")

            # Check if it has dependencies
            if setting_id in game_state.resolver.dependencies:
                print(f"    Has dependencies: YES")
                deps = game_state.resolver.dependencies[setting_id]
                print(f"    Number of dependencies: {len(deps)}")

                # Check if dependencies are satisfied
                can_enable = game_state.resolver.can_enable(setting_id, game_state)
                print(f"    Dependencies satisfied: {can_enable}")

                # Get hints
                hints = game_state.get_dependency_hints(setting_id)
                if hints:
                    print(f"    Hints:")
                    for hint in hints:
                        print(f"      • {hint}")
                else:
                    print(f"    Hints: None")
            else:
                print(f"    Has dependencies: NO ⚠️ WARNING!")
        else:
            print(f"  ❌ Setting {setting_id} not found!")

    print("\n\n2. CHECKING PREREQUISITE SETTINGS:")
    print("-" * 70)

    prereq_settings = [
        "audio_enable",
        "graphics_vsync",
        "controls_invert_y"
    ]

    for setting_id in prereq_settings:
        setting = game_state.get_setting(setting_id)
        if setting:
            print(f"\n  {setting.label} ({setting_id}):")
            print(f"    State: {setting.state}")
            print(f"    Value: {setting.value}")
        else:
            print(f"  ❌ Setting {setting_id} not found!")

    print("\n\n3. CHECKING DEPENDENCY RESOLVER:")
    print("-" * 70)
    print(f"  Total dependencies registered: {len(game_state.resolver.dependencies)}")
    print(f"  Settings with dependencies: {list(game_state.resolver.dependencies.keys())}")

    print("\n\n4. SIMULATING ENABLING PREREQUISITES:")
    print("-" * 70)

    # Enable audio_enable
    audio_setting = game_state.get_setting("audio_enable")
    print(f"\n  Changing audio_enable from {audio_setting.state} to ENABLED...")
    audio_setting.state = SettingState.ENABLED

    # Check if speaker config can now be enabled
    can_enable_speaker = game_state.resolver.can_enable("audio_speaker_config", game_state)
    print(f"  Can enable audio_speaker_config now? {can_enable_speaker}")

    # Call propagate_changes
    print(f"\n  Calling propagate_changes()...")
    game_state.propagate_changes()

    speaker_setting = game_state.get_setting("audio_speaker_config")
    print(f"  audio_speaker_config state after propagate: {speaker_setting.state}")

    if speaker_setting.state == SettingState.DISABLED:
        print(f"  ✅ LOCKED → DISABLED transition worked!")
    else:
        print(f"  ❌ WARNING: Expected DISABLED but got {speaker_setting.state}")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    diagnose_startup_state()
