#!/usr/bin/env python3

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generation.pipeline import GenerationPipeline
from src.testing.balance_tuner import BalanceTuner
from src.testing.difficulty_analyzer import DifficultyAnalyzer
from src.testing.playtest_interface import PlaytestInterface
from src.testing.session_reviewer import SessionReviewer
from src.testing.solvability_checker import SolvabilityChecker


class PlaytestMenu:
    def __init__(self):
        self.pipeline = None
        self.running = True

    def clear_screen(self) -> None:
        os.system("clear" if os.name != "nt" else "cls")

    def print_header(self, title: str) -> None:
        width = 70
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)

    def show_welcome(self) -> None:
        self.clear_screen()
        self.print_header("READY TO START - PLAYTESTING TOOL")
        print("""
Welcome to the Ready to Start Playtesting Interface!

This tool helps you:
  • Generate and test games interactively
  • Track playtest sessions with detailed metrics
  • Analyze game difficulty and solvability
  • Review and compare multiple playtest sessions
  • Tune game balance with preset difficulty levels

Perfect for QA testers, game designers, and developers!

Type 'help' at any time for assistance.
        """)
        input("Press Enter to continue...")

    def show_main_menu(self) -> None:
        self.clear_screen()
        self.print_header("MAIN MENU")
        print("""
1. Generate & Playtest New Game
2. Analyze Existing Game (no playtest)
3. Review Past Sessions
4. Batch Test Multiple Games
5. Help & Documentation
6. Exit

        """)

    def generate_and_playtest(self) -> None:
        self.clear_screen()
        self.print_header("GENERATE & PLAYTEST")

        print("\nEnter seed (or press Enter for random): ", end="")
        seed_input = input().strip()
        seed = int(seed_input) if seed_input.isdigit() else None

        print("\nDifficulty preset (easy/medium/hard/very_hard) or Enter to skip: ", end="")
        preset = input().strip().lower()

        print("\nGenerating game...")
        try:
            if self.pipeline is None:
                self.pipeline = GenerationPipeline()

            game_state = self.pipeline.generate(seed=seed)

            if preset in ["easy", "medium", "hard", "very_hard"]:
                print(f"Applying {preset} difficulty preset...")
                tuner = BalanceTuner(game_state)
                tuner.apply_preset(preset)

            print("\nPre-game Analysis:")
            print("-" * 70)

            checker = SolvabilityChecker(game_state)
            checker.validate()
            print(f"\nSolvability: {len(checker.issues)} issues found")

            analyzer = DifficultyAnalyzer(game_state)
            score = analyzer.analyze()
            print(f"Difficulty: {score.overall}/100 ({score.rating.upper()})")

            print("\nReady to start playtesting!")
            print("You'll be able to manually play through the game.")
            input("\nPress Enter to begin...")

            interface = PlaytestInterface(game_state, seed=seed)
            interface.run_gameplay_loop()

            print("\nWould you like to see the full analysis? (y/n): ", end="")
            if input().strip().lower() == "y":
                interface.show_final_analysis()
                input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\nError: {e}")
            input("\nPress Enter to continue...")

    def analyze_game(self) -> None:
        self.clear_screen()
        self.print_header("ANALYZE GAME")

        print("\nEnter seed: ", end="")
        seed_input = input().strip()

        if not seed_input.isdigit():
            print("Invalid seed!")
            input("Press Enter to continue...")
            return

        seed = int(seed_input)

        print("\nGenerating game...")
        try:
            if self.pipeline is None:
                self.pipeline = GenerationPipeline()

            game_state = self.pipeline.generate(seed=seed)

            checker = SolvabilityChecker(game_state)
            checker.validate()

            analyzer = DifficultyAnalyzer(game_state)
            score = analyzer.analyze()

            self.clear_screen()
            self.print_header(f"ANALYSIS - Seed {seed}")

            print("\nSOLVABILITY:")
            print(checker.get_report())

            print("\n\nDIFFICULTY:")
            print(analyzer.get_report())

            print("\n\nWould you like to export this analysis? (y/n): ", end="")
            if input().strip().lower() == "y":
                filepath = f"analysis_reports/seed_{seed}.json"
                interface = PlaytestInterface(game_state, seed=seed)
                interface.export_analysis(filepath)

            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\nError: {e}")
            input("\nPress Enter to continue...")

    def review_sessions(self) -> None:
        self.clear_screen()
        self.print_header("REVIEW SESSIONS")

        sessions_files = SessionReviewer.list_sessions()

        if not sessions_files:
            print("\nNo saved sessions found!")
            print("Play some games first to generate session data.")
            input("\nPress Enter to continue...")
            return

        print(f"\nFound {len(sessions_files)} sessions:")
        print("-" * 70)

        for i, filepath in enumerate(sessions_files[:20], 1):
            print(f"{i}. {filepath.name}")

        print("\nOptions:")
        print("  [number] - View individual session")
        print("  all      - Compare all sessions")
        print("  back     - Return to main menu")

        choice = input("\n> ").strip().lower()

        if choice == "back":
            return
        elif choice == "all":
            self.compare_all_sessions(sessions_files)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sessions_files):
                self.view_session(sessions_files[idx])

    def view_session(self, filepath) -> None:
        self.clear_screen()
        self.print_header(f"SESSION: {filepath.name}")

        try:
            tracker = SessionReviewer.load_session(filepath)
            print(tracker.get_summary())
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"\nError loading session: {e}")
            input("\nPress Enter to continue...")

    def compare_all_sessions(self, sessions_files) -> None:
        self.clear_screen()
        self.print_header("SESSION COMPARISON")

        print("\nLoading sessions...")
        sessions = []

        for filepath in sessions_files:
            try:
                sessions.append(SessionReviewer.load_session(filepath))
            except Exception:
                continue

        if not sessions:
            print("Could not load any sessions!")
            input("\nPress Enter to continue...")
            return

        report = SessionReviewer.generate_comparison_report(sessions)
        print(report)

        print("\n\nWould you like to export this comparison? (y/n): ", end="")
        if input().strip().lower() == "y":
            filepath = "analysis_reports/session_comparison.json"
            SessionReviewer.export_comparison(sessions, filepath)
            print(f"Exported to: {filepath}")

        input("\nPress Enter to continue...")

    def batch_test(self) -> None:
        self.clear_screen()
        self.print_header("BATCH TEST")

        print("\nStarting seed: ", end="")
        start_seed = int(input().strip() or "1")

        print("Number of games: ", end="")
        count = int(input().strip() or "5")

        print("Difficulty preset (or Enter to skip): ", end="")
        preset = input().strip().lower()

        print(f"\nTesting {count} games starting from seed {start_seed}...")
        print("-" * 70)

        if self.pipeline is None:
            self.pipeline = GenerationPipeline()

        results = []

        for i in range(count):
            seed = start_seed + i
            try:
                game_state = self.pipeline.generate(seed=seed)

                if preset in ["easy", "medium", "hard", "very_hard"]:
                    tuner = BalanceTuner(game_state)
                    tuner.apply_preset(preset)

                checker = SolvabilityChecker(game_state)
                checker.validate()

                analyzer = DifficultyAnalyzer(game_state)
                score = analyzer.analyze()

                results.append({
                    "seed": seed,
                    "solvable": len(checker.issues) == 0,
                    "issues": len(checker.issues),
                    "difficulty": score.overall,
                    "rating": score.rating,
                })

                status = "✓" if len(checker.issues) == 0 else "✗"
                print(f"{status} Seed {seed}: {score.rating.upper()} ({score.overall}/100) - {len(checker.issues)} issues")

            except Exception as e:
                print(f"✗ Seed {seed}: Failed - {e}")

        if results:
            print("\n" + "=" * 70)
            print("BATCH TEST SUMMARY")
            print("=" * 70)

            solvable = sum(1 for r in results if r["solvable"])
            avg_difficulty = sum(r["difficulty"] for r in results) / len(results)

            print(f"\nSolvable: {solvable}/{len(results)} ({solvable/len(results)*100:.1f}%)")
            print(f"Average Difficulty: {avg_difficulty:.1f}/100")

            ratings = {}
            for r in results:
                ratings[r["rating"]] = ratings.get(r["rating"], 0) + 1

            print("\nDifficulty Distribution:")
            for rating, count in sorted(ratings.items()):
                print(f"  {rating.capitalize()}: {count}")

        input("\nPress Enter to continue...")

    def show_help(self) -> None:
        self.clear_screen()
        self.print_header("HELP & DOCUMENTATION")

        print("""
QUICK START GUIDE
-----------------

1. Generate & Playtest New Game
   - Creates a new game and lets you play it manually
   - Track your progress with live stats
   - Sessions are automatically saved

2. Analyze Existing Game
   - Check solvability and difficulty without playing
   - Good for quick validation of specific seeds

3. Review Past Sessions
   - View individual session details
   - Compare multiple sessions to find patterns
   - Export comparison data

4. Batch Test Multiple Games
   - Test many games quickly
   - Get aggregate statistics
   - Perfect for validating generation quality

DURING GAMEPLAY
---------------
  [number] - Toggle setting or navigate to menu
  l        - List all settings
  m        - Show available menus
  h        - Show hints for locked settings
  s        - Session statistics
  p        - Progress report
  save     - Save and continue
  exit     - Save and exit
  help     - Show help

TIPS FOR TESTERS
----------------
• Start with easy difficulty preset to learn the game
• Use 'h' command frequently to understand dependencies
• Watch for stuck detection (idle >60s)
• Save often to preserve your progress
• Review sessions to identify problematic areas

DOCUMENTATION
-------------
• Detailed manual: docs/testing/PLAYTESTING_MANUAL.md
• Quick reference: src/testing/README.md
• Examples: docs/testing/WORKFLOWS.md
        """)

        input("\nPress Enter to continue...")

    def run(self) -> None:
        self.show_welcome()

        while self.running:
            self.show_main_menu()
            choice = input("Select option (1-6): ").strip()

            if choice == "1":
                self.generate_and_playtest()
            elif choice == "2":
                self.analyze_game()
            elif choice == "3":
                self.review_sessions()
            elif choice == "4":
                self.batch_test()
            elif choice == "5":
                self.show_help()
            elif choice == "6":
                print("\nThank you for playtesting!")
                self.running = False
            else:
                print("\nInvalid option!")
                input("Press Enter to continue...")


def main():
    try:
        menu = PlaytestMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
