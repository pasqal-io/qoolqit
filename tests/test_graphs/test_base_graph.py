from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np
import pytest
import torch
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


def test_from_pyg_wrong_input() -> None:
    with pytest.raises(TypeError, match="Input must be a torch_geometric.data.Data object."):
        BaseGraph.from_pyg("hello")


def test_from_pyg_only_edges() -> None:
    """Test importing a PyG Data with only edge_index (no weights or positions)."""
    edge_index = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]])  # edges: (0,1), (1,0), (1,2), (2,1)
    data = Data(edge_index=edge_index, num_nodes=3)

    g = BaseGraph.from_pyg(data)

    # Check that nodes and edges were copied
    assert set(g.nodes) == {0, 1, 2}
    assert all(v is None for v in g._node_weights.values())
    assert all(v is None for v in g._coords.values())
    assert all(v is None for v in g._edge_weights.values())


def test_from_pyg_with_qoolqit_attrs() -> None:
    """Test importing a PyG Data object with QoolQit attributes (weight, pos, edge_weight)."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)

    weight = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)  # node weights
    pos = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], dtype=torch.float64)  # positions
    edge_weight = torch.tensor([0.1, 0.2, 0.3], dtype=torch.float64)  # edge weights

    data = Data(weight=weight, pos=pos, edge_index=edge_index, edge_weight=edge_weight)

    g = BaseGraph.from_pyg(data)

    assert g._node_weights == {0: 1.0, 1: 2.0, 2: 3.0}
    assert g._edge_weights == {(0, 1): 0.1, (1, 2): 0.2, (0, 2): 0.3}
    assert g._coords == {0: [0.0, 0.0], 1: [1.0, 0.0], 2: [0.5, 1.0]}


def test_from_pyg_with_pyg_attrs() -> None:
    """Test importing a PyG Data object with standard PyG attributes (x, edge_attr)."""
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.int64)

    x = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=torch.float64)  # multi-dim x
    edge_attr = torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]], dtype=torch.float64)

    data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)

    g = BaseGraph.from_pyg(data)

    # x and edge_attr should be stored as node/edge attributes
    assert g.nodes[0]["x"] == [1.0, 2.0]
    assert g.nodes[1]["x"] == [3.0, 4.0]
    assert g.nodes[2]["x"] == [5.0, 6.0]
    assert g.edges[0, 1]["edge_attr"] == [0.1, 0.2]


def test_from_pyg_with_y_graph_attr() -> None:
    """Test that y is stored as a graph attribute."""
    edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)
    y = torch.tensor([1], dtype=torch.int64)

    data = Data(edge_index=edge_index, y=y, num_nodes=2)

    g = BaseGraph.from_pyg(data)

    assert "y" in g.graph
    assert g.graph["y"] == [1]  # to_networkx converts tensor to list


def test_to_pyg_basic() -> None:
    """Test converting a BaseGraph to PyG Data object."""
    G = nx.Graph()
    G.add_node(0, weight=1.0, pos=(0.0, 0.0))
    G.add_node(1, weight=2.0, pos=(1.0, 0.0))
    G.add_node(2, weight=3.0, pos=(0.5, 1.0))
    G.add_edge(0, 1, weight=0.1)
    G.add_edge(1, 2, weight=0.2)
    G.add_edge(0, 2, weight=0.3)

    g = BaseGraph.from_nx(G)
    data = g.to_pyg()

    # Check that pos is exported
    assert hasattr(data, "pos")
    assert data.pos.shape == (3, 2)

    # Check that weight is exported
    assert hasattr(data, "weight")
    assert data.weight.tolist() == [1.0, 2.0, 3.0]

    # Check that edge_weight is exported
    assert hasattr(data, "edge_weight")


def test_to_pyg_with_graph_attr_y() -> None:
    """Test that graph attribute y is exported to Data.y as tensor."""
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_edge(1, 2)

    g = BaseGraph.from_nx(G)
    g.graph["y"] = [42]  # stored as Python list

    data = g.to_pyg()

    assert hasattr(data, "y")
    assert torch.equal(data.y, torch.tensor([42]))


def test_pyg_roundtrip() -> None:
    """Test that from_pyg -> to_pyg preserves the graph structure and attributes."""
    edge_index = torch.tensor([[0, 1, 2, 1, 2, 0], [1, 2, 0, 0, 1, 2]], dtype=torch.int64)
    weight = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    pos = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], dtype=torch.float64)
    y = torch.tensor([1], dtype=torch.int64)

    original_data = Data(edge_index=edge_index, weight=weight, pos=pos, y=y, num_nodes=3)

    g = BaseGraph.from_pyg(original_data)
    roundtrip_data = g.to_pyg()

    # Check structure
    assert roundtrip_data.num_nodes == 3

    # Check pos preserved
    assert torch.allclose(roundtrip_data.pos, pos)

    # Check weight preserved
    assert torch.allclose(roundtrip_data.weight, weight)

    # Check y preserved as tensor
    assert torch.equal(roundtrip_data.y, torch.tensor([1]))
