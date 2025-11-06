import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class GenerationConfig:
    min_path_length: int
    max_depth: int
    required_categories: int
    gate_distribution: float
    critical_ratio: float
    decoy_ratio: float
    noise_ratio: float


class ConfigLoader:
    def __init__(self, config_dir: str = "config/"):
        self.config_dir = Path(config_dir)
        self.parser = configparser.ConfigParser()

    def load_generation_params(self) -> GenerationConfig:
        self._load_file("generation.ini")
        section = self.parser["generation"]
        return GenerationConfig(
            min_path_length=section.getint("min_path_length"),
            max_depth=section.getint("max_depth"),
            required_categories=section.getint("required_categories"),
            gate_distribution=section.getfloat("gate_distribution"),
            critical_ratio=section.getfloat("critical_ratio"),
            decoy_ratio=section.getfloat("decoy_ratio"),
            noise_ratio=section.getfloat("noise_ratio"),
        )

    def load_wfc_rules(self) -> Dict[str, Dict[str, List[str]]]:
        self._load_file("wfc_rules.ini")
        rules = {}
        for section in self.parser.sections():
            rules[section] = {
                "connections": self._parse_list(self.parser[section]["connections"]),
                "requires": self._parse_list(
                    self.parser[section].get("requires", "")
                ),
            }
        return rules

    def load_templates(self) -> Dict[str, List[str]]:
        self._load_file("templates.ini")
        return self._parse_sections()

    def load_categories(self) -> Dict[str, Dict]:
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

    def load_vocabulary(self) -> Dict[str, List[str]]:
        self._load_file("vocabulary.ini")
        return self._parse_sections()

    def _load_file(self, filename: str) -> None:
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        self.parser = configparser.ConfigParser()
        self.parser.read(filepath)

    def _parse_list(self, value: str) -> List[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    def _parse_sections(self) -> Dict[str, List[str]]:
        return {
            section: [self.parser[section][key] for key in self.parser[section]]
            for section in self.parser.sections()
        }
