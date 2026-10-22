from __future__ import annotations

import functools
from typing import Any, Literal, TypeVar

import numpy as np

Value = TypeVar("Value", float, np.ndarray)
FormatType = Literal["full", "triu", "sym"]


def _format_return(input: Value, ret: np.ndarray, *, format: FormatType) -> Value:
    if isinstance(input, (float, int)):
        return float(ret)

    if input.ndim == 1:
        return ret

    match format:
        case "full":
            return ret
        case "triu":
            return np.triu(ret, k=1)
        case "sym":
            np.fill_diagonal(ret, 0)
            return ret
        case _:
            raise ValueError(f"Invalid format: {format}")


def normalized_interaction(dist: Value, *, format: FormatType = "sym") -> Value:
    """Convert pairwise distances into interactions.

    Args:
        dist: Pairwise distances between nodes.
        format: Format of the output if `dist` is a numpy array. Can be "full"
        (all values), "triu" (upper triangle without diagonal), or "sym"
        (upper and lower triangles without diagonal).
    """
    squared_dist = dist * dist
    interactions = np.divide(
        1,
        squared_dist * squared_dist * squared_dist,
        out=np.full_like(dist, np.inf, dtype=float),
        where=(dist != 0),
    )

    # following type ignore is required probably due to a bug of mypy
    # (it works if the function's content is copied-pasted here)
    return _format_return(input=dist, ret=interactions, format=format)  # type: ignore


def normalized_best_dist(weight: Value, *, format: FormatType = "sym") -> Value:
    """Convert pairwise interactions into distances.

    Args:
        dist: Pairwise distances between nodes.
        format: Format of the output if `dist` is a numpy array. Can be "full"
        (all values), "triu" (upper triangle without diagonal), or "sym"
        (upper and lower triangles without diagonal).
    """
    dists = np.divide(
        1,
        np.cbrt(np.sqrt(weight)),
        out=np.full_like(weight, np.inf, dtype=float),
        where=(weight != 0),
    )

    # following type ignore is required probably due to a bug of mypy
    # (it works if the function's content is copied-pasted here)
    return _format_return(input=weight, ret=dists, format=format)  # type: ignore


def distance_matrix_from_positions(positions: np.ndarray) -> np.ndarray:
    # loop over the few dimensions to avoid allocating a (N, N, d) array
    squared_distances = np.zeros((len(positions), len(positions)))
    for coordinates in np.transpose(positions):
        differences = coordinates[np.newaxis, :] - coordinates[:, np.newaxis]
        squared_distances += differences * differences
    return np.sqrt(squared_distances)


@functools.cache
def upper_triangle_indices(n: int) -> np.ndarray:
    """Flat indices of the pairs (i, j), i < j, in a (n, n) matrix."""
    return np.flatnonzero(np.triu(np.ones((n, n), dtype=bool), k=1))


def symmetric_matrix_from_pairs(values: np.ndarray, pairs: np.ndarray, n: int) -> np.ndarray:
    """(n, n) symmetric matrix with `values` at the flat indices `pairs` of the upper triangle."""
    matrix = np.zeros((n, n))
    np.put(matrix, pairs, values)
    return matrix + matrix.T


def interaction_matrix_from_positions(positions: np.ndarray) -> np.ndarray:
    return normalized_interaction(distance_matrix_from_positions(positions), format="triu")


def normalized_distance(target: np.ndarray, actual: np.ndarray) -> np.floating[Any]:
    return np.linalg.norm(target - actual) / np.linalg.norm(target)
