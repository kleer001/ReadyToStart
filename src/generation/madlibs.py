import random
import re

from src.core.config_loader import ConfigLoader


class MadLibsEngine:
    def __init__(self, templates: dict[str, list[str]], config_loader: ConfigLoader):
        self.templates = templates
        self.config_loader = config_loader
        self.vocab = self._load_vocabulary()

    def fill_template(
        self, template: str, context: dict[str, str] | None = None
    ) -> str:
        if context is None:
            context = {}

        placeholders = re.findall(r"\{(\w+)\}", template)
        result = template

        for placeholder in placeholders:
            value = self._get_placeholder_value(placeholder, context)
            result = result.replace(f"{{{placeholder}}}", value, 1)

        return result

    def generate_requirement(self, node_id: str, category: str) -> str:
        return self._generate_from_template(
            "requirement_templates", {"category": category, "node_id": node_id}
        )

    def generate_error(self, setting_id: str) -> str:
        return self._generate_from_template("error_templates", {"setting": setting_id})

    def generate_setting_label(self, category: str, index: int) -> str:
        return self._generate_from_template(
            "setting_labels", {"category": category, "index": str(index)}
        )

    def _generate_from_template(
        self, template_type: str, context: dict[str, str]
    ) -> str:
        template = self._select_template(template_type)
        return self.fill_template(template, context)

    def _load_vocabulary(self) -> dict[str, list[str]]:
        return self.config_loader.load_vocabulary()

    def _get_placeholder_value(self, placeholder: str, context: dict[str, str]) -> str:
        if placeholder in context:
            return context[placeholder]
        if placeholder in self.vocab:
            return random.choice(self.vocab[placeholder])
        return f"[{placeholder}]"

    def _select_template(self, template_type: str) -> str:
        templates = self.templates.get(template_type, [])
        if not templates:
            return "{category} {setting}"
        return random.choice(templates)
