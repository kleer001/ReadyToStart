import pytest

from src.ui.messages import MessageDisplay, MessageType


@pytest.fixture
def config_path():
    return "config/messages.ini"


def test_message_display_add_message(config_path):
    display = MessageDisplay(config_path)
    display.add_message("Test error", MessageType.ERROR)

    assert len(display.history) == 1
    assert len(display.current_messages) == 1
    assert display.history[0].text == "Test error"


def test_message_display_get_current_messages(config_path):
    display = MessageDisplay(config_path)
    display.add_message("Error 1", MessageType.ERROR)
    display.add_message("Warning 1", MessageType.WARNING)

    messages = display.get_current_messages()
    assert len(messages) == 2
    assert "[ERROR]" in messages[0]
    assert "[WARNING]" in messages[1]


def test_message_display_clear_current(config_path):
    display = MessageDisplay(config_path)
    display.add_message("Test", MessageType.INFO)
    display.clear_current()

    assert len(display.current_messages) == 0
    assert len(display.history) == 1


def test_message_display_get_history(config_path):
    display = MessageDisplay(config_path)

    for i in range(15):
        display.add_message(f"Message {i}", MessageType.INFO)

    history = display.get_history(10)
    assert len(history) == 10


def test_message_display_max_history(config_path):
    display = MessageDisplay(config_path)

    display.history = __import__("collections").deque(maxlen=5)

    for i in range(10):
        display.add_message(f"Message {i}", MessageType.INFO)

    assert len(display.history) == 5
