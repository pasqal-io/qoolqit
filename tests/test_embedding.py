from __future__ import annotations

import numpy as np
import pytest

from qoolqit.embedding import EmbeddingConfig, InteractionEmbedder, SpringLayoutEmbedder, GraphToGraphEmbedder, MatrixToGraphEmbedder, SpringLayoutConfig, InteractionEmbeddingConfig
from qoolqit.graphs import DataGraph

from dataclasses import dataclass

@pytest.mark.parametrize("n_qubits", [3, 5, 10])
def test_spring_layout_embedding(n_qubits: int) -> None:

    graph = DataGraph.random_er(n=n_qubits, p=0.2)
    assert not graph.has_coords
    embedder = SpringLayoutEmbedder()
    embedded_graph = embedder.embed(graph)

    assert embedded_graph.has_coords

    embedder.config.k = 2.0
    embedded_graph_2 = embedder.embed(graph)
    coords_1 = np.array(list(embedded_graph.coords.values()))
    coords_2 = np.array(list(embedded_graph_2.coords.values()))

    assert not np.array_equal(coords_1, coords_2)

    with pytest.raises(TypeError):
        matrix = np.random.rand(n_qubits, n_qubits)
        embedder.embed(matrix)


@pytest.mark.parametrize("n_qubits", [3, 4, 5])
def test_interaction_embedding(n_qubits: int) -> None:

    embedder = InteractionEmbedder()
    embedder.config.method = "Nelder-Mead"

    matrix = np.random.rand(n_qubits)

    with pytest.raises(ValueError):
        # Fails when not a 2D matrix
        embedded_graph = embedder.embed(matrix)

    matrix = np.random.rand(n_qubits, n_qubits)

    with pytest.raises(ValueError):
        # Fails when not symmetric
        embedded_graph = embedder.embed(matrix)

    matrix = matrix + matrix.T
    embedded_graph = embedder.embed(matrix)

    assert embedded_graph.has_coords

    embedder.config.method = "COBYLA"
    embedded_graph_2 = embedder.embed(matrix)
    coords_1 = np.array(list(embedded_graph.coords.values()))
    coords_2 = np.array(list(embedded_graph_2.coords.values()))

    assert not np.array_equal(coords_1, coords_2)

    with pytest.raises(TypeError):
        graph = DataGraph.random_er(n=n_qubits, p=0.2)
        embedder.embed(graph)


def test_custom_embedders() -> None:

    def some_embedding_algo(data: DataGraph, param1: float) -> DataGraph:
        return data

    ### Config does not inherit from EmbeddingConfig
    @dataclass
    class SomeConfig:
        param1: float = 1.0

    with pytest.raises(TypeError):
        embedder = GraphToGraphEmbedder(some_embedding_algo, SomeConfig())

    ### Config params don't match algo params
    @dataclass
    class SomeConfig(EmbeddingConfig):
        param2: float = 1.0

    with pytest.raises(KeyError):
        embedder = GraphToGraphEmbedder(some_embedding_algo, SomeConfig())

    ### Embedding function returns unexpected data
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