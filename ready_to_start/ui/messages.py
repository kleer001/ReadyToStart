import time
from collections import deque
from configparser import ConfigParser
from enum import Enum

from ready_to_start.ui.renderer import ANSIColor


class MessageType(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"
    SUCCESS = "success"


class Message:
    def __init__(self, text: str, msg_type: MessageType, timestamp: float = None):
        self.text = text
        self.type = msg_type
        self.timestamp = timestamp or time.time()


class MessageDisplay:
    def __init__(self, config_path: str):
        self.config = ConfigParser()
        self.config.read(config_path)
        self.max_history = int(self.config.get("display", "max_history", fallback="50"))
        self.history = deque(maxlen=self.max_history)
        self.current_messages = []

    def add_message(self, text: str, msg_type: MessageType):
        message = Message(text, msg_type)
        self.history.append(message)
        self.current_messages.append(message)

    def _get_timeout(self, msg_type: MessageType) -> float:
        return float(self.config.get("timeouts", msg_type.value, fallback="3.0"))

    def _get_color(self, msg_type: MessageType) -> str:
        return self.config.get("colors", msg_type.value, fallback="white")

    def _wrap_text(self, text: str, width: int) -> list[str]:
        if len(text) <= width:
            return [text]

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + (1 if current_line else 0)
            if current_length + word_length <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _format_message(self, message: Message) -> str:
        color_code = ANSIColor.get_color(self._get_color(message.type))
        type_label = f"[{message.type.value.upper()}]"
        formatted = f"{color_code}{type_label}{ANSIColor.RESET} {message.text}"
        return formatted

    def update(self):
        auto_dismiss = self.config.getboolean("display", "auto_dismiss", fallback=True)
        if not auto_dismiss:
            return

        current_time = time.time()
        self.current_messages = [
            msg
            for msg in self.current_messages
            if current_time - msg.timestamp < self._get_timeout(msg.type)
        ]

    def get_current_messages(self) -> list[str]:
        wrap_width = int(self.config.get("display", "wrap_width", fallback="76"))
        formatted_messages = []

        for message in self.current_messages:
            formatted = self._format_message(message)
            formatted_messages.append(formatted)

        return formatted_messages

    def clear_current(self):
        self.current_messages.clear()

    def get_history(self, count: int = 10) -> list[str]:
        recent = list(self.history)[-count:]
        return [self._format_message(msg) for msg in recent]
