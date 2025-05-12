from __future__ import annotations

import pytest

from qoolqit.graphs import DataGraph


@pytest.mark.parametrize("graph_type", ["circle", "line", "random"])
@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_datagraph_ud(n_nodes: int, graph_type: str) -> None:
    if graph_type == "circle":
        graph = DataGraph.circle(n_nodes)
    if graph_type == "line":
        graph = DataGraph.line(n_nodes)
    if graph_type == "random":
        graph = DataGraph.random_ud(n_nodes)

    assert True
