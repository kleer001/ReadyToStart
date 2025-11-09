from random import Random

import pytest

from src.anti_patterns.messages import (
    FakeMessage,
    FakeMessageGenerator,
    MessageScheduler,
)


@pytest.fixture
def generator():
    gen = FakeMessageGenerator(random=Random(42))
    gen.templates["generic"] = [
        "Error {code}: {operation} failed",
        "Cannot {action}: {resource} is {state}",
    ]
    gen.templates["system"] = [
        "System error {code}",
    ]
    gen.components["code"] = ["0x80004005", "ERR_FATAL"]
    gen.components["operation"] = ["save", "load"]
    gen.components["action"] = ["enable", "disable"]
    gen.components["resource"] = ["audio device", "network"]
    gen.components["state"] = ["locked", "unavailable"]
    return gen


def test_fake_message_creation():
    msg = FakeMessage("test_type", "Test message", "error")

    assert msg.message_type == "test_type"
    assert msg.text == "Test message"
    assert msg.severity == "error"


def test_fake_message_default_severity():
    msg = FakeMessage("test_type", "Test message")

    assert msg.severity == "error"


def test_generator_empty_templates():
    gen = FakeMessageGenerator(random=Random(42))

    msg = gen.generate("missing_category")

    assert msg.message_type == "fake_error"
    assert msg.text == "An error has occurred"


def test_generator_generate_generic(generator):
    msg = generator.generate("generic")

    assert msg.message_type == "fake_error"
    assert msg.severity == "error"
    assert len(msg.text) > 0


def test_generator_generate_system(generator):
    msg = generator.generate("system")

    assert msg.message_type == "fake_error"
    assert "System error" in msg.text


def test_generator_template_substitution(generator):
    generator.templates["test"] = ["Error {code}"]

    msg = generator.generate("test")

    assert msg.text in ["Error 0x80004005", "Error ERR_FATAL"]


def test_generator_multiple_substitutions(generator):
    generator.templates["test"] = ["{action} {resource}"]

    msg = generator.generate("test")

    assert any(action in msg.text for action in ["enable", "disable"]) and any(
        resource in msg.text for resource in ["audio device", "network"]
    )


def test_generator_generate_system_message(generator):
    msg = generator.generate_system_message()

    assert msg.message_type == "fake_error"
    assert "System error" in msg.text


def test_generator_generate_permission_error(generator):
    generator.templates["permission"] = ["Permission denied"]

    msg = generator.generate_permission_error()

    assert msg.text == "Permission denied"


def test_generator_generate_dependency_error(generator):
    generator.templates["dependency"] = ["Dependency error"]

    msg = generator.generate_dependency_error()

    assert msg.text == "Dependency error"


def test_generator_generate_resource_error(generator):
    generator.templates["resource"] = ["Resource unavailable"]

    msg = generator.generate_resource_error()

    assert msg.text == "Resource unavailable"


def test_generator_load_from_config(tmp_path):
    config_content = """[template_generic]
messages =
    Error {code}
    Cannot {action}

[template_system]
messages =
    System {state}

[components_code]
values =
    ERR_001
    ERR_002

[components_action]
values =
    proceed
    continue

[components_state]
values =
    busy
    idle
"""

    config_path = tmp_path / "test_messages.ini"
    config_path.write_text(config_content)

    gen = FakeMessageGenerator()
    gen.load_from_config(str(config_path))

    assert "generic" in gen.templates
    assert len(gen.templates["generic"]) == 2
    assert "system" in gen.templates
    assert len(gen.components["code"]) == 2
    assert len(gen.components["action"]) == 2


def test_message_scheduler_schedule_message(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    scheduler.schedule_message(5, "generic")

    assert len(scheduler.scheduled) == 1
    assert scheduler.scheduled[0][0] == 5


def test_message_scheduler_tick_not_ready(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    scheduler.schedule_message(5, "generic")
    messages = scheduler.tick()

    assert len(messages) == 0
    assert len(scheduler.scheduled) == 1


def test_message_scheduler_tick_ready(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    scheduler.schedule_message(1, "generic")

    messages = scheduler.tick()

    assert len(messages) == 1
    assert len(scheduler.scheduled) == 0


def test_message_scheduler_multiple_messages(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    scheduler.schedule_message(1, "generic")
    scheduler.schedule_message(1, "system")
    scheduler.schedule_message(2, "generic")

    messages = scheduler.tick()

    assert len(messages) == 2


def test_message_scheduler_schedule_random(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    scheduler.schedule_random(5, 10, "generic")

    assert len(scheduler.scheduled) == 1
    tick, msg = scheduler.scheduled[0]
    assert 5 <= (tick - scheduler.tick_count) <= 10


def test_message_scheduler_clear(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    scheduler.schedule_message(5, "generic")
    scheduler.schedule_message(10, "system")

    scheduler.clear()

    assert len(scheduler.scheduled) == 0


def test_message_scheduler_tick_count_increments(generator):
    scheduler = MessageScheduler(generator, random=Random(42))

    assert scheduler.tick_count == 0

    scheduler.tick()
    assert scheduler.tick_count == 1

    scheduler.tick()
    assert scheduler.tick_count == 2


def test_generator_deterministic_with_seed():
    gen1 = FakeMessageGenerator(random=Random(42))
    gen1.templates["test"] = ["Message {code}"]
    gen1.components["code"] = ["A", "B", "C"]

    gen2 = FakeMessageGenerator(random=Random(42))
    gen2.templates["test"] = ["Message {code}"]
    gen2.components["code"] = ["A", "B", "C"]

    msg1 = gen1.generate("test")
    msg2 = gen2.generate("test")

    assert msg1.text == msg2.text
