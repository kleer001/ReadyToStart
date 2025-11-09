from src.meta.achievements import Achievement, AchievementSystem
from src.meta.end_game_summary import EndGameSummary
from src.meta.statistics import GameStatistics


def test_end_game_summary_initialization():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    assert summary.stats == stats
    assert summary.achievements == achievements


def test_end_game_summary_header_generation():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    header = summary._generate_header()
    assert len(header) > 0
    assert any("CONGRATULATIONS" in line for line in header)


def test_end_game_summary_statistics_section():
    stats = GameStatistics()
    stats.total_actions = 100
    stats.settings_enabled = 50

    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    section = summary._generate_statistics_section()
    assert any("STATISTICS" in line for line in section)
    assert any("100" in line for line in section)


def test_end_game_summary_achievements_section():
    stats = GameStatistics()
    achievements = AchievementSystem()

    for i in range(5):
        ach = Achievement(
            id=f"test{i}",
            name=f"Test {i}",
            description="Test",
            condition="settings_enabled",
            threshold=i,
            secret=False,
            rarity="common",
            unlocked=(i < 3),
        )
        achievements.achievements[f"test{i}"] = ach
        if i < 3:
            achievements.unlocked_count += 1

    summary = EndGameSummary(stats, achievements)
    section = summary._generate_achievements_section()

    assert any("ACHIEVEMENTS" in line for line in section)
    assert any("3/5" in line for line in section)


def test_end_game_summary_time_comments():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    stats.total_play_time = 8000
    comments = summary._get_time_comments(8000)
    assert len(comments) > 0
    assert "2 hours" in comments[0]

    comments = summary._get_time_comments(300)
    assert len(comments) > 0
    assert "speedran" in comments[0].lower()


def test_end_game_summary_error_comments():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    stats.total_errors = 0
    comments = summary._get_error_comments()
    assert len(comments) > 0
    assert "Zero errors" in comments[0]

    stats.total_errors = 150
    comments = summary._get_error_comments()
    assert len(comments) > 0
    assert "100 errors" in comments[0]


def test_end_game_summary_efficiency_comments():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    stats.average_efficiency = 95
    comments = summary._get_efficiency_comments()
    assert len(comments) > 0

    stats.average_efficiency = 15
    comments = summary._get_efficiency_comments()
    assert len(comments) > 0


def test_end_game_summary_secret_comments():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    stats.secrets_found = ["s1", "s2", "s3", "s4", "s5", "s6"]
    comments = summary._get_secret_comments()
    assert len(comments) > 0

    stats.secrets_found = []
    comments = summary._get_secret_comments()
    assert len(comments) > 0
    assert "zero secrets" in comments[0].lower()


def test_end_game_summary_quit_comments():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    stats.quit_attempts = 15
    comments = summary._get_quit_comments()
    assert len(comments) > 0
    assert "10 times" in comments[0]


def test_end_game_summary_layer_comments():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    stats.layers_completed = 20
    comments = summary._get_layer_comments()
    assert len(comments) > 0
    assert "EVERY layer" in comments[0]


def test_end_game_summary_complete_generation():
    stats = GameStatistics()
    stats.total_actions = 100
    stats.settings_enabled = 50
    stats.total_errors = 10
    stats.layers_completed = 5

    achievements = AchievementSystem()
    for i in range(3):
        ach = Achievement(
            id=f"test{i}",
            name=f"Test {i}",
            description="Test",
            condition="settings_enabled",
            threshold=i,
            secret=False,
            rarity="common",
            unlocked=True,
        )
        achievements.achievements[f"test{i}"] = ach
    achievements.unlocked_count = 3

    summary = EndGameSummary(stats, achievements)
    result = summary.generate_summary()

    assert len(result) > 0
    assert "CONGRATULATIONS" in result
    assert "STATISTICS" in result
    assert "ACHIEVEMENTS" in result


def test_end_game_summary_footer_generation():
    stats = GameStatistics()
    achievements = AchievementSystem()
    summary = EndGameSummary(stats, achievements)

    footer = summary._generate_footer()
    assert len(footer) > 0
    assert any("Thanks for playing" in line for line in footer)
