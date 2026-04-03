from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ._force import Force
from ._helpers import normalized_best_dist, normalized_interaction

logger = logging.getLogger(__name__)


def compute_target_weights_by_dist_limit(
    *,
    distance_matrix: np.ndarray,
    target_weights: np.ndarray,
    max_distance_to_walk: float,
) -> Any:
    target_distances = normalized_best_dist(target_weights)

    np.fill_diagonal(target_distances, 0)
    distances_to_walk = (distance_matrix - target_distances) / 2
    np.fill_diagonal(distances_to_walk, 0)

    modulated_distances_to_walk = np.minimum(
        max_distance_to_walk, np.maximum(-max_distance_to_walk, distances_to_walk)
    )
    modulated_target_distances = distance_matrix - modulated_distances_to_walk * 2

    # the following lines rectify possible numerical errors
    rectified_modulated_target_distances = np.where(
        modulated_distances_to_walk == 0,
        distance_matrix,
        np.where(
            modulated_distances_to_walk > 0,
            np.maximum(modulated_target_distances, target_distances),
            np.minimum(modulated_target_distances, target_distances),
        ),
    )

    modulated_target_weights = normalized_interaction(rectified_modulated_target_distances)
    assert not np.any(np.isinf(modulated_target_weights))

    return modulated_target_weights


def compute_target_weights_distances_by_weight_diff_limit(
    *,
    distance_matrix: np.ndarray,
    unitary_vectors: np.ndarray,
    current_weights: np.ndarray,
    target_weights: np.ndarray,
    weight_relative_threshold: float,
) -> Any:
    weight_differences = target_weights - current_weights
    n = len(weight_differences)
    logger.debug(f"{weight_differences=}")

    weight_difference_threshold = np.max(np.abs(weight_differences)) * weight_relative_threshold
    logger.debug(f"{weight_difference_threshold=}")

    reduced_weight_differences = weight_differences * (1 - weight_relative_threshold)
    step_target_weights = current_weights + reduced_weight_differences

    step_target_distances = normalized_best_dist(step_target_weights)
    assert not np.any(np.isinf(step_target_distances))

    distances_to_walk = (
        distance_matrix - step_target_distances
    ) / 2  # division by 2 because both forces will be applied on both atoms of each pair
    logger.debug(f"{distances_to_walk=}")

    weighted_vectors = reduced_weight_differences[:, :, np.newaxis] * unitary_vectors
    weighted_vectors[distances_to_walk == 0] = 0.0

    assert not np.any(np.isnan(weighted_vectors))
    logger.debug(f"{weighted_vectors=}")

    return weighted_vectors, distances_to_walk


def compute_interaction_forces(
    *,
    distance_matrix: np.ndarray,
    unitary_vectors: np.ndarray,
    target_weights: np.ndarray,
    weight_relative_threshold: float,
    max_distance_to_walk: float,
) -> tuple[Any, Force]:
    current_weights = normalized_interaction(distance_matrix)

    logger.debug(f"{current_weights=}")
    logger.debug(f"{target_weights=}")

    modulated_target_weights = compute_target_weights_by_dist_limit(
        distance_matrix=distance_matrix,
        target_weights=target_weights,
        max_distance_to_walk=max_distance_to_walk,
    )

    weighted_vectors, distances_to_walk = compute_target_weights_distances_by_weight_diff_limit(
        distance_matrix=distance_matrix,
        unitary_vectors=unitary_vectors,
        current_weights=current_weights,
        target_weights=modulated_target_weights,
        weight_relative_threshold=weight_relative_threshold,
    )

    return modulated_target_weights, Force(
        weighted_vectors=weighted_vectors, distances_to_walk=np.abs(distances_to_walk)
    )
