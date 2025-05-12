from __future__ import annotations

from itertools import product
from math import dist
from typing import Iterable


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


def scale_coords(coords: dict, spacing: float) -> dict:
    min_dist = min_distance(coords)
    scale_factor = spacing / min_dist
    scaled_coords = {i: (c[0] * scale_factor, c[1] * scale_factor) for i, c in coords.items()}
    return scaled_coords
