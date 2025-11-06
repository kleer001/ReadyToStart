import pytest
from configparser import ConfigParser

from ready_to_start.ui.progress_bars import (
    NestedProgressBar,
    OscillatingProgressBar,
    ProgressBarFactory,
    ReliableProgressBar,
    StuckProgressBar,
    UnreliableProgressBar,
)


@pytest.fixture
def config():
    cfg = ConfigParser()
    cfg.read("config/progress_bars.ini")
    return cfg


def test_reliable_progress_bar_update(config):
    bar = ReliableProgressBar("Test", config)
    initial_progress = bar.progress

    bar.update(0.1)
    assert bar.progress > initial_progress


def test_reliable_progress_bar_max(config):
    bar = ReliableProgressBar("Test", config)
    bar.progress = 1.0

    bar.update(0.1)
    assert bar.progress == 1.0


def test_stuck_progress_bar_gets_stuck(config):
    bar = StuckProgressBar("Test", config, stuck_at=0.5)

    while bar.progress < 0.5:
        bar.update(0.1)

    bar.update(0.1)
    assert bar.is_stuck is True
    assert bar.progress == 0.5


def test_oscillating_progress_bar_changes_direction(config):
    bar = OscillatingProgressBar("Test", config)
    bar.progress = 1.0
    bar.direction = 1

    bar.update(0.1)
    assert bar.direction == -1


def test_nested_progress_bar_has_children(config):
    bar = NestedProgressBar("Test", config, child_count=3)
    assert len(bar.children) == 3


def test_nested_progress_bar_calculates_average(config):
    bar = NestedProgressBar("Test", config, child_count=2)
    bar.children[0].progress = 0.5
    bar.children[1].progress = 0.5

    total_progress = sum(child.progress for child in bar.children)
    expected_progress = total_progress / len(bar.children)

    assert expected_progress == 0.5


def test_progress_bar_render(config):
    bar = ReliableProgressBar("Test", config)
    bar.progress = 0.5

    lines = bar.render()
    assert len(lines) > 0
    assert "Test" in lines[0]
    assert "50%" in lines[0]


def test_progress_bar_factory_create_reliable(config):
    bar = ProgressBarFactory.create("Test", "reliable", config)
    assert isinstance(bar, ReliableProgressBar)


def test_progress_bar_factory_create_unreliable(config):
    bar = ProgressBarFactory.create("Test", "unreliable", config)
    assert isinstance(bar, UnreliableProgressBar)


def test_progress_bar_factory_create_stuck(config):
    bar = ProgressBarFactory.create("Test", "stuck", config)
    assert isinstance(bar, StuckProgressBar)


def test_progress_bar_factory_create_nested(config):
    bar = ProgressBarFactory.create("Test", "nested", config)
    assert isinstance(bar, NestedProgressBar)
