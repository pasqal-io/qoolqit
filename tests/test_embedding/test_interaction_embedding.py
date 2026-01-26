from __future__ import annotations

import numpy as np
import pytest

from qoolqit.embedding import InteractionEmbedder
from qoolqit.graphs import DataGraph


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
        embedder.embed(graph)  # type: ignore
