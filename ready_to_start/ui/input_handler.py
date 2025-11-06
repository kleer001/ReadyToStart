from dataclasses import dataclass
from typing import Any


@dataclass
class Command:
    action: str
    args: list[str]

    def get_arg(self, index: int, default: Any = None) -> Any:
        return self.args[index] if index < len(self.args) else default


class InputHandler:
    def __init__(self):
        self.aliases = {
            "ls": "list",
            "e": "edit",
            "g": "goto",
            "b": "back",
            "h": "help",
            "?": "help",
            "s": "status",
            "q": "quit",
        }

    def get_input(self, prompt: str = "> ") -> str:
        return input(prompt).strip()

    def parse_command(self, user_input: str) -> Command | None:
        if not user_input:
            return None

        parts = user_input.split()
        action = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        action = self.aliases.get(action, action)

        return Command(action, args)

    def validate_command(self, command: Command) -> tuple[bool, str]:
        valid_actions = [
            "list",
            "edit",
            "goto",
            "back",
            "help",
            "status",
            "quit",
            "history",
        ]

        if command.action not in valid_actions:
            return False, f"Unknown command: {command.action}"

        if command.action == "edit" and not command.args:
            return False, "Edit command requires a setting number"

        if command.action == "goto" and not command.args:
            return False, "Goto command requires a menu name"

        return True, ""

    def read_command(self, prompt: str = "> ") -> Command | None:
        user_input = self.get_input(prompt)
        command = self.parse_command(user_input)

        if not command:
            return None

        is_valid, error = self.validate_command(command)
        if not is_valid:
            print(f"Error: {error}")
            return None

        return command
