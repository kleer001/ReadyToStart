import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Level:
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
    def __init__(self, config_dir: str = "config/"):
        self.config_dir = Path(config_dir)
        self.levels: dict[str, Level] = {}
        self.current_level_id: Optional[str] = None
        self.level_order: list[str] = []

    def load_levels(self) -> None:
        meta_file = self.config_dir / "meta_levels.ini"
        if not meta_file.exists():
            raise FileNotFoundError(f"meta_levels.ini not found in {self.config_dir}")
        self._load_from_meta(meta_file)

    def _load_from_meta(self, meta_file: Path) -> None:
        parser = configparser.ConfigParser()
        parser.read(meta_file)

        if "Algorithm" in parser:
            self._load_algorithmic(parser["Algorithm"])
        elif "Meta" in parser:
            self._load_explicit(parser["Meta"])
        else:
            raise ValueError("meta_levels.ini must have either [Algorithm] or [Meta] section")

    def _load_algorithmic(self, algo_section: configparser.SectionProxy) -> None:
        import random
        total_levels = int(algo_section.get("total_levels", "10"))
        max_settings_per_menu = int(algo_section.get("max_settings_per_menu", "15"))
        base_settings = int(algo_section.get("base_settings", "5"))
        base_menus = int(algo_section.get("base_menus", "1"))
        settings_growth = int(algo_section.get("settings_growth", "2"))
        levels_per_new_menu = int(algo_section.get("levels_per_new_menu", "3"))
        variation = float(algo_section.get("variation", "0.2"))

        hub_level = Level(
            id="Level_0",
            name="Main Menu Hub",
            description="Central hub - always accessible. Keep trying to Play!",
            menu_count=0,
            settings_per_menu=[],
            max_items_per_page=max_settings_per_menu
        )
        self.levels["Level_0"] = hub_level
        self.level_order.append("Level_0")

        for level_num in range(1, total_levels + 1):
            menus = base_menus + (level_num - 1) // levels_per_new_menu
            total_settings = base_settings + (level_num - 1) * settings_growth

            settings_per_menu = self._distribute_settings(
                total_settings,
                menus,
                max_settings_per_menu,
                variation
            )

            level = self._create_level_from_algorithm(
                level_num,
                menus,
                settings_per_menu,
                max_settings_per_menu
            )

            level_id = f"Level_{level_num}"
            self.levels[level_id] = level
            self.level_order.append(level_id)

    def _distribute_settings(
        self,
        total: int,
        menus: int,
        max_per_menu: int,
        variation: float
    ) -> list[int]:
        import random

        base_per_menu = total // menus
        remainder = total % menus

        if base_per_menu > max_per_menu:
            needed_menus = (total + max_per_menu - 1) // max_per_menu
            menus = needed_menus
            base_per_menu = total // menus
            remainder = total % menus

        distribution = [base_per_menu] * menus

        for i in range(remainder):
            distribution[i] += 1

        if variation > 0:
            for i in range(len(distribution)):
                vary_amount = int(distribution[i] * variation)
                if vary_amount > 0:
                    distribution[i] += random.randint(-vary_amount, vary_amount)
                    distribution[i] = max(1, min(max_per_menu, distribution[i]))

        current_total = sum(distribution)
        if current_total != total:
            diff = total - current_total
            distribution[0] = max(1, distribution[0] + diff)
            distribution[0] = min(max_per_menu, distribution[0])

        return distribution

    def _create_level_from_algorithm(
        self,
        level_num: int,
        menus: int,
        settings_per_menu: list[int],
        max_items: int
    ) -> Level:
        min_path = min(level_num, 5)
        max_depth = min(level_num + 1, 7)
        gate_dist = min(0.1 + (level_num - 1) * 0.05, 0.5)
        critical_ratio = min(0.3 + (level_num - 1) * 0.03, 0.6)

        total_settings = sum(settings_per_menu)
        if menus == 1:
            name = f"Options - Level {level_num} ({total_settings} settings)"
        else:
            name = f"Options - Level {level_num} ({menus} menus)"

        return Level(
            id=f"Level_{level_num}",
            name=name,
            description=f"Level {level_num}: {menus} menu(s), {total_settings} settings total",
            menu_count=menus,
            settings_per_menu=settings_per_menu,
            max_items_per_page=max_items,
            min_path_length=min_path,
            max_depth=max_depth,
            required_categories=min(menus, 5),
            gate_distribution=gate_dist,
            critical_ratio=critical_ratio,
            decoy_ratio=0.35,
            noise_ratio=0.30,
            enabled_categories=[],
            dependency_network={}
        )

    def _load_explicit(self, meta_section: configparser.SectionProxy) -> None:
        max_items = int(meta_section.get("max_items_per_page", "15"))
        levels_str = meta_section.get("levels", "")
        level_specs = [line.strip() for line in levels_str.strip().split("\n") if line.strip()]

        hub_level = Level(
            id="Level_0",
            name="Main Menu Hub",
            description="Central hub - always accessible. Keep trying to Play!",
            menu_count=0,
            settings_per_menu=[],
            max_items_per_page=max_items
        )
        self.levels["Level_0"] = hub_level
        self.level_order.append("Level_0")

        for idx, spec in enumerate(level_specs, start=1):
            level = self._parse_meta_spec(idx, spec, max_items)
            level_id = f"Level_{idx}"
            self.levels[level_id] = level
            self.level_order.append(level_id)

    def _parse_meta_spec(self, level_num: int, spec: str, max_items: int) -> Level:
        parts = spec.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid level spec: {spec}. Expected format 'menus:settings'")

        menu_count = int(parts[0])
        settings_parts = parts[1].split("|")
        settings_per_menu = [int(s) for s in settings_parts]

        min_path = min(level_num, 5)
        max_depth = min(level_num + 1, 7)
        gate_dist = min(0.1 + (level_num - 1) * 0.05, 0.5)
        critical_ratio = min(0.3 + (level_num - 1) * 0.03, 0.6)

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
            enabled_categories=[],
            dependency_network={}
        )


    def get_level(self, level_id: str) -> Optional[Level]:
        return self.levels.get(level_id)

    def set_current_level(self, level_id: str) -> bool:
        if level_id not in self.levels:
            return False
        self.current_level_id = level_id
        return True

    def get_current_level(self) -> Optional[Level]:
        if self.current_level_id:
            return self.levels.get(self.current_level_id)
        return None

    def get_next_level(self) -> Optional[Level]:
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
        return [self.levels[level_id] for level_id in self.level_order]

    def get_level_count(self) -> int:
        return len(self.levels)
