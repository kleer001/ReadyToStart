import random
from typing import Any

from src.core.config_loader import GenerationConfig
from src.core.enums import SettingState, SettingType
from src.core.types import Setting
from src.generation.madlibs import MadLibsEngine

DEFAULT_MIN_VALUE = 0
DEFAULT_MAX_VALUE = 100

CRITICAL_TYPE_WEIGHTS = {
    SettingType.BOOLEAN: 0.5,
    SettingType.INTEGER: 0.2,
    SettingType.FLOAT: 0.2,
    SettingType.STRING: 0.1,
}

NORMAL_TYPE_WEIGHTS = {
    SettingType.BOOLEAN: 0.25,
    SettingType.INTEGER: 0.25,
    SettingType.FLOAT: 0.25,
    SettingType.STRING: 0.25,
}


class SettingCompiler:
    def __init__(self, config: GenerationConfig, madlibs: MadLibsEngine, max_items_per_page: int = 15):
        self.config = config
        self.madlibs = madlibs
        self.max_items_per_page = max_items_per_page
        self.categories_config = self._load_category_config()

    def compile_settings(
        self, node_id: str, category: str, is_critical: bool
    ) -> list[Setting]:
        cat_config = self.categories_config.get(category, {})
        count = cat_config.get("setting_count", 8)

        # Enforce maximum items per page limit
        count = min(count, self.max_items_per_page)

        return [
            self._create_setting(node_id, category, i, is_critical)
            for i in range(count)
        ]

    def _create_setting(
        self, node_id: str, category: str, index: int, is_critical: bool
    ) -> Setting:
        setting_type = self._choose_type(is_critical)
        label = self.madlibs.generate_setting_label(category, index)

        setting = Setting(
            id=f"{node_id}_setting_{index}",
            type=setting_type,
            value=self._default_value(setting_type),
            state=SettingState.DISABLED if is_critical else SettingState.ENABLED,
            label=label,
        )

        if setting_type in [SettingType.INTEGER, SettingType.FLOAT]:
            setting.min_value = DEFAULT_MIN_VALUE
            setting.max_value = DEFAULT_MAX_VALUE

        return setting

    def _load_category_config(self) -> dict[str, dict]:
        return self.madlibs.config_loader.load_categories()

    def _choose_type(self, is_critical: bool) -> SettingType:
        weights_map = CRITICAL_TYPE_WEIGHTS if is_critical else NORMAL_TYPE_WEIGHTS
        types = list(weights_map.keys())
        weights = list(weights_map.values())
        return random.choices(types, weights=weights)[0]

    def _default_value(self, setting_type: SettingType) -> Any:
        defaults = {
            SettingType.BOOLEAN: False,
            SettingType.INTEGER: 0,
            SettingType.FLOAT: 0.0,
            SettingType.STRING: "",
        }
        return defaults[setting_type]
