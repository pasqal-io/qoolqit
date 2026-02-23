from __future__ import annotations

import networkx as nx
import numpy as np
import pytest
from scipy.spatial.distance import pdist, squareform

from qoolqit.embedding import SpringLayoutEmbedder
from qoolqit.embedding.algorithms.spring_layout_embedding import spring_layout_embedding
from qoolqit.graphs import DataGraph


@pytest.mark.parametrize("n_qubits", [3, 5, 10])
def test_spring_layout_embedding(n_qubits: int) -> None:

    graph = DataGraph.random_er(n=n_qubits, p=0.2)
    assert not graph.has_coords
    embedder = SpringLayoutEmbedder()
    embedded_graph = embedder.embed(graph)

    assert embedded_graph.has_coords

    embedded_graph_2 = embedder.embed(graph)
    coords_1 = np.array(list(embedded_graph.coords.values()))
    coords_2 = np.array(list(embedded_graph_2.coords.values()))

    assert not np.array_equal(coords_1, coords_2)

    with pytest.raises(TypeError):
        matrix = np.random.rand(n_qubits, n_qubits)
        embedder.embed(matrix)  # type: ignore


@pytest.mark.parametrize(
    "coords",
    [
        [[-0.5, 0.0], [0.5, 0.0], [-2.0, 2.0]],
        [
            [0.8468, 1.2528],
            [-0.4905, -0.2855],
            [-0.9455, -0.9925],
            [-1.6275, 1.2430],
            [2.1791, 0.2225],
        ],
        [[np.cos(theta), np.sin(theta)] for theta in np.linspace(0, 2 * np.pi, 8, endpoint=False)],
    ],
)
def test_spring_layout_positions(coords: list | np.ndarray) -> None:
    # generate a graph based on the given coordinates
    # weights are set to 1/r^6, where r is the pairwise distance
    expected_interactions = squareform(1 / pdist(coords) ** 6)
    expected_distances = squareform(pdist(coords))
    graph = nx.from_numpy_array(expected_interactions, create_using=DataGraph)
    assert not graph.has_coords

    # embed the graph and extract interactions
    threshold = 1e-4
    iterations = 500  # sufficiently high to do not stop before threshold
    seed = 0  # for reproducibility
    embedded_graph = spring_layout_embedding(
        graph, iterations=iterations, threshold=threshold, seed=seed
    )
    embedded_coords = list(embedded_graph.coords.values())
    embedded_distances = squareform(pdist(embedded_coords))

    # compare the embedded/expected distance matrices
    # spring_layout sets convergence criteria to |delta_pos| / nnodes < threshold
    expected_tolerance = threshold * len(coords)
    # TOFIX: older networkx have lower tolerance for the convergence
    # remove this when dropping python 3.10 and networkx ~3.4 support
    if nx.__version__ < "3.5":
        expected_tolerance *= 10

    stress = np.linalg.norm(embedded_distances - expected_distances)
    np.testing.assert_allclose(stress, 0.0, atol=expected_tolerance, rtol=0.0)
