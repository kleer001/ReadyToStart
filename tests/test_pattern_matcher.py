import pytest

from src.generation.pattern_matcher import DependencyPatternMatcher


class TestDependencyPatternMatcher:
    @pytest.fixture
    def matcher(self, tmp_path):
        patterns_file = tmp_path / "test_patterns.json"
        patterns_file.write_text(
            """{
            "patterns": [
                {
                    "name": "master_enable",
                    "applies_to": ["all_categories"],
                    "weight": 1.0
                },
                {
                    "name": "advanced_gate",
                    "applies_to": ["all_categories"],
                    "weight": 0.8
                }
            ],
            "pattern_probabilities": {
                "complexity_3": {
                    "master_enable": 0.95,
                    "advanced_gate": 0.6
                }
            },
            "density_modifiers": {
                "low": 0.5,
                "medium": 1.0,
                "high": 1.5
            },
            "special_category_rules": {}
        }"""
        )
        return DependencyPatternMatcher(str(patterns_file))

    def test_load_patterns(self, matcher):
        assert len(matcher.patterns) == 2
        assert matcher.patterns[0]["name"] == "master_enable"

    def test_find_applicable_patterns_all_categories(self, matcher):
        category_info = {"id": "audio", "complexity": 3, "dependency_density": "medium"}

        applicable = matcher.find_applicable_patterns(category_info)
        assert len(applicable) == 2

    def test_pattern_applies_to_category(self, matcher):
        category_info = {"id": "audio", "complexity": 3, "dependency_density": "medium"}

        pattern = matcher.patterns[0]
        applies = matcher._pattern_applies_to_category(pattern, category_info)
        assert applies is True

    def test_apply_master_enable_pattern(self, matcher):
        settings = [
            {"id": "audio_enable", "type": "boolean"},
            {"id": "audio_volume", "type": "integer"},
            {"id": "audio_advanced_mode", "type": "boolean"},
        ]

        pattern = matcher.patterns[0]
        dependencies = matcher.apply_pattern(pattern, settings, "audio")

        assert len(dependencies) > 0
        assert any(dep[0] == "audio_volume" for dep in dependencies)

    def test_apply_advanced_gate_pattern(self, matcher):
        settings = [
            {"id": "audio_advanced_mode", "type": "boolean"},
            {"id": "audio_advanced_eq", "type": "boolean"},
        ]

        pattern = matcher.patterns[1]
        dependencies = matcher.apply_pattern(pattern, settings, "audio")

        assert any(dep[0] == "audio_advanced_eq" for dep in dependencies)

    def test_select_patterns_for_category(self, matcher):
        category_info = {
            "id": "audio",
            "complexity": 3,
            "dependency_density": "medium",
        }

        selected = matcher.select_patterns_for_category(category_info)
        assert isinstance(selected, list)


class TestPatternApplications:
    @pytest.fixture
    def matcher_with_all_patterns(self, tmp_path):
        patterns_file = tmp_path / "full_patterns.json"
        patterns_file.write_text(
            """{
            "patterns": [
                {"name": "master_enable", "applies_to": ["all_categories"]},
                {"name": "chain_dependency", "applies_to": ["all_categories"]},
                {"name": "sequential_unlock", "applies_to": ["all_categories"]},
                {"name": "value_threshold", "applies_to": ["all_categories"]}
            ],
            "pattern_probabilities": {"complexity_3": {}},
            "density_modifiers": {"medium": 1.0},
            "special_category_rules": {}
        }"""
        )
        return DependencyPatternMatcher(str(patterns_file))

    def test_apply_chain_pattern(self, matcher_with_all_patterns):
        settings = [
            {"id": f"test_setting_{i}", "type": "boolean"} for i in range(5)
        ]

        pattern = {"name": "chain_dependency"}
        dependencies = matcher_with_all_patterns.apply_pattern(
            pattern, settings, "test"
        )

        assert len(dependencies) >= 2

    def test_apply_sequential_pattern(self, matcher_with_all_patterns):
        settings = [
            {"id": f"test_setting_{i}", "type": "boolean"} for i in range(4)
        ]

        pattern = {"name": "sequential_unlock"}
        dependencies = matcher_with_all_patterns.apply_pattern(
            pattern, settings, "test"
        )

        assert len(dependencies) >= 1

    def test_apply_value_threshold_pattern(self, matcher_with_all_patterns):
        settings = [
            {"id": "test_level", "type": "integer", "min_value": 0, "max_value": 100},
            {
                "id": "test_advanced",
                "type": "integer",
                "min_value": 0,
                "max_value": 100,
            },
        ]

        pattern = {"name": "value_threshold"}
        dependencies = matcher_with_all_patterns.apply_pattern(
            pattern, settings, "test"
        )

        assert any(dep[1] == "value" for dep in dependencies)
