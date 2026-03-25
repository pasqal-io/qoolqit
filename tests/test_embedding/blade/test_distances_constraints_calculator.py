from __future__ import annotations

import numpy as np

from qoolqit.embedding.algorithms.blade._distances_constraints_calculator import (
    compute_best_scaling_for_pos,
)
from qoolqit.embedding.algorithms.blade._helpers import interaction_matrix_from_positions


def test_scaling() -> None:
    positions = np.array(
        [
            [-0.33254565, 1.86186717],
            [0.33254565, 1.86186717],
            [0.43476024, -1.86186717],
            [-0.43476024, -1.86186717],
        ]
    )

    target_interactions = np.array(
        [
            [0.0, 1.771561, 0.0, 0.0],
            [1.771561, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.33489798],
            [0.0, 0.0, 0.33489798, 0.0],
        ]
    )

    scaling = compute_best_scaling_for_pos(
        target_interactions=target_interactions, positions=positions
    )

    new_positions = scaling * positions
    new_interactions = interaction_matrix_from_positions(new_positions)

    target_interactions_values = target_interactions[np.triu_indices_from(target_interactions, k=1)]
    new_interactions_values = new_interactions[np.triu_indices_from(new_interactions, k=1)]

    assert not np.all(target_interactions_values > new_interactions_values)
    assert not np.all(target_interactions_values < new_interactions_values)
