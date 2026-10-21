from __future__ import annotations

import numpy as np
import pytest

from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig
from qoolqit.graphs import DataGraph


@pytest.mark.parametrize("n_qubits", [3, 4, 5])
def test_interaction_embedding(n_qubits: int) -> None:

    rng = np.random.default_rng(seed=n_qubits)
    embedder = InteractionEmbedder()
    embedder.config.rng = 42

    with pytest.raises(ValueError):
        # Fails when not a 2D matrix
        embedder.embed(rng.random(n_qubits))

    matrix = rng.random((n_qubits, n_qubits))

    with pytest.raises(ValueError):
        # Fails when not symmetric
        embedder.embed(matrix)

    with pytest.raises(TypeError):
        embedder.embed(DataGraph.random_er(n=n_qubits, p=0.2))  # type: ignore

    matrix = matrix + matrix.T
    embedded_graph = embedder.embed(matrix)
    assert embedded_graph.has_coords
    coords = np.array(list(embedded_graph.coords.values()))

    # Same seed, same result
    coords_same_seed = np.array(list(embedder.embed(matrix).coords.values()))
    np.testing.assert_allclose(coords, coords_same_seed, atol=1e-6)

    # A Generator seeded the same way gives the same result
    embedder.config.rng = np.random.default_rng(42)
    coords_generator = np.array(list(embedder.embed(matrix).coords.values()))
    np.testing.assert_allclose(coords, coords_generator, atol=1e-6)
    embedder.config.rng = 42

    # Config changes reach the optimizer
    embedder.config.maxiter = 1
    coords_maxiter = np.array(list(embedder.embed(matrix).coords.values()))
    assert not np.allclose(coords, coords_maxiter)

    # Explicit x0 is reproducible and takes precedence over rng
    embedder.config.maxiter = 200000
    embedder.config.x0 = rng.random((n_qubits, 2))
    coords_x0_1 = np.array(list(embedder.embed(matrix).coords.values()))
    embedder.config.rng = 7
    coords_x0_2 = np.array(list(embedder.embed(matrix).coords.values()))
    np.testing.assert_allclose(coords_x0_1, coords_x0_2, atol=1e-6)


def test_interaction_embedder_docstring_example() -> None:
    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    embedder = InteractionEmbedder(InteractionEmbedderConfig(rng=42))
    graph_1 = embedder.embed(matrix)
    graph_2 = embedder.embed(matrix)
    assert graph_1.coords == graph_2.coords
