from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest
from scipy.optimize import minimize

from qoolqit.embedding import InteractionEmbedder, InteractionEmbedderConfig
from qoolqit.graphs import DataGraph


def test_interaction_embedder_default_config() -> None:
    assert InteractionEmbedder().config == InteractionEmbedderConfig()


@pytest.mark.parametrize(
    "coords",
    [
        [[0.0, 0.0], [1.0, 0.0], [0.3, 0.8]],
        [[0.0, 0.0], [1.0, 0.0], [0.0, 1.5]],
    ],
)
def test_interaction_embedding_recovers_interactions(coords: list[list[float]]) -> None:
    # Three nodes: from four on, Nelder-Mead often stops in a local minimum.
    target = DataGraph.from_coordinates(coords).interaction_matrix()
    embedder = InteractionEmbedder(InteractionEmbedderConfig(seed=1668045428))
    graph = embedder.embed(target)
    np.testing.assert_allclose(graph.interaction_matrix(), target, rtol=1e-6)


@pytest.mark.parametrize(
    "coords",
    [
        [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.1, 1.2]],
        [[0.0, 0.0], [1.0, 0.0], [1.3, 0.9], [0.5, 1.5], [-0.3, 0.9]],
    ],
)
def test_interaction_embedding_converges_from_nearby_start(coords: list[list[float]]) -> None:
    rng = np.random.default_rng(seed=1937604089)
    x0 = np.array(coords) + 0.1 * rng.standard_normal((len(coords), 2))
    target = DataGraph.from_coordinates(coords).interaction_matrix()
    embedder = InteractionEmbedder(InteractionEmbedderConfig(x0=x0))
    graph = embedder.embed(target)
    np.testing.assert_allclose(graph.interaction_matrix(), target, rtol=1e-6)


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


def test_interaction_embedding_accepts_flat_x0() -> None:
    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    x0 = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    graph_1 = InteractionEmbedder(InteractionEmbedderConfig(x0=x0)).embed(matrix)
    graph_2 = InteractionEmbedder(InteractionEmbedderConfig(x0=x0.flatten())).embed(matrix)
    assert graph_1.coords == graph_2.coords


def test_interaction_embedding_same_seed_same_coords() -> None:
    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    config = InteractionEmbedderConfig(seed=3083257284)
    embedder = InteractionEmbedder(config=config)
    graph_1 = embedder.embed(matrix)
    graph_2 = embedder.embed(matrix)
    assert graph_1.coords == graph_2.coords


def test_interaction_embedding_passes_maxiter_to_minimize() -> None:
    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    target = "qoolqit.embedding.algorithms.interaction_embedding.minimize"
    with patch(target, wraps=minimize) as mock_minimize:
        InteractionEmbedder(InteractionEmbedderConfig(maxiter=13)).embed(matrix)
    mock_minimize.assert_called_once()
    assert mock_minimize.call_args.kwargs["options"] == {"maxiter": 13}


def test_interaction_embedding_coords_centered_on_median() -> None:
    matrix = np.array([[0.0, 1.0, 0.5], [1.0, 0.0, 0.2], [0.5, 0.2, 0.0]])
    embedder = InteractionEmbedder(InteractionEmbedderConfig(seed=3083257284))
    coords = np.array(list(embedder.embed(matrix).coords.values()))
    np.testing.assert_allclose(np.median(coords, axis=0), 0.0, atol=1e-12)


def test_interaction_embedding_int_matrix() -> None:
    config = InteractionEmbedderConfig(seed=2643948799)
    embedder = InteractionEmbedder(config=config)
    graph = embedder.embed(np.array([[0, 2, 1], [2, 0, 3], [1, 3, 0]]))
    assert all(isinstance(x, float) for coord in graph.coords.values() for x in coord)
