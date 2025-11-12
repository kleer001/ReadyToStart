import json
import random
from pathlib import Path

from src.core.config_loader import ConfigLoader
from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState
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

        self.level_manager = LevelManager(config_dir)
        try:
            self.level_manager.load_levels()
            if level_id:
                self.level_manager.set_current_level(level_id)
        except FileNotFoundError:
            pass

        max_items = 15
        current_level = self.level_manager.get_current_level()
        if current_level:
            max_items = current_level.max_items_per_page
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
        current_level = self.level_manager.get_current_level()
        if current_level and current_level.menu_count > 0:
            return self._generate_simple(current_level)

        graph = self._generate_topology()
        game_state = self._create_game_state()
        critical_path = self._get_critical_path_from_graph(graph)

        self._populate_menus(graph, game_state, critical_path)
        self._add_dependencies(graph, game_state)
        self._set_starting_menu(graph, game_state)

        return game_state

    def _load_tiered_categories(self) -> list[str]:
        categories_file = Path("data") / "menu_categories.json"

        if not categories_file.exists():
            tier_1 = ["audio", "graphics", "appearance", "notifications", "user_profile"]
            tier_2 = ["shortcuts", "gestures", "accessibility", "localization", "devices"]
            tier_3 = ["performance", "power_management", "storage", "updates", "startup"]
            tier_4 = ["network", "security", "privacy", "backup", "cloud_sync"]

            random.shuffle(tier_1)
            random.shuffle(tier_2)
            random.shuffle(tier_3)
            random.shuffle(tier_4)

            return tier_1 + tier_2 + tier_3 + tier_4

        with open(categories_file) as f:
            data = json.load(f)

        tiers = {2: [], 3: [], 4: [], 5: []}

        for category in data["categories"]:
            complexity = category["complexity"]
            category_id = category["id"]
            if complexity in tiers:
                tiers[complexity].append(category_id)

        all_categories = []
        for complexity_level in sorted(tiers.keys()):
            tier = tiers[complexity_level]
            random.shuffle(tier)
            all_categories.extend(tier)

        return all_categories

    def _generate_simple(self, level) -> GameState:
        game_state = self._create_game_state()

        if level.enabled_categories:
            categories = level.enabled_categories
        else:
            categories = self._load_tiered_categories()

        categories = [c.replace("_", " ").title() for c in categories]

        if len(categories) < level.menu_count:
            for i in range(len(categories), level.menu_count):
                categories.append(f"Settings_{i+1}")

        for i in range(level.menu_count):
            menu_id = f"menu_{i}"
            category = categories[i]
            settings_count = level.settings_per_menu[i] if i < len(level.settings_per_menu) else 5

            menu = MenuNode(
                id=menu_id,
                category=category,
                level_id=self.current_level_id,
            )

            settings = []
            while len(settings) < settings_count:
                batch = self.compiler.compile_settings(
                    f"{menu_id}_batch_{len(settings)}",
                    category,
                    is_critical=True
                )
                settings.extend(batch)

            settings = settings[:settings_count]

            for idx, setting in enumerate(settings):
                setting.id = f"{menu_id}_setting_{idx}"
                setting.level_id = self.current_level_id
                menu.add_setting(setting)

            game_state.add_menu(menu)

        if level.dependency_network and len(game_state.menus) > 0:
            self._add_simple_dependencies(game_state, level)

        game_state.current_menu = list(game_state.menus.keys())[0]

        return game_state

    def _add_simple_dependencies(self, game_state: GameState, level):
        all_menus = list(game_state.menus.values())

        if len(all_menus) == 1:
            settings = all_menus[0].settings
            if len(settings) >= 2:
                for i in range(1, len(settings)):
                    dep = SimpleDependency(
                        setting_id=settings[i-1].id,
                        required_state=SettingState.ENABLED
                    )
                    game_state.resolver.add_dependency(settings[i].id, dep)
        else:
            for i in range(1, len(all_menus)):
                prev_menu_settings = all_menus[i-1].settings
                curr_menu_settings = all_menus[i].settings

                if prev_menu_settings and curr_menu_settings:
                    dep = SimpleDependency(
                        setting_id=prev_menu_settings[0].id,
                        required_state=SettingState.ENABLED
                    )
                    game_state.resolver.add_dependency(curr_menu_settings[0].id, dep)

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
