from __future__ import annotations

import random

from qoolqit.graphs import all_node_pairs


def random_edge_list(n_nodes: int, k: int) -> list:
    all_edges = all_node_pairs(range(n_nodes))
    return random.sample(tuple(all_edges), k=k)
