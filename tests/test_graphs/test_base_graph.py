from __future__ import annotations

import numpy as np
import pytest
from helpers import random_edge_list

from qoolqit.graphs import BaseGraph


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_basegraph_init(n_nodes: int) -> None:

    n_edges = 2 * n_nodes

    edge_list = random_edge_list(n_nodes, n_edges)
    graph = BaseGraph(edge_list)

    # Because a random edge list might leave one disconnected one
    actual_n_nodes = len(graph.nodes)

    max_n_edges = (1 / 2) * actual_n_nodes * (actual_n_nodes - 1)

    assert len(graph.edges) == n_edges
    assert len(graph.ordered_edges) == n_edges
    assert len(graph.ordered_edges) <= max_n_edges
    assert len(graph.distances) == max_n_edges
    assert len(graph.edge_distances) == n_edges
    assert graph.ordered_edges == set(edge_list)
    assert graph.has_edges
    assert not graph.has_coords
    assert graph.min_distance is None
    assert graph.ud_radius is None
    assert len(graph.ud_edges) == 0
    assert not graph.is_ud_graph

    # Now we give the graph a random set of coordinates
    scale = ((n_nodes**0.5) ** 0.5) / 2
    x_coords = np.random.uniform(low=-scale, high=scale, size=(actual_n_nodes,))
    y_coords = np.random.uniform(low=-scale, high=scale, size=(actual_n_nodes,))

    graph.coords = {i: (x, y) for i, x, y in zip(graph.nodes, x_coords, y_coords)}
    graph.ud_radius = 1.0

    assert graph.has_coords
    assert graph.min_distance <= 2 * scale
    assert len(graph.ud_edges) >= 1 and len(graph.ud_edges) <= max_n_edges
    assert not graph.is_ud_graph

    # For a big enough radius the ud-graph is fully connected
    graph.ud_radius = 10.0 * scale
    assert len(graph.ud_edges) == max_n_edges
