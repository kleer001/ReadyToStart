#!/usr/bin/env python3

from src.core.evaluator import DependencyEvaluator
from src.core.progress import ProgressCalculator
from src.core.propagation import StatePropagator
from src.generation.pipeline import GenerationPipeline


def test_game_logic():
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=42)

    evaluator = DependencyEvaluator(state)
    propagator = StatePropagator(state, evaluator)
    progress = ProgressCalculator(state, evaluator)

    print("=" * 60)
    print("GAME LOGIC TEST")
    print("=" * 60)

    print("\n[Dependency Evaluation]")
    results = evaluator.evaluate_all()
    print(f"  Total settings: {len(results)}")
    print(f"  Can enable: {sum(1 for r in results.values() if r.can_enable)}")
    print(f"  Blocked: {sum(1 for r in results.values() if not r.can_enable)}")

    blocked_example = next(
        (r for r in results.values() if not r.can_enable and r.blocking_deps), None
    )
    if blocked_example:
        print(f"\n  Example blocked setting: {blocked_example.setting_id}")
        print(f"  Reason: {blocked_example.reason}")

    print("\n[State Propagation]")
    if state.settings:
        first_setting_id = list(state.settings.keys())[0]
        first_setting = state.settings[first_setting_id]
        print(f"  Testing propagation from: {first_setting_id}")
        affected = propagator.propagate(first_setting_id)
        print(f"  Affected settings: {len(affected)}")
        if affected:
            print(f"  First affected: {affected[0]}")

    print("\n[Progress Calculation]")
    overall = progress.calculate_overall_progress()
    critical = progress.get_critical_path_progress()
    victory = progress.is_victory_condition_met()
    print(f"  Overall progress: {overall:.1f}%")
    print(f"  Critical path: {critical:.1f}%")
    print(f"  Victory condition: {'✓ Met' if victory else '✗ Not met'}")

    print("\n[Menu Completion]")
    for menu_id in list(state.menus.keys())[:3]:
        completion = progress.calculate_menu_completion(menu_id)
        print(f"  {menu_id}: {completion.value}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_game_logic()
