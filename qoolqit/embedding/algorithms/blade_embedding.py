from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from qoolqit.embedding.base_embedder import EmbeddingConfig


@dataclass
class BladeEmbeddingConfig(EmbeddingConfig):
    """Configuration parameters for the interaction embedding."""

    max_min_dist_ratio: float | None = None
    draw_steps: bool | list[int] = False
    dimensions: tuple = (5, 4, 3, 2, 2, 2)
    starting_positions: np.ndarray | None = None
    pca: bool = False
    steps_per_round: int = 200
    compute_weight_relative_threshold: Callable[[float], float] = lambda _: 0.1
    compute_max_distance_to_walk: Callable[
        [float, float | None], float | tuple[float, float, float]
    ] = lambda x, max_radial_dist: np.inf
    starting_ratio_factor: int = 2
