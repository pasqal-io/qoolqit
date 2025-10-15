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
        1: (2.71, 0.0),
        2: (1.355, 2.3469288442558285),
        3: (4.0649999999999995, 2.3469288442558285),
        4: (0.0, 4.693857688511657),
        5: (2.71, 4.693857688511657),
    }

    for k, v in graph.coords.items():
        assert np.allclose(v, expected_coords[k])

    edges = graph.sorted_edges
    expected_edges = {(0, 1), (0, 2), (1, 3), (1, 2), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5)}

    assert edges == expected_edges


def test_hexagonal() -> None:
    graph = DataGraph.hexagonal(2, 2, spacing=3.0)

    expected_coords = {
        0: (1.5, 0.0),
        1: (0.0, 2.598076211353316),
        2: (1.5, 5.196152422706632),
        3: (0.0, 7.794228634059948),
        4: (1.5, 10.392304845413264),
        5: (4.5, 0.0),
        6: (6.0, 2.598076211353316),
        7: (4.5, 5.196152422706632),
        8: (6.0, 7.794228634059948),
        9: (4.5, 10.392304845413264),
        10: (6.0, 12.990381056766578),
        11: (9.0, 2.598076211353316),
        12: (10.5, 5.196152422706632),
        13: (9.0, 7.794228634059948),
        14: (10.5, 10.392304845413264),
        15: (9.0, 12.990381056766578),
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


def test_square() -> None:
    graph = DataGraph.square(4, 4, spacing=2.71)

    expected_coords = {
        0: (0.0, 0.0),
        1: (0.0, 2.71),
        2: (0.0, 5.42),
        3: (0.0, 8.13),
        4: (2.71, 0.0),
        5: (2.71, 2.71),
        6: (2.71, 5.42),
        7: (2.71, 8.13),
        8: (5.42, 0.0),
        9: (5.42, 2.71),
        10: (5.42, 5.42),
        11: (5.42, 8.13),
        12: (8.13, 0.0),
        13: (8.13, 2.71),
        14: (8.13, 5.42),
        15: (8.13, 8.13),
    }

    for k, v in graph.coords.items():
        assert np.allclose(v, expected_coords[k])

    edges = graph.sorted_edges

    expected_edges = {
        (0, 1),
        (1, 2),
        (2, 3),
        (4, 5),
        (5, 6),
        (6, 7),
        (8, 9),
        (9, 10),
        (10, 11),
        (12, 13),
        (13, 14),
        (14, 15),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
        (4, 8),
        (5, 9),
        (6, 10),
        (7, 11),
        (8, 12),
        (9, 13),
        (10, 14),
        (11, 15),
    }
    assert edges == expected_edges


def test_heavy_hexagonal() -> None:
    graph = DataGraph.heavy_hexagonal(2, 2, spacing=1.6)

    expected_coords = {
        0: (1.6, 0.0),
        1: (0.8, 1.3856406460551018),
        2: (0.0, 2.7712812921102037),
        3: (0.8, 4.156921938165306),
        4: (1.6, 5.542562584220407),
        5: (0.8, 6.92820323027551),
        6: (0.0, 8.313843876330612),
        7: (0.8, 9.699484522385713),
        8: (1.6, 11.085125168440815),
        9: (3.2, 0.0),
        10: (3.2, 5.542562584220407),
        11: (3.2, 11.085125168440815),
        12: (4.800000000000001, 0.0),
        13: (5.6000000000000005, 1.3856406460551018),
        14: (6.4, 2.7712812921102037),
        15: (5.6000000000000005, 4.156921938165306),
        16: (4.800000000000001, 5.542562584220407),
        17: (5.6000000000000005, 6.92820323027551),
        18: (6.4, 8.313843876330612),
        19: (5.6000000000000005, 9.699484522385713),
        20: (4.800000000000001, 11.085125168440815),
        21: (5.6000000000000005, 12.470765814495916),
        22: (6.4, 13.856406460551018),
        23: (8.0, 2.7712812921102037),
        24: (8.0, 8.313843876330612),
        25: (8.0, 13.856406460551018),
        26: (9.600000000000001, 2.7712812921102037),
        27: (10.400000000000002, 4.156921938165306),
        28: (11.200000000000001, 5.542562584220407),
        29: (10.400000000000002, 6.92820323027551),
        30: (9.600000000000001, 8.313843876330612),
        31: (10.400000000000002, 9.699484522385713),
        32: (11.200000000000001, 11.085125168440815),
        33: (10.400000000000002, 12.470765814495916),
        34: (9.600000000000001, 13.856406460551018),
    }
    for k, v in graph.coords.items():
        assert np.allclose(v, expected_coords[k])

    edges = graph.sorted_edges
    expected_edges = {
        (0, 1),
        (0, 9),
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
        (4, 10),
        (5, 6),
        (6, 7),
        (7, 8),
        (8, 11),
        (9, 12),
        (10, 16),
        (11, 20),
        (12, 13),
        (13, 14),
        (14, 15),
        (14, 23),
        (15, 16),
        (16, 17),
        (17, 18),
        (18, 19),
        (18, 24),
        (19, 20),
        (20, 21),
        (21, 22),
        (22, 25),
        (23, 26),
        (24, 30),
        (25, 34),
        (26, 27),
        (27, 28),
        (28, 29),
        (29, 30),
        (30, 31),
        (31, 32),
        (32, 33),
        (33, 34),
    }
    assert edges == expected_edges
