import random
import re

from ready_to_start.core.config_loader import ConfigLoader


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
        template = self._select_template("requirement_templates")
        context = {"category": category, "node_id": node_id}
        return self.fill_template(template, context)

    def generate_error(self, setting_id: str) -> str:
        template = self._select_template("error_templates")
        context = {"setting": setting_id}
        return self.fill_template(template, context)

    def generate_setting_label(self, category: str, index: int) -> str:
        template = self._select_template("setting_labels")
        context = {"category": category, "index": str(index)}
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
