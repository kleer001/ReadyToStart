# Ready to Start - Phase 4 Detailed Roadmap

## Phase 4: UI Implementation

### 4.1 Text Renderer Core
**Goal:** Basic text-based display system

**Files:**
- `ui/renderer.py`
- `ui/components.py`
- `tests/test_renderer.py`

**Key Components:**
- `TextRenderer` class - handles screen clearing, buffer management
- `Component` base class - abstract interface for all UI elements
- `render()` method - outputs to terminal with ANSI codes
- `clear_screen()` - platform-agnostic screen clearing

**Implementation Notes:**
- Use ANSI escape codes for colors/formatting (don't use curses - too complex)
- Simple string concatenation and `print()` for output
- No external UI libraries needed
- Support basic formatting: bold, colors, borders

**Config:**
- `config/ui.ini` - color schemes, box characters, layout parameters

**Testing:**
- Mock stdout for output verification
- Test ANSI code generation
- Verify layout calculations

**Procedural:** None (rendering logic)

---

### 4.2 Menu Display Component
**Goal:** Render menu nodes as text

**Files:**
- `ui/menu_display.py`
- `tests/test_menu_display.py`

**Key Components:**
- `MenuDisplay` class - renders current menu
- Show menu title/category
- List all settings with their current states
- Display available navigation options
- Show setting indices for selection

**Display Format:**
```
╔═══════════════════════════════════════╗
║ AUDIO SETTINGS                        ║
╠═══════════════════════════════════════╣
║ 1. [ ] Master Volume (disabled)       ║
║ 2. [X] Enable Audio (enabled)         ║
║ 3. [~] Speaker Config (locked)        ║
║ 4. [ ] Microphone (hidden)            ║
╠═══════════════════════════════════════╣
║ Available Menus: Graphics, User       ║
╚═══════════════════════════════════════╝
```

**State Indicators:**
- `[ ]` - disabled
- `[X]` - enabled  
- `[~]` - locked
- `[*]` - blinking (alternate between states)
- Hidden settings not shown

**Config:**
- `config/ui.ini` - box drawing characters, width, padding

**Testing:**
- Render with various setting states
- Hidden setting exclusion
- Width wrapping

**Procedural:** None (display logic)

---

### 4.3 Setting Editor Component
**Goal:** Allow user to modify setting values

**Files:**
- `ui/setting_editor.py`
- `tests/test_setting_editor.py`

**Key Components:**
- `SettingEditor` class - handles setting modification
- Type-specific editors:
  - `BooleanEditor` - toggle true/false
  - `IntegerEditor` - increment/decrement or direct input
  - `FloatEditor` - similar to integer with decimal support
  - `StringEditor` - text input with validation

**User Interactions:**
- Display current value
- Show allowed range (for numeric types)
- Validate input before applying
- Show error messages for invalid input
- Check dependencies before allowing changes

**Display Format:**
```
Edit: Master Volume (integer)
Current value: 50
Range: 0-100
Enter new value: _
```

**Config:**
- `config/ui.ini` - editor prompts, error messages

**Testing:**
- Type-specific validation
- Range enforcement
- Dependency checking integration
- Invalid input handling

**Procedural:** None (editor logic)

---

### 4.4 Navigation System
**Goal:** Handle menu traversal and input

**Files:**
- `ui/navigation.py`
- `tests/test_navigation.py`

**Key Components:**
- `NavigationController` class - manages user input
- Command parser - interprets user commands
- Menu stack - breadcrumb trail for back navigation
- Input validator - ensures commands are valid

**Commands:**
```
list / ls        - Show current menu
edit <n>         - Edit setting number n
goto <menu>      - Navigate to menu
back / b         - Return to previous menu
help / h / ?     - Show commands
status / s       - Show progress
quit / q         - Exit game
```

**Implementation Notes:**
- Use `input()` for command reading
- Support both full names and shortcuts
- Fuzzy matching for menu names (optional)
- Command history (simple list)

**Config:**
- `config/ui.ini` - command aliases, help text

**Testing:**
- Command parsing
- Invalid command handling
- Navigation validation
- Back stack management

**Procedural:** None (navigation logic)

---

### 4.5 Progress Bar System
**Goal:** Display misleading progress indicators

**Files:**
- `ui/progress_bars.py`
- `tests/test_progress_bars.py`

**Key Components:**
- `ProgressBar` base class
- `ReliableProgressBar` - works normally
- `UnreliableProgressBar` - moves backwards randomly
- `NestedProgressBar` - contains sub-bars
- `SpawningProgressBar` - creates child bars
- `StuckProgressBar` - freezes at specific percentage

**Behavior Types (from config):**
```ini
[progress_bar_types]
reliable = normal
unreliable = random_backtrack
nested = spawn_children
stuck = freeze_at_99
oscillating = back_and_forth
```

**Display Format:**
```
Loading Settings: [=========>      ] 67%
  Validating Audio: [=====>         ] 42%
  Checking Graphics: [===========>  ] 89%
```

**Implementation Notes:**
- Update bars based on time, not actual progress
- Some bars ignore actual game progress entirely
- Configurable update frequency
- Optional animations (simple character rotation)

**Config:**
- `config/progress_bars.ini` - bar types, behaviors, frequencies

**Testing:**
- Each bar type behavior
- Nested bar rendering
- Update timing
- Animation cycles

**Procedural:** ✓ Bar behaviors from config

---

### 4.6 Message Display System
**Goal:** Show errors, hints, and status messages

**Files:**
- `ui/messages.py`
- `tests/test_messages.py`

**Key Components:**
- `MessageDisplay` class - manages message queue
- Message types: ERROR, WARNING, INFO, HINT, SUCCESS
- Message formatting with color coding
- Message history buffer
- Dismissal system

**Display Format:**
```
[ERROR] Cannot enable audio - Graphics must be configured first
[HINT]  Try visiting the Graphics menu
[INFO]  Progress: 23.7% (approximately)
```

**Features:**
- Color-coded by type (red errors, yellow warnings, etc.)
- Auto-dismiss after timeout (configurable)
- Manual dismiss with any key
- Scroll through message history
- Word wrapping for long messages

**Config:**
- `config/messages.ini` - colors, timeouts, max history size

**Testing:**
- Message queuing
- Color formatting
- Auto-dismissal timing
- History management

**Procedural:** ✓ Message templates from config

---

### 4.7 State Indicator System
**Goal:** Visual feedback for setting states

**Files:**
- `ui/indicators.py`
- `tests/test_indicators.py`

**Key Components:**
- `StateIndicator` class - manages visual state changes
- Blinking animation for BLINKING state
- Color changes for different states
- Icons/symbols for states
- Animation frame management

**State Visuals (configurable):**
```ini
[state_visuals]
enabled = [X] green
disabled = [ ] red
locked = [~] yellow
hidden = 
blinking = [*] alternate_green_red
```

**Animation System:**
- Frame-based animation (not real-time)
- Update on each render cycle
- Configurable frame duration
- State-specific animations

**Implementation Notes:**
- Use ANSI color codes
- Simple frame counter for animations
- Don't use threads (keep it simple)

**Config:**
- `config/indicators.ini` - symbols, colors, animation speeds

**Testing:**
- State-to-visual mapping
- Animation frame progression
- Color code generation

**Procedural:** ✓ Visuals from config

---

### 4.8 Layout Manager
**Goal:** Organize UI components on screen

**Files:**
- `ui/layout.py`
- `tests/test_layout.py`

**Key Components:**
- `LayoutManager` class - positions components
- `Region` class - defines screen areas
- Simple grid-based layout (no complex flex/grid)
- Fixed regions: header, content, footer, sidebar

**Layout Structure:**
```
┌─────────────────────────────────────┐
│ HEADER (title, progress)           │
├──────────────┬──────────────────────┤
│ SIDEBAR      │ CONTENT              │
│ (navigation) │ (menu/settings)      │
│              │                      │
├──────────────┴──────────────────────┤
│ FOOTER (status, messages)           │
└─────────────────────────────────────┘
```

**Features:**
- Calculate component dimensions based on terminal size
- Handle terminal resize (re-render)
- Clip content to region boundaries
- Scrolling for overflow content

**Implementation Notes:**
- Use `os.get_terminal_size()` for dimensions
- Recalculate on each render (simple approach)
- No caching initially (YAGNI)

**Config:**
- `config/layout.ini` - region sizes, borders, padding

**Testing:**
- Region calculation
- Content clipping
- Resize handling

**Procedural:** None (layout logic)

---

### 4.9 Input Handler
**Goal:** Process keyboard input reliably

**Files:**
- `ui/input_handler.py`
- `tests/test_input_handler.py`

**Key Components:**
- `InputHandler` class - reads and processes input
- Command queue for async processing (optional, probably YAGNI)
- Input validation
- Special key handling (arrows, escape, etc.)

**Supported Input:**
- Text commands (most important)
- Single character shortcuts
- Arrow keys for navigation (nice-to-have)
- Escape to cancel operations

**Implementation Notes:**
- Start with simple `input()` - blocking is fine
- Can upgrade to non-blocking later if needed
- Don't over-engineer initially
- Platform differences: use `msvcrt` on Windows, `termios` on Unix (only if needed)

**For MVP:**
- Just use blocking `input()`
- Parse command strings
- Validate before executing
- Simple and reliable

**Testing:**
- Command parsing
- Input validation
- Special character handling (if implemented)

**Procedural:** None (input logic)

---

### 4.10 Main UI Loop
**Goal:** Orchestrate all UI components

**Files:**
- `ui/main_loop.py`
- `tests/test_main_loop.py`

**Key Components:**
- `UILoop` class - main game loop
- Render cycle management
- Input processing
- State synchronization
- Event handling

**Loop Structure:**
```python
while not quit:
    1. Process any pending state changes
    2. Update progress bars / animations
    3. Check victory conditions
    4. Render current screen
    5. Get user input
    6. Execute command
    7. Update game state
    8. Trigger propagation/evaluation
```

**Features:**
- Clean screen on each cycle (or partial updates)
- Error handling for all user actions
- Graceful exit on quit command
- Auto-save session data on exit

**Implementation Notes:**
- Single-threaded, simple loop
- No async/await complexity initially
- Handle exceptions within loop
- Provide clean shutdown

**Testing:**
- Loop lifecycle
- Command execution flow
- State updates
- Exit handling

**Procedural:** None (loop logic)

---

## Helper Scripts

### UI Tester
**File:** `scripts/test_ui.py`
```python
#!/usr/bin/env python3
# Interactive UI testing
# Generates sample game state
# Launches UI loop
# Allows manual testing of all components
```

### Layout Previewer
**File:** `scripts/preview_layout.py`
```python
#!/usr/bin/env python3
# Shows layout structure without game logic
# Displays placeholder content in each region
# Useful for testing terminal sizes
```

### Color Scheme Tester
**File:** `scripts/test_colors.py`
```python
#!/usr/bin/env python3
# Displays all ANSI color combinations
# Shows state indicators with different colors
# Verifies terminal color support
```

---

## Config Files Required

**config/ui.ini**
```ini
[display]
width = 80
padding = 2
border_style = double  # single, double, rounded

[colors]
enabled = green
disabled = red
locked = yellow
hidden = 
blinking = cyan

[layout]
header_height = 3
footer_height = 2
sidebar_width = 20
```

**config/progress_bars.ini**
```ini
[bar_defaults]
width = 40
update_interval = 0.5
character = =

[behavior_weights]
reliable = 0.3
unreliable = 0.4
stuck = 0.2
nested = 0.1
```

**config/messages.ini**
```ini
[timeouts]
error = 5.0
warning = 3.0
info = 2.0
hint = 4.0

[colors]
error = red
warning = yellow
info = white
hint = cyan
```

**config/indicators.ini**
```ini
[symbols]
enabled = [X]
disabled = [ ]
locked = [~]
blinking = [*]

[animation]
blink_speed = 0.5
frames = 2
```

**config/layout.ini**
```ini
[regions]
header = 0,0,80,3
sidebar = 0,3,20,20
content = 20,3,60,20
footer = 0,23,80,2

[scrolling]
content_scroll = true
lines_per_page = 15
```

---

## Libraries Summary

**Core:**
- os (terminal size)
- sys (stdout)
- time (animations)

**Optional/Platform-specific:**
- msvcrt (Windows non-blocking input) - only if non-blocking needed
- termios (Unix non-blocking input) - only if non-blocking needed
- colorama (Windows ANSI support) - might be needed for Windows

**Recommendation:** Start without colorama/termios/msvcrt. Use simple blocking input. Add complexity only if actually needed.

---

## Phase 4 Completion Criteria

- [ ] Text rendering with ANSI colors working
- [ ] Menu display shows all setting states correctly
- [ ] Setting editor allows value modification
- [ ] Navigation system handles all commands
- [ ] Progress bars display (with various behaviors)
- [ ] Message system queues and displays messages
- [ ] State indicators animate correctly
- [ ] Layout manager positions components
- [ ] Input handler processes commands reliably
- [ ] Main loop integrates all components
- [ ] All UI configurable via INI files
- [ ] Runs in standard terminals (Linux, Mac, Windows)
- [ ] 80%+ test coverage
- [ ] Helper scripts functional
- [ ] No external dependencies (except maybe colorama for Windows)

---

## Implementation Priority

1. **Start Simple:** Text renderer + basic menu display
2. **Add Interaction:** Input handler + navigation
3. **Enhance Display:** State indicators + progress bars
4. **Polish:** Messages + layout manager + animations
5. **Integration:** Main loop connecting everything

Keep it simple. Terminal-based text UI. No ncurses, no fancy TUI libraries. Just print statements and ANSI codes. The senior dev will appreciate not having to debug curses window management.
