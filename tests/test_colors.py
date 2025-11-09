#!/usr/bin/env python3

from src.ui.renderer import ANSIColor


def test_basic_colors():
    print("Basic Colors:")
    print("-" * 40)

    colors = {
        "Red": ANSIColor.RED,
        "Green": ANSIColor.GREEN,
        "Yellow": ANSIColor.YELLOW,
        "Blue": ANSIColor.BLUE,
        "Magenta": ANSIColor.MAGENTA,
        "Cyan": ANSIColor.CYAN,
        "White": ANSIColor.WHITE,
    }

    for name, code in colors.items():
        print(f"{code}{name:10}{ANSIColor.RESET} - Sample text in {name.lower()}")

    print()


def test_bold():
    print("Bold Text:")
    print("-" * 40)
    print(f"{ANSIColor.BOLD}This is bold text{ANSIColor.RESET}")
    print(
        f"{ANSIColor.BOLD}{ANSIColor.RED}Bold Red{ANSIColor.RESET} "
        f"{ANSIColor.BOLD}{ANSIColor.GREEN}Bold Green{ANSIColor.RESET}"
    )
    print()


def test_state_indicators():
    print("State Indicators:")
    print("-" * 40)

    states = [
        ("Enabled", "[X]", ANSIColor.GREEN),
        ("Disabled", "[ ]", ANSIColor.RED),
        ("Locked", "[~]", ANSIColor.YELLOW),
        ("Blinking", "[*]", ANSIColor.CYAN),
    ]

    for state_name, symbol, color in states:
        print(f"{color}{symbol}{ANSIColor.RESET} {state_name:10} - {state_name} state")

    print()


def test_backgrounds():
    print("Background Colors:")
    print("-" * 40)

    backgrounds = [
        ("Black BG", ANSIColor.BG_BLACK, ANSIColor.WHITE),
        ("Red BG", ANSIColor.BG_RED, ANSIColor.WHITE),
        ("Green BG", ANSIColor.BG_GREEN, ANSIColor.BLACK),
        ("Yellow BG", ANSIColor.BG_YELLOW, ANSIColor.BLACK),
        ("Blue BG", ANSIColor.BG_BLUE, ANSIColor.WHITE),
        ("Magenta BG", ANSIColor.BG_MAGENTA, ANSIColor.WHITE),
        ("Cyan BG", ANSIColor.BG_CYAN, ANSIColor.BLACK),
    ]

    for name, bg_color, fg_color in backgrounds:
        print(f"{bg_color}{fg_color} {name:12} {ANSIColor.RESET}")

    print()


def test_progress_bar():
    print("Progress Bar:")
    print("-" * 40)

    for percentage in [0, 25, 50, 75, 100]:
        width = 40
        filled = int(width * percentage / 100)
        bar = "=" * filled + " " * (width - filled)
        print(f"[{bar}] {percentage:3}%")

    print()


def main():
    print("Ready to Start - Color Scheme Tester")
    print("=" * 40)
    print()

    test_basic_colors()
    test_bold()
    test_state_indicators()
    test_backgrounds()
    test_progress_bar()

    print("Terminal color support test complete!")
    print()


if __name__ == "__main__":
    main()
