import pytest
from src.generation.pipeline import GenerationPipeline
from src.core.game_state import GameState
from src.core.menu import MenuNode


class TestGenerationPipeline:
    @pytest.fixture
    def pipeline(self):
        return GenerationPipeline("config/")

    def test_generate_returns_game_state(self, pipeline):
        state = pipeline.generate(seed=42)
        assert isinstance(state, GameState)

    def test_generate_creates_menus(self, pipeline):
        state = pipeline.generate(seed=42)
        assert len(state.menus) > 0

    def test_generate_creates_settings(self, pipeline):
        state = pipeline.generate(seed=42)
        assert len(state.settings) > 0

    def test_menus_have_settings(self, pipeline):
        state = pipeline.generate(seed=42)
        for menu in state.menus.values():
            assert len(menu.settings) > 0

    def test_menus_have_connections(self, pipeline):
        state = pipeline.generate(seed=42)
        menu_with_connections = any(
            len(m.connections) > 0 for m in state.menus.values()
        )
        assert menu_with_connections

    def test_current_menu_set(self, pipeline):
        state = pipeline.generate(seed=42)
        assert state.current_menu is not None
        assert state.current_menu in state.menus

    def test_dependencies_created(self, pipeline):
        state = pipeline.generate(seed=42)
        assert isinstance(state.resolver.dependencies, dict)

    def test_deterministic_with_seed(self, pipeline):
        state1 = pipeline.generate(seed=42)
        state2 = pipeline.generate(seed=42)

        assert len(state1.menus) == len(state2.menus)
        assert len(state1.settings) == len(state2.settings)

        for menu_id in state1.menus:
            if menu_id in state2.menus:
                menu1 = state1.menus[menu_id]
                menu2 = state2.menus[menu_id]
                assert menu1.category == menu2.category
                assert len(menu1.settings) == len(menu2.settings)

    def test_different_seeds_produce_different_results(self, pipeline):
        state1 = pipeline.generate(seed=42)
        state2 = pipeline.generate(seed=99)

        menus1 = set(state1.menus.keys())
        menus2 = set(state2.menus.keys())

        assert menus1 != menus2 or len(state1.menus) != len(state2.menus)

    def test_menus_are_menu_nodes(self, pipeline):
        state = pipeline.generate(seed=42)
        for menu in state.menus.values():
            assert isinstance(menu, MenuNode)

    def test_settings_have_labels(self, pipeline):
        state = pipeline.generate(seed=42)
        for setting in state.settings.values():
            assert len(setting.label) > 0

    def test_categories_from_wfc_rules(self, pipeline):
        state = pipeline.generate(seed=42)
        categories = {menu.category for menu in state.menus.values()}
        wfc_categories = set(pipeline.wfc_rules.keys())

        assert categories.issubset(wfc_categories)

    def test_pipeline_without_seed(self, pipeline):
        state = pipeline.generate()
        assert isinstance(state, GameState)
        assert len(state.menus) > 0

    def test_config_loaded(self, pipeline):
        assert pipeline.config is not None
        assert pipeline.config.min_path_length > 0
        assert pipeline.config.max_depth > 0

    def test_components_initialized(self, pipeline):
        assert pipeline.madlibs is not None
        assert pipeline.compiler is not None
        assert pipeline.wfc_rules is not None
        assert pipeline.templates is not None
