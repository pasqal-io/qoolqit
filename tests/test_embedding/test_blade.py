from __future__ import annotations

import networkx as nx
import numpy as np
import pytest
import scipy

from qoolqit import AnalogDevice, BladeConfig, DigitalAnalogDevice, MockDevice
from qoolqit.devices import Device
from qoolqit.embedding.algorithms.blade._helpers import (
    normalized_best_dist,
    normalized_interaction,
)
from qoolqit.embedding.algorithms.blade._qubo_mapper import Qubo
from qoolqit.embedding.algorithms.blade.blade import (
    blade,
    update_positions,
)


@pytest.mark.parametrize(
    "max_distance_to_walk, expected_distance",
    [
        (np.inf, normalized_best_dist(1e-4)),
        (0, 1),
        (1, 3),
        (20, normalized_best_dist(1e-4)),
    ],
)
def test_update_positions(
    max_distance_to_walk: float | int, expected_distance: float | int
) -> None:
    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    weight = 1e-4
    interactions_graph.add_edge(0, 1, weight=weight)

    new_positions = update_positions(
        positions=np.array([[0, 0], [1, 0]]),
        target_interactions_graph=interactions_graph,
        max_distance_to_walk=max_distance_to_walk,
    )

    np.testing.assert_allclose(
        np.linalg.norm(new_positions[0] - new_positions[1]), expected_distance
    )


def test_max_dist_constraint() -> None:
    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    interactions_graph.add_edge(0, 1, weight=1)

    max_radial_dist = 0.1

    new_positions = update_positions(
        positions=np.array([[-0.5, 0], [0.5, 0]]),
        target_interactions_graph=interactions_graph,
        max_dist=max_radial_dist,
    )

    np.testing.assert_allclose(
        np.linalg.norm(new_positions[0] - new_positions[1]), 2 * max_radial_dist, rtol=1e-2
    )


def test_min_dist_constraint() -> None:
    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    interactions_graph.add_edge(0, 1, weight=normalized_interaction(10 * np.sqrt(2)))

    new_positions = update_positions(
        positions=np.array([[-10, 0], [0, 10]]),
        target_interactions_graph=interactions_graph,
        min_dist=30,
    )

    np.testing.assert_allclose(np.linalg.norm(new_positions[0] - new_positions[1]), 30, rtol=1e-2)


def test_min_dist_constraint_limited() -> None:
    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    interactions_graph.add_edge(0, 1, weight=normalized_interaction(1))

    new_positions = update_positions(
        positions=np.array([[-1, 0], [1, 0]]),
        target_interactions_graph=interactions_graph,
        min_dist=10,
        max_distance_to_walk=(0, 2, 0),
    )

    expected_positions = np.array([[-3, 0], [3, 0]])
    np.testing.assert_allclose(new_positions, expected_positions)


def test_max_dist_constraint_limited() -> None:
    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    interactions_graph.add_edge(0, 1, weight=normalized_interaction(1))

    new_positions = update_positions(
        positions=np.array([[-10, 0], [10, 0]]),
        target_interactions_graph=interactions_graph,
        max_dist=1,
        max_distance_to_walk=(0, 0, 1),
    )

    expected_positions = np.array([[-9, 0], [9, 0]])
    np.testing.assert_allclose(new_positions, expected_positions)


def test_force_based_embedding() -> None:
    min_dist = 1
    max_dist = 2

    factor_dist_0_1 = 1 / 1.1
    factor_dist_2_3 = 1.2

    qubo = np.array(
        [
            [0, normalized_interaction(min_dist * factor_dist_0_1), 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, normalized_interaction(min_dist * factor_dist_2_3)],
            [0, 0, 0, 0],
        ]
    )

    positions = blade(
        matrix=qubo,
        max_min_dist_ratio=max_dist / min_dist,
        steps_per_round=1000,
        starting_positions=np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]]) * max_dist / 3,
        dimensions=(2, 2),
    )

    new_min_dist = np.linalg.norm(positions[0] - positions[1])
    new_max_dist = new_min_dist * (max_dist / min_dist)
    new_max_diameter_dist = 2 * new_max_dist

    np.testing.assert_allclose(np.linalg.norm(positions[0] - positions[1]), new_min_dist)

    assert (
        (new_max_diameter_dist - new_min_dist)
        < np.linalg.norm(positions[0] - positions[2])
        < new_max_diameter_dist
    )
    assert (
        new_max_diameter_dist - new_min_dist
        < np.linalg.norm(positions[0] - positions[3])
        < new_max_diameter_dist
    )

    assert (
        new_max_diameter_dist - new_min_dist
        < np.linalg.norm(positions[1] - positions[2])
        < new_max_diameter_dist
    )
    assert (
        new_max_diameter_dist - new_min_dist
        < np.linalg.norm(positions[1] - positions[3])
        < new_max_diameter_dist
    )

    expected_dist = new_min_dist * factor_dist_2_3 / factor_dist_0_1
    np.testing.assert_allclose(np.linalg.norm(positions[2] - positions[3]), expected_dist, rtol=0.1)


def test_high_dimension_increase_after_equilibrium() -> None:
    qubo = np.array(
        [
            [0.0, 0.7, 0.3, 0.5, 0.4, 0.9, 0.9, 0.7, 0.9, 0.8],
            [0.0, 0.0, 0.7, 0.4, 0.8, 0.4, 0.8, 1.0, 0.5, 0.8],
            [0.0, 0.0, 0.0, 0.7, 0.5, 0.8, 0.0, 0.8, 0.7, 1.0],
            [0.0, 0.0, 0.0, 0.0, 0.7, 0.0, 0.1, 0.9, 0.2, 0.6],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.2, 0.4, 0.7, 0.4],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.9, 0.4, 0.8],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.4, 0.3],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7, 0.6],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )
    blade(qubo, dimensions=(2, 2, 10), steps_per_round=100)


def test_initial_positions_with_fewer_dimensions_than_starting_dimensions() -> None:
    expected_distances = np.array(
        [
            [0, 1, np.sqrt(2), 1],
            [0, 0, 1, np.sqrt(2)],
            [0, 0, 0, 1],
            [0, 0, 0, 0],
        ]
    )
    expected_interactions = np.triu(normalized_interaction(expected_distances), k=1)

    starting_positions = np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]])
    positions = blade(
        expected_interactions,
        starting_positions=starting_positions,
        dimensions=(starting_positions.shape[1] + 2, 2),
    )

    output_distances = np.triu(
        scipy.spatial.distance.squareform(scipy.spatial.distance.pdist(positions)), k=1
    )

    np.testing.assert_allclose(output_distances, expected_distances, rtol=1e-4)


def test_drawing() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    interactions_graph.add_edge(0, 1, weight=normalized_interaction(1))

    plt.close("all")
    assert len(plt.get_fignums()) == 0
    update_positions(
        positions=np.array([[-10, 0], [10, 0]]),
        target_interactions_graph=interactions_graph,
        max_dist=1,
        max_distance_to_walk=(0, 0, 1),
        draw_step=True,
    )
    assert len(plt.get_fignums()) > 0
    plt.close("all")


def test_simple_positions() -> None:
    qubo = np.array(
        [
            [0, 2],
            [0, 0],
        ]
    )
    positions = blade(qubo, dimensions=(2, 2), steps_per_round=100)
    distances = np.triu(
        np.linalg.norm(positions[np.newaxis, :, :] - positions[:, np.newaxis, :], axis=-1), k=1
    )

    expected_distances = np.array([[0, 2 ** (-1 / 6)], [0, 0]])
    np.testing.assert_allclose(distances, expected_distances)


@pytest.mark.parametrize(
    "device, expected_max_min_ratio",
    [(AnalogDevice(), 7.6), (DigitalAnalogDevice(), 12.5), (MockDevice(), None)],
)
def test_config_from_device(device: Device, expected_max_min_ratio: float | None) -> None:
    config = BladeConfig(device=device)
    assert config.max_min_dist_ratio == expected_max_min_ratio


def test_qubo_nodes() -> None:
    terms: list = [("n1", 2), (4, "I am a node label"), (0, 8)]
    coeffs = [0.1, 1.2, 2.3]
    qubo = Qubo(terms=terms, coeffs=coeffs)

    # expected sorted by value or alphabetically
    expected_nodes = [0, 2, 4, 8, "I am a node label", "n1"]
    qubo_nodes = qubo.nodes()

    assert qubo_nodes == expected_nodes
