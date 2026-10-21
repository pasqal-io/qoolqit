"""Interaction embedding: fit node coordinates to an interaction matrix with scipy.optimize."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform

from qoolqit.embedding.base_embedder import EmbedderConfig
from qoolqit.graphs import DataGraph


@dataclass
class InteractionEmbedderConfig(EmbedderConfig):
    """Configuration parameters for the interaction embedding.

    Attributes:
        method: optimization method passed to `scipy.optimize.minimize`.
        maxiter: maximum number of optimizer iterations.
        tol: tolerance for termination.
        x0: initial node positions, of shape (N, 2) for an N x N matrix.
            If None, positions are drawn uniformly in [0, 1), seeded by `seed`.
        seed: seed for the random initial positions, ignored if `x0` is set.
            If None, results differ between runs.
    """

    method: str = "Nelder-Mead"
    maxiter: int = 200000
    tol: float = 1e-8
    x0: np.ndarray | None = None
    seed: int | None = None


def interaction_embedding(
    matrix: np.ndarray,
    method: str,
    x0: np.ndarray | None,
    maxiter: int,
    tol: float,
    seed: int | None = None,
) -> DataGraph:
    """Embed a matrix into the interaction term of the Rydberg analog model.

    Finds node coordinates whose interactions 1/rᵢⱼ^6 best approximate the
    off-diagonal entries of `matrix`, using `scipy.optimize.minimize`.

    Args:
        matrix: symmetric N x N matrix to embed.
        method: optimization method passed to `scipy.optimize.minimize`.
        x0: initial node positions, of shape (N, 2).
            If None, positions are drawn uniformly in [0, 1), seeded by `seed`.
        maxiter: maximum number of optimizer iterations.
        tol: tolerance for termination.
        seed: seed for the random initial positions, ignored if `x0` is set.
            If None, results differ between runs.

    Returns:
        DataGraph: graph with node coordinates centered on their median.
    """
    matrix = np.asarray(matrix, dtype=float)

    def cost_function(new_coords: np.ndarray, matrix: np.ndarray) -> np.floating[Any]:
        """Cost function."""
        new_coords = np.reshape(new_coords, (len(matrix), 2))
        # Cost based on minimizing the distance between the matrix and the interaction 1/r^6
        new_matrix = squareform(1.0 / (pdist(new_coords) ** 6))
        return np.linalg.norm(new_matrix - matrix)

    if x0 is None:
        rng = np.random.default_rng(seed)
        x0 = rng.random(len(matrix) * 2)

    x0 = np.asarray(x0, dtype=float).flatten()

    res = minimize(
        cost_function,
        x0,
        args=(matrix,),
        method=method,
        tol=tol,
        options={"maxiter": maxiter},
    )

    coords = np.reshape(res.x, (len(matrix), 2))

    centered_coords = coords - np.median(coords, axis=0)

    graph = DataGraph.from_coordinates(centered_coords.tolist())

    return graph
