"""Scripted player: drive UILoop programmatically without curses.

Lets us reproduce UI bugs from a script of keypresses, capturing state
transitions at each step. No real curses surface is initialized — we
hand the UILoop a FakeScreen that satisfies the bits of the curses
stdscr interface UILoop and its editors actually use.
"""

import curses
from contextlib import contextmanager
from unittest.mock import patch

from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.ui.main_loop import UILoop


KEY_NAMES = {
    "UP": curses.KEY_UP,
    "DOWN": curses.KEY_DOWN,
    "LEFT": curses.KEY_LEFT,
    "RIGHT": curses.KEY_RIGHT,
    "ENTER": ord("\n"),
    "ESC": 27,
    "BACKSPACE": curses.KEY_BACKSPACE,
    "SPACE": ord(" "),
    "TAB": ord("\t"),
}


def _key_to_code(key) -> int:
    if isinstance(key, int):
        return key
    if isinstance(key, str):
        if key in KEY_NAMES:
            return KEY_NAMES[key]
        if len(key) == 1:
            return ord(key)
    raise ValueError(f"Unknown key: {key!r}")


class FakeScreen:
    """A minimal stdscr substitute.

    Implements just the methods UILoop, TextRenderer, MenuDisplay, and
    the setting editors actually call. Tracks rendered cells so callers
    can inspect what would have been on screen, and reads input from a
    queue. In non-blocking mode (nodelay / timeout >= 0) getch returns
    -1 when the queue is empty; in blocking mode it raises StopIteration
    rather than hang, so missing scripted input fails loudly.
    """

    def __init__(self, height: int = 40, width: int = 120):
        self.height = height
        self.width = width
        self.key_queue: list[int] = []
        self.cells: dict[tuple[int, int], str] = {}
        self.frames: list[dict[tuple[int, int], str]] = []
        self._cursor = (0, 0)
        self._nodelay = False
        self._timeout_ms = -1

    def feed(self, *keys) -> None:
        for k in keys:
            self.key_queue.append(_key_to_code(k))

    def addstr(self, *args) -> None:
        # addstr(y, x, text[, attr]) or addstr(text[, attr])
        if args and isinstance(args[0], int):
            y, x, text = args[0], args[1], args[2]
        else:
            y, x = self._cursor
            text = args[0]
        for i, ch in enumerate(text):
            self.cells[(y, x + i)] = ch
        self._cursor = (y, x + len(text))

    def erase(self) -> None:
        if self.cells:
            self.frames.append(dict(self.cells))
        self.cells = {}
        self._cursor = (0, 0)

    def clear(self) -> None:
        self.erase()

    def refresh(self) -> None:
        pass

    def getmaxyx(self) -> tuple[int, int]:
        return self.height, self.width

    def nodelay(self, flag: bool) -> None:
        self._nodelay = flag

    def timeout(self, ms: int) -> None:
        self._timeout_ms = ms

    def keypad(self, flag: bool) -> None:
        pass

    def move(self, y: int, x: int) -> None:
        self._cursor = (y, x)

    def clrtoeol(self) -> None:
        y, cx = self._cursor
        for key in [k for k in self.cells if k[0] == y and k[1] >= cx]:
            del self.cells[key]

    def getch(self) -> int:
        if self.key_queue:
            return self.key_queue.pop(0)
        if self._nodelay or self._timeout_ms >= 0:
            return -1
        raise StopIteration("FakeScreen.getch blocked with no queued input")

    def getstr(self, *args) -> bytes:
        chars: list[str] = []
        while self.key_queue:
            ch = self.key_queue.pop(0)
            if ch in (ord("\n"), ord("\r")):
                break
            if 0 <= ch < 256:
                chars.append(chr(ch))
        return "".join(chars).encode("utf-8")

    def render_text(self) -> str:
        if not self.cells:
            return ""
        rows: dict[int, dict[int, str]] = {}
        for (y, x), ch in self.cells.items():
            rows.setdefault(y, {})[x] = ch
        lines = []
        for y in sorted(rows):
            row = rows[y]
            max_x = max(row.keys())
            line = "".join(row.get(x, " ") for x in range(max_x + 1))
            lines.append(line.rstrip())
        return "\n".join(lines)


@contextmanager
def _patched_curses():
    """Stub curses module functions that mutate global terminal state."""
    with patch("curses.curs_set"), patch("curses.echo"), patch("curses.noecho"):
        yield


class ScriptedPlayer:
    """Drive a UILoop with a key script and capture state transitions."""

    def __init__(self, game_state: GameState, config_dir: str):
        self.game_state = game_state
        self.screen = FakeScreen()
        self.ui = UILoop(game_state, config_dir)
        self.log: list[dict] = []

    def _snapshot(self) -> dict:
        menu = self.ui.navigation.current_menu
        enabled = sum(
            1
            for m in self.game_state.menus.values()
            for s in m.settings
            if s.state == SettingState.ENABLED
        )
        total = sum(len(m.settings) for m in self.game_state.menus.values())
        selected_id = None
        if menu:
            visible = [s for s in menu.settings if s.state != SettingState.HIDDEN]
            if 0 <= self.ui.selected_index < len(visible):
                selected_id = visible[self.ui.selected_index].id
        return {
            "current_menu": menu.id if menu else None,
            "selected_index": self.ui.selected_index,
            "selected_id": selected_id,
            "navigation_mode": self.ui.navigation_mode,
            "running": self.ui.running,
            "enabled": f"{enabled}/{total}",
            "messages": list(self.ui.message_display.get_current_messages())[-5:],
        }

    def start(self, start_menu_id: str) -> None:
        self.ui.stdscr = self.screen
        # Skip color init (no real terminal).
        self.ui.renderer.colors_initialized = True
        self.ui.renderer.set_screen(self.screen)

        success, error = self.ui.navigation.navigate_to(start_menu_id)
        if not success:
            raise RuntimeError(f"navigate_to({start_menu_id}) failed: {error}")

        # Match _curses_main's stdscr configuration.
        self.screen.nodelay(True)
        self.screen.timeout(50)

        self.ui.running = True
        self.log.append({"event": "start", "state": self._snapshot()})

    def step(self, key=None) -> bool:
        if key is not None:
            self.screen.feed(key)
        before = self._snapshot()
        with _patched_curses():
            self.ui._update()
            self.ui._render()
            self.ui._process_input()
        after = self._snapshot()
        if before != after:
            self.log.append(
                {"event": "step", "key": key, "before": before, "after": after}
            )
        return self.ui.running

    def play(self, script: list, drain_ticks: int = 20) -> dict:
        """Feed each scripted key (one per loop iteration), then drain.

        Drain ticks let post-input state changes (e.g. victory modal)
        surface. Returns a result dict with final snapshot, rendered
        screen, and the transition log.
        """
        for key in script:
            if not self.ui.running:
                break
            try:
                self.step(key)
            except StopIteration as e:
                self.log.append({"event": "blocked", "detail": str(e)})
                break
        for _ in range(drain_ticks):
            if not self.ui.running:
                break
            try:
                self.step(None)
            except StopIteration as e:
                self.log.append({"event": "blocked", "detail": str(e)})
                break
        return {
            "final": self._snapshot(),
            "screen": self.screen.render_text(),
            "log": self.log,
        }

    def auto_solve(self, max_steps: int = 500) -> dict:
        """Drive the real UI to enable every setting, choosing keys
        based on which DISABLED setting currently has all its deps met.

        Useful as an end-to-end check: same victory condition as the
        headless solver, but routed through real navigation and Enter.
        """
        steps_taken = 0
        while steps_taken < max_steps:
            menu = self.ui.navigation.current_menu
            if not menu:
                break
            visible = [s for s in menu.settings if s.state != SettingState.HIDDEN]
            target_idx = None
            for i, s in enumerate(visible):
                if (
                    s.state == SettingState.DISABLED
                    and self.game_state.resolver.can_enable(s.id, self.game_state)
                ):
                    target_idx = i
                    break
            if target_idx is None:
                # No enable-able setting on this menu; try right-arrow.
                if menu.connections:
                    self.step("RIGHT")
                    steps_taken += 1
                    continue
                break
            # Walk cursor to target.
            while self.ui.selected_index != target_idx:
                if target_idx > self.ui.selected_index:
                    self.step("DOWN")
                else:
                    self.step("UP")
                steps_taken += 1
            # Order matters: the main loop's _read_key consumes one key
            # to trigger _select_current; the modal editor (numeric or
            # string) then drains further keys itself. StringEditor
            # rejects empty input, so feed an actual char.
            target = visible[target_idx]
            self.screen.feed("ENTER")
            if target.type == SettingType.STRING:
                self.screen.feed("x", "ENTER")
            elif target.type != SettingType.BOOLEAN:
                self.screen.feed("ENTER")
            self.step()
            steps_taken += 1
        # Drain & dismiss victory modal if it appears.
        for _ in range(20):
            if not self.ui.running:
                break
            try:
                self.step("ENTER")
            except StopIteration:
                break
        return {
            "steps": steps_taken,
            "final": self._snapshot(),
            "screen": self.screen.render_text(),
            "log": self.log,
        }
