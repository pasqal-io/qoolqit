from __future__ import annotations

import numpy as np
import pytest

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
