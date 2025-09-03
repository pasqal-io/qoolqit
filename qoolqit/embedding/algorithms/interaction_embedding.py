from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform

from qoolqit.graphs import DataGraph

from ..base_embedder import EmbeddingConfig


@dataclass
class InteractionEmbeddingConfig(EmbeddingConfig):
    """Configuration parameters for the interaction embedding."""

    method: str = "Nelder-Mead"
    maxiter: int = 200000
    tol: float = 1e-8


def interaction_embedding(matrix: np.ndarray, method: str, maxiter: int, tol: float) -> np.ndarray:
    """Matrix embedding into the interaction term of the Rydberg Analog Model.

    Uses scipy.minimize to find the optimal set of node coordinates such that the
    matrix of values 1/(r_ij)^6 approximate the off-diagonal terms of the input matrix.

    Check scipy.minimize documentation for more information on each parameter.

    Arguments:
        matrix: the matrix to embed.
        method: the method used by scipy.minimize.
        maxiter: maximum number of iterations.
        tol: tolerance for termination.
    """

    def cost_function(new_coords: np.ndarray, matrix: np.ndarray) -> np.float:
        """Cost function."""
        new_coords = np.reshape(new_coords, (len(matrix), 2))
        # Cost based on minimizing the distance between the matrix and the interaction 1/r^6
        new_matrix = squareform(1.0 / (pdist(new_coords) ** 6))
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
        options={"maxiter": maxiter},
    )

    coords = np.reshape(res.x, (len(matrix), 2))

    centered_coords = coords - np.mean(coords, axis=0)

    graph = DataGraph.from_coordinates(centered_coords.tolist())

    return graph
