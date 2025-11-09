import networkx as nx


class GraphAnalyzer:
    @staticmethod
    def find_critical_path(graph: nx.DiGraph) -> list[str]:
        start_nodes = GraphAnalyzer.get_start_nodes(graph)
        end_nodes = GraphAnalyzer.get_end_nodes(graph)

        longest_path = []
        for start in start_nodes:
            for end in end_nodes:
                if nx.has_path(graph, start, end):
                    path = nx.shortest_path(graph, start, end)
                    if len(path) > len(longest_path):
                        longest_path = path

        return longest_path

    @staticmethod
    def get_start_nodes(graph: nx.DiGraph) -> list[str]:
        return [n for n in graph.nodes() if graph.in_degree(n) == 0]

    @staticmethod
    def get_end_nodes(graph: nx.DiGraph) -> list[str]:
        return [n for n in graph.nodes() if graph.out_degree(n) == 0]

    @staticmethod
    def get_reachable_from(graph: nx.DiGraph, start_node: str) -> set[str]:
        descendants = nx.descendants(graph, start_node)
        descendants.add(start_node)
        return descendants
