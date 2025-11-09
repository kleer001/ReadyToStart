import pytest

from ready_to_start.ui.hint_display import HintDisplay


class TestHintDisplay:
    @pytest.fixture
    def hint_display(self, tmp_path):
        hints_file = tmp_path / "test_hints.json"
        hints_file.write_text(
            """{
            "hint_categories": {
                "navigation": {
                    "helpful": [
                        "Use 'list' to see settings",
                        "Type 'help' for commands"
                    ],
                    "misleading": [
                        "Type 'sudo' for access",
                        "Try random commands"
                    ]
                },
                "dependencies": {
                    "helpful": [
                        "Check locked settings",
                        "Enable prerequisites first"
                    ]
                }
            },
            "contextual_hints": [
                {
                    "trigger": "stuck_on_menu_for_minutes",
                    "threshold": 180,
                    "hint": "Try exploring other menus",
                    "helpful": true,
                    "cooldown": 300
                },
                {
                    "trigger": "many_failed_attempts",
                    "threshold": 5,
                    "hint": "Check dependencies in other menus",
                    "helpful": true
                }
            ],
            "tutorial_sequence": [
                {
                    "step": 1,
                    "trigger": "game_start",
                    "hint": "Welcome! Try 'list' to begin",
                    "show_once": true
                },
                {
                    "step": 2,
                    "trigger": "first_enable",
                    "hint": "Good job enabling a setting",
                    "show_once": true
                }
            ],
            "hint_display_rules": {
                "max_hints_per_session": 50,
                "min_cooldown_seconds": 1,
                "show_helpful_ratio": 0.7
            }
        }"""
        )
        return HintDisplay(str(hints_file))

    def test_load_hints(self, hint_display):
        assert "navigation" in hint_display.hints_database["hint_categories"]

    def test_get_helpful_hint(self, hint_display):
        hint = hint_display.get_helpful_hint("navigation")

        assert hint is not None
        assert isinstance(hint, str)

    def test_get_misleading_hint(self, hint_display):
        hint = hint_display.get_misleading_hint("navigation")

        assert hint is not None
        assert isinstance(hint, str)

    def test_tutorial_hints_sequential(self, hint_display):
        context1 = {"game_just_started": True}
        hint1 = hint_display.get_hint(context=context1)

        assert hint1 is not None
        assert "Welcome" in hint1

    def test_tutorial_progress_tracking(self, hint_display):
        context1 = {"game_just_started": True}
        hint_display.get_hint(context=context1)

        assert hint_display.tutorial_progress >= 1

    def test_contextual_hint_trigger(self, hint_display):
        context = {"time_on_menu": 200}

        hint = hint_display.get_hint(context=context)

        assert hint is not None

    def test_hint_cooldown(self, hint_display):
        hint_display._mark_hint_shown("test_hint")

        shown_recently = not hint_display._check_cooldown(
            "test_hint", {"cooldown": 10}
        )

        assert shown_recently

    def test_show_once_hints(self, hint_display):
        context = {"game_just_started": True}

        hint1 = hint_display.get_hint(context=context)
        hint2 = hint_display.get_hint(context=context)

        assert hint1 is not None

    def test_max_hints_limit(self, hint_display):
        hint_display.hint_count = 50

        can_show = hint_display._can_show_hint()

        assert not can_show

    def test_hint_count_increments(self, hint_display):
        initial_count = hint_display.get_hint_count()

        hint_display.get_hint(category="navigation")

        assert hint_display.get_hint_count() > initial_count

    def test_reset_hint_count(self, hint_display):
        hint_display.get_hint(category="navigation")
        hint_display.reset_hint_count()

        assert hint_display.get_hint_count() == 0

    def test_reset_tutorial(self, hint_display):
        hint_display.tutorial_progress = 5
        hint_display._mark_hint_shown("tutorial_1")

        hint_display.reset_tutorial()

        assert hint_display.tutorial_progress == 0
        assert len(hint_display.shown_hints) == 0


class TestContextualHints:
    @pytest.fixture
    def hint_display_with_contexts(self, tmp_path):
        hints_file = tmp_path / "contextual_hints.json"
        hints_file.write_text(
            """{
            "hint_categories": {
                "test": {
                    "helpful": ["Test hint"]
                }
            },
            "contextual_hints": [
                {
                    "trigger": "many_failed_attempts",
                    "threshold": 5,
                    "hint": "You've failed many times",
                    "helpful": true
                },
                {
                    "trigger": "high_completion_rate",
                    "threshold": 0.75,
                    "hint": "Almost done!",
                    "helpful": true
                }
            ],
            "tutorial_sequence": [],
            "hint_display_rules": {
                "max_hints_per_session": 50,
                "min_cooldown_seconds": 1
            }
        }"""
        )
        return HintDisplay(str(hints_file))

    def test_failed_attempts_trigger(self, hint_display_with_contexts):
        context = {"failed_attempts": 6}

        hint = hint_display_with_contexts.get_hint(context=context)

        assert hint is not None

    def test_completion_rate_trigger(self, hint_display_with_contexts):
        context = {"completion_rate": 0.8}

        hint = hint_display_with_contexts.get_hint(context=context)

        assert hint is not None


class TestHintSelection:
    @pytest.fixture
    def hint_display_for_selection(self, tmp_path):
        hints_file = tmp_path / "selection_hints.json"
        hints_file.write_text(
            """{
            "hint_categories": {
                "category_a": {
                    "helpful": ["Helpful A1", "Helpful A2"],
                    "misleading": ["Misleading A1"]
                },
                "category_b": {
                    "helpful": ["Helpful B1"]
                }
            },
            "contextual_hints": [],
            "tutorial_sequence": [],
            "hint_display_rules": {
                "max_hints_per_session": 100,
                "min_cooldown_seconds": 0,
                "show_helpful_ratio": 0.7
            }
        }"""
        )
        return HintDisplay(str(hints_file))

    def test_category_hint_selection(self, hint_display_for_selection):
        hint = hint_display_for_selection._get_category_hint("category_a", helpful=True)

        assert hint is not None
        assert "Helpful A" in hint

    def test_random_category_when_none_specified(self, hint_display_for_selection):
        hint = hint_display_for_selection._get_random_category_hint(None)

        assert hint is not None
