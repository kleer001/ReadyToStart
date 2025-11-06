#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import networkx as nx
import matplotlib.pyplot as plt
from ready_to_start.generation.pipeline import GenerationPipeline


def visualize_generation(seed: int = 42, output_file: str = None):
    pipeline = GenerationPipeline()
    state = pipeline.generate(seed=seed)

    G = nx.DiGraph()
    for menu_id, menu in state.menus.items():
        G.add_node(menu_id, category=menu.category)
        for conn in menu.connections:
            G.add_edge(menu_id, conn)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    categories = {menu.category for menu in state.menus.values()}
    color_map = {}
    colors = plt.cm.Set3(range(len(categories)))
    for i, category in enumerate(categories):
        color_map[category] = colors[i]

    node_colors = [color_map[G.nodes[node]["category"]] for node in G.nodes()]

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=800,
        font_size=8,
        font_weight="bold",
        arrows=True,
        edge_color="gray",
        arrowsize=15,
        alpha=0.9,
    )

    legend_elements = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color_map[cat],
                   markersize=10, label=cat)
        for cat in categories
    ]
    plt.legend(handles=legend_elements, loc="upper left", fontsize=8)

    plt.title(f"Generated Menu Graph (Seed: {seed})")
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        print(f"Saved graph to {output_file}")
    else:
        output_file = f"graph_seed_{seed}.png"
        plt.savefig(output_file, dpi=150, bbox_inches="tight")
        print(f"Saved graph to {output_file}")

    print(f"\nGraph Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Categories: {len(categories)}")
    print(f"  Settings: {len(state.settings)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize generated menu graph")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("-o", "--output", type=str, help="Output file path")
    args = parser.parse_args()

    visualize_generation(args.seed, args.output)
