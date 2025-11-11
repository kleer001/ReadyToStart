import random

from src.core.config_loader import ConfigLoader
from src.core.game_state import GameState
from src.core.level_manager import LevelManager
from src.core.menu import MenuNode
from src.generation.compiler import SettingCompiler
from src.generation.dep_generator import DependencyGenerator
from src.generation.graph_analyzer import GraphAnalyzer
from src.generation.madlibs import MadLibsEngine
from src.generation.topology import TopologyConverter
from src.generation.wfc import WFCGenerator

MAX_GENERATION_ATTEMPTS = 5


class GenerationPipeline:
    def __init__(self, config_dir: str = "config/", difficulty=None, level_id: str | None = None):
        self.loader = ConfigLoader(config_dir)
        self.config = self.loader.load_generation_params(difficulty=difficulty)
        self.wfc_rules = self.loader.load_wfc_rules()
        self.templates = self.loader.load_templates()

        # Initialize level manager
        self.level_manager = LevelManager(config_dir)
        try:
            self.level_manager.load_levels()
            if level_id:
                self.level_manager.set_current_level(level_id)
        except FileNotFoundError:
            # If levels.ini doesn't exist, continue without levels
            pass

        # Apply level-specific configuration overrides
        max_items = 15
        current_level = self.level_manager.get_current_level()
        if current_level:
            max_items = current_level.max_items_per_page
            # Override generation config with level-specific parameters
            self.config.min_path_length = current_level.min_path_length
            self.config.max_depth = current_level.max_depth
            self.config.required_categories = current_level.required_categories
            self.config.gate_distribution = current_level.gate_distribution
            self.config.critical_ratio = current_level.critical_ratio
            self.config.decoy_ratio = current_level.decoy_ratio
            self.config.noise_ratio = current_level.noise_ratio

        self.madlibs = MadLibsEngine(self.templates, self.loader)
        self.compiler = SettingCompiler(self.config, self.madlibs, max_items_per_page=max_items)
        self.current_level_id = level_id

    def generate(self, seed: int | None = None, difficulty=None) -> GameState:
        if seed is not None:
            random.seed(seed)

        # Update difficulty if specified
        if difficulty is not None:
            self.config = self.loader.load_generation_params(difficulty=difficulty)

        for attempt in range(MAX_GENERATION_ATTEMPTS):
            try:
                return self._generate_once()
            except ValueError:
                if attempt == MAX_GENERATION_ATTEMPTS - 1:
                    raise
                continue

    def _generate_once(self) -> GameState:
        graph = self._generate_topology()
        game_state = self._create_game_state()
        critical_path = self._get_critical_path_from_graph(graph)

        self._populate_menus(graph, game_state, critical_path)
        self._add_dependencies(graph, game_state)
        self._set_starting_menu(graph, game_state)

        return game_state

    def _generate_topology(self):
        wfc = WFCGenerator(self.wfc_rules, self.config)
        grid = wfc.generate()

        converter = TopologyConverter(self.config)
        graph = converter.grid_to_graph(grid)

        if not converter.validate_graph():
            raise ValueError("Generated invalid graph")

        converter.prune_dead_ends()
        return graph

    def _create_game_state(self) -> GameState:
        return GameState()

    def _get_critical_path_from_graph(self, graph) -> list[str]:
        converter = TopologyConverter(self.config)
        converter.graph = graph
        return converter.get_critical_path()

    def _populate_menus(
        self, graph, game_state: GameState, critical_path: list[str]
    ) -> None:
        for node_id in graph.nodes():
            category = graph.nodes[node_id]["category"]
            is_critical = node_id in critical_path

            menu = MenuNode(
                id=node_id,
                category=category,
                connections=list(graph.successors(node_id)),
                level_id=self.current_level_id,
            )

            settings = self.compiler.compile_settings(node_id, category, is_critical)
            for setting in settings:
                # Set level_id on each setting
                setting.level_id = self.current_level_id
                menu.add_setting(setting)

            game_state.add_menu(menu)

    def _add_dependencies(self, graph, game_state: GameState) -> None:
        dep_gen = DependencyGenerator(graph, self.config, game_state.menus)
        dependencies = dep_gen.generate_dependencies()

        for setting_id, deps in dependencies.items():
            for dep in deps:
                game_state.resolver.add_dependency(setting_id, dep)

    def _set_starting_menu(self, graph, game_state: GameState) -> None:
        start_nodes = GraphAnalyzer.get_start_nodes(graph)
        game_state.current_menu = (
            start_nodes[0] if start_nodes else list(graph.nodes())[0]
        )
