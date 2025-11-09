import configparser
from dataclasses import dataclass
from random import Random


@dataclass
class FakeMessage:
    message_type: str
    text: str
    severity: str = "error"


class FakeMessageGenerator:
    def __init__(self, random: Random | None = None):
        self.random = random or Random()
        self.templates: dict[str, list[str]] = {}
        self.components: dict[str, list[str]] = {}

    def load_from_config(self, config_path: str) -> None:
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            if section.startswith("template_"):
                category = section[9:]
                self.templates[category] = [
                    line.strip()
                    for line in parser[section].get("messages", "").split("\n")
                    if line.strip()
                ]
            elif section.startswith("components_"):
                category = section[11:]
                self.components[category] = [
                    line.strip()
                    for line in parser[section].get("values", "").split("\n")
                    if line.strip()
                ]

    def generate(self, category: str = "generic") -> FakeMessage:
        templates = self.templates.get(category, self.templates.get("generic", []))
        if not templates:
            return FakeMessage("fake_error", "An error has occurred", "error")

        template = self.random.choice(templates)
        message = self._fill_template(template)

        return FakeMessage("fake_error", message, "error")

    def _fill_template(self, template: str) -> str:
        result = template

        for key, values in self.components.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, self.random.choice(values))

        return result

    def generate_system_message(self) -> FakeMessage:
        return self.generate("system")

    def generate_permission_error(self) -> FakeMessage:
        return self.generate("permission")

    def generate_dependency_error(self) -> FakeMessage:
        return self.generate("dependency")

    def generate_resource_error(self) -> FakeMessage:
        return self.generate("resource")


class MessageScheduler:
    def __init__(
        self, generator: FakeMessageGenerator, random: Random | None = None
    ):
        self.generator = generator
        self.random = random or Random()
        self.scheduled: list[tuple[int, FakeMessage]] = []
        self.tick_count = 0

    def schedule_message(self, delay: int, category: str) -> None:
        message = self.generator.generate(category)
        self.scheduled.append((self.tick_count + delay, message))

    def schedule_random(self, min_delay: int, max_delay: int, category: str) -> None:
        delay = self.random.randint(min_delay, max_delay)
        self.schedule_message(delay, category)

    def tick(self) -> list[FakeMessage]:
        self.tick_count += 1
        ready = [msg for tick, msg in self.scheduled if tick <= self.tick_count]
        self.scheduled = [(t, m) for t, m in self.scheduled if t > self.tick_count]
        return ready

    def clear(self) -> None:
        self.scheduled.clear()
