"""
DEPRECATED: The gameplay functionality of PlaytestInterface has been consolidated
into UILoop (src/ui/main_loop.py). Use UILoop with session_tracker parameter instead.

This module is kept for analysis-only features and backward compatibility.
For new code, use:
    - UILoop for all gameplay (with optional session tracking)
    - SolvabilityChecker/DifficultyAnalyzer for analysis directly
"""
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.enums import SettingState
from src.testing.difficulty_analyzer import DifficultyAnalyzer
from src.testing.gameplay_simulator import GameplaySimulator
from src.testing.playtest_session import PlaytestTracker
from src.testing.solvability_checker import SolvabilityChecker

if TYPE_CHECKING:
    from src.core.game_state import GameState


class PlaytestInterface:
    def __init__(self, game_state: "GameState", seed: int | None = None):
        self.game_state = game_state
        self.seed = seed
        self.tracker = PlaytestTracker(seed=seed)
        self.simulator = GameplaySimulator(game_state, self.tracker)
        self.show_live_stats = True

    def clear_screen(self) -> None:
        os.system("clear" if os.name != "nt" else "cls")

    def print_header(self, title: str) -> None:
        width = 70
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)

    def print_separator(self) -> None:
        print("-" * 70)

    def show_dashboard(self) -> None:
        if not self.show_live_stats:
            return

        progress = self.simulator.get_progress()
        metrics = self.tracker.metrics

        print()
        print("LIVE DASHBOARD")
        self.print_separator()

        print(f"Settings: {progress['settings_enabled']}/{progress['settings_total']} ({progress['settings_percent']:.1f}%)")
        print(f"Menus:    {progress['menus_visited']}/{progress['menus_total']} ({progress['menus_percent']:.1f}%)")
        print(f"Actions:  {metrics.total_interactions} ({metrics.failed_interactions} failed)")
        print(f"Duration: {metrics.duration:.1f}s")

        if metrics.stuck_events:
            print(f"Stuck:    {len(metrics.stuck_events)} times ({metrics.total_stuck_time:.1f}s total)")

        self.print_separator()

    def show_current_menu(self) -> None:
        menu = self.simulator.get_current_menu()
        if not menu:
            print("\nNo current menu!")
            return

        print(f"\nCurrent Menu: {menu.id}")
        print(f"Category: {menu.category}")
        print(f"Visited: {'Yes' if menu.visited else 'No'}")
        print()

    def show_settings(self) -> None:
        menu = self.simulator.get_current_menu()

        if not menu:
            return

        # Get ALL settings including locked ones
        visible_settings = [s for s in menu.settings if s.state != SettingState.HIDDEN]

        print("SETTINGS:")
        self.print_separator()

        if visible_settings:
            for i, setting in enumerate(visible_settings, 1):
                # State indicator
                if setting.state == SettingState.LOCKED:
                    marker = "[LOCK]"
                    status = "LOCKED"
                elif setting.state == SettingState.ENABLED:
                    marker = "[X]"
                    status = "ENABLED"
                else:
                    marker = "[ ]"
                    status = "DISABLED"

                # Type and value display
                type_abbrev = {
                    'bool': 'bool',
                    'int': 'int',
                    'float': 'float',
                    'string': 'str'
                }.get(setting.type.value, setting.type.value)

                value_str = str(setting.value)
                if len(value_str) > 30:
                    value_str = value_str[:27] + "..."

                print(f"{i}. {marker} {setting.label}: {value_str} ({type_abbrev}) [{status}]")
        else:
            print("No settings in this menu")

        self.print_separator()

    def show_available_menus(self) -> None:
        menus = self.simulator.get_available_menus()

        print("\nAVAILABLE MENUS:")
        self.print_separator()

        if menus:
            for i, menu in enumerate(menus, 1):
                visited = "✓" if menu.visited else " "
                print(f"{i}. [{visited}] {menu.id} ({menu.category})")
        else:
            print("No other menus accessible")

        self.print_separator()

    def show_help(self) -> None:
        self.clear_screen()
        self.print_header("HELP")

        help_text = """
COMMANDS:
  [number]       - Toggle boolean or edit int/float/string setting
  l              - List all settings in current menu
  m              - Show available menus
  h              - Show hints for locked settings
  s              - Show session statistics
  d              - Toggle live dashboard
  p              - Show progress report
  help           - Show this help
  save           - Save session and continue
  exit           - Exit and save session
  quit           - Exit without saving

NAVIGATION:
  - You start in a menu with settings
  - Boolean settings toggle ON/OFF, others prompt for value
  - Navigate to other menus when they become accessible
  - Some settings are LOCKED until you enable their dependencies
  - Click locked settings to see unlock requirements

GOAL:
  Enable all settings to win the game!

TIPS:
  - Use 'h' to see why settings are locked
  - Watch the live dashboard for progress
  - Check session stats with 's' to identify problems
  - Save often with 'save' command
  - Each setting shows its type (bool/int/float/str) and current value
        """
        print(help_text)
        input("\nPress Enter to continue...")

    def show_hints(self) -> None:
        menu = self.simulator.get_current_menu()
        if not menu:
            return

        locked = [s for s in menu.settings if s.state == SettingState.LOCKED]

        if not locked:
            print("\nNo locked settings in this menu!")
            return

        print("\nLOCKED SETTINGS HINTS:")
        self.print_separator()

        for setting in locked:
            hints = self.simulator.get_hints_for_setting(setting.id)
            print(f"\n{setting.label}:")
            if hints:
                for hint in hints:
                    print(f"  → {hint}")
            else:
                print("  → No dependencies (shouldn't be locked)")

        self.print_separator()

    def show_statistics(self) -> None:
        self.clear_screen()
        self.print_header("SESSION STATISTICS")
        print(self.tracker.get_summary())
        input("\nPress Enter to continue...")

    def show_progress_report(self) -> None:
        self.clear_screen()
        self.print_header("PROGRESS REPORT")

        progress = self.simulator.get_progress()

        print(f"\nSettings Progress:")
        print(f"  Enabled: {progress['settings_enabled']}/{progress['settings_total']}")
        print(f"  Progress: {progress['settings_percent']:.1f}%")

        bar_width = 50
        filled = int(bar_width * progress["settings_percent"] / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"  [{bar}]")

        print(f"\nMenu Exploration:")
        print(f"  Visited: {progress['menus_visited']}/{progress['menus_total']}")
        print(f"  Progress: {progress['menus_percent']:.1f}%")

        bar_filled = int(bar_width * progress["menus_percent"] / 100)
        bar = "█" * bar_filled + "░" * (bar_width - bar_filled)
        print(f"  [{bar}]")

        if self.simulator.is_victory():
            print("\n🎉 VICTORY! All settings enabled! 🎉")

        input("\nPress Enter to continue...")

    def save_session(self, filepath: str | None = None) -> None:
        if filepath is None:
            sessions_dir = Path("playtest_sessions")
            sessions_dir.mkdir(exist_ok=True)
            filepath = sessions_dir / f"session_{self.tracker.metrics.session_id}.json"

        self.tracker.complete_session(completed=self.simulator.is_victory())
        self.tracker.save(filepath)
        print(f"\nSession saved to: {filepath}")

    def run_gameplay_loop(self) -> None:
        self.simulator.start()

        while self.simulator.running:
            self.clear_screen()
            self.print_header(f"PLAYTESTING - Seed: {self.seed or 'Random'}")

            if self.show_live_stats:
                self.show_dashboard()

            self.show_current_menu()
            self.show_settings()

            if self.simulator.is_victory():
                print("\n🎉 CONGRATULATIONS! You've enabled all settings! 🎉")
                self.save_session()
                break

            self.tracker.check_stuck()

            print("\nCommands: [number] l m h s d p help save exit quit")
            command = input("\n> ").strip().lower()

            if not command:
                continue

            if command == "help":
                self.show_help()
            elif command == "l":
                self.clear_screen()
                self.print_header("ALL SETTINGS")
                self.show_settings()
                input("\nPress Enter to continue...")
            elif command == "m":
                self.clear_screen()
                self.print_header("AVAILABLE MENUS")
                self.show_available_menus()
                print("\nEnter menu number to navigate, or press Enter to go back")
                choice = input("> ").strip()
                if choice.isdigit():
                    menus = self.simulator.get_available_menus()
                    idx = int(choice) - 1
                    if 0 <= idx < len(menus):
                        self.simulator.navigate_to_menu(menus[idx].id)
            elif command == "h":
                self.show_hints()
                input("\nPress Enter to continue...")
            elif command == "s":
                self.show_statistics()
            elif command == "d":
                self.show_live_stats = not self.show_live_stats
                status = "enabled" if self.show_live_stats else "disabled"
                print(f"\nLive dashboard {status}")
                input("Press Enter to continue...")
            elif command == "p":
                self.show_progress_report()
            elif command == "save":
                self.save_session()
                input("Press Enter to continue...")
            elif command in ("exit", "quit"):
                if command == "exit":
                    self.save_session()
                print("\nExiting playtesting session...")
                break
            elif command.isdigit():
                idx = int(command) - 1
                menu = self.simulator.get_current_menu()
                if menu:
                    visible_settings = [s for s in menu.settings if s.state != SettingState.HIDDEN]
                    if 0 <= idx < len(visible_settings):
                        setting = visible_settings[idx]

                        # Check if locked and show hints
                        if setting.state == SettingState.LOCKED:
                            print(f"\n❌ '{setting.label}' is LOCKED!")
                            hints = self.simulator.get_hints_for_setting(setting.id)
                            if hints:
                                print("To unlock, you need to:")
                                for hint in hints:
                                    print(f"  → {hint}")
                            input("\nPress Enter to continue...")
                        else:
                            # For boolean, toggle; for others, prompt for new value
                            from src.core.enums import SettingType
                            if setting.type == SettingType.BOOLEAN:
                                self.simulator.toggle_setting(setting.id)
                            else:
                                self.simulator.edit_setting(setting.id)
                    else:
                        print("\n❌ Invalid setting number!")
                        input("Press Enter to continue...")

        self.simulator.stop()

    def run_analysis(self) -> dict:
        checker = SolvabilityChecker(self.game_state)
        checker.validate()

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        return {
            "solvability": {
                "is_solvable": len(checker.issues) == 0,
                "issues_count": len(checker.issues),
                "critical_issues": len(
                    [i for i in checker.issues if i.severity == "critical"]
                ),
                "report": checker.get_report(),
            },
            "difficulty": {
                "score": score.overall,
                "rating": score.rating,
                "report": analyzer.get_report(),
            },
            "session": self.tracker.get_summary() if self.tracker.metrics.end_time else None,
        }

    def show_final_analysis(self) -> None:
        self.clear_screen()
        self.print_header("PLAYTEST ANALYSIS")

        analysis = self.run_analysis()

        print("\nSOLVABILITY:")
        print(analysis["solvability"]["report"])

        print("\n\nDIFFICULTY:")
        print(analysis["difficulty"]["report"])

        if analysis["session"]:
            print("\n\nSESSION SUMMARY:")
            print(analysis["session"])

    def export_analysis(self, filepath: str) -> None:
        analysis = self.run_analysis()

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"\nAnalysis exported to: {filepath}")
