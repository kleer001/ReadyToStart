# Testing Guide: LOCKED Settings Dependencies

## Summary of Fixes

The LOCKED settings dependency system has been fixed. Here's what should now work:

1. **LOCKED settings show hints when selected** - When you try to select a LOCKED setting, you'll see a message explaining what needs to be done to unlock it
2. **Auto-unlock when dependencies are met** - When you enable the prerequisite setting, LOCKED settings automatically unlock to DISABLED state
3. **Settings can then be configured** - Once unlocked, you can edit the previously-locked setting

## Test Scenario

### Initial State
When you run `python start.py`, there are 3 LOCKED settings:
- `audio_speaker_config` (Speaker Configuration) - requires `audio_enable` to be ENABLED
- `graphics_antialiasing` (Anti-Aliasing) - requires `graphics_vsync` to be ENABLED
- `controls_vibration` (Controller Vibration) - requires `controls_invert_y` to be ENABLED

### How to Test

1. **Run the game**:
   ```bash
   python start.py
   ```

2. **Navigate to Audio Settings** (you start here by default)

3. **Try to select "Speaker Configuration"**:
   - Move down with arrow keys or 'j' until "Speaker Configuration" is selected
   - Press Enter
   - **EXPECTED**: You should see warning messages:
     ```
     [WARNING] 'Speaker Configuration' is locked. To unlock:
     [WARNING]   • Requires 'Enable Audio' to be enabled
     ```
   - **EXPECTED**: The setting should NOT be editable (you shouldn't be prompted for input)

4. **Enable the prerequisite**:
   - Select "Enable Audio"
   - Press Enter
   - Enter 'true' or 't'
   - **EXPECTED**: Success message and the setting state changes to enabled

5. **Check if Speaker Configuration auto-unlocked**:
   - Try selecting "Speaker Configuration" again
   - **EXPECTED**: Now you should be prompted to edit the value (not blocked)
   - The state should have changed from LOCKED to DISABLED after enabling audio

6. **Repeat for other LOCKED settings**:
   - Navigate to Graphics menu (press 'd' or right arrow)
   - Enable "V-Sync" first, then try "Anti-Aliasing"
   - Navigate to Controls menu
   - Enable "Invert Y-Axis" first, then try "Controller Vibration"

## Visual Indicators

LOCKED settings appear in the menu as:
```
  3. [~] Speaker Configuration (locked)
```

Where:
- `[~]` is the LOCKED indicator (in yellow)
- `(locked)` is the state label

## Important Notes

1. **Hints only appear when you TRY to select a LOCKED setting** - they are not shown in the menu listing by default
2. **Messages timeout after 3 seconds** - so read them before pressing more keys
3. **Auto-unlock happens during propagate_changes()** - which is called after successfully editing any setting

## Automated Tests

Run these tests to verify the fixes:

```bash
# Test basic functionality
python test_fixes.py

# Test LOCKED settings unlock mechanism
python test_locked_settings.py

# Test startup state
python test_startup_state.py

# Test UI interaction
python test_ui_locked_interaction.py
```

All tests should pass with ✅ indicators.

## Troubleshooting

If hints aren't showing:
1. Make sure you're actually pressing Enter on a LOCKED setting
2. Check that messages haven't expired (they disappear after 3 seconds)
3. Look at the bottom of the screen for [WARNING] messages in yellow
4. Try running the automated tests to verify the code is working

If settings won't unlock:
1. Make sure you actually enabled the prerequisite setting to ENABLED state (not just edited it)
2. The prerequisite's value needs to be set for boolean settings (true)
3. Auto-unlock happens after propagate_changes() is called (which happens after each edit)
