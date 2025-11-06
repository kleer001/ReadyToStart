import random
from typing import Any, Dict, List

from ready_to_start.core.config_loader import GenerationConfig
from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.types import Setting
from ready_to_start.generation.madlibs import MadLibsEngine


class SettingCompiler:
    def __init__(self, config: GenerationConfig, madlibs: MadLibsEngine):
        self.config = config
        self.madlibs = madlibs
        self.categories_config = self._load_category_config()

    def compile_settings(self, node_id: str, category: str, is_critical: bool) -> List[Setting]:
        cat_config = self.categories_config.get(category, {})
        count = cat_config.get("setting_count", 8)

        return [
            self._create_setting(node_id, category, i, is_critical)
            for i in range(count)
        ]

    def _create_setting(self, node_id: str, category: str, index: int, is_critical: bool) -> Setting:
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
            setting.min_value = 0
            setting.max_value = 100

        return setting

    def _load_category_config(self) -> Dict[str, Dict]:
        return self.madlibs.config_loader.load_categories()

    def _choose_type(self, is_critical: bool) -> SettingType:
        if is_critical:
            weights = [0.5, 0.2, 0.2, 0.1]
        else:
            weights = [0.25, 0.25, 0.25, 0.25]

        types = [
            SettingType.BOOLEAN,
            SettingType.INTEGER,
            SettingType.FLOAT,
            SettingType.STRING,
        ]
        return random.choices(types, weights=weights)[0]

    def _default_value(self, setting_type: SettingType) -> Any:
        defaults = {
            SettingType.BOOLEAN: False,
            SettingType.INTEGER: 0,
            SettingType.FLOAT: 0.0,
            SettingType.STRING: "",
        }
        return defaults[setting_type]
