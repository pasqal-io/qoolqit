from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ._force import Force
from ._helpers import normalized_best_dist, normalized_interaction, upper_triangle_indices

logger = logging.getLogger(__name__)


def compute_target_weights_by_dist_limit(
    *,
    distances: np.ndarray,
    target_distances: np.ndarray,
    max_distance_to_walk: float,
) -> Any:
    distances_to_walk = (distances - target_distances) / 2

    modulated_distances_to_walk = np.minimum(
        max_distance_to_walk, np.maximum(-max_distance_to_walk, distances_to_walk)
    )
    modulated_target_distances = distances - modulated_distances_to_walk * 2

    # the following lines rectify possible numerical errors
    rectified_modulated_target_distances = np.where(
        modulated_distances_to_walk == 0,
        distances,
        np.where(
            modulated_distances_to_walk > 0,
            np.maximum(modulated_target_distances, target_distances),
            np.minimum(modulated_target_distances, target_distances),
        ),
    )

    modulated_target_weights = normalized_interaction(rectified_modulated_target_distances)
    assert np.all(np.isfinite(modulated_target_weights))

    return modulated_target_weights


def compute_target_weights_distances_by_weight_diff_limit(
    *,
    distances: np.ndarray,
    current_weights: np.ndarray,
    target_weights: np.ndarray,
    weight_relative_threshold: float,
) -> Any:
    weight_differences = target_weights - current_weights

    max_non_overflowing_value = 0.9 * np.sqrt(np.finfo(weight_differences.dtype).max)
    weight_differences = np.clip(
        weight_differences, -max_non_overflowing_value, max_non_overflowing_value
    )

    logger.debug("weight_differences=%r", weight_differences)

    reduced_weight_differences = weight_differences * (1 - weight_relative_threshold)
    step_target_weights = current_weights + reduced_weight_differences

    step_target_distances = normalized_best_dist(step_target_weights)
    assert np.all(np.isfinite(step_target_distances))

    distances_to_walk = (
        distances - step_target_distances
    ) / 2  # division by 2 because both forces will be applied on both atoms of each pair
    logger.debug("distances_to_walk=%r", distances_to_walk)
    assert np.all(np.isfinite(distances_to_walk))

    chosen_weights_l1 = reduced_weight_differences
    chosen_weights_l2 = chosen_weights_l1**2 * np.sign(chosen_weights_l1)
    chosen_weights_l2[distances_to_walk == 0] = 0.0

    logger.debug("chosen_weights_l2=%r", chosen_weights_l2)
    assert np.all(np.isfinite(chosen_weights_l2))

    return chosen_weights_l2, distances_to_walk


def compute_interaction_forces(
    *,
    distance_matrix: np.ndarray,
    positions: np.ndarray,
    target_weights: np.ndarray,
    weight_relative_threshold: float,
    max_distance_to_walk: float,
    target_distances: np.ndarray | None = None,
) -> tuple[Any, Force]:
    """Return the modulated target weights and the force of the pairs (i, j), i < j."""
    pairs = upper_triangle_indices(len(positions))
    distances = np.take(distance_matrix, pairs)
    if target_distances is None:
        target_distances = normalized_best_dist(target_weights)
    target_distances = np.take(target_distances, pairs)

    current_weights = normalized_interaction(distances)

    logger.debug("current_weights=%r", current_weights)
    logger.debug("target_weights=%r", target_weights)

    modulated_target_weights = compute_target_weights_by_dist_limit(
        distances=distances,
        target_distances=target_distances,
        max_distance_to_walk=max_distance_to_walk,
    )

    weights, distances_to_walk = compute_target_weights_distances_by_weight_diff_limit(
        distances=distances,
        current_weights=current_weights,
        target_weights=modulated_target_weights,
        weight_relative_threshold=weight_relative_threshold,
    )

    return modulated_target_weights, Force(
        weights=weights,
        distances_to_walk=np.abs(distances_to_walk),
        positions=positions,
        distances=distances,
        pairs=pairs,
    )
