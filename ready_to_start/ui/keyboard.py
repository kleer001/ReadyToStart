import sys
import tty
import termios


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

    def read_key(self) -> str | None:
        if self.is_unix:
            return self._read_key_unix()
        else:
            return self._read_key_windows()

    def _read_key_unix(self) -> str | None:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
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
            else:
                return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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
                    return decoded
        except ImportError:
            pass
        return None
