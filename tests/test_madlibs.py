import pytest
from src.generation.madlibs import MadLibsEngine
from src.core.config_loader import ConfigLoader


class TestMadLibsEngine:
    @pytest.fixture
    def config_loader(self):
        return ConfigLoader("config/")

    @pytest.fixture
    def templates(self):
        return {
            "requirement_templates": [
                "{category} requires {requirement} to be {state}",
                "Cannot {action} while {condition}",
            ],
            "error_templates": [
                "Error: {setting} incompatible with {other_setting}",
                "Warning: {action} may cause {consequence}",
            ],
            "setting_labels": [
                "{category} {descriptor}",
                "Enable {category} {feature}",
            ],
        }

    @pytest.fixture
    def engine(self, templates, config_loader):
        return MadLibsEngine(templates, config_loader)

    def test_fill_template_with_context(self, engine):
        template = "Hello {name}, you are {age} years old"
        context = {"name": "Alice", "age": "30"}
        result = engine.fill_template(template, context)
        assert result == "Hello Alice, you are 30 years old"

    def test_fill_template_with_vocabulary(self, engine):
        template = "Please {action} the system"
        result = engine.fill_template(template)
        assert "Please" in result
        assert "the system" in result

    def test_fill_template_missing_placeholder(self, engine):
        template = "Unknown {unknown_placeholder}"
        result = engine.fill_template(template)
        assert "[unknown_placeholder]" in result

    def test_fill_template_context_overrides_vocabulary(self, engine):
        template = "Must {action}"
        context = {"action": "custom_action"}
        result = engine.fill_template(template, context)
        assert result == "Must custom_action"

    def test_generate_requirement(self, engine):
        result = engine.generate_requirement("node_1", "Audio")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Audio" in result or "Cannot" in result

    def test_generate_error(self, engine):
        result = engine.generate_error("setting_1")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Error" in result or "Warning" in result

    def test_generate_setting_label(self, engine):
        result = engine.generate_setting_label("Graphics", 5)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Graphics" in result or "Enable" in result

    def test_vocabulary_loaded(self, engine):
        assert "action" in engine.vocab
        assert "condition" in engine.vocab
        assert "consequence" in engine.vocab
        assert len(engine.vocab["action"]) > 0

    def test_select_template_missing_type(self, engine):
        template = engine._select_template("nonexistent_type")
        assert template == "{category} {setting}"

    def test_multiple_same_placeholders(self, engine):
        template = "{action} and {action} again"
        context = {"action": "test"}
        result = engine.fill_template(template, context)
        assert result == "test and test again"

    def test_empty_context(self, engine):
        template = "Test {action}"
        result = engine.fill_template(template, {})
        assert "Test" in result

    def test_deterministic_with_seed(self, engine, templates, config_loader):
        import random

        random.seed(42)
        engine1 = MadLibsEngine(templates, config_loader)
        result1 = engine1.generate_requirement("node_1", "Audio")

        random.seed(42)
        engine2 = MadLibsEngine(templates, config_loader)
        result2 = engine2.generate_requirement("node_1", "Audio")

        assert result1 == result2
