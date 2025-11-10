import curses
import time
from pathlib import Path

from src.anti_patterns.engine import AntiPatternEngine
from src.core.enums import SettingState
from src.core.game_state import GameState
from src.ui.input_handler import InputHandler
from src.ui.menu_display import MenuDisplay
from src.ui.messages import MessageDisplay, MessageType
from src.ui.navigation import NavigationController
from src.ui.renderer import TextRenderer
from src.ui.setting_editor import SettingEditor


# Key mappings
class Key:
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ENTER = "ENTER"
    ESC = "ESC"
    BACKSPACE = "BACKSPACE"


class UILoop:
    def __init__(
        self,
        game_state: GameState,
        config_dir: str,
        session_tracker=None,
        show_live_stats: bool = False,
        seed: int | None = None,
    ):
        self.game_state = game_state
        self.config_dir = config_dir
        self.running = False
        self.seed = seed

        # Optional playtest tracking
        self.session_tracker = session_tracker
        self.show_live_stats = show_live_stats

        self.renderer = TextRenderer()
        self.input_handler = InputHandler()
        self.navigation = NavigationController(game_state)
        self.message_display = MessageDisplay(f"{config_dir}/messages.ini")
        self.setting_editor = SettingEditor()

        self.progress_bars = []
        self.last_frame_time = time.time()
        self.selected_index = 0
        self.navigation_mode = True

        self.ui_state = {}
        self.anti_pattern_engine = AntiPatternEngine(
            game_state, self.ui_state, seed=None
        )

        anti_pattern_config = Path(config_dir) / "anti_patterns.ini"
        if anti_pattern_config.exists():
            self.anti_pattern_engine.load_from_config(str(anti_pattern_config))

        fake_message_config = Path(config_dir) / "fake_messages.ini"
        if fake_message_config.exists():
            self.anti_pattern_engine.message_generator.load_from_config(
                str(fake_message_config)
            )

        self.stdscr = None

    def start(self, start_menu_id: str):
        success, error = self.navigation.navigate_to(start_menu_id)
        if not success:
            print(f"Failed to start: {error}")
            return

        # Track initial menu visit if tracking enabled
        if self.session_tracker:
            self.session_tracker.record_menu_visit(start_menu_id)

        self.running = True
        try:
            curses.wrapper(self._curses_main)
        finally:
            # Complete session tracking if enabled
            if self.session_tracker:
                is_complete = self._check_victory()
                self.session_tracker.complete_session(completed=is_complete)

    def _curses_main(self, stdscr):
        """Main curses loop."""
        self.stdscr = stdscr
        self.renderer.set_screen(stdscr)

        # Configure curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(50)  # 50ms timeout for getch()

        self.run()

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                self._update()
                self._render()
                self._process_input()
            except KeyboardInterrupt:
                self._handle_quit()
            except Exception as e:
                self.message_display.add_message(f"Error: {str(e)}", MessageType.ERROR)

    def _update(self):
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        self.message_display.update()

        for bar in self.progress_bars:
            bar.update(delta_time)

        if self.navigation.current_menu:
            self.navigation.current_menu.completion_state = (
                self.navigation.current_menu.calculate_completion()
            )

        self.anti_pattern_engine.increment_counter("ui_renders")
        self.anti_pattern_engine.update()

        if "fake_messages" in self.ui_state:
            for msg in self.ui_state.pop("fake_messages", []):
                self.message_display.add_message(msg["text"], MessageType.ERROR)

        # Check for stuck state if tracking
        if self.session_tracker:
            if self.session_tracker.check_stuck():
                self.message_display.add_message(
                    "Warning: No progress for 60s - consider checking hints (h)",
                    MessageType.WARNING
                )

        # Check for victory
        if self._check_victory():
            self._handle_victory()

    def _render(self):
        self.renderer.clear_screen()

        current_y = 0

        # Show live stats header if enabled
        if self.show_live_stats and self.session_tracker:
            current_y = self._render_live_stats(current_y)
            current_y += 1

        if self.navigation.current_menu:
            from src.ui.indicators import StateIndicator

            indicator = StateIndicator(f"{self.config_dir}/indicators.ini")
            menu_display = MenuDisplay(
                self.navigation.current_menu,
                self.renderer,
                indicator,
                f"{self.config_dir}/ui.ini",
            )

            selected = self.selected_index if self.navigation_mode else -1
            lines_rendered = menu_display.render(
                window=self.stdscr,
                selected_index=selected,
                start_y=current_y,
                start_x=0
            )
            current_y += lines_rendered

        # Render messages
        messages = self.message_display.get_current_messages()
        if messages:
            current_y += 1
            for msg in messages:
                self.renderer.addstr(current_y, 0, msg)
                current_y += 1

        # Render progress bars
        if self.progress_bars:
            current_y += 1
            for bar in self.progress_bars:
                for line in bar.render():
                    self.renderer.addstr(current_y, 0, line)
                    current_y += 1

        # Render navigation hints
        current_y += 1
        if self.navigation_mode:
            nav_hint = "Nav: ↑↓/ws/jk=move ←→/ad=menu Enter=select :=cmd h=help"
            if self.session_tracker:
                nav_hint += " t=stats"
            nav_hint += " q=quit"
            self.renderer.addstr(current_y, 0, nav_hint)
        else:
            self.renderer.addstr(current_y, 0, "Command mode (ESC to return to navigation) > ")

        self.renderer.refresh()

    def _render_live_stats(self, start_y: int) -> int:
        """Render live session statistics at the top of the screen. Returns next y position."""
        if not self.session_tracker:
            return start_y

        total_settings = sum(len(m.settings) for m in self.game_state.menus.values())
        enabled_settings = sum(
            sum(1 for s in m.settings if s.state == SettingState.ENABLED)
            for m in self.game_state.menus.values()
        )
        progress_pct = (enabled_settings / total_settings * 100) if total_settings > 0 else 0

        total_menus = len(self.game_state.menus)
        visited_menus = sum(1 for m in self.game_state.menus.values() if m.visited)

        metrics = self.session_tracker.metrics
        duration = time.time() - metrics.start_time

        y = start_y
        self.renderer.addstr(y, 0, "=" * 70)
        y += 1
        self.renderer.addstr(y, 0, f" PLAYTEST - Seed: {self.seed or 'Random'} | Session: {metrics.session_id[:8]}")
        y += 1
        self.renderer.addstr(y, 0, "-" * 70)
        y += 1
        self.renderer.addstr(y, 0, f" Settings: {enabled_settings}/{total_settings} ({progress_pct:.1f}%) | Menus: {visited_menus}/{total_menus}")
        y += 1
        self.renderer.addstr(y, 0, f" Actions: {metrics.total_interactions} | Duration: {duration:.1f}s")
        y += 1
        self.renderer.addstr(y, 0, "=" * 70)
        y += 1

        return y

    def _process_input(self):
        if self.navigation_mode:
            self._process_navigation_input()
        else:
            self._process_command_input()

    def _read_key(self) -> str | None:
        """Read a key from ncurses and convert to our key constants."""
        if not self.stdscr:
            return None

        try:
            ch = self.stdscr.getch()
            if ch == -1:  # No input
                return None

            # Handle special keys
            if ch == curses.KEY_UP:
                return Key.UP
            elif ch == curses.KEY_DOWN:
                return Key.DOWN
            elif ch == curses.KEY_LEFT:
                return Key.LEFT
            elif ch == curses.KEY_RIGHT:
                return Key.RIGHT
            elif ch == ord('\n') or ch == ord('\r'):
                return Key.ENTER
            elif ch == 27:  # ESC
                return Key.ESC
            elif ch == curses.KEY_BACKSPACE or ch == 127 or ch == 8:
                return Key.BACKSPACE
            # WASD/HJKL navigation
            elif ch in [ord('w'), ord('W'), ord('k'), ord('K')]:
                return Key.UP
            elif ch in [ord('s'), ord('S'), ord('j'), ord('J')]:
                return Key.DOWN
            elif ch in [ord('a'), ord('A'), ord('h'), ord('H')]:
                return Key.LEFT
            elif ch in [ord('d'), ord('D'), ord('l'), ord('L')]:
                return Key.RIGHT
            else:
                # Return the character
                return chr(ch) if 0 <= ch < 256 else None
        except Exception:
            return None

    def _process_navigation_input(self):
        key = self._read_key()
        if not key:
            return

        if key == Key.UP:
            self._move_selection(-1)
        elif key == Key.DOWN:
            self._move_selection(1)
        elif key == Key.LEFT:
            self._handle_back()
            self.selected_index = 0
        elif key == Key.RIGHT:
            self._navigate_to_first_connection()
        elif key == Key.ENTER:
            self.anti_pattern_engine.increment_counter("clicks")
            self._select_current()
        elif key == ":":
            self.navigation_mode = False
        elif key and key.lower() == "q":
            self._handle_quit()
        elif key and key.lower() == "h" and key != Key.LEFT:
            self._handle_help()
        elif key and key.lower() == "t" and self.session_tracker:
            self._handle_show_session_stats()

    def _navigate_to_first_connection(self):
        if (
            not self.navigation.current_menu
            or not self.navigation.current_menu.connections
        ):
            return

        first_connection = self.navigation.current_menu.connections[0]
        success, error = self.navigation.navigate_to(first_connection)

        if success:
            self.selected_index = 0
            self.anti_pattern_engine.increment_counter("menu_visits")

            # Track menu visit if tracking enabled
            if self.session_tracker:
                self.session_tracker.record_menu_visit(first_connection)

            self.message_display.add_message(
                f"Navigated to {self.navigation.current_menu.category}",
                MessageType.SUCCESS,
            )
        else:
            self.message_display.add_message(error, MessageType.ERROR)
            if self.session_tracker:
                self.session_tracker.record_error(error)

    def _move_selection(self, direction: int):
        if not self.navigation.current_menu:
            return

        visible_settings = [
            s
            for s in self.navigation.current_menu.settings
            if s.state != SettingState.HIDDEN
        ]

        if not visible_settings:
            return

        self.selected_index = (self.selected_index + direction) % len(visible_settings)

    def _select_current(self):
        if not self.navigation.current_menu:
            return

        visible_settings = [
            s
            for s in self.navigation.current_menu.settings
            if s.state != SettingState.HIDDEN
        ]

        if not visible_settings or self.selected_index >= len(visible_settings):
            return

        setting = visible_settings[self.selected_index]

        # Check dependencies for LOCKED settings - show hints about what's needed
        if setting.state == SettingState.LOCKED:
            if not self.game_state.resolver.can_enable(setting.id, self.game_state):
                hints = self.game_state.get_dependency_hints(setting.id)
                if hints:
                    self.message_display.add_message(
                        f"'{setting.label}' is locked. To unlock:", MessageType.WARNING
                    )
                    for hint in hints:
                        self.message_display.add_message(
                            f"  • {hint}", MessageType.WARNING
                        )
                else:
                    self.message_display.add_message(
                        f"'{setting.label}' is locked - dependencies not met",
                        MessageType.WARNING,
                    )
            else:
                # Dependencies met but still locked
                # (shouldn't happen with propagate_changes)
                self.message_display.add_message(
                    f"'{setting.label}' is locked", MessageType.WARNING
                )
            return

        # Check dependencies for DISABLED settings
        if (
            setting.state == SettingState.DISABLED
            and not self.game_state.resolver.can_enable(setting.id, self.game_state)
        ):
            hints = self.game_state.get_dependency_hints(setting.id)
            if hints:
                self.message_display.add_message(
                    f"Cannot configure '{setting.label}':", MessageType.WARNING
                )
                for hint in hints:
                    self.message_display.add_message(f"  • {hint}", MessageType.WARNING)
            else:
                self.message_display.add_message(
                    f"Cannot configure '{setting.label}' - dependencies not met",
                    MessageType.WARNING,
                )
            return

        result = self.setting_editor.edit_setting(setting, self.stdscr)

        if result.success:
            setting.value = result.value
            setting.visit_count += 1
            setting.last_modified = time.time()

            # Transition to ENABLED state if currently DISABLED
            # (marking as "configured")
            if setting.state == SettingState.DISABLED:
                setting.state = SettingState.ENABLED
                self.anti_pattern_engine.increment_counter("settings_enabled")

            self.game_state.propagate_changes()

            # Track setting interaction if tracking enabled
            if self.session_tracker:
                self.session_tracker.record_setting_interaction(
                    setting.id, "edit", result.value, True
                )

            self.message_display.add_message(
                f"Updated {setting.label} to {result.value}", MessageType.SUCCESS
            )
        else:
            if self.session_tracker:
                self.session_tracker.record_setting_interaction(
                    setting.id, "edit", None, False
                )
            self.message_display.add_message(result.error, MessageType.ERROR)

    def _process_command_input(self):
        command = self.input_handler.read_command()
        if not command:
            key = self._read_key()
            if key == Key.ESC:
                self.navigation_mode = True
            return

        self.navigation.add_command_to_history(
            f"{command.action} {' '.join(command.args)}"
        )

        if command.action == "list":
            self._handle_list()
        elif command.action == "edit":
            self._handle_edit(command)
        elif command.action == "goto":
            self._handle_goto(command)
        elif command.action == "back":
            self._handle_back()
        elif command.action == "help":
            self._handle_help()
        elif command.action == "status":
            self._handle_status()
        elif command.action == "quit":
            self._handle_quit()
        elif command.action == "history":
            self._handle_history()

        self.navigation_mode = True

    def _handle_list(self):
        pass

    def _handle_edit(self, command):
        if not self.navigation.current_menu:
            self.message_display.add_message("No menu selected", MessageType.ERROR)
            return

        try:
            setting_index = int(command.get_arg(0)) - 1
        except (ValueError, TypeError):
            self.message_display.add_message(
                "Invalid setting number", MessageType.ERROR
            )
            return

        visible_settings = [
            s
            for s in self.navigation.current_menu.settings
            if s.state != SettingState.HIDDEN
        ]

        if setting_index < 0 or setting_index >= len(visible_settings):
            self.message_display.add_message("Setting not found", MessageType.ERROR)
            return

        setting = visible_settings[setting_index]

        # Check dependencies for LOCKED settings - show hints about what's needed
        if setting.state == SettingState.LOCKED:
            if not self.game_state.resolver.can_enable(setting.id, self.game_state):
                hints = self.game_state.get_dependency_hints(setting.id)
                if hints:
                    self.message_display.add_message(
                        f"'{setting.label}' is locked. To unlock:", MessageType.WARNING
                    )
                    for hint in hints:
                        self.message_display.add_message(
                            f"  • {hint}", MessageType.WARNING
                        )
                else:
                    self.message_display.add_message(
                        f"'{setting.label}' is locked - dependencies not met",
                        MessageType.WARNING,
                    )
            else:
                # Dependencies met but still locked
                # (shouldn't happen with propagate_changes)
                self.message_display.add_message(
                    f"'{setting.label}' is locked", MessageType.WARNING
                )
            return

        # Check dependencies for DISABLED settings
        if (
            setting.state == SettingState.DISABLED
            and not self.game_state.resolver.can_enable(setting.id, self.game_state)
        ):
            hints = self.game_state.get_dependency_hints(setting.id)
            if hints:
                self.message_display.add_message(
                    f"Cannot configure '{setting.label}':", MessageType.WARNING
                )
                for hint in hints:
                    self.message_display.add_message(f"  • {hint}", MessageType.WARNING)
            else:
                self.message_display.add_message(
                    f"Cannot configure '{setting.label}' - dependencies not met",
                    MessageType.WARNING,
                )
            return

        result = self.setting_editor.edit_setting(setting, self.stdscr)

        if result.success:
            setting.value = result.value
            setting.visit_count += 1
            setting.last_modified = time.time()

            # Transition to ENABLED state if currently DISABLED
            # (marking as "configured")
            if setting.state == SettingState.DISABLED:
                setting.state = SettingState.ENABLED
                self.anti_pattern_engine.increment_counter("settings_enabled")

            self.game_state.propagate_changes()

            # Track setting interaction if tracking enabled
            if self.session_tracker:
                self.session_tracker.record_setting_interaction(
                    setting.id, "edit", result.value, True
                )

            self.message_display.add_message(
                f"Updated {setting.label} to {result.value}", MessageType.SUCCESS
            )
        else:
            if self.session_tracker:
                self.session_tracker.record_setting_interaction(
                    setting.id, "edit", None, False
                )
            self.message_display.add_message(result.error, MessageType.ERROR)

    def _handle_goto(self, command):
        menu_name = command.get_arg(0)
        if not menu_name:
            self.message_display.add_message("Menu name required", MessageType.ERROR)
            return

        menu = self.navigation.find_menu_by_name(menu_name)
        if not menu:
            self.message_display.add_message(
                f"Menu not found: {menu_name}", MessageType.ERROR
            )
            return

        success, error = self.navigation.navigate_to(menu.id)
        if not success:
            self.message_display.add_message(error, MessageType.ERROR)
        else:
            self.message_display.add_message(
                f"Navigated to {menu.category}", MessageType.SUCCESS
            )

    def _handle_back(self):
        success, error = self.navigation.go_back()
        if not success:
            self.message_display.add_message(error, MessageType.WARNING)

    def _handle_help(self):
        help_text = """
Navigation Mode:
  ↑/w/k            - Move selection up
  ↓/s/j            - Move selection down
  ←/a              - Go back to previous menu
  →/d              - Navigate to first connected menu
  Enter            - Select/edit current setting
  :                - Enter command mode
  h                - Show this help
  q                - Quit game

Command Mode:
  list / ls        - Show current menu
  edit <n>         - Edit setting number n
  goto <menu>      - Navigate to menu
  back / b         - Return to previous menu
  status / s       - Show progress
  history          - Show command history
  quit / q         - Exit game
  ESC              - Return to navigation mode
"""
        self._show_modal(help_text)

    def _handle_status(self):
        total_menus = len(self.game_state.menus)
        visited_menus = sum(1 for m in self.game_state.menus.values() if m.visited)

        total_settings = sum(len(m.settings) for m in self.game_state.menus.values())
        enabled_settings = sum(
            sum(1 for s in m.settings if s.state == SettingState.ENABLED)
            for m in self.game_state.menus.values()
        )

        progress = (
            (enabled_settings / total_settings * 100) if total_settings > 0 else 0
        )

        status_text = f"""
Game Status:
  Menus visited: {visited_menus}/{total_menus}
  Settings enabled: {enabled_settings}/{total_settings}
  Progress: {progress:.1f}%
"""
        self._show_modal(status_text)

    def _handle_history(self):
        history = self.navigation.get_command_history()
        if not history:
            self.message_display.add_message("No command history", MessageType.INFO)
            return

        history_text = "\nCommand History:\n"
        for i, cmd in enumerate(history, 1):
            history_text += f"  {i}. {cmd}\n"

        self._show_modal(history_text)

    def _show_modal(self, text: str):
        """Show a modal dialog with text. Press any key to close."""
        if not self.stdscr:
            return

        # Save current screen state
        curses.curs_set(1)  # Show cursor
        self.stdscr.nodelay(False)  # Blocking input

        # Clear and show text
        self.stdscr.erase()
        self.stdscr.addstr(0, 0, text)
        self.stdscr.addstr("\nPress Enter to continue...")
        self.stdscr.refresh()

        # Wait for input
        while True:
            ch = self.stdscr.getch()
            if ch == ord('\n') or ch == ord('\r'):
                break

        # Restore screen state
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(True)  # Non-blocking input

    def _handle_quit(self):
        if not self.stdscr:
            self.stop()
            return

        # Show quit confirmation
        curses.curs_set(1)
        self.stdscr.nodelay(False)

        self.stdscr.erase()
        self.stdscr.addstr(0, 0, "\nAre you sure you want to quit? (y/n): ")
        self.stdscr.refresh()

        while True:
            ch = self.stdscr.getch()
            if ch in [ord('y'), ord('Y')]:
                self.stop()
                break
            elif ch in [ord('n'), ord('N')]:
                break

        curses.curs_set(0)
        self.stdscr.nodelay(True)

    def _check_victory(self) -> bool:
        """Check if all settings are enabled."""
        total_settings = sum(len(m.settings) for m in self.game_state.menus.values())
        enabled_settings = sum(
            sum(1 for s in m.settings if s.state == SettingState.ENABLED)
            for m in self.game_state.menus.values()
        )
        return enabled_settings == total_settings and total_settings > 0

    def _handle_victory(self):
        """Handle victory condition - called once when all settings are enabled."""
        if hasattr(self, '_victory_handled'):
            return  # Only handle once
        self._victory_handled = True

        self.message_display.add_message(
            "VICTORY! All settings enabled!",
            MessageType.SUCCESS
        )

        # Save session if tracking
        if self.session_tracker:
            from pathlib import Path
            sessions_dir = Path("playtest_sessions")
            sessions_dir.mkdir(exist_ok=True)
            filepath = sessions_dir / f"session_{self.session_tracker.metrics.session_id}.json"
            self.session_tracker.save(str(filepath))
            self.message_display.add_message(
                f"Session saved to {filepath}",
                MessageType.SUCCESS
            )

    def _handle_show_session_stats(self):
        """Show detailed session statistics."""
        if not self.session_tracker:
            return

        stats_text = "=" * 70 + "\n"
        stats_text += "SESSION STATISTICS".center(70) + "\n"
        stats_text += "=" * 70 + "\n"
        stats_text += self.session_tracker.get_summary()

        self._show_modal(stats_text)
