from pathlib import Path
import tempfile
import json
from src.meta.fourth_wall import FourthWallBreaker


def test_fourth_wall_initialization():
    breaker = FourthWallBreaker()
    assert len(breaker.breaks) == 0
    assert len(breaker.triggered_breaks) == 0


def test_fourth_wall_load_breaks():
    breaker = FourthWallBreaker()

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "breaks.json"
        data = {
            "breaks": [
                {
                    "id": "test",
                    "event": "game_start",
                    "condition": "first_time",
                    "show_once": True,
                    "text": "Welcome",
                    "pause": True,
                }
            ]
        }

        with open(filepath, "w") as f:
            json.dump(data, f)

        breaker.load_breaks(filepath)
        assert len(breaker.breaks) == 1


def test_fourth_wall_condition_checks():
    breaker = FourthWallBreaker()

    context_first = {"is_first": True}
    assert breaker._check_condition("first_time", context_first) is True

    context_not_first = {"is_first": False}
    assert breaker._check_condition("first_time", context_not_first) is False


def test_fourth_wall_frustrated_condition():
    breaker = FourthWallBreaker()

    context_frustrated = {"failed_attempts": 10}
    assert breaker._check_condition("frustrated", context_frustrated) is True

    context_not_frustrated = {"failed_attempts": 2}
    assert breaker._check_condition("frustrated", context_not_frustrated) is False


def test_fourth_wall_far_in_game_condition():
    breaker = FourthWallBreaker()

    context_far = {"layer_depth": 5}
    assert breaker._check_condition("far_in_game", context_far) is True

    context_near = {"layer_depth": 2}
    assert breaker._check_condition("far_in_game", context_near) is False


def test_fourth_wall_get_break():
    breaker = FourthWallBreaker()

    break_data = {
        "id": "test",
        "event": "game_start",
        "condition": "first_time",
        "show_once": True,
        "text": "Welcome",
        "pause": True,
    }
    breaker.breaks = [break_data]

    context = {"is_first": True}
    result = breaker.get_break("game_start", context)

    assert result is not None
    assert result["text"] == "Welcome"
    assert "test" in breaker.triggered_breaks


def test_fourth_wall_wrong_event():
    breaker = FourthWallBreaker()

    break_data = {
        "id": "test",
        "event": "game_start",
        "show_once": True,
        "text": "Welcome",
    }
    breaker.breaks = [break_data]

    context = {}
    result = breaker.get_break("game_end", context)

    assert result is None


def test_fourth_wall_show_once():
    breaker = FourthWallBreaker()

    break_data = {
        "id": "test",
        "event": "game_start",
        "show_once": True,
        "text": "Welcome",
    }
    breaker.breaks = [break_data]
    breaker.triggered_breaks.add("test")

    context = {}
    result = breaker.get_break("game_start", context)

    assert result is None


def test_fourth_wall_condition_not_met():
    breaker = FourthWallBreaker()

    break_data = {
        "id": "test",
        "event": "game_start",
        "condition": "frustrated",
        "show_once": True,
        "text": "Frustrated",
    }
    breaker.breaks = [break_data]

    context = {"failed_attempts": 2}
    result = breaker.get_break("game_start", context)

    assert result is None


def test_fourth_wall_multiple_breaks():
    breaker = FourthWallBreaker()

    breaks = [
        {"id": "break1", "event": "layer_transition", "show_once": False, "text": "Break 1"},
        {"id": "break2", "event": "layer_transition", "show_once": False, "text": "Break 2"},
    ]
    breaker.breaks = breaks

    context = {}
    eligible = breaker._find_eligible_breaks("layer_transition", context)

    assert len(eligible) == 2


def test_fourth_wall_break_eligibility():
    breaker = FourthWallBreaker()

    break_data = {
        "id": "test",
        "event": "game_start",
        "condition": "first_time",
        "show_once": True,
        "text": "Welcome",
    }

    context_eligible = {"is_first": True}
    assert breaker._is_break_eligible(break_data, "game_start", context_eligible) is True

    context_not_eligible = {"is_first": False}
    assert breaker._is_break_eligible(break_data, "game_start", context_not_eligible) is False


def test_fourth_wall_no_condition():
    breaker = FourthWallBreaker()

    break_data = {"id": "test", "event": "game_start", "show_once": False, "text": "Welcome"}
    breaker.breaks = [break_data]

    context = {}
    result = breaker.get_break("game_start", context)

    assert result is not None
