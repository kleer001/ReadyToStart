import pytest

from ready_to_start.ui.renderer import ANSIColor, TextRenderer


def test_ansi_color_get_color():
    assert ANSIColor.get_color("red") == ANSIColor.RED
    assert ANSIColor.get_color("green") == ANSIColor.GREEN
    assert ANSIColor.get_color("unknown") == ""


def test_text_renderer_colorize():
    renderer = TextRenderer()
    result = renderer.colorize("test", "red")
    assert ANSIColor.RED in result
    assert "test" in result
    assert ANSIColor.RESET in result


def test_text_renderer_colorize_bold():
    renderer = TextRenderer()
    result = renderer.colorize("test", "green", bold=True)
    assert ANSIColor.BOLD in result
    assert ANSIColor.GREEN in result


def test_text_renderer_colorize_empty_color():
    renderer = TextRenderer()
    result = renderer.colorize("test", "")
    assert result == "test"


def test_text_renderer_buffer():
    renderer = TextRenderer()
    renderer.add("line1")
    renderer.add("line2")
    assert len(renderer.buffer) == 2
    assert renderer.buffer[0] == "line1"
    assert renderer.buffer[1] == "line2"


def test_text_renderer_render_box():
    renderer = TextRenderer()
    content = ["Line 1", "Line 2"]
    box = renderer.render_box(content, 20, "double")

    assert len(box) == 4
    assert box[0].startswith("╔")
    assert box[-1].startswith("╚")


def test_text_renderer_render_box_with_divider():
    renderer = TextRenderer()
    content = ["Header", "---", "Body"]
    box = renderer.render_box(content, 20, "double")

    assert len(box) == 5
    assert "╠" in box[2]
