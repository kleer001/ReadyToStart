import pytest
from src.generation.compiler import SettingCompiler
from src.generation.madlibs import MadLibsEngine
from src.core.config_loader import ConfigLoader, GenerationConfig
from src.core.enums import SettingState, SettingType


class TestSettingCompiler:
    @pytest.fixture
    def config(self):
        return GenerationConfig(
            min_path_length=5,
            max_depth=15,
            required_categories=10,
            gate_distribution=0.3,
            critical_ratio=0.25,
            decoy_ratio=0.35,
            noise_ratio=0.40,
        )

    @pytest.fixture
    def config_loader(self):
        return ConfigLoader("config/")

    @pytest.fixture
    def madlibs(self, config_loader):
        templates = config_loader.load_templates()
        return MadLibsEngine(templates, config_loader)

    @pytest.fixture
    def compiler(self, config, madlibs):
        return SettingCompiler(config, madlibs)

    def test_compile_settings_correct_count(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", False)
        assert len(settings) == 8

    def test_compile_settings_uses_category_config(self, compiler):
        settings = compiler.compile_settings("node_1", "Graphics", False)
        assert len(settings) == 12

    def test_critical_settings_disabled(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", True)
        for setting in settings:
            assert setting.state == SettingState.DISABLED

    def test_non_critical_settings_enabled(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", False)
        for setting in settings:
            assert setting.state == SettingState.ENABLED

    def test_setting_has_unique_id(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", False)
        ids = [s.id for s in settings]
        assert len(ids) == len(set(ids))

    def test_setting_has_label(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", False)
        for setting in settings:
            assert len(setting.label) > 0

    def test_numeric_settings_have_ranges(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", False)
        for setting in settings:
            if setting.type in [SettingType.INTEGER, SettingType.FLOAT]:
                assert setting.min_value is not None
                assert setting.max_value is not None
                assert setting.min_value <= setting.max_value

    def test_default_value_for_boolean(self, compiler):
        value = compiler._default_value(SettingType.BOOLEAN)
        assert value is False

    def test_default_value_for_integer(self, compiler):
        value = compiler._default_value(SettingType.INTEGER)
        assert value == 0

    def test_default_value_for_float(self, compiler):
        value = compiler._default_value(SettingType.FLOAT)
        assert value == 0.0

    def test_default_value_for_string(self, compiler):
        value = compiler._default_value(SettingType.STRING)
        assert value == ""

    def test_choose_type_critical_favors_boolean(self, compiler):
        import random

        random.seed(42)
        types = [compiler._choose_type(True) for _ in range(100)]
        boolean_count = sum(1 for t in types if t == SettingType.BOOLEAN)
        assert boolean_count > 30

    def test_choose_type_non_critical_balanced(self, compiler):
        import random

        random.seed(42)
        types = [compiler._choose_type(False) for _ in range(100)]
        type_counts = {t: types.count(t) for t in SettingType}
        for count in type_counts.values():
            assert 15 <= count <= 35

    def test_unknown_category_uses_default_count(self, compiler):
        settings = compiler.compile_settings("node_1", "UnknownCategory", False)
        assert len(settings) == 8

    def test_setting_id_format(self, compiler):
        settings = compiler.compile_settings("node_1", "Audio", False)
        for i, setting in enumerate(settings):
            assert setting.id == f"node_1_setting_{i}"
