#!/usr/bin/env python3

import json
from pathlib import Path


class ContentStats:
    def __init__(self):
        self.stats = {}
        self.project_root = Path(__file__).parent.parent

    def analyze_content(self) -> None:
        self._count_categories()
        self._count_templates()
        self._count_madlibs_words()
        self._count_error_messages()
        self._count_hints()
        self._count_patterns()
        self._display_results()

    def _count_categories(self) -> None:
        filepath = self.project_root / "data/menu_categories.json"
        if not filepath.exists():
            return

        with open(filepath) as f:
            data = json.load(f)
            categories = data.get("categories", [])

        self.stats["Categories"] = len(categories)

        complexity_counts = {}
        for cat in categories:
            complexity = cat.get("complexity", 0)
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1

        self.stats["Complexity Distribution"] = complexity_counts

    def _count_templates(self) -> None:
        template_dir = self.project_root / "data/setting_templates"
        if not template_dir.exists():
            return

        template_files = list(template_dir.glob("*.json"))
        self.stats["Template Files"] = len(template_files)

        total_templates = 0
        for template_file in template_files:
            with open(template_file) as f:
                data = json.load(f)
                templates = data.get("templates", [])
                total_templates += len(templates)

        self.stats["Total Templates"] = total_templates

    def _count_madlibs_words(self) -> None:
        filepath = self.project_root / "data/madlibs_pools.json"
        if not filepath.exists():
            return

        with open(filepath) as f:
            pools = json.load(f)

        global_count = self._count_pool_words(pools.get("global_pools", {}))
        themed_count = self._count_pool_words(pools.get("themed_pools", {}))

        self.stats["Mad Libs Global Words"] = global_count
        self.stats["Mad Libs Themed Words"] = themed_count
        self.stats["Mad Libs Total Words"] = global_count + themed_count

        themed_pools = pools.get("themed_pools", {})
        self.stats["Themed Pool Categories"] = len(themed_pools)

    def _count_pool_words(self, pools: dict) -> int:
        count = 0
        for pool_data in pools.values():
            if isinstance(pool_data, dict):
                for subpool in pool_data.values():
                    if isinstance(subpool, list):
                        count += len(subpool)
            elif isinstance(pool_data, list):
                count += len(pool_data)
        return count

    def _count_error_messages(self) -> None:
        filepath = self.project_root / "data/error_messages.json"
        if not filepath.exists():
            return

        with open(filepath) as f:
            data = json.load(f)

        categories = data.get("error_categories", {})
        total_messages = sum(
            len(cat.get("messages", [])) for cat in categories.values()
        )
        total_hints = sum(
            len(cat.get("hints", [])) for cat in categories.values()
        )

        contextual = len(data.get("context_sensitive_errors", []))
        error_codes = len(data.get("error_codes", {}))

        self.stats["Error Categories"] = len(categories)
        self.stats["Error Messages"] = total_messages
        self.stats["Error Hints"] = total_hints
        self.stats["Contextual Errors"] = contextual
        self.stats["Error Codes"] = error_codes

    def _count_hints(self) -> None:
        filepath = self.project_root / "data/hints.json"
        if not filepath.exists():
            return

        with open(filepath) as f:
            data = json.load(f)

        hint_categories = data.get("hint_categories", {})
        category_hints = sum(
            len(hints)
            for category in hint_categories.values()
            for hints in category.values()
            if isinstance(hints, list)
        )

        contextual = len(data.get("contextual_hints", []))
        tutorial = len(data.get("tutorial_sequence", []))
        special = len(data.get("special_hints", {}))

        self.stats["Hint Categories"] = len(hint_categories)
        self.stats["Category Hints"] = category_hints
        self.stats["Contextual Hints"] = contextual
        self.stats["Tutorial Hints"] = tutorial
        self.stats["Special Hints"] = special
        self.stats["Total Hints"] = category_hints + contextual + tutorial + special

    def _count_patterns(self) -> None:
        filepath = self.project_root / "data/dependency_patterns.json"
        if not filepath.exists():
            return

        with open(filepath) as f:
            data = json.load(f)

        patterns = data.get("patterns", [])
        probabilities = data.get("pattern_probabilities", {})
        special_rules = data.get("special_category_rules", {})

        self.stats["Dependency Patterns"] = len(patterns)
        self.stats["Complexity Probability Maps"] = len(probabilities)
        self.stats["Special Category Rules"] = len(special_rules)

    def _display_results(self) -> None:
        print("=" * 60)
        print("CONTENT STATISTICS")
        print("=" * 60)

        for key, value in self.stats.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  Level {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")

        print("\n" + "=" * 60)


def main():
    stats = ContentStats()
    stats.analyze_content()


if __name__ == "__main__":
    main()
