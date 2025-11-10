import curses
from abc import ABC, abstractmethod


class CursesColor:
    """Color pair constants for ncurses."""
    # Color pair IDs (initialized in setup_colors)
    DEFAULT = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    BLACK = 8

    @classmethod
    def setup_colors(cls):
        """Initialize ncurses color pairs."""
        if not curses.has_colors():
            return

        curses.start_color()
        curses.use_default_colors()

        # Initialize color pairs (foreground, background)
        curses.init_pair(cls.RED, curses.COLOR_RED, -1)
        curses.init_pair(cls.GREEN, curses.COLOR_GREEN, -1)
        curses.init_pair(cls.YELLOW, curses.COLOR_YELLOW, -1)
        curses.init_pair(cls.BLUE, curses.COLOR_BLUE, -1)
        curses.init_pair(cls.MAGENTA, curses.COLOR_MAGENTA, -1)
        curses.init_pair(cls.CYAN, curses.COLOR_CYAN, -1)
        curses.init_pair(cls.WHITE, curses.COLOR_WHITE, -1)
        curses.init_pair(cls.BLACK, curses.COLOR_BLACK, -1)

    @classmethod
    def get_color(cls, name: str) -> int:
        """Get color pair ID by name."""
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
        return color_map.get(name.lower(), cls.DEFAULT)


class Component(ABC):
    @abstractmethod
    def render(self, window) -> None:
        """Render component to an ncurses window."""
        pass


class TextRenderer:
    """ncurses-based text renderer."""

    def __init__(self, stdscr=None):
        self.stdscr = stdscr
        self.colors_initialized = False

    def set_screen(self, stdscr):
        """Set the curses screen."""
        self.stdscr = stdscr
        if not self.colors_initialized:
            CursesColor.setup_colors()
            self.colors_initialized = True

    def clear_screen(self):
        """Clear the screen."""
        if self.stdscr:
            self.stdscr.clear()

    def refresh(self):
        """Refresh the screen to show changes."""
        if self.stdscr:
            self.stdscr.refresh()

    def addstr(self, y: int, x: int, text: str, color: str = "", bold: bool = False):
        """Add a string at position (y, x) with optional color and bold."""
        if not self.stdscr:
            return

        try:
            attr = 0
            if bold:
                attr |= curses.A_BOLD
            if color:
                color_pair = CursesColor.get_color(color)
                attr |= curses.color_pair(color_pair)

            if attr:
                self.stdscr.addstr(y, x, text, attr)
            else:
                self.stdscr.addstr(y, x, text)
        except curses.error:
            # Ignore errors from writing outside screen bounds
            pass

    def get_screen_size(self) -> tuple[int, int]:
        """Get screen size as (height, width)."""
        if self.stdscr:
            return self.stdscr.getmaxyx()
        return (24, 80)  # Default fallback

    def render_box(self, y: int, x: int, height: int, width: int,
                   content: list[str], style: str = "double") -> int:
        """
        Render a box with content at position (y, x).
        Returns the number of lines rendered.
        """
        if not self.stdscr:
            return 0

        if style == "double":
            # Unicode double-line box characters
            top_left, top_right = "╔", "╗"
            bottom_left, bottom_right = "╚", "╝"
            horizontal, vertical = "═", "║"
            divider_left, divider_right = "╠", "╣"
        else:
            # Unicode single-line box characters
            top_left, top_right = "┌", "┐"
            bottom_left, bottom_right = "└", "┘"
            horizontal, vertical = "─", "│"
            divider_left, divider_right = "├", "┤"

        inner_width = width - 2

        try:
            # Top border
            self.stdscr.addstr(y, x, top_left + horizontal * inner_width + top_right)
            current_y = y + 1

            # Content lines
            for line in content:
                if current_y >= y + height - 1:
                    break

                if line == "---":
                    # Divider line
                    self.stdscr.addstr(current_y, x, divider_left + horizontal * inner_width + divider_right)
                else:
                    # Content line - truncate/pad to fit
                    display_text = line[:inner_width].ljust(inner_width)
                    self.stdscr.addstr(current_y, x, vertical + display_text + vertical)
                current_y += 1

            # Bottom border
            if current_y < y + height:
                self.stdscr.addstr(current_y, x, bottom_left + horizontal * inner_width + bottom_right)
                current_y += 1

        except curses.error:
            pass

        return current_y - y

    def render_box_with_colors(self, y: int, x: int, height: int, width: int,
                               content: list[tuple[str, str, bool]], style: str = "double") -> int:
        """
        Render a box with colored content.
        content is list of (text, color, bold) tuples.
        Returns the number of lines rendered.
        """
        if not self.stdscr:
            return 0

        if style == "double":
            top_left, top_right = "╔", "╗"
            bottom_left, bottom_right = "╚", "╝"
            horizontal, vertical = "═", "║"
            divider_left, divider_right = "╠", "╣"
        else:
            top_left, top_right = "┌", "┐"
            bottom_left, bottom_right = "└", "┘"
            horizontal, vertical = "─", "│"
            divider_left, divider_right = "├", "┤"

        inner_width = width - 2

        try:
            # Top border
            self.stdscr.addstr(y, x, top_left + horizontal * inner_width + top_right)
            current_y = y + 1

            # Content lines
            for item in content:
                if current_y >= y + height - 1:
                    break

                if isinstance(item, str):
                    # Simple string (for backward compatibility)
                    text, color, bold = item, "", False
                else:
                    # Tuple of (text, color, bold)
                    text, color, bold = item

                if text == "---":
                    # Divider line
                    self.stdscr.addstr(current_y, x, divider_left + horizontal * inner_width + divider_right)
                else:
                    # Left border
                    self.stdscr.addstr(current_y, x, vertical)

                    # Content with color
                    display_text = text[:inner_width].ljust(inner_width)

                    attr = 0
                    if bold:
                        attr |= curses.A_BOLD
                    if color:
                        color_pair = CursesColor.get_color(color)
                        attr |= curses.color_pair(color_pair)

                    if attr:
                        self.stdscr.addstr(current_y, x + 1, display_text, attr)
                    else:
                        self.stdscr.addstr(current_y, x + 1, display_text)

                    # Right border
                    self.stdscr.addstr(current_y, x + width - 1, vertical)

                current_y += 1

            # Bottom border
            if current_y < y + height:
                self.stdscr.addstr(current_y, x, bottom_left + horizontal * inner_width + bottom_right)
                current_y += 1

        except curses.error:
            pass

        return current_y - y
