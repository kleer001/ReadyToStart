#!/usr/bin/env python3

import json
import random
from pathlib import Path
from typing import Any


class TemplateGenerator:
    def __init__(self, categories_file: str, pools_file: str):
        with open(categories_file) as f:
            self.categories = json.load(f)["categories"]
        with open(pools_file) as f:
            self.pools = json.load(f)

    def generate_all(self, output_dir: str) -> None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for category in self.categories:
            templates = self._generate_category_templates(category)
            output_file = output_path / f"{category['id']}_templates.json"

            with open(output_file, "w") as f:
                json.dump(templates, f, indent=2)

            print(f"Generated {category['id']}_templates.json")

    def _generate_category_templates(self, category: dict[str, Any]) -> dict:
        theme = category["theme"]
        complexity = category["complexity"]

        base_templates = self._create_base_templates(category["id"])
        themed_templates = self._create_themed_templates(category, theme)
        value_templates = self._create_value_templates(category["id"], complexity)

        all_templates = base_templates + themed_templates + value_templates

        return {
            "category": category["id"],
            "name": category["name"],
            "templates": all_templates,
            "word_pools": self._extract_word_pools(theme),
        }

    def _create_base_templates(self, category_id: str) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_enable",
                "type": "boolean",
                "label_template": "Enable {category_name}",
                "default_value": False,
                "importance": "critical",
                "dependency_likelihood": 0.95,
            },
            {
                "id_pattern": f"{category_id}_advanced_mode",
                "type": "boolean",
                "label_template": "Show Advanced Options",
                "default_value": False,
                "importance": "medium",
                "dependency_likelihood": 0.8,
            },
        ]

    def _create_themed_templates(
        self, category: dict[str, Any], theme: str
    ) -> list[dict]:
        generators = {
            "sound_configuration": self._audio_templates,
            "visual_configuration": self._graphics_templates,
            "connectivity": self._network_templates,
            "protection": self._security_templates,
            "optimization": self._performance_templates,
            "vm_configuration": self._virtualization_templates,
            "development": self._developer_templates,
            "quantum_computing": self._quantum_templates,
        }

        generator = generators.get(theme, self._generic_templates)
        return generator(category["id"], category)

    def _audio_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_volume",
                "type": "integer",
                "label_template": "{adjective} Volume",
                "min_value": 0,
                "max_value": 100,
                "default_value": 50,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_device",
                "type": "string",
                "label_template": "{device} Selection",
                "options": ["default", "speakers", "headphones", "hdmi", "optical"],
                "default_value": "default",
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_sample_rate",
                "type": "integer",
                "label_template": "Sample Rate",
                "min_value": 22050,
                "max_value": 192000,
                "default_value": 44100,
                "importance": "medium",
            },
            {
                "id_pattern": f"{category_id}_channels",
                "type": "string",
                "label_template": "Channel Configuration",
                "options": ["mono", "stereo", "surround_5_1", "surround_7_1", "atmos"],
                "default_value": "stereo",
                "importance": "medium",
            },
        ]

    def _graphics_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_resolution",
                "type": "string",
                "label_template": "Screen Resolution",
                "options": [
                    "1920x1080",
                    "2560x1440",
                    "3840x2160",
                    "5120x2880",
                    "7680x4320",
                ],
                "default_value": "1920x1080",
                "importance": "critical",
            },
            {
                "id_pattern": f"{category_id}_quality",
                "type": "integer",
                "label_template": "{adjective} Quality",
                "min_value": 1,
                "max_value": 5,
                "default_value": 3,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_vsync",
                "type": "boolean",
                "label_template": "Enable VSync",
                "default_value": True,
                "importance": "medium",
            },
            {
                "id_pattern": f"{category_id}_antialiasing",
                "type": "string",
                "label_template": "Antialiasing Mode",
                "options": ["off", "FXAA", "MSAA_2x", "MSAA_4x", "TAA"],
                "default_value": "FXAA",
                "importance": "medium",
            },
        ]

    def _network_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_protocol",
                "type": "string",
                "label_template": "{protocol} Configuration",
                "options": ["auto", "ipv4", "ipv6", "dual_stack"],
                "default_value": "auto",
                "importance": "critical",
            },
            {
                "id_pattern": f"{category_id}_port",
                "type": "integer",
                "label_template": "Port Number",
                "min_value": 1024,
                "max_value": 65535,
                "default_value": 8080,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_timeout",
                "type": "integer",
                "label_template": "Connection Timeout",
                "min_value": 1,
                "max_value": 300,
                "default_value": 30,
                "importance": "medium",
            },
        ]

    def _security_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_encryption",
                "type": "string",
                "label_template": "Encryption Algorithm",
                "options": ["AES-128", "AES-256", "ChaCha20", "RSA-2048", "RSA-4096"],
                "default_value": "AES-256",
                "importance": "critical",
            },
            {
                "id_pattern": f"{category_id}_auth_required",
                "type": "boolean",
                "label_template": "Require Authentication",
                "default_value": True,
                "importance": "critical",
            },
            {
                "id_pattern": f"{category_id}_key_rotation",
                "type": "integer",
                "label_template": "Key Rotation Period (days)",
                "min_value": 1,
                "max_value": 365,
                "default_value": 90,
                "importance": "high",
            },
        ]

    def _performance_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_thread_count",
                "type": "integer",
                "label_template": "Worker Thread Count",
                "min_value": 1,
                "max_value": 64,
                "default_value": 4,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_cache_size",
                "type": "integer",
                "label_template": "Cache Size (MB)",
                "min_value": 16,
                "max_value": 8192,
                "default_value": 256,
                "importance": "medium",
            },
            {
                "id_pattern": f"{category_id}_optimization_level",
                "type": "integer",
                "label_template": "Optimization Level",
                "min_value": 0,
                "max_value": 3,
                "default_value": 2,
                "importance": "medium",
            },
        ]

    def _virtualization_templates(
        self, category_id: str, category: dict
    ) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_vcpu_count",
                "type": "integer",
                "label_template": "Virtual CPU Count",
                "min_value": 1,
                "max_value": 128,
                "default_value": 2,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_memory",
                "type": "integer",
                "label_template": "Memory Allocation (GB)",
                "min_value": 1,
                "max_value": 512,
                "default_value": 4,
                "importance": "critical",
            },
            {
                "id_pattern": f"{category_id}_nested",
                "type": "boolean",
                "label_template": "Enable Nested Virtualization",
                "default_value": False,
                "importance": "medium",
            },
        ]

    def _developer_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_debug_mode",
                "type": "boolean",
                "label_template": "Enable Debug Mode",
                "default_value": False,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_log_level",
                "type": "string",
                "label_template": "Logging Level",
                "options": ["trace", "debug", "info", "warn", "error", "fatal"],
                "default_value": "info",
                "importance": "medium",
            },
            {
                "id_pattern": f"{category_id}_profiling",
                "type": "boolean",
                "label_template": "Enable Profiling",
                "default_value": False,
                "importance": "medium",
            },
        ]

    def _quantum_templates(self, category_id: str, category: dict) -> list[dict]:
        return [
            {
                "id_pattern": f"{category_id}_qubit_count",
                "type": "integer",
                "label_template": "Qubit Allocation",
                "min_value": 1,
                "max_value": 1000,
                "default_value": 50,
                "importance": "critical",
            },
            {
                "id_pattern": f"{category_id}_entanglement",
                "type": "boolean",
                "label_template": "Enable Quantum Entanglement",
                "default_value": True,
                "importance": "high",
            },
            {
                "id_pattern": f"{category_id}_measurement_basis",
                "type": "string",
                "label_template": "Measurement Basis",
                "options": ["computational", "hadamard", "bell", "custom"],
                "default_value": "computational",
                "importance": "medium",
            },
        ]

    def _generic_templates(self, category_id: str, category: dict) -> list[dict]:
        complexity = category["complexity"]
        templates = []

        for i in range(min(complexity * 2, 10)):
            template_type = random.choice(["boolean", "integer", "float", "string"])
            template = self._create_generic_template(
                category_id, i, template_type, complexity
            )
            templates.append(template)

        return templates

    def _create_generic_template(
        self, category_id: str, index: int, template_type: str, complexity: int
    ) -> dict:
        base = {
            "id_pattern": f"{category_id}_setting_{index}",
            "type": template_type,
            "label_template": self._get_label_for_type(template_type),
            "importance": random.choice(["low", "medium", "high"]),
        }

        if template_type == "boolean":
            base["default_value"] = False
        elif template_type in ["integer", "float"]:
            base["min_value"] = 0
            base["max_value"] = 100 * complexity
            base["default_value"] = 50 * complexity
        elif template_type == "string":
            base["options"] = [f"option_{j}" for j in range(3 + complexity)]
            base["default_value"] = "option_0"

        return base

    def _get_label_for_type(self, template_type: str) -> str:
        labels = self.pools.get("label_templates", {}).get(template_type, [])
        return random.choice(labels) if labels else f"{{adjective}} {{noun}}"

    def _create_value_templates(self, category_id: str, complexity: int) -> list[dict]:
        count = min(complexity * 3, 15)
        templates = []

        for i in range(count):
            if random.random() < 0.4:
                template_type = "boolean"
            elif random.random() < 0.7:
                template_type = "integer"
            elif random.random() < 0.9:
                template_type = "string"
            else:
                template_type = "float"

            template = self._create_generic_template(
                category_id, 100 + i, template_type, complexity
            )
            templates.append(template)

        return templates

    def _extract_word_pools(self, theme: str) -> dict:
        pools = {}

        if theme in self.pools.get("themed_pools", {}):
            pools.update(self.pools["themed_pools"][theme])

        for pool_name, pool_data in self.pools.get("global_pools", {}).items():
            if isinstance(pool_data, dict):
                pools[pool_name] = sum(pool_data.values(), [])
            else:
                pools[pool_name] = pool_data

        return pools


def main():
    generator = TemplateGenerator(
        "data/menu_categories.json", "data/madlibs_pools.json"
    )
    generator.generate_all("data/setting_templates")
    print("\nAll template files generated successfully")


if __name__ == "__main__":
    main()
