from __future__ import annotations

import numpy as np
import pytest

from qoolqit.embedding import SpringLayoutEmbedder
from qoolqit.graphs import DataGraph


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
        embedder.embed(matrix)  # type: ignore
