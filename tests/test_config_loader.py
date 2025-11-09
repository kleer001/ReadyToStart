import pytest
from pathlib import Path
from src.core.config_loader import ConfigLoader, GenerationConfig


class TestConfigLoader:
    @pytest.fixture
    def loader(self):
        return ConfigLoader("config/")

    def test_load_generation_params(self, loader):
        config = loader.load_generation_params()
        assert isinstance(config, GenerationConfig)
        assert config.min_path_length == 5
        assert config.max_depth == 15
        assert config.required_categories == 10
        assert config.gate_distribution == 0.3
        assert config.critical_ratio == 0.25
        assert config.decoy_ratio == 0.35
        assert config.noise_ratio == 0.40

    def test_load_wfc_rules(self, loader):
        rules = loader.load_wfc_rules()
        assert "Audio" in rules
        assert "Graphics" in rules
        assert rules["Audio"]["connections"] == ["Graphics", "User", "Network"]
        assert rules["Audio"]["requires"] == []
        assert rules["Graphics"]["requires"] == ["Audio"]

    def test_load_templates(self, loader):
        templates = loader.load_templates()
        assert "requirement_templates" in templates
        assert "error_templates" in templates
        assert "setting_labels" in templates
        assert len(templates["requirement_templates"]) > 0
        assert len(templates["error_templates"]) > 0

    def test_load_categories(self, loader):
        categories = loader.load_categories()
        assert "Audio" in categories
        assert categories["Audio"]["setting_count"] == 8
        assert categories["Audio"]["complexity"] == 2
        assert categories["Audio"]["dependencies"] == []
        assert categories["Graphics"]["dependencies"] == ["Audio"]

    def test_load_vocabulary(self, loader):
        vocab = loader.load_vocabulary()
        assert "action" in vocab
        assert "condition" in vocab
        assert "consequence" in vocab
        assert len(vocab["action"]) > 0
        assert "configure" in vocab["action"]

    def test_missing_file_raises_error(self):
        loader = ConfigLoader("nonexistent/")
        with pytest.raises(FileNotFoundError):
            loader.load_generation_params()

    def test_parse_empty_list(self, loader):
        result = loader._parse_list("")
        assert result == []
        result = loader._parse_list("  ")
        assert result == []

    def test_parse_list_with_spaces(self, loader):
        result = loader._parse_list("item1, item2  , item3")
        assert result == ["item1", "item2", "item3"]

    def test_load_file_creates_parser_state(self, loader):
        loader._load_file("generation.ini")
        assert "generation" in loader.parser.sections()
