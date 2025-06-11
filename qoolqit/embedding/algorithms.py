from __future__ import annotations

from dataclasses import asdict

import networkx as nx

from qoolqit.graphs import DataGraph

from .configs import SpringLayoutConfig


def spring_layout_embedding(graph: DataGraph, config: SpringLayoutConfig) -> dict:
    """Wraps the networkx spring layout algorithm."""
    coordinates: dict = nx.spring_layout(graph, **asdict(config))
    return coordinates
