from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform

from qoolqit.graphs import DataGraph

from ..base_embedder import EmbedderConfig


@dataclass
class InteractionEmbedderConfig(EmbedderConfig):
    """Configuration parameters for the interaction embedding."""

    method: str = "Nelder-Mead"
    maxiter: int = 200000
    tol: float = 1e-8
    x0: np.ndarray | None = None
    """If provided, initial positions to start from.

    Must be of shape (N, 2) or flattened to (2N,), where N is the size of the matrix
    to embed. Otherwise, random positions are drawn uniformly in [0, 1) from an
    unseeded generator, so results may differ between runs. For reproducible
    results, pass positions drawn from a seeded generator, e.g.
    `np.random.default_rng(seed).random((N, 2))`.
    """


def interaction_embedding(
    matrix: np.ndarray, method: str, x0: np.ndarray | None, maxiter: int, tol: float
) -> DataGraph:
    """Matrix embedding into the interaction term of the Rydberg Analog Model.

    Uses scipy.minimize to find the optimal set of node coordinates such that the
    matrix of values 1/(r_ij)^6 approximate the off-diagonal terms of the input matrix.

    Check the documentation for scipy.minimize for more information about each parameter:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html

    If `x0` is None, the starting positions are drawn uniformly in [0, 1) from an
    unseeded generator, so repeated calls may return different embeddings. For
    reproducible results, generate `x0` with your own seeded generator and pass it
    explicitly:

    ```python
    embedder = InteractionEmbedder()
    rng = np.random.default_rng(seed=4851)
    embedder.config.x0 = rng.random((len(matrix), 2))
    ```

    Arguments:
        matrix: the matrix to embed.
        method: the method used by scipy.minimize.
        x0: starting positions, of shape (N, 2) or flattened to (2N,), where N is
            the size of `matrix`. If None, an unseeded random initialization is used.
        maxiter: maximum number of iterations.
        tol: tolerance for termination.
    """

    def cost_function(new_coords: np.ndarray, matrix: np.ndarray) -> np.floating[Any]:
        """Cost function."""
        new_coords = np.reshape(new_coords, (len(matrix), 2))
        # Cost based on minimizing the distance between the matrix and the interaction 1/r^6
        new_matrix = squareform(1.0 / (pdist(new_coords) ** 6))
        return np.linalg.norm(new_matrix - matrix)

    if x0 is None:
        # random initial positions
        rng = np.random.default_rng()
        x0 = rng.random(len(matrix) * 2, dtype=matrix.dtype)

    # make sure positions are of same type as matrix and flatten
    x0 = np.asarray(x0, dtype=matrix.dtype).flatten()

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
