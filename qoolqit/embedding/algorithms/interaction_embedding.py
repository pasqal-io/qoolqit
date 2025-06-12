from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform

from ..base_embedder import EmbeddingConfig


@dataclass
class InteractionEmbeddingConfig(EmbeddingConfig):
    """Configuration parameters for the interaction embedding."""

    """Method passed to scipy.minimize."""
    method: str = "Nelder-Mead"

    """Maximum iterations passed to scipy.minimize."""
    maxiter: int = 200000

    """Tolerance passed to scipy.minimize."""
    tol: float = 1e-8


def interaction_embedding(matrix: np.ndarray, method: str, maxiter: int, tol: float) -> np.ndarray:

    def cost_function(new_coords: np.ndarray, matrix: np.ndarray) -> np.float:
        """Cost functi."""
        new_coords = np.reshape(new_coords, (len(matrix), 2))
        # Cost based on minimizing the distance between the matrix and the interaction 1/r^6
        new_matrix = squareform(1.0 / pdist(new_coords) ** 6)
        return np.linalg.norm(new_matrix - matrix)

    np.random.seed(0)

    # Initial guess for the coordinates
    x0 = np.random.random(len(matrix) * 2)

    res = minimize(
        cost_function,
        x0,
        args=(matrix,),
        method=method,
        tol=tol,
        options={"maxiter": maxiter, "maxfev": None},
    )

    coords = np.reshape(res.x, (len(matrix), 2))

    return coords
