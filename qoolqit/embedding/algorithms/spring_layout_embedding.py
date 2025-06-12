from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from qoolqit.graphs import DataGraph

from ..base_embedder import EmbeddingConfig


@dataclass
class SpringLayoutConfig(EmbeddingConfig):
    """Configuration parameters for the spring-layout embedding."""

    """Optimal distance between nodes."""
    k: float | None = None

    """Maximum number of iterations taken."""
    iterations: int = 50

    """Threshold for relative error in node position changes."""
    threshold: float = 1e-4


def spring_layout_embedding(
    graph: DataGraph,
    k: float,
    iterations: int,
    threshold: float,
) -> dict:
    """Wraps the networkx spring layout algorithm."""
    coordinates: dict = nx.spring_layout(graph, k=k, iterations=iterations, threshold=threshold)
    return coordinates
