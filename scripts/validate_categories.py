#!/usr/bin/env python3

import json
import sys
from pathlib import Path


class CategoryValidator:
    REQUIRED_FIELDS = [
        "id",
        "name",
        "complexity",
        "setting_count_range",
        "dependency_density",
        "theme",
        "subcategories",
    ]

    VALID_COMPLEXITY = range(1, 6)
    EXPECTED_CATEGORY_COUNT = 32

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        if not self._load_file():
            return False

        self._validate_category_count()
        self._validate_each_category()
        self._check_unique_ids()
        self._check_unique_themes()

        return self._report_results()

    def _load_file(self) -> bool:
        try:
            with open(self.filepath) as f:
                self.data = json.load(f)
                self.categories = self.data.get("categories", [])
            return True
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.filepath}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

    def _validate_category_count(self) -> None:
        count = len(self.categories)
        if count != self.EXPECTED_CATEGORY_COUNT:
            self.errors.append(
                f"Expected {self.EXPECTED_CATEGORY_COUNT} categories, found {count}"
            )

    def _validate_each_category(self) -> None:
        for i, category in enumerate(self.categories):
            self._validate_category_fields(i, category)
            self._validate_category_values(i, category)

    def _validate_category_fields(self, index: int, category: dict) -> None:
        cat_id = category.get("id", f"category_{index}")

        for field in self.REQUIRED_FIELDS:
            if field not in category:
                self.errors.append(f"Category {cat_id} missing field: {field}")

    def _validate_category_values(self, index: int, category: dict) -> None:
        cat_id = category.get("id", f"category_{index}")

        complexity = category.get("complexity")
        if complexity not in self.VALID_COMPLEXITY:
            self.errors.append(
                f"Category {cat_id} has invalid complexity: {complexity}"
            )

        setting_range = category.get("setting_count_range", [])
        if not self._validate_range(setting_range):
            self.errors.append(
                f"Category {cat_id} has invalid setting_count_range: {setting_range}"
            )

        subcategories = category.get("subcategories", [])
        if not isinstance(subcategories, list) or len(subcategories) == 0:
            self.warnings.append(f"Category {cat_id} has no subcategories")

    def _validate_range(self, range_value: list) -> bool:
        if not isinstance(range_value, list) or len(range_value) != 2:
            return False

        min_val, max_val = range_value
        return isinstance(min_val, int) and isinstance(max_val, int) and min_val < max_val and min_val > 0

    def _check_unique_ids(self) -> None:
        ids = [cat.get("id") for cat in self.categories]
        duplicates = [id for id in ids if ids.count(id) > 1]

        if duplicates:
            unique_dupes = list(set(duplicates))
            self.errors.append(f"Duplicate category IDs: {unique_dupes}")

    def _check_unique_themes(self) -> None:
        themes = [cat.get("theme") for cat in self.categories]
        theme_counts = {}

        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        duplicates = [
            theme for theme, count in theme_counts.items() if count > 1
        ]

        if duplicates:
            self.warnings.append(f"Duplicate themes: {duplicates}")

    def _report_results(self) -> bool:
        if self.errors:
            print("VALIDATION ERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print("\nVALIDATION WARNINGS:")
            for warning in self.warnings:
                print(f"  ! {warning}")

        if not self.errors:
            print(f"✓ All {len(self.categories)} categories valid")
            return True

        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_categories.py <categories.json>")
        sys.exit(1)

    validator = CategoryValidator(sys.argv[1])
    success = validator.validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
