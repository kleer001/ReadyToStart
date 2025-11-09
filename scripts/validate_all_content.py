#!/usr/bin/env python3

import json
import sys
from pathlib import Path


class ContentValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {}

    def validate_all(self) -> bool:
        self._validate_categories()
        self._validate_templates()
        self._validate_madlibs_pools()
        self._validate_dependency_patterns()
        self._validate_error_messages()
        self._validate_hints()

        return self._report_results()

    def _validate_categories(self) -> None:
        filepath = Path("data/menu_categories.json")
        if not filepath.exists():
            self.errors.append("Missing menu_categories.json")
            return

        try:
            with open(filepath) as f:
                data = json.load(f)
                categories = data.get("categories", [])

            if len(categories) != 32:
                self.errors.append(
                    f"Expected 32 categories, found {len(categories)}"
                )
            else:
                self.stats["categories"] = len(categories)

        except Exception as e:
            self.errors.append(f"Category validation failed: {e}")

    def _validate_templates(self) -> None:
        template_dir = Path("data/setting_templates")
        if not template_dir.exists():
            self.errors.append("Missing setting_templates directory")
            return

        categories_file = Path("data/menu_categories.json")
        if not categories_file.exists():
            return

        with open(categories_file) as f:
            categories = json.load(f)["categories"]

        template_count = 0
        missing = []

        for category in categories:
            template_file = template_dir / f"{category['id']}_templates.json"
            if not template_file.exists():
                missing.append(category["id"])
                continue

            try:
                with open(template_file) as f:
                    template_data = json.load(f)
                    templates = template_data.get("templates", [])
                    template_count += len(templates)
            except Exception as e:
                self.errors.append(
                    f"Failed to load template {category['id']}: {e}"
                )

        if missing:
            self.errors.append(f"Missing template files: {missing}")

        self.stats["template_files"] = len(categories) - len(missing)
        self.stats["total_templates"] = template_count

    def _validate_madlibs_pools(self) -> None:
        filepath = Path("data/madlibs_pools.json")
        if not filepath.exists():
            self.errors.append("Missing madlibs_pools.json")
            return

        try:
            with open(filepath) as f:
                pools = json.load(f)

            global_pools = pools.get("global_pools", {})
            required_pools = ["adjectives", "nouns", "verbs"]

            for pool_name in required_pools:
                if pool_name not in global_pools:
                    self.errors.append(f"Missing required pool: {pool_name}")

            word_count = self._count_words_in_pools(global_pools)
            word_count += self._count_words_in_pools(
                pools.get("themed_pools", {})
            )

            if word_count < 500:
                self.warnings.append(
                    f"Word pool has only {word_count} entries (expected 500+)"
                )

            self.stats["madlibs_words"] = word_count

        except Exception as e:
            self.errors.append(f"Mad Libs validation failed: {e}")

    def _count_words_in_pools(self, pools: dict) -> int:
        count = 0
        for pool_data in pools.values():
            if isinstance(pool_data, dict):
                for subpool in pool_data.values():
                    if isinstance(subpool, list):
                        count += len(subpool)
            elif isinstance(pool_data, list):
                count += len(pool_data)
        return count

    def _validate_dependency_patterns(self) -> None:
        filepath = Path("data/dependency_patterns.json")
        if not filepath.exists():
            self.errors.append("Missing dependency_patterns.json")
            return

        try:
            with open(filepath) as f:
                data = json.load(f)

            patterns = data.get("patterns", [])
            if len(patterns) < 10:
                self.warnings.append(
                    f"Only {len(patterns)} dependency patterns (expected 10+)"
                )

            self.stats["dependency_patterns"] = len(patterns)

        except Exception as e:
            self.errors.append(f"Dependency pattern validation failed: {e}")

    def _validate_error_messages(self) -> None:
        filepath = Path("data/error_messages.json")
        if not filepath.exists():
            self.errors.append("Missing error_messages.json")
            return

        try:
            with open(filepath) as f:
                data = json.load(f)

            error_count = sum(
                len(cat.get("messages", []))
                for cat in data.get("error_categories", {}).values()
            )

            if error_count < 100:
                self.warnings.append(
                    f"Only {error_count} error messages (expected 100+)"
                )

            self.stats["error_messages"] = error_count

        except Exception as e:
            self.errors.append(f"Error message validation failed: {e}")

    def _validate_hints(self) -> None:
        filepath = Path("data/hints.json")
        if not filepath.exists():
            self.errors.append("Missing hints.json")
            return

        try:
            with open(filepath) as f:
                data = json.load(f)

            hint_count = sum(
                len(hints)
                for category in data.get("hint_categories", {}).values()
                for hints in category.values()
                if isinstance(hints, list)
            )

            hint_count += len(data.get("contextual_hints", []))
            hint_count += len(data.get("tutorial_sequence", []))

            if hint_count < 50:
                self.warnings.append(
                    f"Only {hint_count} hints (expected 50+)"
                )

            self.stats["hints"] = hint_count

        except Exception as e:
            self.errors.append(f"Hint validation failed: {e}")

    def _report_results(self) -> bool:
        print("=" * 60)
        print("CONTENT VALIDATION REPORT")
        print("=" * 60)

        if self.stats:
            print("\nSTATISTICS:")
            for key, value in self.stats.items():
                print(f"  {key}: {value}")

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ! {warning}")

        print()

        if not self.errors:
            print("✓ All content files valid")
            return True
        else:
            print(f"✗ Validation failed with {len(self.errors)} errors")
            return False


def main():
    validator = ContentValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
