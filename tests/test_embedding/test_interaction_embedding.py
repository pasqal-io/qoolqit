from __future__ import annotations

import numpy as np
import pytest

from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig
from qoolqit.graphs import DataGraph


@pytest.mark.parametrize("n_qubits", [3, 4, 5])
def test_interaction_embedding(n_qubits: int) -> None:

    rng = np.random.default_rng(seed=1937604089)
    config = InteractionEmbedderConfig(seed=1668045428)
    embedder = InteractionEmbedder(config=config)

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

    # Config changes reach the optimizer
    embedder.config.maxiter = 1
    coords_maxiter = np.array(list(embedder.embed(matrix).coords.values()))
    assert not np.allclose(coords, coords_maxiter)


def test_interaction_embedding_x0_takes_precedence_over_seed() -> None:
    rng = np.random.default_rng(seed=1937604089)
    matrix = rng.random((4, 4))
    matrix = matrix + matrix.T
    x0 = rng.random((4, 2))

    config_1 = InteractionEmbedderConfig(x0=x0, seed=1668045428)
    config_2 = InteractionEmbedderConfig(x0=x0, seed=3929213679)
    coords_1 = np.array(list(InteractionEmbedder(config_1).embed(matrix).coords.values()))
    coords_2 = np.array(list(InteractionEmbedder(config_2).embed(matrix).coords.values()))

    # same result since seeds in config are ignored when x0 is provided in config
    np.testing.assert_allclose(coords_1, coords_2, atol=1e-6)


def test_interaction_embedder_docstring_example() -> None:
    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    config = InteractionEmbedderConfig(seed=3083257284)
    embedder = InteractionEmbedder(config=config)
    graph_1 = embedder.embed(matrix)
    graph_2 = embedder.embed(matrix)
    assert graph_1.coords == graph_2.coords


def test_interaction_embedding_int_matrix() -> None:
    config = InteractionEmbedderConfig(seed=2643948799)
    embedder = InteractionEmbedder(config=config)
    graph = embedder.embed(np.array([[0, 2, 1], [2, 0, 3], [1, 3, 0]]))
    assert all(isinstance(x, float) for coord in graph.coords.values() for x in coord)
