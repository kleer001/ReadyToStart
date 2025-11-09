from abc import ABC, abstractmethod
from random import Random


class Glitch(ABC):
    def __init__(self, glitch_id: str, intensity: float = 0.5):
        self.id = glitch_id
        self.intensity = max(0.0, min(1.0, intensity))

    @abstractmethod
    def apply(self, text: str, random: Random) -> str:
        pass


class CharacterCorruptionGlitch(Glitch):
    GLITCH_CHARS = "░▒▓█▄▀■□▪▫"

    def apply(self, text: str, random: Random) -> str:
        if not text or self.intensity == 0:
            return text

        chars = list(text)
        num_corrupted = int(len(chars) * self.intensity)

        for _ in range(num_corrupted):
            if chars:
                idx = random.randrange(len(chars))
                chars[idx] = random.choice(self.GLITCH_CHARS)

        return "".join(chars)


class CharacterDuplicationGlitch(Glitch):
    def apply(self, text: str, random: Random) -> str:
        if not text or self.intensity == 0:
            return text

        chars = list(text)
        num_duplicated = int(len(chars) * self.intensity)

        for _ in range(num_duplicated):
            if chars:
                idx = random.randrange(len(chars))
                chars.insert(idx, chars[idx])

        return "".join(chars)


class CharacterDeletionGlitch(Glitch):
    def apply(self, text: str, random: Random) -> str:
        if not text or self.intensity == 0:
            return text

        chars = list(text)
        num_deleted = int(len(chars) * self.intensity)

        for _ in range(num_deleted):
            if chars:
                idx = random.randrange(len(chars))
                chars.pop(idx)

        return "".join(chars)


class ColorGlitch(Glitch):
    ANSI_COLORS = [
        "\033[31m",
        "\033[32m",
        "\033[33m",
        "\033[34m",
        "\033[35m",
        "\033[36m",
        "\033[91m",
        "\033[92m",
        "\033[93m",
        "\033[94m",
        "\033[95m",
        "\033[96m",
    ]
    RESET = "\033[0m"

    def apply(self, text: str, random: Random) -> str:
        if not text or self.intensity == 0:
            return text

        if random.random() < self.intensity:
            color = random.choice(self.ANSI_COLORS)
            return f"{color}{text}{self.RESET}"

        return text


class OffsetGlitch(Glitch):
    def apply(self, text: str, random: Random) -> str:
        if not text or self.intensity == 0:
            return text

        if random.random() < self.intensity:
            spaces = random.randint(0, int(10 * self.intensity))
            return " " * spaces + text

        return text


class GlitchComposite:
    def __init__(self, glitches: list[Glitch], random: Random | None = None):
        self.glitches = glitches
        self.random = random or Random()

    def apply(self, text: str) -> str:
        result = text
        for glitch in self.glitches:
            result = glitch.apply(result, self.random)
        return result


class GlitchEngine:
    def __init__(self, intensity: float = 0.3, random: Random | None = None):
        self.intensity = intensity
        self.random = random or Random()
        self.enabled = False

        self.glitches = [
            CharacterCorruptionGlitch("corruption", intensity * 0.5),
            CharacterDuplicationGlitch("duplication", intensity * 0.3),
            CharacterDeletionGlitch("deletion", intensity * 0.2),
            ColorGlitch("color", intensity * 0.4),
            OffsetGlitch("offset", intensity * 0.3),
        ]

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def set_intensity(self, intensity: float) -> None:
        self.intensity = max(0.0, min(1.0, intensity))
        for glitch in self.glitches:
            glitch.intensity = self.intensity * 0.5

    def process_text(self, text: str) -> str:
        if not self.enabled or not text:
            return text

        if self.random.random() > self.intensity:
            return text

        active_glitches = [
            g for g in self.glitches if self.random.random() < g.intensity
        ]

        if not active_glitches:
            return text

        composite = GlitchComposite(active_glitches, self.random)
        return composite.apply(text)
