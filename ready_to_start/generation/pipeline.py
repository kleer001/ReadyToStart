import random

from ready_to_start.core.config_loader import ConfigLoader
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.generation.compiler import SettingCompiler
from ready_to_start.generation.dep_generator import DependencyGenerator
from ready_to_start.generation.madlibs import MadLibsEngine
from ready_to_start.generation.topology import TopologyConverter
from ready_to_start.generation.wfc import WFCGenerator


class GenerationPipeline:
    def __init__(self, config_dir: str = "config/"):
        self.loader = ConfigLoader(config_dir)
        self.config = self.loader.load_generation_params()
        self.wfc_rules = self.loader.load_wfc_rules()
        self.templates = self.loader.load_templates()

        self.madlibs = MadLibsEngine(self.templates, self.loader)
        self.compiler = SettingCompiler(self.config, self.madlibs)

    def _generate_once(self) -> GameState:
        wfc = WFCGenerator(self.wfc_rules, self.config)
        grid = wfc.generate()

        converter = TopologyConverter(self.config)
        graph = converter.grid_to_graph(grid)

        if not converter.validate_graph():
            raise ValueError("Generated invalid graph")

        converter.prune_dead_ends()

        game_state = GameState()
        critical_path = converter.get_critical_path()

        for node_id in graph.nodes():
            category = graph.nodes[node_id]["category"]
            is_critical = node_id in critical_path

            menu = MenuNode(
                id=node_id,
                category=category,
                connections=list(graph.successors(node_id)),
            )

            settings = self.compiler.compile_settings(node_id, category, is_critical)
            for setting in settings:
                menu.add_setting(setting)

            game_state.add_menu(menu)

        dep_gen = DependencyGenerator(graph, self.config, game_state.menus)
        dependencies = dep_gen.generate_dependencies()

        for setting_id, deps in dependencies.items():
            for dep in deps:
                game_state.resolver.add_dependency(setting_id, dep)

        start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        game_state.current_menu = (
            start_nodes[0] if start_nodes else list(graph.nodes())[0]
        )

        return game_state

    def generate(self, seed: int | None = None) -> GameState:
        if seed is not None:
            random.seed(seed)

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                return self._generate_once()
            except ValueError:
                if attempt == max_attempts - 1:
                    raise
                continue
