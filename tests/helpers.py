from __future__ import annotations

import random
from collections.abc import Iterable

from qoolqit.graphs import all_node_pairs


def random_edge_list(nodes: Iterable, k: int) -> list:
    all_edges = all_node_pairs(nodes)
    return random.sample(tuple(all_edges), k=k)
