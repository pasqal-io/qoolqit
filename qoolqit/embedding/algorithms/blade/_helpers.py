from __future__ import annotations

from typing import Any, Literal, TypeVar

import numpy as np

Value = TypeVar("Value", float, np.ndarray)
FormatType = Literal["full", "triu", "sym"]


def _format_return(input: Value, ret: np.ndarray, *, format: FormatType) -> Value:
    if isinstance(input, float) or isinstance(input, int):
        return float(ret)

    if input.ndim == 1:
        return ret

    match format:
        case "full":
            return ret
        case "triu":
            return np.triu(ret, k=1)
        case "sym":
            return np.triu(ret, k=1) + np.tril(ret, k=-1)
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

    interactions = np.divide(
        1, dist**6, out=np.full_like(dist, np.inf, dtype=float), where=(dist != 0)
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
        1, weight ** (1 / 6), out=np.full_like(weight, np.inf, dtype=float), where=(weight != 0)
    )

    # following type ignore is required probably due to a bug of mypy
    # (it works if the function's content is copied-pasted here)
    return _format_return(input=weight, ret=dists, format=format)  # type: ignore


def distance_matrix_from_positions(positions: np.ndarray) -> np.ndarray:
    position_differences = positions[np.newaxis, :] - positions[:, np.newaxis]
    return np.linalg.norm(position_differences, axis=2)


def interaction_matrix_from_positions(positions: np.ndarray) -> np.ndarray:
    return normalized_interaction(distance_matrix_from_positions(positions), format="triu")


def normalized_distance(target: np.ndarray, actual: np.ndarray) -> np.floating[Any]:
    return np.linalg.norm(target - actual) / np.linalg.norm(target)
