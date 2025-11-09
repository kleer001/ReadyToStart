import json
import random
from pathlib import Path
from typing import Any


class ErrorMessageSelector:
    def __init__(self, database_file: str = "data/error_messages.json"):
        self.error_database = {}
        self.message_history = []
        self.context_state = {}
        self._load_database(database_file)

    def get_error_message(
        self, error_type: str, context: dict[str, Any]
    ) -> tuple[str, str | None]:
        contextual_error = self._check_contextual_errors(context)
        if contextual_error:
            return contextual_error

        if error_type not in self.error_database.get("error_categories", {}):
            return ("An error occurred", None)

        category = self.error_database["error_categories"][error_type]
        message = self._select_message(category, context)
        hint = self._select_hint(category, context)

        self._record_message(error_type, message, hint, context)

        return (message, hint)

    def get_error_with_code(
        self, error_type: str, context: dict[str, Any]
    ) -> tuple[str, str | None, str]:
        message, hint = self.get_error_message(error_type, context)
        error_code = self._get_error_code(error_type)

        if error_code:
            message = f"[{error_code}] {message}"

        return (message, hint, error_code)

    def update_context_state(self, key: str, value: Any) -> None:
        self.context_state[key] = value

    def increment_counter(self, counter_name: str) -> int:
        current = self.context_state.get(counter_name, 0)
        self.context_state[counter_name] = current + 1
        return self.context_state[counter_name]

    def reset_counter(self, counter_name: str) -> None:
        self.context_state[counter_name] = 0

    def get_message_history(self) -> list[dict]:
        return self.message_history.copy()

    def clear_history(self) -> None:
        self.message_history.clear()

    def _load_database(self, filepath: str) -> None:
        path = Path(filepath)
        if not path.exists():
            self.error_database = self._default_database()
            return

        with open(path) as f:
            self.error_database = json.load(f)

    def _check_contextual_errors(
        self, context: dict[str, Any]
    ) -> tuple[str, str | None] | None:
        contextual = self.error_database.get("context_sensitive_errors", [])

        for error_spec in contextual:
            if self._check_condition(error_spec, context):
                message = self._fill_template(error_spec["message"], context)
                hint = self._fill_template(error_spec.get("hint", ""), context)
                return (message, hint if hint else None)

        return None

    def _check_condition(self, error_spec: dict, context: dict[str, Any]) -> bool:
        condition = error_spec["condition"]

        condition_handlers = {
            "too_many_attempts": lambda: self.context_state.get("attempt_count", 0)
            > error_spec.get("threshold", 5),
            "rapid_changes": lambda: self.context_state.get("changes_per_minute", 0)
            > error_spec.get("threshold", 10),
            "after_glitch": lambda: self.context_state.get("glitch_occurred", False),
            "circular_dependency_detected": lambda: context.get(
                "circular_detected", False
            ),
            "dependency_chain_too_long": lambda: context.get("chain_length", 0)
            > error_spec.get("threshold", 10),
            "resource_exhausted": lambda: self.context_state.get(
                "resource_usage", 0.0
            )
            > 0.9,
            "validation_in_progress": lambda: self.context_state.get(
                "validating", False
            ),
        }

        handler = condition_handlers.get(condition)
        if handler:
            applies_to = error_spec.get("applies_to", [])
            if applies_to:
                category = context.get("category", "")
                if category not in applies_to:
                    return False
            return handler()

        return False

    def _select_message(self, category: dict, context: dict[str, Any]) -> str:
        messages = category.get("messages", [])
        if not messages:
            return "An error occurred"

        message_template = random.choice(messages)
        return self._fill_template(message_template, context)

    def _select_hint(self, category: dict, context: dict[str, Any]) -> str | None:
        hints = category.get("hints", [])
        if not hints or random.random() > 0.6:
            return None

        hint_template = random.choice(hints)
        return self._fill_template(hint_template, context)

    def _fill_template(self, template: str, context: dict[str, Any]) -> str:
        result = template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))

        result = self._fill_random_placeholders(result)
        return result

    def _fill_random_placeholders(self, text: str) -> str:
        if "{code}" in text:
            code = format(random.randint(0, 0xFFFF), "04X")
            text = text.replace("{code}", code)
        return text

    def _get_error_code(self, error_type: str) -> str:
        error_codes = self.error_database.get("error_codes", {})
        code_map = {
            "locked_setting": "E001",
            "invalid_value": "E002",
            "permission_denied": "E003",
            "state_transition": "E004",
            "dependency_conflict": "E005",
            "value_dependency": "E006",
        }
        return code_map.get(error_type, "E000")

    def _record_message(
        self, error_type: str, message: str, hint: str | None, context: dict[str, Any]
    ) -> None:
        self.message_history.append(
            {
                "type": error_type,
                "message": message,
                "hint": hint,
                "context": context.copy(),
            }
        )

        if len(self.message_history) > 100:
            self.message_history = self.message_history[-100:]

    def _default_database(self) -> dict:
        return {
            "error_categories": {
                "locked_setting": {
                    "messages": [
                        "Cannot modify {setting}: Prerequisites not satisfied"
                    ],
                    "hints": ["Check for dependencies"],
                }
            }
        }
