from __future__ import annotations

import numpy as np
import pytest
from helpers import random_coords, random_edge_list

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
    scale = ((actual_n_nodes**0.5) ** 0.5) / 2
    coords = random_coords(actual_n_nodes, scale)

    graph.coords = {i: pos for i, pos in zip(graph.nodes, coords)}
    graph.ud_radius = 1.0

    assert graph.has_coords
    assert graph.min_distance <= 2 * scale
    assert len(graph.ud_edges) >= 1 and len(graph.ud_edges) <= max_n_edges

    # For a big enough radius the ud-graph is fully connected
    graph.ud_radius = 10.0 * scale
    assert len(graph.ud_edges) == max_n_edges


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_basegraph_constructors(n_nodes: int) -> None:
    scale = ((n_nodes**0.5) ** 0.5) / 2
    node_set = set(np.random.randint(1, 1000, size=n_nodes))
    coords = {i: pos for i, pos in zip(node_set, random_coords(n_nodes, scale))}

    graph1 = BaseGraph.from_nodes(node_set)
    graph2 = BaseGraph.from_coordinates(coords)

    for graph in [graph1, graph2]:
        assert len(graph.edges) == 0
        assert len(graph.ordered_edges) == 0
        assert len(graph.edge_distances) == 0
        assert not graph.has_edges

    assert not graph1.has_coords
    assert graph2.has_coords

    # Set graph1 to have the same coordinates as graph2
    graph1.coords = coords
    graph1.ud_radius = 1.0
    graph2.ud_radius = 1.0

    assert len(graph1.ud_edges) > 0 and len(graph2.ud_edges) > 0
    assert np.isclose(graph1.min_distance, graph2.min_distance)
    assert graph1.ud_edges == graph2.ud_edges

    # Rescale the coordinates of graph1 by a constant factor
    graph1.rescale_coords(scaling=0.5)
    assert np.isclose(graph1.min_distance, 0.5 * graph2.min_distance)  # type: ignore [operator]
    assert len(graph1.ud_edges) >= len(graph2.ud_edges)

    # Respace them so the minimum distance is equal to a constant factor
    graph1.respace_coords(spacing=1.0)
    assert np.isclose(graph1.min_distance, 1.0)

    # Since we used the UD radius value, all edges in the UD set are
    # now expected to have exactly this minimum distance
    for edge in graph1.ud_edges:
        assert np.isclose(graph2.distances[edge], graph2.min_distance)

    # Reset our changes, and rescale again
    graph1.respace_coords(spacing=graph2.min_distance)  # type: ignore [arg-type]
    graph1.rescale_coords(scaling=0.5)

    # Reset edges in both graphs to be equal to their UD sets
    graph1.set_edges_ud()
    graph2.set_edges_ud()

    assert graph1.is_ud_graph
    assert graph2.is_ud_graph
