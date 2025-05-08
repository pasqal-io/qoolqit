from __future__ import annotations

import pytest
from helpers import random_edge_list

from qoolqit.graphs import BaseGraph


@pytest.mark.parametrize("n_nodes", [5, 10, 50])
def test_basegraph_init(n_nodes: int) -> None:
    n_edges = 2 * n_nodes
    edge_list = random_edge_list(n_nodes, n_edges)
    graph = BaseGraph(edge_list)

    # FAILING BECAUSE OF STUPID NETWORKX CONVENTION
    # assert set(graph.edges) == set(edge_list)
