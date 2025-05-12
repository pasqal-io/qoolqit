from __future__ import annotations

import random

import numpy as np

from qoolqit.graphs import all_node_pairs


def random_edge_list(n_nodes: int, k: int) -> list:
    all_edges = all_node_pairs(range(n_nodes))
    return random.sample(tuple(all_edges), k=k)


def random_coords(n_nodes: int, scale: float = 1.0) -> list:
    x_coords = np.random.uniform(low=-scale, high=scale, size=(n_nodes,))
    y_coords = np.random.uniform(low=-scale, high=scale, size=(n_nodes,))
    return [(x, y) for x, y in zip(x_coords, y_coords)]
