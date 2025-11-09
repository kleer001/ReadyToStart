import pytest

from src.ui.error_selector import ErrorMessageSelector


class TestErrorMessageSelector:
    @pytest.fixture
    def selector(self, tmp_path):
        error_file = tmp_path / "test_errors.json"
        error_file.write_text(
            """{
            "error_categories": {
                "locked_setting": {
                    "messages": [
                        "Cannot modify {setting}: Prerequisites not satisfied",
                        "{setting} is locked"
                    ],
                    "hints": [
                        "Try enabling {dependency} first",
                        "Check related settings"
                    ]
                },
                "invalid_value": {
                    "messages": [
                        "Value {value} is invalid"
                    ],
                    "hints": []
                }
            },
            "context_sensitive_errors": [
                {
                    "condition": "too_many_attempts",
                    "threshold": 5,
                    "message": "Too many attempts",
                    "hint": "Wait before trying again"
                }
            ],
            "error_codes": {
                "E001": "Dependency not satisfied"
            }
        }"""
        )
        return ErrorMessageSelector(str(error_file))

    def test_load_database(self, selector):
        assert "locked_setting" in selector.error_database["error_categories"]

    def test_get_error_message_basic(self, selector):
        context = {"setting": "audio_volume", "dependency": "audio_enable"}

        message, hint = selector.get_error_message("locked_setting", context)

        assert "audio_volume" in message
        assert isinstance(message, str)

    def test_get_error_message_with_hint(self, selector):
        context = {"setting": "test_setting", "dependency": "other_setting"}

        message, hint = selector.get_error_message("locked_setting", context)

        assert message is not None

    def test_get_error_with_code(self, selector):
        context = {"setting": "test_setting"}

        message, hint, code = selector.get_error_with_code("locked_setting", context)

        assert code is not None
        assert isinstance(code, str)

    def test_fill_template(self, selector):
        template = "Setting {setting} requires {dependency}"
        context = {"setting": "audio_volume", "dependency": "audio_enable"}

        result = selector._fill_template(template, context)

        assert "audio_volume" in result
        assert "audio_enable" in result

    def test_context_sensitive_error(self, selector):
        selector.update_context_state("attempt_count", 6)

        message, hint = selector.get_error_message("locked_setting", {})

        assert message is not None

    def test_increment_counter(self, selector):
        count1 = selector.increment_counter("test_counter")
        count2 = selector.increment_counter("test_counter")

        assert count1 == 1
        assert count2 == 2

    def test_reset_counter(self, selector):
        selector.increment_counter("test_counter")
        selector.reset_counter("test_counter")

        assert selector.context_state["test_counter"] == 0

    def test_message_history(self, selector):
        context = {"setting": "test"}
        selector.get_error_message("locked_setting", context)

        history = selector.get_message_history()
        assert len(history) > 0

    def test_clear_history(self, selector):
        context = {"setting": "test"}
        selector.get_error_message("locked_setting", context)
        selector.clear_history()

        history = selector.get_message_history()
        assert len(history) == 0

    def test_unknown_error_type(self, selector):
        message, hint = selector.get_error_message("unknown_type", {})

        assert message == "An error occurred"

    def test_template_with_missing_context(self, selector):
        context = {"setting": "test"}

        message, hint = selector.get_error_message("locked_setting", context)

        assert message is not None


class TestContextualErrors:
    @pytest.fixture
    def selector_with_contextual(self, tmp_path):
        error_file = tmp_path / "contextual_errors.json"
        error_file.write_text(
            """{
            "error_categories": {
                "test_error": {
                    "messages": ["Test message"],
                    "hints": []
                }
            },
            "context_sensitive_errors": [
                {
                    "condition": "too_many_attempts",
                    "threshold": 3,
                    "message": "Rate limit exceeded",
                    "hint": "Slow down"
                },
                {
                    "condition": "circular_dependency_detected",
                    "message": "Circular dependency found",
                    "hint": "Check your settings"
                }
            ],
            "error_codes": {}
        }"""
        )
        return ErrorMessageSelector(str(error_file))

    def test_too_many_attempts_contextual(self, selector_with_contextual):
        selector_with_contextual.update_context_state("attempt_count", 4)

        message, hint = selector_with_contextual.get_error_message("test_error", {})

        assert "Rate limit" in message or "attempt" in message.lower()

    def test_circular_dependency_contextual(self, selector_with_contextual):
        context = {"circular_detected": True}

        message, hint = selector_with_contextual.get_error_message(
            "test_error", context
        )

        assert message is not None
