"""Interaction embedding: fit node coordinates to an interaction matrix with scipy.optimize."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from scipy.optimize import minimize
from scipy.spatial.distance import cdist

from qoolqit.embedding.base_embedder import EmbedderConfig
from qoolqit.graphs import DataGraph


@dataclass
class InteractionEmbedderConfig(EmbedderConfig):
    """Configuration parameters for the interaction embedding.

    Explicit initial positions, one (x, y) row per node:

    ```python
    import numpy as np
    from qoolqit.embedding import InteractionEmbedderConfig

    x0 = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    config = InteractionEmbedderConfig(x0=x0)
    ```

    Random initial positions with a fixed seed:

    ```python
    from qoolqit.embedding import InteractionEmbedderConfig

    config = InteractionEmbedderConfig(seed=3083257284)
    ```

    Initial positions from an external seeded generator:

    ```python
    import numpy as np
    from qoolqit.embedding import InteractionEmbedderConfig

    rng = np.random.default_rng(seed=2754767221)
    config = InteractionEmbedderConfig(x0=rng.random((5, 2)))
    ```

    Attributes:
        method: optimization method passed to `scipy.optimize.minimize`.
        maxiter: maximum number of optimizer iterations.
        tol: tolerance for termination.
        x0: initial node positions, of shape (N, 2) for an N x N matrix, or flattened to (2N,).
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

    Finds node coordinates whose interactions 1/rᵢⱼ⁶ best approximate the
    off-diagonal entries of `matrix`, using `scipy.optimize.minimize`.

    Args:
        matrix: symmetric N x N target matrix to embed.
        method: optimization method passed to `scipy.optimize.minimize`.
        x0: initial node positions, of shape (N, 2) or flattened to (2N,).
            If None, positions are drawn uniformly in [0, 1), seeded by `seed`.
        maxiter: maximum number of optimizer iterations.
        tol: tolerance for termination.
        seed: seed for the random initial positions, ignored if `x0` is set.
            If None, results differ between runs.

    Returns:
        DataGraph: graph with node coordinates centered on their median.
    """
    matrix = np.asarray(matrix, dtype=np.float64)

    def cost_function(new_coords: np.ndarray) -> float:
        """Distance between the matrix and the interaction 1/r⁶."""
        new_coords = np.reshape(new_coords, (len(matrix), 2))
        squared_dist: npt.NDArray[np.float64] = cdist(new_coords, new_coords, metric="sqeuclidean")
        np.fill_diagonal(squared_dist, np.inf)  # 1/inf = 0: no self-interaction
        interactions = 1.0 / (squared_dist * squared_dist * squared_dist)
        return np.linalg.norm(matrix - interactions)

    if x0 is None:
        rng = np.random.default_rng(seed)
        x0 = rng.random(len(matrix) * 2)

    x0 = np.asarray(x0, dtype=float).flatten()

    res = minimize(
        cost_function,
        x0,
        method=method,
        tol=tol,
        options={"maxiter": maxiter},
    )

    coords = np.reshape(res.x, (len(matrix), 2))

    centered_coords = coords - np.median(coords, axis=0)

    graph = DataGraph.from_coordinates(centered_coords.tolist())

    return graph
