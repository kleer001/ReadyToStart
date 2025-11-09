#!/usr/bin/env python3
from pathlib import Path

from src.anti_patterns.engine import AntiPatternEngine
from src.generation.pipeline import GenerationPipeline


def test_anti_patterns():
    print("Generating game state...")
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=42)

    print(f"Generated {len(state.menus)} menus with {len(state.settings)} settings\n")

    ui_state = {}
    engine = AntiPatternEngine(state, ui_state, seed=42)

    config_path = Path(__file__).parent.parent / "config" / "anti_patterns.ini"
    engine.load_from_config(str(config_path))

    print(f"Loaded {len(engine.patterns)} anti-patterns\n")
    print("Testing anti-pattern triggers...\n")

    for i in range(100):
        engine.increment_counter("clicks", 1)
        engine.increment_counter("ui_renders", 1)

        if i % 10 == 0:
            engine.increment_counter("settings_enabled", 1)

        if i % 5 == 0:
            engine.increment_counter("menu_visits", 1)

        engine.update()

        active = engine.get_active_effect_ids()
        if active:
            print(f"Tick {i:3d}: {', '.join(active)}")

    print(f"\nFinal active effects: {engine.get_active_effect_ids()}")
    print(f"\nUI state keys: {list(ui_state.keys())}")

    if "fake_messages" in ui_state:
        print(f"\nFake messages generated: {len(ui_state['fake_messages'])}")
        for msg in ui_state["fake_messages"][:5]:
            print(f"  - {msg['text']}")

    print("\nTesting glitch engine...")
    engine.enable_glitches(0.5)
    sample_texts = [
        "Audio Settings",
        "Graphics Quality: High",
        "Enable V-Sync [X]",
        "Network Configuration",
    ]

    for text in sample_texts:
        glitched = engine.apply_glitch(text)
        if text != glitched:
            print(f"  Original: {text}")
            print(f"  Glitched: {glitched}")

    print("\nAnti-pattern engine test complete!")


if __name__ == "__main__":
    test_anti_patterns()
