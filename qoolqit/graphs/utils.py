from __future__ import annotations

from itertools import product
from math import dist
from typing import Iterable

import numpy as np


def _dist(p: Iterable | None, q: Iterable | None) -> float | None:
    """Wrapper on dist that accepts None."""
    return None if p is None or q is None else dist(p, q)


def all_node_pairs(nodes: Iterable, both: bool = False) -> set:
    if not both:
        return set(filter(lambda x: x[0] < x[1], product(nodes, nodes)))
    else:
        fullpairs = set(product(nodes, nodes))
        diagonal = set((i, i) for i in nodes)
        return fullpairs - diagonal


def distances(coords: dict, edge_list: Iterable | None) -> dict:
    if edge_list is None:
        edge_list = all_node_pairs(list(coords.keys()))
    return {edge: _dist(coords[edge[0]], coords[edge[1]]) for edge in edge_list}


def min_distance(coords: dict) -> float:
    pairs = all_node_pairs(list(coords.keys()))
    dist_dict = distances(coords, pairs)
    distance: float = min(dist_dict.values())
    return distance


def scale_coords(coords: dict, scaling: float) -> dict:
    scaled_coords = {i: (c[0] * scaling, c[1] * scaling) for i, c in coords.items()}
    return scaled_coords


def space_coords(coords: dict, spacing: float) -> dict:
    min_dist = min_distance(coords)
    scale_factor = spacing / min_dist
    return scale_coords(coords, scale_factor)


def random_coords(n_nodes: int, scale: float = 1.0) -> list:
    x_coords = np.random.uniform(low=-scale, high=scale, size=(n_nodes,))
    y_coords = np.random.uniform(low=-scale, high=scale, size=(n_nodes,))
    return [(x, y) for x, y in zip(x_coords, y_coords)]
