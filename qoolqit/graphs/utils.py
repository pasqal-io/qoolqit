from __future__ import annotations

from itertools import product
from math import dist, isclose
from typing import Iterable

import numpy as np

from qoolqit.utils import ATOL_32


def _dist(p: Iterable | None, q: Iterable | None) -> float | None:
    """Wrapper on dist that accepts None and returns None."""
    return None if p is None or q is None else dist(p, q)


def all_node_pairs(nodes: Iterable) -> set:
    """Return all pairs of nodes (u, v) where u < v.

    Arguments:
        nodes: iterable on node indices.
    """
    return set(filter(lambda x: x[0] < x[1], product(nodes, nodes)))


def distances(coords: dict, edge_list: Iterable | None) -> dict:
    """Return dictionary of edge distances.

    If no edge list is given, the distances are calculated for all pairs of
    all nodes in the dictionary. Otherwise, only for the pairs given in the edge list.

    Arguments:
        coords: dictionary of node coordinates.
        edge_list: optional edge list to compute the distances for.
    """
    if edge_list is None:
        edge_list = all_node_pairs(list(coords.keys()))
    return {edge: _dist(coords[edge[0]], coords[edge[1]]) for edge in edge_list}


def min_distance(coords: dict) -> float:
    """Return the distance between the two closest nodes.

    Arguments:
        coords: dictionary of node coordinates.
    """
    pairs = all_node_pairs(list(coords.keys()))
    dist_dict = distances(coords, pairs)
    distance: float = min(dist_dict.values())
    return distance


def scale_coords(coords: dict, scaling: float) -> dict:
    """Scale the coordinates by a given value.

    Arguments:
        coords: dictionary of node coordinates.
        scaling: value to scale by.
    """
    scaled_coords = {i: (c[0] * scaling, c[1] * scaling) for i, c in coords.items()}
    return scaled_coords


def space_coords(coords: dict, spacing: float) -> dict:
    """Spaces the coordinates so the minimum distance is equal to a set spacing.

    Arguments:
        coords: dictionary of node coordinates.
        spacing: value to set as minimum distance.
    """
    min_dist = min_distance(coords)
    scale_factor = spacing / min_dist
    return scale_coords(coords, scale_factor)


def random_coords(n: int, L: float = 1.0) -> list:
    """Generate a random set of node coordinates on a square of side L.

    Arguments:
        n: number of coordinate pairs to generate.
        L: side of the square.
    """
    x_coords = np.random.uniform(low=-L / 2, high=L / 2, size=(n,))
    y_coords = np.random.uniform(low=-L / 2, high=L / 2, size=(n,))
    return [(x, y) for x, y in zip(x_coords, y_coords)]


def less_or_equal(a: float, b: float, rel_tol: float = 0.0, abs_tol: float = ATOL_32) -> bool:
    """Less or approximately equal."""
    return a < b or isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
