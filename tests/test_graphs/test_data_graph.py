from __future__ import annotations

import networkx as nx
import numpy as np
import pytest
import torch
from torch_geometric.data import Data

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


# ---------------------------------------------------------------------------
# PyG conversion tests (from_pyg / to_pyg)
# ---------------------------------------------------------------------------


def test_from_pyg_wrong_input() -> None:
    with pytest.raises(TypeError, match="Input must be a torch_geometric.data.Data object."):
        DataGraph.from_pyg("hello")


def test_from_pyg_only_edges() -> None:
    """Test importing a PyG Data with only edge_index (no weights or positions)."""
    edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]])
    data = Data(edge_index=edge_index, num_nodes=3)

    g = DataGraph.from_pyg(data)

    assert set(g.nodes) == {0, 1, 2}
    assert all(v is None for v in g._node_weights.values())
    assert all(v is None for v in g._coords.values())
    assert all(v is None for v in g._edge_weights.values())


def test_from_pyg_with_qoolqit_attrs() -> None:
    """Test importing a PyG Data object with QoolQit attributes (weight, pos, edge_weight)."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    weight = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    pos = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], dtype=torch.float64)
    edge_weight = torch.tensor([0.1, 0.2, 0.3], dtype=torch.float64)

    data = Data(weight=weight, pos=pos, edge_index=edge_index, edge_weight=edge_weight)

    g = DataGraph.from_pyg(data, node_weights_attr="weight", edge_weights_attr="edge_weight")

    assert g._node_weights == {0: 1.0, 1: 2.0, 2: 3.0}
    assert g._edge_weights == {(0, 1): 0.1, (1, 2): 0.2, (0, 2): 0.3}
    assert g._coords == {0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.5, 1.0)}


def test_from_pyg_with_pyg_attrs() -> None:
    """Test that standard PyG attributes (x, edge_attr) are stored as graph attributes."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=torch.float64)
    edge_attr = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=torch.float64)

    data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)

    g = DataGraph.from_pyg(data)

    assert g.nodes[0]["x"] == [1.0, 2.0]
    assert g.nodes[1]["x"] == [3.0, 4.0]
    assert g.nodes[2]["x"] == [5.0, 6.0]
    assert g.edges[0, 1]["edge_attr"] == [0.1, 0.2]


def test_from_pyg_with_y_graph_attr() -> None:
    """Test that y is stored as a graph-level attribute."""
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)
    y = torch.tensor([1], dtype=torch.int64)
    data = Data(edge_index=edge_index, y=y, num_nodes=2)

    g = DataGraph.from_pyg(data)

    assert "y" in g.graph
    assert g.graph["y"] == [1]  # to_networkx converts tensor to list


def test_from_pyg_no_auto_weight_detection() -> None:
    """Without node_weights_attr, weight attribute is NOT auto-mapped to node weights."""
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)
    weight = torch.tensor([1.0, 2.0], dtype=torch.float64)
    data = Data(edge_index=edge_index, weight=weight)

    g = DataGraph.from_pyg(data)

    assert all(v is None for v in g._node_weights.values())


def test_from_pyg_with_node_weights_attr() -> None:
    """Test mapping a PyG x attribute (shape (n, 1)) to node weights."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    x = torch.tensor([[1.0], [2.0], [3.0]], dtype=torch.float64)
    data = Data(x=x, edge_index=edge_index)

    g = DataGraph.from_pyg(data, node_weights_attr="x")

    assert g._node_weights == {0: 1.0, 1: 2.0, 2: 3.0}


def test_from_pyg_with_node_weights_attr_1d() -> None:
    """Test mapping a 1D PyG attribute to node weights."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    data = Data(edge_index=edge_index, num_nodes=3)
    data.my_weights = torch.tensor([10.0, 20.0, 30.0], dtype=torch.float64)

    g = DataGraph.from_pyg(data, node_weights_attr="my_weights")

    assert g._node_weights == {0: 10.0, 1: 20.0, 2: 30.0}


def test_from_pyg_with_edge_weights_attr() -> None:
    """Test mapping edge_attr (shape (m, 1)) to edge weights."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    edge_attr = torch.tensor([[0.1], [0.2], [0.3]], dtype=torch.float64)
    data = Data(edge_index=edge_index, edge_attr=edge_attr, num_nodes=3)

    g = DataGraph.from_pyg(data, edge_weights_attr="edge_attr")

    assert g._edge_weights == {(0, 1): 0.1, (1, 2): 0.2, (0, 2): 0.3}


def test_from_pyg_with_edge_weights_attr_1d() -> None:
    """Test mapping a custom 1D attribute to edge weights."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    data = Data(edge_index=edge_index, num_nodes=3)
    data.my_edge_w = torch.tensor([0.5, 0.6, 0.7], dtype=torch.float64)

    g = DataGraph.from_pyg(data, edge_weights_attr="my_edge_w")

    assert g._edge_weights == {(0, 1): 0.5, (1, 2): 0.6, (0, 2): 0.7}


def test_from_pyg_weights_attr_wrong_shape() -> None:
    """Test that a multi-column attribute raises ValueError."""
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float64)  # shape (2, 2)
    data = Data(x=x, edge_index=edge_index)

    with pytest.raises(ValueError, match="must have shape"):
        DataGraph.from_pyg(data, node_weights_attr="x")


def test_from_pyg_weights_attr_missing() -> None:
    """Test that a missing attribute raises AttributeError."""
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)
    data = Data(edge_index=edge_index, num_nodes=2)

    with pytest.raises(AttributeError, match="has no attribute 'nonexistent'"):
        DataGraph.from_pyg(data, node_weights_attr="nonexistent")

    with pytest.raises(AttributeError, match="has no attribute 'nonexistent'"):
        DataGraph.from_pyg(data, edge_weights_attr="nonexistent")


def test_from_pyg_weights_attr_wrong_size() -> None:
    """Test that a size mismatch raises ValueError."""
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)
    data = Data(edge_index=edge_index, num_nodes=2)
    data.bad_node = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)  # 3 elements, 2 nodes
    data.bad_edge = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)  # 3 elements, 2 edges

    with pytest.raises(ValueError, match="has 3 elements, expected 2"):
        DataGraph.from_pyg(data, node_weights_attr="bad_node")

    with pytest.raises(ValueError, match="has 3 elements, expected 2"):
        DataGraph.from_pyg(data, edge_weights_attr="bad_edge")


def test_from_pyg_edge_weights_attr_wrong_shape() -> None:
    """Test that a multi-column edge attribute raises ValueError."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)
    edge_attr = torch.tensor(
        [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=torch.float64
    )  # shape (3, 2)
    data = Data(edge_index=edge_index, edge_attr=edge_attr, num_nodes=3)

    with pytest.raises(ValueError, match="must have shape"):
        DataGraph.from_pyg(data, edge_weights_attr="edge_attr")


def test_to_pyg_basic() -> None:
    """Test converting a DataGraph to a PyG Data object."""
    G = nx.Graph()
    G.add_node(0, weight=1.0, pos=(0.0, 0.0))
    G.add_node(1, weight=2.0, pos=(1.0, 0.0))
    G.add_node(2, weight=3.0, pos=(0.5, 1.0))
    G.add_edge(0, 1, weight=0.1)
    G.add_edge(1, 2, weight=0.2)
    G.add_edge(0, 2, weight=0.3)

    g = DataGraph.from_nx(G)
    data = g.to_pyg()

    assert hasattr(data, "pos")
    assert data.pos.shape == (3, 2)

    assert hasattr(data, "weight")
    assert data.weight.tolist() == [1.0, 2.0, 3.0]

    assert hasattr(data, "edge_weight")


def test_to_pyg_with_graph_attr_y() -> None:
    """Test that graph attribute y is exported to Data.y."""
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_edge(1, 2)

    g = DataGraph.from_nx(G)
    g.graph["y"] = [42]

    data = g.to_pyg()

    assert hasattr(data, "y")
    assert torch.equal(data.y, torch.tensor([42]))


def test_to_pyg_with_custom_weights_attr() -> None:
    """Test that to_pyg exports weights under custom attribute names."""
    G = nx.Graph()
    G.add_node(0, weight=1.0, pos=(0.0, 0.0))
    G.add_node(1, weight=2.0, pos=(1.0, 0.0))
    G.add_edge(0, 1, weight=0.5)

    g = DataGraph.from_nx(G)
    data = g.to_pyg(node_weights_attr="x", edge_weights_attr="edge_attr")

    assert hasattr(data, "x")
    assert data.x.tolist() == [1.0, 2.0]

    assert hasattr(data, "edge_attr")
    assert data.edge_attr.shape[0] == data.edge_index.shape[1]

    # Default names should NOT be present
    assert not hasattr(data, "weight") or data.weight is None
    assert not hasattr(data, "edge_weight") or data.edge_weight is None


def test_pyg_roundtrip_qoolqit_attrs() -> None:
    """Test that from_pyg -> to_pyg preserves QoolQit attributes (weight, pos, edge_weight, y)."""
    edge_index = torch.tensor([[0, 1, 2, 1, 2, 0], [1, 2, 0, 0, 1, 2]], dtype=torch.int64)
    weight = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    pos = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], dtype=torch.float64)
    edge_weight = torch.tensor([0.1, 0.2, 0.3, 0.1, 0.2, 0.3], dtype=torch.float64)
    y = torch.tensor([1], dtype=torch.int64)

    original_data = Data(
        edge_index=edge_index, weight=weight, pos=pos, edge_weight=edge_weight, y=y, num_nodes=3
    )

    g = DataGraph.from_pyg(
        original_data, node_weights_attr="weight", edge_weights_attr="edge_weight"
    )
    roundtrip_data = g.to_pyg()

    assert roundtrip_data.num_nodes == 3
    assert torch.allclose(roundtrip_data.pos, pos)
    assert torch.allclose(roundtrip_data.weight, weight)
    assert hasattr(roundtrip_data, "edge_weight")
    assert roundtrip_data.edge_weight.shape[0] == edge_index.shape[1]
    assert torch.equal(roundtrip_data.y, torch.tensor([1]))


def test_pyg_roundtrip_pyg_attrs() -> None:
    """Test that from_pyg -> to_pyg preserves standard PyG attributes (x, edge_attr)."""
    edge_index = torch.tensor([[0, 1, 2, 1, 2, 0], [1, 2, 0, 0, 1, 2]], dtype=torch.int64)
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=torch.float64)
    edge_attr = torch.tensor(
        [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
        dtype=torch.float64,
    )

    original_data = Data(edge_index=edge_index, x=x, edge_attr=edge_attr)

    g = DataGraph.from_pyg(original_data)
    roundtrip_data = g.to_pyg()

    assert roundtrip_data.num_nodes == 3
    assert hasattr(roundtrip_data, "x")
    assert roundtrip_data.x.shape == x.shape
    assert torch.allclose(roundtrip_data.x.double(), x)
    assert hasattr(roundtrip_data, "edge_attr")
    assert roundtrip_data.edge_attr.shape == edge_attr.shape


def test_from_pyg_to_pyg_roundtrip_custom_weights_attr() -> None:
    """Test roundtrip with custom weights attribute names."""
    edge_index = torch.tensor([[0, 1, 2, 1, 2, 0], [1, 2, 0, 0, 1, 2]], dtype=torch.int64)
    data = Data(edge_index=edge_index, num_nodes=3)
    data.my_node_w = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    data.my_edge_w = torch.tensor([0.1, 0.2, 0.3, 0.1, 0.2, 0.3], dtype=torch.float64)

    g = DataGraph.from_pyg(data, node_weights_attr="my_node_w", edge_weights_attr="my_edge_w")

    assert g._node_weights == {0: 1.0, 1: 2.0, 2: 3.0}

    roundtrip_data = g.to_pyg(node_weights_attr="my_node_w", edge_weights_attr="my_edge_w")

    assert hasattr(roundtrip_data, "my_node_w")
    assert torch.allclose(
        roundtrip_data.my_node_w,
        torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64),
    )
    assert hasattr(roundtrip_data, "my_edge_w")
    assert roundtrip_data.my_edge_w.shape[0] == edge_index.shape[1]
