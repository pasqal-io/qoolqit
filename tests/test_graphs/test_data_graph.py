from __future__ import annotations

import numpy as np
import pytest

from qoolqit.graphs import DataGraph, random_edge_list
from qoolqit.utils import ATOL_64


@pytest.mark.parametrize("graph_type", ["circle", "line", "random_ud"])
@pytest.mark.parametrize("n_nodes", [10, 20, 30, 40, 50])
def test_datagraph_unit_disk(n_nodes: int, graph_type: str) -> None:

    spacing = 1.0

    if graph_type == "circle":
        graph = DataGraph.circle(n_nodes, spacing=spacing)
        circle_edges = set((i, i + 1) for i in range(n_nodes - 1)).union(set([(0, n_nodes - 1)]))
        assert graph.sorted_edges == circle_edges
        assert np.isclose(graph.min_distance(), spacing)
    if graph_type == "line":
        graph = DataGraph.line(n_nodes, spacing=spacing)
        line_edges = set((i, i + 1) for i in range(n_nodes - 1))
        assert graph.sorted_edges == line_edges
        assert np.isclose(graph.min_distance(), spacing)
    if graph_type == "random_ud":
        graph = DataGraph.random_ud(n_nodes)

    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert not graph.has_node_weights
    assert not graph.has_edge_weights
    assert graph.is_ud_graph()

    # Save a radius value where the graph is unit-disk
    rmin, rmax = graph.ud_radius_range()
    radius = np.random.uniform(rmin, rmax)

    original_edges = graph.sorted_edges
    graph.set_ud_edges(radius=0.0)
    assert len(graph.sorted_edges) == 0
    graph.set_ud_edges(radius=radius)
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

    with pytest.raises(AttributeError):
        graph.distances()
    with pytest.raises(AttributeError):
        graph.min_distance()


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

    data_diag = np.diag(data)
    node_weights = list(graph.node_weights.values())
    assert np.allclose(node_weights, data_diag)

    # Remove diagonal and some random values from the data
    almost_zero = ATOL_64

    np.fill_diagonal(data, almost_zero)

    random_edges_removal = random_edge_list(range(n_nodes), k=4)

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
