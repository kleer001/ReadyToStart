import os
import sys
from abc import ABC, abstractmethod


class ANSIColor:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @classmethod
    def get_color(cls, name: str) -> str:
        color_map = {
            "red": cls.RED,
            "green": cls.GREEN,
            "yellow": cls.YELLOW,
            "blue": cls.BLUE,
            "magenta": cls.MAGENTA,
            "cyan": cls.CYAN,
            "white": cls.WHITE,
            "black": cls.BLACK,
        }
        return color_map.get(name.lower(), "")


class Component(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class TextRenderer:
    def __init__(self):
        self.buffer = []

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def add(self, text: str):
        self.buffer.append(text)

    def colorize(self, text: str, color: str, bold: bool = False) -> str:
        if not color:
            return text

        result = ""
        if bold:
            result += ANSIColor.BOLD
        result += ANSIColor.get_color(color)
        result += text
        result += ANSIColor.RESET
        return result

    def render(self):
        output = "\n".join(self.buffer)
        print(output, end="")
        sys.stdout.flush()
        self.buffer.clear()

    def render_box(self, content: list[str], width: int, style: str = "double") -> list[str]:
        if style == "double":
            top_left, top_right = "╔", "╗"
            bottom_left, bottom_right = "╚", "╝"
            horizontal, vertical = "═", "║"
            divider_left, divider_right, divider_cross = "╠", "╣", "╬"
        else:
            top_left, top_right = "┌", "┐"
            bottom_left, bottom_right = "└", "┘"
            horizontal, vertical = "─", "│"
            divider_left, divider_right, divider_cross = "├", "┤", "┼"

        inner_width = width - 2
        lines = []

        lines.append(top_left + horizontal * inner_width + top_right)

        for line in content:
            if line == "---":
                lines.append(divider_left + horizontal * inner_width + divider_right)
            else:
                padded = line.ljust(inner_width)[:inner_width]
                lines.append(vertical + padded + vertical)

        lines.append(bottom_left + horizontal * inner_width + bottom_right)

        return lines
