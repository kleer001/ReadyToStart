import os
from configparser import ConfigParser
from dataclasses import dataclass

from src.ui.renderer import pad_ansi


@dataclass
class Region:
    x: int
    y: int
    width: int
    height: int

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def clip_text(self, text: str) -> str:
        return pad_ansi(text, self.width)


class LayoutManager:
    def __init__(self, config_path: str):
        self.config = ConfigParser()
        self.config.read(config_path)
        self.terminal_width, self.terminal_height = self._get_terminal_size()
        self.regions = self._calculate_regions()

    def _get_terminal_size(self) -> tuple[int, int]:
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except OSError:
            return 80, 24

    def _parse_region_config(self, region_name: str) -> Region:
        config_str = self.config.get("regions", region_name, fallback="0,0,80,24")
        parts = [int(p.strip()) for p in config_str.split(",")]

        if len(parts) != 4:
            return Region(0, 0, 80, 24)

        return Region(parts[0], parts[1], parts[2], parts[3])

    def _calculate_regions(self) -> dict[str, Region]:
        return {
            "header": self._parse_region_config("header"),
            "sidebar": self._parse_region_config("sidebar"),
            "content": self._parse_region_config("content"),
            "footer": self._parse_region_config("footer"),
        }

    def get_region(self, name: str) -> Region | None:
        return self.regions.get(name)

    def render_region(self, region_name: str, content: list[str]) -> list[str]:
        region = self.get_region(region_name)
        if not region:
            return content

        lines_per_page = int(self.config.get("scrolling", "lines_per_page", fallback="15"))
        max_lines = min(region.height, lines_per_page)

        clipped_lines = []
        for i, line in enumerate(content[:max_lines]):
            clipped_lines.append(region.clip_text(line))

        while len(clipped_lines) < max_lines:
            clipped_lines.append(" " * region.width)

        return clipped_lines

    def refresh_terminal_size(self):
        self.terminal_width, self.terminal_height = self._get_terminal_size()
