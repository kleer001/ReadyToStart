import json
from pathlib import Path

from src.testing.playtest_session import PlaytestTracker


class SessionReviewer:
    @staticmethod
    def list_sessions(directory: str = "playtest_sessions") -> list[Path]:
        sessions_dir = Path(directory)
        if not sessions_dir.exists():
            return []

        return sorted(sessions_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    @staticmethod
    def load_session(filepath: Path) -> PlaytestTracker:
        return PlaytestTracker.load(filepath)

    @staticmethod
    def compare_sessions(sessions: list[PlaytestTracker]) -> dict:
        if not sessions:
            return {}

        comparison = {
            "count": len(sessions),
            "completed": sum(1 for s in sessions if s.metrics.completed),
            "avg_duration": sum(s.metrics.duration for s in sessions) / len(sessions),
            "avg_interactions": sum(s.metrics.total_interactions for s in sessions) / len(sessions),
            "avg_failed": sum(s.metrics.failed_interactions for s in sessions) / len(sessions),
            "avg_stuck_time": sum(s.metrics.total_stuck_time for s in sessions) / len(sessions),
            "completion_rate": sum(1 for s in sessions if s.metrics.completed) / len(sessions) * 100,
        }

        return comparison

    @staticmethod
    def get_common_problems(sessions: list[PlaytestTracker]) -> dict:
        all_problem_settings = {}
        all_problem_menus = {}

        for session in sessions:
            for setting_id, count in session.metrics.get_problem_settings():
                all_problem_settings[setting_id] = all_problem_settings.get(setting_id, 0) + count

            for menu_id, duration in session.metrics.get_problem_menus():
                all_problem_menus[menu_id] = all_problem_menus.get(menu_id, 0.0) + duration

        return {
            "settings": sorted(all_problem_settings.items(), key=lambda x: x[1], reverse=True)[:10],
            "menus": sorted(all_problem_menus.items(), key=lambda x: x[1], reverse=True)[:10],
        }

    @staticmethod
    def generate_comparison_report(sessions: list[PlaytestTracker]) -> str:
        if not sessions:
            return "No sessions to compare"

        comparison = SessionReviewer.compare_sessions(sessions)
        problems = SessionReviewer.get_common_problems(sessions)

        lines = [
            "SESSION COMPARISON REPORT",
            "=" * 60,
            f"",
            f"Total Sessions: {comparison['count']}",
            f"Completed: {comparison['completed']} ({comparison['completion_rate']:.1f}%)",
            f"",
            f"Averages:",
            f"  Duration: {comparison['avg_duration']:.1f}s",
            f"  Interactions: {comparison['avg_interactions']:.1f}",
            f"  Failed Actions: {comparison['avg_failed']:.1f}",
            f"  Stuck Time: {comparison['avg_stuck_time']:.1f}s",
        ]

        if problems["settings"]:
            lines.append(f"\nMost Problematic Settings:")
            for setting_id, count in problems["settings"][:5]:
                lines.append(f"  {setting_id}: {count} failures")

        if problems["menus"]:
            lines.append(f"\nMost Time-Consuming Menus:")
            for menu_id, duration in problems["menus"][:5]:
                lines.append(f"  {menu_id}: {duration:.1f}s")

        return "\n".join(lines)

    @staticmethod
    def export_comparison(sessions: list[PlaytestTracker], filepath: str) -> None:
        comparison = SessionReviewer.compare_sessions(sessions)
        problems = SessionReviewer.get_common_problems(sessions)

        data = {
            "comparison": comparison,
            "problems": {
                "settings": [{"id": s, "count": c} for s, c in problems["settings"]],
                "menus": [{"id": m, "duration": d} for m, d in problems["menus"]],
            },
            "sessions": [
                {
                    "session_id": s.metrics.session_id,
                    "seed": s.metrics.seed,
                    "completed": s.metrics.completed,
                    "duration": s.metrics.duration,
                    "interactions": s.metrics.total_interactions,
                }
                for s in sessions
            ],
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
