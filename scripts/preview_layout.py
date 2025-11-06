#!/usr/bin/env python3

import os
from configparser import ConfigParser


def preview_layout():
    print("\033[2J\033[H")

    width = 80
    height = 25

    header_lines = ["╔" + "═" * (width - 2) + "╗"]
    header_lines.append("║" + " READY TO START - Layout Preview ".center(width - 2) + "║")
    header_lines.append("╠" + "═" * (width - 2) + "╣")

    for line in header_lines:
        print(line)

    sidebar_width = 20
    content_width = width - sidebar_width - 2

    content_height = height - len(header_lines) - 3

    for i in range(content_height):
        if i == 0:
            sidebar_text = "SIDEBAR"
            content_text = "CONTENT AREA"
        elif i < 5:
            sidebar_text = f"Menu {i}"
            content_text = f"Content line {i}"
        else:
            sidebar_text = ""
            content_text = ""

        sidebar_part = sidebar_text.ljust(sidebar_width - 1)
        content_part = content_text.ljust(content_width - 1)

        print("║" + sidebar_part + "│" + content_part + "║")

    footer_line = "╠" + "═" * (width - 2) + "╣"
    print(footer_line)
    print("║" + " Status: Ready | Commands: help ".ljust(width - 2) + "║")
    print("╚" + "═" * (width - 2) + "╝")


def main():
    print("Ready to Start - Layout Previewer")
    print("=" * 40)
    print()

    try:
        term_size = os.get_terminal_size()
        print(f"Terminal size: {term_size.columns}x{term_size.lines}")
    except OSError:
        print("Could not detect terminal size, using default 80x24")

    print()
    input("Press Enter to preview layout...")
    print()

    preview_layout()

    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
