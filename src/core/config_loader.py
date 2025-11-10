import configparser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DifficultyTier(Enum):
    """Difficulty tiers for dependency generation."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class DifficultyConfig:
    """Configuration for dependency difficulty per tier."""
    min_dependencies: int = 1
    max_dependencies: int = 3
    mean_dependencies: float = 2.0
    std_dev: float = 0.5

    @staticmethod
    def for_tier(tier: DifficultyTier, total_settings: int) -> "DifficultyConfig":
        """Create difficulty config for a specific tier.

        Args:
            tier: Difficulty tier
            total_settings: Total number of settings (used for cap calculation)

        Returns:
            DifficultyConfig with appropriate parameters
        """
        # Cap max at half of total settings or 20, whichever is lower
        absolute_max = min(total_settings // 2, 20)

        if tier == DifficultyTier.EASY:
            max_deps = min(3, absolute_max)
            mean = 1.5
            std_dev = 0.7
        elif tier == DifficultyTier.MEDIUM:
            max_deps = min(6, absolute_max)
            mean = 3.0
            std_dev = 1.2
        else:  # HARD
            max_deps = min(12, absolute_max)
            mean = 5.0
            std_dev = 2.0

        return DifficultyConfig(
            min_dependencies=1,
            max_dependencies=max_deps,
            mean_dependencies=mean,
            std_dev=std_dev
        )


@dataclass
class GenerationConfig:
    min_path_length: int
    max_depth: int
    required_categories: int
    gate_distribution: float
    critical_ratio: float
    decoy_ratio: float
    noise_ratio: float
    difficulty_tier: DifficultyTier = DifficultyTier.MEDIUM


class ConfigLoader:
    def __init__(self, config_dir: str = "config/"):
        self.config_dir = Path(config_dir)
        self.parser = configparser.ConfigParser()

    def load_generation_params(self, difficulty: DifficultyTier | None = None) -> GenerationConfig:
        self._load_file("generation.ini")
        section = self.parser["generation"]

        # Allow override or read from config
        if difficulty is None:
            difficulty_str = section.get("difficulty_tier", "medium")
            difficulty = DifficultyTier(difficulty_str)

        return GenerationConfig(
            min_path_length=section.getint("min_path_length"),
            max_depth=section.getint("max_depth"),
            required_categories=section.getint("required_categories"),
            gate_distribution=section.getfloat("gate_distribution"),
            critical_ratio=section.getfloat("critical_ratio"),
            decoy_ratio=section.getfloat("decoy_ratio"),
            noise_ratio=section.getfloat("noise_ratio"),
            difficulty_tier=difficulty
        )

    def load_wfc_rules(self) -> dict[str, dict[str, list[str]]]:
        self._load_file("wfc_rules.ini")
        rules = {}
        for section in self.parser.sections():
            rules[section] = {
                "connections": self._parse_list(self.parser[section]["connections"]),
                "requires": self._parse_list(self.parser[section].get("requires", "")),
            }
        return rules

    def load_templates(self) -> dict[str, list[str]]:
        self._load_file("templates.ini")
        return self._parse_sections()

    def load_categories(self) -> dict[str, dict]:
        self._load_file("categories.ini")
        config = {}
        for section in self.parser.sections():
            config[section] = {
                "setting_count": self.parser[section].getint("setting_count"),
                "complexity": self.parser[section].getint("complexity"),
                "dependencies": self._parse_list(
                    self.parser[section].get("dependencies", "")
                ),
            }
        return config

    def load_vocabulary(self) -> dict[str, list[str]]:
        self._load_file("vocabulary.ini")
        return self._parse_sections()

    def _load_file(self, filename: str) -> None:
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        self.parser = configparser.ConfigParser()
        self.parser.read(filepath)

    def _parse_list(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    def _parse_sections(self) -> dict[str, list[str]]:
        return {
            section: [self.parser[section][key] for key in self.parser[section]]
            for section in self.parser.sections()
        }
