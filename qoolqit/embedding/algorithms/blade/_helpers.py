from __future__ import annotations

import warnings
from typing import Any, TypeVar

import numpy as np

Value = TypeVar("Value", float, np.ndarray)


def normalized_interaction(dist: Value) -> Value:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="divide by zero encountered in divide", category=RuntimeWarning
        )
        result = 1 / dist**6

    if isinstance(result, np.ndarray) and result.ndim == 2:
        np.fill_diagonal(result, 0)

    return result


def normalized_best_dist(weight: Value) -> Value:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="divide by zero encountered in divide", category=RuntimeWarning
        )
        result = (1 / weight) ** (1 / 6)

    if isinstance(result, np.ndarray) and result.ndim == 2:
        np.fill_diagonal(result, 0)

    return result  # type: ignore[no-any-return]


def distance_matrix_from_positions(positions: np.ndarray) -> np.ndarray:
    position_differences = positions[np.newaxis, :] - positions[:, np.newaxis]
    return np.linalg.norm(position_differences, axis=2)


def interaction_matrix_from_distances(distance_matrix: np.ndarray) -> np.ndarray:
    current_weights = normalized_interaction(distance_matrix)
    current_weights = np.triu(current_weights, k=1)
    return current_weights


def interaction_matrix_from_positions(positions: np.ndarray) -> np.ndarray:
    return interaction_matrix_from_distances(
        distance_matrix=distance_matrix_from_positions(positions)
    )


def normalized_distance(target: np.ndarray, actual: np.ndarray) -> np.floating[Any]:
    return np.linalg.norm(target - actual) / np.linalg.norm(target)
