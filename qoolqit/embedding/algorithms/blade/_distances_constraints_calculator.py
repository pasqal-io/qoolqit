from __future__ import annotations

import dataclasses
from typing import Any, Optional

import numpy as np

from ._helpers import distance_matrix_from_positions, normalized_interaction
from .drawing import plot_differences


def compute_best_scaling_for_qubo(
    target_interactions: np.ndarray,
    embedded_interactions: np.ndarray,
    filter_differences: bool = True,
    draw_differences: bool = False,
) -> Any:
    embedded_interactions_triu = embedded_interactions[
        np.triu_indices_from(embedded_interactions, k=1)
    ]
    target_interactions_triu = target_interactions[np.triu_indices_from(target_interactions, k=1)]

    differences = embedded_interactions_triu - target_interactions_triu

    percent = 100 - 2 / (len(target_interactions) - 1) * 10
    percentile = np.percentile(differences, percent)

    difference_ceiling = np.maximum(0.0, percentile)

    if filter_differences:
        weights = np.where(
            differences > difference_ceiling,
            difference_ceiling / differences,
            1.0,
        )
    else:
        weights = np.ones_like(differences)

    if draw_differences:
        plot_differences(differences)

    best_scaling = (
        np.sum(weights * embedded_interactions_triu**2)
        / np.sum(weights * embedded_interactions_triu * target_interactions_triu)
    ) ** (1 / 6)

    assert not np.isnan(best_scaling)
    assert not np.isinf(best_scaling)
    assert best_scaling > 0

    return best_scaling


def compute_best_scaling_for_pos(
    target_interactions: np.ndarray, positions: np.ndarray, draw_differences: bool = False
) -> Any:
    distance_matrix = distance_matrix_from_positions(positions)

    current_weights = np.vectorize(normalized_interaction, signature="(m,n)->(m,n)")(
        dist=distance_matrix
    )
    current_weights = np.triu(current_weights, k=1)

    return compute_best_scaling_for_qubo(
        target_interactions=target_interactions,
        embedded_interactions=current_weights,
        draw_differences=draw_differences,
    )


@dataclasses.dataclass
class DistancesConstraintsCalculator:
    target_interactions: np.ndarray
    starting_min: float | None
    starting_ratio: float | None
    final_ratio: float | None = None
    current_min: float | None = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        if self.final_ratio is not None:
            assert self.starting_min is not None
            self.current_min = self.starting_min
        else:
            self.starting_ratio = None
            self.current_min = None

    def compute_scaling_min_max(
        self, positions: np.ndarray, step_cursor: float, draw_differences: bool = False
    ) -> tuple[float, Optional[float], Optional[float]]:
        """Step_cursor is between 0 (start) and 1 (end)."""
        assert 0 <= step_cursor <= 1

        scaling_factor = compute_best_scaling_for_pos(
            target_interactions=self.target_interactions,
            positions=positions,
            draw_differences=draw_differences,
        )

        if self.final_ratio is None:
            return scaling_factor, None, None

        assert self.starting_ratio is not None

        step_ratio = self.final_ratio + (1 - step_cursor) * (self.starting_ratio - self.final_ratio)

        scaled_min = self.current_min * scaling_factor
        self.current_min, current_max = scaled_min, scaled_min * step_ratio

        return scaling_factor, self.current_min, current_max
