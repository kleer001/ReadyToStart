import pytest

from src.ui.input_handler import Command, InputHandler


def test_input_handler_parse_command():
    handler = InputHandler()

    command = handler.parse_command("edit 5")
    assert command.action == "edit"
    assert command.args == ["5"]


def test_input_handler_parse_command_alias():
    handler = InputHandler()

    command = handler.parse_command("ls")
    assert command.action == "list"


def test_input_handler_parse_command_empty():
    handler = InputHandler()

    command = handler.parse_command("")
    assert command is None


def test_input_handler_validate_command_valid():
    handler = InputHandler()
    command = Command("list", [])

    is_valid, error = handler.validate_command(command)
    assert is_valid is True
    assert error == ""


def test_input_handler_validate_command_invalid_action():
    handler = InputHandler()
    command = Command("invalid", [])

    is_valid, error = handler.validate_command(command)
    assert is_valid is False
    assert "Unknown command" in error


def test_input_handler_validate_command_edit_missing_arg():
    handler = InputHandler()
    command = Command("edit", [])

    is_valid, error = handler.validate_command(command)
    assert is_valid is False
    assert "requires a setting number" in error


def test_input_handler_validate_command_goto_missing_arg():
    handler = InputHandler()
    command = Command("goto", [])

    is_valid, error = handler.validate_command(command)
    assert is_valid is False
    assert "requires a menu name" in error


def test_command_get_arg():
    command = Command("test", ["arg1", "arg2"])

    assert command.get_arg(0) == "arg1"
    assert command.get_arg(1) == "arg2"
    assert command.get_arg(2) is None
    assert command.get_arg(2, "default") == "default"
