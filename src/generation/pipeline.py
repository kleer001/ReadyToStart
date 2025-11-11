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
        # Check if current level has explicit menu structure (simple generation)
        current_level = self.level_manager.get_current_level()
        if current_level and current_level.menu_count > 0:
            # Use simple direct generation for levels with explicit menu counts
            return self._generate_simple(current_level)

        # Use procedural WFC generation for complex levels
        graph = self._generate_topology()
        game_state = self._create_game_state()
        critical_path = self._get_critical_path_from_graph(graph)

        self._populate_menus(graph, game_state, critical_path)
        self._add_dependencies(graph, game_state)
        self._set_starting_menu(graph, game_state)

        return game_state

    def _generate_simple(self, level) -> GameState:
        """Generate a simple game state with explicit menu structure.

        Used for introductory levels with fixed menu counts and settings.

        Args:
            level: Level configuration with menu_count and settings_per_menu

        Returns:
            GameState with simple menu structure
        """
        game_state = self._create_game_state()

        # Get available categories - use enabled_categories or fallback to tiered system
        if level.enabled_categories:
            categories = level.enabled_categories
        else:
            # Tiered category system: common → advanced → technical
            # Random order within each tier for variety
            import random

            tier_1_common = ["Audio", "Display", "Graphics", "User", "Interface"]
            tier_2_advanced = ["Performance", "System", "Hardware", "Network", "Device"]
            tier_3_technical = ["Security", "Privacy", "Data", "Storage", "File",
                               "Cache", "Memory", "Access", "Permission"]
            tier_4_specialized = ["Input", "Output", "Control", "Appearance", "Theme",
                                 "Color", "Visual"]

            # Shuffle within each tier for randomness
            random.shuffle(tier_1_common)
            random.shuffle(tier_2_advanced)
            random.shuffle(tier_3_technical)
            random.shuffle(tier_4_specialized)

            # Combine tiers in order (maintaining tier progression)
            categories = tier_1_common + tier_2_advanced + tier_3_technical + tier_4_specialized

        # Ensure we have enough unique categories for all menus
        if len(categories) < level.menu_count:
            # If we need more categories, generate unique names
            for i in range(len(categories), level.menu_count):
                categories.append(f"Settings_{i+1}")

        # Create menus based on level specification
        for i in range(level.menu_count):
            menu_id = f"menu_{i}"
            # Use unique category for each menu (no cycling)
            category = categories[i]
            settings_count = level.settings_per_menu[i] if i < len(level.settings_per_menu) else 5

            menu = MenuNode(
                id=menu_id,
                category=category,
                level_id=self.current_level_id,
            )

            # Generate EXACT number of settings specified
            settings = []
            while len(settings) < settings_count:
                # Generate a batch of settings
                batch = self.compiler.compile_settings(
                    f"{menu_id}_batch_{len(settings)}",
                    category,
                    is_critical=True
                )
                settings.extend(batch)

            # Trim to exact count
            settings = settings[:settings_count]

            # Renumber setting IDs to be sequential
            for idx, setting in enumerate(settings):
                setting.id = f"{menu_id}_setting_{idx}"
                setting.level_id = self.current_level_id
                menu.add_setting(setting)

            game_state.add_menu(menu)

        # Add simple dependencies based on dependency network
        if level.dependency_network and len(game_state.menus) > 0:
            self._add_simple_dependencies(game_state, level)

        # Set first menu as starting point
        game_state.current_menu = list(game_state.menus.keys())[0]

        return game_state

    def _add_simple_dependencies(self, game_state: GameState, level):
        """Add simple dependencies for explicit level structures.

        Args:
            game_state: Game state to add dependencies to
            level: Level configuration with dependency network
        """
        # For simple levels, just make some settings depend on others in a chain
        all_menus = list(game_state.menus.values())

        if len(all_menus) == 1:
            # Single menu: create simple chain of dependencies within the menu
            settings = all_menus[0].settings
            if len(settings) >= 2:
                from src.core.dependencies import SimpleDependency
                from src.core.enums import SettingState

                # First setting has no dependencies (already enabled)
                # Each subsequent setting depends on the previous one
                for i in range(1, len(settings)):
                    dep = SimpleDependency(
                        setting_id=settings[i-1].id,
                        required_state=SettingState.ENABLED
                    )
                    game_state.resolver.add_dependency(settings[i].id, dep)
        else:
            # Multiple menus: menus depend on each other
            from src.core.dependencies import SimpleDependency
            from src.core.enums import SettingState

            for i in range(1, len(all_menus)):
                # Settings in menu i depend on some settings in menu i-1
                prev_menu_settings = all_menus[i-1].settings
                curr_menu_settings = all_menus[i].settings

                if prev_menu_settings and curr_menu_settings:
                    # Make first setting of current menu depend on first setting of previous menu
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
