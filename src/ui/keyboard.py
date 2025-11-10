import sys
import tty
import termios
from contextlib import contextmanager


class Key:
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ENTER = "ENTER"
    ESC = "ESC"
    BACKSPACE = "BACKSPACE"


class KeyboardReader:
    def __init__(self):
        self.is_unix = sys.platform != "win32"
        self.raw_mode_active = False
        self.old_settings = None

    def enable_raw_mode(self):
        """Enable raw mode for the terminal."""
        if not self.is_unix or self.raw_mode_active:
            return
        try:
            fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            self.raw_mode_active = True
        except Exception:
            pass

    def disable_raw_mode(self):
        """Disable raw mode and restore normal terminal settings."""
        if not self.is_unix or not self.raw_mode_active:
            return
        try:
            fd = sys.stdin.fileno()
            if self.old_settings:
                termios.tcsetattr(fd, termios.TCSADRAIN, self.old_settings)
            self.raw_mode_active = False
        except Exception:
            pass

    @contextmanager
    def normal_mode(self):
        """Context manager to temporarily disable raw mode."""
        was_active = self.raw_mode_active
        if was_active:
            self.disable_raw_mode()
        try:
            yield
        finally:
            if was_active:
                self.enable_raw_mode()

    def read_key(self) -> str | None:
        if self.is_unix:
            return self._read_key_unix()
        else:
            return self._read_key_windows()

    def _read_key_unix(self) -> str | None:
        if not self.raw_mode_active:
            self.enable_raw_mode()

        try:
            ch = sys.stdin.read(1)

            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return Key.UP
                    elif ch3 == "B":
                        return Key.DOWN
                    elif ch3 == "C":
                        return Key.RIGHT
                    elif ch3 == "D":
                        return Key.LEFT
                return Key.ESC
            elif ch == "\r" or ch == "\n":
                return Key.ENTER
            elif ch == "\x7f":
                return Key.BACKSPACE
            elif ch == "w" or ch == "W":
                return Key.UP
            elif ch == "s" or ch == "S":
                return Key.DOWN
            elif ch == "a" or ch == "A":
                return Key.LEFT
            elif ch == "d" or ch == "D":
                return Key.RIGHT
            elif ch == "k" or ch == "K":
                return Key.UP
            elif ch == "j" or ch == "J":
                return Key.DOWN
            elif ch == "h" or ch == "H":
                return Key.LEFT
            elif ch == "l" or ch == "L":
                return Key.RIGHT
            else:
                return ch
        except Exception:
            return None

    def _read_key_windows(self) -> str | None:
        try:
            import msvcrt

            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch == b"\xe0":
                    ch2 = msvcrt.getch()
                    if ch2 == b"H":
                        return Key.UP
                    elif ch2 == b"P":
                        return Key.DOWN
                    elif ch2 == b"K":
                        return Key.LEFT
                    elif ch2 == b"M":
                        return Key.RIGHT
                elif ch == b"\r":
                    return Key.ENTER
                elif ch == b"\x1b":
                    return Key.ESC
                elif ch == b"\x08":
                    return Key.BACKSPACE
                else:
                    decoded = ch.decode("utf-8", errors="ignore")
                    if decoded in "wsadWSAD":
                        if decoded.lower() == "w":
                            return Key.UP
                        elif decoded.lower() == "s":
                            return Key.DOWN
                        elif decoded.lower() == "a":
                            return Key.LEFT
                        elif decoded.lower() == "d":
                            return Key.RIGHT
                    elif decoded in "jkJK":
                        if decoded.lower() == "k":
                            return Key.UP
                        elif decoded.lower() == "j":
                            return Key.DOWN
                    elif decoded in "hlHL":
                        if decoded.lower() == "h":
                            return Key.LEFT
                        elif decoded.lower() == "l":
                            return Key.RIGHT
                    return decoded
        except ImportError:
            pass
        return None
