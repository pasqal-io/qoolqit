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


def test_triangular() -> None:
    graph = DataGraph.triangular(2, 2, spacing=2.71)

    expected_coords = {
        0: (0.0, 0.0),
        1: (1.355, 2.3469288442558285),
        2: (0.0, 4.693857688511657),
        3: (2.71, 0.0),
        4: (4.0649999999999995, 2.3469288442558285),
        5: (2.71, 4.693857688511657),
    }
    for k, v in graph.coords.items():
        assert np.allclose(v, expected_coords[k])

    edges = graph.sorted_edges
    expected_edges = {(0, 1), (0, 3), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (3, 4), (4, 5)}
    assert edges == expected_edges


def test_hexagonal() -> None:
    graph = DataGraph.hexagonal(2, 2, spacing=5.0)

    expected_coords = {
        0: (2.5, 0.0),
        1: (0.0, 4.330127018922193),
        2: (2.5, 8.660254037844386),
        3: (0.0, 12.99038105676658),
        4: (2.5, 17.32050807568877),
        5: (7.5, 0.0),
        6: (10.0, 4.330127018922193),
        7: (7.5, 8.660254037844386),
        8: (10.0, 12.99038105676658),
        9: (7.5, 17.32050807568877),
        10: (10.0, 21.650635094610962),
        11: (15.0, 4.330127018922193),
        12: (17.5, 8.660254037844386),
        13: (15.0, 12.99038105676658),
        14: (17.5, 17.32050807568877),
        15: (15.0, 21.650635094610962),
    }
    for k, v in graph.coords.items():
        assert np.allclose(v, expected_coords[k])

    edges = graph.sorted_edges
    expected_edges = {
        (0, 1),
        (0, 5),
        (1, 2),
        (2, 3),
        (2, 7),
        (3, 4),
        (4, 9),
        (5, 6),
        (6, 7),
        (6, 11),
        (7, 8),
        (8, 9),
        (8, 13),
        (9, 10),
        (10, 15),
        (11, 12),
        (12, 13),
        (13, 14),
        (14, 15),
    }
    assert edges == expected_edges
