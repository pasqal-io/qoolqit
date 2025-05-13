from __future__ import annotations

import pytest

from qoolqit.graphs import DataGraph


@pytest.mark.parametrize("graph_type", ["circle", "line", "random_ud"])
@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_unit_disk(n_nodes: int, graph_type: str) -> None:
    if graph_type == "circle":
        graph = DataGraph.circle(n_nodes, spacing=1.0, radius=1.0)
    if graph_type == "line":
        graph = DataGraph.line(n_nodes, spacing=1.0, radius=1.0)
    if graph_type == "random_ud":
        graph = DataGraph.random_ud(n_nodes, radius=1.0)

    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert not graph.is_node_weighted
    assert not graph.is_edge_weighted

    assert graph.is_ud_graph


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_random_er(n_nodes: int) -> None:
    graph = DataGraph.random_er(n_nodes, p=0.5)
    assert len(graph.node_weights) == graph.number_of_nodes()
    assert len(graph.edge_weights) == graph.number_of_edges()
    assert not graph.is_node_weighted
    assert not graph.is_edge_weighted
    assert not graph.is_ud_graph


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_from_matrix(n_nodes: int) -> None:

    assert True
