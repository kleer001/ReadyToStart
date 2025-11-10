# Ready to Start - Phase 6 Detailed Roadmap

## Phase 6: Content Creation (Menu Categories & Settings)

### 6.1 Menu Category Definitions
**Goal:** Define all 32 menu categories with themes and characteristics

**Files:**
- `data/menu_categories.json`
- `data/category_schemas.json`
- `scripts/validate_categories.py`

**Implementation:**

**Menu Categories (32 total):**
```json
{
  "categories": [
    {
      "id": "audio",
      "name": "Audio Settings",
      "complexity": 3,
      "setting_count_range": [8, 15],
      "dependency_density": "medium",
      "theme": "sound_configuration",
      "subcategories": ["output", "input", "processing", "devices"]
    },
    {
      "id": "graphics",
      "name": "Graphics Settings",
      "complexity": 4,
      "setting_count_range": [12, 20],
      "dependency_density": "high",
      "theme": "visual_configuration",
      "subcategories": ["display", "rendering", "effects", "performance"]
    },
    {
      "id": "network",
      "name": "Network Settings",
      "complexity": 5,
      "setting_count_range": [10, 18],
      "dependency_density": "high",
      "theme": "connectivity",
      "subcategories": ["connection", "protocols", "security", "advanced"]
    },
    {
      "id": "user_profile",
      "name": "User Profile",
      "complexity": 2,
      "setting_count_range": [6, 12],
      "dependency_density": "low",
      "theme": "personalization",
      "subcategories": ["account", "preferences", "privacy"]
    },
    {
      "id": "accessibility",
      "name": "Accessibility",
      "complexity": 3,
      "setting_count_range": [10, 16],
      "dependency_density": "medium",
      "theme": "inclusive_design",
      "subcategories": ["visual", "audio", "input", "cognitive"]
    },
    {
      "id": "security",
      "name": "Security Settings",
      "complexity": 5,
      "setting_count_range": [12, 22],
      "dependency_density": "very_high",
      "theme": "protection",
      "subcategories": ["authentication", "encryption", "permissions", "monitoring"]
    },
    {
      "id": "performance",
      "name": "Performance Tuning",
      "complexity": 4,
      "setting_count_range": [8, 14],
      "dependency_density": "high",
      "theme": "optimization",
      "subcategories": ["cpu", "memory", "disk", "cache"]
    },
    {
      "id": "localization",
      "name": "Language & Region",
      "complexity": 2,
      "setting_count_range": [6, 10],
      "dependency_density": "low",
      "theme": "internationalization",
      "subcategories": ["language", "formatting", "timezone", "currency"]
    },
    {
      "id": "notifications",
      "name": "Notifications",
      "complexity": 3,
      "setting_count_range": [8, 14],
      "dependency_density": "medium",
      "theme": "alerts",
      "subcategories": ["system", "applications", "email", "visual"]
    },
    {
      "id": "power_management",
      "name": "Power Management",
      "complexity": 3,
      "setting_count_range": [7, 12],
      "dependency_density": "medium",
      "theme": "energy",
      "subcategories": ["battery", "sleep", "performance", "thermal"]
    },
    {
      "id": "storage",
      "name": "Storage Settings",
      "complexity": 4,
      "setting_count_range": [10, 16],
      "dependency_density": "high",
      "theme": "data_management",
      "subcategories": ["drives", "backup", "sync", "cleanup"]
    },
    {
      "id": "devices",
      "name": "Devices & Peripherals",
      "complexity": 3,
      "setting_count_range": [9, 15],
      "dependency_density": "medium",
      "theme": "hardware",
      "subcategories": ["input", "output", "wireless", "usb"]
    },
    {
      "id": "updates",
      "name": "System Updates",
      "complexity": 4,
      "setting_count_range": [8, 13],
      "dependency_density": "high",
      "theme": "maintenance",
      "subcategories": ["automatic", "schedule", "rollback", "sources"]
    },
    {
      "id": "privacy",
      "name": "Privacy Settings",
      "complexity": 5,
      "setting_count_range": [14, 24],
      "dependency_density": "very_high",
      "theme": "data_protection",
      "subcategories": ["tracking", "sharing", "analytics", "permissions"]
    },
    {
      "id": "startup",
      "name": "Startup & Boot",
      "complexity": 3,
      "setting_count_range": [7, 11],
      "dependency_density": "medium",
      "theme": "initialization",
      "subcategories": ["boot_order", "programs", "services", "splash"]
    },
    {
      "id": "experimental",
      "name": "Experimental Features",
      "complexity": 5,
      "setting_count_range": [10, 20],
      "dependency_density": "chaotic",
      "theme": "bleeding_edge",
      "subcategories": ["beta", "alpha", "developer", "unstable"]
    },
    {
      "id": "telemetry",
      "name": "Diagnostics & Telemetry",
      "complexity": 4,
      "setting_count_range": [9, 15],
      "dependency_density": "high",
      "theme": "monitoring",
      "subcategories": ["logging", "reporting", "crash_reports", "usage"]
    },
    {
      "id": "cloud_sync",
      "name": "Cloud Synchronization",
      "complexity": 4,
      "setting_count_range": [10, 16],
      "dependency_density": "high",
      "theme": "sync",
      "subcategories": ["files", "settings", "credentials", "conflicts"]
    },
    {
      "id": "gestures",
      "name": "Gestures & Touch",
      "complexity": 2,
      "setting_count_range": [6, 11],
      "dependency_density": "low",
      "theme": "input_methods",
      "subcategories": ["touch", "trackpad", "mouse_gestures", "shortcuts"]
    },
    {
      "id": "appearance",
      "name": "Appearance & Themes",
      "complexity": 2,
      "setting_count_range": [8, 14],
      "dependency_density": "low",
      "theme": "aesthetics",
      "subcategories": ["colors", "fonts", "icons", "wallpaper"]
    },
    {
      "id": "extensions",
      "name": "Extensions & Plugins",
      "complexity": 3,
      "setting_count_range": [7, 12],
      "dependency_density": "medium",
      "theme": "modularity",
      "subcategories": ["installed", "marketplace", "updates", "permissions"]
    },
    {
      "id": "shortcuts",
      "name": "Keyboard Shortcuts",
      "complexity": 3,
      "setting_count_range": [12, 20],
      "dependency_density": "medium",
      "theme": "keybindings",
      "subcategories": ["system", "application", "custom", "conflicts"]
    },
    {
      "id": "search_indexing",
      "name": "Search & Indexing",
      "complexity": 3,
      "setting_count_range": [8, 13],
      "dependency_density": "medium",
      "theme": "discovery",
      "subcategories": ["locations", "file_types", "schedule", "exclusions"]
    },
    {
      "id": "virtualization",
      "name": "Virtualization",
      "complexity": 5,
      "setting_count_range": [10, 17],
      "dependency_density": "very_high",
      "theme": "vm_configuration",
      "subcategories": ["hypervisor", "resources", "networking", "integration"]
    },
    {
      "id": "developer",
      "name": "Developer Options",
      "complexity": 5,
      "setting_count_range": [15, 25],
      "dependency_density": "very_high",
      "theme": "development",
      "subcategories": ["debugging", "profiling", "apis", "tools"]
    },
    {
      "id": "gaming",
      "name": "Gaming Settings",
      "complexity": 4,
      "setting_count_range": [11, 18],
      "dependency_density": "high",
      "theme": "gaming_optimization",
      "subcategories": ["performance", "overlays", "recording", "controller"]
    },
    {
      "id": "backup",
      "name": "Backup & Restore",
      "complexity": 4,
      "setting_count_range": [9, 14],
      "dependency_density": "high",
      "theme": "data_safety",
      "subcategories": ["automatic", "manual", "restore", "verification"]
    },
    {
      "id": "parental_controls",
      "name": "Parental Controls",
      "complexity": 4,
      "setting_count_range": [10, 16],
      "dependency_density": "high",
      "theme": "restrictions",
      "subcategories": ["time_limits", "content", "apps", "reporting"]
    },
    {
      "id": "advanced_system",
      "name": "Advanced System",
      "complexity": 5,
      "setting_count_range": [14, 22],
      "dependency_density": "very_high",
      "theme": "system_internals",
      "subcategories": ["registry", "services", "kernel", "hardware"]
    },
    {
      "id": "legacy_compatibility",
      "name": "Legacy Compatibility",
      "complexity": 4,
      "setting_count_range": [8, 13],
      "dependency_density": "high",
      "theme": "backwards_compatibility",
      "subcategories": ["emulation", "compatibility_modes", "drivers", "apis"]
    },
    {
      "id": "quantum_settings",
      "name": "Quantum Configuration",
      "complexity": 5,
      "setting_count_range": [10, 18],
      "dependency_density": "paradoxical",
      "theme": "quantum_computing",
      "subcategories": ["entanglement", "superposition", "decoherence", "measurement"]
    },
    {
      "id": "meta_settings",
      "name": "Settings Settings",
      "complexity": 5,
      "setting_count_range": [8, 15],
      "dependency_density": "recursive",
      "theme": "self_reference",
      "subcategories": ["menu_behavior", "dependency_rules", "generation", "reality"]
    }
  ]
}
```

**Validation Script:**
```python
#!/usr/bin/env python3
"""Validate menu category definitions"""

import json
import sys

def validate_categories(filepath: str) -> bool:
    with open(filepath) as f:
        data = json.load(f)

    categories = data['categories']

    # Check count
    if len(categories) != 32:
        print(f"ERROR: Expected 32 categories, found {len(categories)}")
        return False

    # Validate each category
    required_fields = ['id', 'name', 'complexity', 'setting_count_range',
                       'dependency_density', 'theme', 'subcategories']

    for cat in categories:
        for field in required_fields:
            if field not in cat:
                print(f"ERROR: Category {cat.get('id', 'unknown')} missing field: {field}")
                return False

        # Complexity should be 1-5
        if not 1 <= cat['complexity'] <= 5:
            print(f"ERROR: Category {cat['id']} has invalid complexity: {cat['complexity']}")
            return False

        # Setting count should be reasonable
        min_count, max_count = cat['setting_count_range']
        if min_count >= max_count or min_count < 1:
            print(f"ERROR: Category {cat['id']} has invalid setting count range")
            return False

    print(f"✓ All {len(categories)} categories valid")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_categories.py <categories.json>")
        sys.exit(1)

    if validate_categories(sys.argv[1]):
        sys.exit(0)
    else:
        sys.exit(1)
```

**Testing:**
- Category count validation
- Required field presence
- Complexity range checking
- Setting count range validation
- JSON schema validation

**Procedural:** ✓ Categories loaded from JSON

---

### 6.2 Setting Templates Expansion
**Goal:** Create comprehensive setting templates for each category

**Files:**
- `data/setting_templates/`
  - `audio_templates.json`
  - `graphics_templates.json`
  - `network_templates.json`
  - (... 29 more files)
- `scripts/generate_setting_templates.py`

**Template Structure:**
```json
{
  "category": "audio",
  "templates": [
    {
      "id_pattern": "{category}_master_volume",
      "type": "integer",
      "label_template": "Master {noun} Volume",
      "min_value": 0,
      "max_value": 100,
      "default_value": 50,
      "importance": "critical",
      "dependency_likelihood": 0.7,
      "description_template": "Controls the overall {adjective} level of {noun} output"
    },
    {
      "id_pattern": "{category}_enable_{feature}",
      "type": "boolean",
      "label_template": "Enable {adjective} {feature}",
      "default_value": false,
      "importance": "high",
      "dependency_likelihood": 0.9,
      "description_template": "Toggles the {adjective} {feature} functionality"
    },
    {
      "id_pattern": "{category}_{device}_configuration",
      "type": "string",
      "label_template": "{device} Configuration Mode",
      "options": ["stereo", "mono", "surround_5_1", "surround_7_1", "headphones"],
      "default_value": "stereo",
      "importance": "medium",
      "dependency_likelihood": 0.5,
      "description_template": "Sets the output mode for {device}"
    }
  ],
  "word_pools": {
    "nouns": ["audio", "sound", "speaker", "output", "playback"],
    "adjectives": ["primary", "secondary", "enhanced", "advanced", "default"],
    "features": ["surround_processing", "3d_audio", "normalization", "enhancement"],
    "devices": ["speakers", "headphones", "microphone", "line_in", "optical"]
  }
}
```

**Template Generator:**
```python
#!/usr/bin/env python3
"""Generate setting templates for all categories"""

import json
from pathlib import Path

def generate_category_templates(category_id: str, category_info: dict) -> dict:
    """Generate setting templates for a category"""

    # Base templates applicable to all categories
    base_templates = [
        {
            "id_pattern": f"{category_id}_enable",
            "type": "boolean",
            "label_template": "Enable {category_name}",
            "default_value": False,
            "importance": "critical",
            "dependency_likelihood": 0.95
        },
        {
            "id_pattern": f"{category_id}_advanced_mode",
            "type": "boolean",
            "label_template": "Show Advanced Options",
            "default_value": False,
            "importance": "medium",
            "dependency_likelihood": 0.8
        }
    ]

    # Generate specific templates based on category theme
    theme_generators = {
        "sound_configuration": generate_audio_templates,
        "visual_configuration": generate_graphics_templates,
        "connectivity": generate_network_templates,
        # Add generators for each theme
    }

    specific_templates = []
    if category_info['theme'] in theme_generators:
        generator = theme_generators[category_info['theme']]
        specific_templates = generator(category_id, category_info)

    return {
        "category": category_id,
        "templates": base_templates + specific_templates,
        "word_pools": generate_word_pools(category_info['theme'])
    }

def generate_audio_templates(category_id: str, info: dict) -> list:
    """Generate audio-specific templates"""
    return [
        {
            "id_pattern": f"{category_id}_volume",
            "type": "integer",
            "label_template": "{adjective} Volume",
            "min_value": 0,
            "max_value": 100,
            "default_value": 50,
            "importance": "high"
        },
        {
            "id_pattern": f"{category_id}_device",
            "type": "string",
            "label_template": "{device} Selection",
            "options": ["default", "speakers", "headphones", "hdmi"],
            "importance": "high"
        },
        # More audio-specific templates...
    ]

def generate_graphics_templates(category_id: str, info: dict) -> list:
    """Generate graphics-specific templates"""
    return [
        {
            "id_pattern": f"{category_id}_resolution",
            "type": "string",
            "label_template": "Screen Resolution",
            "options": ["1920x1080", "2560x1440", "3840x2160"],
            "importance": "critical"
        },
        {
            "id_pattern": f"{category_id}_quality",
            "type": "integer",
            "label_template": "{adjective} Quality",
            "min_value": 1,
            "max_value": 5,
            "default_value": 3,
            "importance": "high"
        },
        # More graphics-specific templates...
    ]

def generate_network_templates(category_id: str, info: dict) -> list:
    """Generate network-specific templates"""
    return [
        {
            "id_pattern": f"{category_id}_protocol",
            "type": "string",
            "label_template": "{protocol} Configuration",
            "options": ["auto", "ipv4", "ipv6", "dual_stack"],
            "importance": "critical"
        },
        # More network-specific templates...
    ]

def generate_word_pools(theme: str) -> dict:
    """Generate word pools for Mad Libs based on theme"""
    common_pools = {
        "adjectives": ["primary", "secondary", "enhanced", "advanced", "default",
                       "optimal", "custom", "automatic", "manual"],
        "nouns": ["configuration", "setting", "option", "parameter", "value"]
    }

    theme_specific_pools = {
        "sound_configuration": {
            "nouns": ["audio", "sound", "volume", "frequency", "balance"],
            "devices": ["speaker", "microphone", "headphones", "subwoofer"]
        },
        "visual_configuration": {
            "nouns": ["graphics", "display", "rendering", "texture", "shader"],
            "features": ["antialiasing", "vsync", "bloom", "shadows"]
        },
        # Add pools for each theme...
    }

    pools = common_pools.copy()
    if theme in theme_specific_pools:
        pools.update(theme_specific_pools[theme])

    return pools

def main():
    # Load category definitions
    with open("data/menu_categories.json") as f:
        categories_data = json.load(f)

    output_dir = Path("data/setting_templates")
    output_dir.mkdir(exist_ok=True)

    for category in categories_data['categories']:
        templates = generate_category_templates(category['id'], category)

        output_file = output_dir / f"{category['id']}_templates.json"
        with open(output_file, 'w') as f:
            json.dump(templates, f, indent=2)

        print(f"Generated templates for {category['id']}")

if __name__ == "__main__":
    main()
```

**Testing:**
- Template generation for all 32 categories
- Required field presence in templates
- Type-specific field validation
- Word pool completeness
- Template count matches category specification

**Procedural:** ✓ Templates generated from category definitions

---

### 6.3 Mad Libs Content Pool Expansion
**Goal:** Massive expansion of Mad Libs word pools for variety

**Files:**
- `data/madlibs_pools.json`
- `data/themed_pools/` (category-specific pools)
- `scripts/test_madlibs_coverage.py`

**Expanded Pool Structure:**
```json
{
  "global_pools": {
    "adjectives": {
      "positive": ["optimal", "enhanced", "improved", "advanced", "superior"],
      "negative": ["degraded", "limited", "reduced", "minimal", "restricted"],
      "technical": ["synchronized", "calibrated", "optimized", "configured", "initialized"],
      "vague": ["dynamic", "adaptive", "intelligent", "smart", "automatic"]
    },
    "nouns": {
      "technical": ["parameter", "configuration", "threshold", "coefficient", "tolerance"],
      "abstract": ["performance", "quality", "efficiency", "stability", "reliability"],
      "measurement": ["level", "rate", "frequency", "duration", "interval"]
    },
    "verbs": {
      "action": ["enable", "disable", "toggle", "activate", "deactivate"],
      "adjustment": ["increase", "decrease", "modify", "adjust", "calibrate"],
      "checking": ["verify", "validate", "check", "test", "monitor"]
    },
    "technical_jargon": [
      "quantum entanglement", "phase synchronization", "harmonic resonance",
      "spectral analysis", "vector optimization", "matrix recalibration",
      "buffer optimization", "cache coherency", "pipeline synchronization"
    ],
    "fake_units": [
      "microvolts", "nanopixels", "jiggawatts", "teraflops", "gigaframes",
      "quantum bits", "hyperthreads", "bandwidth units"
    ]
  },
  "themed_pools": {
    "audio": {
      "nouns": ["frequency", "amplitude", "waveform", "harmonic", "timbre",
                "resonance", "acoustics", "decibel", "spectrum"],
      "adjectives": ["sonic", "auditory", "aural", "acoustic", "harmonic"],
      "jargon": ["frequency response curve", "signal-to-noise ratio",
                 "dynamic range compression", "spatial audio processing"]
    },
    "graphics": {
      "nouns": ["pixel", "shader", "texture", "polygon", "framebuffer",
                "viewport", "rasterization", "tessellation"],
      "adjectives": ["rendered", "antialiased", "shaded", "filtered", "mapped"],
      "jargon": ["anisotropic filtering", "ambient occlusion",
                 "screen space reflection", "temporal antialiasing"]
    }
    // ... pools for remaining 30 categories
  },
  "misleading_descriptions": [
    "This setting controls the {technical_jargon} of the {noun}",
    "Adjusts the {adjective} {noun} to optimize {abstract_noun}",
    "Enables {vague_adjective} processing of {technical_term}",
    "Configures the {unit} threshold for {technical_process}"
  ],
  "dependency_reasons": [
    "requires {setting_name} to be configured first",
    "conflicts with {setting_name} when enabled",
    "depends on the {adjective} state of {setting_name}",
    "must be synchronized with {setting_name}"
  ]
}
```

**Coverage Testing Script:**
```python
#!/usr/bin/env python3
"""Test Mad Libs pool coverage and variety"""

import json
import random
from collections import Counter

def test_pool_coverage(pools_file: str, num_samples: int = 1000):
    """Test that pools provide good variety"""

    with open(pools_file) as f:
        pools = json.load(f)

    # Test each pool type
    for pool_name, pool_data in pools['global_pools'].items():
        print(f"\n=== Testing {pool_name} ===")

        if isinstance(pool_data, dict):
            # Pool has subcategories
            for subpool_name, words in pool_data.items():
                test_word_distribution(f"{pool_name}.{subpool_name}", words, num_samples)
        else:
            # Flat list
            test_word_distribution(pool_name, pool_data, num_samples)

def test_word_distribution(pool_name: str, words: list, num_samples: int):
    """Check distribution of word selection"""

    if len(words) < 5:
        print(f"  ⚠ {pool_name}: Only {len(words)} words (needs more variety)")
        return

    # Sample words
    samples = [random.choice(words) for _ in range(num_samples)]
    counts = Counter(samples)

    # Check distribution
    expected_freq = num_samples / len(words)
    max_deviation = max(abs(count - expected_freq) / expected_freq
                       for count in counts.values())

    print(f"  ✓ {pool_name}: {len(words)} words, max deviation: {max_deviation:.2%}")

    # List words that never appeared
    unused = set(words) - set(samples)
    if unused:
        print(f"    ! {len(unused)} words unused in {num_samples} samples")

def test_template_generation(pools_file: str, templates_file: str):
    """Test that templates can be filled from pools"""

    with open(pools_file) as f:
        pools = json.load(f)

    with open(templates_file) as f:
        templates = json.load(f)

    # Try generating from each template
    from ready_to_start.generation.madlibs import MadLibsEngine

    engine = MadLibsEngine()
    engine.load_pools(pools_file)

    for template in templates.get('misleading_descriptions', []):
        try:
            result = engine.fill_template(template)
            print(f"  ✓ '{template[:40]}...' -> '{result[:40]}...'")
        except KeyError as e:
            print(f"  ✗ Template failed: {template[:40]}... (missing: {e})")

if __name__ == "__main__":
    test_pool_coverage("data/madlibs_pools.json")
    print("\n" + "="*60)
    test_template_generation("data/madlibs_pools.json",
                            "data/madlibs_pools.json")
```

**Testing:**
- Pool size validation (minimum words per pool)
- Word distribution uniformity
- Template filling success rate
- Category-specific pool coverage
- Jargon believability testing

**Procedural:** ✓ Pools loaded from JSON

---

### 6.4 Dependency Pattern Library
**Goal:** Pre-defined dependency patterns for realistic constraints

**Files:**
- `data/dependency_patterns.json`
- `generation/pattern_matcher.py`
- `tests/test_dependency_patterns.py`

**Pattern Definitions:**
```json
{
  "patterns": [
    {
      "name": "master_enable",
      "description": "Main enable setting that gates all others",
      "structure": {
        "master": {
          "id_pattern": "{category}_enable",
          "type": "boolean",
          "state": "enabled"
        },
        "dependents": {
          "pattern": "{category}_*",
          "exclude": ["{category}_enable"],
          "dependency_type": "simple",
          "required_state": "enabled"
        }
      },
      "applies_to": ["all_categories"]
    },
    {
      "name": "advanced_gate",
      "description": "Advanced settings hidden behind toggle",
      "structure": {
        "gate": {
          "id_pattern": "{category}_advanced_mode",
          "type": "boolean",
          "state": "enabled"
        },
        "dependents": {
          "pattern": "{category}_advanced_*",
          "dependency_type": "simple",
          "required_state": "enabled"
        }
      },
      "applies_to": ["all_categories"]
    },
    {
      "name": "value_threshold",
      "description": "Setting B requires setting A to exceed threshold",
      "structure": {
        "prerequisite": {
          "id_pattern": "{category}_{feature}_level",
          "type": "integer",
          "min_value": 50
        },
        "dependent": {
          "id_pattern": "{category}_{feature}_advanced",
          "dependency_type": "value",
          "operator": ">",
          "threshold": 50
        }
      },
      "applies_to": ["high_complexity_categories"]
    },
    {
      "name": "mutual_exclusion",
      "description": "Two settings that cannot both be enabled",
      "structure": {
        "setting_a": {
          "id_pattern": "{category}_mode_a"
        },
        "setting_b": {
          "id_pattern": "{category}_mode_b"
        },
        "constraint": "exactly_one_enabled"
      },
      "applies_to": ["all_categories"]
    },
    {
      "name": "chain_dependency",
      "description": "A requires B, B requires C, C requires D",
      "structure": {
        "chain_length": [3, 5],
        "pattern": "{category}_tier_{n}",
        "each_depends_on": "previous"
      },
      "applies_to": ["very_high_complexity"]
    },
    {
      "name": "circular_hint",
      "description": "Appears circular but has solution",
      "structure": {
        "setting_a": {
          "id_pattern": "{category}_init"
        },
        "setting_b": {
          "id_pattern": "{category}_verify"
        },
        "apparent_cycle": "a->b->a",
        "actual_solution": "enable both simultaneously or find third setting"
      },
      "applies_to": ["experimental", "meta_settings"]
    }
  ],
  "pattern_probabilities": {
    "complexity_1": {
      "master_enable": 0.9,
      "advanced_gate": 0.3,
      "value_threshold": 0.1
    },
    "complexity_5": {
      "master_enable": 0.95,
      "advanced_gate": 0.7,
      "value_threshold": 0.6,
      "chain_dependency": 0.4,
      "circular_hint": 0.2
    }
  }
}
```

**Pattern Matcher Implementation:**
```python
from typing import List, Dict
import re

class DependencyPatternMatcher:
    """Matches and applies dependency patterns to generated settings"""

    def __init__(self):
        self.patterns = []

    def load_patterns(self, patterns_file: str):
        """Load dependency patterns from JSON"""
        import json
        with open(patterns_file) as f:
            data = json.load(f)
        self.patterns = data['patterns']
        self.probabilities = data['pattern_probabilities']

    def find_applicable_patterns(self, category_info: dict) -> List[dict]:
        """Find patterns that apply to this category"""
        applicable = []

        for pattern in self.patterns:
            applies_to = pattern['applies_to']

            if 'all_categories' in applies_to:
                applicable.append(pattern)
            elif category_info['id'] in applies_to:
                applicable.append(pattern)
            elif f"complexity_{category_info['complexity']}" in applies_to:
                applicable.append(pattern)
            elif category_info['dependency_density'] in applies_to:
                applicable.append(pattern)

        return applicable

    def apply_pattern(self, pattern: dict, settings: List[dict],
                     category_id: str) -> List[tuple]:
        """Apply a pattern to generate dependencies"""
        dependencies = []

        if pattern['name'] == 'master_enable':
            dependencies.extend(
                self._apply_master_enable(pattern, settings, category_id)
            )
        elif pattern['name'] == 'advanced_gate':
            dependencies.extend(
                self._apply_advanced_gate(pattern, settings, category_id)
            )
        elif pattern['name'] == 'value_threshold':
            dependencies.extend(
                self._apply_value_threshold(pattern, settings, category_id)
            )
        elif pattern['name'] == 'chain_dependency':
            dependencies.extend(
                self._apply_chain(pattern, settings, category_id)
            )
        # ... other patterns

        return dependencies

    def _apply_master_enable(self, pattern: dict, settings: List[dict],
                            category_id: str) -> List[tuple]:
        """Apply master enable pattern"""
        master_pattern = pattern['structure']['master']['id_pattern']
        master_id = master_pattern.replace('{category}', category_id)

        # Find master setting
        master = None
        for setting in settings:
            if setting['id'] == master_id:
                master = setting
                break

        if not master:
            return []

        # All other settings depend on master
        dependencies = []
        for setting in settings:
            if setting['id'] != master_id:
                dependencies.append((
                    setting['id'],
                    'simple',
                    master_id,
                    'enabled'
                ))

        return dependencies

    def _matches_pattern(self, setting_id: str, pattern: str,
                        category_id: str) -> bool:
        """Check if setting ID matches pattern"""
        pattern = pattern.replace('{category}', category_id)
        pattern = pattern.replace('*', '.*')
        return re.match(pattern, setting_id) is not None
```

**Testing:**
- Pattern matching logic
- Pattern application to settings
- Dependency generation from patterns
- Pattern probability selection
- Circular dependency detection
- Solvability validation

**Procedural:** ✓ Patterns applied during generation

---

### 6.5 Error Message Database
**Goal:** Comprehensive library of misleading error messages

**Files:**
- `data/error_messages.json`
- `ui/error_selector.py`
- `tests/test_error_messages.py`

**Error Message Database:**
```json
{
  "error_categories": {
    "locked_setting": {
      "messages": [
        "Cannot modify {setting}: Prerequisite {dependency} not satisfied",
        "{setting} is locked. Check {category} configuration first",
        "Access denied: {setting} requires {dependency} to be in {state} state",
        "Circular dependency detected when enabling {setting}",
        "Configuration conflict: {setting} is incompatible with current state"
      ],
      "hints": [
        "Try enabling {dependency} first",
        "Check the {category} menu for related settings",
        "This setting may require multiple prerequisites",
        "Look for settings with similar names"
      ]
    },
    "invalid_value": {
      "messages": [
        "Value {value} exceeds maximum allowable threshold",
        "{value} conflicts with {related_setting} configuration",
        "Cannot set {setting} to {value}: Out of acceptable range",
        "Value {value} would cause system instability",
        "Rejected: {value} is not a valid configuration"
      ],
      "hints": [
        "Try a value between {min} and {max}",
        "Check {related_setting} for constraints",
        "This setting may have hidden limits"
      ]
    },
    "fake_system_error": {
      "messages": [
        "CRITICAL: {setting} modification triggered failsafe",
        "System integrity check failed after enabling {setting}",
        "Configuration database corruption detected",
        "Unable to persist changes: Write error 0x{code}",
        "Fatal: {setting} caused recursive dependency loop"
      ],
      "hints": [
        "Try restarting the configuration process",
        "This might be a temporary system issue",
        "Check system logs for more details",
        "Contact administrator if problem persists"
      ],
      "fake_hint": true
    },
    "misleading_success": {
      "messages": [
        "{setting} enabled successfully (verification pending)",
        "Change applied. Restart required to take effect",
        "{setting} configured. Synchronizing with other settings...",
        "Setting saved. Background validation in progress",
        "Applied. Note: Some features may not activate immediately"
      ],
      "actually_failed": true
    }
  },
  "context_sensitive_errors": [
    {
      "condition": "too_many_attempts",
      "message": "Maximum retry limit exceeded. Cooling down...",
      "hint": "Wait a moment before trying again",
      "fake": true
    },
    {
      "condition": "rapid_changes",
      "message": "Change rate exceeded. Please slow down.",
      "hint": "System needs time to process each change",
      "fake": true
    },
    {
      "condition": "after_glitch",
      "message": "Settings corrupted. Attempting auto-recovery...",
      "hint": "This may take a few moments",
      "fake": true,
      "show_fake_progress": true
    }
  ]
}
```

**Error Selector:**
```python
import random
from typing import Optional

class ErrorMessageSelector:
    """Selects appropriate error messages"""

    def __init__(self):
        self.error_database = {}
        self.message_history = []

    def load_database(self, database_file: str):
        """Load error message database"""
        import json
        with open(database_file) as f:
            self.error_database = json.load(f)

    def get_error_message(self, error_type: str, context: dict) -> tuple:
        """Get an error message with optional hint"""

        if error_type not in self.error_database['error_categories']:
            return ("An error occurred", None)

        category = self.error_database['error_categories'][error_type]

        # Select message template
        message_template = random.choice(category['messages'])
        message = self._fill_template(message_template, context)

        # Maybe include a hint
        hint = None
        if 'hints' in category and random.random() < 0.6:
            hint_template = random.choice(category['hints'])
            hint = self._fill_template(hint_template, context)

        # Track history
        self.message_history.append({
            'type': error_type,
            'message': message,
            'hint': hint,
            'context': context
        })

        return (message, hint)

    def get_contextual_error(self, context: dict) -> Optional[tuple]:
        """Get context-sensitive error if applicable"""

        contextual = self.error_database.get('context_sensitive_errors', [])

        for error_spec in contextual:
            if self._check_condition(error_spec['condition'], context):
                message = self._fill_template(error_spec['message'], context)
                hint = self._fill_template(error_spec.get('hint', ''), context)
                return (message, hint, error_spec.get('fake', False))

        return None

    def _fill_template(self, template: str, context: dict) -> str:
        """Fill in template variables"""
        result = template
        for key, value in context.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result

    def _check_condition(self, condition: str, context: dict) -> bool:
        """Check if condition is met"""
        if condition == 'too_many_attempts':
            return context.get('attempt_count', 0) > 3
        elif condition == 'rapid_changes':
            return context.get('changes_per_minute', 0) > 10
        elif condition == 'after_glitch':
            return context.get('glitch_occurred', False)
        return False
```

**Testing:**
- Message selection from categories
- Template variable substitution
- Hint inclusion logic
- Context-sensitive error triggering
- Message history tracking
- Fake vs real error distinction

**Procedural:** ✓ Messages loaded from database

---

### 6.6 Hint System
**Goal:** Helpful (and sometimes misleading) hints

**Files:**
- `data/hints.json`
- `ui/hint_display.py`
- `tests/test_hints.py`

**Hint Database:**
```json
{
  "hint_categories": {
    "navigation": {
      "helpful": [
        "Use 'list' or 'ls' to see current menu contents",
        "Type 'goto <menu>' to navigate to a different menu",
        "Press 'back' or 'b' to return to previous menu"
      ],
      "misleading": [
        "Try typing 'unlock all' to bypass dependencies",
        "Some menus are only accessible via secret commands",
        "Certain settings can only be changed in a specific order"
      ]
    },
    "dependencies": {
      "helpful": [
        "Locked settings have dependencies. Check the hint text",
        "Enable prerequisite settings to unlock dependent ones",
        "Dependencies can chain: A requires B requires C"
      ],
      "misleading": [
        "All settings must be enabled in alphabetical order",
        "Disabling a setting may unlock others",
        "Some dependencies are time-based - wait and try again"
      ]
    },
    "progress": {
      "helpful": [
        "Your progress is tracked across all menus",
        "Not all settings need to be enabled to win",
        "Focus on the critical path through menus"
      ],
      "misleading": [
        "You must reach exactly 100% to proceed",
        "Progress can go backwards if you make mistakes",
        "Hidden achievements affect your completion percentage"
      ]
    },
    "meta": {
      "fourth_wall": [
        "Remember: This is a game about settings menus",
        "Not everything works the way it claims to",
        "Some error messages are more error than message",
        "If it seems impossible, it probably is... or isn't"
      ]
    }
  },
  "contextual_hints": [
    {
      "trigger": "stuck_on_menu_for_minutes",
      "threshold": 180,
      "hint": "Can't find the right setting? Try exploring connected menus",
      "helpful": true
    },
    {
      "trigger": "many_failed_attempts",
      "threshold": 5,
      "hint": "That setting requires something else first. Check for locked settings in other menus",
      "helpful": true
    },
    {
      "trigger": "first_locked_encounter",
      "threshold": 1,
      "hint": "Locked settings can be unlocked by satisfying their dependencies",
      "helpful": true
    },
    {
      "trigger": "rapid_clicking",
      "threshold": 10,
      "hint": "Patience is a virtue. So is reading error messages.",
      "helpful": false
    }
  ],
  "tutorial_sequence": [
    {
      "step": 1,
      "trigger": "game_start",
      "hint": "Welcome! Your goal is to enable all the settings. Try 'list' to see what's available.",
      "show_once": true
    },
    {
      "step": 2,
      "trigger": "first_enable",
      "hint": "Good! You enabled your first setting. Notice how it might have affected others.",
      "show_once": true
    },
    {
      "step": 3,
      "trigger": "first_navigation",
      "hint": "You're navigating between menus. Each menu has its own settings and dependencies.",
      "show_once": true
    }
  ]
}
```

**Testing:**
- Hint selection by category
- Contextual hint triggering
- Tutorial sequence progression
- Helpful vs misleading ratio
- Hint cooldown logic
- Show-once tracking

**Procedural:** ✓ Hints loaded from database

---

## Helper Scripts

### Content Validator
**File:** `scripts/validate_all_content.py`
```python
#!/usr/bin/env python3
"""Validate all content files"""

import json
from pathlib import Path

def validate_all():
    errors = []

    # Validate categories
    try:
        with open("data/menu_categories.json") as f:
            categories = json.load(f)
        if len(categories['categories']) != 32:
            errors.append(f"Expected 32 categories, found {len(categories['categories'])}")
    except Exception as e:
        errors.append(f"Category validation failed: {e}")

    # Validate templates exist for all categories
    template_dir = Path("data/setting_templates")
    for cat in categories['categories']:
        template_file = template_dir / f"{cat['id']}_templates.json"
        if not template_file.exists():
            errors.append(f"Missing template file for category: {cat['id']}")

    # Validate Mad Libs pools
    try:
        with open("data/madlibs_pools.json") as f:
            pools = json.load(f)
        required_pools = ['adjectives', 'nouns', 'verbs']
        for pool_name in required_pools:
            if pool_name not in pools['global_pools']:
                errors.append(f"Missing required pool: {pool_name}")
    except Exception as e:
        errors.append(f"Mad Libs validation failed: {e}")

    if errors:
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"  ✗ {error}")
        return False
    else:
        print("✓ All content files valid")
        return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if validate_all() else 1)
```

---

## Testing Strategy

### Content Generation Testing
**File:** `tests/test_content_generation.py`
```python
import pytest
from ready_to_start.generation.pipeline import GenerationPipeline

def test_all_categories_generate():
    """Test that all 32 categories can generate settings"""
    pipeline = GenerationPipeline()

    for seed in range(10):  # Try multiple seeds
        game_state = pipeline.generate(seed=seed)

        # Should have settings from multiple categories
        assert len(game_state.menus) >= 5
        assert len(game_state.settings) >= 50

def test_mad_libs_variety():
    """Test that Mad Libs produces varied output"""
    from ready_to_start.generation.madlibs import MadLibsEngine

    engine = MadLibsEngine()
    engine.load_pools("data/madlibs_pools.json")

    # Generate 100 labels, should have high uniqueness
    labels = [engine.generate_label("audio") for _ in range(100)]
    unique_labels = set(labels)

    assert len(unique_labels) > 80  # At least 80% unique

def test_dependency_patterns_applied():
    """Test that dependency patterns are correctly applied"""
    pipeline = GenerationPipeline()
    game_state = pipeline.generate(seed=42)

    # Should have dependencies
    assert len(game_state.resolver.dependencies) > 0

    # Should have master enable patterns
    master_enables = [
        sid for sid in game_state.settings
        if sid.endswith('_enable')
    ]
    assert len(master_enables) > 0
```

---

## Phase 6 Completion Criteria

- [ ] All 32 menu categories defined
- [ ] Setting templates for each category
- [ ] Mad Libs pools with 500+ entries
- [ ] Themed word pools for each category
- [ ] Dependency pattern library (10+ patterns)
- [ ] Error message database (100+ messages)
- [ ] Hint system (50+ hints)
- [ ] Content validation scripts working
- [ ] Generation produces varied output
- [ ] All content files follow JSON schema
- [ ] 80%+ test coverage for content systems
- [ ] Helper scripts functional
