from __future__ import annotations

from dataclasses import dataclass
from qoolqit.graphs import DataGraph
from qoolqit.embedding.graph_embedder import GraphToGraphEmbedder
from qoolqit.embedding.matrix_embedder import MatrixToGraphEmbedder
from qoolqit.embedding.base_embedder import EmbeddingConfig

import pytest
import numpy as np


def test_custom_embedders() -> None:

    def some_embedding_algo(data: DataGraph, param1: float) -> DataGraph:
        return data

    # Config does not inherit from EmbeddingConfig
    @dataclass
    class WrongTypeConfig:
        param1: float = 1.0

    with pytest.raises(TypeError):
        embedder = GraphToGraphEmbedder(some_embedding_algo, WrongTypeConfig())  # type: ignore

    # Config params don't match algo params
    @dataclass
    class WrongParamConfig(EmbeddingConfig):  # type: ignore
        param2: float = 1.0

    with pytest.raises(KeyError):
        embedder = GraphToGraphEmbedder(some_embedding_algo, WrongParamConfig())

    # Embedding function returns unexpected data
    @dataclass
    class SomeConfig(EmbeddingConfig):
        param1: float = 1.0

    def some_wrong_embedding_algo(data: DataGraph, param1: float) -> float:
        return 2.0

    embedder = GraphToGraphEmbedder(some_wrong_embedding_algo, SomeConfig())

    with pytest.raises(TypeError):
        graph = DataGraph.random_er(5, 0.5)
        embedder.embed(graph)

    embedder = MatrixToGraphEmbedder(some_wrong_embedding_algo, SomeConfig())

    with pytest.raises(TypeError):
        matrix = np.random.rand(5, 5)
        matrix = matrix + matrix.T
        embedder.embed(matrix)
