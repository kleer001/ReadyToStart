from random import Random

import pytest

from src.anti_patterns.glitches import (
    CharacterCorruptionGlitch,
    CharacterDeletionGlitch,
    CharacterDuplicationGlitch,
    ColorGlitch,
    GlitchComposite,
    GlitchEngine,
    OffsetGlitch,
)


@pytest.fixture
def random_gen():
    return Random(42)


def test_character_corruption_zero_intensity(random_gen):
    glitch = CharacterCorruptionGlitch("test", intensity=0.0)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert result == text


def test_character_corruption_applies(random_gen):
    glitch = CharacterCorruptionGlitch("test", intensity=0.5)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert result != text
    assert len(result) == len(text)


def test_character_corruption_empty_string(random_gen):
    glitch = CharacterCorruptionGlitch("test", intensity=0.5)

    result = glitch.apply("", random_gen)

    assert result == ""


def test_character_duplication_zero_intensity(random_gen):
    glitch = CharacterDuplicationGlitch("test", intensity=0.0)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert result == text


def test_character_duplication_applies(random_gen):
    glitch = CharacterDuplicationGlitch("test", intensity=0.5)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert len(result) > len(text)


def test_character_duplication_empty_string(random_gen):
    glitch = CharacterDuplicationGlitch("test", intensity=0.5)

    result = glitch.apply("", random_gen)

    assert result == ""


def test_character_deletion_zero_intensity(random_gen):
    glitch = CharacterDeletionGlitch("test", intensity=0.0)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert result == text


def test_character_deletion_applies(random_gen):
    glitch = CharacterDeletionGlitch("test", intensity=0.5)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert len(result) < len(text)


def test_character_deletion_empty_string(random_gen):
    glitch = CharacterDeletionGlitch("test", intensity=0.5)

    result = glitch.apply("", random_gen)

    assert result == ""


def test_color_glitch_zero_intensity(random_gen):
    glitch = ColorGlitch("test", intensity=0.0)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert result == text


def test_color_glitch_applies(random_gen):
    glitch = ColorGlitch("test", intensity=1.0)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert "\033[" in result
    assert "\033[0m" in result


def test_color_glitch_empty_string(random_gen):
    glitch = ColorGlitch("test", intensity=0.5)

    result = glitch.apply("", random_gen)

    assert result == ""


def test_offset_glitch_zero_intensity(random_gen):
    glitch = OffsetGlitch("test", intensity=0.0)
    text = "Hello World"

    result = glitch.apply(text, random_gen)

    assert result == text


def test_offset_glitch_applies(random_gen):
    glitch = OffsetGlitch("test", intensity=1.0)
    text = "Hello World"

    applied_count = 0
    for _ in range(100):
        result = glitch.apply(text, random_gen)
        if result.startswith(" "):
            applied_count += 1
            assert result.strip() == text

    assert applied_count > 0


def test_offset_glitch_empty_string(random_gen):
    glitch = OffsetGlitch("test", intensity=0.5)

    result = glitch.apply("", random_gen)

    assert result == ""


def test_glitch_intensity_clamping():
    glitch = CharacterCorruptionGlitch("test", intensity=1.5)
    assert glitch.intensity == 1.0

    glitch = CharacterCorruptionGlitch("test", intensity=-0.5)
    assert glitch.intensity == 0.0


def test_glitch_composite_single_glitch(random_gen):
    glitch = CharacterCorruptionGlitch("test", intensity=0.5)
    composite = GlitchComposite([glitch], random_gen)

    text = "Hello World"
    result = composite.apply(text)

    assert result != text


def test_glitch_composite_multiple_glitches(random_gen):
    glitches = [
        CharacterCorruptionGlitch("c1", intensity=0.2),
        CharacterDuplicationGlitch("c2", intensity=0.2),
        ColorGlitch("c3", intensity=0.5),
    ]
    composite = GlitchComposite(glitches, random_gen)

    text = "Hello World"
    result = composite.apply(text)

    assert result != text


def test_glitch_composite_empty_list(random_gen):
    composite = GlitchComposite([], random_gen)

    text = "Hello World"
    result = composite.apply(text)

    assert result == text


def test_glitch_engine_disabled_by_default():
    engine = GlitchEngine(intensity=0.5, random=Random(42))

    assert not engine.enabled


def test_glitch_engine_enable():
    engine = GlitchEngine(intensity=0.5, random=Random(42))

    engine.enable()

    assert engine.enabled


def test_glitch_engine_disable():
    engine = GlitchEngine(intensity=0.5, random=Random(42))

    engine.enable()
    engine.disable()

    assert not engine.enabled


def test_glitch_engine_process_text_disabled():
    engine = GlitchEngine(intensity=1.0, random=Random(42))
    text = "Hello World"

    result = engine.process_text(text)

    assert result == text


def test_glitch_engine_process_text_enabled():
    engine = GlitchEngine(intensity=1.0, random=Random(42))
    engine.enable()

    text = "Hello World"
    glitched_count = 0

    for _ in range(100):
        result = engine.process_text(text)
        if result != text:
            glitched_count += 1

    assert glitched_count > 0


def test_glitch_engine_process_empty_string():
    engine = GlitchEngine(intensity=0.5, random=Random(42))
    engine.enable()

    result = engine.process_text("")

    assert result == ""


def test_glitch_engine_set_intensity():
    engine = GlitchEngine(intensity=0.3, random=Random(42))

    engine.set_intensity(0.8)

    assert engine.intensity == 0.8


def test_glitch_engine_intensity_clamping():
    engine = GlitchEngine(intensity=0.5, random=Random(42))

    engine.set_intensity(1.5)
    assert engine.intensity == 1.0

    engine.set_intensity(-0.5)
    assert engine.intensity == 0.0


def test_glitch_engine_has_glitches():
    engine = GlitchEngine(intensity=0.5, random=Random(42))

    assert len(engine.glitches) > 0


def test_glitch_engine_deterministic():
    engine1 = GlitchEngine(intensity=0.5, random=Random(42))
    engine1.enable()

    engine2 = GlitchEngine(intensity=0.5, random=Random(42))
    engine2.enable()

    text = "Hello World"

    result1 = engine1.process_text(text)
    result2 = engine2.process_text(text)

    assert result1 == result2
