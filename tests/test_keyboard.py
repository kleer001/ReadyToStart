import pytest

from ready_to_start.ui.keyboard import Key, KeyboardReader


def test_key_constants():
    assert Key.UP == "UP"
    assert Key.DOWN == "DOWN"
    assert Key.LEFT == "LEFT"
    assert Key.RIGHT == "RIGHT"
    assert Key.ENTER == "ENTER"
    assert Key.ESC == "ESC"


def test_keyboard_reader_initialization():
    reader = KeyboardReader()
    assert reader.is_unix is not None
