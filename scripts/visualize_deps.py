#!/usr/bin/env python3
"""Visualize dependency chains for debugging.

This script prints a text-based representation of setting dependencies.
For graphical visualization, install graphviz or networkx.
"""

from ready_to_start.core.game_state import GameState


def visualize_dependencies_text(state: GameState):
    """Print text-based dependency visualization."""
    print("\n=== Dependency Graph ===\n")

    if not state.resolver.dependencies:
        print("No dependencies defined.")
        return

    for setting_id, deps in state.resolver.dependencies.items():
        setting = state.get_setting(setting_id)
        if setting:
            print(f"{setting.label} ({setting_id})")
            print(f"  Current state: {setting.state.value}")
            print(f"  Can enable: {state.resolver.can_enable(setting_id, state)}")
            print("  Dependencies:")

            for dep in deps:
                if hasattr(dep, "setting_id"):
                    # SimpleDependency
                    req_setting = state.get_setting(dep.setting_id)
                    req_label = req_setting.label if req_setting else dep.setting_id
                    print(
                        f"    - Requires {req_label} to be {dep.required_state.value}"
                    )
                    if req_setting:
                        print(
                            f"      (Currently: {req_setting.state.value}) "
                            f"{'✓' if req_setting.state == dep.required_state else '✗'}"
                        )
                elif hasattr(dep, "operator"):
                    # ValueDependency
                    setting_a = state.get_setting(dep.setting_a)
                    setting_b = state.get_setting(dep.setting_b)
                    label_a = setting_a.label if setting_a else dep.setting_a
                    label_b = setting_b.label if setting_b else dep.setting_b
                    print(f"    - Requires {label_a} {dep.operator} {label_b}")
                    if setting_a and setting_b:
                        result = dep.evaluate(state)
                        print(
                            f"      ({setting_a.value} {dep.operator} "
                            f"{setting_b.value}) {'✓' if result else '✗'}"
                        )
            print()


def visualize_menu_connections(state: GameState):
    """Print text-based menu connection visualization."""
    print("\n=== Menu Connection Graph ===\n")

    for menu_id, menu in state.menus.items():
        print(f"{menu.category} ({menu_id})")
        print(f"  Accessible: {menu.is_accessible(state)}")
        print(f"  Visited: {menu.visited}")
        print(f"  Completion: {menu.calculate_completion().value}")

        if menu.requirements:
            print("  Requirements:")
            for req in menu.requirements:
                setting_id = req.get("setting_id")
                required_state = req.get("state")
                setting = state.get_setting(setting_id)
                if setting:
                    current_state = setting.state.value
                    met = "✓" if current_state == required_state else "✗"
                    print(f"    - {setting.label} = {required_state} {met}")

        if menu.connections:
            print(f"  Connects to: {', '.join(menu.connections)}")

        print()


if __name__ == "__main__":
    # Example usage with generate_test_data
    try:
        from generate_test_data import create_sample_game_state

        print("Loading sample game state...")
        game_state = create_sample_game_state()

        visualize_dependencies_text(game_state)
        visualize_menu_connections(game_state)

    except ImportError:
        print("Error: Could not import generate_test_data")
        print("Run this script from the scripts directory")
