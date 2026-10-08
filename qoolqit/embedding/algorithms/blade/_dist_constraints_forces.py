from __future__ import annotations

import numpy as np

from ._force import Force


def compute_min_dist_constraint_forces(
    *,
    min_dist: float | None,
    positions: np.ndarray,
    distance_matrix: np.ndarray,
) -> Force:
    """Computes the forces to enforce the minimum distance constraint."""
    min_distances_to_walk = (
        np.maximum(0, min_dist - distance_matrix) / 2
        if min_dist is not None
        else np.full_like(distance_matrix, 0)
    )
    min_force = Force(
        weights=-min_distances_to_walk,
        distances_to_walk=min_distances_to_walk,
        positions=positions,
        distances=distance_matrix,
    )

    return min_force


def compute_max_dist_constraint_forces(
    *,
    positions: np.ndarray,
    max_radius: float | None,
) -> Force:
    """Computes the forces to enforce the maximum distance constraint."""
    distances_from_center = np.linalg.norm(positions, axis=1)
    max_distances_to_walk = (
        np.maximum(0, distances_from_center - max_radius)
        if max_radius is not None
        else np.full_like(distances_from_center, 0)
    )
    max_force = Force(
        weights=-max_distances_to_walk,
        distances_to_walk=max_distances_to_walk,
        positions=positions,
        distances=distances_from_center,
    )

    return max_force
