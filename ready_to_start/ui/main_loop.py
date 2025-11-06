import time

from ready_to_start.core.enums import SettingState
from ready_to_start.core.game_state import GameState
from ready_to_start.ui.input_handler import InputHandler
from ready_to_start.ui.menu_display import MenuDisplay
from ready_to_start.ui.messages import MessageDisplay, MessageType
from ready_to_start.ui.navigation import NavigationController
from ready_to_start.ui.progress_bars import ProgressBarFactory
from ready_to_start.ui.renderer import TextRenderer
from ready_to_start.ui.setting_editor import SettingEditor


class UILoop:
    def __init__(self, game_state: GameState, config_dir: str):
        self.game_state = game_state
        self.config_dir = config_dir
        self.running = False

        self.renderer = TextRenderer()
        self.input_handler = InputHandler()
        self.navigation = NavigationController(game_state)
        self.message_display = MessageDisplay(f"{config_dir}/messages.ini")
        self.setting_editor = SettingEditor()

        self.progress_bars = []
        self.last_frame_time = time.time()

    def start(self, start_menu_id: str):
        success, error = self.navigation.navigate_to(start_menu_id)
        if not success:
            print(f"Failed to start: {error}")
            return

        self.running = True
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

    def _render(self):
        self.renderer.clear_screen()

        if self.navigation.current_menu:
            from ready_to_start.ui.indicators import StateIndicator

            indicator = StateIndicator(f"{self.config_dir}/indicators.ini")
            menu_display = MenuDisplay(
                self.navigation.current_menu,
                self.renderer,
                indicator,
                f"{self.config_dir}/ui.ini",
            )
            print(menu_display.render())

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

    def _process_input(self):
        command = self.input_handler.read_command()
        if not command:
            return

        self.navigation.add_command_to_history(f"{command.action} {' '.join(command.args)}")

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

    def _handle_list(self):
        pass

    def _handle_edit(self, command):
        if not self.navigation.current_menu:
            self.message_display.add_message("No menu selected", MessageType.ERROR)
            return

        try:
            setting_index = int(command.get_arg(0)) - 1
        except (ValueError, TypeError):
            self.message_display.add_message("Invalid setting number", MessageType.ERROR)
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

        if setting.state == SettingState.LOCKED:
            self.message_display.add_message(
                f"Setting '{setting.label}' is locked", MessageType.WARNING
            )
            return

        result = self.setting_editor.edit_setting(setting)

        if result.success:
            setting.value = result.value
            setting.visit_count += 1
            setting.last_modified = time.time()
            self.game_state.propagate_changes()
            self.message_display.add_message(
                f"Updated {setting.label} to {result.value}", MessageType.SUCCESS
            )
        else:
            self.message_display.add_message(result.error, MessageType.ERROR)

    def _handle_goto(self, command):
        menu_name = command.get_arg(0)
        if not menu_name:
            self.message_display.add_message("Menu name required", MessageType.ERROR)
            return

        menu = self.navigation.find_menu_by_name(menu_name)
        if not menu:
            self.message_display.add_message(f"Menu not found: {menu_name}", MessageType.ERROR)
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
Available commands:
  list / ls        - Show current menu
  edit <n>         - Edit setting number n
  goto <menu>      - Navigate to menu
  back / b         - Return to previous menu
  help / h / ?     - Show this help
  status / s       - Show progress
  history          - Show command history
  quit / q         - Exit game
"""
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

        progress = (enabled_settings / total_settings * 100) if total_settings > 0 else 0

        status_text = f"""
Game Status:
  Menus visited: {visited_menus}/{total_menus}
  Settings enabled: {enabled_settings}/{total_settings}
  Progress: {progress:.1f}%
"""
        print(status_text)
        input("Press Enter to continue...")

    def _handle_history(self):
        history = self.navigation.get_command_history()
        if not history:
            self.message_display.add_message("No command history", MessageType.INFO)
            return

        print("\nCommand History:")
        for i, cmd in enumerate(history, 1):
            print(f"  {i}. {cmd}")
        input("Press Enter to continue...")

    def _handle_quit(self):
        print("\nAre you sure you want to quit? (y/n): ", end="")
        response = input().strip().lower()
        if response in ["y", "yes"]:
            self.stop()
