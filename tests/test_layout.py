import pytest

from src.ui.layout import LayoutManager, Region


def test_region_contains():
    region = Region(0, 0, 10, 10)

    assert region.contains(5, 5) is True
    assert region.contains(0, 0) is True
    assert region.contains(9, 9) is True
    assert region.contains(10, 10) is False
    assert region.contains(-1, 5) is False


def test_region_clip_text():
    region = Region(0, 0, 10, 10)

    assert region.clip_text("short") == "short     "
    assert region.clip_text("exactly10!") == "exactly10!"
    assert region.clip_text("this is too long") == "this is to"


def test_layout_manager_get_region():
    layout = LayoutManager("config/layout.ini")

    header = layout.get_region("header")
    assert header is not None
    assert isinstance(header, Region)


def test_layout_manager_render_region():
    layout = LayoutManager("config/layout.ini")

    content = ["Line 1", "Line 2", "Line 3"]
    rendered = layout.render_region("header", content)

    assert len(rendered) > 0


def test_layout_manager_render_region_clips_content():
    layout = LayoutManager("config/layout.ini")

    long_content = [f"Line {i}" for i in range(100)]
    rendered = layout.render_region("header", long_content)

    header_region = layout.get_region("header")
    assert len(rendered) <= header_region.height
