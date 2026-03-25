from __future__ import annotations

import numpy as np
import pytest

from qoolqit.embedding.algorithms.blade._dist_constraints_forces import (
    compute_max_dist_constraint_forces,
)


@pytest.mark.parametrize("max_dist", [1.0, None])
def test_compute_max_dist_constraint_forces_no_violation(max_dist: float | None) -> None:
    positions = np.array([[0.5, 0.0], [-0.3, 0.3], [0.0, 0.4], [1.0, 0.0], [0.0, 0.0]])

    force = compute_max_dist_constraint_forces(positions=positions, max_radius=max_dist)

    np.testing.assert_allclose(force.weighted_vectors, np.zeros_like(positions))
    np.testing.assert_allclose(force.distances_to_walk, np.zeros(len(positions)))


def test_compute_max_dist_constraint_forces_multiple_violations() -> None:
    max_dist = 1.0

    positions = np.array([[0.5, 0.0], [0.0, 1.5], [-2.0, 0.0]])

    force = compute_max_dist_constraint_forces(positions=positions, max_radius=max_dist)

    expected_distances_to_walk = np.array([0.0, 0.5, 1.0])
    np.testing.assert_allclose(force.distances_to_walk, expected_distances_to_walk)

    expected_weighted_vectors = np.array(
        [
            [0.0, 0.0],
            [0.0, -0.5],
            [1.0, 0.0],
        ]
    )
    np.testing.assert_allclose(force.weighted_vectors, expected_weighted_vectors)
