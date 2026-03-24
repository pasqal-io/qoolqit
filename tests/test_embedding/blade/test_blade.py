from __future__ import annotations

from types import SimpleNamespace
from typing import Callable

import networkx as nx
import numpy as np
import pytest
import scipy

from qoolqit import AnalogDevice, BladeConfig, DigitalAnalogDevice, MockDevice
from qoolqit.devices import Device
from qoolqit.embedding.algorithms.blade._helpers import (
    distance_matrix_from_positions,
    interaction_matrix_from_distances,
    interaction_matrix_from_positions,
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
def test_update_positions_reaches_distance_limited_by_distance_to_walk(
    max_distance_to_walk: float | int, expected_distance: float | int
) -> None:
    qubo = np.array([[0, 1e-4], [0, 0]])
    qubo = qubo + qubo.T

    new_positions = update_positions(
        positions=np.array([[0, 0], [1, 0]]),
        target_interactions=qubo,
        max_distance_to_walk=max_distance_to_walk,
    )

    np.testing.assert_allclose(
        np.linalg.norm(new_positions[0] - new_positions[1]), expected_distance
    )


def test_max_dist_constraint() -> None:
    max_radial_dist = 0.1

    qubo = np.array([[0, 1], [0, 0]])
    qubo = qubo + qubo.T

    new_positions = update_positions(
        positions=np.array([[-0.5, 0], [0.5, 0]]),
        target_interactions=qubo,
        max_radius=max_radial_dist,
    )

    np.testing.assert_allclose(
        np.linalg.norm(new_positions[0] - new_positions[1]), 2 * max_radial_dist, rtol=1e-2
    )


def test_min_dist_constraint() -> None:
    qubo = np.array([[0, normalized_interaction(10 * np.sqrt(2))], [0, 0]])
    qubo = qubo + qubo.T

    new_positions = update_positions(
        positions=np.array([[-10, 0], [0, 10]]),
        target_interactions=qubo,
        min_dist=30,
    )

    np.testing.assert_allclose(np.linalg.norm(new_positions[0] - new_positions[1]), 30, rtol=1e-2)


def test_min_dist_constraint_limited() -> None:
    qubo = np.array([[0, normalized_interaction(1)], [0, 0]])
    qubo = qubo + qubo.T

    new_positions = update_positions(
        positions=np.array([[-1, 0], [1, 0]]),
        target_interactions=qubo,
        min_dist=10,
        max_distance_to_walk=(0, 2, 0),
    )

    expected_positions = np.array([[-3, 0], [3, 0]])
    np.testing.assert_allclose(new_positions, expected_positions)


def test_max_dist_constraint_limited() -> None:
    qubo = np.array([[0, normalized_interaction(1)], [0, 0]])
    qubo = qubo + qubo.T

    new_positions = update_positions(
        positions=np.array([[-10, 0], [10, 0]]),
        target_interactions=qubo,
        max_radius=1,
        max_distance_to_walk=(0, 0, 1),
    )

    expected_positions = np.array([[-9, 0], [9, 0]])
    np.testing.assert_allclose(new_positions, expected_positions)


def test_weight_differences_discrepancy() -> None:
    pairs_curr_dists = np.array([1.1, 50])
    pairs_curr_weights = normalized_interaction(pairs_curr_dists)

    pairs_target_dists = np.array([1, 45])
    pairs_target_weights = normalized_interaction(pairs_target_dists)

    pairs_weight_diffs = normalized_interaction(pairs_target_dists) - normalized_interaction(
        pairs_curr_dists
    )
    pairs_dist_diffs = pairs_target_dists - pairs_curr_dists

    assert pairs_weight_diffs[0] > 10 * pairs_weight_diffs[1]
    assert 10 * np.abs(pairs_dist_diffs[0]) < np.abs(pairs_dist_diffs[1])

    initial_positions = np.array([-pairs_curr_dists[0], 0, pairs_curr_dists[1]]).reshape(-1, 1)

    target_pairwise_distances = np.array(
        [
            [0, pairs_target_dists[0], np.sum(pairs_curr_dists)],
            [0, 0, pairs_target_dists[1]],
            [0, 0, 0],
        ]
    )

    target_interactions = interaction_matrix_from_distances(target_pairwise_distances)
    target_interactions += target_interactions.T

    for weight_relative_threshold in (0, 0.1, 0.9, 1):

        new_positions = update_positions(
            positions=initial_positions,
            target_interactions=target_interactions,
            weight_relative_threshold=weight_relative_threshold,
        )

        new_interactions = interaction_matrix_from_positions(new_positions)

        np.testing.assert_allclose(
            new_interactions[0, 1],
            weight_relative_threshold * pairs_curr_weights[0]
            + (1 - weight_relative_threshold) * pairs_target_weights[0],
        )
        np.testing.assert_allclose(new_interactions[1, 2], pairs_curr_weights[1], rtol=1e-2)


@pytest.fixture
def small_weight_difference_params() -> SimpleNamespace:
    pairs_curr_dists = np.array([1 + 1e-5, 3])
    pairs_curr_weights = normalized_interaction(pairs_curr_dists)

    pairs_target_dists = np.array([1, 3 + 1])
    pairs_target_weights = normalized_interaction(pairs_target_dists)

    pairs_weight_diffs = normalized_interaction(pairs_target_dists) - normalized_interaction(
        pairs_curr_dists
    )
    pairs_dist_diffs = pairs_target_dists - pairs_curr_dists

    expected_min_weight_diff_ratio = 1e1
    expected_min_temperature_ratio = 1e3

    weight_diff_ratio = np.abs(pairs_weight_diffs[1] / pairs_weight_diffs[0])
    temperature_ratio = np.abs(
        (pairs_dist_diffs[1] / pairs_weight_diffs[1])
        / (pairs_dist_diffs[0] / pairs_weight_diffs[0])
    )

    assert expected_min_weight_diff_ratio < weight_diff_ratio < 10 * expected_min_weight_diff_ratio
    assert expected_min_temperature_ratio < temperature_ratio < 10 * expected_min_temperature_ratio

    initial_positions = np.array([-pairs_curr_dists[0], 0, 1, 1 + pairs_curr_dists[1]]).reshape(
        -1, 1
    )
    current_pairwise_distances = np.triu(
        np.linalg.norm(
            initial_positions[np.newaxis, :, :] - initial_positions[:, np.newaxis, :], axis=-1
        ),
        k=1,
    )

    target_pairwise_distances = np.copy(current_pairwise_distances)
    target_pairwise_distances[0, 1] = pairs_target_dists[0]
    target_pairwise_distances[2, 3] = pairs_target_dists[1]

    target_interactions = interaction_matrix_from_distances(target_pairwise_distances)
    target_interactions += target_interactions.T

    return SimpleNamespace(
        initial_positions=initial_positions,
        target_interactions=target_interactions,
        pairs_curr_dists=pairs_curr_dists,
        pairs_curr_weights=pairs_curr_weights,
        pairs_target_dists=pairs_target_dists,
        pairs_target_weights=pairs_target_weights,
        weight_diff_ratio=weight_diff_ratio,
        pairs_dist_diffs=pairs_dist_diffs,
        pairs_weight_diffs=pairs_weight_diffs,
    )


def test_full_priority_on_small_weight_difference(
    small_weight_difference_params: SimpleNamespace,
) -> None:
    params = small_weight_difference_params
    weight_relative_threshold = 0

    new_positions = update_positions(
        positions=params.initial_positions,
        target_interactions=params.target_interactions,
        weight_relative_threshold=weight_relative_threshold,
        regulation_cursor=weight_relative_threshold,
    )

    new_interactions = interaction_matrix_from_positions(new_positions)

    np.testing.assert_allclose(
        new_interactions[0, 1],
        params.pairs_target_weights[0],
        err_msg=f"Error with {weight_relative_threshold=}",
    )
    second_pair_expected_progress = np.abs(params.weight_diff_ratio * params.pairs_dist_diffs[0])
    new_distances = np.linalg.norm(
        new_positions[np.newaxis, :, :] - new_positions[:, np.newaxis, :], axis=-1
    )
    np.testing.assert_allclose(
        new_distances[2, 3],
        params.pairs_curr_dists[1] * (1 - second_pair_expected_progress)
        + params.pairs_target_dists[1] * second_pair_expected_progress,
    )


def test_partial_priority_on_small_weight_difference(
    small_weight_difference_params: SimpleNamespace,
) -> None:
    params = small_weight_difference_params
    weight_relative_threshold = 0.5

    new_positions = update_positions(
        positions=params.initial_positions,
        target_interactions=params.target_interactions,
        weight_relative_threshold=weight_relative_threshold,
        regulation_cursor=weight_relative_threshold,
    )

    new_interactions = interaction_matrix_from_positions(new_positions)

    np.testing.assert_allclose(
        new_interactions[0, 1],
        weight_relative_threshold * params.pairs_curr_weights[0]
        + (1 - weight_relative_threshold) * params.pairs_target_weights[0],
        err_msg=f"Error with {weight_relative_threshold=}",
    )
    np.testing.assert_allclose(
        np.log10(np.abs(new_interactions[2, 3] - params.pairs_curr_weights[1]))
        / np.log10(np.abs(params.pairs_weight_diffs[1])),
        2,
        atol=0.5,
    )


def test_cancelled_priority_on_small_weight_difference(
    small_weight_difference_params: SimpleNamespace,
) -> None:
    params = small_weight_difference_params
    weight_relative_threshold = 1

    new_positions = update_positions(
        positions=params.initial_positions,
        target_interactions=params.target_interactions,
        weight_relative_threshold=weight_relative_threshold,
        regulation_cursor=weight_relative_threshold,
    )

    new_interactions = interaction_matrix_from_positions(new_positions)

    np.testing.assert_allclose(new_interactions[0, 1], params.pairs_curr_weights[0])
    np.testing.assert_allclose(
        new_interactions[2, 3],
        params.pairs_curr_weights[1],
        err_msg=f"Error with {weight_relative_threshold=}",
    )


@pytest.mark.parametrize(
    "steps_per_round, compute_regulation_cursor, compute_max_distance_to_walk, margin_factor",
    [
        (
            1000,
            lambda progress: (1 - progress) ** (1 / 3),
            lambda progress, max_radial_dist: max_radial_dist * (1 - np.sin(np.pi / 2 * progress)),
            1.7,
        ),
        (1000, lambda progress: 0.1, lambda progress, max_radial_dist: np.inf, 1),
    ],
)
def test_force_based_embedding(
    steps_per_round: int,
    compute_regulation_cursor: Callable[[float], float],
    compute_max_distance_to_walk: Callable[
        [float, float | None], float | tuple[float, float, float]
    ],
    margin_factor: float,
) -> None:
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
        starting_positions=np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]]) * max_dist / 3,
        steps_per_round=steps_per_round,  # ok
        compute_max_distance_to_walk=compute_max_distance_to_walk,
        compute_regulation_cursor=compute_regulation_cursor,
        dimensions=(2, 2),
    )

    distances = distance_matrix_from_positions(positions)
    new_min_dist = np.min(distances[np.triu_indices_from(distances, k=1)])
    new_max_dist = new_min_dist * (max_dist / min_dist)
    new_max_diameter_dist = 2 * new_max_dist

    unconnected_pairs = [(0, 2), (0, 3), (1, 2), (1, 3)]
    unconnected_distances = np.array(
        [np.linalg.norm(positions[i] - positions[j]) for i, j in unconnected_pairs]
    )
    assert np.all(unconnected_distances > new_max_diameter_dist - margin_factor * new_min_dist)
    assert np.all(unconnected_distances < new_max_diameter_dist)

    np.testing.assert_allclose(np.linalg.norm(positions[0] - positions[1]), new_min_dist)
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


def test_important_edge_tiny_temperature_does_not_fly_away() -> None:
    positions = np.array([[-0.1], [0], [10], [15]])
    pairs_walks = [1e-15, 10]
    desired_equivalent_positions = np.array(
        [positions[0] + pairs_walks[0], [0], [10], positions[3] + pairs_walks[1]]
    )

    current_interactions = interaction_matrix_from_positions(positions)
    desired_interactions = interaction_matrix_from_positions(desired_equivalent_positions)
    interaction_differences = np.abs(desired_interactions - current_interactions)

    assert interaction_differences[0, 1] < 1e-3 * interaction_differences[2, 3]
    assert (
        interaction_differences[0, 1] / pairs_walks[0]
        > 1e3 * interaction_differences[2, 3] / pairs_walks[1]
    )

    target_interactions = np.copy(current_interactions)
    target_interactions[0, 1] = desired_interactions[0, 1]
    target_interactions[2, 3] = desired_interactions[2, 3]

    output_positions = update_positions(
        positions=positions,
        target_interactions=target_interactions + target_interactions.T,
        weight_relative_threshold=0.1,
        regulation_cursor=current_interactions[0, 1] * 2,
    )

    expected_interactions = np.copy(target_interactions)
    expected_interactions[0, 1] = current_interactions[0, 1]

    output_interactions = interaction_matrix_from_positions(output_positions)

    assert (
        np.abs(np.log10(output_interactions[2, 3] / target_interactions[2, 3]))
        - np.abs(np.log10(current_interactions[2, 3] / target_interactions[2, 3]))
        < -0.9
    )
    np.testing.assert_allclose(
        np.abs(
            np.abs(positions[0] - positions[1]) / np.abs(output_positions[0] - output_positions[1])
        ),
        1,
    )


def test_drawing() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    interactions_graph = nx.Graph()
    interactions_graph.add_nodes_from([i for i in range(2)])
    interactions_graph.add_edge(0, 1, weight=normalized_interaction(1))

    qubo = np.array([[0, normalized_interaction(1)], [0, 0]])
    qubo = qubo + qubo.T

    plt.close("all")
    assert len(plt.get_fignums()) == 0
    update_positions(
        positions=np.array([[-10, 0], [10, 0]]),
        target_interactions=qubo,
        max_radius=1,
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


@pytest.mark.parametrize(
    "dimensions, steps_per_round",
    [
        ((2, 2), 200),
        ((5, 4, 3, 2, 2, 2), 100),
    ],
)
def test_embed_3_nodes(dimensions: tuple[int, ...], steps_per_round: int) -> None:
    target_positions = np.array([[-1.5, 0.0], [-0.5, 0.0], [6.0, 0.0]], dtype=np.float64)
    target_interactions = interaction_matrix_from_positions(target_positions)
    np.fill_diagonal(target_interactions, 0)

    blade_pos = blade(target_interactions, dimensions=dimensions, steps_per_round=steps_per_round)
    blade_interactions = interaction_matrix_from_positions(blade_pos)
    quality = np.linalg.norm(target_interactions - blade_interactions)
    np.testing.assert_allclose(quality, 0.0, atol=1e-2)
