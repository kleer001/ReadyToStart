"""Level management system for Ready to Start.

This module handles loading and managing discrete game levels with
specific constraints and configuration.
"""

import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Level:
    """Represents a discrete game level with specific constraints.

    Attributes:
        id: Unique identifier (e.g., "Level_1")
        name: Display name for the level
        description: Brief description of the level
        menu_count: Number of menu nodes to generate
        settings_per_menu: List of setting counts per menu (or single value for all)
        max_items_per_page: Maximum items allowed per menu page
        min_path_length: Minimum critical path length
        max_depth: Maximum graph depth
        required_categories: Number of required categories
        gate_distribution: Proportion of gated dependencies
        critical_ratio: Ratio of critical path settings
        decoy_ratio: Ratio of decoy settings
        noise_ratio: Ratio of noise settings
        enabled_categories: List of category names to use
        dependency_network: Dict mapping categories to their dependencies
    """

    id: str
    name: str
    description: str
    menu_count: int
    settings_per_menu: list[int]
    max_items_per_page: int = 15
    min_path_length: int = 3
    max_depth: int = 5
    required_categories: int = 5
    gate_distribution: float = 0.3
    critical_ratio: float = 0.25
    decoy_ratio: float = 0.35
    noise_ratio: float = 0.40
    enabled_categories: list[str] = field(default_factory=list)
    dependency_network: dict[str, list[str]] = field(default_factory=dict)


class LevelManager:
    """Manages game levels and their configurations.

    Loads level definitions from levels.ini and provides access to
    level-specific generation parameters and constraints.
    """

    def __init__(self, config_dir: str = "config/"):
        """Initialize the level manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.levels: dict[str, Level] = {}
        self.current_level_id: Optional[str] = None
        self.level_order: list[str] = []

    def load_levels(self) -> None:
        """Load all levels from configuration files.

        Tries meta_levels.ini first (single source of truth), falls back to levels.ini.

        Raises:
            FileNotFoundError: If no level configuration exists
            ValueError: If level configuration is invalid
        """
        meta_file = self.config_dir / "meta_levels.ini"
        levels_file = self.config_dir / "levels.ini"

        # Try meta_levels.ini first (preferred)
        if meta_file.exists():
            self._load_from_meta(meta_file)
        elif levels_file.exists():
            # Fall back to levels.ini
            self._load_from_levels_ini(levels_file)
        else:
            raise FileNotFoundError(f"No level configuration found in {self.config_dir}")

    def _load_from_meta(self, meta_file: Path) -> None:
        """Load levels from meta_levels.ini.

        Args:
            meta_file: Path to meta_levels.ini
        """
        parser = configparser.ConfigParser()
        parser.read(meta_file)

        if "Meta" not in parser:
            raise ValueError("meta_levels.ini must have a [Meta] section")

        meta_section = parser["Meta"]
        max_items = int(meta_section.get("max_items_per_page", "15"))

        # Parse level pattern
        levels_str = meta_section.get("levels", "")
        level_specs = [line.strip() for line in levels_str.strip().split("\n") if line.strip()]

        # Always add Level_0 (hub)
        hub_level = Level(
            id="Level_0",
            name="Main Menu Hub",
            description="Central hub - always accessible. Keep trying to Play!",
            menu_count=0,  # Hub has no gameplay
            settings_per_menu=[],
            max_items_per_page=max_items
        )
        self.levels["Level_0"] = hub_level
        self.level_order.append("Level_0")

        # Generate levels from pattern
        for idx, spec in enumerate(level_specs, start=1):
            level = self._parse_meta_spec(idx, spec, max_items)
            level_id = f"Level_{idx}"
            self.levels[level_id] = level
            self.level_order.append(level_id)

    def _parse_meta_spec(self, level_num: int, spec: str, max_items: int) -> Level:
        """Parse a level specification from meta format.

        Format: "menus:settings|settings|..."
        Example: "1:5" = 1 menu with 5 settings
        Example: "2:5|10" = 2 menus with 5 and 10 settings

        Args:
            level_num: Level number (1-indexed)
            spec: Level specification string
            max_items: Maximum items per page

        Returns:
            Level object
        """
        parts = spec.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid level spec: {spec}. Expected format 'menus:settings'")

        menu_count = int(parts[0])
        settings_parts = parts[1].split("|")
        settings_per_menu = [int(s) for s in settings_parts]

        # Calculate difficulty parameters based on level number
        min_path = min(level_num, 5)
        max_depth = min(level_num + 1, 7)
        gate_dist = min(0.1 + (level_num - 1) * 0.05, 0.5)
        critical_ratio = min(0.3 + (level_num - 1) * 0.03, 0.6)

        # Generate level name
        total_settings = sum(settings_per_menu)
        if menu_count == 1:
            name = f"Options - Level {level_num} ({total_settings} settings)"
        else:
            name = f"Options - Level {level_num} ({menu_count} menus)"

        return Level(
            id=f"Level_{level_num}",
            name=name,
            description=f"Level {level_num}: {menu_count} menu(s), {total_settings} settings total",
            menu_count=menu_count,
            settings_per_menu=settings_per_menu,
            max_items_per_page=max_items,
            min_path_length=min_path,
            max_depth=max_depth,
            required_categories=min(menu_count, 5),
            gate_distribution=gate_dist,
            critical_ratio=critical_ratio,
            decoy_ratio=0.35,
            noise_ratio=0.30,
            enabled_categories=[],  # Will use default categories
            dependency_network={}
        )

    def _load_from_levels_ini(self, levels_file: Path) -> None:
        """Load levels from legacy levels.ini format.

        Args:
            levels_file: Path to levels.ini
        """
        parser = configparser.ConfigParser()
        parser.read(levels_file)

        for section_name in sorted(parser.sections()):
            if not section_name.startswith("Level_"):
                continue

            section = parser[section_name]
            level = self._parse_level(section_name, section)
            self.levels[section_name] = level
            self.level_order.append(section_name)

    def _parse_level(self, level_id: str, section: configparser.SectionProxy) -> Level:
        """Parse a level configuration section.

        Args:
            level_id: The level identifier
            section: ConfigParser section containing level data

        Returns:
            Parsed Level object
        """
        # Parse settings_per_menu - can be single value or comma-separated list
        settings_str = section.get("settings_per_menu", "5")
        if "," in settings_str:
            settings_per_menu = [int(x.strip()) for x in settings_str.split(",")]
        else:
            # Single value applies to all menus
            count = int(settings_str)
            menu_count = section.getint("menu_count", 5)
            settings_per_menu = [count] * menu_count

        # Parse enabled categories
        enabled_cats_str = section.get("enabled_categories", "")
        enabled_categories = [c.strip() for c in enabled_cats_str.split(",") if c.strip()]

        # Parse dependency network
        dep_network_str = section.get("dependency_network", "")
        dependency_network = self._parse_dependency_network(dep_network_str)

        return Level(
            id=level_id,
            name=section.get("name", level_id),
            description=section.get("description", ""),
            menu_count=section.getint("menu_count", 5),
            settings_per_menu=settings_per_menu,
            max_items_per_page=section.getint("max_items_per_page", 15),
            min_path_length=section.getint("min_path_length", 3),
            max_depth=section.getint("max_depth", 5),
            required_categories=section.getint("required_categories", 5),
            gate_distribution=section.getfloat("gate_distribution", 0.3),
            critical_ratio=section.getfloat("critical_ratio", 0.25),
            decoy_ratio=section.getfloat("decoy_ratio", 0.35),
            noise_ratio=section.getfloat("noise_ratio", 0.40),
            enabled_categories=enabled_categories,
            dependency_network=dependency_network
        )

    def _parse_dependency_network(self, network_str: str) -> dict[str, list[str]]:
        """Parse dependency network string into dictionary.

        Format: "Category1:Dep1,Dep2; Category2:Dep3; Category3:"

        Args:
            network_str: Dependency network string

        Returns:
            Dict mapping category names to lists of dependencies
        """
        if not network_str.strip():
            return {}

        network = {}
        for pair in network_str.split(";"):
            pair = pair.strip()
            if not pair or ":" not in pair:
                continue

            category, deps_str = pair.split(":", 1)
            category = category.strip()

            if deps_str.strip():
                deps = [d.strip() for d in deps_str.split(",") if d.strip()]
            else:
                deps = []

            network[category] = deps

        return network

    def get_level(self, level_id: str) -> Optional[Level]:
        """Get a level by its ID.

        Args:
            level_id: Level identifier

        Returns:
            Level object or None if not found
        """
        return self.levels.get(level_id)

    def set_current_level(self, level_id: str) -> bool:
        """Set the current active level.

        Args:
            level_id: Level identifier to activate

        Returns:
            True if level was set, False if level not found
        """
        if level_id not in self.levels:
            return False

        self.current_level_id = level_id
        return True

    def get_current_level(self) -> Optional[Level]:
        """Get the currently active level.

        Returns:
            Current Level object or None
        """
        if self.current_level_id:
            return self.levels.get(self.current_level_id)
        return None

    def get_next_level(self) -> Optional[Level]:
        """Get the next level in sequence.

        Returns:
            Next Level object or None if at end
        """
        if not self.current_level_id:
            return None

        try:
            current_idx = self.level_order.index(self.current_level_id)
            if current_idx + 1 < len(self.level_order):
                next_id = self.level_order[current_idx + 1]
                return self.levels[next_id]
        except (ValueError, IndexError):
            pass

        return None

    def get_all_levels(self) -> list[Level]:
        """Get all levels in order.

        Returns:
            List of all Level objects
        """
        return [self.levels[level_id] for level_id in self.level_order]

    def get_level_count(self) -> int:
        """Get total number of levels.

        Returns:
            Number of levels loaded
        """
        return len(self.levels)
