from __future__ import annotations

import logging
from dataclasses import InitVar, dataclass
from typing import Callable

import networkx as nx
import numpy as np
import scipy
import torch

from qoolqit.devices.device import Device
from qoolqit.embedding.base_embedder import EmbedderConfig

from ._dimension_shrinker import DimensionShrinker
from ._dist_constraints_forces import (
    compute_max_dist_constraint_forces,
    compute_min_dist_constraint_forces,
)
from ._distances_constraints_calculator import DistancesConstraintsCalculator
from ._helpers import distance_matrix_from_positions, interaction_matrix_from_distances
from ._interactions_forces import compute_interaction_forces
from ._qubo_mapper import Qubo
from .drawing import draw_graph_including_actual_weights, draw_update_positions_step

logger = logging.getLogger(__name__)


def update_positions(
    *,
    positions: np.ndarray,
    target_interactions: np.ndarray,
    weight_relative_threshold: float = 0.0,
    min_dist: float | None = None,
    max_radius: float | None = None,
    max_distance_to_walk: float | tuple[float, float, float] = np.inf,
    regulation_cursor: float = 0.0,
    draw_step: bool = False,
    step: int | None = None,
    draw_weighted_graph: bool = False,
) -> np.ndarray:
    """
    Compute vector moves to adjust node positions toward target interactions.

    positions: Starting positions of the nodes.
    target_interactions: Desired interactions.
    weight_relative_threshold: It is used to compute a weight difference
        threshold defining which weights differences are significant and should
        be considered. For this purpose, it is multiplied by the higher weight difference.
        It is also used to reduce the precision when targeting
        the objective weights.
    min_dist: If set, defined the minimum distance that should be met, and
        creates forces to enforce the constraint.
    max_radius: If set, defined the maximum radius that should be met, and
        creates forces to enforce the constraint.
    max_distance_to_walk: It set, limits the distance that nodes can walk
        when the forces are applied. It impacts the priorities
        of the forces because they only consider the slope of the differences
        in weights that can be targeting with this ceiling.
    regulation_cursor: A cursor between 0 (no regulation) and 1 (full
        regulation) to uniformize the ability of the forces to achieve their
        interaction targets.
    draw_step: Whether to draw the nodes and the forces.
    step: Step number.
    """

    if draw_step:
        print(f"{weight_relative_threshold=}")
        print(f"{regulation_cursor=}")

    assert np.array_equal(target_interactions, target_interactions.T)
    n = len(target_interactions)

    positions = np.array(positions, dtype=float)
    nb_positions, space_dimension = positions.shape

    if isinstance(max_distance_to_walk, tuple):
        max_distance_to_walk, min_constr_max_distance_to_walk, max_constr_max_distance_to_walk = (
            max_distance_to_walk
        )
    else:
        min_constr_max_distance_to_walk = np.inf
        max_constr_max_distance_to_walk = np.inf

    assert nb_positions == n

    position_differences = positions[np.newaxis, :] - positions[:, np.newaxis]
    distance_matrix = np.linalg.norm(position_differences, axis=2)
    with np.errstate(divide="ignore", invalid="ignore"):
        unitary_vectors = position_differences / distance_matrix[:, :, np.newaxis]
    unitary_vectors[range(n), range(n)] = np.zeros(space_dimension)
    logger.debug(f"{unitary_vectors=}")

    modulated_target_interactions, interaction_force = compute_interaction_forces(
        distance_matrix=distance_matrix,
        unitary_vectors=unitary_vectors,
        target_weights=target_interactions,
        weight_relative_threshold=weight_relative_threshold,
        max_distance_to_walk=max_distance_to_walk,
    )

    regulated_interaction_force = interaction_force.regulated(regulation_cursor=regulation_cursor)

    if draw_step:
        temp_ratio_before = np.max(np.triu(interaction_force.maximum_temperatures, k=1)) / np.min(
            interaction_force.maximum_temperatures
        )
        print(f"temperature ratio before regulation: {temp_ratio_before}")
        temp_ratio_after = np.max(
            np.triu(regulated_interaction_force.maximum_temperatures, k=1)
        ) / np.min(regulated_interaction_force.maximum_temperatures)
        print(f"temperature ratio after regulation: {temp_ratio_after}")

    min_constr_force = compute_min_dist_constraint_forces(
        min_dist=min_dist,
        distance_matrix=distance_matrix,
        unitary_vectors=unitary_vectors,
    )
    max_constr_force = compute_max_dist_constraint_forces(
        positions=positions,
        max_radius=max_radius,
    )

    interaction_resulting_forces = regulated_interaction_force.get_resulting_forces(
        regulated_interaction_force.get_temperature()
    )

    min_constr_resulting_forces = min_constr_force.get_resulting_forces(
        min_constr_force.get_temperature()
    )
    limited_min_constr_resulting_forces = (
        min_constr_resulting_forces
        * np.minimum(
            1,
            min_constr_max_distance_to_walk / np.linalg.norm(min_constr_resulting_forces, axis=-1),
        )[:, np.newaxis]
    )
    limited_min_constr_resulting_forces[min_constr_resulting_forces == 0] = 0

    max_constr_resulting_forces = max_constr_force.get_resulting_forces(
        max_constr_force.get_temperature()
    )
    limited_max_constr_resulting_forces = (
        max_constr_resulting_forces
        * np.minimum(
            1,
            max_constr_max_distance_to_walk / np.linalg.norm(max_constr_resulting_forces, axis=-1),
        )[:, np.newaxis]
    )
    limited_max_constr_resulting_forces[max_constr_resulting_forces == 0] = 0

    resulting_forces_vectors = (
        interaction_resulting_forces
        + limited_min_constr_resulting_forces
        + limited_max_constr_resulting_forces
    )
    logger.debug(f"{resulting_forces_vectors=}")

    assert not np.any(np.isinf(interaction_resulting_forces)) and not np.any(
        np.isnan(interaction_resulting_forces)
    )
    assert not np.any(np.isinf(min_constr_resulting_forces)) and not np.any(
        np.isnan(min_constr_resulting_forces)
    )
    assert not np.any(np.isinf(max_constr_resulting_forces)) and not np.any(np.isnan(positions))

    if draw_step:
        draw_update_positions_step(
            positions,
            interaction_resulting_forces=interaction_resulting_forces,
            min_constr_resulting_forces=min_constr_resulting_forces,
            max_constr_resulting_forces=max_constr_resulting_forces,
            resulting_forces_vectors=resulting_forces_vectors,
            target_interactions=target_interactions,
            current_interactions=interaction_matrix_from_distances(distance_matrix),
            min_dist=min_dist,
            max_radius=max_radius,
            max_dist_to_walk=max_distance_to_walk,
            step=step,
            modulated_target_interactions=(
                modulated_target_interactions if max_distance_to_walk != np.inf else None
            ),
        )

    for u, force in enumerate(resulting_forces_vectors):
        positions[u] += force

    assert not np.any(np.isnan(positions))

    if draw_step:
        logger.debug(f"Resulting positions = {dict(enumerate(positions))}")
        print(f"Current number of dimensions is {positions.shape[-1]}")
        distances = distance_matrix[np.triu_indices_from(distance_matrix, k=1)]
        print(
            f"{min_dist=}, {max_radius=}, "
            f"current min dist = {np.min(distances)}, "
            f"current max dist = {np.max(distances)}"
        )
        target_interactions_graph = Qubo.from_matrix(target_interactions).as_graph()
        draw_graph_including_actual_weights(
            target_interactions_graph=target_interactions_graph,
            positions=positions,
            draw_weighted_graph=draw_weighted_graph,
        )

    return positions


def evolve_with_forces_through_dim_change(
    *,
    target_interactions: np.ndarray,
    draw_steps: bool | list[int] = False,
    starting_dimensions: int,
    final_dimensions: int,
    positions: np.ndarray,
    start_step: int,
    stop_step: int,
    starting_min: float | None = None,
    start_ratio: float | None = None,
    final_ratio: float | None = None,
    compute_weight_relative_threshold_by_step: Callable[[int], float],
    compute_max_distance_to_walk_by_step: Callable[
        [int, float | None], float | tuple[float, float, float]
    ],
    compute_regulation_cursor_by_step: Callable[[int], float],
    draw_weighted_graph: bool = False,
    draw_differences: bool = False,
) -> tuple[np.ndarray, float | None]:
    nb_steps = stop_step - start_step

    dim_shrinker = DimensionShrinker(
        dimensions_to_remove=starting_dimensions - final_dimensions,
        steps=nb_steps,
    )
    dist_constr_calc = DistancesConstraintsCalculator(
        target_interactions=target_interactions,
        starting_min=starting_min,
        starting_ratio=start_ratio,
        final_ratio=final_ratio,
    )
    assert np.unique(positions, axis=0).shape == positions.shape

    for step in range(start_step, stop_step):
        draw_step = draw_steps is True or (isinstance(draw_steps, list) and step in draw_steps)

        if draw_step:
            print(f"{step=}")

        scaling, min_dist, max_radius = dist_constr_calc.compute_scaling_min_max(
            positions=positions,
            step_cursor=(step - start_step) / (nb_steps - 1),
            draw_differences=draw_step and draw_differences,
        )
        assert np.unique(positions, axis=0).shape == positions.shape
        positions = scaling * positions
        if draw_step:
            distances = scipy.spatial.distance.pdist(positions)
            print(
                f"After {scaling=}, max/min is "
                f"{np.max(distances)/np.min(distances)} with target {max_radius}/{min_dist}"
            )
        assert not np.any(np.isinf(positions)) and not np.any(np.isnan(positions))

        positions = update_positions(
            positions=positions,
            target_interactions=target_interactions,
            weight_relative_threshold=compute_weight_relative_threshold_by_step(step),
            min_dist=min_dist,
            max_radius=max_radius,
            max_distance_to_walk=compute_max_distance_to_walk_by_step(step, max_radius),
            regulation_cursor=compute_regulation_cursor_by_step(step),
            draw_step=draw_step,
            step=step,
            draw_weighted_graph=draw_step and draw_weighted_graph,
        )
        assert np.unique(positions, axis=0).shape == positions.shape
        assert not np.any(np.isinf(positions)) and not np.any(np.isnan(positions))
        positions = dim_shrinker.applied_step(positions)

    removed_position_dims = positions[:, final_dimensions:]
    assert np.all(
        np.isclose(removed_position_dims, 0)
    ), f"Shrunk dimensions {removed_position_dims=} should only contain zeros"

    return positions[:, :final_dimensions], min_dist


def generate_random_positions(target_interactions: np.ndarray, dimension: int) -> np.ndarray:
    return np.random.uniform(-1, 1, size=(len(target_interactions), dimension))


def augment_dimensions_with_random_values(
    positions: np.ndarray, *, new_dimensions: int
) -> np.ndarray:
    quantiles = np.quantile(positions, q=0.75, axis=0) - np.quantile(positions, q=0.5, axis=0)
    volume_per_point = np.prod(quantiles) / positions.shape[0]
    edge = volume_per_point ** (1 / positions.shape[1])
    positions_noise = np.random.uniform(
        low=-edge / 2,
        high=edge / 2,
        size=(len(positions), new_dimensions),
    )
    return np.concatenate((positions, positions_noise), axis=1)


def evolve_with_dimension_transition(
    *,
    dimensions: tuple[int, ...],
    starting_min: float | None,
    pca: bool,
    start_step: int,
    stop_step: int,
    compute_weight_relative_threshold_by_step: Callable[[int], float],
    compute_max_distance_to_walk_by_step: Callable[
        [int, float | None], float | tuple[float, float, float]
    ],
    compute_regulation_cursor_by_step: Callable[[int], float],
    target_interactions: np.ndarray,
    positions: np.ndarray,
    final_ratio: float | None,
    dim_idx: int,
    start_ratio: float | None,
    draw_steps: bool | list[int],
    draw_weighted_graph: bool = False,
    draw_differences: bool = False,
) -> tuple[np.ndarray, float | None]:

    starting_dimensions = dimensions[dim_idx]
    final_dimensions = dimensions[dim_idx + 1]

    if final_dimensions < starting_dimensions and pca:
        try:
            from sklearn.decomposition import PCA
        except ImportError:
            raise ModuleNotFoundError(
                "To use `pca=True` in the BLaDE algorithm, "
                "please install the `scikit-learn` library."
            )
        pca_inst = PCA(n_components=starting_dimensions)
        positions = pca_inst.fit_transform(positions)

    elif final_dimensions > starting_dimensions:
        positions = augment_dimensions_with_random_values(
            positions, new_dimensions=final_dimensions - starting_dimensions
        )
        starting_dimensions = final_dimensions

    positions, starting_min = evolve_with_forces_through_dim_change(
        target_interactions=target_interactions,
        draw_steps=draw_steps,
        starting_dimensions=starting_dimensions,
        final_dimensions=final_dimensions,
        positions=positions,
        start_step=start_step,
        stop_step=stop_step,
        starting_min=starting_min,
        start_ratio=start_ratio,
        final_ratio=final_ratio,
        compute_weight_relative_threshold_by_step=compute_weight_relative_threshold_by_step,
        compute_max_distance_to_walk_by_step=compute_max_distance_to_walk_by_step,
        compute_regulation_cursor_by_step=compute_regulation_cursor_by_step,
        draw_weighted_graph=draw_weighted_graph,
        draw_differences=draw_differences,
    )

    return positions, starting_min


def _compute_min_pairwise_distance(positions: np.ndarray) -> float:
    distance_matrix = distance_matrix_from_positions(positions)
    upper_diagonal_mask = np.triu(np.ones(distance_matrix.shape), k=1).astype(bool)
    return np.min(distance_matrix[upper_diagonal_mask])  # type: ignore


def default_compute_max_distance_to_walk(progress: float, max_radial_dist: float | None) -> float:
    """Default function with rapid then slow decrease to zero of the walking distance."""
    if max_radial_dist is None:
        return float(np.inf)
    return float(2 * max_radial_dist * (1 - np.sin(np.pi / 2 * progress)))


def default_compute_ratio_step_factors(progress: float) -> float:
    """Default function to decrease the ratio slightly too low and then increase."""
    return float(np.interp(progress, xp=[0, 3 / 5, 1], fp=[2, 0.94, 0.98]))


def blade(
    matrix: np.ndarray,
    *,
    max_min_dist_ratio: float | None = None,
    dimensions: tuple[int, ...] = (5, 4, 3, 2, 2, 2),
    starting_positions: np.ndarray | None = None,
    pca: bool = False,
    steps_per_round: int = 200,
    compute_weight_relative_threshold: Callable[[float], float] = (lambda _: 0.1),
    compute_max_distance_to_walk: Callable[
        [float, float | None], float | tuple[float, float, float]
    ] = default_compute_max_distance_to_walk,
    compute_regulation_cursor: Callable[[float], float] = (lambda _: 0.1),
    compute_ratio_step_factors: Callable[[float], float] = default_compute_ratio_step_factors,
    ratio_rerun: int = 2,
    draw_steps: bool | list[int] = False,
    draw_weighted_graph: bool = False,
    draw_differences: bool = False,
) -> np.ndarray:
    """
    Embed an interaction matrix or QUBO with the BLaDE algorithm.

    BLaDE stands for Balanced Latently Dimensional Embedder.
    It compute positions for nodes so that their interactions
    approach the desired values. The interactions assume that the
    interaction coefficient of the device is set to 1.
    Its typical target is on interaction matrices or QUBOs, but it can also be used
    for MIS with limitations if the adjacency matrix is converted into a QUBO.
    The general principle is based on the Fruchterman-Reingold algorithm.

    matrix: An objective interaction matrix or QUBO between the nodes. It must
        be either symmetrical or triangular.
    max_min_dist_ratio: If present, set the maximum ratio between
        the maximum radial distance and the minimum pairwise distances.
    dimensions: List of numbers of dimensions to explore one
        after the other. A list with one value is equivalent to a list containing
        twice the same value. For a 2D embedding, the last value should be 2.
        Increasing the number of intermediate dimensions can help to escape
        from local minima.
    starting_positions: If provided, initial positions to start from. Otherwise,
        random positions will be generated. The number of dimensions of the
        starting positions must be lower than or equal to the first dimension
        to explore. If it is lower, it is added dimensions filled with
        random values.
    pca: Whether to apply Principal Component Analysis to prioritize dimensions
        to keep when transitioning from a space to a space with fewer dimensions.
        It is disabled by default because it can raise an error when there are
        too many dimensions compared to the number of nodes.
    steps_per_round: Number of elementary steps to perform for each dimension
        transition, where at each step move vectors are computed and applied
        on the nodes.
    compute_weight_relative_threshold: Function that is called at each step.
        It takes a float number between 0 and 1 that represents the progress
        on the steps. It must return a float number between 0 and 1 that gives
        a threshold determining which weights are significant (see
        `update_positions` to learn more).
    compute_max_distance_to_walk: Function that is called at each step.
        It takes a float number between 0 and 1 that represents the progress
        on the steps, and takes another argument that is set to `None` when
        `max_min_dist_ratio` is not enabled, otherwise, it is set to
        the maximum radial distance for the current step.
        It must return a float number that limits the distances
        nodes can move at one step  (see `update_positions` to learn more).
    compute_regulation_cursor: Function that is called at each step.
        It takes a float number between 0 and 1 that represents the progress
        on the steps. It must return a float number between 0 (no regulation)
        and 1 (full regulation) that uniformizes the ability for the forces
        to achieve their objectives at each step by changing priorities.
    ratio_rerun: When the distance ratio constraint is not met, it defines
        the maximum number of times the algorithm applies additional
        computation steps putting the priority on the constraint.
    compute_ratio_step_factors: Function that is called at the boundaries of
        the rounds. It defines the target ratio the enforce during the
        evolution. It acts as a multiplying factor on the target ratio.
    draw_steps: If it is a boolean, it defines whether to globally enable
        drawing and traces for nodes and forces (for all steps). If it is a
        list of integers, it defines a subset of steps to enable such drawing.
        Requires installing the seaborn library.
    draw_weighted_graph: For each step with drawing enabled, defines whether
        to draw a weighted graph representing interactions.
    draw_differences: For each step with drawing enabled, defines whether
        to draw the differences between current and target interactions.
    """

    if len(dimensions) == 1:
        dimensions = (dimensions[0], dimensions[0])

    assert len(dimensions) >= 2

    if isinstance(matrix, np.ndarray):
        assert not np.all(matrix == 0)
    else:
        assert not torch.all(matrix == 0)

    graph = Qubo.from_matrix(matrix).as_graph()
    matrix = np.array(
        nx.adjacency_matrix(graph, nodelist=list(range(len(matrix))), weight="weight").toarray()
    )

    if starting_positions is None:
        positions = generate_random_positions(target_interactions=matrix, dimension=dimensions[0])
    elif starting_positions.shape[1] <= dimensions[0]:
        positions = augment_dimensions_with_random_values(
            starting_positions, new_dimensions=dimensions[0] - starting_positions.shape[1]
        )
    else:
        raise ValueError(
            f"The number of dimensions in the starting positions "
            f"{starting_positions.shape[1]} is greater than the starting "
            f"number of dimensions {dimensions[0]}."
        )

    total_steps = steps_per_round * (len(dimensions) - 1)

    def step_to_progress(step: int) -> float:
        return step / (total_steps - 1)

    steps_ratios: list[float | None] = []

    if max_min_dist_ratio is not None:
        steps_ratios = [
            max_min_dist_ratio * compute_ratio_step_factors(progress)
            for progress in np.linspace(0, 1, len(dimensions))
        ]
        starting_min = _compute_min_pairwise_distance(positions)
    else:
        steps_ratios = [None] * len(dimensions)
        starting_min = None

    assert len(dimensions) == len(steps_ratios)

    def compute_weight_relative_threshold_by_step(step: int) -> float:
        return compute_weight_relative_threshold(step_to_progress(step))

    def compute_max_distance_to_walk_by_step(
        step: int, max_radial_dist: float | None
    ) -> float | tuple[float, float, float]:
        return compute_max_distance_to_walk(step_to_progress(step), max_radial_dist)

    def compute_regulation_cursor_by_step(step: int) -> float:
        return compute_regulation_cursor(step_to_progress(step))

    for dim_idx, start_ratio, final_ratio in zip(
        range(len(dimensions) - 1), steps_ratios[:-1], steps_ratios[1:]
    ):
        positions, starting_min = evolve_with_dimension_transition(
            target_interactions=matrix,
            dimensions=dimensions,
            starting_min=starting_min,
            pca=pca,
            start_step=dim_idx * steps_per_round,
            stop_step=(dim_idx + 1) * steps_per_round,
            compute_weight_relative_threshold_by_step=compute_weight_relative_threshold_by_step,
            compute_max_distance_to_walk_by_step=compute_max_distance_to_walk_by_step,
            compute_regulation_cursor_by_step=compute_regulation_cursor_by_step,
            positions=positions,
            final_ratio=final_ratio,
            dim_idx=dim_idx,
            start_ratio=start_ratio,
            draw_steps=draw_steps,
            draw_weighted_graph=draw_weighted_graph,
            draw_differences=draw_differences,
        )

    if max_min_dist_ratio is not None:
        max_radial_dist = max(np.linalg.norm(positions, axis=-1))
        min_atom_dist = _compute_min_pairwise_distance(positions)
        output_ratio = max_radial_dist / min_atom_dist
        if output_ratio > max_min_dist_ratio:

            if ratio_rerun > 0:
                return blade(
                    matrix=matrix,
                    max_min_dist_ratio=max_min_dist_ratio,
                    dimensions=(2, 2, 2),
                    starting_positions=positions,
                    steps_per_round=steps_per_round,
                    compute_max_distance_to_walk=lambda x, max_radial_dist: 0,
                    compute_ratio_step_factors=lambda progress: np.interp(
                        progress, xp=[0, 1 / 2, 1], fp=[0.8, 0.9, 0.98]
                    ),
                    ratio_rerun=ratio_rerun - 1,
                )

            print(
                f"[Warning] Output ratio {output_ratio}"
                f" is higher than required {max_min_dist_ratio}"
            )

    return positions


@dataclass
class BladeConfig(EmbedderConfig):
    """Configuration parameters to embed with BLaDE."""

    max_min_dist_ratio: float | None = None
    dimensions: tuple[int, ...] = (5, 4, 3, 2, 2, 2)
    starting_positions: np.ndarray | None = None
    pca: bool = False
    steps_per_round: int = 200
    compute_weight_relative_threshold: Callable[[float], float] = lambda _: 0.1
    compute_max_distance_to_walk: Callable[
        [float, float | None], float | tuple[float, float, float]
    ] = lambda x, max_radial_dist: np.inf
    starting_ratio_factor: int = 2
    draw_steps: bool | list[int] = False
    device: InitVar[Device | None] = None

    def __post_init__(self, device: Device | None) -> None:
        """Post initialization of the `BladeConfig` dataclass.

        Set the `max_min_dist_ratio` argument of the `blade_embedding` algorithm
        based on the specification of the selected device.

        Args:
            device (Device): the QoolQit device to use to set the maximum ratio between the maximum
                radial distance and the minimum pairwise distance between atoms.
        """
        if device:
            if self.max_min_dist_ratio:
                logger.warning(
                    "`max_min_dist_ratio` and `device` attributes should not be set simultaneously."
                )
            min_distance = device._min_distance
            max_radial_distance = device._max_radial_distance
            if max_radial_distance and min_distance:
                self.max_min_dist_ratio = max_radial_distance / min_distance
