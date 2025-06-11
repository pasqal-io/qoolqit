from __future__ import annotations

import networkx as nx

from qoolqit.graphs import DataGraph


def spring_layout_embedding(
    graph: DataGraph,
    k: float,
    iterations: int,
    threshold: float,
) -> dict:
    """Wraps the networkx spring layout algorithm."""
    coordinates: dict = nx.spring_layout(graph, k=k, iterations=iterations, threshold=threshold)
    return coordinates
