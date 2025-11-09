from pathlib import Path
import tempfile
import json
from time import sleep
from src.meta.self_awareness import SelfAwarenessSystem


def test_self_awareness_initialization():
    system = SelfAwarenessSystem()
    assert len(system.comments) == 0
    assert system.awareness_level == 0
    assert len(system.triggered_comments) == 0


def test_self_awareness_load_comments():
    system = SelfAwarenessSystem()

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "comments.json"
        data = {
            "comments": [
                {
                    "id": "test1",
                    "trigger": "time_spent_excessive",
                    "min_awareness": 0,
                    "show_once": True,
                    "text": "Test comment",
                }
            ]
        }

        with open(filepath, "w") as f:
            json.dump(data, f)

        system.load_comments(filepath)
        assert len(system.comments) == 1


def test_self_awareness_trigger_checks():
    system = SelfAwarenessSystem()

    context_excessive_time = {"time_spent": 700}
    assert system._check_trigger("time_spent_excessive", context_excessive_time) is True

    context_normal_time = {"time_spent": 100}
    assert system._check_trigger("time_spent_excessive", context_normal_time) is False


def test_self_awareness_failed_attempts_trigger():
    system = SelfAwarenessSystem()

    context_many_fails = {"failed_attempts": 15}
    assert system._check_trigger("many_failed_attempts", context_many_fails) is True

    context_few_fails = {"failed_attempts": 5}
    assert system._check_trigger("many_failed_attempts", context_few_fails) is False


def test_self_awareness_glitch_trigger():
    system = SelfAwarenessSystem()

    context_with_glitch = {"glitch_count": 3}
    assert system._check_trigger("glitch_occurred", context_with_glitch) is True

    context_no_glitch = {"glitch_count": 0}
    assert system._check_trigger("glitch_occurred", context_no_glitch) is False


def test_self_awareness_layer_depth_trigger():
    system = SelfAwarenessSystem()

    context_deep = {"layer_depth": 7}
    assert system._check_trigger("deep_layer_reached", context_deep) is True

    context_shallow = {"layer_depth": 2}
    assert system._check_trigger("deep_layer_reached", context_shallow) is False


def test_self_awareness_awareness_level():
    system = SelfAwarenessSystem()
    assert system.get_awareness_level() == 0

    system.increase_awareness(3)
    assert system.get_awareness_level() == 3

    system.increase_awareness(10)
    assert system.get_awareness_level() == 10


def test_self_awareness_comment_eligibility():
    system = SelfAwarenessSystem()

    comment = {
        "id": "test",
        "trigger": "time_spent_excessive",
        "min_awareness": 2,
        "show_once": True,
        "text": "Test",
    }
    system.comments = [comment]

    context = {"time_spent": 700}

    system.awareness_level = 1
    assert system._is_comment_eligible(comment, context) is False

    system.awareness_level = 3
    assert system._is_comment_eligible(comment, context) is True


def test_self_awareness_show_once():
    system = SelfAwarenessSystem()

    comment = {
        "id": "test",
        "trigger": "time_spent_excessive",
        "min_awareness": 0,
        "show_once": True,
        "text": "Test",
    }
    system.comments = [comment]
    system.triggered_comments.add("test")

    context = {"time_spent": 700}
    assert system._is_comment_eligible(comment, context) is False


def test_self_awareness_get_contextual_comment():
    system = SelfAwarenessSystem()

    comment = {
        "id": "test",
        "trigger": "time_spent_excessive",
        "min_awareness": 0,
        "show_once": True,
        "text": "Time spent comment",
    }
    system.comments = [comment]

    context = {"time_spent": 700}
    result = system.get_contextual_comment(context)

    assert result == "Time spent comment"
    assert "test" in system.triggered_comments


def test_self_awareness_no_eligible_comments():
    system = SelfAwarenessSystem()

    comment = {
        "id": "test",
        "trigger": "time_spent_excessive",
        "min_awareness": 5,
        "show_once": True,
        "text": "Test",
    }
    system.comments = [comment]

    context = {"time_spent": 100}
    result = system.get_contextual_comment(context)

    assert result is None


def test_self_awareness_cooldown():
    system = SelfAwarenessSystem()
    system.comment_cooldown = 0.1

    context = {"time_spent": 700}

    assert system.should_trigger_comment(context) is False

    sleep(0.15)
    system.last_comment_time = 0.0

    system.awareness_level = 10
    triggered = False
    for _ in range(100):
        if system.should_trigger_comment(context):
            triggered = True
            break

    assert triggered


def test_self_awareness_multiple_triggers():
    system = SelfAwarenessSystem()

    comments = [
        {
            "id": "time",
            "trigger": "time_spent_excessive",
            "min_awareness": 0,
            "show_once": False,
            "text": "Time comment",
        },
        {
            "id": "glitch",
            "trigger": "glitch_occurred",
            "min_awareness": 0,
            "show_once": False,
            "text": "Glitch comment",
        },
    ]
    system.comments = comments

    context = {"time_spent": 700, "glitch_count": 3}
    eligible = system._find_eligible_comments(context)

    assert len(eligible) == 2
