from __future__ import annotations

import numpy as np
import pytest
from helpers import random_edge_list

from qoolqit.graphs import DataGraph
from qoolqit.utils import ATOL_64


@pytest.mark.parametrize("graph_type", ["circle", "line", "random_ud"])
@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_unit_disk(n_nodes: int, graph_type: str) -> None:

    spacing = 1.0
    ud_radius = 1.0

    if graph_type == "circle":
        graph = DataGraph.circle(n_nodes, spacing=spacing, ud_radius=ud_radius)
        circle_edges = set((i, i + 1) for i in range(n_nodes - 1)).union(set([(0, n_nodes - 1)]))
        assert graph.sorted_edges == circle_edges
        assert np.isclose(graph.min_distance, spacing)
    if graph_type == "line":
        graph = DataGraph.line(n_nodes, spacing=spacing, ud_radius=ud_radius)
        line_edges = set((i, i + 1) for i in range(n_nodes - 1))
        assert graph.sorted_edges == line_edges
        assert np.isclose(graph.min_distance, spacing)
    if graph_type == "random_ud":
        graph = DataGraph.random_ud(n_nodes, ud_radius=ud_radius)

    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert not graph.has_node_weights
    assert not graph.has_edge_weights
    assert graph.is_ud_graph

    original_edges = graph.sorted_edges
    graph.ud_radius = 0.0
    graph.set_edges_ud()
    assert len(graph.edges) == 0
    graph.ud_radius = ud_radius
    graph.set_edges_ud()
    assert graph.sorted_edges == original_edges

    graph.node_weights = {i: np.random.rand() for i in graph.nodes}
    graph.edge_weights = {e: np.random.rand() for e in graph.sorted_edges}

    assert graph.has_node_weights
    assert graph.has_edge_weights


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_random_er(n_nodes: int) -> None:
    graph = DataGraph.random_er(n_nodes, p=0.5)
    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert not graph.has_node_weights
    assert not graph.has_node_weights
    assert not graph.is_ud_graph


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_from_matrix(n_nodes: int) -> None:

    data = np.random.rand(n_nodes, n_nodes)

    with pytest.raises(ValueError):
        # Matrix is not symmetric
        graph = DataGraph.from_matrix(data)

    data = data + data.T

    graph = DataGraph.from_matrix(data)

    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert graph.has_node_weights
    assert graph.has_edge_weights
    assert not graph.is_ud_graph

    data_diag = np.diag(data)
    node_weights = list(graph.node_weights.values())
    assert np.allclose(node_weights, data_diag)

    # Remove diagonal and some random values from the data
    almost_zero = ATOL_64

    np.fill_diagonal(data, almost_zero)

    random_edges_removal = random_edge_list(n_nodes, k=4)

    i_list, j_list = zip(*random_edges_removal)

    data[i_list, j_list] = almost_zero
    data[j_list, i_list] = almost_zero

    graph = DataGraph.from_matrix(data)

    assert not graph.has_node_weights
    assert graph.has_edge_weights

    for edge in random_edges_removal:
        assert edge not in graph.sorted_edges

    n_edges = graph.number_of_edges()
    idx = [2 * i for i in range(n_edges)]

    data_edge_weights = np.sort(data[data.nonzero()])[idx]
    edge_weights = sorted(list(graph.edge_weights.values()))

    assert np.allclose(edge_weights, data_edge_weights)
