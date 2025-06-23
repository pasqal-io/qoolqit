from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from qoolqit.graphs import DataGraph

from ..base_embedder import EmbeddingConfig


@dataclass
class SpringLayoutConfig(EmbeddingConfig):
    """Configuration parameters for the spring-layout embedding."""

    k: float | None = None
    iterations: int = 50
    threshold: float = 1e-4
    seed: int | None = None


def spring_layout_embedding(
    graph: DataGraph,
    k: float | None,
    iterations: int,
    threshold: float,
    seed: int | None,
) -> DataGraph:
    """Force-directed embedding, wrapping nx.spring_layout.

    Generates a graph with the same nodes and edges as the original graph, but with
    node coordinates set to be the positions given by nx.spring_layout.

    Check the documentation for nx.spring_layout for more information on each parameter.

    Arguments:
        graph: the graph to embed.
        k: optimal distance between nodes.
        iterations: maximum number of iterations to take.
        threshold: threshold value for relative error in node position changes.
        sed: random seed.
    """
    output_graph = DataGraph.from_nodes(graph.nodes)
    output_graph.add_edges_from(graph.edges)
    output_graph.coords = nx.spring_layout(
        graph, k=k, iterations=iterations, threshold=threshold, seed=seed
    )
    return output_graph
