"""Tests for state machine module."""

from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.state_machine import SettingStateMachine
from ready_to_start.core.types import Setting


def test_valid_transitions():
    """Test all valid state transitions."""
    valid_cases = [
        (SettingState.DISABLED, SettingState.ENABLED),
        (SettingState.DISABLED, SettingState.HIDDEN),
        (SettingState.ENABLED, SettingState.DISABLED),
        (SettingState.ENABLED, SettingState.LOCKED),
        (SettingState.LOCKED, SettingState.ENABLED),
        (SettingState.HIDDEN, SettingState.DISABLED),
        (SettingState.HIDDEN, SettingState.ENABLED),
        (SettingState.BLINKING, SettingState.ENABLED),
        (SettingState.BLINKING, SettingState.DISABLED),
    ]

    for from_state, to_state in valid_cases:
        assert SettingStateMachine.can_transition(from_state, to_state) is True


def test_invalid_transitions():
    """Test invalid state transitions."""
    invalid_cases = [
        (SettingState.DISABLED, SettingState.LOCKED),
        (SettingState.ENABLED, SettingState.HIDDEN),
        (SettingState.LOCKED, SettingState.DISABLED),
        (SettingState.LOCKED, SettingState.HIDDEN),
        (SettingState.HIDDEN, SettingState.LOCKED),
    ]

    for from_state, to_state in invalid_cases:
        assert SettingStateMachine.can_transition(from_state, to_state) is False


def test_transition_setting(sample_setting):
    """Test transitioning a setting."""
    # Valid transition
    assert sample_setting.state == SettingState.DISABLED
    result = SettingStateMachine.transition(sample_setting, SettingState.ENABLED)
    assert result is True
    assert sample_setting.state == SettingState.ENABLED

    # Invalid transition
    result = SettingStateMachine.transition(sample_setting, SettingState.HIDDEN)
    assert result is False
    assert sample_setting.state == SettingState.ENABLED  # State unchanged


def test_get_allowed_transitions():
    """Test getting allowed transitions."""
    allowed = SettingStateMachine.get_allowed_transitions(SettingState.DISABLED)
    assert SettingState.ENABLED in allowed
    assert SettingState.HIDDEN in allowed
    assert len(allowed) == 2

    allowed = SettingStateMachine.get_allowed_transitions(SettingState.LOCKED)
    assert SettingState.ENABLED in allowed
    assert len(allowed) == 1


def test_transition_chain():
    """Test a chain of transitions."""
    setting = Setting(
        id="chain",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="Chain Test",
    )

    # DISABLED -> ENABLED -> LOCKED -> ENABLED -> DISABLED
    assert SettingStateMachine.transition(setting, SettingState.ENABLED)
    assert setting.state == SettingState.ENABLED

    assert SettingStateMachine.transition(setting, SettingState.LOCKED)
    assert setting.state == SettingState.LOCKED

    assert SettingStateMachine.transition(setting, SettingState.ENABLED)
    assert setting.state == SettingState.ENABLED

    assert SettingStateMachine.transition(setting, SettingState.DISABLED)
    assert setting.state == SettingState.DISABLED
