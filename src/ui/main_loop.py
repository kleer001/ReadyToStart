import time
from pathlib import Path

from src.anti_patterns.engine import AntiPatternEngine
from src.core.enums import SettingState
from src.core.game_state import GameState
from src.ui.input_handler import InputHandler
from src.ui.keyboard import Key, KeyboardReader
from src.ui.menu_display import MenuDisplay
from src.ui.messages import MessageDisplay, MessageType
from src.ui.navigation import NavigationController
from src.ui.renderer import TextRenderer
from src.ui.setting_editor import SettingEditor


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
        self.keyboard = KeyboardReader()
        self.navigation = NavigationController(game_state)
        self.message_display = MessageDisplay(f"{config_dir}/messages.ini")
        self.setting_editor = SettingEditor()
        self.setting_editor.set_keyboard(self.keyboard)

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

    def start(self, start_menu_id: str):
        success, error = self.navigation.navigate_to(start_menu_id)
        if not success:
            print(f"Failed to start: {error}")
            return

        # Track initial menu visit if tracking enabled
        if self.session_tracker:
            self.session_tracker.record_menu_visit(start_menu_id)

        self.running = True
        self.keyboard.enable_raw_mode()
        try:
            self.run()
        finally:
            self.keyboard.disable_raw_mode()
            # Complete session tracking if enabled
            if self.session_tracker:
                is_complete = self._check_victory()
                self.session_tracker.complete_session(completed=is_complete)

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

        # Show live stats header if enabled
        if self.show_live_stats and self.session_tracker:
            self._render_live_stats()

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
            print(menu_display.render(selected))

        messages = self.message_display.get_current_messages()
        if messages:
            print()
            for msg in messages:
                print(msg)

        if self.progress_bars:
            print()
            for bar in self.progress_bars:
                for line in bar.render():
                    print(line)

        print()
        if self.navigation_mode:
            nav_hint = "Nav: ↑↓/ws/jk=move ←→/ad=menu Enter=select :=cmd h=help"
            if self.session_tracker:
                nav_hint += " t=stats"
            nav_hint += " q=quit"
            print(nav_hint)
        else:
            print("Command mode (ESC to return to navigation) > ", end="")

    def _process_input(self):
        if self.navigation_mode:
            self._process_navigation_input()
        else:
            self._process_command_input()

    def _process_navigation_input(self):
        key = self.keyboard.read_key()
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
        elif key.lower() == "q":
            self._handle_quit()
        elif key.lower() == "h":
            self._handle_help()
        elif key.lower() == "t" and self.session_tracker:
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

        result = self.setting_editor.edit_setting(setting)

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
            key = self.keyboard.read_key()
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

        result = self.setting_editor.edit_setting(setting)

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
        with self.keyboard.normal_mode():
            print(help_text)
            input("Press Enter to continue...")

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
        with self.keyboard.normal_mode():
            print(status_text)
            input("Press Enter to continue...")

    def _handle_history(self):
        history = self.navigation.get_command_history()
        if not history:
            self.message_display.add_message("No command history", MessageType.INFO)
            return

        with self.keyboard.normal_mode():
            print("\nCommand History:")
            for i, cmd in enumerate(history, 1):
                print(f"  {i}. {cmd}")
            input("Press Enter to continue...")

    def _handle_quit(self):
        with self.keyboard.normal_mode():
            print("\nAre you sure you want to quit? (y/n): ", end="")
            response = input().strip().lower()
            if response in ["y", "yes"]:
                self.stop()

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
            "🎉 VICTORY! All settings enabled! 🎉",
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

    def _render_live_stats(self):
        """Render live session statistics at the top of the screen."""
        if not self.session_tracker:
            return

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

        print("=" * 70)
        print(f" PLAYTEST - Seed: {self.seed or 'Random'} | Session: {metrics.session_id[:8]}")
        print("-" * 70)
        print(f" Settings: {enabled_settings}/{total_settings} ({progress_pct:.1f}%) | Menus: {visited_menus}/{total_menus}")
        print(f" Actions: {metrics.total_interactions} | Duration: {duration:.1f}s")
        print("=" * 70)
        print()

    def _handle_show_session_stats(self):
        """Show detailed session statistics."""
        if not self.session_tracker:
            return

        with self.keyboard.normal_mode():
            self.renderer.clear_screen()
            print("=" * 70)
            print("SESSION STATISTICS".center(70))
            print("=" * 70)
            print(self.session_tracker.get_summary())
            input("\nPress Enter to continue...")
