"""State machine for managing setting state transitions."""

from src.core.enums import SettingState
from src.core.types import Setting


class SettingStateMachine:
    """Manages valid state transitions for settings.

    Defines which state transitions are allowed and provides
    methods to validate and perform transitions.
    """

    TRANSITIONS = {
        SettingState.DISABLED: [SettingState.ENABLED, SettingState.HIDDEN],
        SettingState.ENABLED: [SettingState.DISABLED, SettingState.LOCKED],
        SettingState.LOCKED: [SettingState.ENABLED],
        SettingState.HIDDEN: [SettingState.DISABLED, SettingState.ENABLED],
        SettingState.BLINKING: [SettingState.ENABLED, SettingState.DISABLED],
    }

    @staticmethod
    def can_transition(from_state: SettingState, to_state: SettingState) -> bool:
        """Check if a transition is valid.

        Args:
            from_state: Current state
            to_state: Desired state

        Returns:
            True if transition is allowed
        """
        allowed_transitions = SettingStateMachine.TRANSITIONS.get(from_state, [])
        return to_state in allowed_transitions

    @staticmethod
    def transition(setting: Setting, new_state: SettingState) -> bool:
        """Attempt to transition a setting to a new state.

        Args:
            setting: Setting to transition
            new_state: Desired new state

        Returns:
            True if transition succeeded, False otherwise
        """
        if SettingStateMachine.can_transition(setting.state, new_state):
            setting.state = new_state
            return True
        return False

    @staticmethod
    def get_allowed_transitions(state: SettingState) -> list[SettingState]:
        """Get all allowed transitions from a given state.

        Args:
            state: Current state

        Returns:
            List of allowed target states
        """
        return SettingStateMachine.TRANSITIONS.get(state, [])
