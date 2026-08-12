from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np
import pytest
from scipy.spatial.distance import pdist, squareform
from torch_geometric.data import Data

from qoolqit.graphs import BaseGraph, random_coords, random_edge_list


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_basegraph_init(n_nodes: int) -> None:

    n_edges = 2 * n_nodes

    edge_list = random_edge_list(range(n_nodes), n_edges)
    graph = BaseGraph(edge_list)

    # Because a random edge list might leave one disconnected one
    actual_n_nodes = len(graph.nodes)

    max_n_edges = (1 / 2) * actual_n_nodes * (actual_n_nodes - 1)

    assert len(graph.edges) == n_edges
    assert len(graph.sorted_edges) == n_edges
    assert len(graph.sorted_edges) <= max_n_edges
    assert graph.sorted_edges == set(edge_list)
    assert graph.has_edges
    assert not graph.has_coords

    with pytest.raises(AttributeError):
        graph.distances()

    with pytest.raises(AttributeError):
        graph.min_distance()

    with pytest.raises(AttributeError):
        graph.max_distance()

    no_coords_match = "Trying to compute distances for a graph without coordinates."

    with pytest.raises(AttributeError, match=no_coords_match):
        graph.interactions()

    with pytest.raises(AttributeError, match=no_coords_match):
        graph.interaction_matrix()

    with pytest.raises(AttributeError):
        graph.is_ud_graph()

    with pytest.raises(AttributeError):
        graph.ud_edges(radius=1.0)

    with pytest.raises(AttributeError):
        graph.set_ud_edges(radius=1.0)

    # Now we give the graph a random set of coordinates
    scale = ((actual_n_nodes**0.5) ** 0.5) / 2
    coords = random_coords(actual_n_nodes, scale)

    graph.coords = {i: pos for i, pos in zip(graph.nodes, coords)}

    assert graph.has_coords
    assert graph.max_distance() <= 2 * scale
    assert len(graph.ud_edges(radius=0.0)) == 0
    assert len(graph.ud_edges(radius=1.0)) >= 1
    assert len(graph.ud_edges(radius=10.0 * scale)) == max_n_edges


@pytest.mark.parametrize("n_nodes", [3, 8, 13])
def test_basegraph_interactions(n_nodes: int) -> None:

    rng = np.random.default_rng(0)
    coords_array = rng.uniform(-1, 1, size=(n_nodes, 2))
    graph = BaseGraph.from_coordinates([c for c in coords_array])

    expected_interactions = {
        (i, j): np.linalg.norm(coords_array[i] - coords_array[j]) ** (-6)
        for i in range(n_nodes)
        for j in range(i + 1, n_nodes)
    }
    expected_interaction_matrix = squareform(1 / pdist(coords_array) ** 6)

    interactions = graph.interactions()
    assert isinstance(interactions, dict)
    for (u, v), interaction in expected_interactions.items():
        np.testing.assert_allclose(interactions[(u, v)], interaction, atol=1e-8)

    np.testing.assert_allclose(graph.interaction_matrix(), expected_interaction_matrix, atol=1e-8)


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_basegraph_constructors(n_nodes: int) -> None:
    scale = ((n_nodes**0.5) ** 0.5) / 2
    node_set = set(np.random.randint(1, 1000, size=n_nodes).tolist())
    coords = {i: pos for i, pos in zip(node_set, random_coords(n_nodes, scale))}

    graph1 = BaseGraph.from_nodes(node_set)
    graph2 = BaseGraph.from_coordinates(coords)

    for graph in [graph1, graph2]:
        assert len(graph.edges) == 0
        assert len(graph.sorted_edges) == 0
        assert not graph.has_edges

    assert not graph1.has_coords
    assert graph2.has_coords

    # Set graph1 to have the same coordinates as graph2
    graph1.coords = coords
    random_edges = random_edge_list(node_set, k=5)

    graph1.add_edges_from(random_edges)
    graph2.add_edges_from(random_edges)

    for connected in [True, False, None]:
        assert np.isclose(graph1.min_distance(connected), graph2.min_distance(connected))
        assert np.isclose(graph1.max_distance(connected), graph2.max_distance(connected))

    radius = np.random.uniform(0.0, 1.0)

    assert graph1.ud_edges(radius) == graph2.ud_edges(radius)

    # Rescale the coordinates of graph1 by a constant factor
    graph1.rescale_coords(scaling=0.5)

    for connected in [True, False, None]:
        assert np.isclose(graph1.min_distance(connected), 0.5 * graph2.min_distance(connected))
        assert np.isclose(graph1.max_distance(connected), 0.5 * graph2.max_distance(connected))

    assert len(graph1.ud_edges(radius)) >= len(graph2.ud_edges(radius))

    # Respace them so the minimum distance is equal to a constant factor
    graph1.rescale_coords(spacing=radius)
    assert np.isclose(graph1.min_distance(), radius)

    # Since we used the UD radius value, all edges in the UD set are
    # now expected to have exactly this minimum distance
    for edge in graph1.ud_edges(radius):
        assert np.isclose(graph2.distances()[edge], graph2.min_distance())

    # Reset our changes, and rescale again
    graph1.rescale_coords(spacing=graph2.min_distance())  # type: ignore [arg-type]
    graph1.rescale_coords(scaling=0.5)

    # Reset edges in both graphs to be equal to their UD sets
    graph1.set_ud_edges(radius)
    graph2.set_ud_edges(radius)

    assert graph1.is_ud_graph()
    assert graph2.is_ud_graph()


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_from_matrix(n_nodes: int) -> None:
    np.random.seed(0)
    data = np.random.rand(n_nodes, n_nodes)

    with pytest.raises(ValueError):
        # Matrix is not symmetric
        graph = BaseGraph.from_matrix(data)

    data = data + data.T
    data_copy = data.copy()  # Make a copy to test the original data

    graph = BaseGraph.from_matrix(data)

    # Check input data matrix has not been modified
    np.testing.assert_equal(data, data_copy)

    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert graph.has_node_weights
    assert graph.has_edge_weights

    data_diag = np.diag(data)
    node_weights = list(graph.node_weights.values())
    np.testing.assert_allclose(node_weights, data_diag)

    # Build a fresh matrix for the second sub-test: zero out the diagonal and some random edges
    almost_zero = 1e-14
    data2 = data_copy.copy()
    np.fill_diagonal(data2, almost_zero)
    random_edges_removal = random_edge_list(range(n_nodes), k=4)
    i_list, j_list = zip(*random_edges_removal)
    data2[i_list, j_list] = almost_zero
    data2[j_list, i_list] = almost_zero

    graph = BaseGraph.from_matrix(data2)

    assert not graph.has_node_weights
    assert graph.has_edge_weights

    for edge in random_edges_removal:
        assert edge not in graph.sorted_edges

    n_edges = graph.number_of_edges()
    idx = [2 * i for i in range(n_edges)]

    data_edge_weights = np.sort(data2[data2 >= 1e-7])[idx]
    edge_weights = sorted(list(graph.edge_weights.values()))

    np.testing.assert_allclose(edge_weights, data_edge_weights)


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_to_matrix_unweighted(n_nodes: int) -> None:
    graph = BaseGraph.from_nodes(range(n_nodes))
    graph.add_edges_from(random_edge_list(range(n_nodes), k=2 * n_nodes))
    # FIXME: _edge_weights is a snapshot that goes stale after add_edges_from;
    # see issue #431 (edge_weights does not reflect edges added after construction).
    graph._reset_dicts()
    assert not graph.has_node_weights
    assert not graph.has_edge_weights

    matrix = graph.to_matrix()

    np.testing.assert_equal(matrix, matrix.T)
    np.testing.assert_equal(np.diag(matrix), np.zeros(n_nodes))

    for i, j in graph.sorted_edges:
        assert matrix[i, j] == 1.0
        assert matrix[j, i] == 1.0

    non_edges = graph.all_node_pairs - graph.sorted_edges
    for i, j in non_edges:
        assert matrix[i, j] == 0.0
        assert matrix[j, i] == 0.0


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_to_matrix_weighted(n_nodes: int) -> None:
    graph = BaseGraph.from_nodes(range(n_nodes))
    graph.add_edges_from(random_edge_list(range(n_nodes), k=2 * n_nodes))
    graph.node_weights = {i: np.random.rand() for i in graph.nodes}
    graph.edge_weights = {e: np.random.rand() for e in graph.sorted_edges}

    matrix = graph.to_matrix()

    np.testing.assert_equal(matrix, matrix.T)
    np.testing.assert_allclose(np.diag(matrix), list(graph.node_weights.values()))

    for (i, j), weight in graph.edge_weights.items():
        assert matrix[i, j] == weight
        assert matrix[j, i] == weight


@pytest.mark.parametrize("n_nodes", [3, 7, 21])
@pytest.mark.parametrize("seed", [12345, 5481], ids=[f"seed{i}" for i in range(2)])
def test_to_matrix_roundtrip(n_nodes: int) -> None:
    rng = np.random.default_rng(12345)
    matrix = rng.normal(0, 1, size=(n_nodes, n_nodes))
    # zero out some elements for testing
    rows, cols = rng.integers(n_nodes, size=3), rng.integers(n_nodes, size=3)
    matrix[rows, cols] = 0.0
    matrix[cols, rows] = 0.0
    matrix += matrix.T

    graph = BaseGraph.from_matrix(matrix)
    np.testing.assert_allclose(graph.to_matrix(), matrix, atol=1e-8)


def test_to_matrix_custom_node_labels_and_none_weights() -> None:
    # Ensure `to_matrix()` respects `self.nodes` ordering and handles None weights.
    # Also ensures it works with non-0..N-1 node labels.
    graph = BaseGraph.from_nodes(["b", "a", "c"])  # preserve explicit order
    graph.add_edges_from([("b", "a"), ("a", "c")])

    # Mix of real weights and None
    graph.node_weights = {"b": 2.0, "a": None, "c": -3.0}
    # NOTE: order is not guaranteed because BaseGraph maintains arbitrarily sorted edges
    graph.edge_weights = {("a", "b"): None, ("a", "c"): 0.25}

    matrix = graph.to_matrix()
    expected = np.array(
        [
            [2.0, 1.0, 0.0],
            [1.0, 0.0, 0.25],
            [0.0, 0.25, -3.0],
        ],
    )
    np.testing.assert_equal(matrix, expected)


@pytest.mark.parametrize("input", ["hello", Data()])
def test_from_nx_wrong_input(input: Any) -> None:
    with pytest.raises(TypeError, match="Input must be a networkx.Graph instance."):
        BaseGraph.from_nx(input)


@pytest.mark.parametrize("wrong_node_attr", [{"hello": 1.0}, {"pos": (1.0, 1.0), "world": 3.0}])
def test_from_wrong_node_attrs_name(wrong_node_attr: Any) -> None:
    G = nx.Graph()
    G.add_node(0, **wrong_node_attr)
    G.add_node(1, **wrong_node_attr)
    with pytest.raises(ValueError, match="not allowed in node attributes."):
        BaseGraph.from_nx(G)


@pytest.mark.parametrize("wrong_edge_attr", [{"hello": 1.0}, {"weight": (1.0, 1.0), "world": 3.0}])
def test_from_wrong_edge_attrs_name(wrong_edge_attr: Any) -> None:
    G = nx.Graph()
    G.add_edge(0, 1, **wrong_edge_attr)
    G.add_edge(1, 2, **wrong_edge_attr)
    with pytest.raises(ValueError, match="not allowed in edge attributes."):
        BaseGraph.from_nx(G)


def test_from_nx() -> None:
    """Test importing a NetworkX graph without any weights or positions."""
    G = nx.triangular_lattice_graph(1, 2, with_positions=False)
    g = BaseGraph.from_nx(G)

    # Check whether we copied nodes and edges correctly
    assert set(g.nodes) == set(range(4))
    assert set(g.edges) == set([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)])

    # Check whether the coords exist and are all None
    assert all(v is None for v in g._coords.values())
    assert all(v is None for v in g._node_weights.values())
    assert all(v is None for v in g._edge_weights.values())


def test_from_nx_with_weights_and_pos() -> None:
    """Test importing a NetworkX graph that has node/edge weights and positions."""
    G = nx.Graph()

    G.add_node(0, weight=1.0, pos=(0.0, 0.0))
    G.add_node(1, weight=2.0, pos=(1.0, 0.0))
    G.add_node(2, weight=3.0, pos=(0.5, 1.0))

    G.add_edge(0, 1, weight=0.1)
    G.add_edge(1, 2, weight=0.2)
    G.add_edge(2, 0, weight=0.3)

    g = BaseGraph.from_nx(G)

    assert set(g.nodes) == {0, 1, 2}
    assert set(g.edges) == {(0, 1), (1, 2), (0, 2)}

    assert g._node_weights == {0: 1.0, 1: 2.0, 2: 3.0}
    assert g._edge_weights == {(0, 1): 0.1, (1, 2): 0.2, (0, 2): 0.3}

    assert g._coords == {
        0: (0.0, 0.0),
        1: (1.0, 0.0),
        2: (0.5, 1.0),
    }


def test_from_nx_not_all_node_weights() -> None:
    G = nx.Graph()
    G.add_node(0, weight=1.0)
    G.add_node(1)  # missing weight
    G.add_edge(0, 1, weight=0.5)

    with pytest.raises(ValueError, match="Node attribute `weight` must be defined for all nodes"):
        BaseGraph.from_nx(G)


def test_from_nx_not_all_edges_weights() -> None:
    G = nx.Graph()
    G.add_node(0, weight=1.0)
    G.add_node(1, weight=2.0)
    G.add_node(2, weight=2.0)
    G.add_edge(0, 1, weight=0.5)
    G.add_edge(0, 2)  # missing weight

    with pytest.raises(ValueError, match="Edge attribute `weight` must be defined for all edges"):
        BaseGraph.from_nx(G)


def test_from_nx_not_all_pos() -> None:
    G = nx.Graph()
    G.add_node(0, pos=(1.0, 0))
    G.add_node(1)  # missing pos
    G.add_edge(0, 1, weight=0.5)

    with pytest.raises(ValueError, match="Node attribute `pos` must be defined for all nodes"):
        BaseGraph.from_nx(G)


@pytest.mark.parametrize("wrong_node_weight", ["hello", [1, 2, 3], 2j])
def test_from_nx_wrong_node_weight(wrong_node_weight: Any) -> None:
    """Test that non-numeric node weights raise TypeError."""
    G = nx.Graph()
    G.add_node(0, weight=wrong_node_weight)
    G.add_node(1, weight=3.0)
    G.add_edge(0, 1, weight=0.5)

    with pytest.raises(
        TypeError,
        match="In node 0 the `weight` attribute must be a real number",
    ):
        BaseGraph.from_nx(G)


@pytest.mark.parametrize("wrong_edge_weight", ["hello", [1, 2, 3], 2j])
def test_from_nx_edge_weight_type(wrong_edge_weight: Any) -> None:
    """Test that non-numeric node weights raise TypeError."""
    G = nx.Graph()
    G.add_node(0, weight=1.0)
    G.add_node(1, weight=2.0)
    G.add_edge(0, 1, weight=wrong_edge_weight)
    G.add_edge(1, 0)

    with pytest.raises(
        TypeError,
        match=r"In edge \(0, 1\), the attribute `weight` must be a real number",
    ):
        BaseGraph.from_nx(G)


@pytest.mark.parametrize(
    "wrong_node_pos", ["hello", ("hello", "world"), (1.0, 2.0, 3.0), (1.0, 2.0j)]
)
def test_from_nx_wrong_pos_attr(wrong_node_pos: Any) -> None:
    """Test that non-tuple/list positions raise TypeError."""
    G = nx.Graph()
    G.add_node(0, weight=1.0, pos=wrong_node_pos)
    G.add_node(1, weight=2.0, pos=(1.0, 1.0))
    G.add_edge(0, 1, weight=0.5)

    with pytest.raises(
        TypeError,
        match="In node 0 the `pos` attribute must be a 2D tuple/list of real numbers",
    ):
        BaseGraph.from_nx(G)
