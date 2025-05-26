from __future__ import annotations

import random
from itertools import product
from math import dist, isclose
from typing import Iterable

import numpy as np

from qoolqit.utils import ATOL_32


def all_node_pairs(nodes: Iterable) -> set:
    """Return all pairs of nodes (u, v) where u < v.

    Arguments:
        nodes: set of node indices.
    """
    return set(filter(lambda x: x[0] < x[1], product(nodes, nodes)))


def distances(coords: dict, edge_list: Iterable) -> dict:
    """Return a dictionary of edge distances.

    Arguments:
        coords: dictionary of node coordinates.
        edge_list: edge list to compute the distances for.
    """
    return {edge: dist(coords[edge[0]], coords[edge[1]]) for edge in edge_list}


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
    pairs = all_node_pairs(list(coords.keys()))
    min_dist = min(distances(coords, pairs).values())
    scale_factor = spacing / min_dist
    return scale_coords(coords, scale_factor)


def random_coords(n: int, L: float = 1.0) -> list:
    """Generate a random set of node coordinates on a square of side L.

    Arguments:
        n: number of coordinate pairs to generate.
        L: side of the square.
    """
    x_coords = np.random.uniform(low=-L / 2, high=L / 2, size=(n,)).tolist()
    y_coords = np.random.uniform(low=-L / 2, high=L / 2, size=(n,)).tolist()
    return [(x, y) for x, y in zip(x_coords, y_coords)]


def random_edge_list(nodes: Iterable, k: int) -> list:
    """Generates a random set of k edges linkings items from a set of nodes."""
    all_edges = all_node_pairs(nodes)
    return random.sample(tuple(all_edges), k=k)


def less_or_equal(a: float, b: float, rel_tol: float = 0.0, abs_tol: float = ATOL_32) -> bool:
    """Less or approximately equal."""
    return a < b or isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
