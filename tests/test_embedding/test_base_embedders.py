from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from qoolqit.embedding import EmbedderConfig
from qoolqit.embedding.graph_embedder import GraphToGraphEmbedder
from qoolqit.embedding.matrix_embedder import MatrixToGraphEmbedder
from qoolqit.graphs import DataGraph


def test_custom_embedders() -> None:

    def some_embedding_algo(data: DataGraph, param1: float) -> DataGraph:
        return data

    # Config does not inherit from EmbedderConfig
    @dataclass
    class WrongTypeConfig:
        param1: float = 1.0

    with pytest.raises(TypeError):
        GraphToGraphEmbedder(some_embedding_algo, WrongTypeConfig())  # type: ignore[type-var]

    # Config params don't match algo params
    @dataclass
    class WrongParamConfig(EmbedderConfig):
        param2: float = 1.0

    with pytest.raises(
        TypeError,
        match="Config WrongParamConfig is not compatible with the algorithm some_embedding_algo, "
        "as not all configuration fields correspond to keyword arguments in the algorithm",
    ):
        GraphToGraphEmbedder(some_embedding_algo, WrongParamConfig())

    # Embedding function returns unexpected data
    @dataclass
    class SomeConfig(EmbedderConfig):
        param1: float = 1.0

    def some_wrong_embedding_algo(data: DataGraph, param1: float) -> float:
        return 2.0

    embedder_g2g = GraphToGraphEmbedder(some_wrong_embedding_algo, SomeConfig())
    with pytest.raises(TypeError):
        graph = DataGraph.random_er(5, 0.5)
        embedder_g2g.embed(graph)

    embedder_m2g = MatrixToGraphEmbedder(some_wrong_embedding_algo, SomeConfig())
    with pytest.raises(TypeError):
        matrix = np.random.rand(5, 5)
        matrix = matrix + matrix.T
        embedder_m2g.embed(matrix)


@pytest.mark.parametrize(
    ("data", "error", "match"),
    [
        (np.ones(3), ValueError, "Data must be a 2D matrix"),
        (np.array([[0.0, 1.0], [2.0, 0.0]]), ValueError, "Data must be a symmetric matrix"),
        ([[0.0, 1.0], [1.0, 0.0]], TypeError, "requires data to be a symmetric matrix"),
    ],
)
def test_matrix_to_graph_embedder_invalid_input(
    data: object, error: type[Exception], match: str
) -> None:
    embedder = MatrixToGraphEmbedder(lambda data: data, EmbedderConfig())
    with pytest.raises(error, match=match):
        embedder.embed(data)  # type: ignore[arg-type]


def test_embed_passes_config_to_algorithm() -> None:
    @dataclass
    class SomeConfig(EmbedderConfig):
        param1: float = 1.0

    received = []

    def some_embedding_algo(data: DataGraph, param1: float) -> DataGraph:
        received.append(param1)
        return data

    embedder = GraphToGraphEmbedder(some_embedding_algo, SomeConfig(param1=2.0))
    embedder.embed(DataGraph())
    assert received == [2.0]
