import unittest

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.testing.balance_tuner import BalanceTuner


class TestBalanceTuner(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()

    def test_initialization(self):
        tuner = BalanceTuner(self.game_state)
        self.assertEqual(tuner.game_state, self.game_state)

    def test_unlock_starters(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        tuner = BalanceTuner(self.game_state)
        unlocked = tuner.unlock_starters(3)

        self.assertEqual(unlocked, 3)
        enabled_count = sum(
            1
            for s in self.game_state.settings.values()
            if s.state == SettingState.ENABLED
        )
        self.assertEqual(enabled_count, 3)

    def test_unlock_starters_with_existing_enabled(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(5):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i < 2),
                state=SettingState.ENABLED if i < 2 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        tuner = BalanceTuner(self.game_state)
        unlocked = tuner.unlock_starters(4)

        self.assertEqual(unlocked, 2)
        enabled_count = sum(
            1
            for s in self.game_state.settings.values()
            if s.state == SettingState.ENABLED
        )
        self.assertEqual(enabled_count, 4)

    def test_reduce_density(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(5):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 5):
            for j in range(i):
                self.game_state.resolver.add_dependency(
                    f"s{i}", SimpleDependency(f"s{j}", SettingState.ENABLED)
                )

        initial_deps = sum(
            len(deps) for deps in self.game_state.resolver.dependencies.values()
        )

        tuner = BalanceTuner(self.game_state)
        removed = tuner.reduce_density(1.5)

        final_deps = sum(
            len(deps) for deps in self.game_state.resolver.dependencies.values()
        )

        self.assertGreater(removed, 0)
        self.assertLess(final_deps, initial_deps)

    def test_simplify_chains(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 10):
            self.game_state.resolver.add_dependency(
                f"s{i}", SimpleDependency(f"s{i-1}", SettingState.ENABLED)
            )

        tuner = BalanceTuner(self.game_state)
        simplified = tuner.simplify_chains(max_length=3)

        self.assertGreater(simplified, 0)

    def test_apply_easy_preset(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(20):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 20):
            for j in range(max(0, i - 2), i):
                self.game_state.resolver.add_dependency(
                    f"s{i}", SimpleDependency(f"s{j}", SettingState.ENABLED)
                )

        tuner = BalanceTuner(self.game_state)
        tuner.apply_preset("easy")

        unlockable_count = tuner._count_unlockable()
        self.assertGreaterEqual(unlockable_count, 8)

    def test_apply_hard_preset(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        tuner = BalanceTuner(self.game_state)
        tuner.apply_preset("hard")

        enabled_count = sum(
            1
            for s in self.game_state.settings.values()
            if s.state == SettingState.ENABLED
        )
        self.assertGreaterEqual(enabled_count, 2)

    def test_invalid_preset_raises_error(self):
        tuner = BalanceTuner(self.game_state)

        with self.assertRaises(ValueError):
            tuner.apply_preset("invalid_difficulty")

    def test_ensure_unlocked_ratio(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        tuner = BalanceTuner(self.game_state)
        tuner.ensure_unlocked_ratio(0.5)

        unlockable = tuner._count_unlockable()
        self.assertGreaterEqual(unlockable, 5)

    def test_get_adjustments_summary(self):
        tuner = BalanceTuner(self.game_state)
        summary = tuner.get_adjustments_summary("medium")

        self.assertIn("MEDIUM", summary)
        self.assertIn("Max Dependency Density", summary)
        self.assertIn("Max Chain Length", summary)

    def test_reduce_density_preserves_connectivity(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(5):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s1", SimpleDependency("s0", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s1", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s0", SettingState.ENABLED)
        )

        tuner = BalanceTuner(self.game_state)
        tuner.reduce_density(1.0)

        self.assertTrue(
            "s2" not in self.game_state.resolver.dependencies
            or len(self.game_state.resolver.dependencies["s2"]) >= 1
        )


if __name__ == "__main__":
    unittest.main()
