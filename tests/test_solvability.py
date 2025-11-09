import unittest

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.testing.solvability_checker import SolvabilityChecker


class TestSolvabilityChecker(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()

    def test_empty_game_is_solvable(self):
        checker = SolvabilityChecker(self.game_state)
        self.assertTrue(checker.validate())
        self.assertEqual(len(checker.issues), 0)

    def test_simple_solvable_game(self):
        menu = MenuNode(id="menu1", category="test")
        setting1 = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=True,
            state=SettingState.ENABLED,
            label="Setting 1",
        )
        setting2 = Setting(
            id="s2",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 2",
        )
        menu.add_setting(setting1)
        menu.add_setting(setting2)
        self.game_state.add_menu(menu)
        self.game_state.current_menu = "menu1"

        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s1", SettingState.ENABLED)
        )

        checker = SolvabilityChecker(self.game_state)
        self.assertTrue(checker.validate())

    def test_circular_dependency_detected(self):
        menu = MenuNode(id="menu1", category="test")
        setting1 = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 1",
        )
        setting2 = Setting(
            id="s2",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 2",
        )
        menu.add_setting(setting1)
        menu.add_setting(setting2)
        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s1", SimpleDependency("s2", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s1", SettingState.ENABLED)
        )

        checker = SolvabilityChecker(self.game_state)
        self.assertFalse(checker.validate())
        self.assertTrue(
            any(issue.type == "circular_dependency" for issue in checker.issues)
        )

    def test_missing_dependency_detected(self):
        menu = MenuNode(id="menu1", category="test")
        setting1 = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 1",
        )
        menu.add_setting(setting1)
        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s1", SimpleDependency("nonexistent", SettingState.ENABLED)
        )

        checker = SolvabilityChecker(self.game_state)
        self.assertFalse(checker.validate())
        self.assertTrue(
            any(issue.type == "missing_dependency" for issue in checker.issues)
        )

    def test_unreachable_menu_detected(self):
        menu1 = MenuNode(id="menu1", category="test", connections=["menu2"])
        menu2 = MenuNode(id="menu2", category="test")
        menu3 = MenuNode(id="menu3", category="test")

        self.game_state.add_menu(menu1)
        self.game_state.add_menu(menu2)
        self.game_state.add_menu(menu3)
        self.game_state.current_menu = "menu1"

        checker = SolvabilityChecker(self.game_state)
        self.assertFalse(checker.validate())
        self.assertTrue(
            any(issue.type == "unreachable_menus" for issue in checker.issues)
        )

    def test_unlockable_setting_detected(self):
        menu = MenuNode(id="menu1", category="test")
        setting1 = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 1",
        )
        setting2 = Setting(
            id="s2",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 2",
        )
        menu.add_setting(setting1)
        menu.add_setting(setting2)
        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s1", SimpleDependency("s2", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s1", SettingState.ENABLED)
        )

        checker = SolvabilityChecker(self.game_state)
        self.assertFalse(checker.validate())
        self.assertTrue(
            any(issue.type == "unlockable_setting" for issue in checker.issues)
        )

    def test_get_report_no_issues(self):
        menu = MenuNode(id="menu1", category="test")
        setting = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=True,
            state=SettingState.ENABLED,
            label="Setting 1",
        )
        menu.add_setting(setting)
        self.game_state.add_menu(menu)
        self.game_state.current_menu = "menu1"

        checker = SolvabilityChecker(self.game_state)
        checker.validate()
        report = checker.get_report()

        self.assertIn("solvable", report)
        self.assertIn("no issues", report)

    def test_get_report_with_issues(self):
        menu = MenuNode(id="menu1", category="test")
        setting = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="Setting 1",
        )
        menu.add_setting(setting)
        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s1", SimpleDependency("nonexistent", SettingState.ENABLED)
        )

        checker = SolvabilityChecker(self.game_state)
        checker.validate()
        report = checker.get_report()

        self.assertIn("issues", report)
        self.assertIn("Critical", report)

    def test_complex_dependency_chain(self):
        menu = MenuNode(id="menu1", category="test")

        s1 = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=True,
            state=SettingState.ENABLED,
            label="S1",
        )
        s2 = Setting(
            id="s2",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="S2",
        )
        s3 = Setting(
            id="s3",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="S3",
        )

        menu.add_setting(s1)
        menu.add_setting(s2)
        menu.add_setting(s3)
        self.game_state.add_menu(menu)
        self.game_state.current_menu = "menu1"

        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s1", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s3", SimpleDependency("s2", SettingState.ENABLED)
        )

        checker = SolvabilityChecker(self.game_state)
        self.assertTrue(checker.validate())


if __name__ == "__main__":
    unittest.main()
